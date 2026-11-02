"""Pinned-engine, public-observation behavioral cloning of TavernGym's bot_action.
An isolated research candidate, not the shared baseline or production model.
"""
from __future__ import annotations
import argparse, hashlib, json, os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SID = "s-20261102-4d619f26"
BASE = "315b068bac5ab6d8403c3c9b18f8c101c0cded5d"
GROUPS = (("end",0,1),("refresh",1,2),("freeze",2,3),("upgrade",3,4),
 ("hero",4,6),("dark_gift",6,7),("cancel",7,8),("buy",8,16),
 ("sell",16,23),("activate",23,30),("choose",30,46),("play",46,126),
 ("magnetize",126,196),("move",196,245))

def family(a):
    if not 0 <= int(a) < ACTIONS: raise ValueError(a)
    return next(n for n,lo,hi in GROUPS if lo <= a < hi)

def encode(features, mask):
    f=np.asarray(features,dtype=np.float32)
    m=np.asarray(mask,dtype=bool)
    if f.shape!=(FEATURES,) or m.shape!=(ACTIONS,) or not m.any():
        raise ValueError("Bad public observation or legal action mask")
    if not np.isfinite(f[:42]).all(): raise ValueError("Nonfinite public features")
    # Only own public-global observation prefix (engine obs.rs), no other seats,
    # full state, future shop, RNG, opponent hidden hands or boards.
    return np.r_[np.clip(f[:42],-5,5),m.astype(np.float32)].astype(np.float32)

def observe(game):
    fb,cb=game.observe2(0)
    f=np.frombuffer(fb,dtype="<f4")
    c=np.frombuffer(cb,dtype="<i4")
    mask=np.frombuffer(game.legal_mask(0),dtype=np.uint8).astype(bool)
    if f.shape!=(FEATURES,) or c.shape!=(CARDS,):
        raise ValueError("Pinned engine contract mismatch")
    return encode(f,mask),f,c,mask

def network():
    from torch import nn
    return nn.Sequential(nn.Linear(42+ACTIONS,96),nn.Tanh(),
                         nn.Linear(96,96),nn.Tanh(),nn.Linear(96,ACTIONS))

def teacher_episode(seed):
    import taverngym
    game=taverngym.Game(seed=seed)
    xs,ms,ys=[],[],[]
    for _ in range(30000):
        if game.is_over(): break
        any_action=False
        for seat in range(game.num_players):
            if not game.needs_action(seat): continue
            any_action=True
            if seat:
                game.bot_play(seat)
                continue
            x,_,_,mask=observe(game)
            target=int(game.bot_action(0))
            if not mask[target]: raise RuntimeError("Teacher returned illegal action")
            xs.append(x); ms.append(mask); ys.append(target)
            game.step(0,target)
        if not any_action and not game.is_over(): raise RuntimeError("Teacher stalled")
    if not game.is_over() or game.turn_limit_end or game.truncated_combats:
        raise RuntimeError("Teacher match incomplete/truncated")
    return (np.asarray(xs,np.float32),np.asarray(ms,bool),np.asarray(ys,np.int64),
            {"seed":seed,"decisions":len(ys),"rank":int(game.placements()[0]),
             "turns":int(game.turn),"completed":True})

def examples(games):
    return tuple(np.concatenate([g[i] for g in games],axis=0) for i in range(3))

def train(games,seed=61926,epochs=8):
    import torch
    import torch.nn.functional as F
    torch.set_num_threads(2); torch.manual_seed(seed)
    model=network()
    x,m,y=examples(games)
    x=torch.from_numpy(x); m=torch.from_numpy(m); y=torch.from_numpy(y)
    opt=torch.optim.Adam(model.parameters(),lr=0.001)
    gen=torch.Generator().manual_seed(seed)
    loss_val=None
    for _ in range(epochs):
        for ids in torch.randperm(len(y),generator=gen).split(128):
            logits=model(x[ids]).masked_fill(~m[ids],-1e8)
            loss=F.cross_entropy(logits,y[ids])
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
            loss_val=float(loss.detach())
    model.eval()
    return model,loss_val

def student_action(model,x,mask):
    import torch
    with torch.no_grad():
        logits=model(torch.from_numpy(x).unsqueeze(0))[0].numpy()
    return int(np.argmax(np.where(mask,logits,-1e8)))

def diagnostic(model,games):
    x,m,y=examples(games)
    preds=np.asarray([student_action(model,x[i],m[i]) for i in range(len(y))])
    return {"n":int(len(y)),"exact_accuracy":float(np.mean(preds==y)),
        "family_accuracy":float(np.mean([family(a)==family(b) for a,b in zip(preds,y)])),
        "teacher_family_counts":dict(Counter(map(family,y.tolist()))),
        "student_family_counts":dict(Counter(map(family,preds.tolist())))}

