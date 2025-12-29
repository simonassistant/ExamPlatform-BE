from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.data.dto.question_dto import QuestionPayload, QuestionType, resolve_inheritance, QuestionOptionPayload


class QuestionGroupPayload(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: Optional[str] = None
    seq: int
    title: str
    content: Optional[str] = None
    question_type: Optional[QuestionType] = None
    unit_score: Optional[Decimal] = None
    questions: List[QuestionPayload] = []

    @field_validator('question_type', mode='before')
    @classmethod
    def _coerce_question_type(cls, value):  # type: ignore[override]
        return QuestionPayload._coerce_question_type(value)  # reuse logic

    def apply_inheritance(self, inherited_type: Optional[QuestionType]):
        resolved_type = resolve_inheritance(self.question_type, inherited_type)
        for question in self.questions:
            question.with_inherited_type(resolved_type)
        return self


class PaperSectionPayload(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: Optional[str] = None
    seq: int
    name: str
    duration: Optional[int] = None
    question_type: Optional[QuestionType] = None
    unit_score: Optional[Decimal] = None
    full_score: Optional[Decimal] = None
    pass_score: Optional[Decimal] = None
    note: Optional[str] = None
    question_groups: List[QuestionGroupPayload] = []

    @field_validator('question_type', mode='before')
    @classmethod
    def _coerce_question_type(cls, value):  # type: ignore[override]
        return QuestionPayload._coerce_question_type(value)  # reuse logic

    def apply_inheritance(self, inherited_type: Optional[QuestionType]):
        resolved_type = resolve_inheritance(self.question_type, inherited_type)
        for group in self.question_groups:
            group.apply_inheritance(resolved_type)
        return self


class PaperPayload(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: Optional[str] = None
    title: str
    duration: Optional[int] = None
    question_type: QuestionType
    full_score: Optional[Decimal] = None
    pass_score: Optional[Decimal] = None
    unit_score: Optional[Decimal] = None
    note: Optional[str] = None
    status: Optional[str] = None
    sections: List[PaperSectionPayload] = []

    @field_validator('question_type', mode='before')
    @classmethod
    def _coerce_question_type(cls, value):  # type: ignore[override]
        return QuestionPayload._coerce_question_type(value)  # reuse logic

    def apply_inheritance(self):
        for section in self.sections:
            section.apply_inheritance(self.question_type)
        return self


__all__ = [
    'QuestionType',
    'QuestionOptionPayload',
    'QuestionPayload',
    'QuestionGroupPayload',
    'PaperSectionPayload',
    'PaperPayload',
]
