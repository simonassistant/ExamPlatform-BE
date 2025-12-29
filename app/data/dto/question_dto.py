from decimal import Decimal
from enum import IntEnum
from typing import List, Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.data.dao.paper_dao import (
    QUESTION_TYPE_SINGLE_CHOICE,
    QUESTION_TYPE_TRUE_FALSE,
    QUESTION_TYPE_DEFINITE_MULTIPLE_CHOICE,
    QUESTION_TYPE_INDEFINITE_MULTIPLE_CHOICE,
    QUESTION_TYPE_WRITING,
    QUESTION_TYPE_LISTENING,
    QUESTION_TYPE_SPEAKING,
    QUESTION_TYPE_FILL_IN_THE_BLANK,
)
from app.data.dto.question_option_dto import QuestionOptionDTO
from app.data.entity.entities import Question


class QuestionType(IntEnum):
    SINGLE_CHOICE = QUESTION_TYPE_SINGLE_CHOICE
    TRUE_FALSE = QUESTION_TYPE_TRUE_FALSE
    DEFINITE_MULTIPLE_CHOICE = QUESTION_TYPE_DEFINITE_MULTIPLE_CHOICE
    INDEFINITE_MULTIPLE_CHOICE = QUESTION_TYPE_INDEFINITE_MULTIPLE_CHOICE
    FILL_IN_THE_BLANK = QUESTION_TYPE_FILL_IN_THE_BLANK
    WRITING = QUESTION_TYPE_WRITING
    LISTENING = QUESTION_TYPE_LISTENING
    SPEAKING = QUESTION_TYPE_SPEAKING


def resolve_inheritance(*values: Optional[int | QuestionType]):
    for value in values:
        if value is not None:
            return QuestionType(value)
    return None


class QuestionDTO:
    def __init__(self, **kwargs):
        self.question_id = None
        self.seq = 0
        self.code = None
        self.content = None
        self.question_type = None
        self.score = 0
        self.section_id = None
        self.paper_id = None
        self.question_group_id = None
        self.question_options:List[QuestionOptionDTO] = []

    def md_parse_meta(self, content: str):
        lines = content.split('\n')
        for line in lines:
            data = line.split(':')
            if len(data) == 2:
                key = data[0].strip().lower()
                value = data[1].strip()
                if key == 'question type':
                    self.question_type = QuestionDTO.md_parse_question_type(value)
                elif key == 'score':
                    self.score = Decimal(value)

    @staticmethod
    def md_parse_question_type(text: str):
        if text is None:
            return None
        match text.strip().lower().replace('-', ' ').replace('_', ' '):
            case 'single choice' | 'single choice question':
                return QUESTION_TYPE_SINGLE_CHOICE
            case 'true false' | 'true or false' | 'yes no' | 'yes or no':
                return QUESTION_TYPE_TRUE_FALSE
            case 'definite multiple choice' | 'multiple choice' | 'definite multiple choice question'| 'multiple choice question' | 'reading':
                return QUESTION_TYPE_DEFINITE_MULTIPLE_CHOICE
            case 'indefinite multiple choice' | 'indefinite multiple choice question':
                return QUESTION_TYPE_INDEFINITE_MULTIPLE_CHOICE
            case 'fill in the blank' | 'fill in the blank question' | 'fill in':
                return QUESTION_TYPE_FILL_IN_THE_BLANK
            case 'writing' | 'writing question' | 'essay':
                return QUESTION_TYPE_WRITING
            case 'listening' | 'listening question' | 'audio':
                return QUESTION_TYPE_LISTENING
            case 'speaking' | 'speaking question':
                return QUESTION_TYPE_SPEAKING
        return None

    def to_entity(self) -> Question:
        return Question(
            id = self.question_id,
            seq = self.seq,
            code = self.code,
            content = self.content,
            question_type = self.question_type,
            score = self.score,
            question_group_id = self.question_group_id,
            section_id = self.section_id,
            paper_id = self.paper_id
        )


class QuestionOptionPayload(BaseModel):
    model_config = ConfigDict(extra='forbid', populate_by_name=True)

    id: Optional[str] = None
    seq: int = 1
    option_text: str = Field(alias="optionText")
    is_correct: bool = Field(default=False, alias="isCorrect")
    explanation: Optional[str] = None


class QuestionPayload(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: Optional[str] = None
    seq: int
    title: str
    description: Optional[str] = None
    question_type: Optional[QuestionType] = None
    score: Optional[Decimal] = None
    correct_answer: Optional[str | Sequence[str]] = None
    media_url: Optional[str] = None
    options: List[QuestionOptionPayload] = []
    resolved_question_type: Optional[QuestionType] = None

    @field_validator('question_type', mode='before')
    @classmethod
    def _coerce_question_type(cls, value):  # type: ignore[override]
        if value is None or value == '':
            return None
        if isinstance(value, QuestionType):
            return value
        if isinstance(value, IntEnum):
            return QuestionType(value.value)
        try:
            numeric = int(value)
            return QuestionType(numeric)
        except Exception:
            parsed = QuestionDTO.md_parse_question_type(str(value))
            return QuestionType(parsed) if parsed is not None else None

    def with_inherited_type(self, inherited: Optional[QuestionType]):
        self.resolved_question_type = resolve_inheritance(self.question_type, inherited)
        return self