import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

# Load common env
load_dotenv(find_dotenv())
# Also load .env.dev which we know exists
load_dotenv(".env.dev")

db_url = os.environ.get("SQLALCHEMY_DATABASE_URL")
if db_url and "localhost" in db_url:
    db_url = db_url.replace("localhost", "127.0.0.1")
if not db_url:
    print("Error: SQLALCHEMY_DATABASE_URL not found")
    exit(1)

engine = create_engine(db_url)

# Generate a unique ID (ulid-like string or just uuid)
# The schema uses VARCHAR(26)
proctor_id = str(uuid.uuid4()).replace("-", "")[:26].upper()

import hashlib

def md5_encode(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()

email = "proctor@example.com"
password = "password123"
hashed_pwd = md5_encode(password)

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
ON CONFLICT (email) DO UPDATE SET 
  pwd = EXCLUDED.pwd,
  is_proctor = EXCLUDED.is_proctor,
  updated_at = EXCLUDED.updated_at;
""")

with engine.begin() as conn:
    conn.execute(sql, {
        "id": proctor_id,
        "username": "proctor",
        "pwd": hashed_pwd,
        "email": email,
        "mobile": "0000000000",
        "surname": "Proctor",
        "name": "One",
        "gender": True,
        "enroll_number": "P001",
        "is_examinee": False,
        "is_proctor": True,
        "created_by": "system",
        "created_at": datetime.utcnow(),
        "updated_by": "system",
        "updated_at": datetime.utcnow(),
        "is_deleted": False,
    })

print(f"Created/Updated proctor account:")
print(f"Email: {email}")
print(f"Password: {password}")
