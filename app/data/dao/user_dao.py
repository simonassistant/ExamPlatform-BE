from datetime import datetime

from sqlalchemy import update, select

from app.data.dao.base_dao import BaseDAO
from app.data.database import db_exec, db_one_or_none
from app.data.entity.entities import Users

class UserDAO(BaseDAO):
    def __init__(self):
        super().__init__(Users)

    def add_or_update(self, user: Users) -> str:
        user_existing = self.get_by_email(user.email)
        if user_existing is None:
            return self.add(user)
        else:
            user.id = user_existing.id
            self.update_by_email(user)
            return user_existing.id

    @staticmethod
    def get_by_email(email: str) -> Users | None:
        stmt = select(Users).where(Users.email == email)
        return db_one_or_none(stmt)

    @staticmethod
    def get_by_enroll_number(enroll_number: str) -> Users | None:
        stmt = select(Users).where(Users.enroll_number == enroll_number)
        return db_one_or_none(stmt)

    @staticmethod
    def update_by_email(user: Users):
        statement = update(Users).where(Users.email == user.email).values(
            mobile=user.mobile, pwd=user.pwd,
            surname=user.surname, name=user.name, gender=user.gender,
            enroll_number=user.enroll_number, is_examinee=user.is_examinee, is_proctor=user.is_proctor,
            is_deleted=user.is_deleted, updated_at=datetime.now(), updated_by=user.updated_by)
        db_exec(statement)
