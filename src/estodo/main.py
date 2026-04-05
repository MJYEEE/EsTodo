"""EsTodo - Main entry point"""

import sys
from pathlib import Path

# Add src to path if running directly
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from estodo.database import Database
from estodo.views.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("EsTodo")
    app.setOrganizationName("EsTodo")

    # Set default font - support Chinese characters
    font = QFont()
    font.setPointSize(10)
    # Try common Chinese fonts in order of priority
    chinese_fonts = [
        "Microsoft YaHei",  # 微软雅黑
        "SimHei",           # 黑体
        "WenQuanYi Micro Hei",  # 文泉驿微米黑
        "Noto Sans CJK SC", # Noto CJK 简体中文
        "Source Han Sans SC", # 思源黑体
        "Sans Serif",       # 通用无衬线
    ]
    for font_name in chinese_fonts:
        font.setFamily(font_name)
        if font.exactMatch():
            break
    app.setFont(font)

    # Enable high DPI scaling
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Initialize database
    db = Database()

    # Create and show main window
    window = MainWindow(db)
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