def match(seed,mode,model=None,digest=None):
    import taverngym
    game=taverngym.Game(seed=seed)
    baseline=BaselinePolicy()
    last_turn=-1; used=0; decisions=0; counts=Counter()
    for _ in range(30000):
        if game.is_over(): break
        turn=int(game.turn)
        if turn!=last_turn: last_turn=turn; used=0
        progressed=False
        for seat in range(game.num_players):
            if not game.needs_action(seat): continue
            progressed=True
            if seat:
                game.bot_play(seat); continue
            x,f,c,mask=observe(game)
            if mode=="clone": action=student_action(model,x,mask)
            elif mode=="baseline": action=baseline.act(
                {"features":f,"cards":c,"action_mask":mask},
                {"turn":turn,"actions_used":used})
            elif mode=="official_teacher": action=int(game.bot_action(0))
            else: raise ValueError(mode)
            if not mask[action]: raise RuntimeError("Candidate produced illegal action")
            game.step(0,action); decisions+=1; used+=1; counts[family(action)]+=1
        if not progressed and not game.is_over(): raise RuntimeError("Match stalled")
    if not game.is_over(): raise RuntimeError("Raw candidate full-match driver cap")
    engine=verify_engine()
    receipt={"schema":1,"timestamp":datetime.now(timezone.utc).isoformat(),
       "environment":"TavernGym","engine_source_hash":engine["source_hash"],
       "engine_version":engine["version"],"agent_id":SID,"policy":mode,
       "seed":seed,"completed":True,"turns":int(game.turn),
       "decisions":decisions,"placements":[int(n) for n in game.placements()],
       "truncated_combats":int(game.truncated_combats),
       "turn_limit_end":bool(game.turn_limit_end),
       "git_sha":os.getenv("GITHUB_SHA",""),
       "model_sha256":digest if mode=="clone" else None,
       "research_forced_end_count":0,"action_families":dict(counts)}
    validate(receipt)
    return receipt

def stats(items):
    ranks=np.asarray([r["placements"][0] for r in items])
    return {"n":len(ranks),"ranks":ranks.tolist(),
      "mean_rank":float(ranks.mean()),"top4_rate":float((ranks<=4).mean()),
      "first_place_rate":float((ranks==1).mean()),
      "mean_decisions":float(np.mean([r["decisions"] for r in items]))}

