import os
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SQLALCHEMY_ECHO", "False")

from main import app  # noqa: E402

client = TestClient(app)


def _iso(dt: datetime) -> str:
    return dt.replace(tzinfo=UTC).isoformat()


def test_assignment_crud_and_conflicts_with_validation():
    base_start = datetime.now(UTC) + timedelta(hours=1)
    base_end = base_start + timedelta(hours=1)
    payload = {
        # use camelCase keys to ensure aliases are accepted
        "paperId": "paper-1",
        "startTime": _iso(base_start),
        "endTime": _iso(base_end),
    }

    create_resp = client.post("/api/sessions/session-1/assignments", json=payload)
    assert create_resp.status_code == 200
    created = create_resp.json()["data"]["assignment"]
    assignment_id = created["id"]
    assert created["paper_id"] == "paper-1"
    assert created["start_time"].startswith(payload["startTime"].split(".")[0])

    # list endpoint returns the created assignment
    list_resp = client.get("/api/sessions/session-1/assignments")
    assert list_resp.status_code == 200
    items = list_resp.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["paper_id"] == "paper-1"

    # conflict on overlap
    conflict_payload = {
        "paper_id": "paper-2",
        "start_time": _iso(base_start + timedelta(minutes=30)),
        "end_time": _iso(base_end + timedelta(minutes=30)),
    }
    conflict_resp = client.post("/api/sessions/session-1/assignments", json=conflict_payload)
    assert conflict_resp.status_code == 400
    assert "overlap" in conflict_resp.json()["detail"].lower()

    # start must be before end
    invalid_resp = client.post(
        "/api/sessions/session-1/assignments",
        json={"paper_id": "paper-3", "start_time": _iso(base_end), "end_time": _iso(base_start)},
    )
    assert invalid_resp.status_code == 400
    assert "before end" in invalid_resp.json()["detail"].lower()

    # update to non-overlapping window + add group filter
    new_start = base_end + timedelta(minutes=10)
    new_end = new_start + timedelta(hours=1)
    update_resp = client.put(
        f"/api/sessions/session-1/assignments/{assignment_id}",
        json={
            "startTime": _iso(new_start),
            "endTime": _iso(new_end),
            "examineeGroupFilter": "group-A",
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()["data"]["assignment"]
    assert updated["start_time"].startswith(_iso(new_start).split(".")[0])
    assert updated["examinee_group_filter"] == "group-A"

    # delete
    delete_resp = client.delete(f"/api/sessions/session-1/assignments/{assignment_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["data"]["status"] == "deleted"

    # delete again yields 404
    delete_missing = client.delete(f"/api/sessions/session-1/assignments/{assignment_id}")
    assert delete_missing.status_code == 404
