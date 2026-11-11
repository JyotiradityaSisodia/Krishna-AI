import sys
import os

# Fix import paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication
from main_window import KrishnaWindow


def main():
    app = QApplication(sys.argv)
    window = KrishnaWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()