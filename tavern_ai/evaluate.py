"""Independent seeded evaluation; results are not TavernArena Elo."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
from .canary import run

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--model",type=Path,required=True)
    p.add_argument("--games",type=int,default=3)
    p.add_argument("--start-seed",type=int,default=24000)
    p.add_argument("--out",type=Path,default=Path("artifacts/evaluation.json"))
    a=p.parse_args()
    if a.games<1 or a.games>100:raise ValueError("games must be 1..100")
    records=[run(a.start_seed+i,"evaluation","model",str(a.model)) for i in range(a.games)]
    placements=[r["placements"][0] for r in records]
    report={"games":len(records),"mean_placement":statistics.mean(placements),
      "top4_rate":sum(x<=4 for x in placements)/len(records),
      "first_place_rate":sum(x==1 for x in placements)/len(records),
      "placements":placements,"seed_start":a.start_seed,
      "comparison":"seven scripted TavernGym bots, not arena players"}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
