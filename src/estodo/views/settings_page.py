"""Settings page widget - Windows 11 style"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QSpinBox, QComboBox, QCheckBox,
    QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, Callable
from ..database import Database


class SettingsNavButton(QPushButton):
    """Settings navigation button"""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setObjectName("settingsNavButton")
        self.setMinimumHeight(44)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px 16px;
                border: none;
                border-radius: 8px;
                background-color: transparent;
                color: #333;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f1f1f1;
            }
            QPushButton:checked {
                background-color: #e8e8e8;
                font-weight: 600;
            }
        """)


class SettingsCard(QWidget):
    """Settings card container - Windows 11 style"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._setup_ui(title)

    def _setup_ui(self, title: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(12)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #333;
            padding: 4px 0;
        """)
        layout.addWidget(title_label)

        # Card container
        self.card = QWidget()
        self.card.setObjectName("settingsCard")
        self.card.setStyleSheet("""
            QWidget#settingsCard {
                background-color: white;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(20, 20, 20, 20)
        self.card_layout.setSpacing(16)
        layout.addWidget(self.card)

    def add_row(self, label: str, widget: QWidget):
        """Add a row to the card"""
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #333; font-size: 14px;")
        row_layout.addWidget(label_widget)
        row_layout.addStretch()
        row_layout.addWidget(widget)

        self.card_layout.addLayout(row_layout)

    def add_widget(self, widget: QWidget):
        """Add a widget directly to the card"""
        self.card_layout.addWidget(widget)


class PomodoroSettingsWidget(QWidget):
    """Pomodoro settings widget"""

    setting_changed = pyqtSignal(str, str)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Timing card
        timing_card = SettingsCard("计时设置")

        # Work duration
        self.work_spin = QSpinBox()
        self.work_spin.setRange(5, 90)
        self.work_spin.setSuffix(" 分钟")
        self.work_spin.setMinimumWidth(120)
        self.work_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("pomodoro_work_duration", str(v))
        )
        timing_card.add_row("工作时长", self.work_spin)

        # Short break
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 30)
        self.short_break_spin.setSuffix(" 分钟")
        self.short_break_spin.setMinimumWidth(120)
        self.short_break_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("pomodoro_short_break", str(v))
        )
        timing_card.add_row("短休息", self.short_break_spin)

        # Long break
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(5, 60)
        self.long_break_spin.setSuffix(" 分钟")
        self.long_break_spin.setMinimumWidth(120)
        self.long_break_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("pomodoro_long_break", str(v))
        )
        timing_card.add_row("长休息", self.long_break_spin)

        # Long break after
        self.long_break_after_spin = QSpinBox()
        self.long_break_after_spin.setRange(1, 10)
        self.long_break_after_spin.setSuffix(" 次")
        self.long_break_after_spin.setMinimumWidth(120)
        self.long_break_after_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("pomodoro_long_break_after", str(v))
        )
        timing_card.add_row("长休息间隔", self.long_break_after_spin)

        layout.addWidget(timing_card)
        layout.addStretch()

    def _load_settings(self):
        """Load settings from database"""
        self.work_spin.setValue(int(self.db.get_setting("pomodoro_work_duration", "25")))
        self.short_break_spin.setValue(int(self.db.get_setting("pomodoro_short_break", "5")))
        self.long_break_spin.setValue(int(self.db.get_setting("pomodoro_long_break", "15")))
        self.long_break_after_spin.setValue(int(self.db.get_setting("pomodoro_long_break_after", "4")))

    def _on_setting_changed(self, key: str, value: str):
        """Handle setting change"""
        self.db.set_setting(key, value)
        self.setting_changed.emit(key, value)


class AppearanceSettingsWidget(QWidget):
    """Appearance settings widget"""

    setting_changed = pyqtSignal(str, str)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Theme card
        theme_card = SettingsCard("主题设置")

        # Theme combo
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色模式", "深色模式"])
        self.theme_combo.setMinimumWidth(150)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_card.add_row("应用主题", self.theme_combo)

        layout.addWidget(theme_card)
        layout.addStretch()

    def _load_settings(self):
        """Load settings from database"""
        theme = self.db.get_setting("theme", "light")
        self.theme_combo.setCurrentIndex(0 if theme == "light" else 1)

    def _on_theme_changed(self, index: int):
        """Handle theme change"""
        theme = "light" if index == 0 else "dark"
        self.db.set_setting("theme", theme)
        self.setting_changed.emit("theme", theme)


class SystemSettingsWidget(QWidget):
    """System settings widget"""

    setting_changed = pyqtSignal(str, str)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Behavior card
        behavior_card = SettingsCard("窗口行为")

        # Close action combo
        self.close_action_combo = QComboBox()
        self.close_action_combo.addItems([
            "每次询问我",
            "最小化到托盘",
            "直接退出应用"
        ])
        self.close_action_combo.setMinimumWidth(200)
        self.close_action_combo.currentIndexChanged.connect(self._on_close_action_changed)
        behavior_card.add_row("关闭窗口时", self.close_action_combo)

        # Minimize to tray checkbox
        self.minimize_tray_check = QCheckBox("最小化时也隐藏到托盘")
        self.minimize_tray_check.setStyleSheet("color: #333; font-size: 14px;")
        self.minimize_tray_check.stateChanged.connect(self._on_minimize_tray_changed)
        behavior_card.add_widget(self.minimize_tray_check)

        layout.addWidget(behavior_card)
        layout.addStretch()

    def _load_settings(self):
        """Load settings from database"""
        close_action = self.db.get_setting("close_action", "ask")
        if close_action == "minimize":
            self.close_action_combo.setCurrentIndex(1)
        elif close_action == "quit":
            self.close_action_combo.setCurrentIndex(2)
        else:
            self.close_action_combo.setCurrentIndex(0)

        minimize_tray = self.db.get_setting("minimize_to_tray", "true")
        self.minimize_tray_check.setChecked(minimize_tray == "true")

    def _on_close_action_changed(self, index: int):
        """Handle close action change"""
        actions = ["ask", "minimize", "quit"]
        self.db.set_setting("close_action", actions[index])
        self.setting_changed.emit("close_action", actions[index])

    def _on_minimize_tray_changed(self, state: int):
        """Handle minimize to tray change"""
        value = "true" if state == Qt.CheckState.Checked.value else "false"
        self.db.set_setting("minimize_to_tray", value)
        self.setting_changed.emit("minimize_to_tray", value)


class ShortcutSettingsWidget(QWidget):
    """Shortcut settings widget - read-only display for now"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Shortcuts card
        shortcuts_card = SettingsCard("键盘快捷键")

        # Show shortcuts as read-only
        shortcuts = [
            ("新建待办", "Ctrl+N"),
            ("启动番茄钟", "Ctrl+P"),
            ("退出应用", "Ctrl+Q"),
        ]

        for name, key in shortcuts:
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(name)
            label.setStyleSheet("color: #333; font-size: 14px;")
            row_layout.addWidget(label)
            row_layout.addStretch()

            key_label = QLabel(f"<b>{key}</b>")
            key_label.setStyleSheet("""
                color: #666;
                background-color: #f5f5f5;
                padding: 4px 12px;
                border-radius: 6px;
                font-family: Consolas, Monaco, monospace;
            """)
            row_layout.addWidget(key_label)

            shortcuts_card.card_layout.addLayout(row_layout)

        layout.addWidget(shortcuts_card)
        layout.addStretch()


class SettingsPage(QWidget):
    """Settings page with sidebar navigation - Windows 11 style"""

    theme_changed = pyqtSignal(str)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI - Windows 11 style"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(4)

        # Header
        header = QLabel("设置")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #333;
            padding: 8px 0 16px 0;
        """)
        sidebar_layout.addWidget(header)

        # Nav buttons
        self.nav_pomodoro = SettingsNavButton("🍅  番茄钟")
        self.nav_pomodoro.setChecked(True)
        self.nav_pomodoro.clicked.connect(lambda: self._switch_page(0))
        sidebar_layout.addWidget(self.nav_pomodoro)

        self.nav_appearance = SettingsNavButton("🎨  外观")
        self.nav_appearance.clicked.connect(lambda: self._switch_page(1))
        sidebar_layout.addWidget(self.nav_appearance)

        self.nav_system = SettingsNavButton("⚙️  系统")
        self.nav_system.clicked.connect(lambda: self._switch_page(2))
        sidebar_layout.addWidget(self.nav_system)

        self.nav_shortcuts = SettingsNavButton("⌨️  快捷键")
        self.nav_shortcuts.clicked.connect(lambda: self._switch_page(3))
        sidebar_layout.addWidget(self.nav_shortcuts)

        sidebar_layout.addStretch()

        layout.addWidget(sidebar)

        # Content stack
        self.content_stack = QStackedWidget()

        # Page 0: Pomodoro
        self.pomodoro_settings = PomodoroSettingsWidget(self.db)
        self.content_stack.addWidget(self.pomodoro_settings)

        # Page 1: Appearance
        self.appearance_settings = AppearanceSettingsWidget(self.db)
        self.appearance_settings.setting_changed.connect(self._on_setting_changed)
        self.content_stack.addWidget(self.appearance_settings)

        # Page 2: System
        self.system_settings = SystemSettingsWidget(self.db)
        self.content_stack.addWidget(self.system_settings)

        # Page 3: Shortcuts
        self.shortcut_settings = ShortcutSettingsWidget()
        self.content_stack.addWidget(self.shortcut_settings)

        layout.addWidget(self.content_stack, 1)

    def _switch_page(self, index: int):
        """Switch to a settings page"""
        self.content_stack.setCurrentIndex(index)

        # Update nav buttons
        nav_buttons = [self.nav_pomodoro, self.nav_appearance,
                       self.nav_system, self.nav_shortcuts]
        for i, btn in enumerate(nav_buttons):
            btn.setChecked(i == index)

    def _on_setting_changed(self, key: str, value: str):
        """Handle setting change"""
        if key == "theme":
            self.theme_changed.emit(value)
