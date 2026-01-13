import os
from sqlalchemy import create_engine, text

# Configuration
PG_USER = "postgres"
PG_PASS = "Zza_20040715"
PG_HOST = "127.0.0.1"
PG_PORT = "5432"
TARGET_DB = "ep"
ROOT_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/postgres"
EP_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{TARGET_DB}"

def init_db():
    # 1. Create Database if not exists
    engine = create_engine(ROOT_URL, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{TARGET_DB}'"))
            if not result.scalar():
                print(f"Creating database '{TARGET_DB}'...")
                conn.execute(text(f"CREATE DATABASE {TARGET_DB}"))
            else:
                print(f"Database '{TARGET_DB}' already exists.")
    except Exception as e:
        with open("db_error.txt", "w") as f:
             import traceback
             traceback.print_exc(file=f)
        return

    # 2. Run DDL
    print(f"Connecting to {TARGET_DB}...")
    ep_engine = create_engine(EP_URL)
    ddl_path = os.path.join("deploy", "sql", "ddl.sql")
    
    if not os.path.exists(ddl_path):
        print(f"DDL file not found at {ddl_path}")
        return

    print(f"Reading DDL from {ddl_path}...")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl_content = f.read()

    try:
        with ep_engine.connect() as conn:
            with conn.begin():
                # Execute as one block if possible, or split if needed
                # Psycopg2 usually handles multi-statement in one execute calls if passed as string
                conn.execute(text(ddl_content))
        print("Schema initialized successfully.")
    except Exception as e:
        print(f"Error executing DDL: {e}")

if __name__ == "__main__":
    init_db()
