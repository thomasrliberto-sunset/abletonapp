from unittest.mock import patch

from ableton_bridge import cli
from ableton_bridge.errors import AbletonOSCError
from ableton_bridge.models import AbletonSnapshot, SongSummary, ViewSummary


def test_status_command_prints_status(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.status.return_value = "ok"

        result = cli.main(["status"])

    assert result == 0
    assert "AbletonOSC status: ok" in capsys.readouterr().out


def test_tempo_command_uses_bpm():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["tempo", "128"])

    assert result == 0
    client_class.return_value.set_tempo.assert_called_once_with(128.0)


def test_tempo_get_command_prints_current_tempo(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.get_tempo.return_value = 123.5

        result = cli.main(["tempo-get"])

    assert result == 0
    assert "Tempo: 123.5 BPM" in capsys.readouterr().out


def test_current_time_command_prints_current_time(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.current_time.return_value = 16.0

        result = cli.main(["current-time"])

    assert result == 0
    assert "Current time: 16 beats" in capsys.readouterr().out


def test_set_current_time_command_sets_beats():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["set-current-time", "32"])

    assert result == 0
    client_class.return_value.set_current_time.assert_called_once_with(32.0)


def test_is_playing_command_prints_state(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.is_playing.return_value = True

        result = cli.main(["is-playing"])

    assert result == 0
    assert "Playing: yes" in capsys.readouterr().out


def test_signature_command_prints_signature(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.time_signature.return_value = (7, 8)

        result = cli.main(["signature"])

    assert result == 0
    assert "Time signature: 7/8" in capsys.readouterr().out


def test_song_summary_command_prints_json(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.song_summary.return_value = SongSummary(
            tempo=120.0,
            current_time=1.0,
            is_playing=True,
            metronome=False,
            loop=True,
            song_length=64.0,
            signature_numerator=4,
            signature_denominator=4,
            num_tracks=2,
            num_scenes=3,
        )

        result = cli.main(["song-summary"])

    assert result == 0
    assert '"tempo": 120.0' in capsys.readouterr().out


def test_snapshot_command_prints_json(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.snapshot.return_value = AbletonSnapshot(
            song=SongSummary(
                tempo=120.0,
                current_time=1.0,
                is_playing=True,
                metronome=False,
                loop=True,
                song_length=64.0,
                signature_numerator=4,
                signature_denominator=4,
                num_tracks=2,
                num_scenes=3,
            ),
            view=ViewSummary(
                selected_track=0,
                selected_scene=1,
                selected_clip=(0, 1),
                selected_device=(0, 0),
            ),
            tracks=("Drums", "Bass"),
        )

        result = cli.main(["snapshot"])

    assert result == 0
    assert '"tracks": [' in capsys.readouterr().out


def test_track_clips_command_prints_clip_names(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.track_clips.return_value = ("Intro", "Drop")

        result = cli.main(["track-clips", "0"])

    assert result == 0
    assert "0: Intro" in capsys.readouterr().out
    client_class.return_value.track_clips.assert_called_once_with(0)


def test_track_devices_command_prints_device_names(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.track_devices.return_value = ("Operator", "Echo")

        result = cli.main(["track-devices", "0"])

    assert result == 0
    assert "0: Operator" in capsys.readouterr().out
    client_class.return_value.track_devices.assert_called_once_with(0)


def test_track_name_command_prints_name(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.track_name.return_value = "Bass"

        result = cli.main(["track-name", "1"])

    assert result == 0
    assert "Track 1: Bass" in capsys.readouterr().out


def test_track_volume_get_command_prints_volume(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.track_volume.return_value = 0.75

        result = cli.main(["track-volume", "0"])

    assert result == 0
    assert "Track 0 volume: 0.75" in capsys.readouterr().out


def test_track_volume_set_command_sets_volume():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["track-volume", "0", "0.5"])

    assert result == 0
    client_class.return_value.set_track_volume.assert_called_once_with(0, 0.5)


def test_track_pan_set_command_sets_panning():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["track-pan", "0", "-0.25"])

    assert result == 0
    client_class.return_value.set_track_panning.assert_called_once_with(0, -0.25)


def test_track_mute_get_command_prints_state(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.track_mute.return_value = True

        result = cli.main(["track-mute", "0"])

    assert result == 0
    assert "Track 0 mute: on" in capsys.readouterr().out


def test_track_solo_set_command_sets_state():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["track-solo", "0", "on"])

    assert result == 0
    client_class.return_value.set_track_solo.assert_called_once_with(0, True)


def test_track_arm_set_command_sets_state():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["track-arm", "0", "off"])

    assert result == 0
    client_class.return_value.set_track_arm.assert_called_once_with(0, False)


def test_stop_clip_command_calls_client():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["stop-clip", "1", "2"])

    assert result == 0
    client_class.return_value.stop_clip.assert_called_once_with(1, 2)


def test_clip_name_command_prints_name(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.clip_name.return_value = "Kick Loop"

        result = cli.main(["clip-name", "0", "1"])

    assert result == 0
    assert "Clip 1 on track 0: Kick Loop" in capsys.readouterr().out


def test_clip_color_command_prints_color(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.clip_color.return_value = 123

        result = cli.main(["clip-color", "0", "1"])

    assert result == 0
    assert "Clip 1 on track 0 color: 123" in capsys.readouterr().out


def test_clip_playing_command_prints_state(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.clip_is_playing.return_value = True

        result = cli.main(["clip-playing", "0", "1"])

    assert result == 0
    assert "Clip 1 on track 0 playing: yes" in capsys.readouterr().out


def test_device_name_command_prints_name(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.device_name.return_value = "Operator"

        result = cli.main(["device-name", "0", "1"])

    assert result == 0
    assert "Device 1 on track 0: Operator" in capsys.readouterr().out


def test_device_params_command_prints_parameter_names(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.device_parameters.return_value = ("Device On", "Frequency")

        result = cli.main(["device-params", "0", "1"])

    assert result == 0
    assert "1: Frequency" in capsys.readouterr().out


def test_device_param_get_command_prints_value(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.device_parameter_value.return_value = 0.5

        result = cli.main(["device-param", "0", "1", "2"])

    assert result == 0
    assert "Parameter 2 on device 1 track 0: 0.5" in capsys.readouterr().out


def test_device_param_set_command_sets_value():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["device-param", "0", "1", "2", "0.75"])

    assert result == 0
    client_class.return_value.set_device_parameter_value.assert_called_once_with(0, 1, 2, 0.75)


def test_device_param_text_command_prints_value_string(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.device_parameter_value_string.return_value = "2500 Hz"

        result = cli.main(["device-param-text", "0", "1", "2"])

    assert result == 0
    assert "2500 Hz" in capsys.readouterr().out


def test_selected_track_command_prints_index(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.selected_track.return_value = 2

        result = cli.main(["selected-track"])

    assert result == 0
    assert "Selected track: 2" in capsys.readouterr().out


def test_selected_scene_command_prints_index(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.selected_scene.return_value = 1

        result = cli.main(["selected-scene"])

    assert result == 0
    assert "Selected scene: 1" in capsys.readouterr().out


def test_selected_clip_command_prints_indexes(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.selected_clip.return_value = (0, 2)

        result = cli.main(["selected-clip"])

    assert result == 0
    assert "Selected clip: track 0, scene 2" in capsys.readouterr().out


def test_selected_device_command_prints_indexes(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.selected_device.return_value = (1, 3)

        result = cli.main(["selected-device"])

    assert result == 0
    assert "Selected device: track 1, device 3" in capsys.readouterr().out


def test_select_track_command_sets_index():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["select-track", "2"])

    assert result == 0
    client_class.return_value.set_selected_track.assert_called_once_with(2)


def test_select_scene_command_sets_index():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["select-scene", "3"])

    assert result == 0
    client_class.return_value.set_selected_scene.assert_called_once_with(3)


def test_select_clip_command_sets_indexes():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["select-clip", "1", "2"])

    assert result == 0
    client_class.return_value.set_selected_clip.assert_called_once_with(1, 2)


def test_select_device_command_sets_indexes():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["select-device", "1", "2"])

    assert result == 0
    client_class.return_value.set_selected_device.assert_called_once_with(1, 2)


def test_scene_name_command_prints_name(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.scene_name.return_value = "Verse"

        result = cli.main(["scene-name", "0"])

    assert result == 0
    assert "Scene 0: Verse" in capsys.readouterr().out


def test_scene_color_command_prints_color(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.scene_color.return_value = 456

        result = cli.main(["scene-color", "0"])

    assert result == 0
    assert "Scene 0 color: 456" in capsys.readouterr().out


def test_scene_state_command_prints_state(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.scene_is_empty.return_value = False
        client_class.return_value.scene_is_triggered.return_value = True

        result = cli.main(["scene-state", "0"])

    assert result == 0
    assert "Scene 0 empty: no, triggered: yes" in capsys.readouterr().out


def test_scene_tempo_get_command_prints_tempo(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.scene_tempo.return_value = 128.0

        result = cli.main(["scene-tempo", "0"])

    assert result == 0
    assert "Scene 0 tempo: 128 BPM" in capsys.readouterr().out


def test_scene_tempo_set_command_sets_tempo():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["scene-tempo", "0", "127.5"])

    assert result == 0
    client_class.return_value.set_scene_tempo.assert_called_once_with(0, 127.5)


def test_scene_tempo_enabled_set_command_sets_state():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["scene-tempo-enabled", "0", "on"])

    assert result == 0
    client_class.return_value.set_scene_tempo_enabled.assert_called_once_with(0, True)


def test_scene_signature_command_prints_signature(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.scene_time_signature.return_value = (7, 8)

        result = cli.main(["scene-signature", "0"])

    assert result == 0
    assert "Scene 0 time signature: 7/8" in capsys.readouterr().out


def test_fire_scene_command_calls_client():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["fire-scene", "2"])

    assert result == 0
    client_class.return_value.fire_scene.assert_called_once_with(2)


def test_fire_selected_scene_command_calls_client():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["fire-selected-scene"])

    assert result == 0
    client_class.return_value.fire_selected_scene.assert_called_once_with()


def test_cue_points_command_prints_points(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.cue_points.return_value = (("Intro", 1.0), ("Drop", 33.0))

        result = cli.main(["cue-points"])

    assert result == 0
    output = capsys.readouterr().out
    assert "Intro: 1 beats" in output
    assert "Drop: 33 beats" in output


def test_metronome_get_command_prints_state(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.get_metronome.return_value = True

        result = cli.main(["metronome"])

    assert result == 0
    assert "Metronome: on" in capsys.readouterr().out


def test_metronome_set_command_sets_state():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["metronome", "off"])

    assert result == 0
    client_class.return_value.set_metronome.assert_called_once_with(False)


def test_loop_get_command_prints_state(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.get_loop.return_value = True

        result = cli.main(["loop"])

    assert result == 0
    assert "Loop: on" in capsys.readouterr().out


def test_loop_set_command_sets_state():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["loop", "off"])

    assert result == 0
    client_class.return_value.set_loop.assert_called_once_with(False)


def test_loop_start_set_command_sets_beats():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["loop-start", "4"])

    assert result == 0
    client_class.return_value.set_loop_start.assert_called_once_with(4.0)


def test_record_mode_set_command_sets_state():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["record-mode", "on"])

    assert result == 0
    client_class.return_value.set_record_mode.assert_called_once_with(True)


def test_stop_all_clips_command_calls_client():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["stop-all-clips"])

    assert result == 0
    client_class.return_value.stop_all_clips.assert_called_once_with()


def test_stop_track_clips_command_uses_track_index():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        result = cli.main(["stop-track-clips", "3"])

    assert result == 0
    client_class.return_value.stop_track_clips.assert_called_once_with(3)


def test_doctor_returns_zero_when_setup_and_status_are_ok(tmp_path, capsys):
    remote_scripts = tmp_path / "Remote Scripts"
    abletonosc = remote_scripts / "AbletonOSC"
    abletonosc.mkdir(parents=True)
    (abletonosc / "__init__.py").write_text("", encoding="utf-8")

    with patch("ableton_bridge.cli.default_remote_scripts_path", return_value=remote_scripts):
        with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
            client_class.return_value.status.return_value = "ok"

            result = cli.main(["doctor"])

    assert result == 0
    assert "AbletonOSC installed" in capsys.readouterr().out


def test_doctor_returns_nonzero_when_abletonosc_is_unreachable(tmp_path):
    remote_scripts = tmp_path / "Remote Scripts"
    abletonosc = remote_scripts / "AbletonOSC"
    abletonosc.mkdir(parents=True)
    (abletonosc / "__init__.py").write_text("", encoding="utf-8")

    with patch("ableton_bridge.cli.default_remote_scripts_path", return_value=remote_scripts):
        with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
            client_class.return_value.status.side_effect = AbletonOSCError("no reply")

            result = cli.main(["doctor"])

    assert result == 1


def test_client_errors_return_nonzero():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.status.side_effect = AbletonOSCError("no reply")

        result = cli.main(["status"])

    assert result == 1
