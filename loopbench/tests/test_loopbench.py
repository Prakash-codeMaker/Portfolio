import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from loopbench import validate,evaluate
def row(d,t,split="prospective_holdout",score="0.9",hit="1",campaign="H",batch="HB"):
 return {"design_id":d,"target_id":t,"epitope_id":t+"-E1","binder_format":"VHH","model_version":"m1","campaign_id":campaign,"assay_batch":batch,"predicted_score":score,"observed_hit":hit,"qc_status":"PASS","evaluation_split":split,"evidence_ref":"demo://"+d}
class Tests(unittest.TestCase):
 def test_duplicate_ids(self):
  e,_=validate([row("D1","T1"),row("D1","T2")]);self.assertTrue(any("duplicate" in x for x in e))
 def test_target_overlap_warning(self):
  _,w=validate([row("D1","T1","development",".4","0","D","DB"),row("D2","T1")]);self.assertTrue(any("Target leakage" in x for x in w))
 def test_missing_holdout_blocks(self):self.assertEqual(evaluate([row("D1","T1","development")])["status"],"BLOCKED")
 def test_topk_per_target(self):
  rs=[row("D1","T1","prospective_holdout",".9","1"),row("D2","T1","prospective_holdout",".8","1"),row("D3","T1","prospective_holdout",".1","0"),row("D4","T2","prospective_holdout",".9","0","H2","HB2"),row("D5","T2","prospective_holdout",".8","0","H2","HB2"),row("D6","T2","prospective_holdout",".1","1","H2","HB2")]
  x=evaluate(rs,1);self.assertEqual(x["prospective_holdout_rows"],6);self.assertEqual(x["selected_rows"],2);self.assertAlmostEqual(x["top_k_holdout_hit_rate"],.5)
if __name__=="__main__":unittest.main()
