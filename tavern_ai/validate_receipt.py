"""Validate complete eight-seat TavernGym match receipts."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def validate(p:dict):
    if p.get("environment")!="TavernGym" or p.get("completed") is not True:
        raise ValueError("Incomplete/non-TavernGym game")
    if not isinstance(p.get("agent_id"),str) or not p["agent_id"].strip():
        raise ValueError("Missing agent")
    places=p.get("placements")
    if not isinstance(places,list) or len(places)!=8 or any(type(x)!=int or x<1 or x>8 for x in places):
        raise ValueError("Invalid eight-seat placement result")
    if type(p.get("turns"))!=int or p["turns"]<=0 or type(p.get("decisions"))!=int or p["decisions"]<=0:
        raise ValueError("Missing real game decisions/turns")
    if p.get("truncated_combats",0) or p.get("turn_limit_end",False):
        raise ValueError("Simulator guard was triggered")
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("receipt",type=Path)
    a=parser.parse_args()
    p=json.loads(a.receipt.read_text(encoding="utf-8"))
    validate(p)
    print(f"Verified match: agent={p['agent_id']} placement={p['placements'][0]}")
if __name__=="__main__":main()
