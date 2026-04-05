"""Todo tree widget - Windows 11 style"""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QSize
from PyQt6.QtGui import QDrag, QIcon, QColor, QFont
from typing import Optional, List, Any, Set
from ..models.todo import Todo


class TodoTreeItem(QTreeWidgetItem):
    """Custom tree widget item for todos - Windows 11 style"""

    def __init__(self, todo: Todo):
        super().__init__()
        self.todo = todo
        self.update_display()

    def update_display(self):
        """Update the display text - Windows 11 refined"""
        title = self.todo.title
        if not title:
            title = "(无标题)"

        # Add priority indicator in text
        prefix = ""
        if self.todo.priority == 3:  # High
            prefix = "🔴 "
        elif self.todo.priority == 2:  # Medium
            prefix = "🟡 "
        elif self.todo.priority == 1:  # Low
            prefix = "🟢 "

        self.setText(0, prefix + title)

        # Set font strikeout if completed
        font = self.font(0)
        font.setStrikeOut(self.todo.is_completed)
        font.setPointSize(10)
        self.setFont(0, font)

        # Set foreground color - Windows 11 style
        if self.todo.is_completed:
            self.setForeground(0, QColor("#a0a0a0"))
        else:
            self.setForeground(0, QColor("#000000"))


class TodoTreeWidget(QWidget):
    """Todo tree widget with smooth scrolling - Windows 11 style"""

    todo_selected = pyqtSignal(object)  # Emits Todo or None
    todo_double_clicked = pyqtSignal(object)  # Emits Todo
    start_pomodoro_for_todo = pyqtSignal(object)  # Emits Todo
    new_todo_requested = pyqtSignal()  # Request new todo
    new_child_todo_requested = pyqtSignal(object)  # Request new child todo for parent
    todo_toggle_completed = pyqtSignal(object)  # Toggle todo completion
    todo_delete_requested = pyqtSignal(object)  # Request todo deletion

    def __init__(self, parent=None):
        super().__init__(parent)
        self.todos: List[Todo] = []
        self._expanded_ids: Set[int] = set()  # Store expanded todo IDs
        self._selected_todo_id: Optional[int] = None  # Store selected todo ID
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI - Windows 11 refined layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header with buttons - Windows 11 style
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title_label = QLabel("待办事项")
        title_label.setObjectName("headerLabel")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            padding: 8px 0px;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.add_button = QPushButton("+ 新建")
        self.add_button.setObjectName("primaryButton")
        self.add_button.setMinimumHeight(36)
        header_layout.addWidget(self.add_button)

        self.add_child_button = QPushButton("+ 子待办")
        self.add_child_button.setObjectName("secondaryButton")
        self.add_child_button.setMinimumHeight(36)
        header_layout.addWidget(self.add_child_button)

        self.delete_button = QPushButton("删除")
        self.delete_button.setObjectName("secondaryButton")
        self.delete_button.setMinimumHeight(36)
        header_layout.addWidget(self.delete_button)

        layout.addLayout(header_layout)

        # Tree widget - Windows 11 style with smooth scrolling
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.setAnimated(True)
        self.tree.setIndentation(28)
        self.tree.setUniformRowHeights(True)  # Performance optimization
        self.tree.setWordWrap(False)
        self.tree.setRootIsDecorated(True)  # Enable native branch indicators

        # Smooth scrolling optimization
        self.tree.setVerticalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self.tree.setHorizontalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)

        # Connect signals
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemDoubleClicked.connect(self._on_double_clicked)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.itemExpanded.connect(self._on_item_expanded)
        self.tree.itemCollapsed.connect(self._on_item_collapsed)

        layout.addWidget(self.tree, 1)

    def set_todos(self, todos: List[Todo]):
        """Set the todos to display"""
        self._save_state()  # Save current state before refreshing
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

    def _save_state(self):
        """Save current expansion and selection state"""
        self._expanded_ids.clear()
        self._selected_todo_id = None

        # Save expanded items
        def save_expanded(item):
            if isinstance(item, TodoTreeItem) and item.isExpanded() and item.todo.id:
                self._expanded_ids.add(item.todo.id)
            for i in range(item.childCount()):
                save_expanded(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            save_expanded(self.tree.topLevelItem(i))

        # Save selected item
        selected = self.get_selected_todo()
        if selected and selected.id:
            self._selected_todo_id = selected.id

    def _restore_state(self):
        """Restore expansion and selection state"""
        item_to_select = None

        # Restore expanded items and find item to select
        def restore_item(item):
            nonlocal item_to_select
            if isinstance(item, TodoTreeItem):
                if item.todo.id in self._expanded_ids:
                    item.setExpanded(True)
                if item.todo.id == self._selected_todo_id:
                    item_to_select = item
            for i in range(item.childCount()):
                restore_item(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            restore_item(self.tree.topLevelItem(i))

        # Restore selection
        if item_to_select:
            self.tree.setCurrentItem(item_to_select)

    def _refresh_tree(self):
        """Refresh the tree display - optimized for performance"""
        # Disable updates during refresh for smoother performance
        self.tree.setUpdatesEnabled(False)
        try:
            self.tree.clear()

            for todo in self.todos:
                item = self._create_tree_item(todo)
                self.tree.addTopLevelItem(item)
                self._add_children(item, todo.children)

            # Restore previous state
            self._restore_state()
        finally:
            self.tree.setUpdatesEnabled(True)

    def _on_item_expanded(self, item):
        """Handle item expanded - save to state"""
        if isinstance(item, TodoTreeItem) and item.todo.id:
            self._expanded_ids.add(item.todo.id)

    def _on_item_collapsed(self, item):
        """Handle item collapsed - remove from state"""
        if isinstance(item, TodoTreeItem) and item.todo.id:
            self._expanded_ids.discard(item.todo.id)

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
        """Show context menu - Windows 11 style"""
        item = self.tree.itemAt(position)
        if not item:
            return

        # Select the item under cursor
        self.tree.setCurrentItem(item)

        menu = QMenu(self)

        # Windows 11 style menu styling
        menu.setStyleSheet("""
            QMenu {
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px 8px 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #f1f1f1;
            }
        """)

        add_action = menu.addAction("新建待办")
        add_child_action = menu.addAction("新建子待办")
        menu.addSeparator()
        pomodoro_action = menu.addAction("🍅 开始番茄钟")
        menu.addSeparator()
        edit_action = menu.addAction("编辑")
        toggle_action = menu.addAction("标记完成" if not item.todo.is_completed else "标记未完成")
        menu.addSeparator()
        delete_action = menu.addAction("删除")

        action = menu.exec(self.tree.viewport().mapToGlobal(position))

        if action == add_action:
            self.new_todo_requested.emit()
        elif action == add_child_action:
            self.new_child_todo_requested.emit(item.todo)
        elif action == pomodoro_action:
            self.start_pomodoro_for_todo.emit(item.todo)
        elif action == edit_action:
            self.todo_double_clicked.emit(item.todo)
        elif action == toggle_action:
            self.todo_toggle_completed.emit(item.todo)
        elif action == delete_action:
            self.todo_delete_requested.emit(item.todo)
