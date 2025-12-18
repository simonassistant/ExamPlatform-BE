from datetime import datetime

from sqlalchemy import update

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_exec
from app.data.entity.entities import Paper

QUESTION_TYPE_SINGLE_CHOICE: int = 1
QUESTION_TYPE_TRUE_FALSE: int = 2
QUESTION_TYPE_DEFINITE_MULTIPLE_CHOICE: int = 3
QUESTION_TYPE_INDEFINITE_MULTIPLE_CHOICE: int = 4
QUESTION_TYPE_FILL_IN_THE_BLANK: int = 5
QUESTION_TYPE_WRITING: int = 6
QUESTION_TYPE_LISTENING: int = 7
QUESTION_TYPE_SPEAKING: int = 8


class PaperDAO(BaseDAO):
    def __init__(self):
        super().__init__(Paper)

    def add_or_update(self, paper: Paper) -> str:
        instance_existing: Paper = self.get(paper.id)
        if instance_existing is None:
            return self.add(paper)
        else:
            paper.id = instance_existing.id
            self.update(paper)
            return instance_existing.id

    @staticmethod
    def update(paper: Paper):
        statement = update(Paper).where(Paper.id == paper.id).values(
            title=paper.title, note=paper.note, duration=paper.duration,
            question_type=paper.question_type, unit_score=paper.unit_score, full_score=paper.full_score,
            pass_score=paper.pass_score, question_num=paper.question_num, section_num=paper.section_num,
            is_deleted=paper.is_deleted, updated_at=datetime.now(), updated_by=paper.updated_by)
        db_exec(statement)