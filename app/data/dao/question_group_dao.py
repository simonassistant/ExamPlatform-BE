from datetime import datetime

from sqlalchemy import update, select

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_exec, db_session_query, db_one_or_none
from app.data.entity.entities import QuestionGroup


class QuestionGroupDAO(BaseDAO):
    def __init__(self):
        super().__init__(QuestionGroup)

    def add_or_update(self, instance: QuestionGroup) -> str:
        instance_existing: QuestionGroup = self.get_by_paper_section_title(paper_id=instance.paper_id,
                section_id=instance.section_id, title=instance.title)
        if instance_existing is None:
            return self.add(instance)
        else:
            instance.id = instance_existing.id
            self.update(instance)
            return instance_existing.id

    @staticmethod
    def get_by_paper_section_title(paper_id: str, section_id: str, title: str):
        stmt = select(QuestionGroup).where(QuestionGroup.paper_id==paper_id,
                                           QuestionGroup.section_id==section_id,
                                           QuestionGroup.title==title)
        return db_one_or_none(stmt)

    @staticmethod
    def update(question_group: QuestionGroup):
        statement = update(QuestionGroup).where(QuestionGroup.id == question_group.id).values(
            seq=question_group.seq, code=question_group.code, title=question_group.title, question_type=question_group.question_type,
            content=question_group.content, unit_score=question_group.unit_score, full_score=question_group.full_score,
            section_id=question_group.section_id, paper_id=question_group.paper_id,
            is_deleted=question_group.is_deleted, updated_at=datetime.now(), updated_by=question_group.updated_by)
        db_exec(statement)
