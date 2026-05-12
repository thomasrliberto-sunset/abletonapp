from unittest.mock import patch

import pytest

from ableton_bridge.errors import AbletonOSCError
from ableton_bridge.osc_client import AbletonOSCClient, OSCReply


def test_play_checks_status_then_sends_start():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok") as status:
        with patch.object(client, "send") as send:
            client.play()

    status.assert_called_once_with()
    send.assert_called_once_with("/live/song/start_playing")


def test_set_tempo_sends_float_value():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_tempo(124)

    send.assert_called_once_with("/live/song/set/tempo", 124.0)


def test_set_tempo_rejects_non_positive_bpm():
    client = AbletonOSCClient()

    with pytest.raises(ValueError):
        client.set_tempo(0)


def test_get_tempo_returns_float_from_reply():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/song/get/tempo", (127.5,)),
    ):
        assert client.get_tempo() == 127.5


def test_current_time_returns_float_from_reply():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/song/get/current_song_time", (32.0,)),
    ):
        assert client.current_time() == 32.0


def test_tracks_returns_names_from_reply():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/song/get/track_names", ("Drums", "Bass")),
    ):
        assert client.tracks() == ("Drums", "Bass")


def test_track_clips_skips_track_id_in_reply():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/track/get/clips/name", (0, "Intro", "Drop")),
    ):
        assert client.track_clips(0) == ("Intro", "Drop")


def test_track_clips_rejects_negative_index():
    client = AbletonOSCClient()

    with pytest.raises(ValueError):
        client.track_clips(-1)


def test_fire_clip_rejects_negative_indexes():
    client = AbletonOSCClient()

    with pytest.raises(ValueError):
        client.fire_clip(-1, 0)


def test_fire_clip_sends_clip_fire():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.fire_clip(1, 2)

    send.assert_called_once_with("/live/clip/fire", 1, 2)


def test_status_reports_missing_reply():
    client = AbletonOSCClient()

    with patch.object(client, "query", side_effect=AbletonOSCError("no reply")):
        with pytest.raises(AbletonOSCError):
            client.status()
