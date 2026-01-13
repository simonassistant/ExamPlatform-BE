"""Paper service for CRUD operations on exam papers."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select

from app.data.dao.paper_dao import PaperDAO
from app.data.dao.paper_section_dao import PaperSectionDAO
from app.data.dao.question_dao import QuestionDAO
from app.data.dao.question_option import QuestionOptionDAO
from app.data.database import db_scalars
from app.data.dto.paper_dto import PaperDTO
from app.data.entity.entities import (
    Paper,
    PaperSection,
    Question,
    QuestionOption,
)


class PaperService:
    """Service class for paper management operations."""

    @staticmethod
    def create_paper(
        title: str,
        duration: int,
        full_score: Decimal,
        pass_score: Decimal,
        paper_id: Optional[str] = None,
        paper_type: Optional[int] = None,
        note: Optional[str] = None,
        question_type: Optional[int] = None,
        unit_score: Optional[Decimal] = None,
        created_by: Optional[str] = None,
    ) -> str:
        """Create a new paper and return its ID."""
        paper = Paper(
            id=paper_id,
            title=title,
            note=note,
            paper_type=paper_type,
            duration=duration,
            question_type=question_type,
            unit_score=unit_score,
            full_score=full_score,
            pass_score=pass_score,
            section_num=0,
            question_num=0,
            created_by=created_by,
        )
        return PaperDAO().add(paper)

    @staticmethod
    def get_paper(paper_id: str) -> Optional[Paper]:
        """Get a paper by ID."""
        return PaperDAO().get(paper_id)

    @staticmethod
    def get_paper_full(paper_id: str) -> dict:
        """Get a paper with all sections, questions, and options."""
        paper = PaperDAO().get(paper_id)
        if paper is None:
            return {}

        sections = PaperSectionDAO.list_by_paper(paper_id)
        section_ids = [s.id for s in sections]

        # Get all questions for this paper
        questions = []
        if section_ids:
            stmt = (
                select(Question)
                .where(
                    Question.paper_id == paper_id,
                    Question.is_deleted.is_(None),
                )
                .order_by(Question.section_id, Question.seq)
            )
            questions = db_scalars(stmt)

        question_ids = [q.id for q in questions]

        # Get all options for these questions
        options = []
        if question_ids:
            stmt = (
                select(QuestionOption)
                .where(
                    QuestionOption.paper_id == paper_id,
                    QuestionOption.is_deleted.is_(None),
                )
                .order_by(QuestionOption.question_id, QuestionOption.code)
            )
            options = db_scalars(stmt)

        # Build nested structure
        options_by_question = {}
        for opt in options:
            if opt.question_id not in options_by_question:
                options_by_question[opt.question_id] = []
            options_by_question[opt.question_id].append({
                "id": opt.id,
                "code": opt.code,
                "content": opt.content,
                "is_correct": opt.is_correct,
            })

        questions_by_section = {}
        for q in questions:
            if q.section_id not in questions_by_section:
                questions_by_section[q.section_id] = []
            questions_by_section[q.section_id].append({
                "id": q.id,
                "seq": q.seq,
                "code": q.code,
                "content": q.content,
                "question_type": q.question_type,
                "score": float(q.score) if q.score else None,
                "options": options_by_question.get(q.id, []),
            })

        sections_data = []
        for s in sections:
            sections_data.append({
                "id": s.id,
                "seq": s.seq,
                "name": s.name,
                "content": s.content,
                "duration": s.duration,
                "question_type": s.question_type,
                "unit_score": float(s.unit_score) if s.unit_score else None,
                "full_score": float(s.full_score) if s.full_score else None,
                "pass_score": float(s.pass_score) if s.pass_score else None,
                "note": s.note,
                "questions": questions_by_section.get(s.id, []),
            })

        return {
            "id": paper.id,
            "title": paper.title,
            "note": paper.note,
            "paper_type": paper.paper_type,
            "duration": paper.duration,
            "question_type": paper.question_type,
            "unit_score": float(paper.unit_score) if paper.unit_score else None,
            "full_score": float(paper.full_score) if paper.full_score else None,
            "pass_score": float(paper.pass_score) if paper.pass_score else None,
            "section_num": paper.section_num,
            "question_num": paper.question_num,
            "sections": sections_data,
        }

    @staticmethod
    def update_paper(
        paper_id: str,
        title: Optional[str] = None,
        note: Optional[str] = None,
        paper_type: Optional[int] = None,
        duration: Optional[int] = None,
        question_type: Optional[int] = None,
        unit_score: Optional[Decimal] = None,
        full_score: Optional[Decimal] = None,
        pass_score: Optional[Decimal] = None,
        updated_by: Optional[str] = None,
    ) -> bool:
        """Update paper metadata. Returns True if successful."""
        paper = PaperDAO().get(paper_id)
        if paper is None:
            return False

        if title is not None:
            paper.title = title
        if note is not None:
            paper.note = note
        if paper_type is not None:
            paper.paper_type = paper_type
        if duration is not None:
            paper.duration = duration
        if question_type is not None:
            paper.question_type = question_type
        if unit_score is not None:
            paper.unit_score = unit_score
        if full_score is not None:
            paper.full_score = full_score
        if pass_score is not None:
            paper.pass_score = pass_score
        paper.updated_by = updated_by

        PaperDAO.update(paper)
        return True

    @staticmethod
    def delete_paper(paper_id: str, deleted_by: str) -> bool:
        """Soft-delete a paper and all its contents."""
        paper = PaperDAO().get(paper_id)
        if paper is None:
            return False

        # Soft-delete all child entities
        sections = PaperSectionDAO.list_by_paper(paper_id)
        for section in sections:
            PaperSectionDAO().delete(section.id, deleted_by)

        stmt = select(Question).where(Question.paper_id == paper_id)
        questions = db_scalars(stmt)
        for question in questions:
            QuestionDAO().delete(question.id, deleted_by)

        stmt = select(QuestionOption).where(QuestionOption.paper_id == paper_id)
        options = db_scalars(stmt)
        for option in options:
            QuestionOptionDAO().delete(option.id, deleted_by)

        # Soft-delete the paper itself
        PaperDAO().delete(paper_id, deleted_by)
        return True

    @staticmethod
    def list_papers(proctor_id: Optional[str] = None) -> list:
        """List all papers, optionally filtered by creator."""
        stmt = select(Paper).where(Paper.is_deleted.is_(None)).order_by(Paper.created_at.desc())
        papers = db_scalars(stmt)
        return [
            {
                "id": p.id,
                "title": p.title,
                "section_num": p.section_num,
                "question_num": p.question_num,
                "duration": p.duration,
                "full_score": float(p.full_score) if p.full_score else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in papers
        ]

    @staticmethod
    def save_paper_full(paper_data: dict, user_id: str) -> str:
        """
        Save a complete paper with all sections, question groups, questions, and options.
        This is an upsert operation - create new or update existing based on IDs.
        """
        paper_id = paper_data.get("id")
        is_new = paper_id is None

        # Create or update paper
        if is_new:
            paper_id = PaperService.create_paper(
                title=paper_data.get("title", "Untitled"),
                paper_type=paper_data.get("paper_type"),
                duration=paper_data.get("duration", 0),
                full_score=Decimal(str(paper_data.get("full_score", 0))),
                pass_score=Decimal(str(paper_data.get("pass_score", 0))),
                note=paper_data.get("note"),
                question_type=paper_data.get("question_type"),
                unit_score=Decimal(str(paper_data.get("unit_score", 0))) if paper_data.get("unit_score") else None,
                created_by=user_id,
            )
        else:
            # Check if paper actually exists
            existing_paper = PaperDAO().get(paper_id)
            if existing_paper:
                PaperService.update_paper(
                    paper_id=paper_id,
                    title=paper_data.get("title"),
                    note=paper_data.get("note"),
                    paper_type=paper_data.get("paper_type"),
                    duration=paper_data.get("duration"),
                    question_type=paper_data.get("question_type"),
                    unit_score=Decimal(str(paper_data.get("unit_score"))) if paper_data.get("unit_score") else None,
                    full_score=Decimal(str(paper_data.get("full_score"))) if paper_data.get("full_score") else None,
                    pass_score=Decimal(str(paper_data.get("pass_score"))) if paper_data.get("pass_score") else None,
                    updated_by=user_id,
                )
            else:
                # ID exists but paper doesn't (Upsert case for imports)
                PaperService.create_paper(
                    title=paper_data.get("title", "Untitled"),
                    paper_type=paper_data.get("paper_type"),
                    duration=paper_data.get("duration", 0),
                    full_score=Decimal(str(paper_data.get("full_score", 0))),
                    pass_score=Decimal(str(paper_data.get("pass_score", 0))),
                    paper_id=paper_id,
                    note=paper_data.get("note"),
                    question_type=paper_data.get("question_type"),
                    unit_score=Decimal(str(paper_data.get("unit_score", 0))) if paper_data.get("unit_score") else None,
                    created_by=user_id,
                )

        # Track existing IDs to detect deletions (simplified for now, full sync would need list and diff)
        existing_section_ids = set()
        existing_question_ids = set()
        existing_option_ids = set()

        total_questions = 0

        # Process sections
        sections = paper_data.get("sections", [])
        for section_data in sections:
            section = PaperSection(
                id=section_data.get("id"),
                seq=section_data.get("seq", 1),
                name=section_data.get("name", "Section"),
                content=section_data.get("content"),
                duration=section_data.get("duration"),
                question_type=section_data.get("question_type"),
                unit_score=Decimal(str(section_data.get("unit_score"))) if section_data.get("unit_score") else None,
                full_score=Decimal(str(section_data.get("full_score"))) if section_data.get("full_score") else None,
                pass_score=Decimal(str(section_data.get("pass_score"))) if section_data.get("pass_score") else None,
                note=section_data.get("note"),
                paper_id=paper_id,
                created_by=user_id,
                updated_by=user_id,
            )
            section_id = PaperSectionDAO().add_or_update(section)
            existing_section_ids.add(section_id)

            # Process questions
            for question_data in section_data.get("questions", []):
                total_questions += 1
                question = Question(
                    id=question_data.get("id"),
                    seq=question_data.get("seq", 1),
                    code=question_data.get("code"),
                    content=question_data.get("content"),
                    question_type=question_data.get("question_type"),
                    score=Decimal(str(question_data.get("score"))) if question_data.get("score") else None,
                    section_id=section_id,
                    paper_id=paper_id,
                    created_by=user_id,
                    updated_by=user_id,
                )
                question_id = QuestionDAO().add_or_update(question)
                existing_question_ids.add(question_id)

                # Process options
                for option_data in question_data.get("options", []):
                    option = QuestionOption(
                        id=option_data.get("id"),
                        code=option_data.get("code", "A"),
                        content=option_data.get("content"),
                        is_correct=option_data.get("is_correct", False),
                        correct_seq=option_data.get("correct_seq"),
                        question_id=question_id,
                        paper_id=paper_id,
                        created_by=user_id,
                        updated_by=user_id,
                    )
                    option_id = QuestionOptionDAO().add_or_update(option)
                    existing_option_ids.add(option_id)

        # Update paper counts
        paper = PaperDAO().get(paper_id)
        paper.section_num = len(sections)
        paper.question_num = total_questions
        paper.updated_by = user_id
        PaperDAO.update(paper)

        return paper_id

    @staticmethod
    def import_from_markdown(md_content: str, user_id: str) -> str:
        """Import a paper from markdown content. Returns the paper ID."""
        import tempfile
        import os

        # Write content to a temp file for the existing parser
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(md_content)
            temp_path = f.name

        try:
            paper_dto = PaperDTO().md_parse(temp_path)

            # Convert to the format expected by save_paper_full
            sections_data = []
            for section_dto in paper_dto.sections:
                questions_data = []
                for question_dto in section_dto.questions:
                    options_data = []
                    for opt_dto in question_dto.question_options:
                        options_data.append({
                            "code": opt_dto.code,
                            "content": opt_dto.content,
                            "is_correct": opt_dto.is_correct,
                        })
                    questions_data.append({
                        "seq": question_dto.seq,
                        "content": question_dto.content,
                        "question_type": question_dto.question_type,
                        "score": float(question_dto.score) if question_dto.score else None,
                        "options": options_data,
                    })
                sections_data.append({
                    "seq": section_dto.seq,
                    "name": section_dto.name,
                    "content": section_dto.content,
                    "duration": section_dto.duration,
                    "question_type": section_dto.question_type,
                    "unit_score": float(section_dto.unit_score) if section_dto.unit_score else None,
                    "full_score": float(section_dto.full_score) if section_dto.full_score else None,
                    "pass_score": float(section_dto.pass_score) if section_dto.pass_score else None,
                    "note": section_dto.note,
                    "questions": questions_data,
                })

            paper_data = {
                "id": paper_dto.paper_id,
                "title": paper_dto.title,
                "note": paper_dto.note,
                "paper_type": paper_dto.paper_type,
                "duration": paper_dto.duration,
                "question_type": paper_dto.question_type,
                "unit_score": float(paper_dto.unit_score) if paper_dto.unit_score else None,
                "full_score": float(paper_dto.full_score) if paper_dto.full_score else None,
                "pass_score": float(paper_dto.pass_score) if paper_dto.pass_score else None,
                "sections": sections_data,
            }

            return PaperService.save_paper_full(paper_data, user_id)
        finally:
            os.unlink(temp_path)
