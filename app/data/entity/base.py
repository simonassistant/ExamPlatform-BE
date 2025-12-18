import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Entity(DeclarativeBase):
    pass

class Base(Entity):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String(26), primary_key=True, comment='ID')
    created_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Creator ID')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Create Datetime')
    updated_by: Mapped[Optional[str]] = mapped_column(String(26), comment='Updator ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Update Datetime')
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, comment='Is Deleted')

    def to_dict(self) -> dict:
        d: dict = self.__dict__
        if '_sa_instance_state' in d.keys():
            d.pop('_sa_instance_state')
        if 'password' in d.keys():
            d.pop('password')
        if 'pwd' in d.keys():
            d.pop('pwd')
        return d