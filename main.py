import sys
from PySide6.QtWidgets import QApplication
from styles import GLOBAL_STYLE
from ui import MainWindow


def main() -> None:
    app = QApplication(sys.argv)

    app.setStyleSheet(GLOBAL_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()