import os
import sys

from app.data.dao.exam_dao import ExamDAO
from app.data.dao.schedule_dao import ScheduleDAO
from app.data.dao.schedule_section_dao import ScheduleSectionDAO
from app.data.dao.schedule_session_dao import ScheduleSessionDAO
from app.data.dto.schedule_dto import ScheduleDTO

file_name: str = 'schedule_sample.md'

def import_schedule():
    schedule_dto = ScheduleDTO.md_parse(file_name)
    schedule = schedule_dto.to_entity()
    ScheduleDAO().add_or_update(schedule)
    print(f'Save schedule to Database: {schedule_dto.title}')

    for schedule_session_dto in schedule_dto.sessions:
        session = schedule_session_dto.to_entity()
        schedule_session_dto.schedule_session_id = ScheduleSessionDAO().add_or_update(session)
        print(f'- Save schedule session to Database: {schedule_session_dto.title}')
        for schedule_section in schedule_session_dto.sections:
            section = schedule_section.to_entity()
            ScheduleSectionDAO().add_or_update(section)
            print(f'- Save schedule section to Database: {schedule_section.schedule_section_id}')
        for email in schedule_session_dto.student_emails:
            exam = schedule_session_dto.to_exam_entity(email)
            exam_id = ExamDAO().add_or_update(exam)
            print(f'- Create exam for {email}: {exam_id}')

def main():
    import_schedule()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        print(f"[{os.getenv("ENV_STATE")} env] importing schedule from {file_name}")
    main()