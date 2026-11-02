"""Session-private real-engine public-observation masked action-family BC diagnostic."""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from .baseline import BaselinePolicy
from .contract import verify_engine
from .validate_receipt import validate

SID = "s-20261102-73729553"
# Pinned upstream crates/taverngym/src/actions.rs. All 245 indices exactly partitioned.
FAMILIES = (("end",0,1),("refresh",1,2),("freeze",2,3),
 ("upgrade",3,4),("hero_power",4,6),("dark_gift",6,7),("cancel",7,8),
 ("buy",8,16),("sell",16,23),("activate",23,30),("choose",30,46),
 ("play",46,126),("magnetize",126,196),("move",196,245))
# Own-player-only global fields from pinned upstream crates/taverngym/src/obs.rs.
IDX = (0,5,7,10,11,12,13,15,33,34)

def family(a):
    return next(i for i,(_,lo,hi) in enumerate(FAMILIES) if lo <= int(a) < hi)

def features(f,m,used):
    f=np.asarray(f,dtype=np.float32);m=np.asarray(m,dtype=bool)
    if f.shape!=(4017,) or m.shape!=(245,) or not m.any():raise ValueError("observe2/mask mismatch")
    avail=np.array([m[lo:hi].any() for _,lo,hi in FAMILIES],dtype=bool)
    counts=np.array([m[lo:hi].sum()/(hi-lo) for _,lo,hi in FAMILIES],dtype=np.float32)
    x=np.concatenate((f[list(IDX)],avail.astype(np.float32),counts,[min(used,100)/100.0]))
    if not np.isfinite(x).all():raise ValueError("nonfinite public features")
    return x,avail

def bc_action(f,m,used,w):
    x,avail=features(f,m,used)
    if w.shape!=(len(x),len(FAMILIES)):raise ValueError("bad BC weights")
    logits=x@w;logits[~avail]=-1e9
    _,lo,hi=FAMILIES[int(logits.argmax())]
    options=np.flatnonzero(np.asarray(m,dtype=bool)[lo:hi])
    return int(lo+options[0])

def score(rows,w):
    return float(np.mean([np.argmax(np.where(av,x@w,-1e9))==y for x,av,y in rows]))

def fit(rows,steps=250):
    if not rows:raise ValueError("empty training set")
    x=np.stack([a for a,_,_ in rows]).astype(np.float64)
    av=np.stack([b for _,b,_ in rows]);y=np.array([c for _,_,c in rows])
    if not av[np.arange(len(y)),y].all():raise ValueError("illegal teacher label")
    w=np.random.default_rng(73729553).normal(0,.01,(x.shape[1],len(FAMILIES)))
    for _ in range(steps):
        logits=x@w;logits[~av]=-1e6;logits-=logits.max(axis=1,keepdims=True)
        p=np.exp(logits);p/=p.sum(axis=1,keepdims=True)
        p[np.arange(len(y)),y]-=1;p[~av]=0
        w-=.35*(x.T@p/len(y)+.0005*w)
    return w,{"gradient_updates":steps,"examples":len(rows),
              "training_accuracy":score(rows,w),
              "labels":dict(Counter(FAMILIES[i][0] for i in y))}

