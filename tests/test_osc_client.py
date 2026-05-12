from unittest.mock import patch

import pytest

from ableton_bridge.errors import AbletonOSCError
from ableton_bridge.models import AbletonSnapshot, SongSummary, ViewSummary
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


def test_stop_all_clips_checks_status_then_sends_stop_all():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok") as status:
        with patch.object(client, "send") as send:
            client.stop_all_clips()

    status.assert_called_once_with()
    send.assert_called_once_with("/live/song/stop_all_clips")


def test_stop_track_clips_sends_track_index():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.stop_track_clips(2)

    send.assert_called_once_with("/live/track/stop_all_clips", 2)


def test_stop_track_clips_rejects_negative_index():
    client = AbletonOSCClient()

    with pytest.raises(ValueError):
        client.stop_track_clips(-1)


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


def test_set_current_time_sends_beats():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_current_time(16)

    send.assert_called_once_with("/live/song/set/current_song_time", 16.0)


def test_is_playing_returns_bool():
    client = AbletonOSCClient()

    with patch.object(client, "_song_property", return_value=1):
        assert client.is_playing() is True


def test_set_loop_sends_integer_state():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_loop(False)

    send.assert_called_once_with("/live/song/set/loop", 0)


def test_set_loop_start_sends_beats():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_loop_start(4)

    send.assert_called_once_with("/live/song/set/loop_start", 4.0)


def test_set_loop_length_rejects_non_positive_beats():
    client = AbletonOSCClient()

    with pytest.raises(ValueError):
        client.set_loop_length(0)


def test_time_signature_returns_pair():
    client = AbletonOSCClient()

    with patch.object(client, "_song_property", side_effect=(7, 8)):
        assert client.time_signature() == (7, 8)


def test_set_time_signature_sends_numerator_and_denominator():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_time_signature(7, 8)

    assert send.call_args_list[0].args == ("/live/song/set/signature_numerator", 7)
    assert send.call_args_list[1].args == ("/live/song/set/signature_denominator", 8)


def test_get_metronome_returns_bool_from_reply():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/song/get/metronome", (1,)),
    ):
        assert client.get_metronome() is True


def test_set_metronome_sends_integer_state():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_metronome(False)

    send.assert_called_once_with("/live/song/set/metronome", 0)


def test_tracks_returns_names_from_reply():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/song/get/track_names", ("Drums", "Bass")),
    ):
        assert client.tracks() == ("Drums", "Bass")


def test_num_tracks_returns_int():
    client = AbletonOSCClient()

    with patch.object(client, "_song_property", return_value=5):
        assert client.num_tracks() == 5


def test_song_summary_combines_song_properties():
    client = AbletonOSCClient()

    with patch.object(client, "get_tempo", return_value=120.0):
        with patch.object(client, "current_time", return_value=1.0):
            with patch.object(client, "is_playing", return_value=True):
                with patch.object(client, "get_metronome", return_value=False):
                    with patch.object(client, "get_loop", return_value=True):
                        with patch.object(client, "song_length", return_value=64.0):
                            with patch.object(client, "time_signature", return_value=(4, 4)):
                                with patch.object(client, "num_tracks", return_value=2):
                                    with patch.object(client, "num_scenes", return_value=3):
                                        summary = client.song_summary()

    assert summary == SongSummary(
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


def test_selected_track_returns_index():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/view/get/selected_track", (3,)),
    ):
        assert client.selected_track() == 3


def test_selected_scene_returns_index():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/view/get/selected_scene", (4,)),
    ):
        assert client.selected_scene() == 4


def test_selected_clip_returns_track_and_scene_indexes():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/view/get/selected_clip", (1, 2)),
    ):
        assert client.selected_clip() == (1, 2)


def test_selected_device_returns_track_and_device_indexes():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/view/get/selected_device", (1, 3)),
    ):
        assert client.selected_device() == (1, 3)


def test_view_summary_combines_selected_indexes():
    client = AbletonOSCClient()

    with patch.object(client, "selected_track", return_value=0):
        with patch.object(client, "selected_scene", return_value=1):
            with patch.object(client, "selected_clip", return_value=(0, 1)):
                with patch.object(client, "selected_device", return_value=(0, 2)):
                    assert client.view_summary() == ViewSummary(0, 1, (0, 1), (0, 2))


