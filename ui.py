from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from styles import (
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)

from macro import MacroEngine
from config import load_config, save_config, Config



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Keyboard Sender")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.config = load_config()
        self.macro_engine = MacroEngine(self.config)

        self._remaining_seconds = 0
        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._on_countdown_tick)

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(100)
        self._poll_timer.timeout.connect(self._on_poll)

        self._build_ui()
        self._setup_connections()


    def _build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(self._create_header())
        layout.addWidget(self._create_hotkeys_card())
        layout.addWidget(self._create_timer_card())
        layout.addStretch()
        self.status_label = self._create_status()
        layout.addWidget(self.status_label)

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
        layout.setSpacing(10)

        title = QLabel("Горячие клавиши")
        title.setObjectName("Subtitle")

        layout.addWidget(title)

        self.trigger_row = QLabel(f"Запуск — {self.config.trigger_key.upper()}")
        self.stop_row = QLabel(f"Остановка — {self.config.stop_key.upper()}")

        layout.addWidget(self.trigger_row)
        layout.addWidget(self.stop_row)

        return card


    def _create_timer_card(self):

        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)

        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("Таймер автостопа")
        title.setObjectName("Subtitle")

        layout.addWidget(title)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        self.hours_spin = QSpinBox()
        self.hours_spin.setMinimum(0)
        self.hours_spin.setMaximum(23)
        self.hours_spin.setValue(self.config.timer_hours)
        self.hours_spin.setSuffix(" ч")

        self.minutes_spin = QSpinBox()
        self.minutes_spin.setMinimum(0)
        self.minutes_spin.setMaximum(59)
        self.minutes_spin.setValue(self.config.timer_minutes)
        self.minutes_spin.setSuffix(" мин")

        self.seconds_spin = QSpinBox()
        self.seconds_spin.setMinimum(0)
        self.seconds_spin.setMaximum(59)
        self.seconds_spin.setValue(self.config.timer_seconds)
        self.seconds_spin.setSuffix(" сек")

        row_layout.addWidget(self.hours_spin)
        row_layout.addWidget(self.minutes_spin)
        row_layout.addWidget(self.seconds_spin)

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

        self.start_button = QPushButton("Старт")
        self.start_button.setObjectName("PrimaryButton")

        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Стоп")

        layout.addWidget(self.stop_button)

        return widget


    def _setup_connections(self):
        self.start_button.clicked.connect(self._on_start_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.hours_spin.valueChanged.connect(self._on_timer_changed)
        self.minutes_spin.valueChanged.connect(self._on_timer_changed)
        self.seconds_spin.valueChanged.connect(self._on_timer_changed)
        self.macro_engine.started.connect(self._on_macro_started)
        self.macro_engine.stopped.connect(self._on_macro_stopped)

    def _on_timer_changed(self):
        self.config.timer_hours = self.hours_spin.value()
        self.config.timer_minutes = self.minutes_spin.value()
        self.config.timer_seconds = self.seconds_spin.value()
        save_config(self.config)

    def _on_start_clicked(self):
        self.macro_engine.start()

    def _on_stop_clicked(self):
        self._countdown_timer.stop()
        self._poll_timer.stop()
        self.hours_spin.setEnabled(True)
        self.minutes_spin.setEnabled(True)
        self.seconds_spin.setEnabled(True)
        self.macro_engine.stop()

    def _on_poll(self):
        if not self.macro_engine.running:
            self._poll_timer.stop()
            self._countdown_timer.stop()
            self.hours_spin.setEnabled(True)
            self.minutes_spin.setEnabled(True)
            self.seconds_spin.setEnabled(True)
            self.status_label.setText("⚪ Остановлено")

    def _on_countdown_tick(self):
        self._remaining_seconds -= 1
        if self._remaining_seconds <= 0:
            self._countdown_timer.stop()
            self.hours_spin.setEnabled(True)
            self.minutes_spin.setEnabled(True)
            self.seconds_spin.setEnabled(True)
            self.macro_engine.stop()
            return
        self._update_status_with_countdown()

    def _update_status_with_countdown(self):
        h = self._remaining_seconds // 3600
        m = (self._remaining_seconds % 3600) // 60
        s = self._remaining_seconds % 60
        self.status_label.setText(f"🟢 Запущено — осталось {h:02d}:{m:02d}:{s:02d}")

    def _on_macro_started(self):
        total = (
            self.config.timer_hours * 3600
            + self.config.timer_minutes * 60
            + self.config.timer_seconds
        )
        if total > 0:
            self._remaining_seconds = total
            self._update_status_with_countdown()
            self._countdown_timer.start()
            self.hours_spin.setEnabled(False)
            self.minutes_spin.setEnabled(False)
            self.seconds_spin.setEnabled(False)
        else:
            self.status_label.setText("🟢 Запущено")
        self._poll_timer.start()

    def _on_macro_stopped(self):
        self._countdown_timer.stop()
        self.hours_spin.setEnabled(True)
        self.minutes_spin.setEnabled(True)
        self.seconds_spin.setEnabled(True)
        self.status_label.setText("⚪ Остановлено")

    def closeEvent(self, event):
        self._countdown_timer.stop()
        self._poll_timer.stop()
        self.macro_engine.stop()
        self.macro_engine.cleanup()
        super().closeEvent(event)
