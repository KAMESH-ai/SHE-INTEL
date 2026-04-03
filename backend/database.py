import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE = Path(__file__).parent / "she_intel.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    try:
        with get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS periods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    flow_level TEXT DEFAULT 'medium',
                    symptoms TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            conn.commit()
        print("Database initialized successfully!")
    except sqlite3.Error as e:
        print(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    init_db()
