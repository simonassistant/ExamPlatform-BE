"""Schedule API router for proctor schedule and session management."""

from datetime import datetime
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, Form, HTTPException, Body
from starlette import status

from app.data.service.schedule_service import ScheduleService, SessionService
from app.ui.common.user_ui import get_current_user_id

router = APIRouter()


# Schedule endpoints

@router.get("/list", response_model=None, tags=["schedule"])
async def list_schedules(current_user_id: Annotated[str, Depends(get_current_user_id)]):
    """List all schedules for the current proctor."""
    return ScheduleService.list_schedules(current_user_id)


@router.get("/{schedule_id}", response_model=None, tags=["schedule"])
async def get_schedule(
    schedule_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """Get a schedule with all sessions and sections."""
    schedule = ScheduleService.get_schedule_full(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )
    return schedule


@router.post("", response_model=None, tags=["schedule"])
async def create_schedule(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    title: str = Form(...),
):
    """Create a new schedule."""
    schedule_id = ScheduleService.create_schedule(
        title=title,
        created_by=current_user_id,
    )
    return {"id": schedule_id}


@router.put("/{schedule_id}", response_model=None, tags=["schedule"])
async def update_schedule(
    schedule_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    title: Optional[str] = Form(None),
):
    """Update schedule metadata."""
    success = ScheduleService.update_schedule(
        schedule_id=schedule_id,
        title=title,
        updated_by=current_user_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )
    return {"success": True}


@router.delete("/{schedule_id}", response_model=None, tags=["schedule"])
async def delete_schedule(
    schedule_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """Soft-delete a schedule and all its contents."""
    success = ScheduleService.delete_schedule(schedule_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )
    return {"success": True}


# Session endpoints

@router.post("/session", response_model=None, tags=["session"])
async def create_session(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    schedule_id: str = Form(...),
    title: str = Form(...),
    paper_id: str = Form(...),
    plan_start: Optional[str] = Form(None),
    plan_end: Optional[str] = Form(None),
    place: Optional[str] = Form(None),
    proctor_email: Optional[str] = Form(None),
    is_ready: bool = Form(False),
):
    """Create a new session within a schedule."""
    session_id = SessionService.create_session(
        schedule_id=schedule_id,
        title=title,
        paper_id=paper_id,
        plan_start=datetime.fromisoformat(plan_start) if plan_start else None,
        plan_end=datetime.fromisoformat(plan_end) if plan_end else None,
        place=place,
        proctor_email=proctor_email,
        proctor_id=current_user_id if not proctor_email else None,
        is_ready=is_ready,
        created_by=current_user_id,
    )
    return {"id": session_id}


@router.put("/session/{session_id}", response_model=None, tags=["session"])
async def update_session(
    session_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    title: Optional[str] = Form(None),
    paper_id: Optional[str] = Form(None),
    plan_start: Optional[str] = Form(None),
    plan_end: Optional[str] = Form(None),
    place: Optional[str] = Form(None),
    proctor_email: Optional[str] = Form(None),
    is_ready: Optional[bool] = Form(None),
):
    """Update session details."""
    success = SessionService.update_session(
        session_id=session_id,
        title=title,
        paper_id=paper_id,
        plan_start=datetime.fromisoformat(plan_start) if plan_start else None,
        plan_end=datetime.fromisoformat(plan_end) if plan_end else None,
        place=place,
        proctor_email=proctor_email,
        is_ready=is_ready,
        updated_by=current_user_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return {"success": True}


@router.delete("/session/{session_id}", response_model=None, tags=["session"])
async def delete_session(
    session_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """Soft-delete a session and all its contents."""
    success = SessionService.delete_session(session_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return {"success": True}


@router.post("/session/{session_id}/students", response_model=None, tags=["session"])
async def assign_students(
    session_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    emails: List[str] = Body(...),
):
    """Assign students to a session by email list."""
    result = SessionService.assign_students(
        session_id=session_id,
        student_emails=emails,
        created_by=current_user_id,
    )
    return result


@router.delete("/session/{session_id}/students/{email}", response_model=None, tags=["session"])
async def remove_student(
    session_id: str,
    email: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """Remove a student from a session."""
    success = SessionService.remove_student(session_id, email, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found in session",
        )
    return {"success": True}


@router.post("/session/{session_id}/section", response_model=None, tags=["session"])
async def add_section(
    session_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    seq: int = Form(...),
    plan_start_early: Optional[str] = Form(None),
    plan_start_late: Optional[str] = Form(None),
):
    """Add a section timing to a session."""
    section_id = SessionService.add_section(
        session_id=session_id,
        seq=seq,
        plan_start_early=datetime.fromisoformat(plan_start_early) if plan_start_early else None,
        plan_start_late=datetime.fromisoformat(plan_start_late) if plan_start_late else None,
        created_by=current_user_id,
    )
    return {"id": section_id}
