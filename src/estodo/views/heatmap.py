"""Pomodoro heatmap calendar widget"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QGridLayout, QToolTip
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta


class HeatmapCell(QWidget):
    """Single heatmap cell representing a day"""

    clicked = pyqtSignal(QDate)

    def __init__(self, date: QDate, count: int = 0, parent=None):
        super().__init__(parent)
        self.date = date
        self.count = count
        self.setFixedSize(20, 20)
        self.setToolTip(self._get_tooltip_text())
        self._is_hovered = False

    def _get_tooltip_text(self) -> str:
        """Get tooltip text"""
        date_str = self.date.toString("yyyy-MM-dd dddd")
        if self.count == 0:
            return f"{date_str}\n无番茄钟"
        elif self.count == 1:
            return f"{date_str}\n{self.count} 个番茄钟"
        else:
            return f"{date_str}\n{self.count} 个番茄钟"

    def set_count(self, count: int):
        """Set the pomodoro count"""
        self.count = count
        self.setToolTip(self._get_tooltip_text())
        self.update()

    def get_color(self) -> QColor:
        """Get the color based on count"""
        if self.count == 0:
            return QColor("#f1f5f9")  # Light gray
        elif self.count == 1:
            return QColor("#dbeafe")  # Light blue
        elif self.count == 2:
            return QColor("#93c5fd")
        elif self.count == 3:
            return QColor("#3b82f6")
        else:
            return QColor("#1d4ed8")  # Dark blue

    def paintEvent(self, event):
        """Paint the cell"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        color = self.get_color()
        if self._is_hovered:
            color = color.lighter(110)

        painter.setBrush(color)
        painter.setPen(QPen(QColor("#e2e8f0"), 1))
        painter.drawRoundedRect(2, 2, self.width() - 4, self.height() - 4, 3, 3)

        painter.end()

    def enterEvent(self, event):
        """Mouse enter event"""
        self._is_hovered = True
        self.update()

    def leaveEvent(self, event):
        """Mouse leave event"""
        self._is_hovered = False
        self.update()

    def mousePressEvent(self, event):
        """Mouse press event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.date)


class HeatmapCalendar(QWidget):
    """Pomodoro heatmap calendar like GitHub's contribution graph"""

    date_clicked = pyqtSignal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.daily_counts: Dict[str, int] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header with month labels
        self.header = QWidget()
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(30, 0, 0, 0)
        self.header_layout.setSpacing(0)
        self._update_month_labels()
        layout.addWidget(self.header)

        # Grid area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.cells: List[HeatmapCell] = []
        self._populate_grid()

        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        legend_layout.addWidget(QLabel("少"))

        for count in [0, 1, 2, 3, 4]:
            legend_cell = QLabel()
            legend_cell.setFixedSize(16, 16)
            legend_cell.setStyleSheet(self._get_legend_style(count))
            legend_layout.addWidget(legend_cell)

        legend_layout.addWidget(QLabel("多"))
        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        # Summary label
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setStyleSheet("color: #64748b; font-size: 14px;")
        layout.addWidget(self.summary_label)

    def _get_legend_style(self, count: int) -> str:
        """Get legend cell style"""
        if count == 0:
            color = "#f1f5f9"
        elif count == 1:
            color = "#dbeafe"
        elif count == 2:
            color = "#93c5fd"
        elif count == 3:
            color = "#3b82f6"
        else:
            color = "#1d4ed8"
        return f"""
            QLabel {{
                background-color: {color};
                border-radius: 3px;
                border: 1px solid #e2e8f0;
            }}
        """

    def _update_month_labels(self):
        """Update the month labels"""
        # Clear existing
        for i in reversed(range(self.header_layout.count())):
            self.header_layout.itemAt(i).widget().setParent(None)

        # Calculate dates
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-364)  # ~1 year

        current_month = -1
        current_year = -1

        # Add spacing to align with week days
        day_of_week = start_date.dayOfWeek()  # 1=Mon, 7=Sun
        # Adjust to start on Monday (1)
        spacing = (day_of_week - 1) % 7

        for i in range(spacing):
            spacer = QLabel()
            spacer.setFixedWidth(22)
            self.header_layout.addWidget(spacer)

        # Add month labels
        date = start_date
        while date <= end_date:
            if date.month() != current_month or date.year() != current_year:
                current_month = date.month()
                current_year = date.year()
                month_label = QLabel(date.toString("MMM"))
                month_label.setStyleSheet("color: #64748b; font-size: 11px;")
                month_label.setFixedWidth(154)  # 7 days * 22px
                self.header_layout.addWidget(month_label)

            date = date.addDays(28)  # roughly a month

        self.header_layout.addStretch()

    def _populate_grid(self):
        """Populate the grid with cells"""
        # Clear existing
        self.cells = []
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        # Calculate dates
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-364)  # ~1 year

        # Weekday labels (Mon, Wed, Fri)
        day_labels = ["一", "", "三", "", "五", "", "日"]
        for row in range(7):
            if day_labels[row]:
                label = QLabel(day_labels[row])
                label.setStyleSheet("color: #94a3b8; font-size: 10px;")
                label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                label.setFixedWidth(24)
                self.grid_layout.addWidget(label, row, 0)

        # Populate cells
        date = start_date
        col = 1
        row = (start_date.dayOfWeek() - 1) % 7  # 0=Mon, 6=Sun

        while date <= end_date:
            count = self.daily_counts.get(date.toString("yyyy-MM-dd"), 0)
            cell = HeatmapCell(date, count)
            cell.clicked.connect(self.date_clicked.emit)
            self.cells.append(cell)
            self.grid_layout.addWidget(cell, row, col)

            row += 1
            if row >= 7:
                row = 0
                col += 1

            date = date.addDays(1)

        # Add stretch
        self.grid_layout.setColumnStretch(col + 1, 1)

    def set_daily_counts(self, counts: Dict[str, int]):
        """Set the daily pomodoro counts"""
        self.daily_counts = counts

        # Update cells
        for cell in self.cells:
            date_str = cell.date.toString("yyyy-MM-dd")
            count = counts.get(date_str, 0)
            cell.set_count(count)

        # Update summary
        total = sum(counts.values())
        days_with_pomodoros = sum(1 for c in counts.values() if c > 0)
        self.summary_label.setText(f"过去一年共完成 {total} 个番茄钟，在 {days_with_pomodoros} 天里有记录")

    def get_counts_for_date(self, date: QDate) -> int:
        """Get the count for a specific date"""
        return self.daily_counts.get(date.toString("yyyy-MM-dd"), 0)
