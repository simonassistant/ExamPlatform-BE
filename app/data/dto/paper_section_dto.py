from decimal import Decimal
from typing import List

from app.data.dto.question_dto import QuestionDTO
from app.data.dto.question_group_dto import QuestionGroupDTO
from app.data.entity.entities import PaperSection


class PaperSectionDTO:
    def __init__(self, **kwargs):
        self.section_id = None
        self.seq = 0
        self.name = None
        self.duration = 0
        self.question_num = 0
        self.question_type = None
        self.unit_score:Decimal = Decimal('0')
        self.full_score:Decimal = Decimal('0')
        self.pass_score:Decimal = Decimal('0')
        self.note = None
        self.paper_id = None
        self.question_groups:List[QuestionGroupDTO] = []
        self.questions:List[QuestionDTO] = []

    def md_parse_meta(self, content: str):
        lines = content.split('\n')
        for line in lines:
            data = line.split(':')
            if len(data) == 2:
                key = data[0].strip().lower()
                value = data[1].strip()
                if key == 'question type':
                    self.question_type = QuestionDTO.md_parse_question_type(value)
                elif key == 'duration':
                    self.duration = int(value)
                elif key == 'unit score':
                    self.unit_score = Decimal(value)
                elif key == 'full score':
                    self.full_score = Decimal(value)
                elif key == 'pass score':
                    self.pass_score = Decimal(value)

    def to_entity(self) -> PaperSection:
        return PaperSection(
            id = self.section_id,
            seq = self.seq,
            name = self.name,
            note = self.note,
            question_type  = self.question_type,
            unit_score = self.unit_score,
            pass_score = self.pass_score,
            full_score = self.full_score,
            question_num = len(self.questions),
            duration=self.duration,
            paper_id = self.paper_id
        )