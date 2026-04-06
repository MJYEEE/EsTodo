"""Todo viewer widget - read-only display"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List
from ..models.todo import Todo
from ..models.tag import TagModel, Tag
from .markdown import render_markdown


class TodoViewer(QWidget):
    """Todo viewer widget - read-only display"""

    close_requested = pyqtSignal()

    def __init__(self, tag_model: Optional[TagModel] = None, parent=None):
        super().__init__(parent)
        self.todo: Optional[Todo] = None
        self.tag_model = tag_model
        self._tags: List[Tag] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header with close button
        header_layout = QHBoxLayout()

        header_label = QLabel("待办详情")
        header_label.setObjectName("headerLabel")
        header_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            padding: 8px 0px;
        """)
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        self.close_button = QPushButton("关闭")
        self.close_button.setObjectName("secondaryButton")
        self.close_button.setMinimumHeight(36)
        self.close_button.clicked.connect(self.close_requested.emit)
        header_layout.addWidget(self.close_button)

        layout.addLayout(header_layout)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(16)

        # Title
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            padding: 8px 0px;
        """)
        container_layout.addWidget(self.title_label)

        # Meta info row (priority + tags)
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(12)

        # Priority
        self.priority_label = QLabel()
        self.priority_label.setStyleSheet("""
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 12px;
        """)
        meta_layout.addWidget(self.priority_label)

        # Tags container
        self.tags_container = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(6)
        meta_layout.addWidget(self.tags_container)

        meta_layout.addStretch()
        container_layout.addLayout(meta_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: #e0e0e0;")
        container_layout.addWidget(separator)

        # Markdown content
        self.content_view = QLabel()
        self.content_view.setWordWrap(True)
        self.content_view.setTextFormat(Qt.TextFormat.RichText)
        self.content_view.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_view.setStyleSheet("""
            padding: 8px 0px;
            line-height: 1.6;
        """)
        container_layout.addWidget(self.content_view, 1)

        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        # Initial state
        self.clear()

    def set_todo(self, todo: Optional[Todo]):
        """Set the todo to display"""
        self.todo = todo
        self._tags = []

        if todo:
            # Title
            self.title_label.setText(todo.title or "(无标题)")

            # Priority
            priority_text = todo.priority_name
            priority_color = todo.priority_color
            text_color = "white" if todo.priority == 3 else "#333"
            self.priority_label.setText(priority_text)
            self.priority_label.setStyleSheet(f"""
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 12px;
                background-color: {priority_color};
                color: {text_color};
            """)
            self.priority_label.setVisible(True)

            # Tags
            if todo.id and self.tag_model:
                self._tags = self.tag_model.get_by_todo_id(todo.id)
            self._update_tag_display()

            # Content
            if todo.content:
                html = render_markdown(todo.content)
                self.content_view.setText(html)
            else:
                self.content_view.setText("<div style='color: #a0a0a0; padding: 8px;'>暂无内容</div>")
        else:
            self.clear()

    def clear(self):
        """Clear the viewer"""
        self.title_label.setText("选择一个待办事项查看详情")
        self.priority_label.setVisible(False)
        self.content_view.setText("")
        self._clear_tags()

    def _clear_tags(self):
        """Clear all tag widgets"""
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _update_tag_display(self):
        """Update the tag display"""
        self._clear_tags()

        for tag in self._tags:
            tag_label = QLabel(tag.name)
            tag_label.setStyleSheet(f"""
                padding: 4px 10px;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 500;
                background-color: {tag.color};
                color: white;
            """)
            self.tags_layout.addWidget(tag_label)

        self.tags_container.setVisible(len(self._tags) > 0)
