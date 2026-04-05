"""Pomodoro model"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List
from ..database import Database


@dataclass
class Pomodoro:
    """Pomodoro data class"""
    id: Optional[int] = None
    todo_id: Optional[int] = None
    duration: int = 25  # minutes
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_completed: bool = False
    note: str = ""

    @property
    def elapsed_minutes(self) -> int:
        """Get elapsed minutes"""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        elif self.start_time:
            return int((datetime.now() - self.start_time).total_seconds() / 60)
        return 0


class PomodoroModel:
    """Pomodoro model for database operations"""

    def __init__(self, db: Database):
        self.db = db

    def create(self, pomodoro: Pomodoro) -> Pomodoro:
        """Create a new pomodoro"""
        with self.db._get_connection() as conn:
            start_time = pomodoro.start_time.isoformat() if pomodoro.start_time else None
            end_time = pomodoro.end_time.isoformat() if pomodoro.end_time else None

            cursor = conn.execute("""
                INSERT INTO pomodoros (todo_id, duration, start_time, end_time, is_completed, note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pomodoro.todo_id, pomodoro.duration, start_time, end_time,
                  int(pomodoro.is_completed), pomodoro.note))
            pomodoro.id = cursor.lastrowid

            cursor = conn.execute("SELECT * FROM pomodoros WHERE id = ?", (pomodoro.id,))
            row = cursor.fetchone()
            return self._row_to_pomodoro(row)

    def update(self, pomodoro: Pomodoro) -> Pomodoro:
        """Update a pomodoro"""
        with self.db._get_connection() as conn:
            start_time = pomodoro.start_time.isoformat() if pomodoro.start_time else None
            end_time = pomodoro.end_time.isoformat() if pomodoro.end_time else None

            conn.execute("""
                UPDATE pomodoros
                SET todo_id = ?, duration = ?, start_time = ?, end_time = ?,
                    is_completed = ?, note = ?
                WHERE id = ?
            """, (pomodoro.todo_id, pomodoro.duration, start_time, end_time,
                  int(pomodoro.is_completed), pomodoro.note, pomodoro.id))

            cursor = conn.execute("SELECT * FROM pomodoros WHERE id = ?", (pomodoro.id,))
            row = cursor.fetchone()
            return self._row_to_pomodoro(row)

    def delete(self, pomodoro_id: int):
        """Delete a pomodoro"""
        with self.db._get_connection() as conn:
            conn.execute("DELETE FROM pomodoros WHERE id = ?", (pomodoro_id,))

    def get_by_id(self, pomodoro_id: int) -> Optional[Pomodoro]:
        """Get a pomodoro by id"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM pomodoros WHERE id = ?", (pomodoro_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_pomodoro(row)
            return None

    def get_by_todo_id(self, todo_id: int) -> List[Pomodoro]:
        """Get all pomodoros for a todo"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM pomodoros WHERE todo_id = ? ORDER BY start_time DESC
            """, (todo_id,))
            return [self._row_to_pomodoro(row) for row in cursor.fetchall()]

    def get_recent(self, limit: int = 50) -> List[Pomodoro]:
        """Get recent pomodoros"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM pomodoros ORDER BY start_time DESC LIMIT ?
            """, (limit,))
            return [self._row_to_pomodoro(row) for row in cursor.fetchall()]

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Pomodoro]:
        """Get pomodoros within a date range"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM pomodoros
                WHERE start_time >= ? AND start_time < ?
                ORDER BY start_time ASC
            """, (start_date.isoformat(), end_date.isoformat()))
            return [self._row_to_pomodoro(row) for row in cursor.fetchall()]

    def get_daily_counts(self, days: int = 365) -> dict:
        """Get daily pomodoro counts for heatmap"""
        with self.db._get_connection() as conn:
            start_date = datetime.now() - timedelta(days=days)
            cursor = conn.execute("""
                SELECT DATE(start_time) as date, COUNT(*) as count
                FROM pomodoros
                WHERE is_completed = 1 AND start_time >= ?
                GROUP BY DATE(start_time)
                ORDER BY date
            """, (start_date.isoformat(),))

            counts = {}
            for row in cursor.fetchall():
                counts[row["date"]] = row["count"]
            return counts

    def _row_to_pomodoro(self, row) -> Pomodoro:
        """Convert a database row to a Pomodoro object"""
        return Pomodoro(
            id=row["id"],
            todo_id=row["todo_id"],
            duration=row["duration"],
            start_time=datetime.fromisoformat(row["start_time"]) if row["start_time"] else None,
            end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
            is_completed=bool(row["is_completed"]),
            note=row["note"],
        )
