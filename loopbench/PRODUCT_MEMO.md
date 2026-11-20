# LoopBench — Product & evaluation memo

## Executive thesis
As design and experimental throughput rise, the platform challenge shifts from producing more candidates to ensuring every candidate, prediction, physical measurement and downstream decision can be compared and audited.

## Evidence motivating the concept
Manifold's mBER-2 report reports an 8.6% overall VHH hit rate and 16.8% among retrospectively selected top-100 designs per target. The supplement explicitly distinguishes selected-group results as in-sample retrospective enrichment, not prospective performance. This creates a product requirement: evaluation regimes must travel with metrics and be enforced at report time.

## Proposed product
**Evidence graph:** model run → design record → construct ID → assay batch → readout → scientific decision. Each edge has a stable ID, timestamp, schema version, source reference and owner. Corrections append events.

**Evaluation guardrails:** target/epitope/campaign/time/batch split manifests; duplicate and overlap checks; frozen model/scorer/configuration hashes; separate retrospective and prospective reporting; denominators, QC attrition, missingness, target/format heterogeneity and uncertainty.

**Decision-aware scorecards:** start with the decision being supported. Binding is not proof of biodistribution. Biodistribution is not proof of therapeutic function. Display evidence maturity and missing evidence explicitly.

**Partner collaboration surface:** approved, schema-versioned evidence packages with data rights, permitted use, IP, retention, access and derivative-use scope stated.

## Metrics
- Data reliability: lineage completeness, duplicate rate, missingness, QC attrition, batch coverage, latency and correction rate.
- Model evaluation: per-target and per-format top-k enrichment, target-level coverage, calibration, uncertainty, held-out target/epitope/time performance, batch robustness and ranking stability.
- Workflow impact: time from result to decision, fraction of decisions with complete evidence, feedback latency, review burden and repeat use.

## First 30 days
1. Discover: interview 3–5 scientists, AI/ML researchers and R&D programme owners; map hand-offs and decision points.
2. Contract: agree on a low-risk dataset slice; define event IDs, versioning, QC semantics, splits and source of truth.
3. Integrate: connect one approved read-only dataset or synthetic sandbox; add lineage checks and scorecards.
4. Evaluate: run against a pre-registered holdout; measure reproducibility, missing lineage, time-to-review and scientist usefulness.

## Product risks
- Retrospective leakage → holdout ownership, split manifests, frozen scoring.
- Pooled averages masking target variance → per-target reporting and uncertainty.
- Binding mistaken for in-vivo or therapeutic effect → evidence maturity ladder.
- Partner rights → explicit access, retention and derivative-use controls.
- Workflow friction → derive identifiers where possible and measure scientist burden.

This prototype is a product hypothesis to validate with Manifold's scientists. It is not a protein design system, biological model or wet-lab planner.
