"""Themes for EsTodo"""

from enum import Enum


class Theme(Enum):
    """Theme enum"""
    LIGHT = "light"
    DARK = "dark"


def get_stylesheet(theme: Theme) -> str:
    """Get stylesheet for theme"""
    if theme == Theme.DARK:
        return _DARK_STYLESHEET
    return _LIGHT_STYLESHEET


_LIGHT_STYLESHEET = """
/* Main Window */
QMainWindow {
    background-color: #f8fafc;
}

/* Sidebar */
QWidget#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

QPushButton#navButton {
    border: none;
    padding: 10px 16px;
    text-align: left;
    border-radius: 6px;
    margin: 4px 8px;
    font-size: 14px;
    color: #475569;
    background-color: transparent;
}

QPushButton#navButton:hover {
    background-color: #f1f5f9;
    color: #1e293b;
}

QPushButton#navButton:checked {
    background-color: #e0e7ff;
    color: #4338ca;
    font-weight: 600;
}

/* Content Area */
QWidget#contentArea {
    background-color: #f8fafc;
}

/* Todo Tree */
QTreeWidget {
    border: none;
    background-color: #ffffff;
    border-radius: 8px;
    margin: 8px;
    padding: 4px;
    outline: none;
}

QTreeWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px 0;
}

QTreeWidget::item:hover {
    background-color: #f1f5f9;
}

QTreeWidget::item:selected {
    background-color: #e0e7ff;
    color: #4338ca;
}

/* Buttons */
QPushButton {
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#primaryButton {
    background-color: #4f46e5;
    color: white;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #4338ca;
}

QPushButton#secondaryButton {
    background-color: #e2e8f0;
    color: #475569;
    border: none;
}

QPushButton#secondaryButton:hover {
    background-color: #cbd5e1;
}

QPushButton#dangerButton {
    background-color: #ef4444;
    color: white;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #dc2626;
}

/* Line Edit */
QLineEdit {
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: #ffffff;
    font-size: 14px;
}

QLineEdit:focus {
    border: 2px solid #4f46e5;
    outline: none;
}

/* Text Edit */
QTextEdit {
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: #ffffff;
    font-size: 14px;
}

QTextEdit:focus {
    border: 2px solid #4f46e5;
    outline: none;
}

/* Combo Box */
QComboBox {
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: #ffffff;
    font-size: 14px;
}

QComboBox:hover {
    border-color: #cbd5e1;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #64748b;
}

/* Check Box */
QCheckBox {
    spacing: 8px;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #cbd5e1;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border-color: #4f46e5;
}

QCheckBox::indicator:checked {
    background-color: #4f46e5;
    border-color: #4f46e5;
}

/* Header */
QLabel#headerLabel {
    font-size: 24px;
    font-weight: 700;
    color: #1e293b;
    padding: 16px;
}
"""

_DARK_STYLESHEET = """
/* Main Window */
QMainWindow {
    background-color: #0f172a;
}

/* Sidebar */
QWidget#sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
}

QPushButton#navButton {
    border: none;
    padding: 10px 16px;
    text-align: left;
    border-radius: 6px;
    margin: 4px 8px;
    font-size: 14px;
    color: #94a3b8;
    background-color: transparent;
}

QPushButton#navButton:hover {
    background-color: #334155;
    color: #f1f5f9;
}

QPushButton#navButton:checked {
    background-color: #312e81;
    color: #a5b4fc;
    font-weight: 600;
}

/* Content Area */
QWidget#contentArea {
    background-color: #0f172a;
}

/* Todo Tree */
QTreeWidget {
    border: none;
    background-color: #1e293b;
    border-radius: 8px;
    margin: 8px;
    padding: 4px;
    outline: none;
    color: #e2e8f0;
}

QTreeWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px 0;
}

QTreeWidget::item:hover {
    background-color: #334155;
}

QTreeWidget::item:selected {
    background-color: #312e81;
    color: #a5b4fc;
}

/* Buttons */
QPushButton {
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#primaryButton {
    background-color: #4f46e5;
    color: white;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #6366f1;
}

QPushButton#secondaryButton {
    background-color: #334155;
    color: #e2e8f0;
    border: none;
}

QPushButton#secondaryButton:hover {
    background-color: #475569;
}

QPushButton#dangerButton {
    background-color: #dc2626;
    color: white;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #ef4444;
}

/* Line Edit */
QLineEdit {
    padding: 10px 12px;
    border: 1px solid #334155;
    border-radius: 6px;
    background-color: #1e293b;
    font-size: 14px;
    color: #e2e8f0;
}

QLineEdit:focus {
    border: 2px solid #4f46e5;
    outline: none;
}

/* Text Edit */
QTextEdit {
    padding: 12px;
    border: 1px solid #334155;
    border-radius: 6px;
    background-color: #1e293b;
    font-size: 14px;
    color: #e2e8f0;
}

QTextEdit:focus {
    border: 2px solid #4f46e5;
    outline: none;
}

/* Combo Box */
QComboBox {
    padding: 8px 12px;
    border: 1px solid #334155;
    border-radius: 6px;
    background-color: #1e293b;
    font-size: 14px;
    color: #e2e8f0;
}

QComboBox:hover {
    border-color: #475569;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #94a3b8;
}

/* Check Box */
QCheckBox {
    spacing: 8px;
    font-size: 14px;
    color: #e2e8f0;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #475569;
    border-radius: 4px;
    background-color: #1e293b;
}

QCheckBox::indicator:hover {
    border-color: #4f46e5;
}

QCheckBox::indicator:checked {
    background-color: #4f46e5;
    border-color: #4f46e5;
}

/* Header */
QLabel#headerLabel {
    font-size: 24px;
    font-weight: 700;
    color: #f1f5f9;
    padding: 16px;
}
"""
