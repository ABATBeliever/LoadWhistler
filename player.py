from __future__ import annotations
import random
import threading
import time
from enum import Enum, auto
from typing import Callable, Optional


class PlayMode(Enum):
    SINGLE_LOOP = auto()
    GROUP_LOOP  = auto()
    RANDOM_LOOP = auto()

    def next(self) -> PlayMode:
        modes = list(PlayMode)
        return modes[(modes.index(self) + 1) % len(modes)]

    def label(self) -> str:
        return {
            PlayMode.SINGLE_LOOP: "SINGLE_LOOP",
            PlayMode.GROUP_LOOP:  "GROUP_LOOP",
            PlayMode.RANDOM_LOOP: "RANDOM_LOOP",
        }[self]


class Player:
    def __init__(self, initial_volume: float = 0.8,
                 initial_mode: PlayMode = PlayMode.GROUP_LOOP) -> None:
        import pygame
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        self._pygame = pygame

        self._playlist: list[str] = []
        self._current_index: int = 0
        self._mode: PlayMode = initial_mode
        self._volume: float = max(0.0, min(1.0, initial_volume))
        self._playing: bool = False
        self._paused: bool = False
        self._lock = threading.Lock()

        self._shuffle_queue: list[int] = []

        self._track_start_time: float = 0.0
        self._track_offset: float = 0.0
        self._track_length: float = 0.0

        self.on_track_change: Optional[Callable[[int, str], None]] = None
        self.on_play_state_change: Optional[Callable[[bool], None]] = None
        self.on_position_update: Optional[Callable[[float, float], None]] = None

        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def set_playlist(self, files: list[str], start_index: int = 0) -> None:
        with self._lock:
            self._playlist = list(files)
            self._current_index = max(0, min(start_index, len(files) - 1))
            self._rebuild_shuffle_queue_locked(exclude=self._current_index)
        self._load_and_play(self._current_index)

    def play_index(self, index: int) -> None:
        with self._lock:
            if not self._playlist:
                return
            self._current_index = max(0, min(index, len(self._playlist) - 1))
            self._rebuild_shuffle_queue_locked(exclude=self._current_index)
        self._load_and_play(self._current_index)

    def toggle_play_pause(self) -> None:
        with self._lock:
            if not self._playlist:
                return
            if self._playing and not self._paused:
                self._pygame.mixer.music.pause()
                self._paused = True
                elapsed = time.monotonic() - self._track_start_time
                self._track_offset += elapsed
                self._track_start_time = 0.0
            elif self._paused:
                self._pygame.mixer.music.unpause()
                self._paused = False
                self._track_start_time = time.monotonic()
            elif not self._playing:
                self._load_and_play_locked(self._current_index)
                return
        is_playing = self._playing and not self._paused
        if self.on_play_state_change:
            self.on_play_state_change(is_playing)

    def stop(self) -> None:
        with self._lock:
            self._pygame.mixer.music.stop()
            self._playing = False
            self._paused = False
            self._track_offset = 0.0
            self._track_start_time = 0.0
        if self.on_play_state_change:
            self.on_play_state_change(False)

    def seek(self, seconds: float) -> None:
        with self._lock:
            if not self._playlist or not self._playing:
                return
            seconds = max(0.0, min(seconds, self._track_length))
            try:
                self._pygame.mixer.music.set_pos(seconds)
                self._track_offset = seconds
                self._track_start_time = time.monotonic()
                if self._paused:
                    self._pygame.mixer.music.pause()
            except Exception:
                pass

    def skip_next(self) -> None:
        """次のトラックへ（RANDOM_LOOP時は無効）。"""
        with self._lock:
            if not self._playlist or self._mode == PlayMode.RANDOM_LOOP:
                return
            next_idx = (self._current_index + 1) % len(self._playlist)
        self._load_and_play(next_idx)

    def skip_prev(self) -> None:
        """前のトラックへ。再生位置が1秒超なら先頭に戻るだけ（RANDOM_LOOP時は無効）。"""
        with self._lock:
            if not self._playlist or self._mode == PlayMode.RANDOM_LOOP:
                return
            pos, _ = self._get_position_locked()
            if pos > 1.0:
                # 先頭に戻るだけ
                seek_to = 0.0
                do_prev = False
            else:
                seek_to = 0.0
                do_prev = True
            prev_idx = (self._current_index - 1) % len(self._playlist)

        if do_prev:
            self._load_and_play(prev_idx)
        else:
            self.seek(seek_to)

    def _get_position_locked(self) -> tuple[float, float]:
        """ロック取得済みの状態で現在位置を返す内部メソッド。"""
        if self._playing and not self._paused and self._track_start_time > 0:
            elapsed = time.monotonic() - self._track_start_time
            pos = self._track_offset + elapsed
        else:
            pos = self._track_offset
        return min(pos, self._track_length), self._track_length

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        self._pygame.mixer.music.set_volume(self._volume)

    def get_volume(self) -> float:
        return self._volume

    def set_mode(self, mode: PlayMode) -> None:
        with self._lock:
            self._mode = mode
            if mode == PlayMode.RANDOM_LOOP:
                self._rebuild_shuffle_queue_locked(exclude=self._current_index)

    def get_mode(self) -> PlayMode:
        return self._mode

    def cycle_mode(self) -> PlayMode:
        with self._lock:
            self._mode = self._mode.next()
            if self._mode == PlayMode.RANDOM_LOOP:
                self._rebuild_shuffle_queue_locked(exclude=self._current_index)
            return self._mode

    def is_playing(self) -> bool:
        return self._playing and not self._paused

    def current_path(self) -> Optional[str]:
        with self._lock:
            if not self._playlist:
                return None
            return self._playlist[self._current_index]

    def current_index(self) -> int:
        return self._current_index

    def get_position(self) -> tuple[float, float]:
        with self._lock:
            return self._get_position_locked()

    def _rebuild_shuffle_queue_locked(self, exclude: int = -1) -> None:
        n = len(self._playlist)
        indices = [i for i in range(n) if i != exclude]
        random.shuffle(indices)
        self._shuffle_queue = indices

    def _pop_next_random_locked(self) -> int:
        if not self._shuffle_queue:
            self._rebuild_shuffle_queue_locked(exclude=self._current_index)
        if self._shuffle_queue:
            return self._shuffle_queue.pop(0)
        return self._current_index

    def _load_and_play(self, index: int) -> None:
        with self._lock:
            self._load_and_play_locked(index)

    def _load_and_play_locked(self, index: int) -> None:
        if not self._playlist:
            return
        path = self._playlist[index]
        try:
            self._pygame.mixer.music.load(path)
            self._pygame.mixer.music.set_volume(self._volume)
            self._pygame.mixer.music.play()
            self._playing = True
            self._paused = False
            self._track_offset = 0.0
            self._track_start_time = time.monotonic()
            self._track_length = self._get_length(path)
            self._current_index = index
        except Exception as e:
            print(f"[Player] Load error: {e}")
            self._playing = False
            return
        if self.on_track_change:
            self.on_track_change(index, path)
        if self.on_play_state_change:
            self.on_play_state_change(True)

    def _get_length(self, path: str) -> float:
        try:
            sound = self._pygame.mixer.Sound(path)
            return sound.get_length()
        except Exception:
            return 0.0

    def _next_track(self) -> None:
        with self._lock:
            if not self._playlist:
                return
            n = len(self._playlist)
            mode = self._mode
            idx = self._current_index
            if mode == PlayMode.SINGLE_LOOP:
                next_idx = idx
            elif mode == PlayMode.GROUP_LOOP:
                next_idx = (idx + 1) % n
            elif mode == PlayMode.RANDOM_LOOP:
                next_idx = self._pop_next_random_locked()
            else:
                next_idx = (idx + 1) % n
        self._load_and_play(next_idx)

    def _monitor_loop(self) -> None:
        while True:
            time.sleep(0.2)
            try:
                with self._lock:
                    if not self._playing or self._paused:
                        skip = True
                    else:
                        skip = False
                        busy = self._pygame.mixer.music.get_busy()

                if skip:
                    continue

                if not busy:
                    with self._lock:
                        still_playing = self._playing
                    if still_playing:
                        self._next_track()
                pos, length = self.get_position()
                if self.on_position_update:
                    self.on_position_update(pos, length)
            except Exception as e:
                print(f"[Monitor] {e}")
