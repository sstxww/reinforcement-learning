"""Session-isolated masked behavior cloning on genuine TavernGym observe2 trajectories.

Only public numeric/card observations, legal action mask, turn, and per-turn
decision count enter the student. No hidden opponent state or RNG is used.
"""
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
import numpy as np
from tavern_ai.baseline import BaselinePolicy
from tavern_ai.contract import FEATURES, CARDS, ACTIONS, verify_engine
from tavern_ai.validate_receipt import validate

SESSION = "s-20261102-1f73f4a5"
BASE_SHA = "315b068bac5ab6d8403c3c9b18f8c101c0cded5d"

def encode_features(features, turn, used):
    f = np.asarray(features, dtype=np.float32)
    if f.shape != (FEATURES,) or not np.isfinite(f).all():
        raise ValueError("invalid public observation features")
    v = np.arcsinh(np.clip(f, -500, 500) / 5).astype(np.float32)
    return np.concatenate([v, np.array([min(turn,30)/30, min(used,100)/100], dtype=np.float32)])

def choose_legal(logits, mask, used=0, guard=True):
    scores = np.asarray(logits, dtype=np.float32)
    legal = np.asarray(mask, dtype=bool)
    if scores.shape != (ACTIONS,) or legal.shape != (ACTIONS,) or not legal.any() or not np.isfinite(scores).all():
        raise ValueError("invalid logits or legal mask")
    forced = bool(guard and used >= 85 and legal[0])
    if forced:
        return 0, True
    return int(np.argmax(np.where(legal, scores, -np.inf))), False

def build_model(n_cards):
    import torch
    from torch import nn
    class Student(nn.Module):
        def __init__(self):
            super().__init__()
            self.embedding = nn.Embedding(n_cards, 6, padding_idx=0)
            self.num = nn.Sequential(nn.Linear(FEATURES+2, 96), nn.Tanh())
            self.card = nn.Sequential(nn.Linear(CARDS*6, 64), nn.Tanh())
            self.head = nn.Sequential(nn.Linear(160,128), nn.Tanh(), nn.Linear(128,ACTIONS))
        def forward(self, numbers, cards):
            return self.head(torch.cat([self.num(numbers), self.card(self.embedding(cards).flatten(1))], -1))
    return Student()

def observe(game):
    fbytes,cbytes = game.observe2(0)
    f = np.frombuffer(fbytes, dtype="<f4").copy()
    c = np.frombuffer(cbytes, dtype="<i4").copy()
    mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
    if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,) or not mask.any():
        raise ValueError("observe2 contract changed")
    return f,c,mask

def predict_student(model, f, c, mask, turn, used, guard):
    import torch
    with torch.no_grad():
        logits = model(torch.from_numpy(encode_features(f, turn, used))[None],
                       torch.from_numpy(c.astype(np.int64))[None])[0].numpy()
    return choose_legal(logits, mask, used=used, guard=guard)

def play(seed, policy="teacher", model=None, samples=None, guard=True, max_player_decisions=3000):
    import taverngym
    engine = verify_engine()
    game = taverngym.Game(seed=int(seed))
    teacher = BaselinePolicy()
    last_turn, used, decisions, forced = -1, 0, 0, 0
    for _ in range(30000):
        if game.is_over(): break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, used = turn, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat): continue
            progressed = True
            if seat:
                game.bot_play(seat)
                continue
            f,c,mask = observe(game)
            if policy == "teacher":
                action = teacher.act({"features":f,"cards":c,"action_mask":mask},
                                     {"turn":turn,"actions_used":used})
                override = bool(used>=85 and mask[0] and action==0)
                if samples is not None:
                    samples.append((encode_features(f,turn,used),c,mask,int(action)))
            elif policy == "student" and model is not None:
                action,override = predict_student(model,f,c,mask,turn,used,guard)
            else:
                raise ValueError("policy must be teacher or student with model")
            if not mask[action]: raise RuntimeError("illegal action selected")
            game.step(0,int(action))
            forced += int(override)
            used += 1
            decisions += 1
            if decisions>max_player_decisions:
                raise RuntimeError(f"player action budget exceeded: {decisions} seed={seed} policy={policy}")
        if not progressed and not game.is_over(): raise RuntimeError("game stalled")
    if not game.is_over(): raise RuntimeError("game did not complete")
    result = {"schema":1,"environment":"TavernGym","engine_source_hash":engine["source_hash"],
              "engine_version":engine["version"],"agent_id":SESSION,"policy":policy,"seed":int(seed),
              "completed":True,"turns":int(game.turn),"decisions":decisions,
              "placements":[int(x) for x in game.placements()],
              "truncated_combats":int(game.truncated_combats),"turn_limit_end":bool(game.turn_limit_end),
              "git_sha":os.getenv("GITHUB_SHA",""),"model_sha256":None,
              "safety_forced_ends":forced,"guard_enabled":bool(guard) if policy=="student" else True}
    validate(result)
    return result

