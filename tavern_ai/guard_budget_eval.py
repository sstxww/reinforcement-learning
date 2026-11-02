"""Paired guarded PPO budget evaluation over genuine TavernGym receipts."""
import argparse, json, statistics
from pathlib import Path
from .validate_receipt import validate

def summarize(rows):
    placements = [r["placements"][0] for r in rows]
    return {
        "games":len(rows),"placements":placements,
        "mean_placement":statistics.mean(placements),
        "top4_rate":sum(x<=4 for x in placements)/len(rows),
        "first_place_rate":sum(x==1 for x in placements)/len(rows),
        "mean_decisions":statistics.mean(r["decisions"] for r in rows),
        "mean_interventions":statistics.mean(r["guard_interventions"] for r in rows),
        "decisions":[r["decisions"] for r in rows],
        "interventions":[r["guard_interventions"] for r in rows]
    }

def paired_summary(low, high, low_budget=16, high_budget=32):
    if not low or not high:
        raise ValueError("Both groups need genuine game receipts")
    def index(rows,budget):
        index={}
        for r in rows:
            validate(r)
            if r.get("policy")!="model_guarded" or r.get("guard_max_turn_actions")!=budget:
                raise ValueError("Incorrect guard budget or policy")
            if r["seed"] in index: raise ValueError("Duplicate seed")
            index[r["seed"]]=r
        return index
    lo,hi=index(low,low_budget),index(high,high_budget)
    if set(lo)!=set(hi):raise ValueError("Unpaired seeds")
    seeds=sorted(lo)
    l=[lo[s] for s in seeds]
    h=[hi[s] for s in seeds]
    hashes={r.get("model_sha256") for r in l+h}
    if len(hashes)!=1 or None in hashes:raise ValueError("Inconsistent checkpoint")
    if any(a["engine_source_hash"]!=b["engine_source_hash"] for a,b in zip(l,h)):
        raise ValueError("Mismatched engine")
    a,b=summarize(l),summarize(h)
    return {
        "schema":1,"experiment":"guard_budget_ablation",
        "seeds":seeds,"low_budget":low_budget,"high_budget":high_budget,
        "model_sha256":next(iter(hashes)),
        "low":a,"high":b,
        "paired_rank_delta_low_minus_high":[x["placements"][0]-y["placements"][0] for x,y in zip(l,h)],
        "mean_rank_delta_low_minus_high":a["mean_placement"]-b["mean_placement"],
        "mean_decisions_delta_low_minus_high":a["mean_decisions"]-b["mean_decisions"],
        "interpretation":"Descriptive; small seed sets cannot prove strength improvement"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--lower",nargs="+",required=True,type=Path)
    p.add_argument("--higher",nargs="+",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=paired_summary(
        [json.loads(p.read_text(encoding="utf-8")) for p in args.lower],
        [json.loads(p.read_text(encoding="utf-8")) for p in args.higher]
    )
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print("SUMMARY_JSON="+json.dumps(result,separators=(",",":")))

if __name__=="__main__":main()
