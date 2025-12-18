import logging
import os
from collections.abc import Iterable
from contextlib import contextmanager

from sqlalchemy import create_engine, Executable
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError, SQLAlchemyError
from sqlalchemy.orm import Session
# print(os.environ)
db_url = os.environ["SQLALCHEMY_DATABASE_URL"]
if not db_url:
    raise Exception("SQLALCHEMY_DATABASE_URL should be defined in environment file")
engine = create_engine(
    db_url,
    echo=os.environ["SQLALCHEMY_ECHO"]=='True',
    pool_size=20,
    max_overflow=50,
    pool_timeout=20
)
# Base.metadata.create_all(engine)   # create tables

def db_session_query() -> Session:
    return Session(engine)

@contextmanager
def db_session_commit():
    try:
        with Session(engine) as session:  # ‌:ml-citation{ref="4" data="citationList"}
            yield session
            session.commit()
    except IntegrityError as e:
        logging.error(f"Data Integrity Error: {str(e)}")
        if session is not None:
            session.rollback()
        raise
    except OperationalError as e:
        logging.error(f"Database Connection Error: {str(e)}")
        raise
    except SQLAlchemyError as e:
        logging.exception(f"Unknown SQLAlchemy Error: {str(e)}")
        raise

def db_add(instance: object):
    try:
        with db_session_commit() as session:
            session.add(instance)
    except DatabaseError:
        raise

def db_add_all(instances: Iterable[object]):
    try:
        with db_session_commit() as session:
            session.add_all(instances)
    except DatabaseError:
        raise

def db_exec(statement: Executable):
    try:
        with db_session_commit() as session:
            session.execute(statement)
    except DatabaseError:
        raise

def db_scalars(statement: Executable):
    res = None
    try:
        with Session(engine) as session:
            res = session.scalars(statement).all()
    except DatabaseError:
        raise
    return res

def db_one_or_none(statement: Executable):
    res = None
    try:
        with Session(engine) as session:
            res = session.scalars(statement).one_or_none()
    except DatabaseError:
        raise
    return res