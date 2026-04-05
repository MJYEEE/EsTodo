"""Day detail dialog - shows pomodoros for a specific day"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QFrame, QWidget
)
from PyQt6.QtCore import Qt, QDate
from typing import Optional, List
from datetime import datetime
from ..models.pomodoro import Pomodoro, PomodoroModel
from ..models.todo import TodoModel, Todo


class PomodoroListItem(QWidget):
    """Widget for displaying a single pomodoro in the list"""

    def __init__(self, pomodoro: Pomodoro, todo: Optional[Todo] = None, parent=None):
        super().__init__(parent)
        self.pomodoro = pomodoro
        self.todo = todo
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Icon/status indicator - colored dot
        status_label = QLabel()
        status_label.setFixedSize(16, 16)
        if self.pomodoro.is_completed:
            status_label.setStyleSheet("""
                QLabel {
                    background-color: #22c55e;
                    border-radius: 8px;
                }
            """)
        else:
            status_label.setStyleSheet("""
                QLabel {
                    background-color: #94a3b8;
                    border-radius: 8px;
                }
            """)
        layout.addWidget(status_label)
        layout.addSpacing(8)

        # Time and duration
        time_layout = QVBoxLayout()
        time_layout.setSpacing(2)

        if self.pomodoro.start_time:
            start_str = self.pomodoro.start_time.strftime("%H:%M")
            if self.pomodoro.end_time:
                end_str = self.pomodoro.end_time.strftime("%H:%M")
                time_label = QLabel(f"{start_str} - {end_str}")
            else:
                time_label = QLabel(f"{start_str} - (未完成)")
        else:
            time_label = QLabel("(未知时间)")

        time_label.setStyleSheet("font-weight: 600; color: #1e293b; font-size: 14px;")
        time_layout.addWidget(time_label)

        duration_label = QLabel(f"{self.pomodoro.duration} 分钟")
        duration_label.setStyleSheet("font-size: 12px; color: #64748b;")
        time_layout.addWidget(duration_label)

        layout.addLayout(time_layout, 1)

        # Linked todo if any
        if self.todo:
            todo_label = QLabel(self.todo.title)
            todo_label.setStyleSheet("""
                color: #4f46e5;
                font-size: 12px;
                background-color: #eef2ff;
                padding: 4px 8px;
                border-radius: 4px;
            """)
            todo_label.setWordWrap(True)
            layout.addWidget(todo_label, 2)

        # Note if any
        if self.pomodoro.note:
            note_label = QLabel(self.pomodoro.note)
            note_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
            note_label.setWordWrap(True)
            layout.addWidget(note_label, 1)


class DayDetailDialog(QDialog):
    """Dialog showing pomodoros for a specific day"""

    def __init__(self, date: QDate, pomodoro_model: PomodoroModel,
                 todo_model: TodoModel, parent=None):
        super().__init__(parent)
        self.date = date
        self.pomodoro_model = pomodoro_model
        self.todo_model = todo_model
        self._setup_ui()
        self._load_pomodoros()

    def _setup_ui(self):
        """Setup the UI with better styling"""
        self.setWindowTitle(f"番茄钟 - {self.date.toString('yyyy年MM月dd日 dddd')}")
        self.setMinimumSize(520, 420)
        self.resize(620, 520)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header_layout = QHBoxLayout()

        date_label = QLabel(self.date.toString("yyyy年MM月dd日 dddd"))
        date_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #1e293b;
        """)
        header_layout.addWidget(date_label)

        header_layout.addStretch()

        self.count_label = QLabel()
        self.count_label.setStyleSheet("""
            color: #64748b;
            font-size: 14px;
            font-weight: 500;
            background-color: #f1f5f9;
            padding: 6px 12px;
            border-radius: 6px;
        """)
        header_layout.addWidget(self.count_label)

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

        close_button = QPushButton("关闭")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _load_pomodoros(self):
        """Load pomodoros for the day"""
        # Convert QDate to datetime range
        start_datetime = datetime(
            self.date.year(), self.date.month(), self.date.day(),
            0, 0, 0
        )
        end_datetime = start_datetime.replace(hour=23, minute=59, second=59)

        # Get pomodoros
        pomodoros = self.pomodoro_model.get_by_date_range(
            start_datetime, end_datetime
        )

        # Update count
        completed = sum(1 for p in pomodoros if p.is_completed)
        self.count_label.setText(f"共 {len(pomodoros)} 个番茄钟，完成 {completed} 个")

        # Populate list
        self.list_widget.clear()

        for pomodoro in pomodoros:
            # Get linked todo if any
            todo = None
            if pomodoro.todo_id:
                todo = self.todo_model.get_by_id(pomodoro.todo_id)

            # Create widget
            item_widget = PomodoroListItem(pomodoro, todo)

            # Add to list
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

        if not pomodoros:
            empty_label = QLabel("这一天还没有番茄钟记录")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #94a3b8; padding: 40px;")
            item = QListWidgetItem()
            item.setSizeHint(empty_label.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, empty_label)
