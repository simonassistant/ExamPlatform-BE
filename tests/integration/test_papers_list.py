import os
from fastapi.testclient import TestClient

os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SQLALCHEMY_ECHO", "False")

from main import app  # noqa: E402

client = TestClient(app)


def _payload(title: str):
    return {
        "title": title,
        "question_type": 1,
        "sections": [
            {
                "seq": 1,
                "name": "Section",
                "question_groups": [
                    {
                        "seq": 1,
                        "title": "Group",
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


def test_list_papers_with_status_and_search():
    # create two papers
    create_a = client.post("/api/papers", json=_payload("Alpha Paper"))
    assert create_a.status_code == 200

    create_b = client.post("/api/papers", json=_payload("Beta Paper"))
    assert create_b.status_code == 200
    paper_b = create_b.json()["data"]["paper"]

    # archive beta
    delete_resp = client.delete(f"/api/papers/{paper_b['id']}")
    assert delete_resp.status_code == 200

    # list all
    list_resp = client.get("/api/papers")
    assert list_resp.status_code == 200
    payload = list_resp.json()["data"]
    assert payload["total"] >= 2
    assert any(item.get("title") == "Alpha Paper" for item in payload["items"])

    # status filter
    draft_resp = client.get("/api/papers", params={"status": "Draft"})
    assert draft_resp.status_code == 200
    draft_items = draft_resp.json()["data"]["items"]
    assert any(item.get("title") == "Alpha Paper" for item in draft_items)

    archived_resp = client.get("/api/papers", params={"status": "Archived"})
    assert archived_resp.status_code == 200
    archived_items = archived_resp.json()["data"]["items"]
    assert any(item.get("title") == "Beta Paper" for item in archived_items)

    # search filter
    search_resp = client.get("/api/papers", params={"search": "alpha"})
    assert search_resp.status_code == 200
    search_items = search_resp.json()["data"]["items"]
    assert all("alpha" in item.get("title", "").lower() for item in search_items)

    # ensure summary fields present
    assert draft_items[0].get("section_count") is not None
    assert draft_items[0].get("question_count") is not None
