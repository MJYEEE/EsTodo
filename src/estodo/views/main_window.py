"""Main window for EsTodo"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSplitter, QFrame,
    QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QAction, QIcon
from typing import Optional
from datetime import datetime, timedelta

from .theme import Theme, get_stylesheet
from .todo_tree import TodoTreeWidget
from .todo_editor import TodoEditor
from .pomodoro_timer import PomodoroTimerWidget
from .notifications import notify
from ..database import Database
from ..models.todo import TodoModel, Todo
from ..models.pomodoro import PomodoroModel, Pomodoro


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.todo_model = TodoModel(db)
        self.pomodoro_model = PomodoroModel(db)
        self.current_todo: Optional[Todo] = None
        self.current_theme = Theme.LIGHT
        self.pomodoro_widget: Optional[PomodoroTimerWidget] = None

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

        self.nav_pomodoro = QPushButton("番茄钟")
        self.nav_pomodoro.setObjectName("navButton")
        self.nav_pomodoro.setCheckable(True)
        self.nav_pomodoro.clicked.connect(lambda: self._switch_page(1))
        sidebar_layout.addWidget(self.nav_pomodoro)

        self.nav_calendar = QPushButton("番茄日历")
        self.nav_calendar.setObjectName("navButton")
        self.nav_calendar.setCheckable(True)
        self.nav_calendar.clicked.connect(lambda: self._switch_page(2))
        sidebar_layout.addWidget(self.nav_calendar)

        self.nav_stats = QPushButton("统计")
        self.nav_stats.setObjectName("navButton")
        self.nav_stats.setCheckable(True)
        self.nav_stats.clicked.connect(lambda: self._switch_page(3))
        sidebar_layout.addWidget(self.nav_stats)

        self.nav_settings = QPushButton("设置")
        self.nav_settings.setObjectName("navButton")
        self.nav_settings.setCheckable(True)
        self.nav_settings.clicked.connect(lambda: self._switch_page(4))
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
        self.todo_tree.start_pomodoro_for_todo.connect(self._start_pomodoro_for_todo)
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

        # Page 1: Pomodoro Timer
        pomodoro_page = QWidget()
        pomodoro_layout = QVBoxLayout(pomodoro_page)
        pomodoro_layout.setContentsMargins(32, 32, 32, 32)

        # Create pomodoro widget
        self.pomodoro_widget = PomodoroTimerWidget()
        self.pomodoro_widget.timer_started.connect(self._on_pomodoro_started)
        self.pomodoro_widget.timer_paused.connect(self._on_pomodoro_paused)
        self.pomodoro_widget.timer_resumed.connect(self._on_pomodoro_resumed)
        self.pomodoro_widget.timer_stopped.connect(self._on_pomodoro_stopped)
        self.pomodoro_widget.timer_completed.connect(self._on_pomodoro_completed)

        # Center the pomodoro widget
        pomodoro_layout.addStretch()
        pomodoro_layout.addWidget(self.pomodoro_widget, 0, Qt.AlignmentFlag.AlignCenter)
        pomodoro_layout.addStretch()

        self.page_stack.addWidget(pomodoro_page)

        # Update initial count
        self._update_pomodoro_count()

        # Page 2: Calendar (placeholder)
        calendar_page = QWidget()
        calendar_layout = QVBoxLayout(calendar_page)
        calendar_label = QLabel("番茄日历 - 即将推出")
        calendar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calendar_label.setStyleSheet("font-size: 18px; color: #64748b;")
        calendar_layout.addWidget(calendar_label)
        self.page_stack.addWidget(calendar_page)

        # Page 3: Stats (placeholder)
        stats_page = QWidget()
        stats_layout = QVBoxLayout(stats_page)
        stats_label = QLabel("统计 - 即将推出")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_label.setStyleSheet("font-size: 18px; color: #64748b;")
        stats_layout.addWidget(stats_label)
        self.page_stack.addWidget(stats_page)

        # Page 4: Settings (placeholder)
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

        start_pomodoro = QAction("启动番茄钟(&P)", self)
        start_pomodoro.setShortcut("Ctrl+P")
        start_pomodoro.triggered.connect(self._toggle_pomodoro_window)
        file_menu.addAction(start_pomodoro)

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
        for i, btn in enumerate([self.nav_todos, self.nav_pomodoro, self.nav_calendar, self.nav_stats, self.nav_settings]):
            btn.setChecked(i == index)

    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.current_theme == Theme.LIGHT:
            self.current_theme = Theme.DARK
            self.theme_button.setText("浅色")
            if self.pomodoro_widget:
                self.pomodoro_widget.set_dark_mode(True)
        else:
            self.current_theme = Theme.LIGHT
            self.theme_button.setText("深色")
            if self.pomodoro_widget:
                self.pomodoro_widget.set_dark_mode(False)
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

    def _toggle_pomodoro_window(self):
        """Toggle pomodoro timer page"""
        self._switch_page(1)

    def _start_pomodoro_for_todo(self, todo: Todo):
        """Start pomodoro timer linked to a todo"""
        if self.pomodoro_widget:
            self.pomodoro_widget.link_to_todo(todo.id, todo.title)
            self._switch_page(1)

    def _on_pomodoro_started(self, pomodoro: Pomodoro):
        """Handle pomodoro started"""
        if pomodoro.id is None:
            self.pomodoro_model.create(pomodoro)

    def _on_pomodoro_paused(self, pomodoro: Pomodoro):
        """Handle pomodoro paused"""
        pass

    def _on_pomodoro_resumed(self, pomodoro: Pomodoro):
        """Handle pomodoro resumed"""
        pass

    def _on_pomodoro_stopped(self, pomodoro: Pomodoro):
        """Handle pomodoro stopped"""
        if pomodoro.id:
            self.pomodoro_model.update(pomodoro)

    def _on_pomodoro_completed(self, pomodoro: Pomodoro):
        """Handle pomodoro completed"""
        if pomodoro.id:
            self.pomodoro_model.update(pomodoro)

        # Show notification
        notify("番茄钟完成！", "休息一下吧，你做得很棒！")

        # Show in-app message box - always on top
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("番茄钟完成！")
        msg_box.setText("恭喜！番茄钟完成啦！")
        msg_box.setInformativeText("休息一下吧，你做得很棒！")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        # Set window flags to stay on top
        msg_box.setWindowFlags(
            msg_box.windowFlags() |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Dialog
        )
        msg_box.exec()

        # Update count
        self._update_pomodoro_count()

    def _update_pomodoro_count(self):
        """Update today's pomodoro count"""
        if self.pomodoro_widget:
            today = datetime.now().date()
            start = datetime.combine(today, datetime.min.time())
            end = start + timedelta(days=1)
            pomodoros = self.pomodoro_model.get_by_date_range(start, end)
            completed = [p for p in pomodoros if p.is_completed]
            self.pomodoro_widget.update_today_count(len(completed))
