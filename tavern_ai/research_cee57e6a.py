"""Session-isolated public-observation full-board replacement experiment.

Action/observation offsets sourced from AutoTavern pinned upstream actions.rs
and obs.rs at fb61201a557ddd36a411cf44aac51ce4d9b606ce.
"""
from __future__ import annotations
import argparse, hashlib, json, statistics
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from tavern_ai.baseline import BaselinePolicy
from tavern_ai.canary import run as baseline_game
from tavern_ai.contract import ACTIONS, CARDS, FEATURES, verify_engine
from tavern_ai.validate_receipt import validate

SID = "s-20261102-cee57e6a"
BOARD, MINION, HAND, ITEM = 68, 31, 285, 40
TRAIN, HELDOUT, GRID = (73011,73012), (73031,73032,73033), (4.0,8.0,12.0)

def strength(f,off):
    return (10 * max(0.,float(f[off+1])) + 10 * max(0.,float(f[off+2]))
            + 6*float(f[off+9]) + 3*float(f[off+11])
            + 8*float(f[off+12]) + float(f[off+8]))

class BoardSwapPolicy:
    def __init__(self,margin):
        self.margin=float(margin)
        self.base=BaselinePolicy()
        self.turn=-1
        self.swaps_this_turn=0
        self.swaps=0
    def act(self,obs,context):
        f=np.asarray(obs["features"],dtype=np.float32)
        mask=np.asarray(obs["action_mask"],dtype=bool)
        if f.shape!=(FEATURES,) or mask.shape!=(ACTIONS,):
            raise ValueError("incompatible public observation")
        turn=int(context["turn"])
        if turn!=self.turn:
            self.turn,self.swaps_this_turn=turn,0
        default=self.base.act(obs,context)
        # Preserve choices, hand plays, magnetization and scheduled upgrades.
        if (turn<6 or self.swaps_this_turn or default==3
                or 30<=default<196 or not mask[0] or not mask[16:23].all()):
            return default
        if f[HAND]<.5 or f[HAND+1]<.5 or f[HAND+3]>.5:
            return default
        if any(f[BOARD+i*MINION]<.5 for i in range(7)):
            return default
        eligible=[i for i in range(7)
                  if mask[16+i] and f[BOARD+i*MINION+5]<.5]
        if not eligible:
            return default
        weakest=min(eligible,key=lambda i:(strength(f,BOARD+i*MINION),i))
        if strength(f,HAND+9)<=strength(f,BOARD+weakest*MINION)+self.margin:
            return default
        self.swaps_this_turn+=1
        self.swaps+=1
        return 16+weakest

def check_public_layout(f,game):
    """Oracle check only: game objects never enter policy.act."""
    # The Python PyGame does not expose Rust game.players. Its documented
    # view(0)["me"] is the own-player UI view. Opponents are never inspected.
    own=json.loads(game.view(0))["me"]
    if round(float(f[32])*7)!=len(own["board"]):
        raise AssertionError("board count observation mismatch")
    if round(float(f[33])*10)!=len(own["hand"]):
        raise AssertionError("hand count observation mismatch")
    for i,m in enumerate(own["board"]):
        off=BOARD+i*MINION
        if abs(float(f[off+1])*10-m["atk"])>.06 or abs(float(f[off+2])*10-m["hp"])>.06:
            raise AssertionError("public minion stats observation mismatch")

