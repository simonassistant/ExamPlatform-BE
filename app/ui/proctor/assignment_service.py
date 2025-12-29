from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class Assignment:
    id: str
    paper_id: str
    schedule_session_id: str
    start_time: datetime
    end_time: datetime
    examinee_group_filter: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AssignmentConflictError(Exception):
    pass


class AssignmentLockedError(Exception):
    pass


class AssignmentService:
    def __init__(self):
        # session_id -> assignments
        self._store: Dict[str, List[Assignment]] = {}

    def _parse_dt(self, value: str | datetime) -> datetime:
        if isinstance(value, datetime):
            parsed = value
        else:
            parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)
        return parsed

    def _ensure_window(self, session_id: str, start: datetime, end: datetime, exclude_id: Optional[str] = None):
        if start >= end:
            raise AssignmentConflictError("Start time must be before end time")
        for a in self._store.get(session_id, []):
            if exclude_id and a.id == exclude_id:
                continue
            if not (end <= a.start_time or start >= a.end_time):
                raise AssignmentConflictError("Assignment time overlaps with existing assignment")

    def _ensure_not_started(self, assignment: Assignment):
        if datetime.now(timezone.utc) >= assignment.start_time:
            raise AssignmentLockedError("Assignment already started")

    def create(self, session_id: str, paper_id: str, start_time: str | datetime, end_time: str | datetime, examinee_group_filter: Optional[str] = None) -> Assignment:
        start = self._parse_dt(start_time)
        end = self._parse_dt(end_time)
        self._ensure_window(session_id, start, end)
        assignment = Assignment(
            id=str(uuid4()),
            paper_id=paper_id,
            schedule_session_id=session_id,
            start_time=start,
            end_time=end,
            examinee_group_filter=examinee_group_filter,
        )
        self._store.setdefault(session_id, []).append(assignment)
        return assignment

    def update(
        self,
        session_id: str,
        assignment_id: str,
        *,
        paper_id: Optional[str] = None,
        start_time: Optional[str | datetime] = None,
        end_time: Optional[str | datetime] = None,
        examinee_group_filter: Optional[str] = None,
    ) -> Assignment:
        assignment = self.get(session_id, assignment_id)
        if assignment is None:
            raise KeyError("Assignment not found")
        self._ensure_not_started(assignment)
        new_start = self._parse_dt(start_time) if start_time else assignment.start_time
        new_end = self._parse_dt(end_time) if end_time else assignment.end_time
        self._ensure_window(session_id, new_start, new_end, exclude_id=assignment_id)
        assignment.paper_id = paper_id or assignment.paper_id
        assignment.start_time = new_start
        assignment.end_time = new_end
        assignment.examinee_group_filter = examinee_group_filter if examinee_group_filter is not None else assignment.examinee_group_filter
        return assignment

    def delete(self, session_id: str, assignment_id: str) -> None:
        assignment = self.get(session_id, assignment_id)
        if assignment is None:
            return
        self._ensure_not_started(assignment)
        self._store[session_id] = [a for a in self._store.get(session_id, []) if a.id != assignment_id]

    def get(self, session_id: str, assignment_id: str) -> Optional[Assignment]:
        for a in self._store.get(session_id, []):
            if a.id == assignment_id:
                return a
        return None

    def list(self, session_id: str) -> List[Assignment]:
        return list(self._store.get(session_id, []))
