"""Quick test for Bob Jones SLA/legal escalation workflow."""

from __future__ import annotations

import json
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select, update

from app.db.database import SessionLocal
from app.main import app
from app.models.email import Email

BOB_SENDER = "bob.jones@enterprise.net"
EXPECTED_TOOL_ACTIONS = (
    "get_thread_history",
    'search_knowledge_base("SLA")',
    "check_account_status",
    "flag_for_legal",
    "create_internal_ticket",
    "draft_holding_reply",
    "escalate_to_human",
)


def main() -> None:
    db = SessionLocal()
    bob = db.scalar(
        select(Email)
        .where(Email.sender == BOB_SENDER)
        .order_by(Email.timestamp.desc())
    )
    if bob is None:
        data = next(
            e for e in json.load(open("email-data-advanced.json")) if e["message_id"] == "msg_060"
        )
        client = TestClient(app)
        resp = client.post("/api/ingest", json=data)
        print("ingest:", resp.status_code, resp.json())
        db.close()
        db = SessionLocal()
        bob = db.scalar(
            select(Email)
            .where(Email.sender == BOB_SENDER)
            .order_by(Email.timestamp.desc())
        )

    assert bob is not None
    if bob.confidence is None:
        db.execute(
            update(Email)
            .where(Email.id == bob.id)
            .values(
                category="Legal",
                urgency="Critical",
                confidence=0.98,
                requires_human=True,
            )
        )
        db.commit()
        db.refresh(bob)
    db.close()

    client = TestClient(app)
    resp = client.post(f"/agent/dry-run/{bob.id}")
    print("status:", resp.status_code)
    data = resp.json()
    print("final_action:", data.get("final_action"))
    trace = data.get("reasoning_trace", [])
    print("steps:", len(trace))
    for i, step in enumerate(trace, 1):
        print(f"{i:02d} {step['action']}")
        if step.get("observation"):
            print(f"    -> {step['observation'][:120]}")

    assert resp.status_code == 200, data
    assert data["final_action"] == "escalate_to_human"
    actions = [s["action"] for s in trace]
    for expected in EXPECTED_TOOL_ACTIONS:
        needle = expected.split("(")[0].strip('"')
        assert any(needle in a for a in actions), f"missing {expected}"
    tool_call_steps = [
        a for a in actions if any(t in a for t in (
            "get_thread_history",
            "search_knowledge_base",
            "check_account_status",
            "flag_for_legal",
            "create_internal_ticket",
            "draft_holding_reply",
        ))
    ]
    assert len(tool_call_steps) == 6, tool_call_steps
    print("OK: Bob Jones workflow passed")


if __name__ == "__main__":
    main()
