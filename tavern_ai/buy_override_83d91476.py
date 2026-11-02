"""R002: isolated purchase-opportunity rescue of an *unchanged* V2 checkpoint.

This is an intervention policy, not pure PPO, nor additional training.
Compares raw V2 / override / baseline on fresh paired seeds.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics

from .buy_opportunities_83d91476 import real_game
from .contract import ACTIONS, verify_engine
from .validate_receipt import validate

MODEL_SHA256 = "73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a"
SEEDS = (45113, 45114, 45115, 45116)


class BuyOpportunityOverride:
    """Replace Refresh/Freeze with first legal BUY, but count every override.

    The native model stays frozen. This is neither imitation nor a model update.
    """
    def __init__(self, model):
        self.model = model
        self.counts = Counter()

    def predict(self, observation, *, action_masks, deterministic=True):
        mask = list(action_masks)
        if len(mask) != ACTIONS:
            raise ValueError("Wrong action mask width")
        raw, _ = self.model.predict(
            observation, action_masks=action_masks, deterministic=deterministic)
        import numpy as np
        raw_id = int(np.asarray(raw).item())
        if not (0 <= raw_id < ACTIONS) or not mask[raw_id]:
            raise ValueError("Native model proposed illegal action")
        self.counts["model_decisions"] += 1
        if raw_id in (1, 2):
            self.counts["raw_refresh_or_freeze"] += 1
            target = next((idx for idx in range(8, 16) if mask[idx]), None)
            if target is not None:
                self.counts["overrides"] += 1
                self.counts[f"replaced_{raw_id}"] += 1
                return target, None
        return raw_id, None


def paired(seed: int, model, digest: str) -> dict:
    # Raw model and intervention share seed, seat 0 and opponent type.
    raw = real_game(seed, "model", model, digest)
    proxy = BuyOpportunityOverride(model)
    rescued = real_game(seed, "model", proxy, digest)
    rescued["policy"] = "model_with_explicit_buy_override"
    rescued["manual_intervention"] = {
        "type": "refresh_freeze_to_first_legal_buy",
        "count": proxy.counts["overrides"],
        "replaced_refresh": proxy.counts["replaced_1"],
        "replaced_freeze": proxy.counts["replaced_2"],
        "native_model_decisions": proxy.counts["model_decisions"],
    }
    rescued["guarded"] = bool(rescued["guarded"] or proxy.counts["overrides"])
    rescued["pure_ppo_result"] = False
    baseline = real_game(seed, "baseline")
    for r in [raw, rescued, baseline]:
        validate(r)
        if sorted(r["placements"]) != list(range(1, 9)):
            raise ValueError("Invalid eight-seat result")
    return {"seed": seed, "raw_v2": raw, "buy_override": rescued,
            "baseline": baseline}


def summarise(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("Need real paired games")
    arms = ("raw_v2", "buy_override", "baseline")
    out = {}
    for arm in arms:
        games = [r[arm] for r in rows]
        ranks = [g["placements"][0] for g in games]
        out[arm] = {
            "games": len(games), "ranks": ranks, "mean_rank": statistics.mean(ranks),
            "buy_count": sum(g["opportunity_diagnostics"]["counts"].get("buys", 0) for g in games),
            "buy_legal_exposures": sum(g["opportunity_diagnostics"]["counts"].get("buy_legal_exposures", 0) for g in games),
            "guard_forced_ends": sum(g["opportunity_diagnostics"]["counts"].get("guard_forced_end", 0) for g in games),
        }
    out["buy_override"]["manual_overrides"] = sum(
        row["buy_override"]["manual_intervention"]["count"] for row in rows)
    out["paired_rank_delta_override_minus_raw"] = [
        row["buy_override"]["placements"][0] - row["raw_v2"]["placements"][0]
        for row in rows]
    out["candidate_strength_claim"] = False
    out["reproducibility_note"] = (
        "4 exploratory seeds; no strength/significance claim. Override uses rules outside "
        "the native PPO and cannot be promoted as that checkpoint. All arms see identical "
        "initial RNG seeds, but subsequent game trajectories diverge as expected."
    )
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, type=Path)
    p.add_argument("--out", type=Path, default=Path("outputs/buy-override-r002.json"))
    p.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    args = p.parse_args()
    digest = hashlib.sha256(args.model.read_bytes()).hexdigest()
    if digest != MODEL_SHA256:
        raise ValueError("V2 Release digest mismatch; do not run on unknown checkpoint")
    engine = verify_engine()
    import torch
    from sb3_contrib import MaskablePPO
    torch.set_num_threads(2)
    model = MaskablePPO.load(str(args.model), device="cpu")
    rows = [paired(seed, model, digest) for seed in args.seeds]
    out = {
        "session_id": "s-20261102-83d91476", "round": 2,
        "trained_steps": 0, "engine": engine,
        "model_sha256": digest, "seeds": args.seeds,
        "data": rows, "summary": summarise(rows),
        "intervention": "Native PPO frozen; override ONLY proposed refresh/freeze while BUY is legal. Performance is NOT raw model performance.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
