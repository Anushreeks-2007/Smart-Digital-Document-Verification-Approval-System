import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "lost_found.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    schema_path = BASE_DIR / "schema.sql"

    with get_db_connection() as conn:
        conn.executescript(
            schema_path.read_text(encoding="utf-8")
        )

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")
