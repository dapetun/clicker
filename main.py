import sys
from pathlib import Path

import customtkinter as ctk

from config import load_config
from styles import get_theme_colors
from ui import MainWindow


def _find_icon() -> Path | None:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    for name in ("icon.ico", "icon.png"):
        p = base / name
        if p.exists():
            return p
    return None


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    config = load_config()
    colors = get_theme_colors(config.theme)
    if colors.get("bg", "#f5f5f5").startswith("#") and int(colors["bg"][1:3], 16) < 0x80:
        ctk.set_appearance_mode("dark")

    window = MainWindow(config)

    icon_path = _find_icon()
    if icon_path:
        try:
            window.iconbitmap(str(icon_path))
        except Exception:
            pass

    window.mainloop()


if __name__ == "__main__":
    main()
