from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from styles import (
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Keyboard Sender")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self._build_ui()


    def _build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        layout.addWidget(self._create_header())
        layout.addWidget(self._create_hotkeys_card())
        layout.addWidget(self._create_settings_card())
        layout.addStretch()
        layout.addWidget(self._create_status())
        layout.addWidget(self._create_buttons())


    def _create_header(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title = QLabel("Keyboard Sender")
        title.setObjectName("Title")

        subtitle = QLabel("Минималистичная утилита для клавиатурного макроса")
        subtitle.setObjectName("Secondary")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        return widget

    def _create_hotkeys_card(self):

        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)

        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        title = QLabel("Горячие клавиши")
        title.setObjectName("Subtitle")

        layout.addWidget(title)

        layout.addWidget(
            self._create_row("Запуск", "Z")
        )

        layout.addWidget(
            self._create_row("Остановка", "Q")
        )

        return card


    def _create_settings_card(self):

        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)

        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        title = QLabel("Настройки")
        title.setObjectName("Subtitle")

        layout.addWidget(title)

        row = QWidget()

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Задержка")

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(100)
        slider.setValue(5)

        value = QLabel("5 мс")
        value.setObjectName("Secondary")

        row_layout.addWidget(label)
        row_layout.addWidget(slider)
        row_layout.addWidget(value)

        layout.addWidget(row)

        return card


    def _create_status(self):

        label = QLabel("⚪ Остановлено")
        label.setObjectName("Body")

        return label


    def _create_buttons(self):

        widget = QWidget()

        layout = QHBoxLayout(widget)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        start = QPushButton("Старт")
        start.setObjectName("PrimaryButton")

        stop = QPushButton("Стоп")

        layout.addWidget(start)
        layout.addWidget(stop)

        return widget


    def _create_row(self, title, button_text):

        widget = QWidget()

        layout = QHBoxLayout(widget)

        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(title)

        button = QPushButton(button_text)
        button.setFixedWidth(70)

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(button)

        return widget