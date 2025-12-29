import os
from fastapi.testclient import TestClient

os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SQLALCHEMY_ECHO", "False")

from main import app  # noqa: E402

client = TestClient(app)


SIMPLE_PAYLOAD = {
    "title": "List Me",
    "question_type": 1,
    "sections": [
        {
            "seq": 1,
            "name": "Section X",
            "question_groups": [
                {
                    "seq": 1,
                    "title": "Group X",
                    "questions": [
                        {
                            "seq": 1,
                            "title": "QX",
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


def test_duplicate_and_delete_and_list():
    # create base paper
    create_resp = client.post("/api/papers", json=SIMPLE_PAYLOAD)
    assert create_resp.status_code == 200
    paper = create_resp.json()["data"]["paper"]
    paper_id = paper["id"]

    # duplicate
    dup_resp = client.post(f"/api/papers/{paper_id}/duplicate")
    assert dup_resp.status_code == 200
    dup_id = dup_resp.json()["data"]["paper_id"]
    assert dup_id != paper_id

    # delete original
    del_resp = client.delete(f"/api/papers/{paper_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["status"] == "Archived"

    # list should include both entries (one archived)
    list_resp = client.get("/api/papers")
    assert list_resp.status_code == 200
    payload = list_resp.json()["data"]
    assert payload["total"] >= 2
    titles = [item["title"] for item in payload["items"]]
    assert "List Me" in titles

    # fetch duplicate works
    fetch_dup = client.get(f"/api/papers/{dup_id}")
    assert fetch_dup.status_code == 200
    assert fetch_dup.json()["data"]["paper"]["title"] == "List Me"
