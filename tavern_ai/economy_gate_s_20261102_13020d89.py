"""Public-observation board-aware economy policy search; not neural PPO."""
from __future__ import annotations
import json, os, hashlib, statistics, argparse
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from .baseline import BaselinePolicy
from .contract import ACTIONS, FEATURES, CARDS, verify_engine
from .validate_receipt import validate

SID="s-20261102-13020d89"
BASE="315b068bac5ab6d8403c3c9b18f8c101c0cded5d"
TRAIN=(73010,73011)
TEST=(73020,73021,73022,73023)
CANARY=73030
THRESHOLDS=(2,5)

class EconomyGatePolicy:
    """Upgrade-vs-buy choice using own public board/health and legal mask only."""
    def __init__(self, min_board):
        if min_board not in THRESHOLDS: raise ValueError("bad parameter")
        self.min_board=min_board
        self.base=BaselinePolicy()
        self.deferred=0
    def act(self, obs, context=None):
        context=context or {}
        m=np.asarray(obs["action_mask"],dtype=bool)
        f=np.asarray(obs["features"],dtype=np.float32)
        if m.shape!=(ACTIONS,) or not m.any(): raise ValueError("bad legal mask")
        if f.shape!=(FEATURES,) or not np.isfinite(f).all(): raise ValueError("bad public features")
        # obs.rs global features 5 health/40, 10 tier/6, 33 board_size/7.
        health=float(f[5])*40
        board=int(round(float(f[33])*7))
        if not (-2<=health<=200 and 0<=board<=7):
            raise ValueError("observe2 offsets incompatible with pinned upstream")
        turn=int(context.get("turn",0)); used=int(context.get("actions_used",0))
        buy=np.flatnonzero(m[8:16])
        if (turn in (2,5,7,9,11) and used<85 and m[3]
            and len(buy)>0 and not m[30:196].any()
            and board<self.min_board and (turn<=5 or health<=24)):
            self.deferred+=1
            return 8+int(buy[0])
        return self.base.act(obs,context)

def match(seed,label,threshold=None):
    import taverngym
    engine=verify_engine()
    game=taverngym.Game(seed=seed)
    policy=BaselinePolicy() if threshold is None else EconomyGatePolicy(threshold)
    decisions=buys=upgrades=guards=0
    used=0; last=-1
    for _ in range(30000):
        if game.is_over(): break
        turn=int(game.turn)
        if turn!=last: last,used=turn,0
        progressed=False
        for seat in range(game.num_players):
            if not game.needs_action(seat): continue
            progressed=True
            if seat!=0:
                game.bot_play(seat)
                continue
            fb,cb=game.observe2(0)
            obs={"features":np.frombuffer(fb,dtype="<f4").copy(),
                 "cards":np.frombuffer(cb,dtype="<i4").copy(),
                 "action_mask":np.frombuffer(game.legal_mask(0),dtype=np.uint8).astype(bool)}
            if obs["cards"].shape!=(CARDS,): raise ValueError("card contract mismatch")
            a=int(policy.act(obs,{"turn":turn,"actions_used":used}))
            if not (0<=a<ACTIONS and obs["action_mask"][a]):
                raise RuntimeError("illegal selected action")
            guards+=int(a==0 and used>=85)
            buys+=int(8<=a<16)
            upgrades+=int(a==3)
            game.step(0,a); decisions+=1; used+=1
        if not progressed and not game.is_over(): raise RuntimeError("engine stalled")
    if not game.is_over(): raise RuntimeError("full-game safety limit")
    receipt={"schema":1,"timestamp":datetime.now(timezone.utc).isoformat(),
        "environment":"TavernGym","engine_source_hash":engine["source_hash"],
        "engine_version":engine["version"],"agent_id":SID,"policy":label,
        "seed":seed,"completed":True,"turns":int(game.turn),
        "decisions":decisions,"placements":[int(x) for x in game.placements()],
        "truncated_combats":int(game.truncated_combats),
        "turn_limit_end":bool(game.turn_limit_end),"git_sha":os.getenv("GITHUB_SHA",""),
        "model_sha256":None,"min_board":threshold,"deferred_upgrades":getattr(policy,"deferred",0),
        "buys":buys,"upgrades":upgrades,"budget_guard_ends":guards}
    validate(receipt)
    print("MATCH_RESULT="+json.dumps(receipt,sort_keys=True),flush=True)
    return receipt

def summary(rows):
    if not rows: raise ValueError("no rows")
    p=[r["placements"][0] for r in rows]
    return {"n":len(p),"ranks":p,"mean_rank":statistics.mean(p),
        "top4_rate":sum(x<=4 for x in p)/len(p),
        "first_rate":sum(x==1 for x in p)/len(p),
        "upgrade_deferrals":sum(r["deferred_upgrades"] for r in rows),
        "budget_guard_ends":sum(r["budget_guard_ends"] for r in rows)}

def save(path,body):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(body,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")

def experiment():
    exp=Path("experiments")/SID; reports=Path("reports")/SID
    train={}
    for t in THRESHOLDS:
        rows=[]
        for seed in TRAIN:
            r=match(seed,"economy_gate_train",t)
            save(exp/f"001-train-t{t}-{seed}.json",r);rows.append(r)
        train[str(t)]=summary(rows)
    # Held-out seeds are never used for selection.
    best=min(THRESHOLDS,key=lambda t:(train[str(t)]["mean_rank"],t))
    cfg={"session_id":SID,"base_sha":BASE,"train_seeds":list(TRAIN),
         "search_trials":len(THRESHOLDS),"train_games":len(TRAIN)*len(THRESHOLDS),
         "selected_min_board":best,"ppo_steps":0,"gradient_updates":0,
         "kind":"rule_parameter_search_not_a_neural_checkpoint"}
    configpath=reports/"001-policy.json";save(configpath,cfg)
    canary=match(CANARY,"economy_gate_canary",best)
    save(exp/f"001-canary-{CANARY}.json",canary)
    pairs={"baseline":[],"candidate":[]}
    for seed in TEST:
        for label,threshold in (("baseline",None),("candidate",best)):
            r=match(seed,label if threshold is None else "economy_gate",threshold)
            save(exp/f"001-{label}-{seed}.json",r)
            pairs[label].append(r)
    old=summary(pairs["baseline"]);new=summary(pairs["candidate"])
    result={"session_id":SID,"base_sha":BASE,"train":train,"selected_min_board":best,
        "config_sha256":hashlib.sha256(configpath.read_bytes()).hexdigest(),
        "engine_version":canary["engine_version"],"engine_source_hash":canary["engine_source_hash"],
        "canary":{"seed":CANARY,"rank":canary["placements"][0],"completed":True},
        "heldout_seeds":list(TEST),"baseline":old,"candidate":new,
        "paired_mean_rank_delta":round(new["mean_rank"]-old["mean_rank"],4),
        "complete_eight_seat_games":1+len(TRAIN)*len(THRESHOLDS)+2*len(TEST),
        "ppo_steps":0,"recommendation":"RETEST",
        "caution":"Only four independent seeds, protected baseline 85-action end cap; no MMR claim."}
    save(reports/"001-results.json",result)
    print("EXPERIMENT_RESULT="+json.dumps(result,sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    experiment()
