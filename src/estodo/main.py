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

    # Set default font
    font = QFont("Noto Sans", 10)
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
