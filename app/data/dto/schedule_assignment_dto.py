from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _normalize_aliases(data):
    if not isinstance(data, dict):
        return data
    alias_map = {
        "paperId": "paper_id",
        "startTime": "start_time",
        "endTime": "end_time",
        "examineeGroupFilter": "examinee_group_filter",
        "scheduleSessionId": "schedule_session_id",
    }
    return {alias_map.get(key, key): value for key, value in data.items()}


class ScheduleAssignmentBase(BaseModel):
    """Common fields for schedule assignments with camelCase + snake_case aliases."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    paper_id: str
    start_time: datetime
    end_time: datetime
    examinee_group_filter: Optional[str] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def _normalize_aliases(cls, data):  # type: ignore[override]
        return _normalize_aliases(data)

class ScheduleAssignmentCreatePayload(ScheduleAssignmentBase):
    """Payload for creating an assignment."""


class ScheduleAssignmentUpdatePayload(BaseModel):
    """Partial payload for updates; preserves existing values when omitted."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    paper_id: Optional[str] = Field(default=None)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    examinee_group_filter: Optional[str] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def _normalize_aliases(cls, data):  # type: ignore[override]
        return _normalize_aliases(data)

class ScheduleAssignmentRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    paper_id: str
    schedule_session_id: str
    start_time: datetime
    end_time: datetime
    examinee_group_filter: Optional[str] = None
