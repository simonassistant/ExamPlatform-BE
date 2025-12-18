from datetime import datetime

from sqlalchemy import update, select

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_exec, db_one_or_none
from app.data.entity.entities import ScheduleSection


class ScheduleSectionDAO(BaseDAO):
    def __init__(self):
        super().__init__(ScheduleSection)

    def add_or_update(self, schedule_section: ScheduleSection) -> str:
        instance_existing: ScheduleSection = self.get(schedule_section.id)
        if instance_existing is None:
            return self.add(schedule_section)
        else:
            schedule_section.id = instance_existing.id
            self.update(schedule_section)
            return instance_existing.id

    @staticmethod
    def get_by_session_seq(schedule_session_id: str, seq: int) -> ScheduleSection | None:
        stmt = select(ScheduleSection).where(ScheduleSection.schedule_session_id==schedule_session_id, ScheduleSection.seq==seq)
        return db_one_or_none(stmt)

    @staticmethod
    def update(instance: ScheduleSection):
        statement = update(ScheduleSection).where(ScheduleSection.id == instance.id).values(
            plan_start_early=instance.plan_start_early, plan_start_late=instance.plan_start_late,
            seq=instance.seq, schedule_session_id=instance.schedule_session_id,
            is_deleted=instance.is_deleted, updated_at=datetime.now(), updated_by=instance.updated_by)
        db_exec(statement)