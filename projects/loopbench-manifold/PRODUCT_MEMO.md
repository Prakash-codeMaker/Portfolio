# LoopBench — Product & Evaluation Memo

## Executive thesis
With high-throughput design and experimental loops, the platform challenge is not only generating more candidates. It is ensuring every candidate, prediction, physical measurement and downstream decision can be compared, reproduced and audited—and knowing when a retrospective metric is not a prospective result.

## Product hypothesis
A lightweight evidence operating layer could make this chain queryable and decision-ready:

**Model run → design record → construct ID → assay batch → readout → scientific decision**

Every transition carries a stable ID, timestamp, source reference, version and accountable owner. Corrections append events rather than silently overwriting history.

## Public evidence motivating the concept
Manifold's 22 September 2026 mBER-2 report describes 56 targets. It reports 1,298,334 designs ordered, 584,450 high-signal designs, 26,026 specific on-design hits across formats, pooled hit coverage of 55/56 targets, and 430 binder–antigen pairs tested by BLI.

Reported hit rates:
- VHH: 8.6% overall; 16.8% for retrospectively selected top-100 designs per target.
- Minibinder: 4.64% overall; 8.62% top-100 retrospective.
- Microbinder: 0.93% overall; 3.55% top-100 retrospective.

The top-100 rates are retrospective, not a prospective holdout claim. That distinction can become operational: store the evaluation regime with every metric, prevent retrospective results from being labelled prospective, and require a frozen scorer plus untouched holdout for a generalisation claim.

## Product surfaces
### 1. Evidence graph
Versioned model run, design intent, construct identity, assay batch, readout, QC and decision records. Each object has a canonical ID and immutable event history.

### 2. Evaluation guardrails
- Split manifests for target, epitope, campaign, time and assay-batch boundaries.
- Import-time checks for duplicate identifiers and development/holdout overlap.
- Frozen model, scorer, feature-pipeline, code-commit and configuration hashes.
- Explicit retrospective/prospective labels and pre-registered thresholds.
- Reports with denominators, QC attrition, missingness and target/format heterogeneity.

### 3. Decision-aware scorecards
Each scorecard begins with the decision it supports. A binding hit is not a claim about in-vivo distribution. Distribution is not proof of therapeutic function. Evidence maturity and missing evidence should be explicit.

### 4. Partner collaboration surface
Export an approved, schema-versioned evidence package with data rights, permitted uses, IP, retention, access controls and derivative-use boundaries stated.

## Metrics worth discussing
**Data reliability:** lineage completeness, duplicate rate, missingness, QC attrition, batch coverage, data latency and correction rate.

**Model evaluation:** per-target/per-format top-k enrichment, target-level hit coverage, calibration/Brier score where probabilities are meaningful, held-out-target/epitope/time performance, ranking stability, epitope breadth and uncertainty intervals.

**Workflow impact:** time from readout to decision, share of decisions with complete evidence, experiment-to-model feedback latency, scientist review burden and repeat use.

## A 30-day validation plan
**Week 1 — Discover.** Interview 3–5 scientists, AI/ML researchers and programme owners. Map actual handoffs, identifiers, recurring failures and decision points. Do not assume this prototype's schema is correct.

**Week 2 — Contract.** Agree one low-risk, permitted data slice. Define event IDs, versioning, QC semantics, evaluation splits, source of truth and export boundaries.

**Week 3 — Integrate.** Connect one approved read-only dataset or a partner-approved synthetic sandbox. Add lineage and leakage checks.

**Week 4 — Evaluate.** Run a pre-registered holdout. Measure reproducibility, missing lineage, time-to-review, evaluation quality and scientist usefulness. Expand, redesign or stop based on evidence.

## Main risks
- False confidence from pooled metrics: mitigate with stratified reporting and uncertainty.
- Retrospective metrics presented as prospective lift: mitigate with holdout custody, split manifests and frozen scoring.
- Binding interpreted as biodistribution or therapeutic effect: mitigate with evidence maturity levels.
- Partner data rights: mitigate with explicit access, retention, IP and derivative-use controls.
- Added metadata burdens scientists: derive identifiers where possible and measure review burden.

## Scope boundary
This is an independent product/evaluation concept using public aggregate figures and synthetic examples. It is not protein design software, a biological model, a wet-lab planner or a claim about Manifold's internal infrastructure. Every workflow hypothesis requires validation with the people who use the real system.
