from typing import List

from app.data.dao.exam_dao import EXAM_STATUS_NOT_STARTED
from app.data.dao.user_dao import UserDAO
from app.data.dto.schedule_section_dto import ScheduleSectionDTO
from app.data.entity.entities import ScheduleSession, Users, Exam
from app.util.util import to_datetime


class ScheduleSessionDTO:
    def __init__(self, **kwargs):
        self.schedule_session_id = None
        self.title = None
        self.plan_start = None
        self.plan_end = None
        self.place = None
        self.is_ready = None
        self.proctor_email = None
        self.proctor_id = None
        self.schedule_id = None
        self.paper_id = None
        self.student_emails: List[str] = []
        self.sections: List[ScheduleSectionDTO] = []

    def md_parse_meta(self, content: str):
        index = content.find(':')
        if index == -1:
            return
        key = content[:index].strip().lower()
        value = content[index+1:].strip()
        if key == 'id':
            self.schedule_session_id = value
        elif key == 'plan start':
            self.plan_start = to_datetime(value)
        elif key == 'plan end':
            self.plan_end = to_datetime(value)
        elif key == 'place':
            self.place = value
        elif key == 'is ready':
            self.is_ready = bool(value)
        elif key == 'invigilator email':
            self.proctor_email = value
            self.proctor_id = UserDAO().get_by_email(value).id
        elif key == 'paper id':
            self.paper_id = value

    def to_entity(self) -> ScheduleSession:
        return ScheduleSession(
            id = self.schedule_session_id,
            title = self.title,
            plan_start = self.plan_start,
            plan_end = self.plan_end,
            place = self.place,
            is_ready = self.is_ready,
            proctor_email = self.proctor_email,
            proctor_id = self.proctor_id,
            schedule_id = self.schedule_id,
            paper_id = self.paper_id,
        )

    def to_exam_entity(self, email: str) -> Exam | None:
        examinee: Users = UserDAO().get_by_email(email)
        if examinee is None:
            return None
        return Exam(
            status=EXAM_STATUS_NOT_STARTED,
            examinee_enroll_number=examinee.enroll_number,
            examinee_email=email,
            examinee_id=examinee.id,
            schedule_session_id=self.schedule_session_id,
            schedule_id=self.schedule_id,
            paper_id=self.paper_id
        )
