from app.data.entity.entities import ScheduleSection
from app.util.util import to_datetime


class ScheduleSectionDTO:
    def __init__(self, **kwargs):
        self.schedule_section_id = None
        self.plan_start_early = None
        self.plan_start_late = None
        self.seq = None
        self.schedule_session_id = None

    def to_entity(self) -> ScheduleSection:
        return ScheduleSection(
            id = self.schedule_section_id,
            plan_start_early = self.plan_start_early,
            plan_start_late = self.plan_start_late,
            seq = self.seq,
            schedule_session_id = self.schedule_session_id,
        )

    def md_parse_meta(self, content: str):
        index = content.find(':')
        if index == -1:
            return
        key = content[:index].strip().lower()
        value = content[index+1:].strip()
        if key == 'id':
            self.schedule_section_id = value
        elif key == 'plan early start':
            self.plan_start_early = to_datetime(value)
        elif key == 'plan late start':
            self.plan_start_late = to_datetime(value)
