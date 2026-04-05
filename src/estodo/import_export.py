"""Import/Export functionality for EsTodo"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from .database import Database
from .models.todo import Todo, TodoModel
from .models.pomodoro import Pomodoro, PomodoroModel
from .models.tag import Tag, TagModel


class ImportExport:
    """Import/Export manager"""

    def __init__(self, db: Database):
        self.db = db
        self.todo_model = TodoModel(db)
        self.pomodoro_model = PomodoroModel(db)
        self.tag_model = TagModel(db)

    def export_all(self, file_path: Path) -> Dict[str, Any]:
        """Export all data to JSON file"""
        # Get all data
        todos = self.todo_model.get_all_todos_flat(include_completed=True)
        pomodoros = self.pomodoro_model.get_recent(limit=10000)
        tags = self.tag_model.get_all()

        # Build export data structure
        data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "tags": [self._tag_to_dict(tag) for tag in tags],
            "todos": [self._todo_to_dict(todo) for todo in todos],
            "pomodoros": [self._pomodoro_to_dict(p) for p in pomodoros],
        }

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data

    def import_all(self, file_path: Path, replace: bool = False) -> Dict[str, int]:
        """Import all data from JSON file

        Args:
            file_path: Path to JSON file
            replace: If True, delete all existing data before importing

        Returns:
            Dictionary with counts of imported items
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        counts = {
            "tags": 0,
            "todos": 0,
            "pomodoros": 0,
        }

        # If replace, clear existing data
        if replace:
            self._clear_all_data()

        # Import tags first (todos reference tags)
        tag_id_map = {}  # old_id -> new_tag
        if "tags" in data:
            for tag_dict in data["tags"]:
                old_id = tag_dict.get("id")
                tag = self._dict_to_tag(tag_dict)
                # Check if tag already exists by name
                existing = self.tag_model.get_by_name(tag.name)
                if existing:
                    tag_id_map[old_id] = existing
                else:
                    created = self.tag_model.create(tag)
                    tag_id_map[old_id] = created
                    counts["tags"] += 1

        # Import todos
        todo_id_map = {}  # old_id -> new_todo
        todo_tag_map = {}  # old_todo_id -> list of old_tag_ids
        if "todos" in data:
            for todo_dict in data["todos"]:
                old_id = todo_dict.get("id")
                # Save tag ids for later
                if "tag_ids" in todo_dict:
                    todo_tag_map[old_id] = todo_dict["tag_ids"]

                todo = self._dict_to_todo(todo_dict)
                # Fix parent_id - will set later in a second pass
                original_parent_id = todo.parent_id
                todo.parent_id = None  # temporarily clear

                created = self.todo_model.create(todo)
                todo_id_map[old_id] = created
                counts["todos"] += 1

            # Second pass: fix parent_ids
            for todo_dict in data["todos"]:
                old_id = todo_dict.get("id")
                old_parent_id = todo_dict.get("parent_id")

                if old_parent_id and old_id in todo_id_map and old_parent_id in todo_id_map:
                    todo = todo_id_map[old_id]
                    todo.parent_id = todo_id_map[old_parent_id].id
                    self.todo_model.update(todo)

            # Third pass: set tags
            for old_todo_id, old_tag_ids in todo_tag_map.items():
                if old_todo_id in todo_id_map:
                    todo = todo_id_map[old_todo_id]
                    new_tag_ids = []
                    for old_tag_id in old_tag_ids:
                        if old_tag_id in tag_id_map:
                            new_tag_ids.append(tag_id_map[old_tag_id].id)
                    if new_tag_ids and todo.id:
                        self.tag_model.set_todo_tags(todo.id, new_tag_ids)

        # Import pomodoros
        if "pomodoros" in data:
            for pomo_dict in data["pomodoros"]:
                pomo = self._dict_to_pomodoro(pomo_dict)
                # Fix todo_id if needed
                if pomo.todo_id and pomo.todo_id in todo_id_map:
                    pomo.todo_id = todo_id_map[pomo.todo_id].id

                self.pomodoro_model.create(pomo)
                counts["pomodoros"] += 1

        return counts

    def _clear_all_data(self):
        """Clear all existing data from database"""
        with self.db._get_connection() as conn:
            conn.execute("DELETE FROM todo_tags")
            conn.execute("DELETE FROM tags")
            conn.execute("DELETE FROM pomodoros")
            conn.execute("DELETE FROM todos")

    def _tag_to_dict(self, tag: Tag) -> Dict[str, Any]:
        """Convert Tag to dict"""
        return {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at.isoformat() if tag.created_at else None,
        }

    def _dict_to_tag(self, data: Dict[str, Any]) -> Tag:
        """Convert dict to Tag"""
        return Tag(
            name=data.get("name", ""),
            color=data.get("color", "#6366f1"),
        )

    def _todo_to_dict(self, todo: Todo) -> Dict[str, Any]:
        """Convert Todo to dict"""
        # Get tag ids for this todo
        tag_ids = []
        if todo.id:
            tags = self.tag_model.get_by_todo_id(todo.id)
            tag_ids = [t.id for t in tags if t.id]

        return {
            "id": todo.id,
            "parent_id": todo.parent_id,
            "title": todo.title,
            "content": todo.content,
            "priority": todo.priority,
            "is_completed": todo.is_completed,
            "sort_order": todo.sort_order,
            "created_at": todo.created_at.isoformat() if todo.created_at else None,
            "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
            "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
            "tag_ids": tag_ids,
        }

    def _dict_to_todo(self, data: Dict[str, Any]) -> Todo:
        """Convert dict to Todo"""
        completed_at = None
        if data.get("completed_at"):
            try:
                completed_at = datetime.fromisoformat(data["completed_at"])
            except (ValueError, TypeError):
                pass

        return Todo(
            parent_id=data.get("parent_id"),
            title=data.get("title", ""),
            content=data.get("content", ""),
            priority=data.get("priority", 1),
            is_completed=data.get("is_completed", False),
            sort_order=data.get("sort_order", 0),
            completed_at=completed_at,
        )

    def _pomodoro_to_dict(self, pomo: Pomodoro) -> Dict[str, Any]:
        """Convert Pomodoro to dict"""
        return {
            "id": pomo.id,
            "todo_id": pomo.todo_id,
            "duration": pomo.duration,
            "start_time": pomo.start_time.isoformat() if pomo.start_time else None,
            "end_time": pomo.end_time.isoformat() if pomo.end_time else None,
            "is_completed": pomo.is_completed,
            "note": pomo.note,
        }

    def _dict_to_pomodoro(self, data: Dict[str, Any]) -> Pomodoro:
        """Convert dict to Pomodoro"""
        start_time = None
        if data.get("start_time"):
            try:
                start_time = datetime.fromisoformat(data["start_time"])
            except (ValueError, TypeError):
                pass

        end_time = None
        if data.get("end_time"):
            try:
                end_time = datetime.fromisoformat(data["end_time"])
            except (ValueError, TypeError):
                pass

        return Pomodoro(
            todo_id=data.get("todo_id"),
            duration=data.get("duration", 25),
            start_time=start_time,
            end_time=end_time,
            is_completed=data.get("is_completed", False),
            note=data.get("note", ""),
        )
