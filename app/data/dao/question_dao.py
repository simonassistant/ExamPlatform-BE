from datetime import datetime

from sqlalchemy import update, select

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_exec, db_session_query, db_one_or_none, db_scalars
from app.data.entity.entities import Question


class QuestionDAO(BaseDAO):
    def __init__(self):
        super().__init__(Question)

    def add_or_update(self, instance: Question) -> str:
        instance_existing: Question = self.get_by_paper_section_seq(paper_id=instance.paper_id,
            section_id=instance.section_id, seq=instance.seq)
        if instance_existing is None:
            return self.add(instance)
        else:
            instance.id = instance_existing.id
            self.update(instance)
            return instance_existing.id

    @staticmethod
    def get_by_paper_section_seq(paper_id: str, section_id: str, seq: int):
        stmt = select(Question).where(Question.paper_id == paper_id,
                                      Question.section_id == section_id,
                                      Question.seq == seq)
        return db_one_or_none(stmt)



    @staticmethod
    def list_by_section(section_id: str):
        stmt = select(Question).where(Question.section_id == section_id).order_by(Question.seq)
        return db_scalars(stmt)

    @staticmethod
    def update(question: Question):
        statement = update(Question).where(Question.id == question.id).values(
            seq=question.seq, code=question.code, question_type=question.question_type,
            content=question.content, score=question.score,
            section_id=question.section_id, paper_id=question.paper_id,
            is_deleted=question.is_deleted, updated_at=datetime.now(), updated_by=question.updated_by)
        db_exec(statement)
