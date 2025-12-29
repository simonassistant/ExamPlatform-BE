"""Paper service with lightweight in-memory behavior for current phase.

This keeps contract/integration tests green without requiring a DB while we
layer in full persistence later. An optional audit hook can emit structured
logs with redaction.
"""

from typing import Optional, Protocol, Any, Dict
from uuid import uuid4
from copy import deepcopy

from app.data.dto.paper_dto import PaperDTO
from app.data.dto.paper_schema import PaperPayload
from app.data.dto.question_dto import QuestionType


class AuditHook(Protocol):
    def record(self, event: str, payload: dict, user_id: Optional[str] = None) -> None:  # pragma: no cover - interface
        ...


class PaperService:
    def __init__(self, audit_hook: Optional[AuditHook] = None):
        self._audit_hook = audit_hook
        self._store: Dict[str, Dict[str, Any]] = {}

    def _emit_audit(self, event: str, payload: dict, user_id: Optional[str] = None) -> None:
        if self._audit_hook:
            self._audit_hook.record(event, payload, user_id)

    # --- Lifecycle operations ---
    def import_markdown(self, markdown_text: str, user_id: Optional[str] = None) -> Any:
        self._emit_audit("paper.import.requested", {"length": len(markdown_text)}, user_id)
        dto = PaperDTO().md_parse_content(markdown_text)
        return {
            "title": dto.title,
            "sections_count": len(dto.sections),
            "question_count": len(dto.questions),
        }

    def create_draft(self, payload: PaperPayload, user_id: Optional[str] = None) -> Any:
        payload.apply_inheritance()
        paper_id = payload.id or str(uuid4())
        data = payload.model_dump()
        data["id"] = paper_id
        data["status"] = "Draft"
        self._store[paper_id] = data
        self._emit_audit("paper.create.requested", {"paper_id": paper_id, "title": payload.title}, user_id)
        return {"paper": data}

    def update_draft(self, paper_id: str, payload: PaperPayload, user_id: Optional[str] = None) -> Any:
        payload.apply_inheritance()
        data = payload.model_dump()
        data["id"] = paper_id
        if not data.get("status"):
            data["status"] = "Draft"
        self._store[paper_id] = data
        self._emit_audit("paper.update.requested", {"paper_id": paper_id}, user_id)
        return {"paper": data}

    def publish(self, paper_id: str, version: Optional[int] = None, user_id: Optional[str] = None) -> Any:
        paper = self._store.get(paper_id, {"id": paper_id})
        paper["status"] = "Published"
        paper["version"] = version or 1
        self._store[paper_id] = paper
        self._emit_audit("paper.publish.requested", {"paper_id": paper_id, "version": version}, user_id)
        return {"status": "Published", "paper_id": paper_id, "version": paper["version"]}

    def duplicate(self, paper_id: str, user_id: Optional[str] = None) -> Any:
        source = deepcopy(self._store.get(paper_id, {"id": paper_id}))
        new_id = str(uuid4())
        duplicated = {**source, "id": new_id, "status": "Draft"}
        self._store[new_id] = duplicated
        self._emit_audit("paper.duplicate.requested", {"paper_id": paper_id, "new_id": new_id}, user_id)
        return {"paper_id": new_id, "status": "Draft"}

    def soft_delete(self, paper_id: str, user_id: Optional[str] = None) -> Any:
        paper = self._store.get(paper_id, {"id": paper_id})
        paper["status"] = "Archived"
        self._store[paper_id] = paper
        self._emit_audit("paper.delete.requested", {"paper_id": paper_id}, user_id)
        return {"paper_id": paper_id, "status": "Archived"}

    def fetch(self, paper_id: str, user_id: Optional[str] = None) -> Any:
        self._emit_audit("paper.fetch.requested", {"paper_id": paper_id}, user_id)
        if paper_id not in self._store:
            return None
        return self._store[paper_id]

    def list(self, status: Optional[str] = None, search: Optional[str] = None, page: int = 1, page_size: int = 50) -> Any:
        items = list(self._store.values())
        if status:
            items = [p for p in items if str(p.get("status")) == status]
        if search:
            s = search.lower()
            items = [p for p in items if s in str(p.get("title", "")).lower()]

        total = len(items)
        start = max(page - 1, 0) * page_size
        end = start + page_size
        paged = items[start:end]

        def summarize(paper: Dict[str, Any]) -> Dict[str, Any]:
            sections = paper.get("sections", []) or []
            section_count = len(sections)
            question_count = 0
            for section in sections:
                for group in section.get("question_groups", []) or []:
                    question_count += len(group.get("questions", []) or [])
            return {
                "id": paper.get("id"),
                "title": paper.get("title"),
                "status": paper.get("status"),
                "section_count": section_count,
                "question_count": question_count,
                "updated_at": paper.get("updated_at"),
            }

        return {"items": [summarize(p) for p in paged], "total": total}
