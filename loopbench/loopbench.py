#!/usr/bin/env python3
"""LoopBench CSV validation and prospective top-k diagnostics. Standard library only."""
import argparse,csv,json,random,statistics
from pathlib import Path
REQUIRED=["design_id","target_id","epitope_id","binder_format","model_version","campaign_id","assay_batch","predicted_score","observed_hit","qc_status","evaluation_split","evidence_ref"]
def read_csv(path):
    with open(path,newline="",encoding="utf-8-sig") as f:
        r=csv.DictReader(f)
        if not r.fieldnames: raise ValueError("CSV has no header")
        missing=[x for x in REQUIRED if x not in r.fieldnames]
        if missing: raise ValueError("Missing required columns: "+", ".join(missing))
        return list(r)
def validate(rows):
    errors=[];warnings=[];seen=set()
    for i,r in enumerate(rows,2):
        did=(r.get("design_id") or "").strip()
        if not did: errors.append(f"Row {i}: blank design_id")
        elif did in seen: errors.append(f"Row {i}: duplicate design_id {did}")
        seen.add(did)
        for k in ["target_id","epitope_id","binder_format","model_version","campaign_id","assay_batch","evidence_ref"]:
            if not (r.get(k) or "").strip(): errors.append(f"Row {i}: blank {k}")
        try:
            s=float(r["predicted_score"])
            if not 0<=s<=1: errors.append(f"Row {i}: predicted_score outside [0,1]")
        except Exception: errors.append(f"Row {i}: non-numeric predicted_score")
        if r.get("observed_hit") not in ("0","1"): errors.append(f"Row {i}: observed_hit must be 0 or 1")
        if r.get("qc_status") not in ("PASS","FAIL","REVIEW"): errors.append(f"Row {i}: invalid qc_status")
        if r.get("evaluation_split") not in ("development","prospective_holdout","retrospective"): errors.append(f"Row {i}: invalid evaluation_split")
    dev=[r for r in rows if r.get("evaluation_split")=="development"];hold=[r for r in rows if r.get("evaluation_split")=="prospective_holdout"]
    if not hold: warnings.append("No prospective_holdout rows: do not report prospective performance.")
    if dev and hold:
        for key,label in [("target_id","Target"),("campaign_id","Campaign"),("assay_batch","Assay-batch")]:
            overlap={r.get(key) for r in dev}&{r.get(key) for r in hold}
            if overlap: warnings.append(f"{label} leakage risk: {len(overlap)} {key} value(s) overlap across splits.")
    if len(rows)<30: warnings.append("Small dataset: descriptive results only.")
    return errors,warnings
def mean(v): return statistics.mean(v) if v else None
def bootstrap_ci(values,n_boot=1000,seed=7):
    if not values:return None
    rng=random.Random(seed);n=len(values);m=sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(n_boot))
    return [m[int(.025*n_boot)],m[int(.975*n_boot)-1]]
def evaluate(rows,k=5):
    hold=[r for r in rows if r.get("evaluation_split")=="prospective_holdout" and r.get("qc_status")=="PASS"]
    dev=[r for r in rows if r.get("evaluation_split")=="development" and r.get("qc_status")=="PASS"]
    if not hold:return {"status":"BLOCKED","reason":"No QC-PASS prospective_holdout rows. Development or retrospective rows cannot substitute."}
    by={}
    for r in hold:by.setdefault(r["target_id"],[]).append(r)
    selected=[]
    for group in by.values():selected.extend(sorted(group,key=lambda x:float(x["predicted_score"]),reverse=True)[:k])
    base=mean([int(r["observed_hit"]) for r in hold]);top=mean([int(r["observed_hit"]) for r in selected])
    return {"status":"DESCRIPTIVE_HOLDOUT_EVALUATION","dataset_rows":len(rows),"development_qc_pass_rows":len(dev),"prospective_holdout_rows":len(hold),"holdout_targets":len(by),"top_k_per_target":k,"selected_rows":len(selected),"baseline_holdout_hit_rate":base,"top_k_holdout_hit_rate":top,"descriptive_enrichment_lift":top/base if base else None,"top_k_hit_rate_bootstrap_95ci":bootstrap_ci([int(r["observed_hit"]) for r in selected]),"evidence_completeness":sum(bool(r.get("evidence_ref")) for r in hold)/len(hold),"disclaimer":"Descriptive statistics from user-supplied CSV; not a biological conclusion or independent validation."}
def main():
    p=argparse.ArgumentParser();sp=p.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("validate");a.add_argument("csv")
    b=sp.add_parser("evaluate");b.add_argument("csv");b.add_argument("--top-k",type=int,default=5);b.add_argument("--out")
    x=p.parse_args()
    try: rows=read_csv(x.csv);errors,warnings=validate(rows)
    except Exception as e: print(json.dumps({"status":"ERROR","error":str(e)},indent=2));return 2
    if x.cmd=="validate":result={"status":"VALID" if not errors else "INVALID","rows":len(rows),"errors":errors,"warnings":warnings}
    else:
        result={"validation":{"status":"VALID" if not errors else "INVALID","errors":errors,"warnings":warnings},"evaluation":evaluate(rows,x.top_k) if not errors and x.top_k>0 else {"status":"BLOCKED","reason":"Fix schema errors and use top-k >= 1."}}
        if x.out:Path(x.out).write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2));return 0 if not errors else 1
if __name__=="__main__":raise SystemExit(main())
