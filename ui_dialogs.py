from __future__ import annotations
import platform
import webbrowser
import tkinter as tk
from typing import TYPE_CHECKING

from config import Theme, LangData, AppConfig
from updater import check_update_async, UpdateInfo, DOWNLOAD_PAGE
from ui_widgets import FlatButton

if TYPE_CHECKING:
    from ui_main import MainWindow

APP_VERSION = "2.1.0"


def _get_pygame_version() -> str:
    try:
        import pygame.version
        return pygame.version.ver
    except Exception:
        pass
    try:
        from importlib.metadata import version
        return version("pygame")
    except Exception:
        return "?"


LICENSES = [
    {"name": "Python",           "version_fn": platform.python_version,       "license": "PSF License"},
    {"name": "pygame",           "version_fn": _get_pygame_version,            "license": "LGPL v2.1"},
    {"name": "tkinter / Tcl-Tk", "version_fn": lambda: str(tk.TkVersion),     "license": "Tcl/Tk License (BSD-like)"},
    {"name": "Noto Sans JP",     "version_fn": lambda: "20231101",             "license": "SIL OFL 1.1"},
]


class AboutDialog(tk.Toplevel):
    def __init__(self, parent: "MainWindow", theme: Theme, lang: LangData,
                 config: AppConfig, auto_check: bool) -> None:
        super().__init__(parent)
        self._config = config
        self._lang = lang
        self._parent_win = parent
        L = lang
        self.title(L.t("about", "title"))
        self.resizable(False, False)
        self.configure(bg=theme.bg)
        self.transient(parent)
        self.grab_set()
        t = theme

        tk.Label(self, text="LoadWhistler",
                 bg=t.bg, fg=t.fg, font=("", 14, "bold")).pack(pady=(16, 0))
        tk.Label(self, text=L.t("about", "version", ver=APP_VERSION),
                 bg=t.bg, fg=t.fg_dim, font=("", 9)).pack()
        tk.Label(self, text="https://abatbeliever.net/software/bin/LoadWhistler/",
                 bg=t.bg, fg=t.fg, font=("", 9)).pack(pady=(4, 0))
        tk.Label(self, text=L.t("about", "description"),
                 bg=t.bg, fg=t.fg, font=("", 9)).pack(pady=(6, 0))
        tk.Label(self, text=L.t("about", "formats"),
                 bg=t.bg, fg=t.fg_dim, font=("", 8)).pack(pady=(2, 8))
        tk.Frame(self, bg=t.border, height=1).pack(fill="x", padx=16)

        tk.Label(self, text=L.t("about", "libs_title"),
                 bg=t.bg, fg=t.fg_dim, font=("", 8, "bold"), anchor="w",
                 ).pack(fill="x", padx=16, pady=(8, 2))

        lib_frame = tk.Frame(self, bg=t.bg2)
        lib_frame.pack(fill="x", padx=16, pady=(0, 8))

        col_titles = [L.t("about", "col_library"),
                      L.t("about", "col_version"),
                      L.t("about", "col_license")]
        col_widths = [20, 10, 24]
        for col, (h, w) in enumerate(zip(col_titles, col_widths)):
            tk.Label(lib_frame, text=h, bg=t.bg2, fg=t.fg_dim,
                     font=("", 8, "bold"), width=w, anchor="w",
                     padx=4, pady=3).grid(row=0, column=col, sticky="w")
        tk.Frame(lib_frame, bg=t.border, height=1).grid(
            row=1, column=0, columnspan=3, sticky="ew", padx=2)

        for ri, lib in enumerate(LICENSES, start=2):
            ver = lib["version_fn"]()
            for col, (val, w) in enumerate(
                zip([lib["name"], ver, lib["license"]], col_widths)
            ):
                tk.Label(lib_frame, text=val, bg=t.bg2, fg=t.fg,
                         font=("", 8), width=w, anchor="w",
                         padx=4, pady=2).grid(row=ri, column=col, sticky="w")

        tk.Frame(self, bg=t.border, height=1).pack(fill="x", padx=16)

        upd_frame = tk.Frame(self, bg=t.bg)
        upd_frame.pack(fill="x", padx=16, pady=(8, 0))

        self._auto_check_var = tk.BooleanVar(value=auto_check)
        tk.Checkbutton(
            upd_frame,
            text=L.t("about", "auto_update_check"),
            variable=self._auto_check_var,
            bg=t.bg, fg=t.fg,
            activebackground=t.bg, activeforeground=t.fg,
            selectcolor=t.bg3,
            font=("", 9),
            command=self._on_auto_check_toggle,
        ).pack(side="left")

        btn_row = tk.Frame(self, bg=t.bg)
        btn_row.pack(pady=(6, 0))

        self._btn_check_upd = FlatButton(
            btn_row, t,
            text=L.t("about", "check_update"),
            command=self._manual_check_update,
        )
        self._btn_check_upd.pack(side="left", padx=4)

        FlatButton(self, theme, text=L.t("about", "close"),
                   width=10, command=self.destroy).pack(pady=10)

        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")

    def _on_auto_check_toggle(self) -> None:
        val = "1" if self._auto_check_var.get() else "0"
        self._config.set("auto_update_check", val)
        self._config.save()

    def _manual_check_update(self) -> None:
        self._btn_check_upd.configure(state="disabled")
        check_update_async(APP_VERSION, self._on_manual_result)

    def _on_manual_result(self, info: UpdateInfo) -> None:
        self.after(0, lambda: self._show_update_dialog(info, manual=True))

    def _show_update_dialog(self, info: UpdateInfo, manual: bool = False) -> None:
        self._btn_check_upd.configure(state="normal")
        L = self._lang
        t = self._parent_win._theme  # type: ignore[attr-defined]

        if info.error:
            UpdateDialog(self, t, L,
                         title=L.t("update", "title_error"),
                         message=L.t("update", "check_failed", reason=info.error),
                         show_download=False)
            return

        if info.available:
            msg = L.t("update", "available", ver=info.latest_version)
            if info.changelog:
                msg += "\n\n" + info.changelog
            UpdateDialog(self, t, L,
                         title=L.t("update", "title_available"),
                         message=msg,
                         show_download=True)
        elif manual:
            UpdateDialog(self, t, L,
                         title=L.t("update", "title_latest"),
                         message=L.t("update", "up_to_date", ver=APP_VERSION),
                         show_download=False)


class UpdateDialog(tk.Toplevel):
    """更新確認結果を表示するシンプルなダイアログ。"""

    def __init__(self, parent: tk.Toplevel, theme: Theme, lang: LangData,
                 title: str, message: str, show_download: bool) -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=theme.bg)
        self.transient(parent)
        self.grab_set()
        t = theme
        L = lang

        tk.Label(
            self, text=message,
            bg=t.bg, fg=t.fg, font=("", 9),
            justify="left", wraplength=340, anchor="w",
        ).pack(fill="both", expand=True, padx=20, pady=(16, 8))

        tk.Frame(self, bg=t.border, height=1).pack(fill="x", padx=16)

        btn_row = tk.Frame(self, bg=t.bg)
        btn_row.pack(pady=10)

        if show_download:
            FlatButton(
                btn_row, t,
                text=L.t("update", "open_download"),
                command=lambda: (webbrowser.open(DOWNLOAD_PAGE), self.destroy()),
            ).pack(side="left", padx=6)

        FlatButton(btn_row, t, text=L.t("about", "close"),
                   width=8, command=self.destroy).pack(side="left", padx=6)

        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")
