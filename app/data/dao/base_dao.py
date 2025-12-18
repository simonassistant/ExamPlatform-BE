import copy
from datetime import datetime

from typing import TypeVar, Type

from sqlalchemy import update
from ulid import ULID

from app.data.database import db_add, db_session_query, db_exec
from app.data.entity.base import Base

T = TypeVar('T', bound=Base)

class BaseDAO:
    def __init__(self, cls: Type[T]):
        self._cls = cls

    @staticmethod
    def add(instance: T) -> str:
        if instance.id is None:
            instance.id = str(ULID())
        #instance.is_deleted = False
        instance.created_at = datetime.now()
        instance.updated_at = instance.created_at
        instance.updated_by = instance.created_by
        instance_copy = copy.deepcopy(instance)
        db_add(instance_copy)
        return str(instance.id)

    def get(self, instance_id: str | int) -> T | None:
        if instance_id is None or instance_id == '':
            return None
        res = None
        with db_session_query() as session:
            res = session.get(self._cls, instance_id)
        return res

    def delete(self, instance_id: str, updated_by: str, is_deleted: bool = True):
        stmt = update(self._cls).where(self._cls.id == instance_id).values(
            is_deleted=True if is_deleted else None, updated_at=datetime.now(), updated_by=updated_by)
        db_exec(stmt)
