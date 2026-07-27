from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_DIR = Path.home() / ".clicker"
CONFIG_FILE = CONFIG_DIR / "config.json"

@dataclass
class Config:
    trigger_key: str = "f6"
    stop_key: str = "f7"
    alphabet: str = "qwertyuiopasdfghjklzxcvbnm"
    timer_hours: int = 0
    timer_minutes: int = 0
    timer_seconds: int = 0


def load_config() -> Config:
    """
    Загружает настройки.
    """

    CONFIG_DIR.mkdir(exist_ok=True)

    if not CONFIG_FILE.exists():
        return Config()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return Config()

        trigger_key = str(data.get("trigger_key", "f6")).lower() or "f6"
        stop_key = str(data.get("stop_key", "f7")).lower() or "f7"

        if len(trigger_key) == 1:
            trigger_key = "f6"
        if len(stop_key) == 1:
            stop_key = "f7"

        alphabet = str(data.get("alphabet", "qwertyuiopasdfghjklzxcvbnm"))

        timer_hours = data.get("timer_hours", 0)
        if not isinstance(timer_hours, int) or timer_hours < 0 or timer_hours > 23:
            timer_hours = 0

        timer_minutes = data.get("timer_minutes", 0)
        if not isinstance(timer_minutes, int) or timer_minutes < 0 or timer_minutes > 59:
            timer_minutes = 0

        timer_seconds = data.get("timer_seconds", 0)
        if not isinstance(timer_seconds, int) or timer_seconds < 0 or timer_seconds > 59:
            timer_seconds = 0

        return Config(
            trigger_key=trigger_key,
            stop_key=stop_key,
            alphabet=alphabet,
            timer_hours=timer_hours,
            timer_minutes=timer_minutes,
            timer_seconds=timer_seconds,
        )

    except Exception:
        return Config()


def save_config(config: Config) -> None:
    """
    Сохраняет настройки.
    """

    CONFIG_DIR.mkdir(exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(
            asdict(config),
            file,
            indent=4,
            ensure_ascii=False,
        )