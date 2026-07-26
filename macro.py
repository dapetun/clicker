import threading
import time

import keyboard
from PySide6.QtCore import QObject, Signal

from config import Config


class MacroEngine(QObject):
    """
    Движок макроса.

    Работает в отдельном потоке и уведомляет интерфейс
    о смене состояния через Qt-сигналы.
    """

    started = Signal()
    stopped = Signal()

    def __init__(self, config: Config):
        super().__init__()

        self.config = config

        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    @property
    def running(self) -> bool:
        with self._lock:
            return self._running

    def start(self) -> None:
        with self._lock:
            if self._running:
                return

            self._running = True

        self.started.emit()

        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                return

            self._running = False

        self.stopped.emit()

    def _worker(self) -> None:
        while self.running:

            if keyboard.is_pressed(self.config.stop_key):
                self.stop()
                break

            if keyboard.is_pressed(self.config.trigger_key):

                for letter in self.config.alphabet:
                    keyboard.send(letter)

                time.sleep(self.config.delay / 1000)

            time.sleep(0.01)