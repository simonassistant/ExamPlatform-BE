from datetime import datetime

from sqlalchemy import update, select, desc

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_exec, db_scalars, db_session_query
from app.data.entity.entities import ScheduleSession, Schedule


class ScheduleSessionDAO(BaseDAO):
    def __init__(self):
        super().__init__(ScheduleSession)

    def add_or_update(self, schedule_session: ScheduleSession) -> str:
        instance_existing: ScheduleSession = self.get(schedule_session.id)
        if instance_existing is None:
            return self.add(schedule_session)
        else:
            schedule_session.id = instance_existing.id
            self.update(schedule_session)
            return instance_existing.id

    @staticmethod
    def list_for_schedule_proctor(schedule_id: str, proctor_id: str):
        statement = select(ScheduleSession).where(ScheduleSession.proctor_id == proctor_id,
            ScheduleSession.schedule_id == schedule_id, ScheduleSession.is_deleted.is_(None)).order_by(
            desc(ScheduleSession.plan_start))
        return db_scalars(statement)

    @staticmethod
    def update(schedule_session: ScheduleSession):
        statement = update(ScheduleSession).where(ScheduleSession.id == schedule_session.id).values(
            title=schedule_session.title, is_ready=schedule_session.is_ready,
            plan_start=schedule_session.plan_start, plan_end=schedule_session.plan_end,
            schedule_id=schedule_session.schedule_id, paper_id=schedule_session.paper_id,
            proctor_email=schedule_session.proctor_email, proctor_id=schedule_session.proctor_id,
            is_deleted=schedule_session.is_deleted, updated_at=datetime.now(), updated_by=schedule_session.updated_by)
        db_exec(statement)