from decimal import Decimal
from typing import List

from app.data.dto.question_dto import QuestionDTO
from app.data.entity.entities import QuestionGroup


class QuestionGroupDTO:
    def __init__(self, **kwargs):
        self.question_group_id = None
        self.seq = 0
        self.code = None
        self.title = None
        self.content = None
        self.question_type = None
        self.unit_score: Decimal = Decimal('0')
        self.full_score: Decimal = Decimal('0')
        self.section_id = None
        self.paper_id = None
        self.questions:List[QuestionDTO] = []

    def md_parse_meta(self, text: str):
        lines = text.split('\n')
        for line in lines:
            data = line.split(':')
            if len(data) == 2:
                key = data[0].strip().lower()
                value = data[1].strip()
                if key == 'question type':
                    self.question_type = QuestionDTO.md_parse_question_type(value)
                elif key == 'unit score':
                    self.unit_score = Decimal(value)
                elif key == 'full score':
                    self.full_score = Decimal(value)

    def to_entity(self) -> QuestionGroup:
        return QuestionGroup(
            id = self.question_group_id,
            seq = self.seq,
            code = self.code,
            title = self.title,
            content = self.content,
            question_type = self.question_type,
            unit_score = self.unit_score,
            full_score = self.full_score,
            section_id = self.section_id,
            paper_id = self.paper_id
        )