def play_real(seed,margin):
    import taverngym
    engine=verify_engine()
    game=taverngym.Game(seed=seed)
    policy=BoardSwapPolicy(margin)
    last_turn,used,decisions=-1,0,0
    for _ in range(30000):
        if game.is_over():break
        turn=int(game.turn)
        if turn!=last_turn:last_turn,used=turn,0
        progress=False
        for seat in range(game.num_players):
            if not game.needs_action(seat):continue
            progress=True
            if seat!=0:
                game.bot_play(seat)
                continue
            fbytes,cbytes=game.observe2(0)
            f=np.frombuffer(fbytes,dtype="<f4").copy()
            cards=np.frombuffer(cbytes,dtype="<i4")
            mask=np.frombuffer(game.legal_mask(0),dtype=np.uint8).astype(bool)
            if f.shape!=(FEATURES,) or cards.shape!=(CARDS,) or mask.shape!=(ACTIONS,):
                raise AssertionError("observe2 contract mismatch")
            check_public_layout(f,game)
            action=policy.act({"features":f,"action_mask":mask},{"turn":turn,"actions_used":used})
            if not mask[action]:raise AssertionError("illegal action")
            game.step(0,int(action))
            decisions+=1
            used+=1
        if not progress and not game.is_over():raise RuntimeError("game stalled")
    if not game.is_over():raise RuntimeError("full-game safety limit exceeded")
    result={"schema":1,"timestamp":datetime.now(timezone.utc).isoformat(),
            "environment":"TavernGym","engine_source_hash":engine["source_hash"],
            "engine_version":engine["version"],"agent_id":SID,
            "policy":"public-board-swap","seed":seed,"completed":True,
            "turns":int(game.turn),"decisions":decisions,
            "placements":[int(x) for x in game.placements()],
            "truncated_combats":int(game.truncated_combats),
            "turn_limit_end":bool(game.turn_limit_end),"margin":margin,
            "swaps":policy.swaps,"safety_forced_end_turns":0,
            "model_sha256":None,
            "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    validate(result)
    return result

def summary(rows):
    p=[r["placements"][0] for r in rows]
    return {"games":len(rows),"placements":p,"seeds":[r["seed"] for r in rows],
            "mean_placement":statistics.mean(p),
            "top4_rate":sum(x<=4 for x in p)/len(p),
            "first_place_rate":sum(x==1 for x in p)/len(p),
            "swaps":sum(r.get("swaps",0) for r in rows),
            "decisions":sum(r["decisions"] for r in rows)}

def execute(folder):
    folder.mkdir(parents=True,exist_ok=True)
    def save(name,r):
        (folder/(name+".json")).write_text(json.dumps(r,indent=2),encoding="utf-8")
        return r
    train_base=[save(f"001-train-base-{s}",baseline_game(s,SID)) for s in TRAIN]
    by_margin={str(int(x)):[save(f"001-train-margin{int(x)}-{s}",play_real(s,x))
                            for s in TRAIN] for x in GRID}
    chosen=min(GRID,key=lambda x:(summary(by_margin[str(int(x))])["mean_placement"],-x))
    mandatory=save("001-mandatory-73029",play_real(73029,chosen))
    base=[save(f"001-heldout-base-{s}",baseline_game(s,SID)) for s in HELDOUT]
    cand=[save(f"001-heldout-candidate-{s}",play_real(s,chosen)) for s in HELDOUT]
    diff=[b["placements"][0]-a["placements"][0] for a,b in zip(base,cand)]
    return {
        "schema":1,"session_id":SID,
        "hypothesis":"Observed full-board replacement improves weak baseline",
        "method":"Real-game bounded hyperparameter search, no gradients",
        "actual_ppo_steps":0,"actual_training_games":8,
        "train_seeds":list(TRAIN),"heldout_seeds":list(HELDOUT),
        "mandatory_seed":73029,"grid":list(GRID),"selected_margin":chosen,
        "engine":verify_engine(),
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "training_baseline":summary(train_base),
        "training_candidates":{k:summary(v) for k,v in by_margin.items()},
        "mandatory":mandatory,"heldout_baseline":summary(base),
        "heldout_candidate":summary(cand),
        "paired_candidate_minus_baseline":diff,
        "paired_mean_delta":statistics.mean(diff),
        "total_complete_game_receipts":15,
        "promotion":"RETEST, not enough evidence even if candidate improves",
        "checkpoint":"No neural network; source code plus selected margin reproduces policy"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=execute(a.output)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"selected_margin":result["selected_margin"],
                      "heldout_baseline":result["heldout_baseline"],
                      "heldout_candidate":result["heldout_candidate"],
                      "paired_mean_delta":result["paired_mean_delta"]}))

if __name__=="__main__":main()
