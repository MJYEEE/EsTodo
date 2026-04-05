"""Themes for EsTodo - Windows 11 style"""

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


# Windows 11 Design Tokens
_WIN11_LIGHT = {
    "bg": "#f3f3f3",          # Windows 11 light background
    "surface": "#ffffff",      # Card/surface background
    "surface_hover": "#f8f8f8",
    "surface_pressed": "#f0f0f0",
    "text": "#000000",
    "text_secondary": "#606060",
    "text_tertiary": "#a0a0a0",
    "border": "#e0e0e0",
    "accent": "#0078d4",      # Windows 11 blue
    "accent_hover": "#1084d8",
    "accent_pressed": "#005a9e",
    "accent_light": "#e5f3ff",
    "danger": "#d13438",
    "danger_hover": "#e81123",
    "success": "#107c10",
    "shadow": "rgba(0, 0, 0, 0.08)",
}

_WIN11_DARK = {
    "bg": "#202020",          # Windows 11 dark background
    "surface": "#2d2d2d",      # Card/surface background
    "surface_hover": "#363636",
    "surface_pressed": "#404040",
    "text": "#ffffff",
    "text_secondary": "#cccccc",
    "text_tertiary": "#808080",
    "border": "#404040",
    "accent": "#60cdff",      # Windows 11 blue (dark)
    "accent_hover": "#80d8ff",
    "accent_pressed": "#3da0d4",
    "accent_light": "#1a3a4c",
    "danger": "#ff5b5b",
    "danger_hover": "#ff7a7a",
    "success": "#8cd88c",
    "shadow": "rgba(0, 0, 0, 0.3)",
}


