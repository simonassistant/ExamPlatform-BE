import os
from fastapi.testclient import TestClient

os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SQLALCHEMY_ECHO", "False")

from main import app  # noqa: E402

client = TestClient(app)


def test_create_update_publish_flow():
    payload = {
        "title": "Flow Paper",
        "question_type": 2,
        "sections": [
            {
                "seq": 1,
                "name": "Intro",
                "question_groups": [
                    {
                        "seq": 1,
                        "title": "G1",
                        "questions": [
                            {"seq": 1, "title": "T/F", "options": []},
                        ],
                    }
                ],
            }
        ],
    }
    resp = client.post("/api/papers", json=payload)
    assert resp.status_code == 200
    draft = resp.json()["data"]["paper"]
    assert draft["status"] == "Draft"

    update_payload = payload | {"title": "Flow Paper Updated"}
    resp_upd = client.put("/api/papers/draft-id", json=update_payload)
    assert resp_upd.status_code == 200
    assert resp_upd.json()["data"]["paper"]["title"] == "Flow Paper Updated"

    resp_pub = client.post("/api/papers/draft-id/publish")
    assert resp_pub.status_code == 200
    assert resp_pub.json()["data"]["status"] == "Published"
