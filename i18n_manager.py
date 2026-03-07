from __future__ import annotations
import os
import sys
import configparser
from typing import Optional

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
    import sys
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
