"""Main window for EsTodo"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon
from typing import Optional

from .theme import Theme, get_stylesheet
from .todo_tree import TodoTreeWidget
from .todo_editor import TodoEditor
from ..database import Database
from ..models.todo import TodoModel, Todo


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.todo_model = TodoModel(db)
        self.current_todo: Optional[Todo] = None
        self.current_theme = Theme.LIGHT

        self._setup_ui()
        self._load_todos()
        self._apply_theme()

    def _setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("EsTodo")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 16, 0, 16)

        # Logo / title
        logo_label = QLabel("EsTodo")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 12px 16px;
            color: #4f46e5;
        """)
        sidebar_layout.addWidget(logo_label)

        # Navigation buttons
        self.nav_todos = QPushButton("待办列表")
        self.nav_todos.setObjectName("navButton")
        self.nav_todos.setCheckable(True)
        self.nav_todos.setChecked(True)
        self.nav_todos.clicked.connect(lambda: self._switch_page(0))
        sidebar_layout.addWidget(self.nav_todos)

        self.nav_calendar = QPushButton("番茄日历")
        self.nav_calendar.setObjectName("navButton")
        self.nav_calendar.setCheckable(True)
        self.nav_calendar.clicked.connect(lambda: self._switch_page(1))
        sidebar_layout.addWidget(self.nav_calendar)

        self.nav_stats = QPushButton("统计")
        self.nav_stats.setObjectName("navButton")
        self.nav_stats.setCheckable(True)
        self.nav_stats.clicked.connect(lambda: self._switch_page(2))
        sidebar_layout.addWidget(self.nav_stats)

        self.nav_settings = QPushButton("设置")
        self.nav_settings.setObjectName("navButton")
        self.nav_settings.setCheckable(True)
        self.nav_settings.clicked.connect(lambda: self._switch_page(3))
        sidebar_layout.addWidget(self.nav_settings)

        sidebar_layout.addStretch()

        # Theme toggle button
        self.theme_button = QPushButton("深色")
        self.theme_button.setObjectName("navButton")
        self.theme_button.clicked.connect(self._toggle_theme)
        sidebar_layout.addWidget(self.theme_button)

        main_layout.addWidget(sidebar)

        # Content area
        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Page stack
        self.page_stack = QStackedWidget()

        # Page 0: Todo list (with editor)
        todo_page = QWidget()
        todo_layout = QHBoxLayout(todo_page)
        todo_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.todo_tree = TodoTreeWidget()
        self.todo_tree.todo_selected.connect(self._on_todo_selected)
        self.todo_tree.todo_double_clicked.connect(self._on_todo_double_clicked)
        self.todo_tree.add_button.clicked.connect(self._on_new_todo)
        self.todo_tree.add_child_button.clicked.connect(self._on_new_child_todo)
        self.todo_tree.delete_button.clicked.connect(self._on_delete_todo)
        splitter.addWidget(self.todo_tree)

        self.todo_editor = TodoEditor()
        self.todo_editor.todo_saved.connect(self._on_todo_saved)
        self.todo_editor.todo_deleted.connect(self._on_todo_deleted)
        self.todo_editor.edit_cancelled.connect(self._on_edit_cancelled)
        self.todo_editor.setVisible(False)
        splitter.addWidget(self.todo_editor)

        splitter.setSizes([500, 700])
        todo_layout.addWidget(splitter)

        self.page_stack.addWidget(todo_page)

        # Page 1: Calendar (placeholder)
        calendar_page = QWidget()
        calendar_layout = QVBoxLayout(calendar_page)
        calendar_label = QLabel("番茄日历 - 即将推出")
        calendar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calendar_label.setStyleSheet("font-size: 18px; color: #64748b;")
        calendar_layout.addWidget(calendar_label)
        self.page_stack.addWidget(calendar_page)

        # Page 2: Stats (placeholder)
        stats_page = QWidget()
        stats_layout = QVBoxLayout(stats_page)
        stats_label = QLabel("统计 - 即将推出")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_label.setStyleSheet("font-size: 18px; color: #64748b;")
        stats_layout.addWidget(stats_label)
        self.page_stack.addWidget(stats_page)

        # Page 3: Settings (placeholder)
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_label = QLabel("设置 - 即将推出")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_label.setStyleSheet("font-size: 18px; color: #64748b;")
        settings_layout.addWidget(settings_label)
        self.page_stack.addWidget(settings_page)

        content_layout.addWidget(self.page_stack)
        main_layout.addWidget(content, 1)

        # Menu bar
        self._setup_menu_bar()

    def _setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("文件(&F)")

        new_todo = QAction("新建待办(&N)", self)
        new_todo.setShortcut("Ctrl+N")
        new_todo.triggered.connect(self._on_new_todo)
        file_menu.addAction(new_todo)

        file_menu.addSeparator()

        import_action = QAction("导入(&I)...", self)
        import_action.setEnabled(False)
        file_menu.addAction(import_action)

        export_action = QAction("导出(&E)...", self)
        export_action.setEnabled(False)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("退出(&Q)", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("视图(&V)")

        toggle_theme = QAction("切换主题(&T)", self)
        toggle_theme.triggered.connect(self._toggle_theme)
        view_menu.addAction(toggle_theme)

        # Help menu
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)", self)
        about_action.setEnabled(False)
        help_menu.addAction(about_action)

    def _load_todos(self):
        """Load todos from database"""
        todos = self.todo_model.get_root_todos(include_completed=True)
        self.todo_tree.set_todos(todos)

    def _switch_page(self, index: int):
        """Switch to a page"""
        self.page_stack.setCurrentIndex(index)

        # Update nav buttons
        for i, btn in enumerate([self.nav_todos, self.nav_calendar, self.nav_stats, self.nav_settings]):
            btn.setChecked(i == index)

    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.current_theme == Theme.LIGHT:
            self.current_theme = Theme.DARK
            self.theme_button.setText("浅色")
        else:
            self.current_theme = Theme.LIGHT
            self.theme_button.setText("深色")
        self._apply_theme()

    def _apply_theme(self):
        """Apply the current theme"""
        self.setStyleSheet(get_stylesheet(self.current_theme))

    def _on_todo_selected(self, todo: Optional[Todo]):
        """Handle todo selection"""
        self.current_todo = todo

    def _on_todo_double_clicked(self, todo: Todo):
        """Handle todo double click - open editor"""
        self.todo_editor.set_todo(todo)
        self.todo_editor.setVisible(True)

    def _on_new_todo(self):
        """Create a new todo"""
        new_todo = Todo()
        if self.current_todo and self.current_todo.parent_id is None:
            new_todo.parent_id = None
        elif self.current_todo:
            new_todo.parent_id = self.current_todo.parent_id

        self.todo_editor.set_todo(new_todo)
        self.todo_editor.setVisible(True)
        self.todo_editor.title_input.setFocus()

    def _on_new_child_todo(self):
        """Create a new child todo"""
        if not self.current_todo:
            return

        new_todo = Todo(parent_id=self.current_todo.id)
        self.todo_editor.set_todo(new_todo)
        self.todo_editor.setVisible(True)
        self.todo_editor.title_input.setFocus()

    def _on_delete_todo(self):
        """Delete the selected todo"""
        if not self.current_todo or not self.current_todo.id:
            return

        self.todo_model.delete(self.current_todo.id)
        self.current_todo = None
        self.todo_editor.clear()
        self.todo_editor.setVisible(False)
        self._load_todos()

    def _on_todo_saved(self, todo: Todo):
        """Handle todo saved"""
        if todo.id:
            self.todo_model.update(todo)
        else:
            self.todo_model.create(todo)

        self.current_todo = None
        self.todo_editor.clear()
        self.todo_editor.setVisible(False)
        self._load_todos()

    def _on_todo_deleted(self, todo: Todo):
        """Handle todo deleted from editor"""
        if todo.id:
            self.todo_model.delete(todo.id)

        self.current_todo = None
        self.todo_editor.clear()
        self.todo_editor.setVisible(False)
        self._load_todos()

    def _on_edit_cancelled(self):
        """Handle edit cancelled"""
        self.current_todo = None
        self.todo_editor.clear()
        self.todo_editor.setVisible(False)
