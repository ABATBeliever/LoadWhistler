from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Optional


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
