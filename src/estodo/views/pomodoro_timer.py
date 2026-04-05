"""Pomodoro timer window - Windows 11 style"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSpinBox, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QFontDatabase
from typing import Optional
from ..models.pomodoro import Pomodoro


class PomodoroTimerWidget(QWidget):
    """Pomodoro timer widget - Windows 11 refined style"""

    timer_started = pyqtSignal(object)  # Emits Pomodoro
    timer_paused = pyqtSignal(object)  # Emits Pomodoro
    timer_resumed = pyqtSignal(object)  # Emits Pomodoro
    timer_stopped = pyqtSignal(object)  # Emits Pomodoro
    timer_completed = pyqtSignal(object)  # Emits Pomodoro

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pomodoro: Optional[Pomodoro] = None
        self.timer = QTimer()
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)  # High precision timer
        self.time_remaining: int = 0  # seconds
        self.is_paused: bool = False
        self.current_todo_id: Optional[int] = None
        self.current_todo_title: str = ""
        self.is_dark_mode: bool = False

        self._setup_ui()
        self._connect_signals()

    def set_dark_mode(self, is_dark: bool):
        """Set dark mode for the widget"""
        self.is_dark_mode = is_dark
        self._update_colors()

    def _update_colors(self):
        """Update colors based on theme - Windows 11 style"""
        if self.is_dark_mode:
            timer_bg = "#2d2d2d"
            timer_border = "#404040"
            todo_bg = "#363636"
            todo_color = "#cccccc"
            time_color = "#ffffff"
            status_color = "#808080"
            progress_bg = "#404040"
            progress_chunk = "#60cdff"
        else:
            timer_bg = "#ffffff"
            timer_border = "#e0e0e0"
            todo_bg = "#f3f3f3"
            todo_color = "#606060"
            time_color = "#000000"
            status_color = "#a0a0a0"
            progress_bg = "#e0e0e0"
            progress_chunk = "#0078d4"

        self.timer_container.setStyleSheet(f"""
            QFrame {{
                background-color: {timer_bg};
                border: 1px solid {timer_border};
                border-radius: 16px;
            }}
        """)
        self.todo_label.setStyleSheet(f"""
            color: {todo_color};
            font-size: 13px;
            padding: 10px 14px;
            background-color: {todo_bg};
            border-radius: 8px;
            font-weight: 500;
        """)
        self.time_label.setStyleSheet(f"color: {time_color};")
        self.status_label.setStyleSheet(f"color: {status_color}; font-size: 15px; font-weight: 500;")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {progress_bg};
                height: 6px;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {progress_chunk};
                border-radius: 3px;
            }}
        """)

    def _setup_ui(self):
        """Setup the UI - Windows 11 refined design"""
        self.setMinimumSize(420, 540)

        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)

        # Mode selection - Windows 11 segmented control style
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(6)

        self.work_mode_btn = QPushButton("工作")
        self.work_mode_btn.setObjectName("modeButton")
        self.work_mode_btn.setCheckable(True)
        self.work_mode_btn.setChecked(True)
        self.work_mode_btn.setProperty("mode", "work")
        self.work_mode_btn.setMinimumHeight(36)
        mode_layout.addWidget(self.work_mode_btn)

        self.short_break_btn = QPushButton("短休息")
        self.short_break_btn.setObjectName("modeButton")
        self.short_break_btn.setCheckable(True)
        self.short_break_btn.setProperty("mode", "short_break")
        self.short_break_btn.setMinimumHeight(36)
        mode_layout.addWidget(self.short_break_btn)

        self.long_break_btn = QPushButton("长休息")
        self.long_break_btn.setObjectName("modeButton")
        self.long_break_btn.setCheckable(True)
        self.long_break_btn.setProperty("mode", "long_break")
        self.long_break_btn.setMinimumHeight(36)
        mode_layout.addWidget(self.long_break_btn)

        layout.addLayout(mode_layout)

        # Custom duration - cleaner layout
        custom_layout = QHBoxLayout()
        custom_layout.setSpacing(12)
        custom_label = QLabel("自定义时长:")
        custom_label.setStyleSheet("color: #606060; font-size: 13px; font-weight: 500;")
        custom_layout.addWidget(custom_label)
        custom_layout.addStretch()

        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(0)
        self.hour_spin.setSuffix(" 时")
        self.hour_spin.setMinimumWidth(80)
        custom_layout.addWidget(self.hour_spin)

        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(25)
        self.minute_spin.setSuffix(" 分")
        self.minute_spin.setMinimumWidth(80)
        custom_layout.addWidget(self.minute_spin)

        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 59)
        self.second_spin.setValue(0)
        self.second_spin.setSuffix(" 秒")
        self.second_spin.setMinimumWidth(80)
        custom_layout.addWidget(self.second_spin)

        layout.addLayout(custom_layout)

        # Linked todo (if any) - Windows 11 style
        self.todo_label = QLabel()
        self.todo_label.setWordWrap(True)
        self.todo_label.hide()
        layout.addWidget(self.todo_label)

        # Timer display - Windows 11 card style
        self.timer_container = QFrame()
        timer_layout = QVBoxLayout(self.timer_container)
        timer_layout.setContentsMargins(32, 40, 32, 40)
        timer_layout.setSpacing(20)

        # Time display with modern font
        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_font = QFont("Segoe UI Variable Display", 56, QFont.Weight.Bold)
        time_font.setStyleHint(QFont.StyleHint.System)
        time_font.setKerning(True)
        self.time_label.setFont(time_font)
        timer_layout.addWidget(self.time_label)

        # Status label
        self.status_label = QLabel("准备开始")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.status_label)

        # Progress bar - Windows 11 style
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        timer_layout.addWidget(self.progress_bar)

        layout.addWidget(self.timer_container, 1)

        # Control buttons - Windows 11 style
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        self.start_btn = QPushButton("开始")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.setMinimumHeight(48)
        self.start_btn.setMinimumWidth(140)
        control_layout.addWidget(self.start_btn, 3)

        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setObjectName("secondaryButton")
        self.pause_btn.setMinimumHeight(48)
        self.pause_btn.hide()
        control_layout.addWidget(self.pause_btn, 2)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setObjectName("secondaryButton")
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.hide()
        control_layout.addWidget(self.stop_btn, 2)

        layout.addLayout(control_layout)

        # Pomodoro count - Windows 11 style
        count_layout = QHBoxLayout()
        count_layout.addStretch()
        self.count_label = QLabel("今日完成: 0 个番茄")
        self.count_label.setStyleSheet("color: #a0a0a0; font-size: 13px; font-weight: 500;")
        count_layout.addWidget(self.count_label)
        count_layout.addStretch()
        layout.addLayout(count_layout)

        # Initialize colors
        self._update_colors()

    def _connect_signals(self):
        """Connect signals"""
        # Mode buttons
        self.work_mode_btn.clicked.connect(lambda: self._set_mode("work"))
        self.short_break_btn.clicked.connect(lambda: self._set_mode("short_break"))
        self.long_break_btn.clicked.connect(lambda: self._set_mode("long_break"))

        # Duration spins
        self.hour_spin.valueChanged.connect(self._on_duration_changed)
        self.minute_spin.valueChanged.connect(self._on_duration_changed)
        self.second_spin.valueChanged.connect(self._on_duration_changed)

        # Control buttons
        self.start_btn.clicked.connect(self._on_start)
        self.pause_btn.clicked.connect(self._on_pause_resume)
        self.stop_btn.clicked.connect(self._on_stop)

        # Timer
        self.timer.timeout.connect(self._on_timer_tick)

    def _set_mode(self, mode: str):
        """Set the timer mode"""
        # Update button states
        for btn in [self.work_mode_btn, self.short_break_btn, self.long_break_btn]:
            btn.setChecked(btn.property("mode") == mode)

        # Set duration
        if mode == "work":
            self.hour_spin.setValue(0)
            self.minute_spin.setValue(25)
            self.second_spin.setValue(0)
        elif mode == "short_break":
            self.hour_spin.setValue(0)
            self.minute_spin.setValue(5)
            self.second_spin.setValue(0)
        elif mode == "long_break":
            self.hour_spin.setValue(0)
            self.minute_spin.setValue(15)
            self.second_spin.setValue(0)

    def _on_duration_changed(self):
        """Handle duration change"""
        if not self.timer.isActive() and not self.is_paused:
            hours = self.hour_spin.value()
            minutes = self.minute_spin.value()
            seconds = self.second_spin.value()
            self.time_remaining = hours * 3600 + minutes * 60 + seconds
            self._update_time_display()

    def link_to_todo(self, todo_id: Optional[int], todo_title: str = ""):
        """Link timer to a todo"""
        self.current_todo_id = todo_id
        self.current_todo_title = todo_title

        if todo_id and todo_title:
            self.todo_label.setText(f"📎  {todo_title}")
            self.todo_label.show()
        else:
            self.todo_label.hide()

    def _on_start(self):
        """Handle start button"""
        hours = self.hour_spin.value()
        minutes = self.minute_spin.value()
        seconds = self.second_spin.value()
        total_seconds = hours * 3600 + minutes * 60 + seconds
        total_minutes = total_seconds / 60  # Store as minutes for database

        self.time_remaining = total_seconds
        self.is_paused = False

        # Create pomodoro record
        from datetime import datetime
        self.current_pomodoro = Pomodoro(
            todo_id=self.current_todo_id,
            duration=total_minutes,
            start_time=datetime.now()
        )

        self.timer.start(1000)
        self._update_ui_running()
        self.status_label.setText("专注中...")

        self.timer_started.emit(self.current_pomodoro)

    def _on_pause_resume(self):
        """Handle pause/resume button"""
        if self.is_paused:
            # Resume
            self.timer.start(1000)
            self.is_paused = False
            self.pause_btn.setText("暂停")
            self.status_label.setText("专注中...")
            self.timer_resumed.emit(self.current_pomodoro)
        else:
            # Pause
            self.timer.stop()
            self.is_paused = True
            self.pause_btn.setText("继续")
            self.status_label.setText("已暂停")
            self.timer_paused.emit(self.current_pomodoro)

    def _on_stop(self):
        """Handle stop button"""
        self.timer.stop()

        if self.current_pomodoro:
            from datetime import datetime
            self.current_pomodoro.end_time = datetime.now()
            self.current_pomodoro.is_completed = False
            self.timer_stopped.emit(self.current_pomodoro)

        self.is_paused = False
        self.current_pomodoro = None
        self._update_ui_stopped()
        self.status_label.setText("已停止")

    def _on_timer_tick(self):
        """Handle timer tick"""
        self.time_remaining -= 1
        self._update_time_display()
        self._update_progress()

        if self.time_remaining <= 0:
            self._on_complete()

    def _on_complete(self):
        """Handle timer completion"""
        self.timer.stop()

        if self.current_pomodoro:
            from datetime import datetime
            self.current_pomodoro.end_time = datetime.now()
            self.current_pomodoro.is_completed = True
            self.timer_completed.emit(self.current_pomodoro)

        self.is_paused = False
        self.current_pomodoro = None
        self._update_ui_stopped()
        self.status_label.setText("完成！")

    def _update_time_display(self):
        """Update the time display - optimized"""
        hours = self.time_remaining // 3600
        remaining = self.time_remaining % 3600
        minutes = remaining // 60
        seconds = remaining % 60
        if hours > 0:
            self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def _update_progress(self):
        """Update the progress bar - optimized"""
        hours = self.hour_spin.value()
        minutes = self.minute_spin.value()
        seconds = self.second_spin.value()
        total = hours * 3600 + minutes * 60 + seconds
        if total > 0:
            elapsed = total - self.time_remaining
            progress = int((elapsed / total) * 100)
            self.progress_bar.setValue(progress)

    def _update_ui_running(self):
        """Update UI for running state"""
        self.start_btn.hide()
        self.pause_btn.show()
        self.pause_btn.setText("暂停")
        self.stop_btn.show()
        self.work_mode_btn.setEnabled(False)
        self.short_break_btn.setEnabled(False)
        self.long_break_btn.setEnabled(False)
        self.hour_spin.setEnabled(False)
        self.minute_spin.setEnabled(False)
        self.second_spin.setEnabled(False)

    def _update_ui_stopped(self):
        """Update UI for stopped state"""
        self.start_btn.show()
        self.pause_btn.hide()
        self.stop_btn.hide()
        self.work_mode_btn.setEnabled(True)
        self.short_break_btn.setEnabled(True)
        self.long_break_btn.setEnabled(True)
        self.hour_spin.setEnabled(True)
        self.minute_spin.setEnabled(True)
        self.second_spin.setEnabled(True)
        self.progress_bar.setValue(0)

        # Reset time display
        hours = self.hour_spin.value()
        minutes = self.minute_spin.value()
        seconds = self.second_spin.value()
        self.time_remaining = hours * 3600 + minutes * 60 + seconds
        self._update_time_display()

    def update_today_count(self, count: int):
        """Update the today pomodoro count"""
        self.count_label.setText(f"今日完成: {count} 个番茄")
