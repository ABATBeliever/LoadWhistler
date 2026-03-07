from __future__ import annotations
from dataclasses import dataclass


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

THEMES = {"dark": DARK, "light": LIGHT}
