import re
from decimal import Decimal
from typing import List

from markdown_it import MarkdownIt

from app.data.dto.paper_section_dto import PaperSectionDTO
from app.data.dto.question_dto import QuestionDTO
from app.data.dto.question_group_dto import QuestionGroupDTO
from app.data.dto.question_option_dto import QuestionOptionDTO
from app.data.entity.entities import Paper

list_item_dict = {
    'ordered_list_open': '<ol>',
    'ordered_list_close': '</ol>',
    'bullet_list_open': '<ul>',
    'bullet_list_close': '</ul>',
    'list_item_open': '<li>',
    'list_item_close': '</li>',
}

class PaperDTO:
    def __init__(self, **kwargs):
        self.md = MarkdownIt()
        self.paper_id = None
        self.title = None
        self.note = None
        self.duration = 0
        self.question_type = None
        self.unit_score:Decimal = Decimal('0')
        self.full_score:Decimal = Decimal('0')
        self.pass_score:Decimal = Decimal('0')
        self.sections:List[PaperSectionDTO] = []
        self.question_groups:List[QuestionGroupDTO] = []
        self.questions:List[QuestionDTO] = []

    def _append_paragraph(self, src: str | None, content: str) -> str:
        return (src or '') + self.md.render(content)

    @staticmethod
    def _append_content(paper_dto: "PaperDTO", idx: int, content: str):
        if idx == 1:
            paper_dto.md_parse_append_paper_note(content)
        elif idx == 2:
            paper_dto.md_parse_append_section_note(content)
        elif idx == 3:
            paper_dto.md_parse_append_question_group_content(content)
        elif idx == 4:
            paper_dto.md_parse_append_question_content(content)
        elif idx == 5:
            paper_dto.md_parse_append_question_option(content)

    def md_parse(self, filename: str) -> "PaperDTO":
        with open(filename, 'r', encoding='utf-8') as f:
            md_content = f.read()
        tokens = self.md.parse(md_content)
        token_type: str = ''
        idx = 0
        paper_dto = PaperDTO()
        for token in tokens:
            if token.type == 'heading_open':
                if token.markup == '-':
                    token_type = 'meta'
                elif token.markup == '#':
                    token_type = 'h1'
                    idx = 1
                elif token.markup == '##':
                    token_type = 'h2'
                    idx = 2
                elif token.markup == '###':
                    token_type = 'h3'
                    idx = 3
                elif token.markup == '####':
                    token_type = 'h4'
                    idx = 4
                elif token.markup == '#####':
                    token_type = 'h5'
                    idx = 5
            elif token.type == 'heading_close' or token.type == 'paragraph_close':
                token_type = ''
            elif token.type in ['ordered_list_open', 'ordered_list_close', 'bullet_list_open', 'bullet_list_close', 'list_item_open', 'list_item_close']:
                if idx < 5:
                    self._append_content(paper_dto, idx, list_item_dict[token.type])
            elif token.type == 'paragraph_open':
                token_type = 'p'
            elif token.type == 'inline':
                if token_type == 'h1':
                    paper_dto.md_parse_title(token.content)
                elif token_type == 'h2':
                    paper_dto.md_parse_section_name(token.content)
                elif token_type == 'h3':
                    paper_dto.md_parse_question_group_title(token.content)
                elif token_type == 'h4':
                    paper_dto.md_parse_question_in_group(token.content)
                elif token_type == 'p':
                    self._append_content(paper_dto, idx, token.content)
            elif token.type == 'html_block':
                self._append_content(paper_dto, idx, token.content)
            elif token.type == 'fence':
                if idx == 1:
                    paper_dto.md_parse_meta(token.content)
                elif idx == 2:
                    paper_dto.sections[-1].md_parse_meta(token.content)
                elif idx == 3:
                    paper_dto.sections[-1].question_groups[-1].md_parse_meta(token.content)
                elif idx == 4:
                    paper_dto.sections[-1].question_groups[-1].questions[-1].md_parse_meta(token.content)
                elif idx == 5:
                    paper_dto.sections[-1].question_groups[-1].questions[-1].question_options[-1].md_parse_meta(token.content)
        return paper_dto

    def md_parse_meta(self, text: str):
        lines = text.split('\n')
        for line in lines:
            data = line.split(':')
            if len(data) == 2:
                key = data[0].strip().lower()
                value = data[1].strip()
                if key == 'id':
                    self.paper_id = value
                elif key == 'question type':
                    self.question_type = QuestionDTO.md_parse_question_type(value)
                elif key == 'duration':
                    self.duration = int(value)
                elif key == 'unit score':
                    self.unit_score = Decimal(value)
                elif key == 'full score':
                    self.full_score = Decimal(value)
                elif key == 'pass score':
                    self.pass_score = Decimal(value)

    def md_parse_title(self, text: str):
        self.title = text.strip()

    def md_parse_section_name(self, text: str):
        paper_section_dto = PaperSectionDTO()
        paper_section_dto.seq = len(self.sections) + 1
        paper_section_dto.name = text.strip()
        paper_section_dto.paper_id = self.paper_id
        self.sections.append(paper_section_dto)

    def md_parse_question_group_title(self, text: str):
        paper_section_dto:PaperSectionDTO = self.sections[-1]
        question_group_dto:QuestionGroupDTO = QuestionGroupDTO()
        question_group_dto.seq = len(paper_section_dto.question_groups) + 1
        question_group_dto.title = text.strip()
        question_group_dto.paper_id = self.paper_id
        question_group_dto.section_id = paper_section_dto.section_id
        paper_section_dto.question_groups.append(question_group_dto)
        self.question_groups.append(question_group_dto)

    def md_parse_question_in_group(self, text: str):
        paper_section_dto:PaperSectionDTO = self.sections[-1]
        question_group_dto:QuestionGroupDTO = paper_section_dto.question_groups[-1]
        question_dto = QuestionDTO()
        question_dto.question_group_id = question_group_dto.question_group_id
        question_dto.paper_id = self.paper_id
        question_dto.section_id = paper_section_dto.section_id
        question_group_dto.questions.append(question_dto)
        paper_section_dto.questions.append(question_dto)
        self.questions.append(question_dto)

        pattern = r"\d+"
        match = re.search(pattern, text)
        if match:
            question_dto.seq = int(match.group())
        else:
            question_dto.seq = 0

    def md_parse_append_paper_note(self, text: str):
        self.note = self.md.render(self._append_paragraph(self.note, text))

    def md_parse_append_section_note(self, text: str):
        section_dto = self.sections[-1]
        section_dto.note = self.md.render(self._append_paragraph(section_dto.note, text))

    def md_parse_append_question_group_content(self, text: str):
        section_dto = self.sections[-1]
        question_group_dto = section_dto.question_groups[-1]
        question_group_dto.content = self._append_paragraph(question_group_dto.content, text)

    def md_parse_append_question_content(self, text: str):
        section_dto = self.sections[-1]
        question_dto = section_dto.questions[-1]
        question_dto.content = self.md.render(self._append_paragraph(question_dto.content, text))

    def md_parse_append_question_option(self, text: str):
        text = text.strip()
        if len(text) == 0:
            return
        section_dto = self.sections[-1]
        question_dto = section_dto.questions[-1]
        answer = text.find('[x] ') == 0
        question_option_dto = QuestionOptionDTO(
            code = str(len(question_dto.question_options) + 1),
            content = text.replace('[x] ' if answer else '[ ] ', ''),
            is_correct = answer,
            question_id = question_dto.question_id,
            paper_id = question_dto.paper_id
        )
        question_dto.question_options.append(question_option_dto)

    def to_entity(self) -> Paper:
        return Paper(
            id = self.paper_id,
            title = self.title,
            note = self.note,
            question_type = self.question_type,
            unit_score = self.unit_score,
            pass_score = self.pass_score,
            full_score = self.full_score,
            section_num = len(self.sections),
            question_num = len(self.questions),
            duration=self.duration,
        )