def handoff(result):
    sid=SID
    session=Path("research/sessions")/sid
    proposal=Path("research/knowledge/proposals")/(sid+"-001.md")
    session.mkdir(parents=True,exist_ok=True); proposal.parent.mkdir(parents=True,exist_ok=True)
    sr=result["game_results"]; d=result["heldout_imitation"]
    details="\n".join(
      f"| {k} | {v['n']} | {v['ranks']} | {v['mean_rank']:.3f} | {v['top4_rate']:.3f} | {v['first_place_rate']:.3f} |"
      for k,v in sr.items())
    (session/"round-001.md").write_text(
      f"""# {sid} · Round 001 — public-observation teacher cloning

## Hypothesis and prior work
Main {BASE}. Main rules baseline and PPO both require gameplay skill evidence.
Other unmerged PRs target purchase/refresh/move/entropy; this experiment uses only isolated files.
Read docs/PROJECT_BACKGROUND.md, SESSION_PROTOCOL.md, CLOSED_LOOP.md,
and research/knowledge/INCIDENTS-20261102.md.

## Actual pinned engine mechanisms
TavernGym {result['engine']['version']} / source hash {result['engine']['source_hash']}.
Upstream pinned actions.rs: Buy 8..15, Sell 16..22, Choose 30..45,
Play 46..125, Magnetize 126..195, Move 196..244.
Teacher labels are real legal Game.bot_action(0) outputs.
Student uses only 42 public own/global features and 245 legal mask elements;
it cannot read opponent hidden information or game RNG.

## Actual training and testing
Mask-aware MLP behavior cloning; epochs={result['epochs']},
teacher matches={result['train_seeds']}, learner samples={result['training_samples']}.
Supervised held-out seeds={result['diagnostic_seeds']}; examples={d['n']},
exact action accuracy={d['exact_accuracy']:.4f}, family accuracy={d['family_accuracy']:.4f}.
Train final minibatch loss={result['final_loss']:.6f}.
No PPO steps were run; total PPO timesteps = 0.
Candidate checkpoint hash SHA256={result['model_sha256']}; restored successfully.
Model is an expiring Actions Artifact, not a permanent Champion.

## Genuine eight-seat independent matches
Paired seeds={result['match_seeds']}; seat 0 controlled by stated policy,
seven scripted TavernGym bots on all games. All receipts include placements and
action-family histograms. No research policy forced-end guard (count=0).
| Policy | Games | Seat-0 ranks | Mean rank | Top4 | First |
|---|---:|---|---:|---:|---:|
{details}
Mean paired clone minus baseline rank={result['paired_delta']:+.3f}.
Small sample: results are descriptive, not a strength proof; no Arena MMR inference.
Train/holdout/match seeds disjoint. Baseline and official teacher are separate policies.

## Result / promotion
RETEST: no statistical basis to declare strength improvement on n={len(result['match_seeds'])}
paired seeds; do not promote. No automatic PR merge.

## Reproduction
python -m pytest tests/test_teacher_clone_s4d619f26.py
bash scripts/bootstrap_engine.sh
python -m tavern_ai.teacher_clone_s4d619f26 --out-dir experiments/{sid} --report-dir reports/{sid}
Artifacts preserve candidate .pt for 30 days (if upload succeeded);
do not call this a durable model. The historical PRs are unmerged leads, not main facts.

## Next
Study why the public-only cloned policy disagrees with official teacher by action
family, especially shop card selection; validate source-derived card features before scaling PPO.
""",encoding="utf-8")
    (session/"STATUS.md").write_text(
      f"""# Current research status
Session: {sid}
Branch: agent/{sid}/optimization-001
Base main: {BASE}
Research phase: completed candidate pilot; awaiting PR integration review.
Actual training: supervised {result['training_samples']} labels, {result['epochs']} epochs; PPO steps 0.
Latest checkpoint: reports/{sid}/teacher-clone-candidate.pt in expiring Actions Artifact only.
Checkpoint SHA256: {result['model_sha256']}.
Validated best/champion: none; candidate only.
Evidence: experiments/{sid}/001-*.json and reports/{sid}/001-summary.json.
Current issue: unknown generalization to larger independent samples.
Resume: use the dedicated workflow and pinned engine; do not overwrite Champion.
PR: to be assigned after completed run; no direct merge.
""",encoding="utf-8")
    proposal.write_text(
      f"""# Proposal {sid} R001
- Learned: exact action bands verified against pinned upstream; masked legal-action
  teacher collection and public-only student training can be reproduced.
- Source: Tavergym bot_action (seven other bots), not a human expert.
- Measured holdout: action={d['exact_accuracy']:.4f},
  family={d['family_accuracy']:.4f} on {d['n']} independent decisions.
- Competition: {len(result['match_seeds'])} paired seeds,
  clone mean rank={sr['clone']['mean_rank']:.3f},
  baseline mean rank={sr['baseline']['mean_rank']:.3f}.
- No statistically verified improvement; promotion RETEST, not Champion.
- Never mix model and fallback results; zero research forced-end actions.
- Limitation: student deliberately omits card identities, so cannot reason
  about card-level synergy, Discover values or opponent hidden information.
- Next: extract simulator-verified card mechanics and train a card-aware learner,
  keeping a separate heldout test and paired eight-seat evaluations.
- Replay commands: see research/sessions/{sid}/round-001.md.
""",encoding="utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--report-dir",type=Path,required=True)
    a=p.parse_args()
    verify_engine()
    train_seeds=(61101,61102,61103,61104)
    diagnostic_seeds=(61211,61212)
    match_seeds=(61421,61422)
    train_games=[teacher_episode(s) for s in train_seeds]
    diag_games=[teacher_episode(s) for s in diagnostic_seeds]
    model,final_loss=train(train_games)
    diagnostic_result=diagnostic(model,diag_games)
    import torch
    a.out_dir.mkdir(parents=True,exist_ok=True)
    a.report_dir.mkdir(parents=True,exist_ok=True)
    saved=a.report_dir/"teacher-clone-candidate.pt"
    torch.save(model.state_dict(),saved)
    digest=hashlib.sha256(saved.read_bytes()).hexdigest()
    restored=network()
    restored.load_state_dict(torch.load(saved,map_location="cpu",weights_only=True))
    restored.eval()
    test_x,test_m,_=examples(diag_games)
    if student_action(model,test_x[0],test_m[0])!=student_action(restored,test_x[0],test_m[0]):
        raise RuntimeError("Checkpoint restoration mismatch")
    records={k:[] for k in ("clone","baseline","official_teacher")}
    for seed in match_seeds:
        for mode in records:
            r=match(seed,mode,restored,digest)
            (a.out_dir/f"001-{seed}-{mode}.json").write_text(
                json.dumps(r,indent=2),encoding="utf-8")
            records[mode].append(r)
    summary={ "session":SID, "base_main_sha":BASE, "engine":verify_engine(),
       "algorithm":"masked behavior cloning MLP(287,96,96,245)",
       "train_seeds":train_seeds, "diagnostic_seeds":diagnostic_seeds,
       "match_seeds":match_seeds, "epochs":8,
       "training_samples":len(examples(train_games)[2]),"final_loss":final_loss,
       "heldout_imitation":diagnostic_result,
       "model_sha256":digest, "checkpoint_restored":True,
       "checkpoint_persistent":False,
       "game_results":{k:stats(v) for k,v in records.items()},
       "paired_delta":float(np.mean([
           records["clone"][i]["placements"][0]-records["baseline"][i]["placements"][0]
           for i in range(len(match_seeds))])),
       "research_forced_end_count":0,"promotion":"RETEST"}
    (a.report_dir/"001-summary.json").write_text(
        json.dumps(summary,indent=2),encoding="utf-8")
    handoff(summary)
    print(json.dumps(summary,ensure_ascii=False))

if __name__=="__main__": main()
