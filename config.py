from __future__ import annotations
import os
import sys
import configparser
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

@dataclass
class Theme:
    name: str
    bg: str
    bg2: str
    bg3: str
    border: str
    fg: str
    fg_dim: str
    accent: str
    accent_hover: str
    select_bg: str
    select_fg: str
    btn_bg: str
    btn_fg: str
    btn_hover: str
    slider_bg: str
    slider_progress: str


DARK = Theme(
    name="dark",
    bg="#1e1e1e",
    bg2="#252525",
    bg3="#2a2a2a",
    border="#3a3a3a",
    fg="#e0e0e0",
    fg_dim="#888888",
    accent="#3a7ebf",
    accent_hover="#2d6aa8",
    select_bg="#2d5a8e",
    select_fg="#ffffff",
    btn_bg="#333333",
    btn_fg="#e0e0e0",
    btn_hover="#444444",
    slider_bg="#3a3a3a",
    slider_progress="#3a7ebf",
)

LIGHT = Theme(
    name="light",
    bg="#f0f0f0",
    bg2="#e4e4e4",
    bg3="#ffffff",
    border="#cccccc",
    fg="#1a1a1a",
    fg_dim="#666666",
    accent="#2563ae",
    accent_hover="#1d52a0",
    select_bg="#c5d9f0",
    select_fg="#000000",
    btn_bg="#dcdcdc",
    btn_fg="#1a1a1a",
    btn_hover="#c8c8c8",
    slider_bg="#cccccc",
    slider_progress="#2563ae",
)

THEMES: dict[str, Theme] = {"dark": DARK, "light": LIGHT}


# ---------------------------------------------------------------------------
# File scanner
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".ogg"}


@dataclass
class Group:
    name: str
    path: str
    depth: int
    children: list[Group] = field(default_factory=list)
    _direct_files: list[str] = field(default_factory=list)

    def get_all_files(self) -> list[str]:
        result = list(self._direct_files)
        for child in self.children:
            result.extend(child.get_all_files())
        return sorted(result)

    def has_any_file(self) -> bool:
        if self._direct_files:
            return True
        return any(c.has_any_file() for c in self.children)


def scan_lw_files(base_dir: str) -> Optional[Group]:
    lw_path = os.path.join(base_dir, "lw-files")
    if not os.path.isdir(lw_path):
        return None
    return _scan_dir(lw_path, "lw-files", depth=0)


def scan_dir_as_root(path: str) -> Optional[Group]:
    """任意のパスをルートとしてスキャンする。
    ファイルが1つもなくても Group を返す（ルート行表示のため）。
    パス自体が存在しない場合のみ None を返す。
    """
    if not os.path.isdir(path):
        return None
    name = os.path.basename(path.rstrip("/\\")) or path
    group = Group(name=name, path=path, depth=0)
    try:
        entries = sorted(os.scandir(path), key=lambda e: e.name.lower())
    except PermissionError:
        return group
    for entry in entries:
        if entry.is_file():
            ext = os.path.splitext(entry.name)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                group._direct_files.append(entry.path)
        elif entry.is_dir():
            child = _scan_dir(entry.path, entry.name, depth=1)
            if child is not None and child.has_any_file():
                group.children.append(child)
    return group


def _scan_dir(path: str, name: str, depth: int) -> Optional[Group]:
    group = Group(name=name, path=path, depth=depth)
    try:
        entries = sorted(os.scandir(path), key=lambda e: e.name.lower())
    except PermissionError:
        return None
    for entry in entries:
        if entry.is_file():
            ext = os.path.splitext(entry.name)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                group._direct_files.append(entry.path)
        elif entry.is_dir():
            child = _scan_dir(entry.path, entry.name, depth + 1)
            if child is not None and child.has_any_file():
                group.children.append(child)
    if not group.has_any_file():
        return None
    return group


def flatten_groups(root: Group) -> list[Group]:
    result: list[Group] = []
    _flatten(root, result)
    return result


def _flatten(group: Group, result: list[Group]) -> None:
    result.append(group)
    for child in group.children:
        _flatten(child, result)


# ---------------------------------------------------------------------------
# i18n / AppConfig
# ---------------------------------------------------------------------------

CONFIG_FILENAME = "config.ini"
CONFIG_SECTION  = "settings"


