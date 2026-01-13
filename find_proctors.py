from app.data.database import db_session_query
from app.data.entity.entities import Users

def find_proctors():
    with db_session_query() as session:
        proctors = session.query(Users).filter(Users.is_proctor == True).all()
        for p in proctors:
            print(f"Email: {p.email}, Pwd: {p.pwd}, Proctor: {p.is_proctor}")

if __name__ == "__main__":
    import os
    # Ensure environment variable is set for the script
    if "SQLALCHEMY_DATABASE_URL" not in os.environ:
        os.environ["SQLALCHEMY_DATABASE_URL"] = "postgresql://postgres:postgres@localhost/ep"
    find_proctors()
