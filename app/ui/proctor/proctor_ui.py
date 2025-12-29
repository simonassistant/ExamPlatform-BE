from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.data.dao.exam_dao import ExamDAO
from app.data.dao.schedule_dao import ScheduleDAO
from app.data.dao.schedule_session_dao import ScheduleSessionDAO
from app.data.dao.user_dao import UserDAO
from app.data.dto.schedule_assignment_dto import (
    ScheduleAssignmentCreatePayload,
    ScheduleAssignmentRead,
    ScheduleAssignmentUpdatePayload,
)
from app.data.entity.entities import Users
from app.ui.common.user_ui import get_current_user_id
from app.ui.proctor.assignment_service import (
    AssignmentConflictError,
    AssignmentLockedError,
    AssignmentService,
)
from app.util.util import respond_fail, respond_suc
from app.util.util_jwt import jwt_token_encode

router = APIRouter()
assignment_api = APIRouter(prefix="/api")
assignment_service = AssignmentService()

@router.get("/hello", tags=["user"])
async def hello(user: str="World"):
    return "Hello, " + user

@router.post("/login", response_model=dict, tags=["user"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    username:str = form_data.username
    if username == "":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please input student ID!")
    user:Users = UserDAO.get_by_email(username)
    if (not user) or user.is_deleted or (user.pwd != form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User!")

    return {
        "access_token": jwt_token_encode(str(user.id)),
        "token_type": "bearer",
        "user": user.to_dict(),
    }

@router.get("/schedules", response_model=None, tags=["exam"])
async def list_schedule(current_user_id: Annotated[str, Depends(get_current_user_id)]):
    return ScheduleDAO.list_for_proctor(current_user_id)

@router.get("/session", response_model=None, tags=["exam"])
async def get_session(current_user_id: Annotated[str, Depends(get_current_user_id)], session_id: str):
    session = ScheduleSessionDAO().get(session_id)
    if session.proctor_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session!")
    exams = ExamDAO.list_in_schedule_session_for_proctor(session_id)
    return {
        "session": session,
        "exams": [exam._asdict() for exam in exams],
    }

@router.get("/sessions", response_model=None, tags=["exam"])
async def list_session(current_user_id: Annotated[str, Depends(get_current_user_id)], schedule_id: str):
    return ScheduleSessionDAO.list_for_schedule_proctor(schedule_id=schedule_id, proctor_id=current_user_id)


@assignment_api.get("/sessions/{session_id}/assignments", tags=["assignments"])
async def list_assignments(session_id: str):
    items = [
        ScheduleAssignmentRead(
            id=a.id,
            paper_id=a.paper_id,
            schedule_session_id=a.schedule_session_id,
            start_time=a.start_time,
            end_time=a.end_time,
            examinee_group_filter=a.examinee_group_filter,
        ).model_dump()
        for a in assignment_service.list(session_id)
    ]
    return respond_suc({"items": items})


@assignment_api.post("/sessions/{session_id}/assignments", tags=["assignments"])
async def create_assignment(session_id: str, payload: ScheduleAssignmentCreatePayload):
    try:
        assignment = assignment_service.create(
            session_id=session_id,
            paper_id=payload.paper_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
            examinee_group_filter=payload.examinee_group_filter,
        )
    except AssignmentConflictError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return respond_suc({
        "assignment": ScheduleAssignmentRead(
            id=assignment.id,
            paper_id=assignment.paper_id,
            schedule_session_id=assignment.schedule_session_id,
            start_time=assignment.start_time,
            end_time=assignment.end_time,
            examinee_group_filter=assignment.examinee_group_filter,
        ).model_dump(),
    })


@assignment_api.put("/sessions/{session_id}/assignments/{assignment_id}", tags=["assignments"])
async def update_assignment(session_id: str, assignment_id: str, payload: ScheduleAssignmentUpdatePayload):
    try:
        assignment = assignment_service.update(
            session_id=session_id,
            assignment_id=assignment_id,
            paper_id=payload.paper_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
            examinee_group_filter=payload.examinee_group_filter,
        )
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    except AssignmentLockedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except AssignmentConflictError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return respond_suc({
        "assignment": ScheduleAssignmentRead(
            id=assignment.id,
            paper_id=assignment.paper_id,
            schedule_session_id=assignment.schedule_session_id,
            start_time=assignment.start_time,
            end_time=assignment.end_time,
            examinee_group_filter=assignment.examinee_group_filter,
        ).model_dump(),
    })


@assignment_api.delete("/sessions/{session_id}/assignments/{assignment_id}", tags=["assignments"])
async def delete_assignment(session_id: str, assignment_id: str):
    assignment = assignment_service.get(session_id, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    try:
        assignment_service.delete(session_id, assignment_id)
    except AssignmentLockedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return respond_suc({"status": "deleted"})
