import os
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SQLALCHEMY_ECHO", "False")

from main import app  # noqa: E402

client = TestClient(app)


def _iso(dt: datetime) -> str:
    return dt.replace(tzinfo=UTC).isoformat()


def test_assignment_locked_after_start():
    past_start = datetime.now(UTC) - timedelta(minutes=10)
    past_end = datetime.now(UTC) + timedelta(minutes=50)
    payload = {
        "paper_id": "paper-locked",
        "start_time": _iso(past_start),
        "end_time": _iso(past_end),
    }

    create_resp = client.post("/api/sessions/session-lock/assignments", json=payload)
    assert create_resp.status_code == 200
    assignment_id = create_resp.json()["data"]["assignment"]["id"]

    # updates should be blocked once started
    update_resp = client.put(
        f"/api/sessions/session-lock/assignments/{assignment_id}",
        json={"paper_id": "new-paper"},
    )
    assert update_resp.status_code == 400
    assert "started" in update_resp.json()["detail"].lower()

    # deletion should also be blocked
    delete_resp = client.delete(f"/api/sessions/session-lock/assignments/{assignment_id}")
    assert delete_resp.status_code == 400
    assert "started" in delete_resp.json()["detail"].lower()
