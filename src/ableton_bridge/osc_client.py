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

    def set_selected_track(self, track_index: int) -> None:
        self._validate_index(track_index, "Track index")
        self.ensure_reachable()
        self.send("/live/view/set/selected_track", int(track_index))

    def set_selected_scene(self, scene_index: int) -> None:
        self._validate_index(scene_index, "Scene index")
        self.ensure_reachable()
        self.send("/live/view/set/selected_scene", int(scene_index))

    def scene_name(self, scene_index: int) -> str:
        return str(self._scene_property("name", scene_index))

    def scene_color(self, scene_index: int) -> int:
        return int(self._scene_property("color", scene_index))

    def scene_is_empty(self, scene_index: int) -> bool:
        return bool(self._scene_property("is_empty", scene_index))

    def scene_is_triggered(self, scene_index: int) -> bool:
        return bool(self._scene_property("is_triggered", scene_index))

    def scene_tempo(self, scene_index: int) -> float:
        return float(self._scene_property("tempo", scene_index))

    def set_scene_tempo(self, scene_index: int, tempo: float) -> None:
        self._validate_index(scene_index, "Scene index")
        if tempo <= 0:
            raise ValueError("Scene tempo must be greater than 0 BPM.")
        self.ensure_reachable()
        self.send("/live/scene/set/tempo", int(scene_index), float(tempo))

    def scene_tempo_enabled(self, scene_index: int) -> bool:
        return bool(self._scene_property("tempo_enabled", scene_index))

    def set_scene_tempo_enabled(self, scene_index: int, enabled: bool) -> None:
        self._set_scene_bool_property("tempo_enabled", scene_index, enabled)

    def scene_time_signature(self, scene_index: int) -> tuple[int, int]:
        numerator = int(self._scene_property("time_signature_numerator", scene_index))
        denominator = int(self._scene_property("time_signature_denominator", scene_index))
        return numerator, denominator

    def scene_time_signature_enabled(self, scene_index: int) -> bool:
        return bool(self._scene_property("time_signature_enabled", scene_index))

    def set_scene_time_signature_enabled(self, scene_index: int, enabled: bool) -> None:
        self._set_scene_bool_property("time_signature_enabled", scene_index, enabled)

    def fire_scene(self, scene_index: int) -> None:
        self._validate_index(scene_index, "Scene index")
        self.ensure_reachable()
        self.send("/live/scene/fire", int(scene_index))

    def fire_scene_as_selected(self, scene_index: int) -> None:
        self._validate_index(scene_index, "Scene index")
        self.ensure_reachable()
        self.send("/live/scene/fire_as_selected", int(scene_index))

    def fire_selected_scene(self) -> None:
        self.ensure_reachable()
        self.send("/live/scene/fire_selected")

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

    def track_devices(self, track_index: int) -> tuple[str, ...]:
        self._validate_index(track_index, "Track index")
        reply = self.query(
            "/live/track/get/devices/name",
            int(track_index),
            expected_address="/live/track/get/devices/name",
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

    def stop_clip(self, track_index: int, clip_index: int) -> None:
        self._validate_index(track_index, "Track index")
        self._validate_index(clip_index, "Clip index")
        self.ensure_reachable()
        self.send("/live/clip/stop", int(track_index), int(clip_index))

    def clip_name(self, track_index: int, clip_index: int) -> str:
        return str(self._clip_property("name", track_index, clip_index))

    def clip_color(self, track_index: int, clip_index: int) -> int:
        return int(self._clip_property("color", track_index, clip_index))

    def clip_is_playing(self, track_index: int, clip_index: int) -> bool:
        return bool(self._clip_property("is_playing", track_index, clip_index))

    def device_name(self, track_index: int, device_index: int) -> str:
        return str(self._device_property("name", track_index, device_index))

    def device_type(self, track_index: int, device_index: int) -> str:
        return str(self._device_property("type", track_index, device_index))

    def device_parameters(self, track_index: int, device_index: int) -> tuple[str, ...]:
        self._validate_index(track_index, "Track index")
        self._validate_index(device_index, "Device index")
        reply = self.query(
            "/live/device/get/parameters/name",
            int(track_index),
            int(device_index),
            expected_address="/live/device/get/parameters/name",
        )
        if len(reply.values) <= 2:
            return ()
        return tuple(str(value) for value in reply.values[2:])

    def device_parameter_value(
        self,
        track_index: int,
        device_index: int,
        parameter_index: int,
    ) -> float:
        self._validate_index(parameter_index, "Parameter index")
        return float(
            self._device_parameter_property(
                "value",
                track_index,
                device_index,
                parameter_index,
            )
        )

    def device_parameter_value_string(
        self,
        track_index: int,
        device_index: int,
        parameter_index: int,
    ) -> str:
        self._validate_index(parameter_index, "Parameter index")
        return str(
            self._device_parameter_property(
                "value_string",
                track_index,
                device_index,
                parameter_index,
            )
        )

    def set_device_parameter_value(
        self,
        track_index: int,
        device_index: int,
        parameter_index: int,
        value: float,
    ) -> None:
        self._validate_index(track_index, "Track index")
        self._validate_index(device_index, "Device index")
        self._validate_index(parameter_index, "Parameter index")
        self.ensure_reachable()
        self.send(
            "/live/device/set/parameter/value",
            int(track_index),
            int(device_index),
            int(parameter_index),
            float(value),
        )

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

    def _clip_property(self, property_name: str, track_index: int, clip_index: int) -> Any:
        self._validate_index(track_index, "Track index")
        self._validate_index(clip_index, "Clip index")
        address = f"/live/clip/get/{property_name}"
        reply = self.query(
            address,
            int(track_index),
            int(clip_index),
            expected_address=address,
        )
        if len(reply.values) < 3:
            raise AbletonOSCError(f"AbletonOSC returned no clip {property_name} value.")
        return reply.values[2]

    def _scene_property(self, property_name: str, scene_index: int) -> Any:
        self._validate_index(scene_index, "Scene index")
        address = f"/live/scene/get/{property_name}"
        reply = self.query(address, int(scene_index), expected_address=address)
        if len(reply.values) < 2:
            raise AbletonOSCError(f"AbletonOSC returned no scene {property_name} value.")
        return reply.values[1]

    def _set_scene_bool_property(self, property_name: str, scene_index: int, enabled: bool) -> None:
        self._validate_index(scene_index, "Scene index")
        self.ensure_reachable()
        self.send(f"/live/scene/set/{property_name}", int(scene_index), 1 if enabled else 0)

    def _device_property(self, property_name: str, track_index: int, device_index: int) -> Any:
        self._validate_index(track_index, "Track index")
        self._validate_index(device_index, "Device index")
        address = f"/live/device/get/{property_name}"
        reply = self.query(
            address,
            int(track_index),
            int(device_index),
            expected_address=address,
        )
        if len(reply.values) < 3:
            raise AbletonOSCError(f"AbletonOSC returned no device {property_name} value.")
        return reply.values[2]

    def _device_parameter_property(
        self,
        property_name: str,
        track_index: int,
        device_index: int,
        parameter_index: int,
    ) -> Any:
        self._validate_index(track_index, "Track index")
        self._validate_index(device_index, "Device index")
        address = f"/live/device/get/parameter/{property_name}"
        reply = self.query(
            address,
            int(track_index),
            int(device_index),
            int(parameter_index),
            expected_address=address,
        )
        if len(reply.values) < 4:
            raise AbletonOSCError(f"AbletonOSC returned no device parameter {property_name}.")
        return reply.values[3]

    def _validate_index(self, value: int, label: str) -> None:
        if value < 0:
            raise ValueError(f"{label} must be zero or greater.")
