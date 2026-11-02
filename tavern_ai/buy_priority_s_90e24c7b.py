"""R002: one-variable legal-BUY override on saved, UNPROMOTED V2 PPO.

The fixed model is unchanged; this is a RULE-HYBRID causal behavior ablation,
not a gradient update or stronger learned model claim. An override triggers
whenever Buy is mask-legal and PPO proposes something outside BUY family.
No extra hidden state or own-view debug fields enter its action selection.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics

import numpy as np

from .contract import verify_engine
from .v2_opportunity_s_90e24c7b import (
    SESSION, V2_SHA256, V2_TAG, aggregate, load_verified_model, play, write,
)

SEEDS = (89111, 89112, 89113)


class MaskLegalBuyOverride:
    def __init__(self, base_model):
        self.model = base_model
        self.overrides = 0
        self.model_wanted_buy = 0
        self.model_wanted_nonbuy_while_buy_legal = 0

    def predict(self, observation, action_masks, deterministic=True):
        proposed, recurrent = self.model.predict(
            observation, action_masks=action_masks, deterministic=deterministic
        )
        proposal = int(np.asarray(proposed).item())
        legal = np.asarray(action_masks, dtype=bool)
        if legal.shape != (245,):
            raise ValueError("Expected pinned 245-action mask")
        if not legal[proposal]:
            raise ValueError("Underlying model proposed illegal action")
        buys = np.flatnonzero(legal[8:16])
        if buys.size:
            if 8 <= proposal < 16:
                self.model_wanted_buy += 1
            else:
                self.model_wanted_nonbuy_while_buy_legal += 1
                proposal = 8 + int(buys[0])
                self.overrides += 1
        return np.asarray(proposal), recurrent


def run(model_path: Path, out_dir: Path, report_path: Path, start_seed: int = SEEDS[0]):
    engine = verify_engine()
    model = load_verified_model(model_path)
    seeds = tuple(start_seed + k for k in range(3))
    arms = {"baseline": [], "model_control": [], "model_buy_override": []}
    for seed in seeds:
        # Each arm starts a NEW true TavernGym game from the same seed, seat 0.
        base = play(seed, "baseline", engine)
        control = play(seed, "model", engine, model=model)
        wrapper = MaskLegalBuyOverride(model)
        candidate = play(seed, "model", engine, model=wrapper)
        candidate["buy_override_count"] = wrapper.overrides
        candidate["model_wanted_buy"] = wrapper.model_wanted_buy
        candidate["model_wanted_nonbuy_while_buy_legal"] = wrapper.model_wanted_nonbuy_while_buy_legal
        candidate["rule_override"] = "first_mask_legal_buy_when_model_would_not_buy"
        candidate["strength_claim"] = None
        for label, receipt in (("baseline", base), ("model_control", control), ("model_buy_override", candidate)):
            write(out_dir / f"002-{label}-{seed}.json", receipt)
            arms[label].append(receipt)
            print(f"{label} seed={seed} rank={receipt['placements'][0]} "
                  f"buy={receipt['buy_actions']} legal={receipt['legal_buy_decisions']} "
                  f"guard={receipt['guard_forced_ends']}", flush=True)
    ranks = {label: [x["placements"][0] for x in rows] for label, rows in arms.items()}
    delta = [new-old for old, new in zip(ranks["model_control"], ranks["model_buy_override"])]
    report = {
        "schema": 1, "session_id": SESSION, "round": 2, "engine": engine,
        "release": V2_TAG, "checkpoint_sha256": V2_SHA256,
        "seeds": list(seeds), "ppo_steps_in_this_round": 0,
        "model_weights_updated": False,
        "baseline": aggregate(arms["baseline"]),
        "model_control_guarded": aggregate(arms["model_control"]),
        "hybrid_buy_override_guarded": aggregate(arms["model_buy_override"]),
        "buy_overrides": sum(x["buy_override_count"] for x in arms["model_buy_override"]),
        "per_game_buy_overrides": [x["buy_override_count"] for x in arms["model_buy_override"]],
        "paired_rank_delta_hybrid_minus_model": delta,
        "mean_paired_rank_delta": statistics.mean(delta),
        "source_type": "source-model inference plus explicitly counted rule override; NOT PPO retraining",
        "champion_promoted": False,
        "limitations": [
            "First legal shop slot is a simple selection rule, not card-value reasoning.",
            "All model/hybrid game results are guarded by the same 75-action legal EndTurn cap.",
            "Three new heldout seed pairs cannot establish general strength improvement.",
            "Rule-hybrid performance cannot be attributed to PPO learning.",
            "Per-decision buy legality is not a statistically independent opportunity.",
        ],
    }
    write(report_path, report)
    print(json.dumps({"deltas": delta, "overrides": report["buy_overrides"]}, ensure_ascii=False))
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--start-seed", type=int, default=SEEDS[0])
    p.add_argument("--out-dir", type=Path, default=Path("experiments") / SESSION)
    p.add_argument("--report", type=Path, default=Path("reports") / SESSION / "002-buy-ablation.json")
    args = p.parse_args()
    import torch
    torch.set_num_threads(2)
    run(args.model, args.out_dir, args.report, args.start_seed)


if __name__ == "__main__":
    main()
