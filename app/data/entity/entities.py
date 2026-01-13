from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Numeric, PrimaryKeyConstraint, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column
import datetime
import decimal

from app.data.entity.base import Base


class Behavior(Base):
    __tablename__ = 'behavior'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='behavior_pkey'),
        {'comment': '用户行为记录'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    user_id: Mapped[Optional[str]] = mapped_column(String(26), comment='User ID')
    ip: Mapped[Optional[str]] = mapped_column(String(40), comment='IP')
    behavior_type: Mapped[Optional[str]] = mapped_column(String(64), comment='Behavior Type')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[str]] = mapped_column(String, comment='Is Deleted')


class Exam(Base):
    __tablename__ = 'exam'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='exam_pkey'),
        Index('idx_exam_examinee_status', 'examinee_id', 'status'),
        Index('idx_exam_paper', 'paper_id'),
        Index('idx_exam_schedule_session_examinee', 'schedule_session_id', 'examinee_id'),
        {'comment': 'Exam'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    token: Mapped[Optional[str]] = mapped_column(String(64), comment='Login Token')
    status: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Exam Status;0:No Access; 1:In Preparation; 2:In Exam; 3:Closed')
    current_seq: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Current Exam Section Sequence')
    current_section: Mapped[Optional[str]] = mapped_column(String(26), comment='Current Exam Section')
    actual_start: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Actual Start Datetime')
    actual_end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Actual End Datetime')
    is_timeout: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Exam Timeout')
    score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Exam Score')
    is_passed: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Exam Passed')
    examinee_enroll_number: Mapped[Optional[str]] = mapped_column(String(20), comment='examinee_enroll_number')
    examinee_email: Mapped[Optional[str]] = mapped_column(String(255), comment='Examinee Email')
    examinee_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Examinee ID')
    paper_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Paper ID')
    schedule_session_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Schedule Session ID')
    schedule_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Schedule ID')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')


class ExamAnswer(Base):
    __tablename__ = 'exam_answer'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='exam_answer_pkey'),
        {'comment': 'Exam Answer'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    seq: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Sequence')
    answer: Mapped[Optional[str]] = mapped_column(Text, comment='Answer')
    marked: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Marked for review')
    is_correct: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Is Answer Correct;0:Wrong; 1:Half Correct; 2:All Correct')
    score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Exam Answer Score')
    question_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Question ID')
    examinee_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Examinee ID')
    exam_section_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Exam Section ID')
    exam_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Exam ID')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')


class ExamSection(Base):
    __tablename__ = 'exam_section'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='exam_section_pkey'),
        Index('idx_exam_section_exam_seq', 'exam_id', 'seq'),
        Index('idx_exam_section_schedule_session_examinee_seq', 'schedule_session_id', 'examinee_id', 'seq'),
        {'comment': 'Exam Section'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    name: Mapped[Optional[str]] = mapped_column(String(20), comment='Name;same as the name of paper section')
    seq: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Sequence')
    status: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Exam Status;0:No Access; 1:In Preparation; 2:In Exam; 3:Closed')
    current_seq: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Current Exam Answer Sequence')
    actual_start: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Actual Start Datetime')
    actual_end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Actual End Datetime')
    is_timeout: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Exam Section Timeout')
    score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Exam Section Score')
    is_passed: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Exam Section Passed')
    examinee_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Examinee ID')
    exam_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Exam ID')
    paper_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Paper ID')
    paper_section_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Paper Section ID')
    schedule_session_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Schedule Session ID')
    schedule_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Schedule ID')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')


class Paper(Base):
    __tablename__ = 'paper'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='paper_pkey'),
        {'comment': 'Paper'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    title: Mapped[Optional[str]] = mapped_column(String(255), comment='Paper Title')
    note: Mapped[Optional[str]] = mapped_column(Text, comment='Paper Note')
    paper_type: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Paper Type;1.Reading; 2.Listening; 3.Writing; 4.Speaking')
    section_num: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Section Num')
    question_num: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Question Num')
    question_type: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Question Type;1.single choice; 2.true-false; 3.definite multiple choice; 4.indefinite multiple choice; 5.fill-in-the-blank; 6.writing; 7.listening; 8.speaking')
    unit_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Unit/Question Score')
    full_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Full Score')
    pass_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Pass Score')
    duration: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Duration in Minutes')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')


