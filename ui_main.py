from __future__ import annotations
import os
import sys
import platform
import base64
import webbrowser
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Optional

from file_scanner import Group, scan_lw_files
from player import Player, PlayMode
from theme import Theme, DARK, LIGHT, THEMES
from i18n_manager import (
    LangData, AppConfig, scan_languages, load_language,
    resolve_initial_language, get_base_dir,
)
from updater import check_update, check_update_async, UpdateInfo, DOWNLOAD_PAGE

APP_VERSION = "2.0.0"
ICON_B64: str = "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"

print(f"LoadWhistler v{APP_VERSION}\nhttps://abatbeliever/software/bin/LoadWhistler/\n")


def _patch_default_fonts(root: tk.Tk, base_dir: str) -> None:
    """
    font/noto.ttf が存在すればそれを読み込んで全ウィジェットに適用。
    なければシステムの日本語フォントにフォールバック。
    """
    family = ""

    bundled = os.path.join(base_dir, "font", "noto.ttf")
    if os.path.isfile(bundled):
        try:
            root.tk.call("font", "create", "_lw_noto_check")
        except Exception:
            pass
        try:
            from ctypes import windll  # Windows専用パス（失敗しても続行）
            windll.gdi32.AddFontResourceExW(bundled, 0x10, 0)
        except Exception:
            pass
        try:
            # クロスプラットフォーム: Tkのfont measureでロード確認
            root.tk.call("font", "create", "_lw_noto",
                         "-family", "Noto Sans JP", "-size", "10")
            root.tk.call("font", "delete", "_lw_noto")
            family = "Noto Sans JP"
        except Exception:
            pass

        if not family:
            # Tk 8.6+: source経由でフォントファイルを直接登録
            try:
                root.tk.call("lappend", "::auto_path", "")
                import tkinter.font as _f
                _test = _f.Font(root, family="Noto Sans JP", size=10)
                _test.measure("A")
                family = "Noto Sans JP"
                _test.delete()
            except Exception:
                pass

    # システムフォントへフォールバック
    if not family:
        candidates = [
            "Noto Sans CJK JP", "Noto Sans JP",
            "IPAGothic", "IPAPGothic",
            "VL Gothic", "TakaoGothic",
            "WenQuanYi Micro Hei",
        ]
        available = set(tkfont.families())
        for f in candidates:
            if f in available:
                family = f
                break

    if not family:
        return

    for name in ("TkDefaultFont", "TkTextFont", "TkFixedFont",
                 "TkMenuFont", "TkHeadingFont", "TkCaptionFont"):
        try:
            tkfont.nametofont(name).configure(family=family)
        except Exception:
            pass

def fmt_time(seconds: float) -> str:
    s = max(0, int(seconds))
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


class FlatButton(tk.Button):
    def __init__(self, master, theme: Theme, text="", width=None, command=None, **kw):
        cfg = dict(
            text=text,
            bg=theme.btn_bg, fg=theme.btn_fg,
            activebackground=theme.btn_hover, activeforeground=theme.btn_fg,
            relief="flat", bd=0, font=("", 9), cursor="hand2",
            command=command, padx=6, pady=2,
        )
        if width:
            cfg["width"] = width
        cfg.update(kw)
        super().__init__(master, **cfg)

    def retheme(self, t: Theme) -> None:
        self.configure(
            bg=t.btn_bg, fg=t.btn_fg,
            activebackground=t.btn_hover, activeforeground=t.btn_fg,
        )


