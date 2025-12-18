from typing import List

from markdown_it import MarkdownIt

from app.data.dto.schedule_section_dto import ScheduleSectionDTO
from app.data.dto.schedule_session_dto import ScheduleSessionDTO
from app.data.entity.entities import Schedule


class ScheduleDTO:
    def __init__(self, **kwargs):
        self.schedule_id = None
        self.title = None
        self.sessions:List[ScheduleSessionDTO] = []

    @staticmethod
    def md_parse(filename: str) -> "ScheduleDTO":
        md = MarkdownIt()
        with open(filename, 'r', encoding='utf-8') as f:
            md_content = f.read()
        tokens = md.parse(md_content)
        token_type: str = ''
        idx = 0
        schedule_dto:ScheduleDTO = ScheduleDTO()
        is_student = False
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
            elif token.type == 'heading_close' or token_type == 'list_item_close':
                token_type = ''
            elif token.type == 'list_item_open':
                token_type = 'li'
            elif token.type == 'inline':
                text = token.content.strip()
                if token_type == 'h1':
                    schedule_dto.title = text
                elif token_type == 'h2':
                    schedule_session_dto = ScheduleSessionDTO()
                    schedule_session_dto.title = text
                    schedule_session_dto.schedule_id = schedule_dto.schedule_id
                    schedule_session_dto.schedule_session_id = schedule_dto.schedule_id + '_' + text.split(' ')[1].lower()
                    schedule_dto.sessions.append(schedule_session_dto)
                elif token_type == 'h3':
                    text = text.lower()
                    is_student = text.startswith('student')
                    if not is_student:
                        schedule_section_dto = ScheduleSectionDTO()
                        session = schedule_dto.sessions[-1]
                        schedule_section_dto.schedule_session_id = session.schedule_session_id
                        schedule_section_dto.schedule_section_id = session.schedule_session_id + '_' + text.split(' ')[1]
                        schedule_section_dto.seq = len(session.sections) + 1
                        session.sections.append(schedule_section_dto)
                elif token_type == 'li':
                    if idx == 1:
                        schedule_dto.md_parse_meta(text)
                    elif idx == 2:
                        schedule_dto.sessions[-1].md_parse_meta(text)
                    elif idx == 3:
                        schedule_session_dto = schedule_dto.sessions[-1]
                        if is_student:
                            schedule_session_dto.student_emails.append(text)
                        else:
                            schedule_session_dto.sections[-1].md_parse_meta(text)
            #print(token)
        return schedule_dto

    def md_parse_meta(self, content: str):
        lines = content.split('\n')
        for line in lines:
            data = line.split(':')
            if len(data) == 2:
                key = data[0].strip().lower()
                value = data[1].strip()
                if key == 'id':
                    self.schedule_id = value

    def to_entity(self) -> Schedule:
        return Schedule(
            id = self.schedule_id,
            title = self.title
        )