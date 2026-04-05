"""Main window for EsTodo"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSplitter, QFrame,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QAction, QIcon
from typing import Optional
from datetime import datetime, timedelta

from .theme import Theme, get_stylesheet
from .todo_tree import TodoTreeWidget
from .todo_editor import TodoEditor
from .pomodoro_timer import PomodoroTimerWidget
from .heatmap import HeatmapCalendar
from .day_detail_dialog import DayDetailDialog
from .tag_dialog import TagManagerDialog
from .notifications import notify
from ..database import Database
from ..models.todo import TodoModel, Todo
from ..models.pomodoro import PomodoroModel, Pomodoro
from ..models.tag import TagModel, Tag
from ..import_export import ImportExport


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.todo_model = TodoModel(db)
        self.pomodoro_model = PomodoroModel(db)
        self.tag_model = TagModel(db)
        self.import_export = ImportExport(db)
        self.current_todo: Optional[Todo] = None
        self.current_theme = Theme.LIGHT
        self.pomodoro_widget: Optional[PomodoroTimerWidget] = None

        self._setup_ui()
        self._load_todos()
        self._apply_theme()

    def _setup_ui(self):
        """Setup the UI - Windows 11 refined layout"""
        self.setWindowTitle("EsTodo")
        self.setMinimumSize(1100, 750)
        self.resize(1280, 850)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar - Windows 11 style with more padding
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(4)

        # Logo / title - Windows 11 style
        logo_label = QLabel("EsTodo")
        logo_label.setObjectName("headerLabel")
        logo_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            padding: 16px 20px 20px 20px;
        """)
        sidebar_layout.addWidget(logo_label)

        # Navigation buttons with icons (text-based for simplicity)
        self.nav_todos = QPushButton("✓  待办列表")
        self.nav_todos.setObjectName("navButton")
        self.nav_todos.setCheckable(True)
        self.nav_todos.setChecked(True)
        self.nav_todos.clicked.connect(lambda: self._switch_page(0))
        sidebar_layout.addWidget(self.nav_todos)

        self.nav_pomodoro = QPushButton("🍅  番茄钟")
        self.nav_pomodoro.setObjectName("navButton")
        self.nav_pomodoro.setCheckable(True)
        self.nav_pomodoro.clicked.connect(lambda: self._switch_page(1))
        sidebar_layout.addWidget(self.nav_pomodoro)

        self.nav_calendar = QPushButton("📅  番茄日历")
        self.nav_calendar.setObjectName("navButton")
        self.nav_calendar.setCheckable(True)
        self.nav_calendar.clicked.connect(lambda: self._switch_page(2))
        sidebar_layout.addWidget(self.nav_calendar)

        self.nav_stats = QPushButton("📊  统计")
        self.nav_stats.setObjectName("navButton")
        self.nav_stats.setCheckable(True)
        self.nav_stats.clicked.connect(lambda: self._switch_page(3))
        sidebar_layout.addWidget(self.nav_stats)

        self.nav_settings = QPushButton("⚙️  设置")
        self.nav_settings.setObjectName("navButton")
        self.nav_settings.setCheckable(True)
        self.nav_settings.clicked.connect(lambda: self._switch_page(4))
        sidebar_layout.addWidget(self.nav_settings)

        sidebar_layout.addSpacing(8)
        sidebar_layout.addStretch()

        # Theme toggle button - more prominent
        theme_container = QWidget()
        theme_container.setContentsMargins(12, 0, 12, 0)
        theme_layout = QVBoxLayout(theme_container)
        theme_layout.setContentsMargins(0, 0, 0, 0)

        self.theme_button = QPushButton("🌙  深色模式")
        self.theme_button.setObjectName("secondaryButton")
        self.theme_button.setMinimumHeight(40)
        self.theme_button.clicked.connect(self._toggle_theme)
        theme_layout.addWidget(self.theme_button)

        sidebar_layout.addWidget(theme_container)

        main_layout.addWidget(sidebar)

        # Content area - Windows 11 style with more padding
        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Page stack
        self.page_stack = QStackedWidget()
        self.page_stack.setContentsMargins(0, 0, 0, 0)

        # Page 0: Todo list (with editor)
        todo_page = QWidget()
        todo_layout = QHBoxLayout(todo_page)
        todo_layout.setContentsMargins(12, 12, 12, 12)
        todo_layout.setSpacing(12)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(12)
        splitter.setChildrenCollapsible(False)

        self.todo_tree = TodoTreeWidget()
        self.todo_tree.todo_selected.connect(self._on_todo_selected)
        self.todo_tree.todo_double_clicked.connect(self._on_todo_double_clicked)
        self.todo_tree.add_button.clicked.connect(self._on_new_todo)
        self.todo_tree.add_child_button.clicked.connect(self._on_new_child_todo)
        self.todo_tree.delete_button.clicked.connect(self._on_delete_todo)
        self.todo_tree.start_pomodoro_for_todo.connect(self._start_pomodoro_for_todo)
        self.todo_tree.new_todo_requested.connect(self._on_new_todo)
        self.todo_tree.new_child_todo_requested.connect(self._on_new_child_todo_from_menu)
        self.todo_tree.todo_toggle_completed.connect(self._on_toggle_todo_completed)
        self.todo_tree.todo_delete_requested.connect(self._on_delete_todo_from_menu)
        splitter.addWidget(self.todo_tree)

        self.todo_editor = TodoEditor(self.tag_model)
        self.todo_editor.todo_saved.connect(self._on_todo_saved)
        self.todo_editor.todo_deleted.connect(self._on_todo_deleted)
        self.todo_editor.edit_cancelled.connect(self._on_edit_cancelled)
        self.todo_editor.setVisible(False)
        splitter.addWidget(self.todo_editor)

        splitter.setSizes([520, 720])
        todo_layout.addWidget(splitter)

        self.page_stack.addWidget(todo_page)

        # Page 1: Pomodoro Timer - with generous padding
        pomodoro_page = QWidget()
        pomodoro_layout = QVBoxLayout(pomodoro_page)
        pomodoro_layout.setContentsMargins(40, 40, 40, 40)

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

        # Page 2: Calendar heatmap - Windows 11 style
        calendar_page = QWidget()
        calendar_layout = QVBoxLayout(calendar_page)
        calendar_layout.setContentsMargins(24, 24, 24, 24)
        calendar_layout.setSpacing(20)

        # Header
        calendar_header = QLabel("番茄日历")
        calendar_header.setObjectName("headerLabel")
        calendar_layout.addWidget(calendar_header)

        # Create heatmap in a card container
        heatmap_container = QWidget()
        heatmap_container.setObjectName("card")
        heatmap_layout = QVBoxLayout(heatmap_container)
        heatmap_layout.setContentsMargins(20, 20, 20, 20)

        self.heatmap = HeatmapCalendar()
        self.heatmap.date_clicked.connect(self._on_date_clicked)
        heatmap_layout.addWidget(self.heatmap)

        calendar_layout.addWidget(heatmap_container, 1)

        self.page_stack.addWidget(calendar_page)

        # Load initial heatmap data
        self._update_heatmap()

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
        import_action.triggered.connect(self._import_data)
        file_menu.addAction(import_action)

        export_action = QAction("导出(&E)...", self)
        export_action.triggered.connect(self._export_data)
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

        # Manage menu
        manage_menu = menubar.addMenu("管理(&M)")

        manage_tags = QAction("标签管理(&G)...", self)
        manage_tags.triggered.connect(self._open_tag_manager)
        manage_menu.addAction(manage_tags)

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
            self.theme_button.setText("☀️  浅色模式")
            if self.pomodoro_widget:
                self.pomodoro_widget.set_dark_mode(True)
        else:
            self.current_theme = Theme.LIGHT
            self.theme_button.setText("🌙  深色模式")
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

        # Save tags
        if todo.id:
            self.tag_model.set_todo_tags(todo.id, self.todo_editor.selected_tag_ids)

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

    def _on_new_child_todo_from_menu(self, parent_todo: Todo):
        """Create a new child todo from context menu"""
        self.current_todo = parent_todo
        new_todo = Todo(parent_id=parent_todo.id)
        self.todo_editor.set_todo(new_todo)
        self.todo_editor.setVisible(True)
        self.todo_editor.title_input.setFocus()

    def _on_toggle_todo_completed(self, todo: Todo):
        """Toggle todo completion status"""
        todo.is_completed = not todo.is_completed
        if todo.id:
            self.todo_model.update(todo)
        self._load_todos()

    def _on_delete_todo_from_menu(self, todo: Todo):
        """Delete todo from context menu"""
        if not todo or not todo.id:
            return

        self.todo_model.delete(todo.id)
        if self.current_todo and self.current_todo.id == todo.id:
            self.current_todo = None
            self.todo_editor.clear()
            self.todo_editor.setVisible(False)
        self._load_todos()

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

        # Also update heatmap when pomodoro count changes
        self._update_heatmap()

    def _update_heatmap(self):
        """Update the heatmap with daily counts"""
        if hasattr(self, 'heatmap'):
            daily_counts = self.pomodoro_model.get_daily_counts(365)
            self.heatmap.set_daily_counts(daily_counts)

    def _on_date_clicked(self, date: QDate):
        """Handle date click in heatmap"""
        dialog = DayDetailDialog(date, self.pomodoro_model, self.todo_model, self)
        dialog.exec()

    def _open_tag_manager(self):
        """Open tag manager dialog"""
        dialog = TagManagerDialog(self.tag_model, self)
        dialog.tag_changed.connect(self._on_tags_changed)
        dialog.exec()

    def _on_tags_changed(self):
        """Handle tags changed"""
        # Refresh the todo editor if it's open and has a todo
        if self.todo_editor.isVisible() and self.todo_editor.todo and self.todo_editor.todo.id:
            # Reload tags for the current todo
            self.todo_editor.selected_tag_ids = [
                t.id for t in self.tag_model.get_by_todo_id(self.todo_editor.todo.id)
                if t.id
            ]
            self.todo_editor._update_tag_display()

    def _export_data(self):
        """Export data to JSON file"""
        # Get default filename
        from datetime import datetime
        default_name = f"estodo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            default_name,
            "JSON 文件 (*.json);;所有文件 (*)"
        )

        if not file_path:
            return

        try:
            from pathlib import Path
            self.import_export.export_all(Path(file_path))
            QMessageBox.information(
                self,
                "导出成功",
                f"数据已成功导出到：\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "导出失败",
                f"导出时出错：\n{str(e)}"
            )

    def _import_data(self):
        """Import data from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入数据",
            "",
            "JSON 文件 (*.json);;所有文件 (*)"
        )

        if not file_path:
            return

        # Ask whether to replace or merge
        reply = QMessageBox.question(
            self,
            "导入选项",
            "是否替换现有数据？\n\n"
            "「是」 - 删除所有现有数据，然后导入\n"
            "「否」 - 保留现有数据，合并导入（可能重复）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return

        replace = (reply == QMessageBox.StandardButton.Yes)

        try:
            from pathlib import Path
            counts = self.import_export.import_all(Path(file_path), replace=replace)

            # Refresh UI
            self._load_todos()
            self._update_heatmap()

            QMessageBox.information(
                self,
                "导入成功",
                f"数据已成功导入！\n\n"
                f"标签：{counts['tags']} 个\n"
                f"待办：{counts['todos']} 个\n"
                f"番茄钟：{counts['pomodoros']} 个"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "导入失败",
                f"导入时出错：\n{str(e)}"
            )