class LangDropdown(tk.Frame):

    def __init__(self, master, theme: Theme,
                 languages: dict[str, str],   # {code: filepath}
                 current_code: str,
                 on_change,                    # callback(code: str, lang: LangData)
                 **kw):
        super().__init__(master, bg=theme.bg2, **kw)
        self._theme = theme
        self._languages = languages            # code -> filepath
        self._on_change = on_change
        self._popup: Optional[tk.Toplevel] = None

        self._names: dict[str, str] = {}
        for code, path in languages.items():
            ld = load_language(path)
            self._names[code] = ld.name if ld else code

        self._current_code = current_code

        self._btn = FlatButton(self, theme,
                               text=self._display_text(),
                               command=self._toggle_popup)
        self._btn.pack(side="left")

    def _display_text(self) -> str:
        name = self._names.get(self._current_code, self._current_code)
        return f"  {name} ▾"

    def set_current(self, code: str) -> None:
        self._current_code = code
        self._btn.configure(text=self._display_text())

    def retheme(self, t: Theme) -> None:
        self._theme = t
        self.configure(bg=t.bg2)
        self._btn.retheme(t)

    def _toggle_popup(self) -> None:
        if self._popup and self._popup.winfo_exists():
            self._close_popup()
            return
        self._open_popup()

    def _open_popup(self) -> None:
        t = self._theme
        popup = tk.Toplevel(self)
        popup.overrideredirect(True) 
        popup.configure(bg=t.border)
        popup.attributes("-topmost", True)

        self.update_idletasks()
        bx = self._btn.winfo_rootx()
        by = self._btn.winfo_rooty() + self._btn.winfo_height()
        popup.geometry(f"+{bx}+{by}")

        inner = tk.Frame(popup, bg=t.bg3, bd=0)
        inner.pack(padx=1, pady=1)

        for code, name in self._names.items():
            is_sel = (code == self._current_code)
            bg = t.select_bg if is_sel else t.bg3
            fg = t.select_fg if is_sel else t.fg
            lbl = tk.Label(
                inner, text=f"  {name}  ",
                bg=bg, fg=fg,
                font=("", 9), anchor="w", cursor="hand2",
                padx=4, pady=3,
            )
            lbl.pack(fill="x")
            lbl.bind("<Enter>",
                     lambda e, w=lbl: w.configure(bg=t.accent, fg="white"))
            lbl.bind("<Leave>",
                     lambda e, w=lbl, c=code: w.configure(
                         bg=t.select_bg if c == self._current_code else t.bg3,
                         fg=t.select_fg if c == self._current_code else t.fg,
                     ))
            lbl.bind("<Button-1>",
                     lambda e, c=code: self._select(c))

        self._popup = popup
        popup.bind("<FocusOut>", lambda e: self._close_popup())
        popup.focus_set()

    def _close_popup(self) -> None:
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
        self._popup = None

    def _select(self, code: str) -> None:
        self._close_popup()
        if code == self._current_code:
            return
        path = self._languages.get(code)
        if not path:
            return
        lang = load_language(path)
        if lang:
            self._current_code = code
            self._btn.configure(text=self._display_text())
            self._on_change(code, lang)


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
    {"name": "Python",          "version_fn": platform.python_version,        "license": "PSF License"},
    {"name": "pygame",          "version_fn": _get_pygame_version,             "license": "LGPL v2.1"},
    {"name": "tkinter / Tcl-Tk","version_fn": lambda: str(tk.TkVersion),      "license": "Tcl/Tk License (BSD-like)"},
    {"name": "Noto Sans JP",    "version_fn": lambda: "20231101",              "license": "SIL OFL 1.1"},
]


class AboutDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, theme: Theme, lang: LangData,
                 config: "AppConfig", auto_check: bool) -> None:
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

        tk.Label(self, text="LoadWhistler",      bg=t.bg, fg=t.fg,
                 font=("", 14, "bold")).pack(pady=(16, 0))
        tk.Label(self, text=L.t("about","version", ver=APP_VERSION),
                 bg=t.bg, fg=t.fg_dim, font=("", 9)).pack()
        tk.Label(self, text="https://abatbeliever.net/software/bin/LoadWhistler/",
                 bg=t.bg, fg=t.fg, font=("", 9)).pack(pady=(4, 0))
        tk.Label(self, text=L.t("about","description"),
                 bg=t.bg, fg=t.fg, font=("", 9)).pack(pady=(6, 0))
        tk.Label(self, text=L.t("about","formats"),
                 bg=t.bg, fg=t.fg_dim, font=("", 8)).pack(pady=(2, 8))
        tk.Frame(self, bg=t.border, height=1).pack(fill="x", padx=16)

        tk.Label(self, text=L.t("about","libs_title"),
                 bg=t.bg, fg=t.fg_dim, font=("", 8, "bold"), anchor="w"
                 ).pack(fill="x", padx=16, pady=(8, 2))

        lib_frame = tk.Frame(self, bg=t.bg2)
        lib_frame.pack(fill="x", padx=16, pady=(0, 8))

        col_titles = [L.t("about","col_library"),
                      L.t("about","col_version"),
                      L.t("about","col_license")]
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
        chk = tk.Checkbutton(
            upd_frame,
            text=L.t("about", "auto_update_check"),
            variable=self._auto_check_var,
            bg=t.bg, fg=t.fg,
            activebackground=t.bg, activeforeground=t.fg,
            selectcolor=t.bg3,
            font=("", 9),
            command=self._on_auto_check_toggle,
        )
        chk.pack(side="left")

        btn_row = tk.Frame(self, bg=t.bg)
        btn_row.pack(pady=(6, 0))

        self._btn_check_upd = FlatButton(
            btn_row, t,
            text=L.t("about", "check_update"),
            command=self._manual_check_update,
        )
        self._btn_check_upd.pack(side="left", padx=4)

        FlatButton(self, theme, text=L.t("about","close"),
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
            msg = L.t("update", "check_failed", reason=info.error)
            _UpdateDialog(self, t, L,
                          title=L.t("update", "title_error"),
                          message=msg,
                          show_download=False)
            return

        if info.available:
            msg = L.t("update", "available", ver=info.latest_version)
            if info.changelog:
                msg += "\n\n" + info.changelog
            _UpdateDialog(self, t, L,
                          title=L.t("update", "title_available"),
                          message=msg,
                          show_download=True)
        else:
            if manual:
                _UpdateDialog(self, t, L,
                              title=L.t("update", "title_latest"),
                              message=L.t("update", "up_to_date",
                                          ver=APP_VERSION),
                              show_download=False)


class _UpdateDialog(tk.Toplevel):
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

        msg_frame = tk.Frame(self, bg=t.bg)
        msg_frame.pack(fill="both", expand=True, padx=20, pady=(16, 8))

        tk.Label(
            msg_frame, text=message,
            bg=t.bg, fg=t.fg, font=("", 9),
            justify="left", wraplength=340, anchor="w",
        ).pack(fill="both", expand=True)

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


class Sash(tk.Frame):
    W = 5

    def __init__(self, master, theme: Theme,
                 left: tk.Widget, right_widget: tk.Widget,
                 min_left: int = 80, min_right: int = 80, **kw):
        super().__init__(master, width=self.W, bg=theme.border,
                         cursor="sb_h_double_arrow", **kw)
        self._left = left
        self._right = right_widget
        self._min_left  = min_left
        self._min_right = min_right
        self._drag_start_x  = 0
        self._left_start_w  = 0
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>",     self._on_drag)

    def retheme(self, t: Theme) -> None:
        self.configure(bg=t.border)

    def _on_press(self, event) -> None:
        self._drag_start_x = event.x_root
        self._left_start_w = self._left.winfo_width()

    def _on_drag(self, event) -> None:
        delta  = event.x_root - self._drag_start_x
        new_lw = self._left_start_w + delta
        total  = self._left.winfo_width() + self.W + self._right.winfo_width()
        new_lw = max(self._min_left, min(new_lw, total - self._min_right - self.W))
        new_rx = new_lw + self.W
        self._left.place_configure(width=new_lw)
        self.place_configure(x=new_lw)
        self._right.place_configure(x=new_rx, width=total - new_rx)

class MainWindow(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self._base_dir  = get_base_dir()
        self._config    = AppConfig(self._base_dir)
        self._languages = scan_languages(self._base_dir)
        self._lang: LangData = resolve_initial_language(self._config, self._languages)

        _patch_default_fonts(self, self._base_dir)

        self._player    = Player()
        self._root_group: Optional[Group] = None
        self._current_group: Optional[Group] = None
        self._file_paths: list[str] = []
        self._filtered_indices: list[int] = []
        self._panel_visible = True
        self._always_on_top = False
        self._seeking       = False
        self._track_length  = 0.0

        saved_theme = self._config.get("theme", "dark")
        from theme import THEMES
        self._theme: Theme = THEMES.get(saved_theme, DARK)

        self._auto_update_check = self._config.get("auto_update_check", "1") == "1"

        self.title("LoadWhistler")
        self.minsize(400, 100)
        self.geometry("680x420")
        self.configure(bg=self._theme.bg)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._set_icon()
        self._build_ui()
        self._apply_theme(self._theme)
        self._retranslate()
        self._bind_hotkeys()
        self._bind_player_callbacks()
        self._load_files()

        if self._auto_update_check:
            check_update_async(APP_VERSION, self._on_startup_update_result)

    def _set_icon(self) -> None:
        if not ICON_B64:
            return
        try:
            data = base64.b64decode(ICON_B64)
            img  = tk.PhotoImage(data=data)
            self.iconphoto(True, img)
            self._icon_img = img
        except Exception as e:
            print(f"[Icon] {e}")

    def _build_ui(self) -> None:
        t = self._theme
        L = self._lang

        self._toolbar = tk.Frame(self, bg=t.bg2, height=26, bd=0)
        self._toolbar.pack(side="top", fill="x")
        self._toolbar.pack_propagate(False)

        self._btn_panel   = FlatButton(self._toolbar, t, command=self._toggle_panel)
        self._btn_panel.pack(side="left", padx=(4, 2), pady=2)

        self._btn_topmost = FlatButton(self._toolbar, t, command=self._toggle_topmost)
        self._btn_topmost.pack(side="left", padx=2, pady=2)

        self._btn_theme   = FlatButton(self._toolbar, t, command=self._toggle_theme)
        self._btn_theme.pack(side="left", padx=2, pady=2)

        self._btn_about   = FlatButton(self._toolbar, t, command=self._show_about)
        self._btn_about.pack(side="left", padx=2, pady=2)

        self._info_label = tk.Label(self._toolbar, text="", bg=t.bg2, fg=t.fg_dim,
                                    font=("", 8))
        self._info_label.pack(side="right", padx=6)

        self._lang_dropdown = LangDropdown(
            self._toolbar, t,
            languages=self._languages,
            current_code=self._lang.code,
            on_change=self._on_lang_change,
        )
        self._lang_dropdown.pack(side="right", padx=(2, 4))

        self._lang_label = tk.Label(self._toolbar, text="", bg=t.bg2, fg=t.fg_dim,
                                    font=("", 8))
        self._lang_label.pack(side="right", padx=(4, 0))

        self._panel = tk.Frame(self, bg=t.bg)
        self._panel.pack(side="top", fill="both", expand=True)

        _LEFT_W = 170
        
        self._group_frame = tk.Frame(self._panel, bg=t.bg2, bd=0)
        self._group_frame.place(x=4, y=4, width=_LEFT_W, relheight=1.0, height=-8)

        self._group_header_lbl = tk.Label(
            self._group_frame, bg=t.bg2, fg=t.fg_dim,
            font=("", 8, "bold"), anchor="w")
        self._group_header_lbl.pack(fill="x", padx=4, pady=(3, 1))

        self._group_scroll = tk.Scrollbar(self._group_frame, orient="vertical")
        self._group_scroll.pack(side="right", fill="y")

        self._group_tree = ttk.Treeview(
            self._group_frame, show="tree", selectmode="browse",
            yscrollcommand=self._group_scroll.set)
        self._group_tree.pack(side="left", fill="both", expand=True)
        self._group_scroll.config(command=self._group_tree.yview)
        self._group_tree.bind("<<TreeviewSelect>>", self._on_group_select)

        self._file_frame = tk.Frame(self._panel, bg=t.bg)

        self._sash = Sash(self._panel, t,
                          left=self._group_frame,
                          right_widget=self._file_frame,
                          min_left=80, min_right=120)
        self._sash.place(x=4 + _LEFT_W, y=4, width=Sash.W, relheight=1.0, height=-8)

        self._file_frame.place(
            x=4 + _LEFT_W + Sash.W, y=4,
            relwidth=1.0, width=-(4 + _LEFT_W + Sash.W + 4),
            relheight=1.0, height=-8,
        )

        self._panel.bind("<Configure>", self._on_panel_resize)

        search_bar = tk.Frame(self._file_frame, bg=t.bg2, bd=0)
        search_bar.pack(fill="x", pady=(0, 2))

        self._search_icon_lbl = tk.Label(search_bar, bg=t.bg2, fg=t.fg_dim, font=("", 9))
        self._search_icon_lbl.pack(side="left", padx=(4, 1))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)
        self._search_entry = tk.Entry(
            search_bar, textvariable=self._search_var,
            bg=t.bg3, fg=t.fg, insertbackground=t.fg,
            relief="flat", bd=2, font=("", 9),
        )
        self._search_entry.pack(side="left", fill="x", expand=True, pady=2, padx=(0, 2))

        self._clear_btn = FlatButton(search_bar, t, command=self._clear_search)
        self._clear_btn.pack(side="right", padx=(0, 4))

        list_container = tk.Frame(self._file_frame, bg=t.bg)
        list_container.pack(fill="both", expand=True)

        self._file_scroll = tk.Scrollbar(list_container)
        self._file_scroll.pack(side="right", fill="y")

        self._file_listbox = tk.Listbox(
            list_container,
            bg=t.bg3, fg=t.fg,
            selectbackground=t.select_bg, selectforeground=t.select_fg,
            activestyle="none",
            bd=0, highlightthickness=1, highlightbackground=t.border,
            font=("", 10),
            yscrollcommand=self._file_scroll.set,
        )
        self._file_listbox.pack(side="left", fill="both", expand=True)
        self._file_scroll.config(command=self._file_listbox.yview)
        self._file_listbox.bind("<Double-Button-1>", self._on_file_doubleclick)
        self._file_listbox.bind("<Return>",          self._on_file_return)

        ctrl = tk.Frame(self, bg=t.bg2, bd=0)
        ctrl.pack(side="bottom", fill="x")
        self._ctrl_frame = ctrl

        self._title_var   = tk.StringVar()
        self._title_label = tk.Label(
            ctrl, textvariable=self._title_var,
            bg=t.bg2, fg=t.fg, font=("", 9, "bold"), anchor="w", padx=6)
        self._title_label.pack(fill="x", pady=(4, 0))

        seek_row = tk.Frame(ctrl, bg=t.bg2)
        seek_row.pack(fill="x", padx=6, pady=1)

        self._pos_label = tk.Label(seek_row, text="0:00", bg=t.bg2, fg=t.fg_dim,
                                   font=("", 8), width=5, anchor="e")
        self._pos_label.pack(side="left")

        self._seek_var = tk.DoubleVar()
        self._seek_bar = ttk.Scale(
            seek_row, from_=0, to=100, orient="horizontal",
            variable=self._seek_var, command=self._on_seek_drag)
        self._seek_bar.pack(side="left", fill="x", expand=True, padx=4)
        self._seek_bar.bind("<ButtonPress-1>",   lambda e: setattr(self, "_seeking", True))
        self._seek_bar.bind("<ButtonRelease-1>", self._on_seek_release)

        self._len_label = tk.Label(seek_row, text="0:00", bg=t.bg2, fg=t.fg_dim,
                                   font=("", 8), width=4, anchor="w")
        self._len_label.pack(side="left")

        btn_row = tk.Frame(ctrl, bg=t.bg2)
        btn_row.pack(fill="x", padx=6, pady=(1, 5))

        self._btn_play = FlatButton(btn_row, t, width=8,
                                    command=self._player.toggle_play_pause)
        self._btn_play.pack(side="left", padx=(0, 4))

        self._btn_mode = FlatButton(btn_row, t, width=10,
                                    command=self._on_mode_cycle)
        self._btn_mode.pack(side="left", padx=2)

        vol_frame = tk.Frame(btn_row, bg=t.bg2)
        vol_frame.pack(side="right")

        self._vol_icon_lbl = tk.Label(vol_frame, text="🔊", bg=t.bg2, fg=t.fg,
                                      font=("", 9))
        self._vol_icon_lbl.pack(side="left")

        self._vol_var = tk.DoubleVar(value=self._player.get_volume())
        self._vol_bar = ttk.Scale(
            vol_frame, from_=0, to=1, orient="horizontal", length=100,
            variable=self._vol_var, command=self._on_volume_change)
        self._vol_bar.pack(side="left", padx=4)

        self._vol_label = tk.Label(vol_frame, text=f"{int(self._player.get_volume()*100)}%",
                                   bg=t.bg2, fg=t.fg_dim, font=("", 8), width=4)
        self._vol_label.pack(side="left")

        self._ttkstyle = ttk.Style()
        self._ttkstyle.theme_use("clam")

        self._title_var.set("---")


    def _apply_theme(self, t: Theme) -> None:
        self._theme = t
        self.configure(bg=t.bg)

        # Treeview
        self._ttkstyle.configure(
            "LW.Treeview",
            background=t.bg3, foreground=t.fg,
            fieldbackground=t.bg3,
            borderwidth=0, rowheight=22, font=("", 9),
        )
        self._ttkstyle.configure("LW.Treeview.Heading",
                                 background=t.bg2, foreground=t.fg_dim)
        self._ttkstyle.map("LW.Treeview",
                           background=[("selected", t.select_bg)],
                           foreground=[("selected", t.select_fg)])
        self._group_tree.configure(style="LW.Treeview")

        self._ttkstyle.configure(
            "LW.Horizontal.TScale",
            troughcolor=t.slider_bg,
            background=t.bg2,        
            sliderlength=14,
        )
        thumb_color = "#d0d0d0"
        self._ttkstyle.map(
            "LW.Horizontal.TScale",
            background=[("active", "#ffffff"), ("!active", thumb_color)],
        )
        self._seek_bar.configure(style="LW.Horizontal.TScale")
        self._vol_bar.configure( style="LW.Horizontal.TScale")

        for w in (self._toolbar, self._group_frame):
            w.configure(bg=t.bg2)
        self._panel.configure(bg=t.bg)
        self._file_frame.configure(bg=t.bg)
        self._ctrl_frame.configure(bg=t.bg2)
        self._title_label.configure(bg=t.bg2, fg=t.fg)
        self._pos_label.configure(bg=t.bg2, fg=t.fg_dim)
        self._len_label.configure(bg=t.bg2, fg=t.fg_dim)
        self._info_label.configure(bg=t.bg2, fg=t.fg_dim)
        self._lang_label.configure(bg=t.bg2, fg=t.fg_dim)
        self._group_header_lbl.configure(bg=t.bg2, fg=t.fg_dim)
        self._search_icon_lbl.configure(bg=t.bg2, fg=t.fg_dim)
        self._search_entry.configure(bg=t.bg3, fg=t.fg, insertbackground=t.fg)
        self._vol_icon_lbl.configure(bg=t.bg2, fg=t.fg)
        self._vol_label.configure(bg=t.bg2, fg=t.fg_dim)
        self._file_listbox.configure(
            bg=t.bg3, fg=t.fg,
            selectbackground=t.select_bg, selectforeground=t.select_fg,
            highlightbackground=t.border,
        )

        for btn in (self._btn_panel, self._btn_topmost, self._btn_theme,
                    self._btn_about, self._btn_play, self._btn_mode, self._clear_btn):
            btn.retheme(t)
        self._sash.retheme(t)
        self._lang_dropdown.retheme(t)

        for child in self._ctrl_frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=t.bg2)
                for gc in child.winfo_children():
                    if isinstance(gc, tk.Frame):
                        gc.configure(bg=t.bg2)

        search_bar = self._search_entry.master
        search_bar.configure(bg=t.bg2)

    def _toggle_theme(self) -> None:
        new_t = LIGHT if self._theme.name == "dark" else DARK
        self._apply_theme(new_t)
        self._config.set("theme", new_t.name)
        self._config.save()
        self._retranslate()
        
    def _retranslate(self) -> None:
        L = self._lang
        t = self._theme

        self._btn_panel.configure(
            text=L.t("toolbar", "panel_hide" if self._panel_visible else "panel_show"))
        self._btn_topmost.configure(
            text=L.t("toolbar", "topmost_on" if self._always_on_top else "topmost_off"))
        self._btn_theme.configure(
            text=L.t("toolbar", "theme_light" if t.name == "light" else "theme_dark"))
        self._btn_about.configure(text=L.t("toolbar", "about"))
        self._lang_label.configure(text=L.t("toolbar", "lang_label"))

        is_playing = self._player.is_playing()
        self._btn_play.configure(
            text=L.t("controls", "pause_btn" if is_playing else "play_btn"))
        self._btn_mode.configure(
            text=self._mode_label(self._player.get_mode()))

        self._group_header_lbl.configure(text=L.t("panel", "group_header"))
        self._search_icon_lbl.configure( text=L.t("panel", "search_icon"))
        self._clear_btn.configure(       text=L.t("panel", "search_clear"))

        if not self._player.current_path():
            self._title_var.set(L.t("controls", "stopped"))

    def _mode_label(self, mode: PlayMode) -> str:
        key = {
            PlayMode.SINGLE_LOOP: "mode_single",
            PlayMode.GROUP_LOOP:  "mode_group",
            PlayMode.RANDOM_LOOP: "mode_random",
        }[mode]
        return self._lang.t("controls", key)

    def _on_lang_change(self, code: str, lang: LangData) -> None:
        self._lang = lang
        self._config.set("language", code)
        self._config.save()
        self._retranslate()

    def _load_files(self) -> None:
        self._root_group = scan_lw_files(self._base_dir)
        if self._root_group is None:
            self._group_tree.insert(
                "", "end",
                text=self._lang.t("errors", "no_lw_files"))
            return
        self._populate_group_tree(self._root_group)

    def _populate_group_tree(self, root: Group) -> None:
        self._group_tree.delete(*self._group_tree.get_children())
        self._tree_iid_map: dict[str, Group] = {}
        self._insert_group(root, "")

    def _insert_group(self, group: Group, parent_iid: str) -> None:
        prefix = "  " * group.depth
        count  = len(group.get_all_files())
        label  = f"{prefix}{group.name}  ({count})"
        iid    = str(id(group))
        self._tree_iid_map[iid] = group
        self._group_tree.insert(parent_iid, "end", iid=iid, text=label)
        for child in group.children:
            self._insert_group(child, iid)

    def _on_group_select(self, event) -> None:
        selection = self._group_tree.selection()
        if not selection:
            return
        group = self._tree_iid_map.get(selection[0])
        if group is None:
            return
        self._current_group = group
        self._file_paths    = group.get_all_files()
        self._search_var.set("")
        self._apply_filter("")
        n = len(self._file_paths)
        self._info_label.configure(
            text=self._lang.t("toolbar", "file_count", n=n))

    def _apply_filter(self, query: str) -> None:
        q = query.lower().strip()
        self._file_listbox.delete(0, tk.END)
        self._filtered_indices = []
        for i, path in enumerate(self._file_paths):
            name = os.path.basename(path)
            if q == "" or q in name.lower():
                self._file_listbox.insert(tk.END, name)
                self._filtered_indices.append(i)

    def _on_search_change(self, *args) -> None:
        self._apply_filter(self._search_var.get())

    def _clear_search(self) -> None:
        self._search_var.set("")

    def _on_file_doubleclick(self, event) -> None:
        self._play_selected()

    def _on_file_return(self, event) -> None:
        self._play_selected()

    def _play_selected(self) -> None:
        sel = self._file_listbox.curselection()
        if not sel:
            return
        list_pos   = sel[0]
        real_index = (self._filtered_indices[list_pos]
                      if self._filtered_indices else list_pos)
        self._player.set_playlist(self._file_paths, start_index=real_index)

    def _sync_list_selection(self, index: int) -> None:
        try:
            list_pos = self._filtered_indices.index(index)
            self._file_listbox.selection_clear(0, tk.END)
            self._file_listbox.selection_set(list_pos)
            self._file_listbox.see(list_pos)
        except ValueError:
            pass

    def _toggle_panel(self) -> None:
        L = self._lang
        if self._panel_visible:
            self._panel.pack_forget()
            self._btn_panel.configure(text=L.t("toolbar", "panel_show"))
            self.resizable(False, False)
            self.update_idletasks()
            total = (self._ctrl_frame.winfo_reqheight()
                     + self._toolbar.winfo_reqheight() + 8)
            self.geometry(f"{self.winfo_width()}x{total}")
        else:
            self._panel.pack(side="top", fill="both", expand=True,
                             before=self._ctrl_frame)
            self._btn_panel.configure(text=L.t("toolbar", "panel_hide"))
            self.resizable(True, True)
            self.geometry(f"{self.winfo_width()}x420")
        self._panel_visible = not self._panel_visible

    def _toggle_topmost(self) -> None:
        self._always_on_top = not self._always_on_top
        try:
            self.wm_attributes("-topmost", self._always_on_top)
        except Exception:
            pass
        key = "topmost_on" if self._always_on_top else "topmost_off"
        self._btn_topmost.configure(text=self._lang.t("toolbar", key))


    def _on_panel_resize(self, event) -> None:
        lw    = self._group_frame.winfo_width()
        sx    = lw + 4
        total = event.width
        rw    = total - sx - Sash.W - 4
        if rw < 1:
            return
        self._sash.place_configure(x=sx)
        self._file_frame.place_configure(x=sx + Sash.W, width=rw)

    def _show_about(self) -> None:
        AboutDialog(self, self._theme, self._lang,
                    config=self._config,
                    auto_check=self._auto_update_check)

    def _on_startup_update_result(self, info: "UpdateInfo") -> None:
        if info.available:
            self.after(0, lambda: self._show_startup_update_dialog(info))

    def _show_startup_update_dialog(self, info: "UpdateInfo") -> None:
        L = self._lang
        msg = L.t("update", "available", ver=info.latest_version)
        if info.changelog:
            msg += "\n\n" + info.changelog
        _UpdateDialog(self, self._theme, L,
                      title=L.t("update", "title_available"),
                      message=msg,
                      show_download=True)

    def _bind_player_callbacks(self) -> None:
        self._player.on_track_change    = self._cb_track_change
        self._player.on_play_state_change = self._cb_play_state
        self._player.on_position_update = self._cb_position_update

    def _cb_track_change(self, index: int, path: str) -> None:
        name = os.path.basename(path)
        text = self._lang.t("controls", "playing", name=name)
        self.after(0, lambda: (
            self._title_var.set(text),
            self._sync_list_selection(index),
        ))

    def _cb_play_state(self, is_playing: bool) -> None:
        key  = "pause_btn" if is_playing else "play_btn"
        text = self._lang.t("controls", key)
        self.after(0, lambda: self._btn_play.configure(text=text))

    def _cb_position_update(self, pos: float, length: float) -> None:
        if self._seeking:
            return
        self._track_length = length

        def _update():
            self._pos_label.configure(text=fmt_time(pos))
            self._len_label.configure(text=fmt_time(length))
            if length > 0:
                self._seek_bar.configure(to=length)
                self._seek_var.set(pos)
            else:
                self._seek_var.set(0)
        self.after(0, _update)

    def _on_mode_cycle(self) -> None:
        mode = self._player.cycle_mode()
        self._btn_mode.configure(text=self._mode_label(mode))

    def _on_volume_change(self, value) -> None:
        v = float(value)
        self._player.set_volume(v)
        self._vol_label.configure(text=f"{int(v * 100)}%")

    def _on_seek_drag(self, value) -> None:
        self._pos_label.configure(text=fmt_time(float(value)))

    def _on_seek_release(self, event) -> None:
        self._player.seek(self._seek_var.get())
        self._seeking = False

    def _bind_hotkeys(self) -> None:
        ign = (self._search_entry,)
        self.bind("<space>",
                  lambda e: self._player.toggle_play_pause() if e.widget not in ign else None)
        self.bind("<m>",
                  lambda e: self._on_mode_cycle() if e.widget not in ign else None)
        self.bind("<M>",
                  lambda e: self._on_mode_cycle() if e.widget not in ign else None)
        self.bind("<Up>",
                  lambda e: self._volume_step(+0.05) if e.widget not in ign else None)
        self.bind("<Down>",
                  lambda e: self._volume_step(-0.05) if e.widget not in ign else None)

    def _volume_step(self, delta: float) -> None:
        v = max(0.0, min(1.0, self._player.get_volume() + delta))
        self._player.set_volume(v)
        self._vol_var.set(v)
        self._vol_label.configure(text=f"{int(v * 100)}%")

    def _on_close(self) -> None:
        self._player.stop()
        self.destroy()
