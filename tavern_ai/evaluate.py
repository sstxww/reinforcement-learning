"""Independent seeded evaluation of either a learned model or the rule baseline."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
from .canary import run

def evaluate(policy:str,model:Path|None,games:int,start_seed:int):
    if games<1 or games>100:raise ValueError("games must be 1..100")
    if policy not in ("baseline","model"):raise ValueError("Unknown policy")
    if policy=="model" and (model is None or not model.is_file()):
        raise FileNotFoundError("Model evaluation requires a checkpoint")
    records=[run(start_seed+i,"evaluation",policy,str(model) if model else None)
             for i in range(games)]
    placements=[r["placements"][0] for r in records]
    return {"schema":2,"environment":"TavernGym","policy":policy,
       "model":str(model) if model else None,
       "engine_version":records[0]["engine_version"],
       "engine_source_hash":records[0]["engine_source_hash"],
       "games":len(records),"mean_placement":statistics.mean(placements),
       "top4_rate":sum(x<=4 for x in placements)/len(records),
       "first_place_rate":sum(x==1 for x in placements)/len(records),
       "placements":placements,"seeds":[r["seed"] for r in records],
       "receipts":records,
       "comparison":"seven scripted TavernGym bots, not arena players"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--policy",choices=["model","baseline"],default="model")
    p.add_argument("--model",type=Path)
    p.add_argument("--games",type=int,default=3)
    p.add_argument("--start-seed",type=int,default=24000)
    p.add_argument("--out",type=Path,default=Path("artifacts/evaluation.json"))
    a=p.parse_args()
    result=evaluate(a.policy,a.model,a.games,a.start_seed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="receipts"},ensure_ascii=False))
if __name__=="__main__":main()
