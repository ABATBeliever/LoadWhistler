from __future__ import annotations
import threading
import urllib.request
import urllib.error
from typing import Callable, Optional
from dataclasses import dataclass

UPDATE_URL = "https://abatbeliever.net/upd/LoadWhistler/version.updat"
DOWNLOAD_PAGE = "https://abatbeliever.net/software/bin/LoadWhistler/"
SENTINEL = "[LoadWhistler]"


@dataclass
class UpdateInfo:
    available: bool
    latest_version: str
    changelog: str        # <br> already replaced with \n
    error: Optional[str] = None


def _parse_updat(text: str) -> Optional[UpdateInfo]:
    """
    形式: [LoadWhistler],2.0.0.0,変更内容(<br>区切り)
    先頭が [LoadWhistler] でなければ None を返す。
    """
    text = text.strip()
    if not text.startswith(SENTINEL):
        return None
    parts = text.split(",", 2)
    if len(parts) < 2:
        return None
    version = parts[1].strip()
    changelog_raw = parts[2].strip() if len(parts) > 2 else ""
    changelog = changelog_raw.replace("<br>", "\n")
    return UpdateInfo(available=False, latest_version=version, changelog=changelog)


def _version_tuple(v: str):
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0,)


def check_update(current_version: str) -> UpdateInfo:
    """同期的に更新を確認して UpdateInfo を返す。"""
    try:
        req = urllib.request.Request(UPDATE_URL, headers={"User-Agent": "LoadWhistler-Updater"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return UpdateInfo(available=False, latest_version="", changelog="",
                          error=f"HTTP {e.code}")
    except Exception as e:
        return UpdateInfo(available=False, latest_version="", changelog="",
                          error=str(e))

    info = _parse_updat(raw)
    if info is None:
        return UpdateInfo(available=False, latest_version="", changelog="",
                          error="invalid_response")

    info.available = (
        _version_tuple(info.latest_version) > _version_tuple(current_version)
    )
    return info


def check_update_async(
    current_version: str,
    callback: Callable[[UpdateInfo], None],
) -> None:
    """バックグラウンドスレッドで更新を確認し、結果を callback に渡す。"""
    def _run():
        result = check_update(current_version)
        callback(result)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
