import ctypes
import ctypes.wintypes
import sys
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from styles import WINDOW_HEIGHT, WINDOW_WIDTH, THEMES, THEME_LIST, get_theme_colors
from macro import MacroEngine
from config import load_config, save_config

if sys.platform == "win32":
    try:
        _dwmapi = ctypes.windll.dwmapi
        _dwmapi.DwmSetWindowAttribute.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.wintypes.DWORD,
            ctypes.c_void_p,
            ctypes.wintypes.DWORD,
        ]
        _dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long
        _user32 = ctypes.windll.user32
    except Exception:
        _dwmapi = None
        _user32 = None
else:
    _dwmapi = None
    _user32 = None

DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36


def _hex_to_colorref(hex_color: str) -> int:
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return r | (g << 8) | (b << 16)


def _apply_title_bar_color(hwnd: int, theme_key: str):
    if not _dwmapi:
        return
    theme = THEMES.get(theme_key, THEMES["light"])
    title_bg = theme.get("title_bar", "#f5f5f5")
    title_text = theme.get("title_bar_text", "#000000")
    bg_ref = _hex_to_colorref(title_bg)
    txt_ref = _hex_to_colorref(title_text)
    try:
        _dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_CAPTION_COLOR,
            ctypes.byref(ctypes.c_int(bg_ref)),
            ctypes.sizeof(ctypes.c_int),
        )
        _dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_TEXT_COLOR,
            ctypes.byref(ctypes.c_int(txt_ref)),
            ctypes.sizeof(ctypes.c_int),
        )
    except Exception:
        pass


