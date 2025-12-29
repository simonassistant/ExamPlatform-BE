import os
from fastapi.testclient import TestClient

os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SQLALCHEMY_ECHO", "False")

from main import app  # noqa: E402

client = TestClient(app)


def _sample_payload(title: str = "Draft Paper"):
    return {
        "title": title,
        "question_type": 1,
        "sections": [
            {
                "seq": 1,
                "name": "Section A",
                "question_groups": [
                    {
                        "seq": 1,
                        "title": "Group 1",
                        "questions": [
                            {
                                "seq": 1,
                                "title": "Q1",
                                "options": [
                                    {"seq": 1, "optionText": "A", "isCorrect": True},
                                    {"seq": 2, "optionText": "B", "isCorrect": False},
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }


def test_edit_publish_flow():
    create_resp = client.post("/api/papers", json=_sample_payload())
    assert create_resp.status_code == 200
    paper = create_resp.json()["data"]["paper"]
    paper_id = paper["id"]

    # Update draft
    update_payload = _sample_payload(title="Updated Title")
    update_resp = client.put(f"/api/papers/{paper_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()["data"]["paper"]
    assert updated["title"] == "Updated Title"
    assert updated["status"] == "Draft"

    # Fetch and verify
    fetch_resp = client.get(f"/api/papers/{paper_id}")
    assert fetch_resp.status_code == 200
    fetched = fetch_resp.json()["data"]["paper"]
    assert fetched["title"] == "Updated Title"

    # Publish
    publish_resp = client.post(f"/api/papers/{paper_id}/publish", params={"version": 2})
    assert publish_resp.status_code == 200
    assert publish_resp.json()["data"]["status"] == "Published"
    assert publish_resp.json()["data"].get("version") == 2

    # Fetch after publish to ensure status persisted
    fetch_after = client.get(f"/api/papers/{paper_id}")
    assert fetch_after.status_code == 200
    assert fetch_after.json()["data"]["paper"]["status"] == "Published"
