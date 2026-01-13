from sqlalchemy import text
from app.data.database import engine

def update_schema():
    with engine.connect() as conn:
        try:
            # Add paper_type column to paper table
            print("Adding paper_type to paper table...")
            conn.execute(text("ALTER TABLE paper ADD COLUMN paper_type INTEGER"))
            print("Success.")
        except Exception as e:
            print(f"Skipping paper_type (maybe exists): {e}")

        try:
            # Add content column to paper_section table
            print("Adding content to paper_section table...")
            conn.execute(text("ALTER TABLE paper_section ADD COLUMN content TEXT"))
            print("Success.")
        except Exception as e:
            print(f"Skipping content (maybe exists): {e}")

        conn.commit()

if __name__ == "__main__":
    print("Updating schema...")
    update_schema()
    print("Schema update complete.")
