"""Tag selector widget for todo editor"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QScrollArea, QPushButton, QFrame, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List, Set
from ..models.tag import TagModel, Tag


class TagCheckBox(QWidget):
    """Single tag checkbox widget"""

    def __init__(self, tag: Tag, checked: bool = False, parent=None):
        super().__init__(parent)
        self.tag = tag
        self._checked = checked
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Color dot
        color_label = QLabel()
        color_label.setFixedSize(16, 16)
        color_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.tag.color};
                border-radius: 8px;
                border: 2px solid {self._darken_color(self.tag.color)};
            }}
        """)
        layout.addWidget(color_label)

        # Checkbox
        self.checkbox = QCheckBox(self.tag.name)
        self.checkbox.setChecked(self._checked)
        layout.addWidget(self.checkbox)

    def is_checked(self) -> bool:
        """Get checked state"""
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        """Set checked state"""
        self.checkbox.setChecked(checked)

    def _darken_color(self, color_str: str) -> str:
        """Darken a color for border"""
        from PyQt6.QtGui import QColor
        color = QColor(color_str)
        return color.darker(120).name()


class TagSelectorDialog(QDialog):
    """Dialog for selecting tags for a todo"""

    tags_selected = pyqtSignal(list)  # Emits list of tag IDs

    def __init__(self, tag_model: TagModel, selected_tag_ids: Optional[List[int]] = None, parent=None):
        super().__init__(parent)
        self.tag_model = tag_model
        self.selected_tag_ids: Set[int] = set(selected_tag_ids or [])
        self.tag_widgets: List[TagCheckBox] = []
        self._setup_ui()
        self._load_tags()

    def _setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("选择标签")
        self.setMinimumSize(350, 300)
        self.resize(400, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title_label = QLabel("为待办选择标签")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #1e293b;
        """)
        layout.addWidget(title_label)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #e2e8f0;")
        layout.addWidget(divider)

        # Scroll area for tags
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tags_container = QWidget()
        self.tags_layout = QVBoxLayout(self.tags_container)
        self.tags_layout.setSpacing(8)
        self.tags_layout.setContentsMargins(0, 8, 0, 8)

        scroll.setWidget(self.tags_container)
        layout.addWidget(scroll, 1)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        clear_btn = QPushButton("清除全部")
        clear_btn.setObjectName("secondaryButton")
        clear_btn.clicked.connect(self._clear_all)
        button_layout.addWidget(clear_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("primaryButton")
        ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def _load_tags(self):
        """Load tags from database"""
        # Clear existing
        for i in reversed(range(self.tags_layout.count())):
            self.tags_layout.itemAt(i).widget().setParent(None)

        self.tag_widgets = []
        tags = self.tag_model.get_all()

        if not tags:
            empty_label = QLabel("还没有标签，在主界面打开「标签管理」来创建吧！")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setWordWrap(True)
            empty_label.setStyleSheet("color: #94a3b8; padding: 20px;")
            self.tags_layout.addWidget(empty_label)
            self.tags_layout.addStretch()
            return

        for tag in tags:
            checked = tag.id in self.selected_tag_ids
            tag_widget = TagCheckBox(tag, checked)
            self.tag_widgets.append(tag_widget)
            self.tags_layout.addWidget(tag_widget)

        self.tags_layout.addStretch()

    def _clear_all(self):
        """Clear all selections"""
        for widget in self.tag_widgets:
            widget.set_checked(False)

    def _on_ok(self):
        """Handle OK button"""
        selected_ids = [
            w.tag.id for w in self.tag_widgets
            if w.is_checked() and w.tag.id is not None
        ]
        self.tags_selected.emit(selected_ids)
        self.accept()


class TagDisplayWidget(QWidget):
    """Widget for displaying selected tags"""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags: List[Tag] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        self.label = QLabel("标签:")
        self.label.setStyleSheet("color: #64748b;")
        self.layout.addWidget(self.label)

        self.tags_container = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(6)
        self.layout.addWidget(self.tags_container, 1)

        self.edit_btn = QPushButton("选择...")
        self.edit_btn.setObjectName("secondaryButton")
        self.edit_btn.clicked.connect(self.clicked.emit)
        self.layout.addWidget(self.edit_btn)

    def set_tags(self, tags: List[Tag]):
        """Set the tags to display"""
        self.tags = tags
        self._refresh_display()

    def _refresh_display(self):
        """Refresh the tag display"""
        # Clear existing
        for i in reversed(range(self.tags_layout.count())):
            item = self.tags_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
                
        if not self.tags:
            no_label = QLabel("(无标签)")
            no_label.setStyleSheet("color: #94a3b8; font-style: italic;")
            self.tags_layout.addWidget(no_label)
            return

        for tag in self.tags:
            tag_label = QLabel(tag.name)
            tag_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {tag.color};
                    color: white;
                    padding: 4px 10px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 500;
                }}
            """)
            self.tags_layout.addWidget(tag_label)

        self.tags_layout.addStretch()