class LangData:
    def __init__(self, code: str, data: dict[str, dict[str, str]]) -> None:
        self.code = code
        self._data = data
        self.name: str = data.get("meta", {}).get("name", code)

    def t(self, section: str, key: str, **fmt) -> str:
        raw = self._data.get(section, {}).get(key, f"[{section}.{key}]")
        if fmt:
            try:
                return raw.format(**fmt)
            except KeyError:
                return raw
        return raw


def get_base_dir() -> str:
    if getattr(sys, "frozen", False) or sys.argv[0].endswith(".exe"):
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.dirname(os.path.abspath(__file__))


def scan_languages(base_dir: str) -> dict[str, str]:
    i18n_dir = os.path.join(base_dir, "i18n")
    result: dict[str, str] = {}
    if not os.path.isdir(i18n_dir):
        return result
    for entry in sorted(os.scandir(i18n_dir), key=lambda e: e.name):
        if entry.is_file() and entry.name.lower().endswith(".ini"):
            cp = configparser.ConfigParser()
            try:
                cp.read(entry.path, encoding="utf-8")
                code = cp.get("meta", "code", fallback=None)
                if code:
                    result[code] = entry.path
            except Exception:
                pass
    return result


def load_language(filepath: str) -> Optional[LangData]:
    cp = configparser.ConfigParser()
    try:
        cp.read(filepath, encoding="utf-8")
    except Exception as e:
        print(f"[i18n] Failed to load {filepath}: {e}")
        return None
    data: dict[str, dict[str, str]] = {}
    for section in cp.sections():
        data[section] = dict(cp[section])
    return LangData(code=data.get("meta", {}).get("code", "??"), data=data)


class AppConfig:
    def __init__(self, base_dir: str) -> None:
        self._path = os.path.join(base_dir, CONFIG_FILENAME)
        self._cp = configparser.ConfigParser()
        self._load()

    def _load(self) -> None:
        if os.path.isfile(self._path):
            try:
                self._cp.read(self._path, encoding="utf-8")
            except Exception:
                pass
        if CONFIG_SECTION not in self._cp:
            self._cp[CONFIG_SECTION] = {}

    def get(self, key: str, fallback: str = "") -> str:
        return self._cp.get(CONFIG_SECTION, key, fallback=fallback)

    def set(self, key: str, value: str) -> None:
        self._cp[CONFIG_SECTION][key] = value

    def save(self) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                self._cp.write(f)
        except Exception as e:
            print(f"[Config] Save error: {e}")

    # --- 型付きアクセサ ---

    def get_float(self, key: str, fallback: float) -> float:
        try:
            return float(self.get(key, str(fallback)))
        except ValueError:
            return fallback

    def get_int(self, key: str, fallback: int) -> int:
        try:
            return int(self.get(key, str(fallback)))
        except ValueError:
            return fallback

    # --- スキャンルート管理 ---
    _ROOTS_SEP = ";"

    def has_scan_roots_key(self) -> bool:
        """scan_roots キーが ini に存在するかどうか。"""
        return self._cp.has_option(CONFIG_SECTION, "scan_roots")

    def get_scan_roots(self) -> list[str]:
        """保存済みのスキャンルートパス一覧を返す（存在しないパスは除去済み）。"""
        raw = self.get("scan_roots", "")
        paths = [p.strip() for p in raw.split(self._ROOTS_SEP) if p.strip()]
        valid = [p for p in paths if os.path.isdir(p)]
        if valid != paths:
            self.set_scan_roots(valid)
        return valid

    def set_scan_roots(self, paths: list[str]) -> None:
        self.set("scan_roots", self._ROOTS_SEP.join(paths))

    def add_scan_root(self, path: str) -> bool:
        """パスを追加。既存なら False を返す。"""
        roots = self.get_scan_roots()
        norm = os.path.normpath(path)
        if any(os.path.normpath(r) == norm for r in roots):
            return False
        roots.append(path)
        self.set_scan_roots(roots)
        return True

    def remove_scan_root(self, path: str) -> None:
        norm = os.path.normpath(path)
        roots = [r for r in self.get_scan_roots()
                 if os.path.normpath(r) != norm]
        self.set_scan_roots(roots)


def resolve_initial_language(
    config: AppConfig,
    languages: dict[str, str],
) -> Optional[LangData]:
    saved = config.get("language")
    for code in [saved, "en", *languages.keys()]:
        if code and code in languages:
            lang = load_language(languages[code])
            if lang:
                return lang
    return None
