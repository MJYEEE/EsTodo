"""EsTodo - Main entry point - Windows 11 optimized (PyQt6 compatible)"""

import sys
import os
from pathlib import Path

# ============================================
# Environment variables must be set BEFORE Qt import
# ============================================

# WSL / Linux: force xcb instead of wayland
if sys.platform.startswith("linux"):
    os.environ["QT_QPA_PLATFORM"] = "xcb"

# Add src to path if running directly
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon    

from estodo.database import Database
from estodo.views.main_window import MainWindow


def main():
    """Main application entry point - PyQt6 compatible"""

    # Windows-specific optimizations
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EsTodo.App")
        except (AttributeError, ImportError):
            pass

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("EsTodo")
    app.setOrganizationName("EsTodo")

    # 设置窗口图标
    # 获取程序运行的根目录
    base_path = Path(__file__).parent.parent.parent
    icon_path = base_path / "assets" / "icon.ico"

    # 设置左上角图标 + 任务栏图标
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Qt6 supports this rounding policy API
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Font configuration
    font = QFont()
    font.setPointSize(10)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)

    font_families = [
        "Segoe UI Variable Display",
        "Segoe UI Variable Text",
        "Segoe UI",
        "Microsoft YaHei UI",
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "WenQuanYi Micro Hei",
        "Sans Serif",
    ]

    for font_name in font_families:
        font.setFamily(font_name)
        app.setFont(font)
        # 这里只是尽量设置，不强依赖 exactMatch
        break

    # Initialize database
    db = Database()

    # Create and show main window
    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()