from __future__ import annotations
import os
import base64
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog
from typing import Optional

from config import (
    Theme, DARK, LIGHT, THEMES,
    Group, scan_lw_files, scan_dir_as_root,
    LangData, AppConfig, scan_languages, resolve_initial_language, get_base_dir,
)
from player import Player, PlayMode
from updater import check_update_async, UpdateInfo
from ui_widgets import FlatButton, LangDropdown, Sash, fmt_time, patch_default_fonts
from ui_dialogs import AboutDialog, UpdateDialog, APP_VERSION

ICON_B64: str = "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"

print(f"LoadWhistler v{APP_VERSION}\nhttps://abatbeliever.net/software/bin/LoadWhistler/\n")


class MainWindow(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self._base_dir  = get_base_dir()
        self._config    = AppConfig(self._base_dir)
        self._languages = scan_languages(self._base_dir)
        self._lang: LangData = resolve_initial_language(self._config, self._languages)

        _saved_volume = self._config.get_float("volume", 0.8)
        _saved_mode_name = self._config.get("play_mode", PlayMode.GROUP_LOOP.name)
        _saved_mode = next(
            (m for m in PlayMode if m.name == _saved_mode_name),
            PlayMode.GROUP_LOOP,
        )
        self._player    = Player(initial_volume=_saved_volume, initial_mode=_saved_mode)
        self._root_group: Optional[Group] = None
        self._current_group: Optional[Group] = None
        self._file_paths: list[str] = []
        self._filtered_indices: list[int] = []
        self._tree_iid_map: dict[str, Group] = {}
        self._root_iid_path: dict[str, str] = {}
        self._panel_visible = True
        self._always_on_top = False
        self._seeking       = False
        self._track_length  = 0.0

        self._theme: Theme = THEMES.get(self._config.get("theme", "dark"), DARK)
        self._auto_update_check = self._config.get("auto_update_check", "1") == "1"

        self.title("LoadWhistler")
        self.minsize(400, 100)
        self.geometry("680x420")
        self.configure(bg=self._theme.bg)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        patch_default_fonts(self, self._base_dir)
        self._set_icon()
        self._build_ui()
        self._apply_theme(self._theme)
        self._retranslate()
        self._bind_hotkeys()
        self._bind_player_callbacks()

        # scan_roots キーが ini に一度も書かれていない場合のみ lw-files をデフォルト登録
        if not self._config.has_scan_roots_key():
            lw_default = os.path.join(self._base_dir, "lw-files")
            if os.path.isdir(lw_default):
                self._config.add_scan_root(lw_default)
            self._config.save()  # キーを確定させる（lw-files がなくても空で保存）

        self._load_files()

        if self._auto_update_check:
            check_update_async(APP_VERSION, self._on_startup_update_result)

    # ------------------------------------------------------------------
    # Icon
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        t = self._theme

        # Toolbar
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

        # Main panel (group tree + file list)
        self._panel = tk.Frame(self, bg=t.bg)
        self._panel.pack(side="top", fill="both", expand=True)

        _LEFT_W = 170

        self._group_frame = tk.Frame(self._panel, bg=t.bg2, bd=0)
        self._group_frame.place(x=4, y=4, width=_LEFT_W, relheight=1.0, height=-8)

        self._group_header_lbl = tk.Label(
            self._group_frame, bg=t.bg2, fg=t.fg_dim, font=("", 8, "bold"), anchor="w")
        self._group_header_lbl.pack(fill="x", padx=4, pady=(3, 1))

        # ＋ボタン（ルート追加）— ツリーより先にpackして領域を確保
        self._btn_add_root = FlatButton(
            self._group_frame, t, text="＋",
            command=self._on_add_root)
        self._btn_add_root.pack(side="bottom", fill="x", padx=2, pady=(0, 2))

        self._group_scroll = tk.Scrollbar(self._group_frame, orient="vertical")
        self._group_scroll.pack(side="right", fill="y")

        self._group_tree = ttk.Treeview(
            self._group_frame, show="tree", selectmode="browse",
            yscrollcommand=self._group_scroll.set)
        self._group_tree.pack(side="left", fill="both", expand=True)
        self._group_scroll.config(command=self._group_tree.yview)
        self._group_tree.bind("<<TreeviewSelect>>", self._on_group_select)
        self._group_tree.bind("<Button-3>",         self._on_tree_right_click)

        # ツールチップ
        self._tooltip = tk.Label(
            self, bg="#ffffe0", fg="#000000",
            font=("", 8), relief="solid", bd=1, padx=4, pady=2)
        self._group_tree.bind("<Motion>",    self._on_tree_motion)
        self._group_tree.bind("<Leave>",     lambda e: self._hide_tooltip())

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

        # Search bar
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

        # File list
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

        # Controls
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

        self._btn_prev = FlatButton(btn_row, t, width=4,
                                    command=self._player.skip_prev)
        self._btn_prev.pack(side="left", padx=(0, 2))

        self._btn_play = FlatButton(btn_row, t, width=8,
                                    command=self._player.toggle_play_pause)
        self._btn_play.pack(side="left", padx=(0, 2))

        self._btn_next = FlatButton(btn_row, t, width=4,
                                    command=self._player.skip_next)
        self._btn_next.pack(side="left", padx=(0, 4))

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
        # クリックした場所に直接ジャンプ（ttk.Scale はデフォルトでドラッグのみ）
        self._vol_bar.bind("<ButtonPress-1>",   self._on_vol_click)
        self._vol_bar.bind("<ButtonRelease-1>", self._on_vol_click)

        self._vol_label = tk.Label(vol_frame,
                                   text=f"{int(self._player.get_volume()*100)}%",
                                   bg=t.bg2, fg=t.fg_dim, font=("", 8), width=4)
        self._vol_label.pack(side="left")

        self._ttkstyle = ttk.Style()
        self._ttkstyle.theme_use("clam")
        self._title_var.set("---")

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def _apply_theme(self, t: Theme) -> None:
        self._theme = t
        self.configure(bg=t.bg)

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
        self._ttkstyle.map(
            "LW.Horizontal.TScale",
            background=[("active", "#ffffff"), ("!active", "#d0d0d0")],
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
                    self._btn_about, self._btn_prev, self._btn_play, self._btn_next,
                    self._btn_mode, self._clear_btn, self._btn_add_root):
            btn.retheme(t)
        self._sash.retheme(t)
        self._lang_dropdown.retheme(t)

        for child in self._ctrl_frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=t.bg2)
                for gc in child.winfo_children():
                    if isinstance(gc, tk.Frame):
                        gc.configure(bg=t.bg2)

        self._search_entry.master.configure(bg=t.bg2)

    def _toggle_theme(self) -> None:
        new_t = LIGHT if self._theme.name == "dark" else DARK
        self._apply_theme(new_t)
        self._config.set("theme", new_t.name)
        self._config.save()
        self._retranslate()

    # ------------------------------------------------------------------
    # i18n
    # ------------------------------------------------------------------

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
        self._btn_prev.configure(text=L.t("controls", "prev_btn"))
        self._btn_next.configure(text=L.t("controls", "next_btn"))
        self._btn_mode.configure(text=self._mode_label(self._player.get_mode()))

        self._group_header_lbl.configure(text=L.t("panel", "group_header"))
        self._search_icon_lbl.configure( text=L.t("panel", "search_icon"))
        self._clear_btn.configure(       text=L.t("panel", "search_clear"))
        self._btn_add_root.configure(    text=L.t("panel", "add_root_dialog"))

        if not self._player.current_path():
            self._title_var.set(L.t("controls", "stopped"))

        self._update_skip_btn_state()

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

    # ------------------------------------------------------------------
    # File loading / tree
    # ------------------------------------------------------------------

    def _load_files(self) -> None:
        """全スキャンルートをロードしてツリーを再構築する。"""
        self._group_tree.delete(*self._group_tree.get_children())
        self._tree_iid_map  = {}
        self._root_iid_path = {}

        scan_roots = self._config.get_scan_roots()
        if not scan_roots:
            self._group_tree.insert(
                "", "end", text=self._lang.t("errors", "no_files_found"))
            return

        for path in scan_roots:
            g = scan_dir_as_root(path)
            self._insert_root(g, path)

    def _insert_root(self, group: Optional[Group], path: str) -> None:
        """ルートをトップレベルに挿入する。ファイルがなくてもルート行は表示する。"""
        name  = os.path.basename(path.rstrip("/\\")) or path
        count = len(group.get_all_files()) if group else 0
        label = f"{name}  ({count})"
        # id() は group が None の場合もあるので path のハッシュをiidに使う
        iid   = f"root_{abs(hash(path))}"
        if group:
            self._tree_iid_map[iid] = group
        self._root_iid_path[iid] = path
        self._group_tree.insert("", "end", iid=iid, text=label)
        if group:
            for child in group.children:
                self._insert_group(child, iid)

    def _insert_group(self, group: Group, parent_iid: str) -> None:
        prefix = "  " * max(0, group.depth - 1)   # ルートが depth=0 なので子は1段下げ
        count  = len(group.get_all_files())
        label  = f"{prefix}{group.name}  ({count})"
        iid    = str(id(group))
        self._tree_iid_map[iid] = group
        self._group_tree.insert(parent_iid, "end", iid=iid, text=label)
        for child in group.children:
            self._insert_group(child, iid)

    # ------------------------------------------------------------------
    # Root management
    # ------------------------------------------------------------------

    def _on_add_root(self) -> None:
        path = filedialog.askdirectory(title=self._lang.t("panel", "add_root_dialog"))
        if not path:
            return
        added = self._config.add_scan_root(path)
        if added:
            self._config.save()
        self._load_files()

    def _on_tree_right_click(self, event) -> None:
        iid = self._group_tree.identify_row(event.y)
        if not iid or iid not in self._root_iid_path:
            return
        path = self._root_iid_path[iid]
        menu = tk.Menu(self, tearoff=False,
                       bg=self._theme.bg3, fg=self._theme.fg,
                       activebackground=self._theme.accent,
                       activeforeground="#ffffff",
                       relief="flat", bd=0)
        menu.add_command(
            label=self._lang.t("panel", "remove_root"),
            command=lambda: self._remove_root(path))
        menu.tk_popup(event.x_root, event.y_root)

    def _remove_root(self, path: str) -> None:
        self._config.remove_scan_root(path)
        self._config.save()
        self._load_files()

    # ------------------------------------------------------------------
    # Tooltip
    # ------------------------------------------------------------------

    def _on_tree_motion(self, event) -> None:
        iid = self._group_tree.identify_row(event.y)
        if iid and iid in self._root_iid_path:
            self._show_tooltip(event, self._root_iid_path[iid])
        else:
            self._hide_tooltip()

    def _show_tooltip(self, event, text: str) -> None:
        self._tooltip.configure(text=text)
        x = self._group_tree.winfo_rootx() + event.x + 12
        y = self._group_tree.winfo_rooty() + event.y + 12
        self._tooltip.place(x=x - self.winfo_rootx(),
                            y=y - self.winfo_rooty())
        self._tooltip.lift()

    def _hide_tooltip(self) -> None:
        self._tooltip.place_forget()

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
        self._info_label.configure(
            text=self._lang.t("toolbar", "file_count", n=len(self._file_paths)))

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

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------

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

    def _bind_player_callbacks(self) -> None:
        self._player.on_track_change      = self._cb_track_change
        self._player.on_play_state_change = self._cb_play_state
        self._player.on_position_update   = self._cb_position_update

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

    def _update_skip_btn_state(self) -> None:
        """RANDOM_LOOP時は前へ/次へを無効化。"""
        is_random = self._player.get_mode() == PlayMode.RANDOM_LOOP
        state = "disabled" if is_random else "normal"
        self._btn_prev.configure(state=state)
        self._btn_next.configure(state=state)

    def _on_mode_cycle(self) -> None:
        mode = self._player.cycle_mode()
        self._btn_mode.configure(text=self._mode_label(mode))
        self._update_skip_btn_state()
        self._config.set("play_mode", mode.name)
        self._config.save()

    def _on_volume_change(self, value) -> None:
        v = float(value)
        self._player.set_volume(v)
        self._vol_label.configure(text=f"{int(v * 100)}%")
        self._config.set("volume", str(round(v, 4)))
        self._config.save()

    def _on_vol_click(self, event) -> None:
        """クリック位置を音量値に変換して直接セットする。"""
        w = self._vol_bar.winfo_width()
        if w <= 0:
            return "break"
        ratio = max(0.0, min(1.0, event.x / w))
        self._vol_var.set(ratio)
        self._on_volume_change(ratio)
        return "break"

    def _on_seek_drag(self, value) -> None:
        self._pos_label.configure(text=fmt_time(float(value)))

    def _on_seek_release(self, event) -> None:
        self._player.seek(self._seek_var.get())
        self._seeking = False

    # ------------------------------------------------------------------
    # Window controls
    # ------------------------------------------------------------------

    def _toggle_panel(self) -> None:
        L = self._lang
        if self._panel_visible:
            self._panel.pack_forget()
            self._btn_panel.configure(text=L.t("toolbar", "panel_show"))
            self.update_idletasks()
            total = (self._ctrl_frame.winfo_reqheight()
                     + self._toolbar.winfo_reqheight() + 8)
            self.geometry(f"{self.winfo_width()}x{total}")
            self.resizable(True, False)
            self.minsize(400, total)
        else:
            self._panel.pack(side="top", fill="both", expand=True,
                             before=self._ctrl_frame)
            self._btn_panel.configure(text=L.t("toolbar", "panel_hide"))
            self.resizable(True, True)
            self.minsize(400, 100)
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

    def _on_startup_update_result(self, info: UpdateInfo) -> None:
        if info.available:
            self.after(0, lambda: self._show_startup_update_dialog(info))

    def _show_startup_update_dialog(self, info: UpdateInfo) -> None:
        L = self._lang
        msg = L.t("update", "available", ver=info.latest_version)
        if info.changelog:
            msg += "\n\n" + info.changelog
        UpdateDialog(self, self._theme, L,
                     title=L.t("update", "title_available"),
                     message=msg,
                     show_download=True)

    def _bind_hotkeys(self) -> None:
        ign = (self._search_entry,)
        self.bind("<space>",
                  lambda e: self._player.toggle_play_pause() if e.widget not in ign else None)
        self.bind("<m>",
                  lambda e: self._on_mode_cycle() if e.widget not in ign else None)
        self.bind("<M>",
                  lambda e: self._on_mode_cycle() if e.widget not in ign else None)
        self.bind("<Left>",
                  lambda e: self._player.skip_prev() if e.widget not in ign else None)
        self.bind("<Right>",
                  lambda e: self._player.skip_next() if e.widget not in ign else None)
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