def match(seed,policy,w=None,digest=None,capture=False):
    import taverngym
    engine=verify_engine()
    game=taverngym.Game(seed=int(seed));teacher=BaselinePolicy()
    turn_old=-1;used=0;decisions=0;guard=0;only_end=0
    counts=Counter();rows=[]
    for _ in range(30000):
        if game.is_over():break
        turn=int(game.turn)
        if turn!=turn_old:turn_old=turn;used=0
        progressed=False
        for seat in range(game.num_players):
            if not game.needs_action(seat):continue
            progressed=True
            if seat!=0:game.bot_play(seat);continue
            fb,cb=game.observe2(0)
            f=np.frombuffer(fb,dtype="<f4").copy()
            cards=np.frombuffer(cb,dtype="<i4").copy()
            m=np.frombuffer(game.legal_mask(0),dtype=np.uint8).astype(bool)
            if cards.shape!=(447,):raise ValueError("card observation contract")
            only_end+=int(m.sum()==1 and m[0])
            if policy=="baseline":
                a=teacher.act({"features":f,"cards":cards,"action_mask":m},
                              {"turn":turn,"actions_used":used})
                guard+=int(used>=85 and m[0] and not m[30:46].any())
            elif policy=="bc_category":
                if w is None:raise ValueError("missing learned weights")
                a=bc_action(f,m,used,w)
            else:raise ValueError("unknown policy")
            if not m[int(a)]:raise ValueError("illegal action")
            if capture:
                x,av=features(f,m,used);rows.append((x,av,family(a)))
            counts[FAMILIES[family(a)][0]]+=1
            game.step(0,int(a));used+=1;decisions+=1
        if not progressed and not game.is_over():raise RuntimeError("unfinished stalled game")
    if not game.is_over():raise RuntimeError("full-game safety limit")
    receipt={"schema":1,"timestamp":datetime.now(timezone.utc).isoformat(),
      "environment":"TavernGym","engine_version":engine["version"],
      "engine_source_hash":engine["source_hash"],"agent_id":SID,
      "policy":policy,"seed":int(seed),"completed":True,"turns":int(game.turn),
      "decisions":decisions,"placements":[int(a) for a in game.placements()],
      "truncated_combats":int(game.truncated_combats),"turn_limit_end":bool(game.turn_limit_end),
      "model_sha256":digest if policy=="bc_category" else None,
      "action_families":dict(counts),"baseline_85_action_guard":guard,
      "only_end_legal":only_end,"extra_bc_guard":0}
    validate(receipt)
    return receipt,rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--receipts-dir",type=Path,required=True)
    p.add_argument("--report-dir",type=Path,required=True)
    a=p.parse_args()
    a.receipts_dir.mkdir(parents=True,exist_ok=True)
    a.report_dir.mkdir(parents=True,exist_ok=True)
    training_seeds=[67010,67011,67012];heldout_seeds=[67020,67021]
    pair_seeds=[67030,67031,67032]
    rows=[]
    for seed in training_seeds:rows.extend(match(seed,"baseline",capture=True)[1])
    w,fit_report=fit(rows)
    checkpoint={"schema":1,"session":SID,"algorithm":"masked_linear_action_family_BC",
      "teacher":"V0 BaselinePolicy with public-only observations",
      "feature_indices":list(IDX),"families":[x[0] for x in FAMILIES],
      "train_seeds":training_seeds,"gradient_updates":250,
      "engine":verify_engine(),"weights":w.tolist()}
    data=(json.dumps(checkpoint,sort_keys=True,separators=(",",":"))+"\n").encode()
    (a.report_dir/"001-checkpoint.json").write_bytes(data)
    digest=hashlib.sha256(data).hexdigest()
    held=[]
    for seed in heldout_seeds:held.extend(match(seed,"baseline",capture=True)[1])
    games=[]
    for seed,policy in [(67029,"bc_category")]+[(s,p) for s in pair_seeds for p in ("baseline","bc_category")]:
        rec,_=match(seed,policy,w if policy=="bc_category" else None,digest)
        path=a.receipts_dir/f"001-{policy}-{seed}.json"
        path.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+"\n")
        games.append({"seed":seed,"policy":policy,"rank":rec["placements"][0],
           "decisions":rec["decisions"],"actions":rec["action_families"],
           "baseline_guard":rec["baseline_85_action_guard"],
           "only_end_legal":rec["only_end_legal"],"receipt":str(path)})
    summary={}
    for name in ("baseline","bc_category"):
        ranks=[g["rank"] for g in games if g["seed"] in pair_seeds and g["policy"]==name]
        summary[name]={"n":len(ranks),"ranks":ranks,"mean_rank":float(np.mean(ranks)),
                       "top4_rate":float(np.mean(np.array(ranks)<=4)),
                       "first_rate":float(np.mean(np.array(ranks)==1))}
    report={"session":SID,"rule_version":verify_engine(),"teacher":"V0 baseline",
      "training_seeds":training_seeds,"heldout_seeds":heldout_seeds,
      "comparison_seeds":pair_seeds,"training":fit_report,
      "heldout_examples":len(held),"heldout_family_accuracy":score(held,w),
      "model_sha256":digest,"ppo_steps":0,
      "paired_results":summary,"games":games,
      "caveat":"Action-family imitation is not card understanding or competitive strength; baseline teacher is weak."}
    (a.report_dir/"001-results.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"train":fit_report,"heldout_family_accuracy":score(held,w),
                      "paired_results":summary,"model_sha256":digest,"games":len(games)}))

if __name__=="__main__":main()
