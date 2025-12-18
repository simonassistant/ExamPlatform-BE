from datetime import datetime

from sqlalchemy import update, select, text

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_exec, db_one_or_none, db_session_query, engine
from app.data.entity.entities import Exam, ScheduleSession, Users

EXAM_STATUS_NOT_STARTED: int = 0
EXAM_STATUS_IN_PREPARATION: int = 1
EXAM_STATUS_IN_EXAM: int = 2
EXAM_STATUS_CLOSED: int = 3

class ExamDAO(BaseDAO):
    def __init__(self):
        super().__init__(Exam)

    def add_or_update(self, instance: Exam) -> str:
        instance_existing: Exam = self.get_by_session_examinee(instance.schedule_session_id, instance.examinee_email)
        if instance_existing is None:
            return self.add(instance)
        else:
            instance.id = instance_existing.id
            self.update(instance)
            return instance_existing.id

    @staticmethod
    def get_by_session_examinee(schedule_session_id: str, examinee_email: str):
        stmt = select(Exam).where(Exam.schedule_session_id == schedule_session_id, Exam.examinee_email == examinee_email)
        return db_one_or_none(stmt)

    @staticmethod
    def get_unclosed_for_examinee(examinee_id: str) -> Exam:
        stmt = (select(Exam)
                .where(Exam.examinee_id==examinee_id, Exam.status!=EXAM_STATUS_CLOSED, Exam.is_deleted.is_(None))
                .join(ScheduleSession, Exam.paper_id == ScheduleSession.paper_id)
                .order_by(ScheduleSession.plan_start).limit(1))
        return db_one_or_none(stmt)

    @staticmethod
    def get_unclosed_by_examinee_email(email: str):
        stmt = select(Exam).where(Exam.examinee_email==email, Exam.status!=EXAM_STATUS_CLOSED, Exam.is_deleted.is_(None))
        return db_one_or_none(stmt)

    @staticmethod
    def get_unclosed_by_enroll_number(enroll_number: str):
        stmt = select(Exam).where(Exam.examinee_enroll_number == enroll_number, Exam.status != EXAM_STATUS_CLOSED,
                                  Exam.is_deleted != True)
        return db_one_or_none(stmt)

    @staticmethod
    def enter_section(user_id: str, exam_id: str, seq: int):
        now = datetime.now()
        statement = update(Exam).where(Exam.id==exam_id, Exam.examinee_id==user_id, Exam.status!=EXAM_STATUS_CLOSED
            ).values(current_seq=seq, updated_at=now, updated_by=user_id)
        db_exec(statement)

    @staticmethod
    def list_in_schedule_session_for_proctor(schedule_session_id: str):
        stmt = """
SELECT
  Exam.status, Exam.actual_start, Exam.actual_end, CONCAT(Users.surname, ', ', Users.name) AS examinee,
  es.name AS section, es.status as section_status, es.actual_start AS section_start, es.actual_end AS section_end
FROM Exam
LEFT JOIN (
  SELECT es1.schedule_session_id, es1.name, exam_id, status, actual_start, actual_end FROM exam_section es1
  JOIN (
    SELECT schedule_session_id, examinee_id, MAX(seq) AS seq
        FROM exam_section
        GROUP BY schedule_session_id, examinee_id) es2
    ON es1.schedule_session_id=es2.schedule_session_id AND es1.examinee_id=es2.examinee_id AND es1.seq=es2.seq) es
  ON es.exam_id = exam.id
JOIN Users ON Exam.examinee_id = Users.id
where Exam.schedule_session_id=:schedule_session_id AND Exam.is_deleted IS NULL
"""
        result = db_session_query().execute(text(stmt).params(schedule_session_id=schedule_session_id)).all()
        return result

    @staticmethod
    def submit(exam_id: str, updated_by: str, is_timeout: bool=False):
        now = datetime.now()
        statement = update(Exam).where(Exam.id == exam_id).values(
            status=EXAM_STATUS_CLOSED, actual_end=now, is_timeout=is_timeout,
            updated_at=now, updated_by=updated_by)
        db_exec(statement)

    @staticmethod
    def update(exam: Exam):
        statement = update(Exam).where(Exam.id == exam.id).values(
            token=exam.token, status=exam.status, actual_start=exam.actual_start, actual_end=exam.actual_end,
            is_passed=exam.is_passed, is_timeout=exam.is_timeout, score=exam.score,
            examinee_id=exam.examinee_id, paper_id=exam.paper_id,
            schedule_id=exam.schedule_id, schedule_session_id=exam.schedule_session_id,
            is_deleted=exam.is_deleted, updated_at=datetime.now(), updated_by=exam.updated_by)
        db_exec(statement)