def _build_stylesheet(colors: dict) -> str:
    """Build stylesheet from color tokens"""
    return f"""
/* ============================================
   Windows 11 Style Theme
   ============================================ */

/* Main Window */
QMainWindow {{
    background-color: {colors["bg"]};
}}

/* Sidebar */
QWidget#sidebar {{
    background-color: {colors["surface"]};
    border-right: 1px solid {colors["border"]};
}}

/* Navigation Buttons - Windows 11 style */
QPushButton#navButton {{
    border: none;
    padding: 12px 16px;
    text-align: left;
    border-radius: 8px;
    margin: 4px 12px;
    font-size: 14px;
    font-weight: 500;
    color: {colors["text_secondary"]};
    background-color: transparent;
    outline: none;
}}

QPushButton#navButton:hover {{
    background-color: {colors["surface_hover"]};
    color: {colors["text"]};
}}

QPushButton#navButton:pressed {{
    background-color: {colors["surface_pressed"]};
}}

QPushButton#navButton:checked {{
    background-color: {colors["accent_light"]};
    color: {colors["accent"]};
    font-weight: 600;
}}

/* Content Area */
QWidget#contentArea {{
    background-color: {colors["bg"]};
}}

/* Todo Tree - Windows 11 style */
QTreeWidget {{
    border: none;
    background-color: {colors["surface"]};
    border-radius: 12px;
    margin: 12px;
    padding: 8px;
    outline: none;
    color: {colors["text"]};
    alternate-background-color: transparent;
}}

QTreeWidget::item {{
    padding: 10px 12px;
    border-radius: 8px;
    margin: 2px 4px;
    border: none;
    outline: none;
}}

QTreeWidget::item:hover {{
    background-color: {colors["surface_hover"]};
}}

QTreeWidget::item:selected {{
    background-color: {colors["accent_light"]};
    color: {colors["accent"]};
}}

/* Buttons - Windows 11 style */
QPushButton {{
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    border: 1px solid transparent;
    background-color: transparent;
    color: {colors["text"]};
    outline: none;
}}

QPushButton:hover {{
    background-color: {colors["surface_hover"]};
}}

QPushButton:pressed {{
    background-color: {colors["surface_pressed"]};
}}

/* Primary Button - Windows 11 accent */
QPushButton#primaryButton {{
    background-color: {colors["accent"]};
    color: white;
    border: none;
    padding: 10px 20px;
    font-weight: 600;
}}

QPushButton#primaryButton:hover {{
    background-color: {colors["accent_hover"]};
}}

QPushButton#primaryButton:pressed {{
    background-color: {colors["accent_pressed"]};
}}

/* Secondary Button */
QPushButton#secondaryButton {{
    background-color: {colors["surface"]};
    color: {colors["text"]};
    border: 1px solid {colors["border"]};
}}

QPushButton#secondaryButton:hover {{
    background-color: {colors["surface_hover"]};
    border-color: {colors["text_tertiary"]};
}}

QPushButton#secondaryButton:pressed {{
    background-color: {colors["surface_pressed"]};
}}

/* Danger Button */
QPushButton#dangerButton {{
    background-color: {colors["danger"]};
    color: white;
    border: none;
}}

QPushButton#dangerButton:hover {{
    background-color: {colors["danger_hover"]};
}}

/* Mode Buttons (Pomodoro) */
QPushButton#modeButton {{
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 500;
    background-color: transparent;
    color: {colors["text_secondary"]};
    border: 1px solid transparent;
}}

QPushButton#modeButton:hover {{
    background-color: {colors["surface_hover"]};
    color: {colors["text"]};
}}

QPushButton#modeButton:checked {{
    background-color: {colors["accent_light"]};
    color: {colors["accent"]};
    font-weight: 600;
    border: 1px solid {colors["accent"]};
}}

/* Line Edit - Windows 11 style */
QLineEdit {{
    padding: 10px 14px;
    border: 1px solid {colors["border"]};
    border-radius: 8px;
    background-color: {colors["surface"]};
    color: {colors["text"]};
    font-size: 14px;
    selection-background-color: {colors["accent"]};
    selection-color: white;
}}

QLineEdit:hover {{
    border-color: {colors["text_tertiary"]};
}}

QLineEdit:focus {{
    border: 2px solid {colors["accent"]};
    padding: 9px 13px;
    outline: none;
}}

/* Text Edit */
QTextEdit {{
    padding: 12px 14px;
    border: 1px solid {colors["border"]};
    border-radius: 8px;
    background-color: {colors["surface"]};
    color: {colors["text"]};
    font-size: 14px;
    selection-background-color: {colors["accent"]};
    selection-color: white;
}}

QTextEdit:hover {{
    border-color: {colors["text_tertiary"]};
}}

QTextEdit:focus {{
    border: 2px solid {colors["accent"]};
    padding: 11px 13px;
    outline: none;
}}

/* Plain Text Edit */
QPlainTextEdit {{
    padding: 12px 14px;
    border: 1px solid {colors["border"]};
    border-radius: 8px;
    background-color: {colors["surface"]};
    color: {colors["text"]};
    font-size: 14px;
    selection-background-color: {colors["accent"]};
    selection-color: white;
}}

QPlainTextEdit:hover {{
    border-color: {colors["text_tertiary"]};
}}

QPlainTextEdit:focus {{
    border: 2px solid {colors["accent"]};
    padding: 11px 13px;
    outline: none;
}}

/* Combo Box */
QComboBox {{
    padding: 10px 14px;
    border: 1px solid {colors["border"]};
    border-radius: 8px;
    background-color: {colors["surface"]};
    color: {colors["text"]};
    font-size: 14px;
    min-height: 20px;
}}

QComboBox:hover {{
    border-color: {colors["text_tertiary"]};
}}

QComboBox:focus {{
    border: 2px solid {colors["accent"]};
    padding: 9px 13px;
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {colors["text_secondary"]};
}}

QComboBox QAbstractItemView {{
    border: 1px solid {colors["border"]};
    border-radius: 8px;
    background-color: {colors["surface"]};
    color: {colors["text"]};
    padding: 4px;
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    border-radius: 6px;
    margin: 2px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {colors["surface_hover"]};
}}

QComboBox QAbstractItemView::item:selected {{
    background-color: {colors["accent_light"]};
    color: {colors["accent"]};
}}

/* Spin Box */
QSpinBox {{
    padding: 10px 14px;
    border: 1px solid {colors["border"]};
    border-radius: 8px;
    background-color: {colors["surface"]};
    color: {colors["text"]};
    font-size: 14px;
}}

QSpinBox:hover {{
    border-color: {colors["text_tertiary"]};
}}

QSpinBox:focus {{
    border: 2px solid {colors["accent"]};
    padding: 9px 13px;
}}

QSpinBox::up-button, QSpinBox::down-button {{
    border: none;
    width: 20px;
    background-color: transparent;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {colors["surface_hover"]};
}}

/* Check Box */
QCheckBox {{
    spacing: 10px;
    font-size: 14px;
    color: {colors["text"]};
}}

QCheckBox::indicator {{
    width: 22px;
    height: 22px;
    border: 2px solid {colors["border"]};
    border-radius: 6px;
    background-color: {colors["surface"]};
}}

QCheckBox::indicator:hover {{
    border-color: {colors["accent"]};
}}

QCheckBox::indicator:checked {{
    background-color: {colors["accent"]};
    border-color: {colors["accent"]};
}}

/* Radio Button */
QRadioButton {{
    spacing: 10px;
    font-size: 14px;
    color: {colors["text"]};
}}

QRadioButton::indicator {{
    width: 22px;
    height: 22px;
    border: 2px solid {colors["border"]};
    border-radius: 11px;
    background-color: {colors["surface"]};
}}

QRadioButton::indicator:hover {{
    border-color: {colors["accent"]};
}}

QRadioButton::indicator:checked {{
    background-color: {colors["surface"]};
    border-color: {colors["accent"]};
}}

QRadioButton::indicator::indicator {{
    width: 10px;
    height: 10px;
    border-radius: 5px;
    background-color: {colors["accent"]};
}}

/* Header */
QLabel#headerLabel {{
    font-size: 28px;
    font-weight: 700;
    color: {colors["text"]};
    padding: 16px 12px;
}}

/* Subheader */
QLabel#subheaderLabel {{
    font-size: 18px;
    font-weight: 600;
    color: {colors["text"]};
}}

/* Caption Text */
QLabel#captionLabel {{
    font-size: 12px;
    color: {colors["text_tertiary"]};
}}

/* Card/Surface Container */
QWidget#card {{
    background-color: {colors["surface"]};
    border-radius: 12px;
    border: 1px solid {colors["border"]};
}}

/* Progress Bar - Windows 11 style */
QProgressBar {{
    border: none;
    background-color: {colors["border"]};
    height: 4px;
    border-radius: 2px;
}}

QProgressBar::chunk {{
    background-color: {colors["accent"]};
    border-radius: 2px;
}}

/* Menu Bar */
QMenuBar {{
    background-color: {colors["surface"]};
    border-bottom: 1px solid {colors["border"]};
    padding: 4px;
}}

QMenuBar::item {{
    padding: 6px 12px;
    border-radius: 6px;
    background-color: transparent;
    color: {colors["text"]};
}}

QMenuBar::item:selected {{
    background-color: {colors["surface_hover"]};
}}

/* Menu */
QMenu {{
    background-color: {colors["surface"]};
    border: 1px solid {colors["border"]};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px 8px 12px;
    border-radius: 6px;
    margin: 2px;
    color: {colors["text"]};
}}

QMenu::item:selected {{
    background-color: {colors["surface_hover"]};
}}

QMenu::separator {{
    height: 1px;
    background-color: {colors["border"]};
    margin: 4px 8px;
}}

/* Scroll Bar - Windows 11 style */
QScrollBar:vertical {{
    border: none;
    background-color: transparent;
    width: 12px;
    margin: 4px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {colors["text_tertiary"]};
    min-height: 50px;
    border-radius: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors["text_secondary"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background-color: transparent;
    height: 12px;
    margin: 4px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {colors["text_tertiary"]};
    min-width: 50px;
    border-radius: 6px;
    margin: 0px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {colors["text_secondary"]};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Tool Tip */
QToolTip {{
    background-color: {colors["surface"]};
    color: {colors["text"]};
    border: 1px solid {colors["border"]};
    border-radius: 6px;
    padding: 6px 10px;
}}

/* Message Box */
QMessageBox {{
    background-color: {colors["surface"]};
}}

QMessageBox QLabel {{
    color: {colors["text"]};
}}

QMessageBox QPushButton {{
    min-width: 80px;
    padding: 8px 24px;
}}

/* Splitter */
QSplitter::handle {{
    background-color: {colors["border"]};
    width: 1px;
    height: 1px;
}}

QSplitter::handle:hover {{
    background-color: {colors["accent"]};
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {colors["border"]};
    border-radius: 8px;
    background-color: {colors["surface"]};
}}

QTabBar::tab {{
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    background-color: transparent;
    color: {colors["text_secondary"]};
    margin-right: 4px;
}}

QTabBar::tab:selected {{
    background-color: {colors["surface"]};
    color: {colors["accent"]};
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background-color: {colors["surface_hover"]};
    color: {colors["text"]};
}}

/* Group Box */
QGroupBox {{
    border: 1px solid {colors["border"]};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    color: {colors["text_secondary"]};
    font-weight: 500;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}

/* Slider */
QSlider::groove:horizontal {{
    height: 4px;
    background-color: {colors["border"]};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    width: 20px;
    height: 20px;
    background-color: {colors["accent"]};
    border-radius: 10px;
    margin: -8px 0;
}}

QSlider::handle:horizontal:hover {{
    background-color: {colors["accent_hover"]};
}}

QSlider::add-page:horizontal {{
    background-color: {colors["border"]};
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background-color: {colors["accent"]};
    border-radius: 2px;
}}
"""


_LIGHT_STYLESHEET = _build_stylesheet(_WIN11_LIGHT)
_DARK_STYLESHEET = _build_stylesheet(_WIN11_DARK)
