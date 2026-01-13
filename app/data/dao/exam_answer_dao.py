from datetime import datetime

from sqlalchemy import select, update

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_one_or_none, db_exec
from app.data.entity.entities import ExamAnswer


class ExamAnswerDAO(BaseDAO):
    def __init__(self):
        super().__init__(ExamAnswer)

    @staticmethod
    def get_by_examinee_question(examinee_id: str, question_id: str):
        stmt = select(ExamAnswer).where(ExamAnswer.question_id == question_id, ExamAnswer.examinee_id == examinee_id)
        return db_one_or_none(stmt)

    @staticmethod
    def mark(user_id:str, instance_id:str, mark: bool):
        stmt = update(ExamAnswer).where(ExamAnswer.id == instance_id, ExamAnswer.examinee_id == user_id).values(
            marked=mark, updated_at=datetime.now(), updated_by=user_id)
        db_exec(stmt)

    @staticmethod
    def submit(user_id:str, instance_id:str, answer: str):
        stmt = update(ExamAnswer).where(ExamAnswer.id == instance_id).values(
            answer=answer, updated_at=datetime.now(), updated_by=user_id)
        db_exec(stmt)