def optimize(samples,n_cards,seed=173,epochs=5):
    import torch
    torch.set_num_threads(2)
    torch.manual_seed(seed)
    model=build_model(n_cards)
    model.train()
    numbers=torch.from_numpy(np.stack([s[0] for s in samples]))
    cards=torch.from_numpy(np.stack([s[1] for s in samples]).astype(np.int64))
    legal=torch.from_numpy(np.stack([s[2] for s in samples]))
    labels=torch.tensor([s[3] for s in samples],dtype=torch.long)
    assert bool(legal.gather(1,labels[:,None]).all()),"illegal teacher action"
    optim=torch.optim.Adam(model.parameters(),lr=0.0006)
    steps,losses=0,[]
    rng=np.random.default_rng(seed)
    for _ in range(epochs):
        for idx in np.array_split(rng.permutation(len(samples)),max(1,(len(samples)+127)//128)):
            logits=model(numbers[idx],cards[idx]).masked_fill(~legal[idx],-1e8)
            loss=torch.nn.functional.cross_entropy(logits,labels[idx])
            optim.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
            optim.step()
            steps+=1
            losses.append(float(loss.detach()))
    model.eval()
    return model, {"gradient_steps":steps,"epochs":epochs,"final_minibatch_loss":losses[-1],
                   "teacher_samples":len(samples),"optimizer":"Adam","learning_rate":0.0006}

def teacher_agreement(model,samples):
    if not samples: raise ValueError("heldout samples required")
    import torch
    matches, legal_ok=0,0
    for f,c,mask,label in samples:
        with torch.no_grad():
            logits=model(torch.from_numpy(f)[None],
                         torch.from_numpy(c.astype(np.int64))[None])[0].numpy()
        choice,_=choose_legal(logits,mask,guard=False)
        matches+=int(choice==label)
        legal_ok+=int(mask[choice])
    return {"samples":len(samples),"exact_action_accuracy":matches/len(samples),
            "masked_legal_rate":legal_ok/len(samples)}

def execute(out:Path,seed_train=56100,seed_eval=56103):
    import torch,taverngym
    out.mkdir(parents=True,exist_ok=True)
    data=[]
    teacher_train=[play(seed_train+k,samples=data) for k in range(2)]
    model,train=optimize(data,taverngym.N_CARDS)
    ckpt=out/"student.pt"
    torch.save({"state_dict":model.state_dict(),"num_cards":taverngym.N_CARDS,
                "base_sha":BASE_SHA,"source_hash":verify_engine()["source_hash"],"train":train},ckpt)
    sha=hashlib.sha256(ckpt.read_bytes()).hexdigest()
    restored=torch.load(ckpt,map_location="cpu",weights_only=True)
    assert restored["source_hash"]==verify_engine()["source_hash"]
    student=build_model(restored["num_cards"])
    student.load_state_dict(restored["state_dict"])
    student.eval()
    heldout=[]
    teacher_eval=[play(seed_eval+i,samples=heldout) for i in range(2)]
    student_eval=[play(seed_eval+i,"student",model=student,guard=True) for i in range(2)]
    for r in student_eval:
        r["policy"]="student_bc_guarded"
        r["model_sha256"]=sha
    for k,r in enumerate(teacher_eval):
        (out/f"teacher-{seed_eval+k}.json").write_text(json.dumps(r,indent=2))
    for k,r in enumerate(student_eval):
        (out/f"student-guarded-{seed_eval+k}.json").write_text(json.dumps(r,indent=2))
    delta=float(np.mean([r["placements"][0] for r in student_eval])-
                np.mean([r["placements"][0] for r in teacher_eval]))
    report={"session":SESSION,"base_main":BASE_SHA,"engine":verify_engine(),
            "training_seeds":[seed_train,seed_train+1],
            "heldout_seeds":[seed_eval,seed_eval+1],
            "train":train,"model_sha256":sha,
            "teacher_agreement":teacher_agreement(student,heldout),
            "teacher_train_placements":[r["placements"][0] for r in teacher_train],
            "teacher_eval_placements":[r["placements"][0] for r in teacher_eval],
            "student_guarded_eval_placements":[r["placements"][0] for r in student_eval],
            "student_guard_triggers":[r["safety_forced_ends"] for r in student_eval],
            "paired_mean_rank_delta_student_minus_teacher":delta,
            "claim":"pilot only; guarded BC is not pure model; n=2 cannot prove improvement",
            "checkpoint_durable":False,"checkpoint_storage":"Actions artifact with expiration"}
    (out/"summary.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,ensure_ascii=False))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--seed-train",type=int,default=56100)
    p.add_argument("--seed-eval",type=int,default=56103)
    a=p.parse_args()
    execute(a.out,a.seed_train,a.seed_eval)
if __name__=="__main__":main()
