"""Seeded full-game evaluation, with optional paired baseline comparison."""
from __future__ import annotations
import argparse, hashlib, json, statistics
from pathlib import Path
from .canary import run
from .contract import ENGINE_HASH
from .receipt_integrity import validate_integrity

def summarize(records: list[dict]) -> dict:
    placements = [r["placements"][0] for r in records]
    return {
        "games": len(records),
        "mean_placement": statistics.mean(placements),
        "top4_rate": sum(x <= 4 for x in placements) / len(records),
        "first_place_rate": sum(x == 1 for x in placements) / len(records),
        "placements": placements, "seeds": [r["seed"] for r in records],
    }

def _check_game(receipt: dict, expected_policy: str, seed: int, model_digest: str | None) -> None:
    """Only strict, unassisted full games enter comparable evaluation scores."""
    validate_integrity(receipt)
    if receipt["policy"] != expected_policy:
        raise ValueError("Evaluation policy/receipt mismatch (possible fallback)")
    if receipt["seed"] != seed:
        raise ValueError("Evaluation receipt seed mismatch")
    if receipt.get("guard_forced_ends", 0) != 0 or receipt.get("raw_model_only", True) is False:
        raise ValueError("Guarded/assisted model result cannot be scored as raw PPO")
    if expected_policy == "model" and receipt["model_sha256"] != model_digest:
        raise ValueError("Evaluation model checkpoint SHA256 mismatch")

def evaluate(policy: str | int = "baseline", model: Path | int | None = None, games: int | None = None, start_seed: int = 24000,
             compare_baseline: bool = False) -> dict:
    if isinstance(policy, int):
        # Compact baseline-only API: evaluate(games, seed). Preserve legacy API.
        games, start_seed, model, policy = policy, (model if isinstance(model, int) else 24000), None, "baseline"
    if games is None:
        games = 3
    if policy not in {"baseline", "model"}:
        raise ValueError("Unknown evaluation policy")
    if not 1 <= games <= 100:
        raise ValueError("games must be 1..100")
    if policy == "model" and (model is None or not model.is_file()):
        raise FileNotFoundError("Model checkpoint required for evaluation")
    if compare_baseline and policy != "model":
        raise ValueError("Paired baseline comparison requires a model")
    # Verify receipts before computing any performance aggregates. These are
    # raw-policy games: externally guarded/fallback runs need a separate label.
    model_digest = hashlib.sha256(model.read_bytes()).hexdigest() if policy == "model" else None
    candidate = []
    for i in range(games):
        seed = start_seed + i
        receipt = run(seed, "evaluation", policy, str(model) if model else None)
        _check_game(receipt, policy, seed, model_digest)
        candidate.append(receipt)
    report = {
        "policy": policy, "candidate": summarize(candidate),
        "seed_start": start_seed,
        "comparison": "seven scripted TavernGym bots, not Arena Elo",
        "inference": "Descriptive results only; small samples do not establish improvement",
        "receipt_gate": "strict_unassisted_full_match",
        "control_seat": 0,
        "engine_source_hash": ENGINE_HASH,
        "candidate_model_sha256": model_digest,
    }
    if compare_baseline:
        baseline = []
        for i in range(games):
            seed = start_seed + i
            receipt = run(seed, "evaluation", "baseline")
            _check_game(receipt, "baseline", seed, None)
            baseline.append(receipt)
        report["baseline"] = summarize(baseline)
        report["paired_rank_deltas"] = [a["placements"][0] - b["placements"][0]
                                        for a, b in zip(candidate, baseline)]
        report["paired_seed_count"] = len(report["paired_rank_deltas"])
        report["paired_mean_placement_delta"] = (
            report["candidate"]["mean_placement"] - report["baseline"]["mean_placement"]
        )
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--policy", choices=["model", "baseline"])
    p.add_argument("--model", type=Path)
    p.add_argument("--compare-baseline", action="store_true")
    p.add_argument("--games", type=int, default=3)
    p.add_argument("--start-seed", type=int, default=24000)
    p.add_argument("--out", type=Path, default=Path("artifacts/evaluation.json"))
    a = p.parse_args()
    policy = a.policy or ("model" if a.model is not None else "baseline")
    report = evaluate(policy, a.model, a.games, a.start_seed, a.compare_baseline)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    main()
