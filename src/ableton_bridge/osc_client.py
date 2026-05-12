"""OSC client wrapper for AbletonOSC-compatible remote scripts."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from ableton_bridge.config import AbletonBridgeConfig
from ableton_bridge.errors import AbletonOSCError

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class OSCReply:
    address: str
    values: tuple[Any, ...]


class AbletonOSCClient:
    """Small AbletonOSC client with command helpers."""

    def __init__(self, config: AbletonBridgeConfig | None = None) -> None:
        self.config = config or AbletonBridgeConfig()
        self._client = SimpleUDPClient(self.config.host, self.config.port)

    def status(self) -> str:
        reply = self.query("/live/test", expected_address="/live/test")
        if reply.values:
            return " ".join(str(value) for value in reply.values)
        return "ok"

    def play(self) -> None:
        self.ensure_reachable()
        self.send("/live/song/start_playing")

    def stop(self) -> None:
        self.ensure_reachable()
        self.send("/live/song/stop_playing")

    def stop_all_clips(self) -> None:
        self.ensure_reachable()
        self.send("/live/song/stop_all_clips")

    def stop_track_clips(self, track_index: int) -> None:
        self._validate_index(track_index, "Track index")
        self.ensure_reachable()
        self.send("/live/track/stop_all_clips", int(track_index))

    def set_tempo(self, bpm: float) -> None:
        if bpm <= 0:
            raise ValueError("Tempo must be greater than 0 BPM.")
        self.ensure_reachable()
        self.send("/live/song/set/tempo", float(bpm))

    def get_tempo(self) -> float:
        reply = self.query(
            "/live/song/get/tempo",
            expected_address="/live/song/get/tempo",
        )
        if not reply.values:
            raise AbletonOSCError("AbletonOSC returned no tempo value.")
        return float(reply.values[0])

    def current_time(self) -> float:
        reply = self.query(
            "/live/song/get/current_song_time",
            expected_address="/live/song/get/current_song_time",
        )
        if not reply.values:
            raise AbletonOSCError("AbletonOSC returned no current song time.")
        return float(reply.values[0])

    def get_metronome(self) -> bool:
        reply = self.query(
            "/live/song/get/metronome",
            expected_address="/live/song/get/metronome",
        )
        if not reply.values:
            raise AbletonOSCError("AbletonOSC returned no metronome value.")
        return bool(reply.values[0])

    def set_metronome(self, enabled: bool) -> None:
        self.ensure_reachable()
        self.send("/live/song/set/metronome", 1 if enabled else 0)

    def tracks(self) -> tuple[str, ...]:
        reply = self.query(
            "/live/song/get/track_names",
            expected_address="/live/song/get/track_names",
        )
        return tuple(str(value) for value in reply.values)

    def selected_track(self) -> int:
        reply = self.query(
            "/live/view/get/selected_track",
            expected_address="/live/view/get/selected_track",
        )
        if not reply.values:
            raise AbletonOSCError("AbletonOSC returned no selected track index.")
        return int(reply.values[0])

    def selected_scene(self) -> int:
        reply = self.query(
            "/live/view/get/selected_scene",
            expected_address="/live/view/get/selected_scene",
        )
        if not reply.values:
            raise AbletonOSCError("AbletonOSC returned no selected scene index.")
        return int(reply.values[0])

    def scene_name(self, scene_index: int) -> str:
        self._validate_index(scene_index, "Scene index")
        reply = self.query(
            "/live/scene/get/name",
            int(scene_index),
            expected_address="/live/scene/get/name",
        )
        if len(reply.values) < 2:
            raise AbletonOSCError("AbletonOSC returned no scene name.")
        return str(reply.values[1])

    def cue_points(self) -> tuple[tuple[str, float], ...]:
        reply = self.query(
            "/live/song/get/cue_points",
            expected_address="/live/song/get/cue_points",
        )
        values = reply.values
        return tuple(
            (str(values[index]), float(values[index + 1]))
            for index in range(0, len(values) - 1, 2)
        )

    def track_clips(self, track_index: int) -> tuple[str, ...]:
        self._validate_index(track_index, "Track index")
        reply = self.query(
            "/live/track/get/clips/name",
            int(track_index),
            expected_address="/live/track/get/clips/name",
        )
        if not reply.values:
            return ()
        return tuple(str(value) for value in reply.values[1:])

    def track_name(self, track_index: int) -> str:
        return str(self._track_property("name", track_index))

    def track_color(self, track_index: int) -> int:
        return int(self._track_property("color", track_index))

    def track_volume(self, track_index: int) -> float:
        return float(self._track_property("volume", track_index))

    def set_track_volume(self, track_index: int, volume: float) -> None:
        self._validate_index(track_index, "Track index")
        if not 0 <= volume <= 1:
            raise ValueError("Track volume must be between 0.0 and 1.0.")
        self.ensure_reachable()
        self.send("/live/track/set/volume", int(track_index), float(volume))

    def track_panning(self, track_index: int) -> float:
        return float(self._track_property("panning", track_index))

    def set_track_panning(self, track_index: int, panning: float) -> None:
        self._validate_index(track_index, "Track index")
        if not -1 <= panning <= 1:
            raise ValueError("Track panning must be between -1.0 and 1.0.")
        self.ensure_reachable()
        self.send("/live/track/set/panning", int(track_index), float(panning))

    def track_mute(self, track_index: int) -> bool:
        return bool(self._track_property("mute", track_index))

    def set_track_mute(self, track_index: int, enabled: bool) -> None:
        self._set_track_bool_property("mute", track_index, enabled)

    def track_solo(self, track_index: int) -> bool:
        return bool(self._track_property("solo", track_index))

    def set_track_solo(self, track_index: int, enabled: bool) -> None:
        self._set_track_bool_property("solo", track_index, enabled)

    def track_arm(self, track_index: int) -> bool:
        return bool(self._track_property("arm", track_index))

    def set_track_arm(self, track_index: int, enabled: bool) -> None:
        self._set_track_bool_property("arm", track_index, enabled)

    def fire_clip(self, track_index: int, clip_index: int) -> None:
        self._validate_index(track_index, "Track index")
        self._validate_index(clip_index, "Clip index")
        self.ensure_reachable()
        self.send("/live/clip/fire", int(track_index), int(clip_index))

    def ensure_reachable(self) -> None:
        self.status()

    def send(self, address: str, *values: Any) -> None:
        LOGGER.debug("Sending OSC message %s %s", address, values)
        self._client.send_message(address, list(values))

    def query(self, address: str, *values: Any, expected_address: str) -> OSCReply:
        LOGGER.debug("Querying OSC message %s %s", address, values)
        replies: list[OSCReply] = []
        errors: list[str] = []

        dispatcher = Dispatcher()

        def handle_reply(reply_address: str, *reply_values: Any) -> None:
            replies.append(OSCReply(reply_address, tuple(reply_values)))

        def handle_error(_reply_address: str, *reply_values: Any) -> None:
            message = " ".join(str(value) for value in reply_values)
            errors.append(message or "AbletonOSC returned an error.")

        dispatcher.map(expected_address, handle_reply)
        dispatcher.map("/live/error", handle_error)

        try:
            server = BlockingOSCUDPServer(
                (self.config.reply_host, self.config.reply_port),
                dispatcher,
            )
        except OSError as exc:
            raise AbletonOSCError(
                "Could not listen for AbletonOSC replies on "
                f"{self.config.reply_host}:{self.config.reply_port}. "
                "Check that the reply port is free."
            ) from exc

        server.timeout = self.config.timeout
        self.send(address, *values)
        server.handle_request()
        server.server_close()

        if errors:
            raise AbletonOSCError(errors[0])
        if replies:
            return replies[0]

        raise AbletonOSCError(
            "AbletonOSC did not reply. Make sure Ableton Live is running, "
            "AbletonOSC is selected as a Control Surface, and the host/port "
            f"({self.config.host}:{self.config.port}) are correct."
        )

    def _track_property(self, property_name: str, track_index: int) -> Any:
        self._validate_index(track_index, "Track index")
        address = f"/live/track/get/{property_name}"
        reply = self.query(address, int(track_index), expected_address=address)
        if len(reply.values) < 2:
            raise AbletonOSCError(f"AbletonOSC returned no track {property_name} value.")
        return reply.values[1]

    def _set_track_bool_property(
        self,
        property_name: str,
        track_index: int,
        enabled: bool,
    ) -> None:
        self._validate_index(track_index, "Track index")
        self.ensure_reachable()
        self.send(f"/live/track/set/{property_name}", int(track_index), 1 if enabled else 0)

    def _validate_index(self, value: int, label: str) -> None:
        if value < 0:
            raise ValueError(f"{label} must be zero or greater.")
