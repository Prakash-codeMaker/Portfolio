#!/usr/bin/env python3
"""LoopBench: validate provenance metadata and evaluate a frozen scorer on holdout rows.

This tool handles de-identified metadata/outcome tables only. It does not design
proteins, interpret biology, generate protocols, or recommend experiments.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

REQUIRED = (
    "design_id", "target_id", "epitope_id", "binder_format", "model_version",
    "campaign_id", "assay_batch", "predicted_score", "observed_hit",
    "qc_status", "evaluation_split", "evidence_ref",
)
QC_STATES = {"PASS", "FAIL", "REVIEW"}
SPLITS = {"development", "prospective_holdout", "retrospective"}


def load_csv(path: str) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [field for field in REQUIRED if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(missing))
        return list(reader)


def validate(rows: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()

    for line_no, row in enumerate(rows, start=2):
        design_id = (row.get("design_id") or "").strip()
        if not design_id:
            errors.append(f"Row {line_no}: design_id is blank")
        elif design_id in seen:
            errors.append(f"Row {line_no}: duplicate design_id {design_id}")
        seen.add(design_id)

        for field in ("target_id", "epitope_id", "model_version", "campaign_id",
                      "assay_batch", "evidence_ref"):
            if not (row.get(field) or "").strip():
                errors.append(f"Row {line_no}: {field} is blank")

        try:
            score = float(row["predicted_score"])
            if not 0.0 <= score <= 1.0:
                errors.append(f"Row {line_no}: predicted_score must be between 0 and 1")
        except (ValueError, TypeError, KeyError):
            errors.append(f"Row {line_no}: predicted_score is not numeric")

        if str(row.get("observed_hit")) not in {"0", "1"}:
            errors.append(f"Row {line_no}: observed_hit must be 0 or 1")
        if row.get("qc_status") not in QC_STATES:
            errors.append(f"Row {line_no}: qc_status must be PASS, FAIL or REVIEW")
        if row.get("evaluation_split") not in SPLITS:
            errors.append(
                f"Row {line_no}: evaluation_split must be development, "
                "prospective_holdout or retrospective"
            )

    development = [r for r in rows if r.get("evaluation_split") == "development"]
    holdout = [r for r in rows if r.get("evaluation_split") == "prospective_holdout"]
    if not holdout:
        warnings.append("No prospective_holdout rows: prospective evaluation is blocked.")
    if development and holdout:
        for field, label in (
            ("target_id", "target"), ("epitope_id", "epitope"),
            ("campaign_id", "campaign"), ("assay_batch", "assay batch"),
        ):
            overlap = {r.get(field) for r in development} & {r.get(field) for r in holdout}
            if overlap:
                warnings.append(
                    f"{label} overlap between development and holdout: "
                    f"{len(overlap)} shared value(s). Check the declared split strategy."
                )
    if len(rows) < 30:
        warnings.append("Fewer than 30 records: treat output as a small descriptive sample.")
    return errors, warnings


def mean(values: list[int]) -> float | None:
    return statistics.mean(values) if values else None


def cluster_bootstrap_topk(
    by_target: dict[str, list[dict[str, str]]],
    top_k: int,
    iterations: int = 2000,
    seed: int = 17,
) -> list[float] | None:
    """Bootstrap targets as clusters, preserving the target as the sampling unit."""
    target_ids = list(by_target)
    if len(target_ids) < 3:
        return None
    rng = random.Random(seed)
    estimates: list[float] = []
    for _ in range(iterations):
        sampled_targets = [rng.choice(target_ids) for _ in target_ids]
        hits: list[int] = []
        for target in sampled_targets:
            ranked = sorted(
                by_target[target],
                key=lambda item: float(item["predicted_score"]),
                reverse=True,
            )[:top_k]
            hits.extend(int(item["observed_hit"]) for item in ranked)
        if hits:
            estimates.append(sum(hits) / len(hits))
    estimates.sort()
    return [
        estimates[int(0.025 * len(estimates))],
        estimates[min(len(estimates) - 1, int(0.975 * len(estimates)))],
    ]


def evaluate(rows: list[dict[str, str]], top_k: int = 5) -> dict:
    errors, warnings = validate(rows)
    if errors:
        return {"status": "BLOCKED", "reason": "Fix validation errors before evaluation.", "errors": errors}
    if top_k < 1:
        return {"status": "ERROR", "reason": "top_k must be >= 1"}

    eligible = [
        row for row in rows
        if row.get("evaluation_split") == "prospective_holdout"
        and row.get("qc_status") == "PASS"
    ]
    if not eligible:
        return {
            "status": "BLOCKED",
            "reason": "No QC-PASS prospective_holdout records. Retrospective rows cannot substitute.",
            "warnings": warnings,
        }

    by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in eligible:
        by_target[row["target_id"]].append(row)

    selected: list[dict[str, str]] = []
    per_target = []
    for target_id, group in sorted(by_target.items()):
        ranked = sorted(group, key=lambda item: float(item["predicted_score"]), reverse=True)
        top_rows = ranked[:top_k]
        selected.extend(top_rows)
        per_target.append({
            "target_id": target_id,
            "eligible_qc_pass_rows": len(group),
            "selected_rows": len(top_rows),
            "baseline_hit_rate": mean([int(r["observed_hit"]) for r in group]),
            "top_k_hit_rate": mean([int(r["observed_hit"]) for r in top_rows]),
        })

    baseline_rate = mean([int(r["observed_hit"]) for r in eligible])
    top_k_rate = mean([int(r["observed_hit"]) for r in selected])
    ci = cluster_bootstrap_topk(by_target, top_k)

    return {
        "status": "DESCRIPTIVE_HOLDOUT_ONLY",
        "disclaimer": (
            "Computed only from QC-PASS records explicitly labelled prospective_holdout. "
            "This is a descriptive metric, not evidence of causal improvement, biological "
            "efficacy or external validity. Confirm split design and outcome semantics."
        ),
        "dataset_rows": len(rows),
        "prospective_holdout_qc_pass_rows": len(eligible),
        "holdout_target_count": len(by_target),
        "top_k_per_target": top_k,
        "selected_rows": len(selected),
        "baseline_holdout_hit_rate": baseline_rate,
        "top_k_holdout_hit_rate": top_k_rate,
        "descriptive_enrichment_lift": (
            top_k_rate / baseline_rate if baseline_rate not in (None, 0) else None
        ),
        "top_k_hit_rate_target_cluster_bootstrap_95ci": ci,
        "uncertainty_note": (
            "Cluster bootstrap resamples targets as units; fewer than three holdout "
            "targets returns no interval. This simple interval is a diagnostic, not a "
            "replacement for a statistician-approved analysis plan."
        ),
        "validation_warnings": warnings,
        "per_target": per_target,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LoopBench metadata validator/evaluator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="Validate schema, IDs, QC and split overlap")
    validate_parser.add_argument("csv")
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate only prospective holdout rows")
    eval_parser.add_argument("csv")
    eval_parser.add_argument("--top-k", type=int, default=5)
    eval_parser.add_argument("--out", help="Optional JSON report destination")
    args = parser.parse_args()

    try:
        rows = load_csv(args.csv)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
        return 2

    errors, warnings = validate(rows)
    if args.command == "validate":
        result = {
            "status": "VALID" if not errors else "INVALID",
            "record_count": len(rows),
            "errors": errors,
            "warnings": warnings,
        }
    else:
        result = evaluate(rows, args.top_k)
        if args.out:
            Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
