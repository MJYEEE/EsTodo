"""Todo tree widget"""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QIcon, QColor
from typing import Optional, List, Any
from ..models.todo import Todo


class TodoTreeItem(QTreeWidgetItem):
    """Custom tree widget item for todos"""

    def __init__(self, todo: Todo):
        super().__init__()
        self.todo = todo
        self.update_display()

    def update_display(self):
        """Update the display text"""
        title = self.todo.title
        if not title:
            title = "(无标题)"

        self.setText(0, title)

        # Set font strikeout if completed
        font = self.font(0)
        font.setStrikeOut(self.todo.is_completed)
        self.setFont(0, font)

        # Set foreground color
        if self.todo.is_completed:
            self.setForeground(0, QColor("#94a3b8"))
        else:
            self.setForeground(0, QColor("#1e293b"))

        # Add priority indicator
        if self.todo.priority == 3:  # High
            self.setIcon(0, QIcon.fromTheme("emblem-important"))
        elif self.todo.priority == 2:  # Medium
            self.setIcon(0, QIcon())
        else:  # Low
            self.setIcon(0, QIcon())


class TodoTreeWidget(QWidget):
    """Todo tree widget with drag and drop support"""

    todo_selected = pyqtSignal(object)  # Emits Todo or None
    todo_double_clicked = pyqtSignal(object)  # Emits Todo

    def __init__(self, parent=None):
        super().__init__(parent)
        self.todos: List[Todo] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header with buttons
        header_layout = QHBoxLayout()

        title_label = QLabel("待办事项")
        title_label.setObjectName("headerLabel")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.add_button = QPushButton("+ 新建")
        self.add_button.setObjectName("primaryButton")
        header_layout.addWidget(self.add_button)

        self.add_child_button = QPushButton("+ 子待办")
        self.add_child_button.setObjectName("secondaryButton")
        header_layout.addWidget(self.add_child_button)

        self.delete_button = QPushButton("删除")
        self.delete_button.setObjectName("dangerButton")
        header_layout.addWidget(self.delete_button)

        layout.addLayout(header_layout)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)

        # Connect signals
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemDoubleClicked.connect(self._on_double_clicked)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.tree)

    def set_todos(self, todos: List[Todo]):
        """Set the todos to display"""
        self.todos = todos
        self._refresh_tree()

    def get_selected_todo(self) -> Optional[Todo]:
        """Get the currently selected todo"""
        items = self.tree.selectedItems()
        if items:
            return items[0].todo
        return None

    def expand_all(self):
        """Expand all items"""
        self.tree.expandAll()

    def collapse_all(self):
        """Collapse all items"""
        self.tree.collapseAll()

    def _refresh_tree(self):
        """Refresh the tree display"""
        self.tree.clear()

        for todo in self.todos:
            item = self._create_tree_item(todo)
            self.tree.addTopLevelItem(item)
            self._add_children(item, todo.children)

    def _create_tree_item(self, todo: Todo) -> TodoTreeItem:
        """Create a tree item for a todo"""
        return TodoTreeItem(todo)

    def _add_children(self, parent_item: QTreeWidgetItem, children: List[Todo]):
        """Add child todos to a tree item"""
        for child in children:
            item = self._create_tree_item(child)
            parent_item.addChild(item)
            self._add_children(item, child.children)

    def _on_selection_changed(self):
        """Handle selection change"""
        todo = self.get_selected_todo()
        self.todo_selected.emit(todo)

    def _on_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double click"""
        if isinstance(item, TodoTreeItem):
            self.todo_double_clicked.emit(item.todo)

    def _show_context_menu(self, position):
        """Show context menu"""
        item = self.tree.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        add_action = menu.addAction("新建待办")
        add_child_action = menu.addAction("新建子待办")
        menu.addSeparator()
        edit_action = menu.addAction("编辑")
        toggle_action = menu.addAction("标记完成" if not item.todo.is_completed else "标记未完成")
        menu.addSeparator()
        delete_action = menu.addAction("删除")

        action = menu.exec(self.tree.viewport().mapToGlobal(position))

        if action == add_action:
            # TODO: Emit signal
            pass
        elif action == add_child_action:
            # TODO: Emit signal
            pass
        elif action == edit_action:
            self.todo_double_clicked.emit(item.todo)
        elif action == toggle_action:
            # TODO: Emit signal
            pass
        elif action == delete_action:
            # TODO: Emit signal
            pass
