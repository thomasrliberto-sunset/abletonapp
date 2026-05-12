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

    def set_tempo(self, bpm: float) -> None:
        if bpm <= 0:
            raise ValueError("Tempo must be greater than 0 BPM.")
        self.ensure_reachable()
        self.send("/live/song/set/tempo", float(bpm))

    def tracks(self) -> tuple[str, ...]:
        reply = self.query(
            "/live/song/get/track_names",
            expected_address="/live/song/get/track_names",
        )
        return tuple(str(value) for value in reply.values)

    def fire_clip(self, track_index: int, clip_index: int) -> None:
        if track_index < 0 or clip_index < 0:
            raise ValueError("Track and clip indexes must be zero or greater.")
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
