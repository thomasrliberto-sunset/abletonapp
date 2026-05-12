from unittest.mock import patch

from ableton_bridge import cli
from ableton_bridge.errors import AbletonOSCError


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


def test_track_clips_command_prints_clip_names(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.track_clips.return_value = ("Intro", "Drop")

        result = cli.main(["track-clips", "0"])

    assert result == 0
    assert "0: Intro" in capsys.readouterr().out
    client_class.return_value.track_clips.assert_called_once_with(0)


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


def test_scene_name_command_prints_name(capsys):
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.scene_name.return_value = "Verse"

        result = cli.main(["scene-name", "0"])

    assert result == 0
    assert "Scene 0: Verse" in capsys.readouterr().out


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