def test_snapshot_combines_song_view_and_tracks():
    client = AbletonOSCClient()
    song = SongSummary(120.0, 1.0, True, False, True, 64.0, 4, 4, 2, 3)
    view = ViewSummary(0, 1, (0, 1), (0, 2))

    with patch.object(client, "song_summary", return_value=song):
        with patch.object(client, "view_summary", return_value=view):
            with patch.object(client, "tracks", return_value=("Drums", "Bass")):
                assert client.snapshot() == AbletonSnapshot(song, view, ("Drums", "Bass"))


def test_set_selected_track_sends_index():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_selected_track(2)

    send.assert_called_once_with("/live/view/set/selected_track", 2)


def test_set_selected_scene_sends_index():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_selected_scene(3)

    send.assert_called_once_with("/live/view/set/selected_scene", 3)


def test_set_selected_clip_sends_indexes():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_selected_clip(1, 2)

    send.assert_called_once_with("/live/view/set/selected_clip", 1, 2)


def test_set_selected_device_sends_indexes():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_selected_device(1, 2)

    send.assert_called_once_with("/live/view/set/selected_device", 1, 2)


def test_scene_name_returns_name_after_scene_index():
    client = AbletonOSCClient()

    with patch.object(client, "_scene_property", return_value="Verse") as prop:
        assert client.scene_name(0) == "Verse"

    prop.assert_called_once_with("name", 0)


def test_scene_color_returns_int():
    client = AbletonOSCClient()

    with patch.object(client, "_scene_property", return_value=123):
        assert client.scene_color(0) == 123


def test_scene_is_empty_returns_bool():
    client = AbletonOSCClient()

    with patch.object(client, "_scene_property", return_value=0):
        assert client.scene_is_empty(0) is False


def test_scene_tempo_returns_float():
    client = AbletonOSCClient()

    with patch.object(client, "_scene_property", return_value=128.0):
        assert client.scene_tempo(0) == 128.0


def test_set_scene_tempo_sends_tempo():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_scene_tempo(0, 127.5)

    send.assert_called_once_with("/live/scene/set/tempo", 0, 127.5)


def test_set_scene_tempo_rejects_non_positive_tempo():
    client = AbletonOSCClient()

    with pytest.raises(ValueError):
        client.set_scene_tempo(0, 0)


def test_scene_time_signature_returns_pair():
    client = AbletonOSCClient()

    with patch.object(client, "_scene_property", side_effect=(7, 8)):
        assert client.scene_time_signature(0) == (7, 8)


def test_set_scene_tempo_enabled_sends_integer_state():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_scene_tempo_enabled(0, True)

    send.assert_called_once_with("/live/scene/set/tempo_enabled", 0, 1)


def test_fire_scene_sends_fire():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.fire_scene(2)

    send.assert_called_once_with("/live/scene/fire", 2)


def test_fire_scene_as_selected_sends_fire_as_selected():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.fire_scene_as_selected(2)

    send.assert_called_once_with("/live/scene/fire_as_selected", 2)


def test_fire_selected_scene_sends_fire_selected():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.fire_selected_scene()

    send.assert_called_once_with("/live/scene/fire_selected")


def test_scene_property_queries_and_returns_value_after_index():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/scene/get/name", (0, "Verse")),
    ):
        assert client.scene_name(0) == "Verse"


def test_scene_name_rejects_negative_index():
    client = AbletonOSCClient()

    with pytest.raises(ValueError):
        client.scene_name(-1)


def test_cue_points_returns_name_time_pairs():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/song/get/cue_points", ("Intro", 1.0, "Drop", 33.0)),
    ):
        assert client.cue_points() == (("Intro", 1.0), ("Drop", 33.0))


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


def test_track_devices_skips_track_id_in_reply():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/track/get/devices/name", (0, "Operator", "Echo")),
    ):
        assert client.track_devices(0) == ("Operator", "Echo")


def test_track_name_returns_name():
    client = AbletonOSCClient()

    with patch.object(client, "_track_property", return_value="Bass") as prop:
        assert client.track_name(1) == "Bass"

    prop.assert_called_once_with("name", 1)


def test_track_volume_returns_float():
    client = AbletonOSCClient()

    with patch.object(client, "_track_property", return_value=0.8):
        assert client.track_volume(0) == 0.8


def test_set_track_volume_sends_value():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_track_volume(0, 0.5)

    send.assert_called_once_with("/live/track/set/volume", 0, 0.5)


