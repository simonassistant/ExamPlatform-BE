"""
Create test proctor account in SQLite database.
SQLite-compatible version using INSERT OR REPLACE.
"""
import os
import uuid
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.data.entity.entities import Users

db_url = os.environ.get("SQLALCHEMY_DATABASE_URL")
if not db_url:
    print("Error: SQLALCHEMY_DATABASE_URL not found")
    exit(1)

print(f"Using database: {db_url}")

engine = create_engine(db_url)

def md5_encode(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()

# Proctor credentials
email = "proctor@example.com"
password = "password123"
hashed_pwd = md5_encode(password)
proctor_id = str(uuid.uuid4()).replace("-", "")[:26].upper()

with Session(engine) as session:
    # Check if user exists
    existing = session.query(Users).filter(Users.email == email).first()
    
    if existing:
        print(f"Updating existing proctor account...")
        existing.pwd = hashed_pwd
        existing.is_proctor = True
        existing.updated_at = datetime.utcnow()
    else:
        print(f"Creating new proctor account...")
        user = Users(
            id=proctor_id,
            username="proctor",
            pwd=hashed_pwd,
            email=email,
            mobile="0000000000",
            surname="Proctor",
            name="One",
            gender=True,
            enroll_number="P001",
            is_examinee=False,
            is_proctor=True,
            created_by="system",
            created_at=datetime.utcnow(),
            updated_by="system",
            updated_at=datetime.utcnow(),
            is_deleted=False,
        )
        session.add(user)
    
    session.commit()

print(f"\\nProctor account ready:")
print(f"  Email: {email}")
print(f"  Password: {password}")
