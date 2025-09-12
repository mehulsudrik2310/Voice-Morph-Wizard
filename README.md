# Voice Morph Wizard

Voice Morph Wizard is a small desktop application written in Python that lets you apply real-time and offline voice/audio modulation effects (alien, robotic, pitch shifts, echo, flanger, ping-pong, etc.) to audio files or microphone input. It provides a simple Tkinter GUI for choosing an input (microphone or audio file), selecting an effect, converting audio, previewing the original and processed audio, and saving the processed WAV file.

This README covers installation, usage, the included effects, development tips, and troubleshooting notes.

## Project structure

Top-level files:

- `main.py` — Application entry point and GUI glue code (Tkinter). Handles playback, upload, conversion, and UI wiring.
- `ui.py` — Small helpers for UI behaviour (button colours and drawing connection lines on a canvas).
- `filters.py` — DSP implementations of available audio effects using NumPy (and SciPy in a few places).
- `utils.py` — Utility helpers (file name shortening, dialogs, upload helper for audio clips).
- `audio_clips/` — Example short audio clips bundled with the project used by the "Audio Clips" window.
- `requirements.txt` — Exact Python dependency pins used by the project.

## Features

- Real-time microphone input processing (requires an audio input device and PyAudio).
- Offline conversion of uploaded `.wav` and `.mp3` files to a modulated WAV you can preview and download.
- Multiple effects: Alien, Robotic, Male/Female/Baby pitch shifts, Echo, Ping-Pong, Alternate Channels, Mutation (vibrato), Flanger, and more.
- Small, easy to extend codebase if you want to add new filters or change UI behaviour.

## Requirements

The project uses Python 3.9+ and the pins in `requirements.txt`:

```
numpy==1.26.2
PyAudio==0.2.14
pydub==0.25.1
scipy==1.11.4
simpleaudio==1.0.4
```

Notes:
- `PyAudio` requires portaudio to be installed on your system. On Windows you can often install the `PyAudio` wheel; on macOS/Linux install `portaudio` via your package manager first (e.g. `brew install portaudio` or `sudo apt install portaudio19-dev`).
- `pydub` requires `ffmpeg` or `avlib` available on PATH for MP3 decoding/encoding. Install `ffmpeg` for your OS and ensure it is on PATH.

## Installation (Windows)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Install ffmpeg and make sure it is on your PATH (for MP3 support). On Windows you can download a static build from https://ffmpeg.org and add the `bin` folder to PATH.

4. (Optional) If `PyAudio` wheel is problematic to build, download a prebuilt wheel for your Python version from a trusted source and install with `pip install <wheel-file>`.

## Running the app

From the project root (where `main.py` is located) run:

```powershell
python main.py
```

The application window will open. High-level usage:

- Toggle `Microphone` to enable realtime processing from your mic (requires a working input device). Toggle the filter button and choose a filter from the combobox.
- Use `File -> Upload Audio` to choose a local `.wav` or `.mp3`. After upload you can `Convert` (apply the selected effect), preview the original and processed audio, and `Download` the result as a WAV.
- `Audio Clips` menu opens a small window with bundled short clips you can play.

## Available filters / effects

The project includes implementations in `filters.py`. Short descriptions:

- Normal — no effect.
- Alien Voice — cosine amplitude modulation producing an alien-y tone.
- Robotic Voice — amplitude modulation with a mild pitch shift.
- Male / Female / Baby — simple pitch shifts implemented by resampling/interpolation.
- Echoed Voice — adds delayed echo using a circular buffer.
- Ping Pong Voice — a stereo ping-pong delay effect.
- Alternate Channel Effect — alternates samples between left/right channels.
- Mutation Effect — a vibrato-like effect using a delay buffer with a sinusoidal modulation.
- Flanger Effect — classic flanger by modulating a short delay and mixing.

If you extend or tweak effects, keep their computational cost in mind for realtime processing (prefer smaller frame sizes or optimized NumPy operations).

## Development notes

- The GUI is implemented with Tkinter, and audio playback uses `pydub` + `simpleaudio` for buffering and playback.
- Realtime microphone processing uses PyAudio streams and processes frames in `BLOCKLEN` chunks (see `main.py`).
- Some DSP implementations use Python loops which may not be optimal for large inputs or strict realtime; consider vectorized NumPy or C extensions for higher performance.

Suggested improvements you might consider:

- Replace sample-wise Python loops in filters with NumPy vectorized operations where possible.
- Add unit tests for DSP functions in `filters.py` (small arrays, edge-cases like empty input, mono vs stereo shapes).
- Add a small CLI mode for batch processing files without the GUI.

## Edge cases and notes

- Empty input files: the app expects non-empty audio. Uploading an empty file may cause exceptions.
- Unsupported formats: only `.wav` and `.mp3` are handled by `on_convert` — other types will show the select dialog.
- Stereo vs mono: some effects return stereo outputs (2D arrays). The rest of the code assumes 1D int16 arrays; converting back/forth is handled in `main.py` but double-check when adding new effects.
- Realtime latency: Python + Tkinter + Python-level DSP will have noticeable latency for heavy filters. Reduce `BLOCKLEN` or optimize filters to improve responsiveness.

## Troubleshooting

- PyAudio errors opening device: ensure your audio device is available and not in use, and that `portaudio`/`PyAudio` are correctly installed.
- MP3 import errors: ensure `ffmpeg` binary is available on your PATH.
- If playback fails on Windows, try running the script from a console that has access to your audio drivers or try using different output backends.
