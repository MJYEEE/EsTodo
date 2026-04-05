"""Tag model"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from ..database import Database


@dataclass
class Tag:
    """Tag data class"""
    id: Optional[int] = None
    name: str = ""
    color: str = "#6366f1"
    created_at: Optional[datetime] = None


class TagModel:
    """Tag model for database operations"""

    def __init__(self, db: Database):
        self.db = db

    def create(self, tag: Tag) -> Tag:
        """Create a new tag"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO tags (name, color)
                VALUES (?, ?)
            """, (tag.name, tag.color))
            tag.id = cursor.lastrowid

            cursor = conn.execute("SELECT * FROM tags WHERE id = ?", (tag.id,))
            row = cursor.fetchone()
            return self._row_to_tag(row)

    def update(self, tag: Tag) -> Tag:
        """Update a tag"""
        with self.db._get_connection() as conn:
            conn.execute("""
                UPDATE tags
                SET name = ?, color = ?
                WHERE id = ?
            """, (tag.name, tag.color, tag.id))

            cursor = conn.execute("SELECT * FROM tags WHERE id = ?", (tag.id,))
            row = cursor.fetchone()
            return self._row_to_tag(row)

    def delete(self, tag_id: int):
        """Delete a tag"""
        with self.db._get_connection() as conn:
            conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))

    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """Get a tag by id"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_tag(row)
            return None

    def get_by_name(self, name: str) -> Optional[Tag]:
        """Get a tag by name"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tags WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return self._row_to_tag(row)
            return None

    def get_all(self) -> List[Tag]:
        """Get all tags"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tags ORDER BY name")
            return [self._row_to_tag(row) for row in cursor.fetchall()]

    def get_by_todo_id(self, todo_id: int) -> List[Tag]:
        """Get tags for a todo"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("""
                SELECT t.* FROM tags t
                JOIN todo_tags tt ON t.id = tt.tag_id
                WHERE tt.todo_id = ?
                ORDER BY t.name
            """, (todo_id,))
            return [self._row_to_tag(row) for row in cursor.fetchall()]

    def add_to_todo(self, todo_id: int, tag_id: int):
        """Add a tag to a todo"""
        with self.db._get_connection() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO todo_tags (todo_id, tag_id)
                VALUES (?, ?)
            """, (todo_id, tag_id))

    def remove_from_todo(self, todo_id: int, tag_id: int):
        """Remove a tag from a todo"""
        with self.db._get_connection() as conn:
            conn.execute("""
                DELETE FROM todo_tags
                WHERE todo_id = ? AND tag_id = ?
            """, (todo_id, tag_id))

    def set_todo_tags(self, todo_id: int, tag_ids: List[int]):
        """Set tags for a todo (replaces existing)"""
        with self.db._get_connection() as conn:
            conn.execute("DELETE FROM todo_tags WHERE todo_id = ?", (todo_id,))
            for tag_id in tag_ids:
                conn.execute("""
                    INSERT INTO todo_tags (todo_id, tag_id)
                    VALUES (?, ?)
                """, (todo_id, tag_id))

    def _row_to_tag(self, row) -> Tag:
        """Convert a database row to a Tag object"""
        return Tag(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        )