class Spinbox(ctk.CTkFrame):
    def __init__(self, parent, min_val=0, max_val=99, initial=0, suffix="", callback=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.callback = callback
        self._value = initial

        self.entry = ctk.CTkEntry(self, width=60, height=28, justify="center",
                                   font=ctk.CTkFont(size=13), corner_radius=6)
        self.entry.pack(side="left", padx=(0, 4))
        self.entry.insert(0, str(initial))
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Return>", self._on_focus_out)

        self.suffix_label = ctk.CTkLabel(self, text=suffix, font=ctk.CTkFont(size=12),
                                          width=30, anchor="w")
        self.suffix_label.pack(side="left")

    def _on_focus_out(self, event=None):
        try:
            v = int(self.entry.get())
            v = max(self.min_val, min(self.max_val, v))
        except ValueError:
            v = self._value
        self._value = v
        self.entry.delete(0, "end")
        self.entry.insert(0, str(v))
        if self.callback:
            self.callback()

    def get(self) -> int:
        return self._value

    def set_state(self, state: str):
        self.entry.configure(state=state)


class MainWindow(ctk.CTk):
    def __init__(self, config=None):
        super().__init__()

        self.config = config or load_config()
        self.macro_engine = MacroEngine(
            self.config,
            on_started=self._on_macro_started,
            on_stopped=self._on_macro_stopped,
        )

        self.title("Keyboard Sender")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(320, 360)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._remaining_seconds = 0
        self._countdown_active = False
        self._poll_active = False

        self._build_ui()
        self._apply_theme(self.config.theme)

        self.after(100, self._apply_dwm)

    def _apply_dwm(self):
        hwnd = self.winfo_id()
        _apply_title_bar_color(hwnd, self.config.theme)

    def _build_ui(self):
        self.container = ctk.CTkFrame(self, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self._build_title_bar()
        self._build_content()

    def _build_title_bar(self):
        self.title_bar = ctk.CTkFrame(self.container, height=36, corner_radius=0)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)

        self.about_btn = ctk.CTkButton(self.title_bar, text="О приложении",
                                        width=0, height=24,
                                        corner_radius=4,
                                        command=self._on_about,
                                        font=ctk.CTkFont(size=12))
        self.about_btn.pack(side="right", padx=(0, 8), pady=6)

        self.theme_btn = ctk.CTkButton(self.title_bar, text="Тема",
                                        width=50, height=24,
                                        corner_radius=4,
                                        command=self._on_theme_menu,
                                        font=ctk.CTkFont(size=12))
        self.theme_btn.pack(side="right", padx=(0, 4), pady=6)

        self._theme_menu = None

    def _build_content(self):
        self.content = ctk.CTkFrame(self.container, corner_radius=0)
        self.content.pack(fill="both", expand=True, padx=24, pady=(16, 24))

        self._build_header()
        self._build_hotkeys_card()
        self._build_timer_card()

        spacer = ctk.CTkFrame(self.content, height=1, fg_color="transparent")
        spacer.pack(fill="x", pady=(8, 0))

        self._build_status()
        self._build_buttons()

    def _build_header(self):
        self.title_label = ctk.CTkLabel(self.content, text="Keyboard Sender",
                                         font=ctk.CTkFont(size=20, weight="bold"),
                                         anchor="w")
        self.title_label.pack(fill="x", pady=(0, 2))

        self.subtitle_label = ctk.CTkLabel(self.content,
                                            text="Минималистичная утилита для клавиатурного макроса",
                                            font=ctk.CTkFont(size=13), anchor="w")
        self.subtitle_label.pack(fill="x", pady=(0, 12))

    def _build_hotkeys_card(self):
        self.hotkeys_card = ctk.CTkFrame(self.content, corner_radius=8)
        self.hotkeys_card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(self.hotkeys_card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        self.hotkeys_title = ctk.CTkLabel(inner, text="Горячие клавиши",
                                           font=ctk.CTkFont(size=14, weight="bold"),
                                           anchor="w")
        self.hotkeys_title.pack(fill="x", pady=(0, 8))

        cols = ctk.CTkFrame(inner, fg_color="transparent")
        cols.pack(fill="x")
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)

        self.trigger_label = ctk.CTkLabel(cols,
                                           text=f"Запуск — {self.config.trigger_key.upper()}",
                                           font=ctk.CTkFont(size=13))
        self.trigger_label.grid(row=0, column=0, sticky="e", padx=(0, 24))

        self.stop_label = ctk.CTkLabel(cols,
                                        text=f"Остановка — {self.config.stop_key.upper()}",
                                        font=ctk.CTkFont(size=13))
        self.stop_label.grid(row=0, column=1, sticky="w", padx=(24, 0))

    def _build_timer_card(self):
        self.timer_card = ctk.CTkFrame(self.content, corner_radius=8)
        self.timer_card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(self.timer_card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        self.timer_title = ctk.CTkLabel(inner, text="Таймер автостопа",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         anchor="w")
        self.timer_title.pack(fill="x", pady=(0, 8))

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)
        row.columnconfigure(2, weight=1)

        self.hours_spin = Spinbox(row, min_val=0, max_val=23,
                                   initial=self.config.timer_hours,
                                   suffix="ч", callback=self._on_timer_changed)
        self.hours_spin.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.minutes_spin = Spinbox(row, min_val=0, max_val=59,
                                     initial=self.config.timer_minutes,
                                     suffix="мин", callback=self._on_timer_changed)
        self.minutes_spin.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        self.seconds_spin = Spinbox(row, min_val=0, max_val=59,
                                     initial=self.config.timer_seconds,
                                     suffix="сек", callback=self._on_timer_changed)
        self.seconds_spin.grid(row=0, column=2, sticky="ew")

    def _build_status(self):
        self.status_label = ctk.CTkLabel(self.content, text="\u25cf Остановлено",
                                          font=ctk.CTkFont(size=13), anchor="w")
        self.status_label.pack(fill="x", pady=(0, 8))

    def _build_buttons(self):
        btn_row = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_row.pack(fill="x")

        self.start_btn = ctk.CTkButton(btn_row, text="Старт", height=36,
                                        corner_radius=6,
                                        command=self._on_start,
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.stop_btn = ctk.CTkButton(btn_row, text="Стоп", height=36,
                                       corner_radius=6,
                                       command=self._on_stop,
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _on_start(self):
        self.macro_engine.start()

    def _on_stop(self):
        self._countdown_active = False
        self._poll_active = False
        self._update_stopped()
        self.macro_engine.stop()

    def _on_macro_started(self):
        total = (self.config.timer_hours * 3600
                 + self.config.timer_minutes * 60
                 + self.config.timer_seconds)
        if total > 0:
            self._remaining_seconds = total
            self._countdown_active = True
            self._update_countdown_label()
            self._schedule_countdown()
            self.hours_spin.set_state("disabled")
            self.minutes_spin.set_state("disabled")
            self.seconds_spin.set_state("disabled")
        else:
            self.after(0, lambda: self.status_label.configure(text="\u25cf Запущено"))
        self._poll_active = True
        self._schedule_poll()

    def _on_macro_stopped(self):
        self._countdown_active = False
        self._poll_active = False
        self.after(0, self._update_stopped)

    def _update_stopped(self):
        self.status_label.configure(text="\u25cf Остановлено")
        self.hours_spin.set_state("normal")
        self.minutes_spin.set_state("normal")
        self.seconds_spin.set_state("normal")

    def _schedule_countdown(self):
        if self._countdown_active:
            self.after(1000, self._countdown_tick)

    def _countdown_tick(self):
        if not self._countdown_active:
            return
        self._remaining_seconds -= 1
        if self._remaining_seconds <= 0:
            self._countdown_active = False
            self._poll_active = False
            self.macro_engine.stop()
            self.after(0, self._update_stopped)
            return
        self._update_countdown_label()
        self._schedule_countdown()

    def _update_countdown_label(self):
        h = self._remaining_seconds // 3600
        m = (self._remaining_seconds % 3600) // 60
        s = self._remaining_seconds % 60
        self.after(0, lambda: self.status_label.configure(
            text=f"\u25cf Запущено \u2014 осталось {h:02d}:{m:02d}:{s:02d}"))

    def _schedule_poll(self):
        if self._poll_active:
            self.after(100, self._poll_tick)

    def _poll_tick(self):
        if not self._poll_active:
            return
        if not self.macro_engine.running:
            self._poll_active = False
            self._countdown_active = False
            self.after(0, self._update_stopped)
            return
        self._schedule_poll()

    def _on_timer_changed(self):
        self.config.timer_hours = self.hours_spin.get()
        self.config.timer_minutes = self.minutes_spin.get()
        self.config.timer_seconds = self.seconds_spin.get()
        save_config(self.config)

    def _on_about(self):
        messagebox.showinfo(
            "О приложении",
            "Keyboard Sender v1.0\n\n"
            "Минималистичная утилита для клавиатурного макроса.\n\n"
            "Лицензия MIT (\u00a9 2026 dapetun). Разрешено свободно\n"
            "использовать, копировать, изменять и\n"
            "распространять программу при сохранении\n"
            "уведомления об авторских правах и лицензии.\n\n"
            "Программа предоставляется \u00abкак есть\u00bb, без каких-либо\n"
            "гарантий. Автор не нес\u0430т ответственности за любые\n"
            "последствия её использования."
        )

    def _on_theme_menu(self):
        if self._theme_menu is not None:
            self._theme_menu.destroy()
            self._theme_menu = None
            return

        colors = get_theme_colors(self.config.theme)

        self._theme_menu = tk.Toplevel(self)
        self._theme_menu.wm_overrideredirect(True)
        self._theme_menu.wm_attributes("-topmost", True)

        x = self.theme_btn.winfo_rootx()
        y = self.theme_btn.winfo_rooty() + self.theme_btn.winfo_height()
        self._theme_menu.wm_geometry(f"+{x}+{y}")

        frame = tk.Frame(self._theme_menu, bg=colors["card_bg"],
                          bd=1, relief="solid", highlightbackground=colors["card_border"])
        frame.pack(fill="both", expand=True)

        for key in THEME_LIST:
            name = THEMES[key]["name"]

            btn = tk.Label(frame, text=name, anchor="w", padx=12, pady=4,
                            bg=colors["card_bg"], fg=colors["text"],
                            font=("Segoe UI", 11), cursor="hand2")
            btn.pack(fill="x")

            btn.bind("<Enter>", lambda e, w=btn, c=colors: w.configure(bg=c["card_border"]))
            btn.bind("<Leave>", lambda e, w=btn, c=colors: w.configure(bg=c["card_bg"]))
            btn.bind("<Button-1>", lambda e, k=key: self._select_theme(k))

        self.bind("<Button-1>", self._close_theme_menu)

    def _close_theme_menu(self, event=None):
        if self._theme_menu is not None:
            self._theme_menu.destroy()
            self._theme_menu = None

    def _select_theme(self, theme_key: str):
        self._close_theme_menu()
        self._apply_theme(theme_key)

    def _apply_theme(self, theme_key: str):
        self.config.theme = theme_key
        save_config(self.config)

        colors = get_theme_colors(theme_key)

        self.configure(fg_color=colors["bg"])
        self.container.configure(fg_color=colors["bg"])
        self.title_bar.configure(fg_color=colors["title_bar"])
        self.content.configure(fg_color=colors["bg"])

        self.title_label.configure(text_color=colors["text_title"])
        self.subtitle_label.configure(text_color=colors["text_subtitle"])

        self.hotkeys_card.configure(fg_color=colors["card_bg"], border_color=colors["card_border"])
        self.hotkeys_title.configure(text_color=colors["text_title"])
        self.trigger_label.configure(text_color=colors["text"])
        self.stop_label.configure(text_color=colors["text"])

        self.timer_card.configure(fg_color=colors["card_bg"], border_color=colors["card_border"])
        self.timer_title.configure(text_color=colors["text_title"])

        self.status_label.configure(text_color=colors["text"])

        self.start_btn.configure(fg_color=colors["accent"], hover_color=colors["accent_hover"],
                                  text_color="white")
        self.stop_btn.configure(fg_color=colors["card_bg"], border_color=colors["card_border"],
                                 text_color=colors["text"], hover_color=colors["card_border"])

        self.about_btn.configure(fg_color="transparent", text_color=colors["text_subtitle"],
                                 hover_color=colors["card_border"])
        self.theme_btn.configure(fg_color=colors["card_bg"], text_color=colors["text"],
                                 border_color=colors["card_border"], hover_color=colors["card_border"])

        for spin in [self.hours_spin, self.minutes_spin, self.seconds_spin]:
            spin.configure(fg_color="transparent")
            spin.entry.configure(fg_color=colors["input_bg"], border_color=colors["input_border"],
                                  text_color=colors["text"])
            spin.suffix_label.configure(text_color=colors["text_subtitle"])

        hwnd = self.winfo_id()
        _apply_title_bar_color(hwnd, theme_key)

    def _on_close(self):
        self._countdown_active = False
        self._poll_active = False
        self.macro_engine.stop()
        self.macro_engine.cleanup()
        self.destroy()
