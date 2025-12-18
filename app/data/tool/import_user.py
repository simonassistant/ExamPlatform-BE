import os
import sys

import pandas as pd

from app.data.dao.user_dao import UserDAO
from app.data.entity.entities import Users
from app.util.util import md5_encode

file_name: str = 'user_sample.xlsx'

def _is_male(value: str) -> bool | None:
    if pd.isna(value) or value is None or value=='':
        return None
    if value in ['M', 'm']:
        return True
    return False

def _is_true(value: str) -> bool | None:
    if pd.isna(value) or value is None or value=='':
        return None
    if value in ['T', 't', 'Y', 'y']:
        return True
    return False

def _get_str(value: str | int) -> str | None:
    if pd.isna(value):
        return None
    if type(value) == int:
        return str(value)
    return value

def import_examinee():
    df = pd.read_excel(file_name, sheet_name='student')
    if df.empty:
        return
    for index, row in df.iterrows():
        email = _get_str(row['email'])
        user = Users(
            enroll_number=_get_str(row['student id']),
            email=email,
            mobile=_get_str(row['mobile']),
            name=_get_str(row['given name']),
            surname=_get_str(row['surname']),
            gender=_is_male(row['gender']),
            is_deleted=_is_true(row['deleted']),
            is_examinee=True,
        )
        if user.email is not None:
            UserDAO().add_or_update(user)
            print(f'Import examinee {email}')

def import_proctor():
    df = pd.read_excel(file_name, sheet_name='invigilator')
    if df.empty:
        return
    for index, row in df.iterrows():
        email = _get_str(row['email'])
        user = Users(
            enroll_number=_get_str(row['staff id']),
            email=email,
            pwd=md5_encode(_get_str(row['password'])),
            mobile=_get_str(row['mobile']),
            name=_get_str(row['given name']),
            surname=_get_str(row['surname']),
            gender=_is_male(row['gender']),
            is_deleted=_is_true(row['deleted']),
            is_proctor=True,
        )
        if user.email is not None:
            UserDAO().add_or_update(user)
            print(f'Import proctor {email}')

def main():
    import_examinee()
    import_proctor()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        print(f"[{os.getenv("ENV_STATE")} env] importing user from {file_name}")
    main()