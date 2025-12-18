from datetime import datetime

from sqlalchemy import select, update

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_session_query, db_exec, db_one_or_none, db_scalars
from app.data.entity.entities import QuestionOption


class QuestionOptionDAO(BaseDAO):
    def __init__(self):
        super().__init__(QuestionOption)

    def add_or_update(self, instance: QuestionOption) -> str:
        instance_existing: QuestionOption = self.get_by_paper_question_code(paper_id=instance.paper_id,
                question_id=instance.question_id, code=instance.code)
        if instance_existing is None:
            return self.add(instance)
        else:
            instance.id = instance_existing.id
            self.update(instance)
            return instance_existing.id

    @staticmethod
    def get_by_paper_question_code(paper_id: str, question_id: str, code: str):
        stmt = select(QuestionOption).where(QuestionOption.paper_id == paper_id,
                                            QuestionOption.question_id == question_id,
                                            QuestionOption.code==code)
        return db_one_or_none(stmt)

    @staticmethod
    def list_by_question_4_exam(paper_id: str, question_id: str) -> list[QuestionOption]:
        stmt = (select(QuestionOption)
                .where(QuestionOption.paper_id == paper_id, QuestionOption.question_id == question_id)
                .order_by(QuestionOption.code))
        options = db_scalars(stmt)
        for option in options:
            option.is_correct = None
        return options

    @staticmethod
    def list_by_question_group(question_ids: list[str]):
        options = db_session_query().query(QuestionOption).filter(QuestionOption.question_id.in_(question_ids)
               ).order_by(QuestionOption.question_id, QuestionOption.code).all()
        for option in options:
            option.is_correct = None
        return options

    @staticmethod
    def update(option: QuestionOption):
        statement = update(QuestionOption).where(QuestionOption.id == option.id).values(
            code=option.code, content=option.content, is_correct=option.is_correct,
            question_id=option.question_id, paper_id=option.paper_id,
            is_deleted=option.is_deleted, updated_at=datetime.now(), updated_by=option.updated_by)
        db_exec(statement)