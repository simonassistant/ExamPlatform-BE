"""
Initialize SQLite database for local development.
Uses SQLAlchemy's create_all to generate schema from entity definitions.
"""
import os
import sys

# Ensure .env is loaded before importing database module
from dotenv import load_dotenv
load_dotenv()

from app.data.entity.base import Base
from app.data.entity import entities  # Import all entities to register them
from sqlalchemy import create_engine

db_url = os.environ.get("SQLALCHEMY_DATABASE_URL")
if not db_url:
    print("ERROR: SQLALCHEMY_DATABASE_URL not set in .env")
    sys.exit(1)

print(f"Database URL: {db_url}")

# For SQLite, we don't need pool settings
if db_url.startswith("sqlite"):
    engine = create_engine(db_url, echo=True)
else:
    engine = create_engine(db_url, echo=True, pool_size=5)

print("Creating all tables...")
Base.metadata.create_all(engine)
print("Database initialized successfully!")
