"""Seeded evaluation with optional paired baseline; no Elo or significance claim."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
from .canary import run

def summarize(records:list[dict])->dict:
    placements=[r["placements"][0] for r in records]
    return {"games":len(records),"mean_placement":statistics.mean(placements),
        "top4_rate":sum(x<=4 for x in placements)/len(records),
        "first_place_rate":sum(x==1 for x in placements)/len(records),
        "placements":placements,"seeds":[r["seed"] for r in records]}

def evaluate(games:int,start_seed:int,model:Path|None=None,compare_baseline:bool=False)->dict:
    if not 1<=games<=100:raise ValueError("games must be 1..100")
    if compare_baseline and model is None:raise ValueError("Comparison requires a model")
    policy="model" if model is not None else "baseline"
    candidate=[run(start_seed+i,"evaluation",policy,str(model) if model is not None else None)
               for i in range(games)]
    report={"policy":policy,"candidate":summarize(candidate),"seed_start":start_seed,
        "comparison":"seven scripted TavernGym bots, not Arena Elo",
        "inference":"Descriptive results only; small samples do not establish improvement"}
    if compare_baseline:
        baseline=[run(start_seed+i,"evaluation","baseline") for i in range(games)]
        report["baseline"]=summarize(baseline)
        report["paired_mean_placement_delta"]=report["candidate"]["mean_placement"]-report["baseline"]["mean_placement"]
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--model",type=Path)
    p.add_argument("--compare-baseline",action="store_true")
    p.add_argument("--games",type=int,default=3)
    p.add_argument("--start-seed",type=int,default=24000)
    p.add_argument("--out",type=Path,default=Path("artifacts/evaluation.json"))
    a=p.parse_args()
    if a.model is not None and not a.model.is_file():p.error("Checkpoint not found")
    report=evaluate(a.games,a.start_seed,a.model,a.compare_baseline)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))

if __name__=="__main__":main()
