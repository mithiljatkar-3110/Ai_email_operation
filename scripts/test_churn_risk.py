"""Quick test for churn-risk retention workflow (Karen / msg_033)."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import select, update

from app.db.database import SessionLocal
from app.main import app
from app.models.email import Email

KAREN_SENDER = "karen.w@retail-co.com"
MSG_033 = "msg_033"
EXPECTED_ACTIONS = (
    "get_thread_history",
    "search_knowledge_base",
    "create_retention_ticket",
    "escalate_to_account_manager",
    "draft_retention_reply",
)


def main() -> None:
    db = SessionLocal()
    karen = db.scalar(
        select(Email)
        .where(Email.sender == KAREN_SENDER)
        .order_by(Email.timestamp.desc())
    )
    if karen is None:
        data = json.load(open("email-data-advanced.json"))
        client = TestClient(app)
        for row in data:
            if row.get("thread_id") == "thread_karen_refund":
                resp = client.post("/api/ingest", json=row)
                print("ingest", row["message_id"], resp.status_code)
        db.close()
        db = SessionLocal()
        karen = db.scalar(
            select(Email)
            .where(Email.message_id == MSG_033)
        )

    assert karen is not None, "msg_033 not found — ingest thread_karen_refund emails first"

    if karen.confidence is None:
        db.execute(
            update(Email)
            .where(Email.id == karen.id)
            .values(
                category="Complaint",
                urgency="High",
                confidence=0.92,
                requires_human=True,
                sentiment_score=-0.8,
            )
        )
        db.commit()
        db.refresh(karen)
    db.close()

    client = TestClient(app)
    resp = client.post(f"/agent/dry-run/{karen.id}")
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
    assert data["final_action"] == "retention_draft_response"
    actions = [s["action"] for s in trace]
    for expected in EXPECTED_ACTIONS:
        needle = expected.split("(")[0]
        assert any(needle in a for a in actions), f"missing {expected}"
    print("OK: Churn-risk workflow passed")


if __name__ == "__main__":
    main()
