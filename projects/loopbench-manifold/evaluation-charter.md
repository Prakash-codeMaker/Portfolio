# Prospective Evaluation Charter — Draft Template

## Claim to test
Does a frozen scoring model improve candidate selection on an untouched future or target-held-out campaign, compared with a pre-defined baseline?

## Split strategy
Choose and document one primary split before looking at holdout outcomes:
- Unseen targets (target-held-out).
- Unseen epitopes within known targets.
- Future campaign / temporal holdout.
- Independent assay batch or site holdout.

Document the unit of randomisation and why the split matches the intended deployment setting.

## Frozen artefacts
Record the model checkpoint/version, scorer and feature-pipeline version, code commit/configuration hash, candidate eligibility rules, exclusions, thresholds, assay protocol version, controls and outcome semantics.

## Primary metric
Choose one metric tied to the decision:
- Target-stratified top-k enrichment vs unfiltered baseline.
- Target-level hit coverage at fixed experimental budget.
- Calibration/Brier score, only where scores represent probabilities.
- Epitope breadth at fixed experimental budget.

## Pre-analysis gates
1. Holdout labels are controlled by an evaluator not involved in model tuning.
2. Split manifest checked for target, epitope, campaign, time and assay-batch leakage.
3. Model, scorer, feature pipeline, code and configuration are frozen.
4. Hit definition, controls, QC exclusions and missingness semantics are approved.
5. Primary metric, denominator and uncertainty analysis are specified before unblinding.
6. Scientific owner signs off on interpretation and defines which decision the metric informs.

## Reporting rules
- Keep development, retrospective and prospective results separate.
- Retain FAIL, REVIEW and missing as explicit states; do not silently recode.
- Report denominators and attrition at every stage.
- Do not generalise binding results to in-vivo distribution, PK or therapeutic function.
- Report target-level variance, not only a pooled score.
- Record protocol deviations and every exclusion.

No experiment or biological recommendation is authorised by this template. Relevant scientific and platform owners must approve the protocol, data access and interpretation.
