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


def test_client_errors_return_nonzero():
    with patch("ableton_bridge.cli.AbletonOSCClient") as client_class:
        client_class.return_value.status.side_effect = AbletonOSCError("no reply")

        result = cli.main(["status"])

    assert result == 1
