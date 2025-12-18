from datetime import datetime

from sqlalchemy import update, select
from sqlalchemy.sql.functions import count

from app.data.dao.base_dao import BaseDAO
from app.data.dao.exam_dao import EXAM_STATUS_IN_EXAM, EXAM_STATUS_CLOSED
from app.data.database import db_exec, db_scalars, db_one_or_none
from app.data.entity.entities import ExamSection


class ExamSectionDAO(BaseDAO):
    def __init__(self):
        super().__init__(ExamSection)

    @staticmethod
    def count_by_exam(exam_id: str) -> int:
        statement = select(count(ExamSection)).where(ExamSection.exam_id == exam_id)
        return db_scalars(statement)

    @staticmethod
    def get_by_exam_seq(exam_id: str, seq: int) -> ExamSection | None:
        statement = select(ExamSection).where(ExamSection.exam_id == exam_id, ExamSection.seq == seq)
        return db_one_or_none(statement)

    @staticmethod
    def get_last_section(exam_id: str) -> ExamSection | None:
        statement = select(ExamSection).where(ExamSection.exam_id==exam_id).order_by(ExamSection.id.desc()).limit(1)
        return db_one_or_none(statement)

    @staticmethod
    def list_by_exam(exam_id: str) -> list[ExamSection]:
        statement = select(ExamSection).where(ExamSection.exam_id == exam_id).order_by(ExamSection.created_at)
        return db_scalars(statement)

    @staticmethod
    def start(section_id: str, updated_by: str) -> datetime:
        now = datetime.now()
        statement = update(ExamSection).where(ExamSection.id == section_id).values(
            actual_start=now, status=EXAM_STATUS_IN_EXAM,
            updated_at=now, updated_by=updated_by)
        db_exec(statement)
        return now

    @staticmethod
    def submit(section_id: str, updated_by: str, is_timeout: bool=False):
        now = datetime.now()
        statement = update(ExamSection).where(ExamSection.id == section_id).values(
            actual_end=now, status=EXAM_STATUS_CLOSED, is_timeout=is_timeout,
            updated_at=now, updated_by=updated_by)
        db_exec(statement)