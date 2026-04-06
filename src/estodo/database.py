"""Database management for EsTodo"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional


class Database:
    """Database wrapper for EsTodo"""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Default to user data directory
            db_path = Path.home() / ".estodo" / "estodo.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            # Todos table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT,
                    priority INTEGER DEFAULT 1,
                    is_completed INTEGER DEFAULT 0,
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status INTEGER DEFAULT 0,
                    FOREIGN KEY (parent_id) REFERENCES todos(id)
                )
            """)

            # Database migration: add status column if not exists
            self._migrate_database(conn)

    def _migrate_database(self, conn: sqlite3.Connection):
        """Migrate database to latest version"""
        # Check if status column exists
        cursor = conn.execute("PRAGMA table_info(todos)")
        columns = [col[1] for col in cursor.fetchall()]

        if "status" not in columns:
            # Add status column with default 0 (active)
            conn.execute("ALTER TABLE todos ADD COLUMN status INTEGER DEFAULT 0")
            # Create index for status
            conn.execute("CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status)")

            # Pomodoros table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pomodoros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    todo_id INTEGER,
                    duration INTEGER NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    is_completed INTEGER DEFAULT 0,
                    note TEXT,
                    FOREIGN KEY (todo_id) REFERENCES todos(id)
                )
            """)

            # Tags table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT DEFAULT '#6366f1',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Todo-Tag association table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS todo_tags (
                    todo_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (todo_id, tag_id),
                    FOREIGN KEY (todo_id) REFERENCES todos(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            # Settings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Create indexes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_todos_parent_id ON todos(parent_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos(is_completed)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pomodoros_start ON pomodoros(start_time)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pomodoros_todo ON pomodoros(todo_id)
            """)

            # Initialize default settings
            self._init_default_settings(conn)

    def _init_default_settings(self, conn: sqlite3.Connection):
        """Initialize default settings"""
        defaults = {
            "pomodoro_work_duration": "25",
            "pomodoro_short_break": "5",
            "pomodoro_long_break": "15",
            "pomodoro_long_break_after": "4",
            "theme": "light",
            "shortcut_new_todo": "Ctrl+N",
            "shortcut_complete": "Ctrl+Enter",
        }

        for key, value in defaults.items():
            conn.execute("""
                INSERT OR IGNORE INTO settings (key, value)
                VALUES (?, ?)
            """, (key, value))

    def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting value"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT value FROM settings WHERE key = ?
            """, (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            """, (key, value))
