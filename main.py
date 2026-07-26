import sys
from PySide6.QtWidgets import QApplication
from styles import load_fonts, GLOBAL_STYLE
from ui import MainWindow


def main() -> None:
    app = QApplication(sys.argv)

    load_fonts()

    app.setStyleSheet(GLOBAL_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()