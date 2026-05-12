# ableton-bridge

A small Python CLI/library for controlling Ableton Live over OSC through
[AbletonOSC](https://github.com/ideoforms/AbletonOSC) or a compatible OSC
remote script.

This project does not require Max for Live and does not assume Ableton Live is
currently running. Commands that need AbletonOSC will report a helpful error if
the OSC endpoint is not reachable.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

If you prefer requirements files:

```powershell
python -m pip install -r requirements.txt
```

## Install AbletonOSC

1. Download AbletonOSC from <https://github.com/ideoforms/AbletonOSC>.
2. Unzip it and rename the folder to `AbletonOSC`.
3. Copy the `AbletonOSC` folder into Ableton's Remote Scripts folder:
   - Windows: `C:\Users\<you>\Documents\Ableton\User Library\Remote Scripts`
   - macOS: `/Users/<you>/Music/Ableton/User Library/Remote Scripts`
4. Restart Ableton Live.
5. Open `Preferences > Link, Tempo & MIDI`.
6. In a Control Surface dropdown, select `AbletonOSC`.

AbletonOSC listens on OSC port `11000` by default and sends replies to port
`11001`.

## CLI

```powershell
ableton-bridge status
ableton-bridge doctor
ableton-bridge tempo-get
ableton-bridge current-time
ableton-bridge track-clips 0
ableton-bridge selected-track
ableton-bridge selected-scene
ableton-bridge select-track 0
ableton-bridge select-scene 0
ableton-bridge scene-name 0
ableton-bridge cue-points
ableton-bridge metronome
ableton-bridge metronome on
ableton-bridge play
ableton-bridge stop
ableton-bridge stop-all-clips
ableton-bridge stop-track-clips 0
ableton-bridge tempo 124
ableton-bridge tracks
ableton-bridge track-name 0
ableton-bridge track-color 0
ableton-bridge track-volume 0
ableton-bridge track-volume 0 0.75
ableton-bridge track-pan 0 -0.25
ableton-bridge track-mute 0 on
ableton-bridge track-solo 0 off
ableton-bridge track-arm 0 on
ableton-bridge fire-clip 0 0
ableton-bridge stop-clip 0 0
ableton-bridge clip-name 0 0
ableton-bridge clip-color 0 0
ableton-bridge clip-playing 0 0
```

Common options:

```powershell
ableton-bridge --host 127.0.0.1 --port 11000 --reply-port 11001 status
ableton-bridge --log-level DEBUG status
```

Use `doctor` after installing AbletonOSC. It checks whether the local Remote
Scripts folder exists and whether AbletonOSC replies on the configured OSC
ports.

## Example

```powershell
python examples/test_connection.py
```

## Tests

The unit tests mock OSC networking and do not require Ableton Live to be
running.

```powershell
python -m pytest
```
