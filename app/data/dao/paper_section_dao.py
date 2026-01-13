from datetime import datetime

from sqlalchemy import update, and_, select
from ulid import ULID

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_exec, db_session_query, db_one_or_none, db_scalars
from app.data.entity.entities import PaperSection


class PaperSectionDAO(BaseDAO):
    def __init__(self):
        super().__init__(PaperSection)

    def add_or_update(self, section: PaperSection) -> str:
        instance_existing: PaperSection = self.get_by_paper(section.paper_id, section.name)
        if instance_existing is None:
            return self.add(section)
        else:
            section.id = instance_existing.id
            self.update(section)
            return instance_existing.id

    @staticmethod
    def get_by_paper(paper_id: str, name: str) -> PaperSection:
        stmt = select(PaperSection).where(PaperSection.paper_id == paper_id, PaperSection.name == name)
        return db_one_or_none(stmt)

    @staticmethod
    def get_by_paper_seq(paper_id: str, seq: int) -> PaperSection | None:
        statement = select(PaperSection).where(PaperSection.paper_id == paper_id, PaperSection.seq == seq)
        return db_one_or_none(statement)

    @staticmethod
    def list_by_paper(paper_id: str):
        stmt = (select(PaperSection)
                .where(PaperSection.paper_id==paper_id, PaperSection.is_deleted.is_(None))
                .order_by(PaperSection.seq))
        return db_scalars(stmt)

    @staticmethod
    def update(section: PaperSection):
        statement = update(PaperSection).where(and_(PaperSection.paper_id == section.paper_id,
            PaperSection.name == section.name)).values(
            seq=section.seq, name=section.name, content=section.content, note=section.note, question_type=section.question_type,
            duration=section.duration, full_score=section.full_score,
            pass_score=section.pass_score, unit_score=section.unit_score, question_num=section.question_num,
            is_deleted=section.is_deleted, updated_at=datetime.now(), updated_by=section.updated_by)
        db_exec(statement)