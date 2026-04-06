"""Todo model"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from ..database import Database


# Status constants
TODO_STATUS_ACTIVE = 0
TODO_STATUS_ARCHIVED = 1


@dataclass
class Todo:
    """Todo data class"""
    id: Optional[int] = None
    parent_id: Optional[int] = None
    title: str = ""
    content: str = ""
    priority: int = 1  # 1=low, 2=medium, 3=high
    is_completed: bool = False
    sort_order: int = 0
    status: int = TODO_STATUS_ACTIVE  # 0=active, 1=archived
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    children: List["Todo"] = field(default_factory=list)
    tags: List["Tag"] = field(default_factory=list)

    @property
    def priority_name(self) -> str:
        """Get priority name"""
        return {1: "低", 2: "中", 3: "高"}.get(self.priority, "中")

    @property
    def priority_color(self) -> str:
        """Get priority color"""
        return {1: "#22c55e", 2: "#eab308", 3: "#ef4444"}.get(self.priority, "#eab308")


@dataclass
class Tag:
    """Tag data class"""
    id: Optional[int] = None
    name: str = ""
    color: str = "#6366f1"
    created_at: Optional[datetime] = None


class TodoModel:
    """Todo model for database operations"""

    def __init__(self, db: Database):
        self.db = db

    def create(self, todo: Todo) -> Todo:
        """Create a new todo"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO todos (parent_id, title, content, priority, sort_order, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (todo.parent_id, todo.title, todo.content, todo.priority, todo.sort_order, todo.status))
            todo.id = cursor.lastrowid

            # Get the created todo with timestamps
            cursor = conn.execute("SELECT * FROM todos WHERE id = ?", (todo.id,))
            row = cursor.fetchone()
            return self._row_to_todo(row)

    def update(self, todo: Todo) -> Todo:
        """Update a todo"""
        with self.db._get_connection() as conn:
            completed_at = todo.completed_at.isoformat() if todo.completed_at else None
            conn.execute("""
                UPDATE todos
                SET parent_id = ?, title = ?, content = ?, priority = ?,
                    is_completed = ?, sort_order = ?, status = ?,
                    updated_at = CURRENT_TIMESTAMP, completed_at = ?
                WHERE id = ?
            """, (todo.parent_id, todo.title, todo.content, todo.priority,
                  int(todo.is_completed), todo.sort_order, todo.status,
                  completed_at, todo.id))

            cursor = conn.execute("SELECT * FROM todos WHERE id = ?", (todo.id,))
            row = cursor.fetchone()
            return self._row_to_todo(row)

    def delete(self, todo_id: int):
        """Delete a todo and all its children"""
        with self.db._get_connection() as conn:
            # Recursively delete children
            self._delete_with_children(conn, todo_id)

    def _delete_with_children(self, conn, todo_id: int):
        """Recursively delete a todo and its children"""
        # Get all children
        cursor = conn.execute("SELECT id FROM todos WHERE parent_id = ?", (todo_id,))
        children = cursor.fetchall()
        for child in children:
            self._delete_with_children(conn, child["id"])

        # Delete the todo itself
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))

    def archive(self, todo_id: int):
        """Archive a todo and all its children recursively"""
        with self.db._get_connection() as conn:
            self._archive_with_children(conn, todo_id)

    def _archive_with_children(self, conn, todo_id: int):
        """Recursively archive a todo and its children"""
        # Get all children first
        cursor = conn.execute("SELECT id FROM todos WHERE parent_id = ?", (todo_id,))
        children = cursor.fetchall()
        for child in children:
            self._archive_with_children(conn, child["id"])

        # Archive the todo itself
        conn.execute("UPDATE todos SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                     (TODO_STATUS_ARCHIVED, todo_id))

    def unarchive(self, todo_id: int):
        """Unarchive a todo and all its children recursively"""
        with self.db._get_connection() as conn:
            self._unarchive_with_children(conn, todo_id)

    def _unarchive_with_children(self, conn, todo_id: int):
        """Recursively unarchive a todo and its children"""
        # Get all children first
        cursor = conn.execute("SELECT id FROM todos WHERE parent_id = ?", (todo_id,))
        children = cursor.fetchall()
        for child in children:
            self._unarchive_with_children(conn, child["id"])

        # Unarchive the todo itself
        conn.execute("UPDATE todos SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                     (TODO_STATUS_ACTIVE, todo_id))

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        """Get a todo by id"""
        with self.db._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_todo(row)
            return None

    def get_root_todos(self, include_completed: bool = True, status: int = TODO_STATUS_ACTIVE) -> List[Todo]:
        """Get all root level todos with optional status filter"""
        with self.db._get_connection() as conn:
            query = "SELECT * FROM todos WHERE parent_id IS NULL AND status = ?"
            params = [status]
            if not include_completed:
                query += " AND is_completed = 0"
            query += " ORDER BY sort_order, created_at DESC"

            cursor = conn.execute(query, params)
            todos = [self._row_to_todo(row) for row in cursor.fetchall()]

            # Load children for each todo
            for todo in todos:
                todo.children = self.get_children(todo.id, include_completed, status)

            return todos

    def get_children(self, parent_id: int, include_completed: bool = True, status: int = TODO_STATUS_ACTIVE) -> List[Todo]:
        """Get children of a todo"""
        with self.db._get_connection() as conn:
            query = "SELECT * FROM todos WHERE parent_id = ? AND status = ?"
            params = [parent_id, status]
            if not include_completed:
                query += " AND is_completed = 0"
            query += " ORDER BY sort_order, created_at DESC"

            cursor = conn.execute(query, params)
            children = [self._row_to_todo(row) for row in cursor.fetchall()]

            # Recursively load children
            for child in children:
                child.children = self.get_children(child.id, include_completed, status)

            return children

    def get_all_todos_flat(self, include_completed: bool = True, status: Optional[int] = None) -> List[Todo]:
        """Get all todos as a flat list"""
        with self.db._get_connection() as conn:
            query = "SELECT * FROM todos"
            params = []
            conditions = []
            if not include_completed:
                conditions.append("is_completed = 0")
            if status is not None:
                conditions.append("status = ?")
                params.append(status)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY created_at DESC"

            cursor = conn.execute(query, params)
            return [self._row_to_todo(row) for row in cursor.fetchall()]

    def _row_to_todo(self, row) -> Todo:
        """Convert a database row to a Todo object"""
        return Todo(
            id=row["id"],
            parent_id=row["parent_id"],
            title=row["title"],
            content=row["content"],
            priority=row["priority"],
            is_completed=bool(row["is_completed"]),
            sort_order=row["sort_order"],
            # status=row.get("status", TODO_STATUS_ACTIVE),
            status=row["status"] if "status" in row.keys() else TODO_STATUS_ACTIVE,
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
        )
