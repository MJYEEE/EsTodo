"""Pomodoro timer window"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSpinBox, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon
from typing import Optional
from ..models.pomodoro import Pomodoro


class PomodoroTimerWindow(QWidget):
    """Pomodoro timer window - floating, always on top"""

    timer_started = pyqtSignal(object)  # Emits Pomodoro
    timer_paused = pyqtSignal(object)  # Emits Pomodoro
    timer_resumed = pyqtSignal(object)  # Emits Pomodoro
    timer_stopped = pyqtSignal(object)  # Emits Pomodoro
    timer_completed = pyqtSignal(object)  # Emits Pomodoro

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pomodoro: Optional[Pomodoro] = None
        self.timer = QTimer()
        self.time_remaining: int = 0  # seconds
        self.is_paused: bool = False
        self.current_todo_id: Optional[int] = None
        self.current_todo_title: str = ""

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("番茄钟")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setMinimumSize(320, 400)
        self.setMaximumSize(400, 500)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(8)

        self.work_mode_btn = QPushButton("工作")
        self.work_mode_btn.setCheckable(True)
        self.work_mode_btn.setChecked(True)
        self.work_mode_btn.setProperty("mode", "work")
        mode_layout.addWidget(self.work_mode_btn)

        self.short_break_btn = QPushButton("短休息")
        self.short_break_btn.setCheckable(True)
        self.short_break_btn.setProperty("mode", "short_break")
        mode_layout.addWidget(self.short_break_btn)

        self.long_break_btn = QPushButton("长休息")
        self.long_break_btn.setCheckable(True)
        self.long_break_btn.setProperty("mode", "long_break")
        mode_layout.addWidget(self.long_break_btn)

        layout.addLayout(mode_layout)

        # Custom duration
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("自定义时长:"))

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 120)
        self.duration_spin.setValue(25)
        self.duration_spin.setSuffix(" 分钟")
        custom_layout.addWidget(self.duration_spin)

        layout.addLayout(custom_layout)

        # Linked todo (if any)
        self.todo_label = QLabel()
        self.todo_label.setStyleSheet("""
            color: #64748b;
            font-size: 12px;
            padding: 8px;
            background-color: #f1f5f9;
            border-radius: 6px;
        """)
        self.todo_label.setWordWrap(True)
        self.todo_label.hide()
        layout.addWidget(self.todo_label)

        # Timer display
        timer_container = QFrame()
        timer_container.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 16px;
            }
        """)
        timer_layout = QVBoxLayout(timer_container)
        timer_layout.setContentsMargins(24, 32, 24, 32)

        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_font = QFont()
        time_font.setPointSize(48)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        self.time_label.setStyleSheet("color: #1e293b;")
        timer_layout.addWidget(self.time_label)

        self.status_label = QLabel("准备开始")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #64748b; font-size: 14px;")
        timer_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e2e8f0;
                height: 8px;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #4f46e5;
                border-radius: 4px;
            }
        """)
        timer_layout.addWidget(self.progress_bar)

        layout.addWidget(timer_container, 1)

        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        self.start_btn = QPushButton("开始")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.setMinimumHeight(48)
        control_layout.addWidget(self.start_btn, 2)

        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setObjectName("secondaryButton")
        self.pause_btn.setMinimumHeight(48)
        self.pause_btn.hide()
        control_layout.addWidget(self.pause_btn, 1)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setObjectName("dangerButton")
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.hide()
        control_layout.addWidget(self.stop_btn, 1)

        layout.addLayout(control_layout)

        # Pomodoro count
        count_layout = QHBoxLayout()
        count_layout.addStretch()
        self.count_label = QLabel("今日完成: 0 个番茄")
        self.count_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        count_layout.addWidget(self.count_label)
        count_layout.addStretch()
        layout.addLayout(count_layout)

    def _connect_signals(self):
        """Connect signals"""
        # Mode buttons
        self.work_mode_btn.clicked.connect(lambda: self._set_mode("work"))
        self.short_break_btn.clicked.connect(lambda: self._set_mode("short_break"))
        self.long_break_btn.clicked.connect(lambda: self._set_mode("long_break"))

        # Duration spin
        self.duration_spin.valueChanged.connect(self._on_duration_changed)

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
            self.duration_spin.setValue(25)
        elif mode == "short_break":
            self.duration_spin.setValue(5)
        elif mode == "long_break":
            self.duration_spin.setValue(15)

    def _on_duration_changed(self, value: int):
        """Handle duration change"""
        if not self.timer.isActive() and not self.is_paused:
            self.time_remaining = value * 60
            self._update_time_display()

    def link_to_todo(self, todo_id: Optional[int], todo_title: str = ""):
        """Link timer to a todo"""
        self.current_todo_id = todo_id
        self.current_todo_title = todo_title

        if todo_id and todo_title:
            self.todo_label.setText(f"📋 {todo_title}")
            self.todo_label.show()
        else:
            self.todo_label.hide()

    def _on_start(self):
        """Handle start button"""
        duration = self.duration_spin.value()
        self.time_remaining = duration * 60
        self.is_paused = False

        # Create pomodoro record
        from datetime import datetime
        self.current_pomodoro = Pomodoro(
            todo_id=self.current_todo_id,
            duration=duration,
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
        """Update the time display"""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def _update_progress(self):
        """Update the progress bar"""
        total = self.duration_spin.value() * 60
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
        self.duration_spin.setEnabled(False)

    def _update_ui_stopped(self):
        """Update UI for stopped state"""
        self.start_btn.show()
        self.pause_btn.hide()
        self.stop_btn.hide()
        self.work_mode_btn.setEnabled(True)
        self.short_break_btn.setEnabled(True)
        self.long_break_btn.setEnabled(True)
        self.duration_spin.setEnabled(True)
        self.progress_bar.setValue(0)

        # Reset time display
        duration = self.duration_spin.value()
        self.time_remaining = duration * 60
        self._update_time_display()

    def update_today_count(self, count: int):
        """Update the today pomodoro count"""
        self.count_label.setText(f"今日完成: {count} 个番茄")
