import asyncio
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import HTTPException, Depends, APIRouter, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.data.dao.behavior_dao import BehaviorDAO
from app.data.dao.exam_answer_dao import ExamAnswerDAO
from app.data.dao.exam_dao import ExamDAO, EXAM_STATUS_NOT_STARTED, EXAM_STATUS_IN_PREPARATION, EXAM_STATUS_CLOSED, \
    EXAM_STATUS_IN_EXAM
from app.data.dao.exam_section_dao import ExamSectionDAO
from app.data.dao.paper_dao import PaperDAO, QUESTION_TYPE_FILL_IN_THE_BLANK
from app.data.dao.paper_section_dao import PaperSectionDAO
from app.data.dao.question_dao import QuestionDAO
from app.data.dao.question_option import QuestionOptionDAO
from app.data.dao.schedule_section_dao import ScheduleSectionDAO
from app.data.dao.user_dao import UserDAO
from app.data.entity.entities import Users, ExamSection, ExamAnswer, Behavior
from app.ui.common.user_ui import get_current_user_id
from app.util.util import to_bool
from app.util.util_ali import get_ali_credentials
from app.util.util_jwt import jwt_token_encode

router = APIRouter()

@router.get("/hello", tags=["exam"])
async def hello(user: str="World"):
    return "Hello, " + user

@router.post("/login", response_model=dict, tags=["exam"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request):
    username:str = form_data.username
    if username == "":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please input student ID!")
    user:Users = UserDAO.get_by_email(username) if username.find("@")>=0 else UserDAO.get_by_enroll_number(username)
    if (not user) or user.is_deleted == True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User!")

    exam = ExamDAO.get_unclosed_for_examinee(str(user.id))
    if not exam:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No valid exam for you now!")
    if exam.status == EXAM_STATUS_NOT_STARTED:
        exam.status = EXAM_STATUS_IN_PREPARATION
        ExamDAO.update(exam)

    asyncio.create_task(behavior_record(user_id=user.id, behavior_type="login", request=request))
    return {
        "access_token": jwt_token_encode(str(user.id)),
        "token_type": "bearer",
        "user": user.to_dict(),
        "exam": exam.to_dict()
    }

@router.post("/credentials", tags=["exam"])
async def ali_credentials(current_user_id: Annotated[str, Depends(get_current_user_id)]):
    return get_ali_credentials()

@router.post("/exam", response_model=None, tags=["exam"])
async def get_exam(current_user_id: Annotated[str, Depends(get_current_user_id)], exam_id: Annotated[str, Form()]) -> dict:
    exam = ExamDAO().get(exam_id)
    if not exam or exam.is_deleted or exam.examinee_id!=current_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not exist!")
    if exam.status == EXAM_STATUS_CLOSED:
        return {
            "exam": exam,
        }
    paper = PaperDAO().get(exam.paper_id)
    paper_sections = PaperSectionDAO().list_by_paper(paper_id=exam.paper_id)

    section_seq = 1
    if exam.status == EXAM_STATUS_IN_EXAM:
        exam_section = ExamSectionDAO.get_last_section(exam_id)
        if exam_section is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam Section not exist!")
        section_seq = exam_section.seq
        if exam_section.status == EXAM_STATUS_IN_EXAM:
            paper_section = paper_sections[section_seq-1]
            plan_end = exam_section.actual_start + timedelta(minutes=paper_section.duration)
            now = datetime.now()
            if now >= plan_end:
                ExamSectionDAO.submit(exam_section.id, current_user_id, is_timeout=True)
                exam_section = ExamSectionDAO().get(exam_section.id)
        if exam_section.status == EXAM_STATUS_CLOSED:
            if section_seq < len(paper_sections):
                section_seq = exam_section.seq + 1
            else:
                ExamDAO.submit(exam_id, current_user_id)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Last section is timeout and exam is over!")
    return {
        "exam": exam,
        "paper": paper,
        "paper_sections": paper_sections,
        "section_seq": section_seq,
    }

@router.post("/exam_submit", response_model=None, tags=["exam"])
async def exam_submit(current_user_id: Annotated[str, Depends(get_current_user_id)],
                      exam_id: Annotated[str, Form()],
                      section_id: Annotated[str, Form()]):
    ExamDAO().submit(exam_id, current_user_id)
    ExamSectionDAO().submit(section_id, current_user_id)

@router.post("/section", response_model=None, tags=["exam"])
async def get_section(current_user_id: Annotated[str, Depends(get_current_user_id)], exam_id: Annotated[str, Form()],
                      section_seq: Annotated[int, Form()]):
    exam = ExamDAO().get(exam_id)
    if exam is None or exam.is_deleted or exam.examinee_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not exist!")
    if exam.status == EXAM_STATUS_CLOSED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam is over!")
    paper_section = PaperSectionDAO().get_by_paper_seq(exam.paper_id, section_seq)
    if paper_section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper Section not exist!")

    exam_section_dao = ExamSectionDAO()
    exam_section = exam_section_dao.get_by_exam_seq(exam_id=exam_id, seq=section_seq)
    if exam_section is None:
        exam_section = ExamSection(
            exam_id=exam_id,
            examinee_id=current_user_id,
            name=paper_section.name,
            paper_id=exam.paper_id,
            paper_section_id=paper_section.id,
            schedule_id=exam.schedule_id,
            schedule_session_id=exam.schedule_session_id,
            seq=section_seq,
            status=EXAM_STATUS_NOT_STARTED,
        )
        exam_section.id = exam_section_dao.add(exam_section)

    schedule_section = ScheduleSectionDAO().get_by_session_seq(schedule_session_id=exam.schedule_session_id, seq=section_seq)
    if schedule_section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule section not exist!")
    start_count_down = None
    now = datetime.now()
    if now > schedule_section.plan_start_late:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="The time to start this exam section is over!")
    if now <= schedule_section.plan_start_early:
        start_count_down = schedule_section.plan_start_early - now
    return {
        "exam": exam,
        "exam_section": exam_section,
        "paper_section": paper_section,
        "start_count_down": start_count_down,
    }

