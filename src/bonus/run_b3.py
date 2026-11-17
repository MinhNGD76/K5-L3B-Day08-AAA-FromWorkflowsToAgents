"""B3: workflow vs swarm vs swarm_verified on the public corpus and on bonus/cases.jsonl.

Run from src/:  python -m bonus.run_b3
Writes reports/bonus_swarm_verified.json. Same claims, seeds, prices and evaluator
for every shape (lab8.benchmark.run_benchmark).
"""

from __future__ import annotations

import json
from pathlib import Path

from lab8.app import register_extra_shapes
from lab8.benchmark import run_benchmark
from lab8.config_loader import repo_path
from lab8.db import load_json, load_jsonl

SRC = Path(__file__).resolve().parents[1]
SHAPES = ["workflow", "swarm", "swarm_verified"]
SEEDS = [11, 22, 33, 44, 55]
KEYS = ("pass_rate", "pass_5", "seed_variance", "seed_min", "seed_max", "cost_per_success_vnd", "mean_steps")


def _overrides(trials: list[dict]) -> list[dict]:
    """Trials where the verifier changed the quote, read from each run's trace file."""
    found = []
    for row in trials:
        if row["shape"] != "swarm_verified":
            continue
        trace = json.loads(Path("traces", f"{row['run_id']}.json").read_text(encoding="utf-8"))
        for event in trace["events"]:
            if event["kind"] == "verifier_override":
                found.append({"run_id": row["run_id"], "claim_id": row["claim_id"], "seed": row["seed"],
                              "payload": event["payload"]})
    return found


def _run(world_path, claims_path) -> dict:
    world, claims = load_json(world_path), load_jsonl(claims_path)
    report = run_benchmark(world=world, claims=claims, shapes=SHAPES, seeds=SEEDS)
    return {
        "claims": len(claims),
        "by_shape": {s: {k: v[k] for k in KEYS} for s, v in report["by_shape"].items()},
        "failed_trials": [
            {"shape": t["shape"], "claim_id": t["claim_id"], "seed": t["seed"], "reason": t["reason"]}
            for t in report["trials"] if t["passed"] is False
        ],
        "verifier_overrides": _overrides(report["trials"]),
        "trials": report["trials"],
    }


def main() -> None:
    register_extra_shapes(["swarm_verified=bonus.swarm_verified:run_claim"])
    out = {
        "seeds": SEEDS,
        "public": _run(repo_path("data", "public_world_state.json"), repo_path("data", "public_claims.jsonl")),
        "adversarial": _run(SRC / "bonus" / "world.json", SRC / "bonus" / "cases.jsonl"),
    }
    path = SRC / "reports" / "bonus_swarm_verified.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    for corpus in ("public", "adversarial"):
        print(f"[{corpus}] {out[corpus]['claims']} claims, verifier overrides: {len(out[corpus]['verifier_overrides'])}")
        for shape, s in out[corpus]["by_shape"].items():
            print(f"  {shape:15} pass={s['pass_rate']:.3f} pass^5={s['pass_5']:.3f} var={s['seed_variance']:.6f} "
                  f"cost/success={s['cost_per_success_vnd']:.2f}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
