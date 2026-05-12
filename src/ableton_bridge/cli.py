"""Command-line interface for ableton-bridge."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

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
    subparsers.add_parser("doctor", help="Check local setup and AbletonOSC reachability.")
    subparsers.add_parser("tempo-get", help="Print the current song tempo.")
    subparsers.add_parser("current-time", help="Print the current song time in beats.")
    subparsers.add_parser("selected-track", help="Print the selected track index.")
    subparsers.add_parser("selected-scene", help="Print the selected scene index.")
    subparsers.add_parser("cue-points", help="List cue point names and beat positions.")
    subparsers.add_parser("play", help="Start playback.")
    subparsers.add_parser("stop", help="Stop playback.")
    subparsers.add_parser("stop-all-clips", help="Stop all currently playing clips.")
    subparsers.add_parser("tracks", help="List track names.")

    metronome_parser = subparsers.add_parser("metronome", help="Get or set metronome state.")
    metronome_parser.add_argument(
        "state",
        nargs="?",
        choices=("on", "off"),
        help="Optional state to set.",
    )

    tempo_parser = subparsers.add_parser("tempo", help="Set the song tempo.")
    tempo_parser.add_argument("bpm", type=float, help="Tempo in beats per minute.")

    fire_parser = subparsers.add_parser("fire-clip", help="Fire a session clip.")
    fire_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    fire_parser.add_argument("clip_index", type=int, help="Zero-based clip index.")

    stop_clip_parser = subparsers.add_parser("stop-clip", help="Stop a session clip.")
    stop_clip_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    stop_clip_parser.add_argument("clip_index", type=int, help="Zero-based clip index.")

    clip_name_parser = subparsers.add_parser("clip-name", help="Print a clip name.")
    clip_name_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    clip_name_parser.add_argument("clip_index", type=int, help="Zero-based clip index.")

    clip_color_parser = subparsers.add_parser("clip-color", help="Print a clip color value.")
    clip_color_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    clip_color_parser.add_argument("clip_index", type=int, help="Zero-based clip index.")

    clip_playing_parser = subparsers.add_parser(
        "clip-playing",
        help="Print whether a clip is playing.",
    )
    clip_playing_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    clip_playing_parser.add_argument("clip_index", type=int, help="Zero-based clip index.")

    clips_parser = subparsers.add_parser("track-clips", help="List clip names on a track.")
    clips_parser.add_argument("track_index", type=int, help="Zero-based track index.")

    devices_parser = subparsers.add_parser("track-devices", help="List device names on a track.")
    devices_parser.add_argument("track_index", type=int, help="Zero-based track index.")

    track_name_parser = subparsers.add_parser("track-name", help="Print a track name.")
    track_name_parser.add_argument("track_index", type=int, help="Zero-based track index.")

    track_color_parser = subparsers.add_parser("track-color", help="Print a track color value.")
    track_color_parser.add_argument("track_index", type=int, help="Zero-based track index.")

    track_volume_parser = subparsers.add_parser("track-volume", help="Get or set track volume.")
    track_volume_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    track_volume_parser.add_argument("volume", nargs="?", type=float, help="Optional volume, 0.0 to 1.0.")

    track_pan_parser = subparsers.add_parser("track-pan", help="Get or set track panning.")
    track_pan_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    track_pan_parser.add_argument("panning", nargs="?", type=float, help="Optional panning, -1.0 to 1.0.")

    for command, help_text in (
        ("track-mute", "Get or set track mute state."),
        ("track-solo", "Get or set track solo state."),
        ("track-arm", "Get or set track arm state."),
    ):
        track_bool_parser = subparsers.add_parser(command, help=help_text)
        track_bool_parser.add_argument("track_index", type=int, help="Zero-based track index.")
        track_bool_parser.add_argument(
            "state",
            nargs="?",
            choices=("on", "off"),
            help="Optional state to set.",
        )

    stop_track_parser = subparsers.add_parser(
        "stop-track-clips",
        help="Stop all clips on one track.",
    )
    stop_track_parser.add_argument("track_index", type=int, help="Zero-based track index.")

    scene_name_parser = subparsers.add_parser("scene-name", help="Print a scene name.")
    scene_name_parser.add_argument("scene_index", type=int, help="Zero-based scene index.")

    set_selected_track_parser = subparsers.add_parser(
        "select-track",
        help="Set the selected track.",
    )
    set_selected_track_parser.add_argument("track_index", type=int, help="Zero-based track index.")

    set_selected_scene_parser = subparsers.add_parser(
        "select-scene",
        help="Set the selected scene.",
    )
    set_selected_scene_parser.add_argument("scene_index", type=int, help="Zero-based scene index.")

    device_name_parser = subparsers.add_parser("device-name", help="Print a device name.")
    device_name_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    device_name_parser.add_argument("device_index", type=int, help="Zero-based device index.")

    device_type_parser = subparsers.add_parser("device-type", help="Print a device type.")
    device_type_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    device_type_parser.add_argument("device_index", type=int, help="Zero-based device index.")

    device_params_parser = subparsers.add_parser(
        "device-params",
        help="List device parameter names.",
    )
    device_params_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    device_params_parser.add_argument("device_index", type=int, help="Zero-based device index.")

    param_value_parser = subparsers.add_parser(
        "device-param",
        help="Get or set a device parameter value.",
    )
    param_value_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    param_value_parser.add_argument("device_index", type=int, help="Zero-based device index.")
    param_value_parser.add_argument("parameter_index", type=int, help="Zero-based parameter index.")
    param_value_parser.add_argument("value", nargs="?", type=float, help="Optional value to set.")

    param_string_parser = subparsers.add_parser(
        "device-param-text",
        help="Print a readable device parameter value.",
    )
    param_string_parser.add_argument("track_index", type=int, help="Zero-based track index.")
    param_string_parser.add_argument("device_index", type=int, help="Zero-based device index.")
    param_string_parser.add_argument("parameter_index", type=int, help="Zero-based parameter index.")

    return parser


def default_remote_scripts_path() -> Path:
    return Path.home() / "Documents" / "Ableton" / "User Library" / "Remote Scripts"


def run_doctor(client: AbletonOSCClient) -> int:
    exit_code = 0
    remote_scripts = default_remote_scripts_path()
    abletonosc = remote_scripts / "AbletonOSC"

    if remote_scripts.exists():
        print(f"Remote Scripts folder: {remote_scripts}")
    else:
        print(f"Remote Scripts folder missing: {remote_scripts}")
        exit_code = 1

    if (abletonosc / "__init__.py").exists():
        print(f"AbletonOSC installed: {abletonosc}")
    else:
        print(f"AbletonOSC not found: {abletonosc}")
        exit_code = 1

    try:
        print(f"AbletonOSC status: {client.status()}")
    except AbletonOSCError as exc:
        print(f"AbletonOSC not reachable: {exc}")
        exit_code = 1

    return exit_code


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
        elif args.command == "doctor":
            return run_doctor(client)
        elif args.command == "tempo-get":
            print(f"Tempo: {client.get_tempo():g} BPM")
        elif args.command == "current-time":
            print(f"Current time: {client.current_time():g} beats")
        elif args.command == "selected-track":
            print(f"Selected track: {client.selected_track()}")
        elif args.command == "selected-scene":
            print(f"Selected scene: {client.selected_scene()}")
        elif args.command == "select-track":
            client.set_selected_track(args.track_index)
            print(f"Selected track set to {args.track_index}.")
        elif args.command == "select-scene":
            client.set_selected_scene(args.scene_index)
            print(f"Selected scene set to {args.scene_index}.")
        elif args.command == "scene-name":
            print(f"Scene {args.scene_index}: {client.scene_name(args.scene_index)}")
        elif args.command == "cue-points":
            cue_points = client.cue_points()
            if cue_points:
                for name, time in cue_points:
                    print(f"{name}: {time:g} beats")
            else:
                print("No cue points returned by AbletonOSC.")
        elif args.command == "metronome":
            if args.state is None:
                state = "on" if client.get_metronome() else "off"
                print(f"Metronome: {state}")
            else:
                client.set_metronome(args.state == "on")
                print(f"Metronome set to {args.state}.")
        elif args.command == "play":
            client.play()
            print("Playback started.")
        elif args.command == "stop":
            client.stop()
            print("Playback stopped.")
        elif args.command == "stop-all-clips":
            client.stop_all_clips()
            print("Stopped all clips.")
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
        elif args.command == "stop-clip":
            client.stop_clip(args.track_index, args.clip_index)
            print(f"Stopped clip {args.clip_index} on track {args.track_index}.")
        elif args.command == "clip-name":
            print(
                f"Clip {args.clip_index} on track {args.track_index}: "
                f"{client.clip_name(args.track_index, args.clip_index)}"
            )
        elif args.command == "clip-color":
            print(
                f"Clip {args.clip_index} on track {args.track_index} color: "
                f"{client.clip_color(args.track_index, args.clip_index)}"
            )
        elif args.command == "clip-playing":
            state = "yes" if client.clip_is_playing(args.track_index, args.clip_index) else "no"
            print(f"Clip {args.clip_index} on track {args.track_index} playing: {state}")
        elif args.command == "track-clips":
            clips = client.track_clips(args.track_index)
            if clips:
                for index, name in enumerate(clips):
                    print(f"{index}: {name}")
            else:
                print(f"No clips returned for track {args.track_index}.")
        elif args.command == "track-devices":
            devices = client.track_devices(args.track_index)
            if devices:
                for index, name in enumerate(devices):
                    print(f"{index}: {name}")
            else:
                print(f"No devices returned for track {args.track_index}.")
        elif args.command == "track-name":
            print(f"Track {args.track_index}: {client.track_name(args.track_index)}")
        elif args.command == "track-color":
            print(f"Track {args.track_index} color: {client.track_color(args.track_index)}")
        elif args.command == "track-volume":
            if args.volume is None:
                print(f"Track {args.track_index} volume: {client.track_volume(args.track_index):g}")
            else:
                client.set_track_volume(args.track_index, args.volume)
                print(f"Track {args.track_index} volume set to {args.volume:g}.")
        elif args.command == "track-pan":
            if args.panning is None:
                print(f"Track {args.track_index} panning: {client.track_panning(args.track_index):g}")
            else:
                client.set_track_panning(args.track_index, args.panning)
                print(f"Track {args.track_index} panning set to {args.panning:g}.")
        elif args.command == "track-mute":
            if args.state is None:
                state = "on" if client.track_mute(args.track_index) else "off"
                print(f"Track {args.track_index} mute: {state}")
            else:
                client.set_track_mute(args.track_index, args.state == "on")
                print(f"Track {args.track_index} mute set to {args.state}.")
        elif args.command == "track-solo":
            if args.state is None:
                state = "on" if client.track_solo(args.track_index) else "off"
                print(f"Track {args.track_index} solo: {state}")
            else:
                client.set_track_solo(args.track_index, args.state == "on")
                print(f"Track {args.track_index} solo set to {args.state}.")
        elif args.command == "track-arm":
            if args.state is None:
                state = "on" if client.track_arm(args.track_index) else "off"
                print(f"Track {args.track_index} arm: {state}")
            else:
                client.set_track_arm(args.track_index, args.state == "on")
                print(f"Track {args.track_index} arm set to {args.state}.")
        elif args.command == "stop-track-clips":
            client.stop_track_clips(args.track_index)
            print(f"Stopped all clips on track {args.track_index}.")
        elif args.command == "device-name":
            print(
                f"Device {args.device_index} on track {args.track_index}: "
                f"{client.device_name(args.track_index, args.device_index)}"
            )
        elif args.command == "device-type":
            print(
                f"Device {args.device_index} on track {args.track_index} type: "
                f"{client.device_type(args.track_index, args.device_index)}"
            )
        elif args.command == "device-params":
            parameters = client.device_parameters(args.track_index, args.device_index)
            if parameters:
                for index, name in enumerate(parameters):
                    print(f"{index}: {name}")
            else:
                print(
                    "No parameters returned for "
                    f"device {args.device_index} on track {args.track_index}."
                )
        elif args.command == "device-param":
            if args.value is None:
                value = client.device_parameter_value(
                    args.track_index,
                    args.device_index,
                    args.parameter_index,
                )
                print(
                    f"Parameter {args.parameter_index} on device {args.device_index} "
                    f"track {args.track_index}: {value:g}"
                )
            else:
                client.set_device_parameter_value(
                    args.track_index,
                    args.device_index,
                    args.parameter_index,
                    args.value,
                )
                print(
                    f"Parameter {args.parameter_index} on device {args.device_index} "
                    f"track {args.track_index} set to {args.value:g}."
                )
        elif args.command == "device-param-text":
            value = client.device_parameter_value_string(
                args.track_index,
                args.device_index,
                args.parameter_index,
            )
            print(
                f"Parameter {args.parameter_index} on device {args.device_index} "
                f"track {args.track_index}: {value}"
            )
    except (AbletonOSCError, OSError, ValueError) as exc:
        logging.error("%s", exc)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