@router.post("/section_start", response_model=None, tags=["exam"])
async def start_section(current_user_id: Annotated[str, Depends(get_current_user_id)],
                        section_id: Annotated[str, Form()],
                        exam_id: Annotated[str, Form()]):
    print(f"user_id: {current_user_id}, exam_id: {exam_id}, section_id: {section_id}")
    exam = ExamDAO().get(instance_id=exam_id)
    if exam is None or exam.is_deleted or exam.examinee_id != current_user_id:
        print(f"Exam {exam_id} not exist for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exam not exist!")
    if exam.status == EXAM_STATUS_CLOSED:
        print(f"Exam {exam_id} is over for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam is over!")
    print(f"exam.status: {exam.status}")

    exam_section = ExamSectionDAO().get(instance_id=section_id)
    if exam_section is None or exam_section.is_deleted or exam_section.exam_id != exam_id:
        print(f"Exam section {section_id} not exist for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam section not exist!")
    if exam_section.status == EXAM_STATUS_CLOSED:
        print(f"Exam section {section_id} is over for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam section is over!")
    print(f"exam_section.status: {exam_section.status}")

    paper_section = PaperSectionDAO().get(exam_section.paper_section_id)
    if paper_section is None:
        print(f"Paper section {exam_section.paper_section_id} not exist for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper section not exist!")
    schedule_section = ScheduleSectionDAO().get_by_session_seq(exam.schedule_session_id, exam_section.seq)
    if schedule_section is None:
        print(f"Schedule section {exam.schedule_session_id} - {exam_section.seq} not exist for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule section not exist!")
    now = datetime.now()
    if now < schedule_section.plan_start_early:
        print(f"It's not time {schedule_section.plan_start_early} to start this exam section {schedule_section.id} for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="It's not time to start this exam section!")
    if now > schedule_section.plan_start_late:
        print(
            f"The time {schedule_section.plan_start_early} to start this exam section {schedule_section.id} is over for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="The time to start this exam section is over!")
    print(f"paper_section.id: {paper_section.id}")
    print(f"schedule_section.id: {schedule_section.id}")

    actual_start = exam_section.actual_start
    print(f"actual_start: {actual_start}")
    if exam_section.status != EXAM_STATUS_IN_EXAM:
        actual_start = ExamSectionDAO.start(section_id=section_id, updated_by=current_user_id)
        if actual_start:
            exam_section.status = EXAM_STATUS_IN_EXAM
            exam_section.actual_start = actual_start
        if exam_section.seq == 1 and exam.status != EXAM_STATUS_IN_EXAM:
            exam.status = EXAM_STATUS_IN_EXAM
            ExamDAO.update(exam)

    now2 = datetime.now()
    end_count_down = timedelta(minutes=paper_section.duration) - (now2 - actual_start)
    print(f"end_count_down: {end_count_down}")

    if end_count_down <= timedelta(0):
        ExamSectionDAO.submit(section_id=section_id, updated_by=current_user_id, is_timeout=True)
        exam_section = None
    return {
        "end_count_down": end_count_down,
        "exam": exam,
        "exam_section": exam_section,
    }

@router.post("/question", response_model=None, tags=["exam"])
async def get_question(current_user_id: Annotated[str, Depends(get_current_user_id)],
                       section_id: Annotated[str, Form()],
                       seq: Annotated[int, Form()]=1):
    exam_section = ExamSectionDAO().get(section_id)
    if exam_section.examinee_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam Section not exist!")
    question = QuestionDAO.get_by_paper_section_seq(exam_section.paper_id, exam_section.paper_section_id, seq)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question is not found!")
    exam_answer = ExamAnswerDAO.get_by_examinee_question(examinee_id=current_user_id, question_id=question.id)
    options = QuestionOptionDAO.list_by_question_4_exam(exam_section.paper_id, question.id)
    if question.question_type == QUESTION_TYPE_FILL_IN_THE_BLANK:
        [setattr(option, 'content', None) for option in options]
    else:
        [setattr(option, 'is_correct', None) for option in options]
        [setattr(option, 'correct_seq', None) for option in options]

    return {
        "exam_answer": exam_answer,
        "question": question,
        "question_options": options,
    }

@router.post("/questions_in_section", response_model=None, tags=["exam"])
async def list_questions_in_section(current_user_id: Annotated[str, Depends(get_current_user_id)],
                       exam_id: Annotated[str, Form()],
                       section_id: Annotated[str, Form()]):
    exam = ExamDAO().get(exam_id)
    if exam.examinee_id != current_user_id:
        print(f"Exam not exist for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not exist!")
    if exam.status != EXAM_STATUS_IN_EXAM:
        print(f"Not in Exam for user {current_user_id}!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not in Exam!")

    questions = QuestionDAO.list_by_section(section_id)
    question_ids = [question.id for question in questions if question.question_type!=QUESTION_TYPE_FILL_IN_THE_BLANK]
    options = QuestionOptionDAO.list_by_question_group(question_ids)
    [setattr(option, 'is_correct', None) for option in options]
    [setattr(option, 'correct_seq', None) for option in options]
    return {
        "questions": questions,
        "question_options": options,
    }

@router.post("/mark", response_model=None, tags=["exam"])
async def mark(current_user_id: Annotated[str, Depends(get_current_user_id)],
                question_id: Annotated[str, Form()],
                exam_answer_id: Annotated[str, Form()],
                exam_section_id: Annotated[str, Form()],
                exam_id: Annotated[str, Form()],
                marked: Annotated[str, Form()]):
    if exam_answer_id is None or exam_answer_id == '':
        question = QuestionDAO().get(question_id)
        exam_answer_id = ExamAnswerDAO.add(
            ExamAnswer(
                exam_id=exam_id,
                exam_section_id=exam_section_id,
                examinee_id=current_user_id,
                question_id=question_id,
                seq = question.seq,
            )
        )
    ExamAnswerDAO.mark(current_user_id, exam_answer_id, to_bool(marked))

@router.post("/answer", response_model=None, tags=["exam"])
async def save_answer(current_user_id: Annotated[str, Depends(get_current_user_id)],
                        answer: Annotated[str, Form()],
                        exam_answer_id: Annotated[str, Form()],
                        exam_id: Annotated[str, Form()],
                        exam_section_id: Annotated[str, Form()],
                        question_id: Annotated[str, Form()],
                        question_seq: Annotated[int, Form()]):
    if exam_answer_id is None or exam_answer_id == "":
        exam_answer = ExamAnswer(
            answer=answer,
            exam_id=exam_id,
            exam_section_id=exam_section_id,
            examinee_id=current_user_id,
            question_id=question_id,
            seq=question_seq,
        )
        exam_answer_id = ExamAnswerDAO.add(exam_answer)
    else:
        ExamAnswerDAO.submit(user_id=current_user_id, instance_id=exam_answer_id, answer=answer)
    return {
        "exam_answer": ExamAnswerDAO().get(instance_id=exam_answer_id),
    }

@router.post("/section_submit", response_model=None, tags=["exam"])
async def section_submit(current_user_id: Annotated[str, Depends(get_current_user_id)],
                         exam_id: Annotated[str, Form()],
                         section_id: Annotated[str, Form()],
                         last_section: Annotated[bool, Form()]):
    exam_dao = ExamDAO()
    exam = exam_dao.get(exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not exist!")
    section_dao = ExamSectionDAO()
    section_dao.submit(section_id, current_user_id)
    if last_section:
        exam_dao.submit(exam_id, current_user_id)

@router.post("/behavior", response_model=None, tags=["exam"])
async def behavior(current_user_id: Annotated[str, Depends(get_current_user_id)],
                behavior_type: Annotated[str, Form()],
                request: Request):
    asyncio.create_task(behavior_record(user_id=current_user_id, behavior_type=behavior_type, request=request))

async def behavior_record(user_id: str, behavior_type: str, request: Request):
    forwarded = request.headers.getlist("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded[0].split(",")[0]  # 处理多层代理情况
    else:
        client_ip = request.client.host
    BehaviorDAO.add(
        Behavior(
            user_id=user_id,
            behavior_type=behavior_type,
            ip=client_ip,
        )
    )
