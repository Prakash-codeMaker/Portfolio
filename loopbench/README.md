# LoopBench — Prospective Evidence & Evaluation Workbench

An independent AI-platform product work sample built from Manifold Bio's public mBER-2 report. It is not affiliated with or endorsed by Manifold Bio.

## Product thesis
The product layer should make every candidate, prediction, physical measurement and downstream decision traceable. It should also prevent retrospective enrichment from being presented as prospective model performance.

## Public report facts
The September 22, 2026 mBER-2 report reports 56 targets; 1,298,334 designs ordered; 1,250,720 primary on-panel sequences; 584,450 high-signal designs; 26,026 specific on-design hits across formats; hits to 55/56 targets pooled; hits on at least two predicted epitope clusters for 51/56; and 430 binder-antigen pairs tested by BLI.

| Format | Overall hit rate | Top-100 retrospective |
|---|---:|---:|
| VHH | 8.6% | 16.8% |
| Minibinder | 4.64% | 8.62% |
| Microbinder | 0.93% | 3.55% |

The top-100 selection is retrospective, not prospective performance. See the report and supplement before interpreting the figures.

## Prototype
Open index.html in a browser. Import a de-identified CSV with the required schema. The app calculates target-stratified top-k metrics only on QC-PASS rows explicitly marked prospective_holdout and warns about target, campaign and batch overlap.

## CLI
Requires Python 3.9+, standard library only:
    python loopbench.py validate data/synthetic_candidate_outcomes.csv
    python loopbench.py evaluate data/synthetic_candidate_outcomes.csv --top-k 5
    python -m unittest discover -s tests -v

## Data contract
design_id,target_id,epitope_id,binder_format,model_version,campaign_id,assay_batch,predicted_score,observed_hit,qc_status,evaluation_split,evidence_ref

evaluation_split: development / prospective_holdout / retrospective.
qc_status: PASS / FAIL / REVIEW.
Keep missing and failed data visible; do not silently recode.

## Product primitives
1. Model run → design → construct → assay batch → readout → decision lineage.
2. Split manifests and leakage checks across targets, campaigns and batches.
3. Frozen model/scorer/configuration versions for each benchmark.
4. Decision-aware scorecards with denominators, QC attrition, uncertainty and target-level heterogeneity.
5. Evidence maturity labels that keep computational design, in-vitro binding, in-vivo distribution/PK and functional claims distinct.
6. Partner-safe data rights, access, retention and export boundaries.

## Limitations
- Event-level fixture is synthetic. Public aggregate values are attributed to the report.
- No protein sequence design, biological prediction, wet-lab protocol or experimental recommendation.
- Enrichment calculation is descriptive, not causal or independently validated.
- Proposed workflow is a hypothesis to validate with scientists and platform users.

## Sources
- mBER-2 technical report: https://manifold-bio-public.s3.us-east-2.amazonaws.com/mBER-2_technical_report_v20260922.pdf
- Manifold mBER-2 announcement: https://www.manifold.bio/news/mber-2-scaling-ai-protein-design-to-learn-from-living-systems
- mBER-open: https://github.com/manifoldbio/mber-open
