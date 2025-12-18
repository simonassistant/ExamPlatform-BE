from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from pandas.core.methods.to_dict import to_dict
from starlette import status

from app.data.dao.exam_dao import ExamDAO
from app.data.dao.schedule_dao import ScheduleDAO
from app.data.dao.schedule_session_dao import ScheduleSessionDAO
from app.data.dao.user_dao import UserDAO
from app.data.entity.entities import Users
from app.ui.common.user_ui import get_current_user_id
from app.util.util_jwt import jwt_token_encode

router = APIRouter()

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
