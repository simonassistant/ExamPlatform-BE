from datetime import datetime

from sqlalchemy import update, select, desc

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_exec, db_scalars, db_session_query
from app.data.entity.entities import Schedule, ScheduleSession


class ScheduleDAO(BaseDAO):
    def __init__(self):
        super().__init__(Schedule)

    def add_or_update(self, schedule: Schedule) -> str:
        instance_existing: Schedule = self.get(schedule.id)
        if instance_existing is None:
            return self.add(schedule)
        else:
            schedule.id = instance_existing.id
            self.update(schedule)
            return instance_existing.id

    @staticmethod
    def list_for_proctor(proctor_id: str):
        return db_session_query().query(Schedule).join(ScheduleSession,
            ScheduleSession.schedule_id == Schedule.id).where(ScheduleSession.proctor_id==proctor_id,
            ScheduleSession.is_deleted.is_(None), Schedule.is_deleted.is_(None)).order_by(
            desc(Schedule.updated_at)).all()

    @staticmethod
    def update(schedule: Schedule):
        statement = update(Schedule).where(Schedule.id == schedule.id).values(
            title=schedule.title,
            is_deleted=schedule.is_deleted, updated_at=datetime.now(), updated_by=schedule.updated_by)
        db_exec(statement)