import os
from fastapi.testclient import TestClient

# Ensure DB env vars exist before app import
os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SQLALCHEMY_ECHO", "False")

from main import app  # noqa: E402

client = TestClient(app)

SIMPLE_MD = """
- Question Type: Single Choice
# Sample Paper
## Section A
### Group 1
#### Q1
This is question one.
- [x] Option A
- [ ] Option B
"""


def test_import_paper_returns_structure():
    resp = client.post("/api/papers/import", params={"markdown_text": SIMPLE_MD})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["sections_count"] == 1
    assert data["question_count"] == 1


def test_create_and_publish_paper():
    payload = {
        "title": "Draft Paper",
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
    create_resp = client.post("/api/papers", json=payload)
    assert create_resp.status_code == 200
    paper = create_resp.json()["data"]["paper"]
    assert paper["title"] == "Draft Paper"
    assert paper["sections"][0]["question_groups"][0]["questions"][0]["options"]

    publish_resp = client.post("/api/papers/sample-id/publish", params={"version": 1})
    assert publish_resp.status_code == 200
    assert publish_resp.json()["data"]["status"] == "Published"
