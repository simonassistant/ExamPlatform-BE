import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text

load_dotenv(find_dotenv())
load_dotenv(find_dotenv(".env.local"))

sql = text("""
INSERT INTO users (
  id, username, pwd, email, mobile,
  surname, name, gender, enroll_number,
  is_examinee, is_proctor,
  created_by, created_at, updated_by, updated_at, is_deleted
) VALUES (
  :id, :username, :pwd, :email, :mobile,
  :surname, :name, :gender, :enroll_number,
  :is_examinee, :is_proctor,
  :created_by, :created_at, :updated_by, :updated_at, :is_deleted
)
""")

engine = create_engine(os.environ["SQLALCHEMY_DATABASE_URL"])
with engine.begin() as conn:
    conn.execute(sql, {
        "id": "01HXYZTESTUSER0000000000",
        "username": "testuser",
        "pwd": "plaintext-or-hash",
        "email": "testuser@example.com",
        "mobile": "1234567890",
        "surname": "Test",
        "name": "User",
        "gender": True,
        "enroll_number": "ENR001",
        "is_examinee": True,
        "is_proctor": False,
        "created_by": "system",
        "created_at": datetime.utcnow(),
        "updated_by": "system",
        "updated_at": datetime.utcnow(),
        "is_deleted": False,
    })
print("Inserted test user.")