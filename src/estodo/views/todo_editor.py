"""Todo editor widget"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List
from ..models.todo import Todo
from ..models.tag import TagModel, Tag
from .markdown import render_markdown
from .tag_selector import TagSelectorDialog, TagDisplayWidget


class TodoEditor(QWidget):
    """Todo editor widget"""

    todo_saved = pyqtSignal(object)  # Emits Todo
    todo_deleted = pyqtSignal(object)  # Emits Todo
    edit_cancelled = pyqtSignal()

    def __init__(self, tag_model: Optional[TagModel] = None, parent=None):
        super().__init__(parent)
        self.todo: Optional[Todo] = None
        self.tag_model = tag_model
        self.selected_tag_ids: List[int] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()

        self.title_label = QLabel("编辑待办")
        self.title_label.setObjectName("headerLabel")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("primaryButton")
        header_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("secondaryButton")
        header_layout.addWidget(self.cancel_button)

        layout.addLayout(header_layout)

        # Title input
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("输入待办标题...")
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        # Priority and completed row
        meta_layout = QHBoxLayout()

        meta_layout.addWidget(QLabel("优先级:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItem("低 (Low)", 1)
        self.priority_combo.addItem("中 (Medium)", 2)
        self.priority_combo.addItem("高 (High)", 3)
        meta_layout.addWidget(self.priority_combo)

        meta_layout.addSpacing(20)

        self.completed_check = QCheckBox("已完成")
        meta_layout.addWidget(self.completed_check)

        meta_layout.addStretch()

        self.delete_button = QPushButton("删除待办")
        self.delete_button.setObjectName("dangerButton")
        meta_layout.addWidget(self.delete_button)

        layout.addLayout(meta_layout)

        # Tags row
        if self.tag_model:
            tags_layout = QHBoxLayout()
            self.tag_display = TagDisplayWidget()
            self.tag_display.clicked.connect(self._open_tag_selector)
            tags_layout.addWidget(self.tag_display)
            layout.addLayout(tags_layout)

        # Content editor with preview splitter
        layout.addWidget(QLabel("内容 (Markdown):"))

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Editor
        self.content_editor = QTextEdit()
        self.content_editor.setPlaceholderText("输入 Markdown 内容...")
        self.content_editor.textChanged.connect(self._update_preview)
        splitter.addWidget(self.content_editor)

        # Preview
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setHtml("<div style='color: #64748b; padding: 8px;'>预览...</div>")
        splitter.addWidget(self.preview)

        splitter.setSizes([500, 500])
        layout.addWidget(splitter, 1)

        # Connect buttons
        self.save_button.clicked.connect(self._on_save)
        self.cancel_button.clicked.connect(self._on_cancel)
        self.delete_button.clicked.connect(self._on_delete)

    def set_todo(self, todo: Optional[Todo]):
        """Set the todo to edit"""
        self.todo = todo
        self.selected_tag_ids = []

        if todo:
            self.title_label.setText(f"编辑待办 - #{todo.id}" if todo.id else "新建待办")
            self.title_input.setText(todo.title)
            self.content_editor.setPlainText(todo.content)
            self.priority_combo.setCurrentIndex(todo.priority - 1)
            self.completed_check.setChecked(todo.is_completed)
            self.delete_button.setVisible(todo.id is not None)
            self._update_preview()

            # Load tags
            if todo.id and self.tag_model:
                tags = self.tag_model.get_by_todo_id(todo.id)
                self.selected_tag_ids = [t.id for t in tags if t.id]
                self._update_tag_display()
        else:
            self.title_label.setText("新建待办")
            self.title_input.clear()
            self.content_editor.clear()
            self.priority_combo.setCurrentIndex(1)
            self.completed_check.setChecked(False)
            self.delete_button.setVisible(False)
            self.preview.setHtml("<div style='color: #64748b; padding: 8px;'>预览...</div>")

            # Clear tags
            if self.tag_model:
                self._update_tag_display()

    def clear(self):
        """Clear the editor"""
        self.set_todo(None)

    def _update_preview(self):
        """Update the markdown preview"""
        content = self.content_editor.toPlainText()
        if content:
            html = render_markdown(content)
            self.preview.setHtml(html)
        else:
            self.preview.setHtml("<div style='color: #64748b; padding: 8px;'>预览...</div>")

    def _on_save(self):
        """Handle save button"""
        if self.todo is None:
            self.todo = Todo()

        self.todo.title = self.title_input.text().strip()
        self.todo.content = self.content_editor.toPlainText()
        self.todo.priority = self.priority_combo.currentData()
        self.todo.is_completed = self.completed_check.isChecked()

        if not self.todo.title:
            self.todo.title = "(无标题)"

        self.todo_saved.emit(self.todo)

    def _on_cancel(self):
        """Handle cancel button"""
        self.edit_cancelled.emit()

    def _on_delete(self):
        """Handle delete button"""
        if self.todo and self.todo.id:
            self.todo_deleted.emit(self.todo)

    def _open_tag_selector(self):
        """Open tag selector dialog"""
        if not self.tag_model:
            return

        dialog = TagSelectorDialog(self.tag_model, self.selected_tag_ids, self)
        dialog.tags_selected.connect(self._on_tags_selected)
        dialog.exec()

    def _on_tags_selected(self, tag_ids: List[int]):
        """Handle tags selected"""
        self.selected_tag_ids = tag_ids
        self._update_tag_display()

    def _update_tag_display(self):
        """Update the tag display widget"""
        if not self.tag_model:
            return

        tags = []
        for tag_id in self.selected_tag_ids:
            tag = self.tag_model.get_by_id(tag_id)
            if tag:
                tags.append(tag)

        self.tag_display.set_tags(tags)
