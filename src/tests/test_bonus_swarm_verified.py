"""B3: verifier makes swarm_verified immune to the ticket-delay weakness."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from bonus import swarm_verified
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.metrics import trial_pass
from lab8.shapes import swarm_reference

BONUS = Path(__file__).resolve().parents[1] / "bonus"
WORLD = load_json(BONUS / "world.json")
CASES = load_jsonl(BONUS / "cases.jsonl")
BY_ID = {c["claim_id"]: c for c in CASES}
SEEDS = [11, 22, 33, 44, 55]


def _run(shape, claim_id, seed, tmp_path):
    store = tmp_path / f"{shape.__name__}-{claim_id}-{seed}.sqlite"
    init_store(store, WORLD, CASES).close()
    started = time.time()
    result = shape.run_claim(claim_id, seed=seed, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started)
    finally:
        conn.close()
    return result, passed, reason


def _events(result, kind):
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    return [e for e in body["events"] if e["kind"] == kind]


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("claim_id", sorted(BY_ID))
def test_verified_passes_every_adversarial_claim(tmp_path, claim_id, seed):
    _, passed, reason = _run(swarm_verified, claim_id, seed, tmp_path)
    assert passed, reason


def test_reference_swarm_still_breaks_on_seed_55(tmp_path):
    # Without the verifier the same weakness shows up: the corpus really attacks it.
    _, passed, _ = _run(swarm_reference, "X-01", 55, tmp_path)
    assert not passed


def test_verifier_overrides_ticket_delay_and_traces_it(tmp_path):
    result, passed, reason = _run(swarm_verified, "X-01", 55, tmp_path)
    assert passed, reason
    (event,) = _events(result, "verifier_override")
    assert event["payload"]["facts"] == {"delay_days": {"used": 9, "row": 1}}
    assert event["payload"]["requoted_vnd"] == 0


@pytest.mark.parametrize("claim_id,seed", [("X-01", 11), ("X-05", 55), ("X-10", 55)])
def test_verifier_stays_silent_when_nothing_disagrees(tmp_path, claim_id, seed):
    # seed 11 never trips the weakness; X-05/X-10 tickets agree with (or omit) the delay.
    result, passed, reason = _run(swarm_verified, claim_id, seed, tmp_path)
    assert passed, reason
    assert _events(result, "verifier_override") == []
