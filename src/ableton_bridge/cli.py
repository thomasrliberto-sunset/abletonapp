"""Command-line interface for ableton-bridge."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence

from ableton_bridge.config import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_REPLY_PORT,
    DEFAULT_TIMEOUT,
    AbletonBridgeConfig,
)
from ableton_bridge.errors import AbletonOSCError
from ableton_bridge.osc_client import AbletonOSCClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ableton-bridge",
        description="Control Ableton Live through AbletonOSC.",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="AbletonOSC host.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="AbletonOSC port.")
    parser.add_argument(
        "--reply-port",
        type=int,
        default=DEFAULT_REPLY_PORT,
        help="Local port used for AbletonOSC replies.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Seconds to wait for OSC replies.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Logging level.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Check whether AbletonOSC replies.")
    subparsers.add_parser("play", help="Start playback.")
    subparsers.add_parser("stop", help="Stop playback.")
    subparsers.add_parser("tracks", help="List track names.")

    tempo_parser = subparsers.add_parser("tempo", help="Set the song tempo.")
    tempo_parser.add_argument("bpm", type=float, help="Tempo in beats per minute.")

    fire_parser = subparsers.add_parser("fire-clip", help="Fire a session clip.")
    fire_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    fire_parser.add_argument("clip_index", type=int, help="Zero-based clip index.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    config = AbletonBridgeConfig(
        host=args.host,
        port=args.port,
        reply_port=args.reply_port,
        timeout=args.timeout,
    )
    client = AbletonOSCClient(config)

    try:
        if args.command == "status":
            print(f"AbletonOSC status: {client.status()}")
        elif args.command == "play":
            client.play()
            print("Playback started.")
        elif args.command == "stop":
            client.stop()
            print("Playback stopped.")
        elif args.command == "tempo":
            client.set_tempo(args.bpm)
            print(f"Tempo set to {args.bpm:g} BPM.")
        elif args.command == "tracks":
            tracks = client.tracks()
            if tracks:
                for index, name in enumerate(tracks):
                    print(f"{index}: {name}")
            else:
                print("No tracks returned by AbletonOSC.")
        elif args.command == "fire-clip":
            client.fire_clip(args.track_index, args.clip_index)
            print(f"Fired clip {args.clip_index} on track {args.track_index}.")
    except (AbletonOSCError, OSError, ValueError) as exc:
        logging.error("%s", exc)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
