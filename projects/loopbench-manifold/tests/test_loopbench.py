import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from loopbench import evaluate, validate


def record(design, target, split="prospective_holdout", score="0.9",
           hit="1", campaign="H", batch="HB", qc="PASS"):
    return {
        "design_id": design,
        "target_id": target,
        "epitope_id": target + "-E1",
        "binder_format": "VHH",
        "model_version": "SYN-MODEL",
        "campaign_id": campaign,
        "assay_batch": batch,
        "predicted_score": score,
        "observed_hit": hit,
        "qc_status": qc,
        "evaluation_split": split,
        "evidence_ref": "synthetic://" + design,
    }


class LoopBenchTests(unittest.TestCase):
    def test_duplicate_design_id_is_error(self):
        errors, _ = validate([record("D1", "T1"), record("D1", "T2")])
        self.assertTrue(any("duplicate design_id" in item for item in errors))

    def test_target_overlap_is_warning(self):
        _, warnings = validate([
            record("D1", "T1", "development", "0.3", "0", "DEV", "DB"),
            record("D2", "T1", "prospective_holdout", "0.8", "1", "HOLD", "HB"),
        ])
        self.assertTrue(any("target overlap" in item for item in warnings))

    def test_no_holdout_blocks_evaluation(self):
        result = evaluate([record("D1", "T1", "development")])
        self.assertEqual(result["status"], "BLOCKED")

    def test_failed_qc_is_not_used(self):
        rows = [
            record("D1", "T1", "prospective_holdout", "0.9", "1", qc="FAIL"),
            record("D2", "T1", "prospective_holdout", "0.8", "0"),
            record("D3", "T2", "prospective_holdout", "0.9", "0", "C2", "B2"),
        ]
        result = evaluate(rows, top_k=1)
        self.assertEqual(result["prospective_holdout_qc_pass_rows"], 2)
        self.assertEqual(result["selected_rows"], 2)

    def test_top_k_is_stratified_per_target(self):
        rows = [
            record("D1", "T1", "prospective_holdout", "0.9", "1"),
            record("D2", "T1", "prospective_holdout", "0.8", "1"),
            record("D3", "T1", "prospective_holdout", "0.1", "0"),
            record("D4", "T2", "prospective_holdout", "0.9", "0", "C2", "B2"),
            record("D5", "T2", "prospective_holdout", "0.8", "0", "C2", "B2"),
            record("D6", "T2", "prospective_holdout", "0.1", "1", "C2", "B2"),
        ]
        result = evaluate(rows, top_k=1)
        self.assertEqual(result["selected_rows"], 2)
        self.assertAlmostEqual(result["top_k_holdout_hit_rate"], 0.5)

    def test_cluster_interval_requires_three_targets(self):
        rows = [
            record("D1", "T1", "prospective_holdout", "0.9", "1"),
            record("D2", "T2", "prospective_holdout", "0.9", "0", "C2", "B2"),
        ]
        result = evaluate(rows, top_k=1)
        self.assertIsNone(result["top_k_hit_rate_target_cluster_bootstrap_95ci"])


if __name__ == "__main__":
    unittest.main()