def test_set_track_volume_rejects_out_of_range_value():
    client = AbletonOSCClient()

    with pytest.raises(ValueError):
        client.set_track_volume(0, 1.5)


def test_set_track_panning_sends_value():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_track_panning(1, -0.25)

    send.assert_called_once_with("/live/track/set/panning", 1, -0.25)


def test_set_track_panning_rejects_out_of_range_value():
    client = AbletonOSCClient()

    with pytest.raises(ValueError):
        client.set_track_panning(0, -1.5)


def test_track_mute_returns_bool():
    client = AbletonOSCClient()

    with patch.object(client, "_track_property", return_value=1):
        assert client.track_mute(0) is True


def test_track_solo_returns_bool():
    client = AbletonOSCClient()

    with patch.object(client, "_track_property", return_value=0):
        assert client.track_solo(0) is False


def test_set_track_arm_sends_integer_state():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_track_arm(2, True)

    send.assert_called_once_with("/live/track/set/arm", 2, 1)


def test_track_property_queries_and_returns_value_after_track_index():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/track/get/color", (0, 123456)),
    ):
        assert client.track_color(0) == 123456


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


def test_stop_clip_sends_clip_stop():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.stop_clip(1, 2)

    send.assert_called_once_with("/live/clip/stop", 1, 2)


def test_clip_name_returns_name():
    client = AbletonOSCClient()

    with patch.object(client, "_clip_property", return_value="Kick Loop") as prop:
        assert client.clip_name(0, 1) == "Kick Loop"

    prop.assert_called_once_with("name", 0, 1)


def test_clip_color_returns_int():
    client = AbletonOSCClient()

    with patch.object(client, "_clip_property", return_value=123):
        assert client.clip_color(0, 1) == 123


def test_clip_is_playing_returns_bool():
    client = AbletonOSCClient()

    with patch.object(client, "_clip_property", return_value=1):
        assert client.clip_is_playing(0, 1) is True


def test_clip_property_queries_and_returns_value_after_indexes():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/clip/get/name", (0, 1, "Kick Loop")),
    ):
        assert client.clip_name(0, 1) == "Kick Loop"


def test_device_name_returns_name():
    client = AbletonOSCClient()

    with patch.object(client, "_device_property", return_value="Operator") as prop:
        assert client.device_name(0, 1) == "Operator"

    prop.assert_called_once_with("name", 0, 1)


def test_device_type_returns_type():
    client = AbletonOSCClient()

    with patch.object(client, "_device_property", return_value="instrument"):
        assert client.device_type(0, 1) == "instrument"


def test_device_parameters_skips_track_and_device_ids():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply(
            "/live/device/get/parameters/name",
            (0, 1, "Device On", "Frequency"),
        ),
    ):
        assert client.device_parameters(0, 1) == ("Device On", "Frequency")


def test_device_parameter_value_returns_float():
    client = AbletonOSCClient()

    with patch.object(client, "_device_parameter_property", return_value=0.5) as prop:
        assert client.device_parameter_value(0, 1, 2) == 0.5

    prop.assert_called_once_with("value", 0, 1, 2)


def test_device_parameter_value_string_returns_text():
    client = AbletonOSCClient()

    with patch.object(client, "_device_parameter_property", return_value="2500 Hz"):
        assert client.device_parameter_value_string(0, 1, 2) == "2500 Hz"


def test_set_device_parameter_value_sends_value():
    client = AbletonOSCClient()

    with patch.object(client, "status", return_value="ok"):
        with patch.object(client, "send") as send:
            client.set_device_parameter_value(0, 1, 2, 0.75)

    send.assert_called_once_with("/live/device/set/parameter/value", 0, 1, 2, 0.75)


def test_device_property_queries_and_returns_value_after_indexes():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/device/get/name", (0, 1, "Operator")),
    ):
        assert client.device_name(0, 1) == "Operator"


def test_device_parameter_property_queries_and_returns_value_after_indexes():
    client = AbletonOSCClient()

    with patch.object(
        client,
        "query",
        return_value=OSCReply("/live/device/get/parameter/value", (0, 1, 2, 0.5)),
    ):
        assert client.device_parameter_value(0, 1, 2) == 0.5


def test_status_reports_missing_reply():
    client = AbletonOSCClient()

    with patch.object(client, "query", side_effect=AbletonOSCError("no reply")):
        with pytest.raises(AbletonOSCError):
            client.status()