class PaperSection(Base):
    __tablename__ = 'paper_section'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='paper_section_pkey'),
        Index('idx_paper_section_paper_seq', 'paper_id', 'seq'),
        {'comment': 'Paper Section'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    seq: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Sequence')
    name: Mapped[Optional[str]] = mapped_column(String(50), comment='Name')
    content: Mapped[Optional[str]] = mapped_column(Text, comment='Section Content (passage text or audio HTML)')
    duration: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Duration in Minutes')
    question_num: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Question Num')
    question_type: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Question Type;1.single choice; 2.true-false; 3.definite multiple choice; 4.indefinite multiple choice; 5.fill-in-the-blank; 6.writing; 7.listening; 8.speaking')
    unit_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Unit/Question Score')
    full_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Full Score')
    pass_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Pass Score')
    note: Mapped[Optional[str]] = mapped_column(Text, comment='Note')
    paper_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Paper ID')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')


class Question(Base):
    __tablename__ = 'question'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='question_pkey'),
        {'comment': 'Question'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    seq: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Sequence')
    code: Mapped[Optional[str]] = mapped_column(String(20), comment='Code')
    content: Mapped[Optional[str]] = mapped_column(Text, comment='Content')
    question_type: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Question Type;1.single choice; 2.true-false; 3.definite multiple choice; 4.indefinite multiple choice; 5.fill-in-the-blank; 6.writing; 7.listening; 8.speaking')
    score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2), comment='Score')
    section_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Section ID')
    paper_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Paper ID')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')


class QuestionOption(Base):
    __tablename__ = 'question_option'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='question_option_pkey'),
        {'comment': 'Question Option'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    code: Mapped[Optional[str]] = mapped_column(String(1), comment='Code/Sequence')
    content: Mapped[Optional[str]] = mapped_column(Text, comment='Content')
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is This Option Correct')
    correct_seq: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Sequence in correct answers')
    question_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Question ID')
    paper_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Paper ID')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')


class Schedule(Base):
    __tablename__ = 'schedule'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='schedule_pkey'),
        Index('idx_schedule_id_updated', 'id', 'updated_at'),
        {'comment': 'Schedule'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    title: Mapped[Optional[str]] = mapped_column(String(255), comment='Schedule Title')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')


class ScheduleSection(Base):
    __tablename__ = 'schedule_section'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='schedule_section_pkey'),
        Index('idx_schedule_section_schedule_session_seq', 'schedule_session_id', 'seq'),
        {'comment': 'Schedule Section'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    seq: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Sequence')
    plan_start_early: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Plan Early Start Datetime')
    plan_start_late: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Plan Late Start Datetime')
    schedule_session_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Schedule Session ID')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[str]] = mapped_column(String, comment='Is Deleted')


class ScheduleSession(Base):
    __tablename__ = 'schedule_session'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='schedule_session_pkey'),
        Index('idx_schedule_session_paper_plan_start', 'paper_id', 'plan_start'),
        Index('idx_schedule_session_proctor_schedule_plan_start', 'proctor_id', 'schedule_id', 'plan_start'),
        {'comment': 'Schedule Session'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    title: Mapped[Optional[str]] = mapped_column(String(255), comment='Session Title')
    is_ready: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Ready')
    plan_start: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Plan Start Datetime')
    plan_end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Plan End Datetime')
    place: Mapped[Optional[str]] = mapped_column(String(255), comment='Examination Room')
    proctor_email: Mapped[Optional[str]] = mapped_column(String(255), comment='Proctor Email')
    proctor_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Proctor ID')
    paper_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Paper ID')
    schedule_id: Mapped[Optional[str]] = mapped_column(String(26), comment='Schedule ID')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        Index('idx_users_email', 'email', unique=True),
        Index('idx_users_enroll_number', 'enroll_number', unique=True),
        {'comment': 'User'}
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    username: Mapped[Optional[str]] = mapped_column(String(64), comment='Username')
    pwd: Mapped[Optional[str]] = mapped_column(String(255), comment='Password')
    email: Mapped[Optional[str]] = mapped_column(String(64), comment='Email')
    mobile: Mapped[Optional[str]] = mapped_column(String(64), comment='Mobile')
    surname: Mapped[Optional[str]] = mapped_column(String(64), comment='Surname')
    name: Mapped[Optional[str]] = mapped_column(String(64), comment='Name')
    gender: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Gender;True: man; False: women')
    enroll_number: Mapped[Optional[str]] = mapped_column(String(20), comment='Enroll Number;student or staff number')
    is_examinee: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Examinee')
    is_proctor: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Proctor')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')
