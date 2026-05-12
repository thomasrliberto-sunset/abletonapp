"""Configuration values for Ableton Bridge."""

from dataclasses import dataclass


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 11000
DEFAULT_REPLY_PORT = 11001
DEFAULT_TIMEOUT = 2.0


@dataclass(frozen=True)
class AbletonBridgeConfig:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    reply_port: int = DEFAULT_REPLY_PORT
    timeout: float = DEFAULT_TIMEOUT
    reply_host: str = DEFAULT_HOST
