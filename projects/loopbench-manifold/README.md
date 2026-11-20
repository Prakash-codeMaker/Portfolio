# LoopBench — Prospective Evidence & Evaluation Workbench

Independent AI-platform work sample inspired by Manifold Bio's public mBER-2 report.

## Open the prototype
Open [the interactive prototype](./index.html). Read the [product memo](./PRODUCT_MEMO.md), [evaluation charter](./evaluation-charter.md), and [candidate outcome schema](./candidate-outcome.schema.json).

## Product thesis
As AI design and experimental throughput increase, the platform challenge is making every candidate, model version, physical construct, assay readout, uncertainty and next decision traceable—and distinguishing retrospective results from prospective evaluation.

## Public report facts
The September 22, 2026 mBER-2 technical report describes 56 targets, 1,298,334 designs ordered, 584,450 high-signal designs, 26,026 specific on-design hits across formats, 55/56 targets with at least one hit pooled across formats, and 430 binder–antigen pairs tested by BLI.

| Format | Overall hit rate | Retrospective top-100 |
|---|---:|---:|
| VHH | 8.6% | 16.8% |
| Minibinder | 4.64% | 8.62% |
| Microbinder | 0.93% | 3.55% |

**The top-100 rates are retrospective selections, not prospective holdout performance.** The product opportunity is to make that distinction operational and enforceable.

## Included engineering components
- loopbench.py: standard-library CSV validator and prospective holdout diagnostic.
- data/synthetic_candidate_outcomes.csv: synthetic-only event-level fixture; every identifier is prefixed SYN-.
- data/public_mber2_aggregate.json: source-attributed public aggregate metrics.
- tests/test_loopbench.py: tests for duplicate IDs, split leakage, absent holdouts, QC filtering, target-stratified top-k and bootstrap boundary.
- .github/workflows/loopbench-tests.yml: CI validation and test workflow.
- candidate-outcome.schema.json: machine-readable record contract.

### Run locally
Python 3.10+; no third-party packages required.

```bash
python loopbench.py validate data/synthetic_candidate_outcomes.csv
python loopbench.py evaluate data/synthetic_candidate_outcomes.csv --top-k 5 --out report.json
python -m unittest discover -s tests -v
```

The CLI only computes holdout metrics from rows explicitly labelled prospective_holdout and with qc_status=PASS. It blocks if no eligible holdout rows exist. It warns about target, epitope, campaign or assay-batch overlap. The bootstrap resamples targets as clusters; for fewer than three holdout targets it reports no interval. This is a simple descriptive diagnostic, not a statistician-approved analysis plan or biological conclusion.

## Guardrails
- Keep development, retrospective and prospective results distinct.
- Freeze model/scorer/configuration before unblinding an untouched holdout.
- Check target, epitope, campaign, time and assay-batch overlap.
- Keep PASS, FAIL, REVIEW and missing outcomes explicit.
- Report denominators, QC attrition, target-level variation and uncertainty.
- Do not treat binding as proof of in-vivo distribution, PK or therapeutic function.

## Scope and safety
This is an independent concept using public aggregate metrics and synthetic examples. It uses no protein sequences, internal Manifold data, patient data or wet-lab protocols. It does not make biological predictions, rank actual targets or recommend experiments. The workflow is a hypothesis to pressure-test with scientists, not a claim about Manifold's internal infrastructure.

## Sources
- [mBER-2 technical report](https://manifold-bio-public.s3.us-east-2.amazonaws.com/mBER-2_technical_report_v20260922.pdf)
- [Manifold mBER-2 announcement](https://www.manifold.bio/news/mber-2-scaling-ai-protein-design-to-learn-from-living-systems)
- [mBER-open repository](https://github.com/manifoldbio/mber-open)
- [AI Platform & Partnerships role](https://job-boards.greenhouse.io/manifoldbio/jobs/5127283007)
