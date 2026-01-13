"""Schedule service for CRUD operations on exam schedules and sessions."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select

from app.data.dao.exam_dao import ExamDAO, EXAM_STATUS_NOT_STARTED
from app.data.dao.schedule_dao import ScheduleDAO
from app.data.dao.schedule_section_dao import ScheduleSectionDAO
from app.data.dao.schedule_session_dao import ScheduleSessionDAO
from app.data.dao.user_dao import UserDAO
from app.data.database import db_scalars
from app.data.entity.entities import (
    Exam,
    Schedule,
    ScheduleSection,
    ScheduleSession,
    Users,
)


class ScheduleService:
    """Service class for schedule management operations."""

    @staticmethod
    def create_schedule(title: str, created_by: Optional[str] = None) -> str:
        """Create a new schedule and return its ID."""
        schedule = Schedule(
            title=title,
            created_by=created_by,
        )
        return ScheduleDAO().add(schedule)

    @staticmethod
    def get_schedule(schedule_id: str) -> Optional[Schedule]:
        """Get a schedule by ID."""
        return ScheduleDAO().get(schedule_id)

    @staticmethod
    def get_schedule_full(schedule_id: str) -> dict:
        """Get a schedule with all sessions and sections."""
        schedule = ScheduleDAO().get(schedule_id)
        if schedule is None:
            return {}

        # Get all sessions for this schedule
        stmt = (
            select(ScheduleSession)
            .where(
                ScheduleSession.schedule_id == schedule_id,
                ScheduleSession.is_deleted.is_(None),
            )
            .order_by(ScheduleSession.plan_start)
        )
        sessions = db_scalars(stmt)

        sessions_data = []
        for session in sessions:
            # Get sections for this session
            stmt = (
                select(ScheduleSection)
                .where(
                    ScheduleSection.schedule_session_id == session.id,
                    ScheduleSection.is_deleted.is_(None),
                )
                .order_by(ScheduleSection.seq)
            )
            sections = db_scalars(stmt)

            # Get exams (students) for this session
            stmt = (
                select(Exam)
                .where(
                    Exam.schedule_session_id == session.id,
                    Exam.is_deleted.is_(None),
                )
            )
            exams = db_scalars(stmt)

            sections_data = [
                {
                    "id": s.id,
                    "seq": s.seq,
                    "plan_start_early": s.plan_start_early.isoformat() if s.plan_start_early else None,
                    "plan_start_late": s.plan_start_late.isoformat() if s.plan_start_late else None,
                }
                for s in sections
            ]

            students_data = [
                {
                    "exam_id": e.id,
                    "email": e.examinee_email,
                    "enroll_number": e.examinee_enroll_number,
                    "status": e.status,
                }
                for e in exams
            ]

            sessions_data.append({
                "id": session.id,
                "title": session.title,
                "plan_start": session.plan_start.isoformat() if session.plan_start else None,
                "plan_end": session.plan_end.isoformat() if session.plan_end else None,
                "place": session.place,
                "is_ready": session.is_ready,
                "proctor_email": session.proctor_email,
                "proctor_id": session.proctor_id,
                "paper_id": session.paper_id,
                "sections": sections_data,
                "students": students_data,
            })

        return {
            "id": schedule.id,
            "title": schedule.title,
            "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
            "sessions": sessions_data,
        }

    @staticmethod
    def update_schedule(
        schedule_id: str,
        title: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> bool:
        """Update schedule metadata. Returns True if successful."""
        schedule = ScheduleDAO().get(schedule_id)
        if schedule is None:
            return False

        if title is not None:
            schedule.title = title
        schedule.updated_by = updated_by
        schedule.updated_at = datetime.now()

        ScheduleDAO.update(schedule)
        return True

    @staticmethod
    def delete_schedule(schedule_id: str, deleted_by: str) -> bool:
        """Soft-delete a schedule and all its contents."""
        schedule = ScheduleDAO().get(schedule_id)
        if schedule is None:
            return False

        # Soft-delete all sessions
        stmt = select(ScheduleSession).where(ScheduleSession.schedule_id == schedule_id)
        sessions = db_scalars(stmt)
        for session in sessions:
            ScheduleService.delete_session(session.id, deleted_by)

        # Soft-delete the schedule itself
        ScheduleDAO().delete(schedule_id, deleted_by)
        return True

    @staticmethod
    def list_schedules(proctor_id: Optional[str] = None) -> list:
        """List all schedules, optionally filtered by proctor."""
        if proctor_id:
            return ScheduleDAO.list_for_proctor(proctor_id)

        stmt = (
            select(Schedule)
            .where(Schedule.is_deleted.is_(None))
            .order_by(Schedule.created_at.desc())
        )
        schedules = db_scalars(stmt)
        return [
            {
                "id": s.id,
                "title": s.title,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in schedules
        ]


class SessionService:
    """Service class for session management operations."""

    @staticmethod
    def create_session(
        schedule_id: str,
        title: str,
        paper_id: str,
        plan_start: Optional[datetime] = None,
        plan_end: Optional[datetime] = None,
        place: Optional[str] = None,
        proctor_email: Optional[str] = None,
        proctor_id: Optional[str] = None,
        is_ready: bool = False,
        created_by: Optional[str] = None,
    ) -> str:
        """Create a new session and return its ID."""
        # If proctor_email is provided but not proctor_id, look up the user
        if proctor_email and not proctor_id:
            proctor = UserDAO.get_by_email(proctor_email)
            if proctor:
                proctor_id = proctor.id

        session = ScheduleSession(
            title=title,
            plan_start=plan_start,
            plan_end=plan_end,
            place=place,
            is_ready=is_ready,
            proctor_email=proctor_email,
            proctor_id=proctor_id,
            paper_id=paper_id,
            schedule_id=schedule_id,
            created_by=created_by,
        )
        return ScheduleSessionDAO().add(session)

    @staticmethod
    def update_session(
        session_id: str,
        title: Optional[str] = None,
        paper_id: Optional[str] = None,
        plan_start: Optional[datetime] = None,
        plan_end: Optional[datetime] = None,
        place: Optional[str] = None,
        proctor_email: Optional[str] = None,
        is_ready: Optional[bool] = None,
        updated_by: Optional[str] = None,
    ) -> bool:
        """Update session details. Returns True if successful."""
        session = ScheduleSessionDAO().get(session_id)
        if session is None:
            return False

        if title is not None:
            session.title = title
        if paper_id is not None:
            session.paper_id = paper_id
        if plan_start is not None:
            session.plan_start = plan_start
        if plan_end is not None:
            session.plan_end = plan_end
        if place is not None:
            session.place = place
        if proctor_email is not None:
            session.proctor_email = proctor_email
            proctor = UserDAO.get_by_email(proctor_email)
            if proctor:
                session.proctor_id = proctor.id
        if is_ready is not None:
            session.is_ready = is_ready

        session.updated_by = updated_by
        session.updated_at = datetime.now()

        ScheduleSessionDAO.update(session)
        return True

    @staticmethod
    def delete_session(session_id: str, deleted_by: str) -> bool:
        """Soft-delete a session and all its contents."""
        session = ScheduleSessionDAO().get(session_id)
        if session is None:
            return False

        # Soft-delete all sections
        stmt = select(ScheduleSection).where(ScheduleSection.schedule_session_id == session_id)
        sections = db_scalars(stmt)
        for section in sections:
            ScheduleSectionDAO().delete(section.id, deleted_by)

        # Soft-delete all exams
        stmt = select(Exam).where(Exam.schedule_session_id == session_id)
        exams = db_scalars(stmt)
        for exam in exams:
            ExamDAO().delete(exam.id, deleted_by)

        # Soft-delete the session
        ScheduleSessionDAO().delete(session_id, deleted_by)
        return True

    @staticmethod
    def assign_students(
        session_id: str,
        student_emails: List[str],
        created_by: Optional[str] = None,
    ) -> dict:
        """
        Assign students to a session by email.
        Returns dict with 'assigned' count and 'errors' list for invalid emails.
        """
        session = ScheduleSessionDAO().get(session_id)
        if session is None:
            return {"assigned": 0, "errors": ["Session not found"]}

        assigned = 0
        errors = []

        for email in student_emails:
            email = email.strip()
            if not email:
                continue

            user = UserDAO.get_by_email(email)
            if user is None:
                errors.append(f"User not found: {email}")
                continue

            # Check if exam already exists for this user in this session
            existing_exam = ExamDAO.get_by_session_examinee(session_id, email)
            if existing_exam:
                errors.append(f"Already assigned: {email}")
                continue

            # Create exam for this student
            exam = Exam(
                status=EXAM_STATUS_NOT_STARTED,
                examinee_enroll_number=user.enroll_number,
                examinee_email=email,
                examinee_id=user.id,
                schedule_session_id=session_id,
                schedule_id=session.schedule_id,
                paper_id=session.paper_id,
                created_by=created_by,
            )
            ExamDAO().add(exam)
            assigned += 1

        return {"assigned": assigned, "errors": errors}

    @staticmethod
    def remove_student(session_id: str, student_email: str, deleted_by: str) -> bool:
        """Remove a student from a session by soft-deleting their exam."""
        user = UserDAO.get_by_email(student_email)
        if user is None:
            return False

        exam = ExamDAO.get_by_session_examinee(session_id, user.id)
        if exam is None:
            return False

        ExamDAO().delete(exam.id, deleted_by)
        return True

    @staticmethod
    def add_section(
        session_id: str,
        seq: int,
        plan_start_early: Optional[datetime] = None,
        plan_start_late: Optional[datetime] = None,
        created_by: Optional[str] = None,
    ) -> str:
        """Add a section timing to a session."""
        section = ScheduleSection(
            seq=seq,
            plan_start_early=plan_start_early,
            plan_start_late=plan_start_late,
            schedule_session_id=session_id,
            created_by=created_by,
        )
        return ScheduleSectionDAO().add(section)
