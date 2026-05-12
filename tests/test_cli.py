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
