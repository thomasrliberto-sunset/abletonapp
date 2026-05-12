"""Structured result models for higher-level Ableton Bridge commands."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SongSummary:
    tempo: float
    current_time: float
    is_playing: bool
    metronome: bool
    loop: bool
    song_length: float
    signature_numerator: int
    signature_denominator: int
    num_tracks: int
    num_scenes: int


@dataclass(frozen=True)
class ViewSummary:
    selected_track: int
    selected_scene: int
    selected_clip: tuple[int, int]
    selected_device: tuple[int, int]


@dataclass(frozen=True)
class AbletonSnapshot:
    song: SongSummary
    view: ViewSummary
    tracks: tuple[str, ...]
