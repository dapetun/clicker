from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_DIR = Path.home() / ".clicker"
CONFIG_FILE = CONFIG_DIR / "config.json"

@dataclass
class Config:
    trigger_key: str = "Z"
    stop_key: str = "Q"
    delay: int = 5
    alphabet: str = "qwertyuiopasdfghjklzxcvbnm"


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

        return Config(**data)

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