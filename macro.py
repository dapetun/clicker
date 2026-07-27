import ctypes
import ctypes.wintypes
import threading
import time

import keyboard
from PySide6.QtCore import QObject, Signal

from config import Config

user32 = ctypes.windll.user32

KEYEVENTF_KEYUP = 0x0002

user32.keybd_event.argtypes = [
    ctypes.wintypes.BYTE,
    ctypes.wintypes.BYTE,
    ctypes.wintypes.DWORD,
    ctypes.c_size_t,
]
user32.keybd_event.restype = None

user32.MapVirtualKeyW.argtypes = [ctypes.wintypes.UINT, ctypes.wintypes.UINT]
user32.MapVirtualKeyW.restype = ctypes.wintypes.UINT

keybd_event = user32.keybd_event
MapVirtualKeyW = user32.MapVirtualKeyW


def _send_letter(letter: str) -> None:
    vk = ord(letter.upper())
    scan = MapVirtualKeyW(vk, 0)
    keybd_event(vk, scan, 0, 0)
    keybd_event(vk, scan, KEYEVENTF_KEYUP, 0)


class MacroEngine(QObject):
    started = Signal()
    stopped = Signal()

    def __init__(self, config: Config):
        super().__init__()

        self._config_lock = threading.Lock()
        self._config = config

        self._running = False
        self._lock = threading.Lock()

        self._trigger_thread = None
        self._trigger_alive = False

        self._start_trigger_poll()

    @property
    def running(self) -> bool:
        with self._lock:
            return self._running

    @property
    def config(self) -> Config:
        with self._config_lock:
            return self._config

    @config.setter
    def config(self, value: Config) -> None:
        with self._config_lock:
            self._config = value

    def _filtered_alphabet(self, alphabet: str) -> str:
        with self._config_lock:
            trigger = self._config.trigger_key.lower()
            stop = self._config.stop_key.lower()
        return "".join(
            c for c in alphabet if c.lower() != trigger and c.lower() != stop
        )

    def _start_trigger_poll(self) -> None:
        self._trigger_alive = True
        self._trigger_thread = threading.Thread(
            target=self._trigger_loop, daemon=True
        )
        self._trigger_thread.start()

    def _trigger_loop(self) -> None:
        debounce = False
        while self._trigger_alive:
            try:
                with self._config_lock:
                    trigger_key = self._config.trigger_key.lower()
                if keyboard.is_pressed(trigger_key):
                    if not debounce:
                        debounce = True
                        if not self.running:
                            self.start()
                        else:
                            self.stop()
                else:
                    debounce = False
            except Exception:
                pass
            time.sleep(0.05)

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True

        with self._config_lock:
            alphabet = self._config.alphabet

        self.started.emit()

        threading.Thread(
            target=self._send_loop,
            args=(alphabet,),
            daemon=True,
        ).start()

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                return
            self._running = False

        self.stopped.emit()

    def _send_loop(self, alphabet: str) -> None:
        filtered = self._filtered_alphabet(alphabet)
        stop_key = self.config.stop_key.lower()
        while self.running:
            if keyboard.is_pressed(stop_key):
                with self._lock:
                    self._running = False
                break
            for letter in filtered:
                if not self.running:
                    break
                _send_letter(letter)
            time.sleep(0.005)

    def cleanup(self) -> None:
        self._trigger_alive = False
        with self._lock:
            self._running = False
