"""B3: reference swarm plus a code verifier before the write.

The swarm is kept as is, including its REFERENCE_WEAKNESS (on seed % 5 == 0 it
trusts the delay written in the ticket). The verifier compares every fact used
for the quote (delay_days, status, damage_verified) with the structured order
row from the read-only investigator. On a mismatch it requotes from the row
(one correction round at most) and traces a `verifier_override` event. Money
and ledger writes stay with the host.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.shapes.swarm_reference import _Trace
from lab8.tools import compute_compensation, tool_cost

SHAPE = "swarm_verified"
VERIFIED_FACTS = ("delay_days", "status", "damage_verified")


def run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = _Trace(make_run_id(SHAPE, claim_id, seed))

    def end(status: str, proposal: int, reason: str | None) -> RunResult:
        return finish(conn, shape=SHAPE, claim_id=claim_id, seed=seed, status=status,
                      proposal_amount=proposal, budget=budget, trace=trace, error_reason=reason)

    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?", (claim_id,)
    ).fetchone()
    if claim_row is None:
        trace.add("error", {"reason": "unknown_claim"})
        return end("failed", 0, "unknown_claim")

    ticket = claim_row["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)

    if not claim_row["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return end("needs_info", 0, "missing_order_id")

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}", claim_id=claim_id, task="check_applicable_policy", facts={},
        allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim_row["principal_id"])
    order_view = investigated["tools"].get("lookup_order", {})
    trace.add("investigator", {"lookup_order": order_view})
    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return end("escalated", 0, order_view.get("reason"))

    structured = dict(order_view["order"])
    order = dict(structured)
    # Same weakness as the reference swarm: the model overrides the row with the ticket.
    if parsed_delay is not None and parsed_delay != int(order["delay_days"]) and seed % 5 == 0:
        order["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})

    if order["delay_days"] != structured["delay_days"]:
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order)
    else:
        quote_payload = investigated["tools"]["compute_compensation"]

    # Verifier (code, no model call): every fact behind the quote must match the structured row.
    budget.add_tool(tool_cost())
    mismatched = {k: {"used": order[k], "row": structured[k]} for k in VERIFIED_FACTS if order[k] != structured[k]}
    if mismatched:
        order = dict(structured)
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order)
        trace.add("verifier_override", {"facts": mismatched, "requoted_vnd": int(quote_payload["amount_vnd"])})

    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", quote_payload)
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
    if proposal <= 0:
        return end("denied", 0, quote_payload.get("reason"))

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    if not outcome["ok"]:
        return end("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return end("resolved", proposal, None)
