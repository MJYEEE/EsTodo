"""Tag management dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QInputDialog, QColorDialog, QMessageBox, QFrame, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, List
from ..models.tag import TagModel, Tag


class TagItemWidget(QWidget):
    """Widget for displaying a single tag in the list"""

    edit_requested = pyqtSignal(object)  # Emits Tag
    delete_requested = pyqtSignal(object)  # Emits Tag

    def __init__(self, tag: Tag, parent=None):
        super().__init__(parent)
        self.tag = tag
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Color dot
        color_label = QLabel()
        color_label.setFixedSize(20, 20)
        color_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.tag.color};
                border-radius: 10px;
                border: 2px solid {QColor(self.tag.color).darker(120).name()};
            }}
        """)
        layout.addWidget(color_label)

        # Tag name
        name_label = QLabel(self.tag.name)
        name_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 500;
            color: #1e293b;
        """)
        layout.addWidget(name_label, 1)

        # Edit button
        edit_btn = QPushButton("编辑")
        edit_btn.setObjectName("secondaryButton")
        edit_btn.setMaximumWidth(60)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.tag))
        layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton("删除")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMaximumWidth(60)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.tag))
        layout.addWidget(delete_btn)


class TagManagerDialog(QDialog):
    """Dialog for managing tags"""

    tag_changed = pyqtSignal()  # Emitted when tags are added/edited/deleted

    def __init__(self, tag_model: TagModel, parent=None):
        super().__init__(parent)
        self.tag_model = tag_model
        self.tags: List[Tag] = []
        self._setup_ui()
        self._load_tags()

    def _setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("标签管理")
        self.setMinimumSize(450, 400)
        self.resize(500, 500)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("标签管理")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #1e293b;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        add_btn = QPushButton("+ 新建标签")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self._add_tag)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #e2e8f0;")
        layout.addWidget(divider)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #e2e8f0;
                background-color: #ffffff;
                border-radius: 12px;
                padding: 8px;
            }
            QListWidget::item {
                border-bottom: 1px solid #f1f5f9;
                border-radius: 8px;
                margin: 4px 0;
            }
            QListWidget::item:last {
                border-bottom: none;
            }
            QListWidget::item:hover {
                background-color: #f8fafc;
            }
        """)
        layout.addWidget(self.list_widget, 1)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setObjectName("secondaryButton")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _load_tags(self):
        """Load tags from database"""
        self.tags = self.tag_model.get_all()
        self._refresh_list()

    def _refresh_list(self):
        """Refresh the tag list"""
        self.list_widget.clear()

        for tag in self.tags:
            item_widget = TagItemWidget(tag)
            item_widget.edit_requested.connect(self._edit_tag)
            item_widget.delete_requested.connect(self._delete_tag)

            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

        if not self.tags:
            empty_label = QLabel("还没有标签，点击「新建标签」来创建吧！")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #94a3b8; padding: 40px;")
            item = QListWidgetItem()
            item.setSizeHint(empty_label.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, empty_label)

    def _add_tag(self):
        """Add a new tag"""
        # Ask for tag name
        name, ok = QInputDialog.getText(self, "新建标签", "请输入标签名称:")
        if not ok or not name.strip():
            return

        name = name.strip()

        # Check if tag already exists
        existing = self.tag_model.get_by_name(name)
        if existing:
            QMessageBox.warning(self, "提示", f"标签「{name}」已经存在！")
            return

        # Ask for color
        color = QColorDialog.getColor(QColor("#6366f1"), self, "选择标签颜色")
        if not color.isValid():
            color = QColor("#6366f1")

        # Create tag
        tag = Tag(name=name, color=color.name())
        self.tag_model.create(tag)

        self._load_tags()
        self.tag_changed.emit()

    def _edit_tag(self, tag: Tag):
        """Edit a tag"""
        # Ask for new name
        name, ok = QInputDialog.getText(
            self, "编辑标签",
            "请输入新的标签名称:",
            text=tag.name
        )
        if not ok or not name.strip():
            return

        name = name.strip()

        # Check if name is taken by another tag
        existing = self.tag_model.get_by_name(name)
        if existing and existing.id != tag.id:
            QMessageBox.warning(self, "提示", f"标签「{name}」已经存在！")
            return

        # Ask for color
        color = QColorDialog.getColor(QColor(tag.color), self, "选择标签颜色")
        if not color.isValid():
            color = QColor(tag.color)

        # Update tag
        tag.name = name
        tag.color = color.name()
        self.tag_model.update(tag)

        self._load_tags()
        self.tag_changed.emit()

    def _delete_tag(self, tag: Tag):
        """Delete a tag"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除标签「{tag.name}」吗？\n\n这不会影响已关联的待办事项。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.tag_model.delete(tag.id)
            self._load_tags()
            self.tag_changed.emit()
