from __future__ import annotations
import os
import platform
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Optional

from config import Theme, LangData, load_language


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fmt_time(seconds: float) -> str:
    s = max(0, int(seconds))
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ---------------------------------------------------------------------------
# Font loading
# ---------------------------------------------------------------------------

def _load_bundled_font(root: tk.Tk, font_path: str) -> str:
    """
    バンドルフォントファイルをOSごとの方法でTkに登録し、
    認識されたファミリー名を返す。失敗時は空文字列。
    """
    _sys = platform.system()

    # --- Windows: GDI に一時登録 ---
    if _sys == "Windows":
        try:
            from ctypes import windll
            windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
        except Exception:
            pass

    # --- Linux: fontconfig のユーザーキャッシュに登録 ---
    elif _sys == "Linux":
        try:
            import subprocess, shutil
            fonts_dir = os.path.join(
                os.path.expanduser("~"), ".local", "share", "fonts", "LoadWhistler")
            os.makedirs(fonts_dir, exist_ok=True)
            dest = os.path.join(fonts_dir, os.path.basename(font_path))
            shutil.copy2(font_path, dest)  # 毎回上書きで確実に反映
            subprocess.run(["fc-cache", "-f", fonts_dir],
                           timeout=10, capture_output=True)
        except Exception:
            pass

    # --- macOS: ~/Library/Fonts にコピー ---
    elif _sys == "Darwin":
        try:
            import shutil
            fonts_dir = os.path.join(os.path.expanduser("~"), "Library", "Fonts")
            os.makedirs(fonts_dir, exist_ok=True)
            shutil.copy2(font_path, os.path.join(fonts_dir, os.path.basename(font_path)))
        except Exception:
            pass

    # Tk 9.0+: font create -file で直接ロード（最も確実・全OS）
    try:
        fam = root.tk.call("font", "create", "-file", font_path)
        if fam:
            return str(fam)
    except Exception:
        pass

    # Tk 8.x: families() を再取得してファミリー名を確認
    # Linux は fc-cache 直後でも families() を叩き直せば認識することがある
    try:
        root.tk.call("font", "families")  # キャッシュ強制更新
    except Exception:
        pass

    for candidate in ("Noto Sans JP", "NotoSansJP", "Noto Sans CJK JP",
                      "Noto Sans CJK", "NotoSansCJK"):
        try:
            f = tkfont.Font(root, family=candidate, size=10)
            if f.measure("あ") > 0:
                f.delete()
                return candidate
            f.delete()
        except Exception:
            pass

    return ""


def patch_default_fonts(root: tk.Tk, base_dir: str) -> None:
    """
    font/noto.ttf が存在すればそれを読み込んで全ウィジェットに適用。
    なければシステムの日本語フォントにフォールバック。
    geometry() 確定後に呼ぶこと。
    """
    family = ""

    bundled = os.path.join(base_dir, "font", "noto.ttf")
    if os.path.isfile(bundled):
        family = _load_bundled_font(root, bundled)

    if not family:
        candidates = [
            "Noto Sans CJK JP", "Noto Sans JP", "Noto Sans CJK",
            "IPAGothic", "IPAPGothic", "IPA Gothic",
            "VL Gothic", "TakaoGothic", "Takao Gothic",
            "WenQuanYi Micro Hei", "WenQuanYi Zen Hei",
            "Droid Sans Japanese", "Source Han Sans JP",
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


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

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
                 languages: dict[str, str],
                 current_code: str,
                 on_change,
                 **kw):
        super().__init__(master, bg=theme.bg2, **kw)
        self._theme = theme
        self._languages = languages
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
