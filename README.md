# Piper TTS Wrapper

A lightweight Python wrapper around the [Piper](https://github.com/rhasspy/piper) offline
text-to-speech engine, with automatic Persian/English language detection and pluggable
audio playback backends.

Tested and used on **Windows**.

## Features

- 🗣️ **Offline TTS** via the Piper CLI — no internet connection or cloud API required
- 🌐 **Automatic language detection** (Persian / English) per input text, with automatic
  voice model selection
- 🔊 **Pluggable audio playback** — choose between:
  - `sounddevice` (default, cross-platform, in-process playback)
  - `ffplay` (via FFmpeg)
  - `termux-media-player` (Android / Termux)
  - any custom executable
- 💾 **Local caching** of generated `.wav` files
- 🧩 **Lazy imports** — optional dependencies (`sounddevice`, `soundfile`, etc.) are only
  imported when the feature that needs them is actually used

## Project Structure

```
.
├── TTS.py                       # Piper wrapper: language detection + speech synthesis
└── sensor/
    └── audio/
        └── player/
            └── AudioPlayer.py   # Backend-agnostic audio playback
```

> Adjust the paths above to match your actual project layout — `TTS.speak()` imports
> `AudioPlayer` from `sensor.audio.player.AudioPlayer`, so keep that import path in sync
> with wherever `AudioPlayer.py` lives in your project.

## Requirements

- Python 3.10+
- [Piper](https://github.com/rhasspy/piper) executable, plus a Persian voice model
  (`.onnx`) and, optionally, an English voice model (`.onnx`)
- Depending on the playback backend you choose:
  - `sounddevice` backend: `pip install sounddevice soundfile`
  - `ffplay` backend: [FFmpeg](https://ffmpeg.org/) installed and available on `PATH`
  - `termux-media-player` backend: Termux on Android

Install the Python dependencies:

```bash
pip install sounddevice soundfile
```

## Installation

1. Download a Piper release for your platform from the
   [Piper releases page](https://github.com/rhasspy/piper/releases).
2. Download the voice model(s) you need (e.g. a Persian `fa_IR` model, and optionally an
   English `en_US` model) from the
   [Piper voices repository](https://huggingface.co/rhasspy/piper-voices).
3. Copy `TTS.py` and `AudioPlayer.py` into your project, keeping the import path used in
   `TTS.speak()` consistent with your folder structure.

## Usage

### Basic synthesis and playback

```python
from TTS import TTS

tts = TTS(
    piper_path="path/to/piper.exe",
    fa_model="path/to/fa_IR-voice.onnx",
    en_model="path/to/en_US-voice.onnx",  # optional
)

tts.speak("سلام، حالت چطوره؟")   # Persian text -> uses fa_model, auto-detected
tts.speak("Hello, how are you?")  # English text -> uses en_model, auto-detected
```

### Saving audio without playing it

```python
tts.save("این متن ذخیره میشه ولی پخش نمیشه.", filename="greeting.wav")
```

### Generating audio and handling the file yourself

```python
output_path = tts.generate("متن نمونه", filename="sample.wav")
print(output_path)  # e.g. llm_sound/sample.wav
```

### Choosing a different playback backend

```python
tts = TTS(
    piper_path="path/to/piper.exe",
    fa_model="path/to/fa_IR-voice.onnx",
    player_backend="ffplay",  # or "termux-media-player", or a custom executable
)
```

### Using `AudioPlayer` directly

```python
from sensor.audio.player.AudioPlayer import AudioPlayer

player = AudioPlayer(backend="sounddevice")
player.play("llm_sound/sample.wav")
```

## Configuration Reference

### `TTS(piper_path, fa_model, en_model=None, sounds_file="llm_sound", player_backend="sounddevice")`

| Parameter        | Type          | Default        | Description                                                        |
|-------------------|---------------|----------------|----------------------------------------------------------------------|
| `piper_path`      | `str \| Path` | —              | Path to the Piper executable                                       |
| `fa_model`        | `str \| Path` | —              | Path to the Persian voice model (also used as the fallback model)  |
| `en_model`        | `str \| Path` | `None`         | Path to the English voice model (optional)                         |
| `sounds_file`     | `str`         | `"llm_sound"`  | Local cache directory for generated `.wav` files                   |
| `player_backend`  | `str`         | `"sounddevice"`| Playback backend used by `speak()`                                 |

### `AudioPlayer(backend="sounddevice")`

| Parameter | Type          | Default          | Description                                                    |
|-----------|---------------|------------------|--------------------------------------------------------------------|
| `backend` | `str \| Path` | `"sounddevice"`  | `"sounddevice"`, `"ffplay"`, `"termux-media-player"`, or a custom executable name/path |

## How Language Detection Works

`TTS.detect_language()` checks the input text for any character in the Arabic Unicode
block (`U+0600`–`U+06FF`), which also covers Persian letters. If found, the text is
classified as Persian (`"fa"`); otherwise it's treated as English (`"en"`). This is a
lightweight heuristic rather than a full language detector, so mixed-language text is
classified by the presence of Persian characters alone.

## Error Handling

- `TTS.generate()` raises `RuntimeError` if the Piper process exits with a non-zero
  return code (the error message includes Piper's `stderr` output), or if Piper reports
  success but no output file was produced.
- `AudioPlayer.__init__` raises `TypeError` if `backend` is not a `str` or `Path`.
- The `ffplay`, `termux-media-player`, and custom backends raise
  `subprocess.CalledProcessError` if the underlying command fails.

## License

Add your license of choice here (e.g. MIT).