---
name: music-analysis
description: "Analyze music/audio files locally without external APIs. Extract tempo (BPM), key estimate, section boundaries, loudness dynamics, spectral/timbre descriptors, and temporal mood journeys. Use when asked to 'hear the music,' audit tracks, compare mixes, inspect structure, or generate producer-facing notes from audio files."
metadata:
  openclaw:
    requires:
      bins: [ffprobe, ffmpeg]
      python: ">=3.10"
    install:
      - id: venv
        kind: script
        label: "Install Python deps (librosa, numpy)"
        run: |
          cd skills/music-analysis
          python3 -m venv .venv
          .venv/bin/pip install librosa numpy
---

# Music Analysis (Local, No External APIs)

Analyze audio files using signal processing. Two tools:

## 1. Quick Analysis — snapshot of the whole track

```bash
python3 skills/music-analysis/scripts/analyze_music.py /path/to/audio.mp3
python3 skills/music-analysis/scripts/analyze_music.py track.mp3 --json
```

**Reports:** duration, sample rate, tempo (BPM), key estimate, energy stats (RMS mean/std/p95), spectral summary (centroid, rolloff, contrast), coarse section boundaries.

## 2. Temporal Listen — experience the track as a journey

```bash
python3 skills/music-analysis/scripts/temporal_listen.py /path/to/audio.mp3
python3 skills/music-analysis/scripts/temporal_listen.py track.mp3 --json
```

**Reports:** sliding-window analysis (4s windows, 2s hops) producing a full timeline of:
- Energy level (relative to track average)
- Mood labels (simmering, soaring, erupting, full force, submerged, ethereal, etc.)
- Transitions (drop hits, pulls back, shifts color, evolves)
- Texture decomposition (harmonic/percussive ratio, onset density, roughness)
- Tension model (sustained intensity tracking)
- Narrative arc (mountain, ascending, descending, plateau, wave)
- Peak moment, quietest moment, mood journey summary

### How it works

No AI/ML models — pure signal processing via librosa:
- **RMS energy** per window (relative to global average)
- **Spectral centroid** (brightness), rolloff, flatness
- **Harmonic/percussive source separation** (HPSS)
- **Onset detection** (rhythmic activity density)
- **Zero-crossing rate** (texture roughness)
- Mood labels are rule-based mappings from these features

### Mood vocabulary

| Mood | Condition |
|------|-----------|
| submerged | Low energy, dark frequencies |
| ethereal | Low energy, high harmonic ratio |
| breathing | Low energy, other |
| simmering | Mid-low energy, warm |
| restless | Mid-low energy, high onset density |
| floating | Mid-low energy, bright |
| driving | Mid energy, percussive |
| soaring | Mid energy, harmonic |
| locked in | Mid energy, balanced |
| erupting | High energy, high onset density |
| searing | High energy, very bright |
| pounding | High energy, percussive |
| full force | High energy, sustained |

## Audio sourcing

The tool needs a real audio file on disk. Source options:
- Direct file (mp3, wav, flac, ogg, m4a — anything ffmpeg/librosa can read)
- YouTube: `yt-dlp -x --audio-format mp3 -o "output.mp3" "URL_OR_SEARCH"`
- Spotify downloads, SoundCloud, Bandcamp, etc. via yt-dlp

## Optional: Whisper transcription

For lyrics/speech transcription, auto-detect which Whisper CLI is available:

```bash
# Detection priority: whisper-cli (C++ port) > whisper (Python)
# If neither is found, skip transcription gracefully — it's optional.

# 1. Check for whisper-cpp (faster on Apple Silicon):
if command -v whisper-cli &>/dev/null; then
  # Requires WAV input — convert first
  ffmpeg -i track.mp3 -ar 16000 -ac 1 /tmp/track.wav
  whisper-cli -m ~/.local/share/whisper-cpp/ggml-medium.bin -f /tmp/track.wav --output-json

# 2. Fallback to Python whisper (accepts mp3/wav/flac directly):
elif command -v whisper &>/dev/null; then
  whisper track.mp3 --model small --output_format json --output_dir /tmp

# 3. Neither installed — skip, don't fail
else
  echo "No Whisper CLI found. Skipping transcription. Install: brew install whisper-cpp OR pip install openai-whisper"
fi
```

### Install options
- **whisper-cpp** (recommended for Apple Silicon): `brew install whisper-cpp`, then download a model from https://huggingface.co/ggerganov/whisper.cpp/tree/main
- **OpenAI whisper** (Python): `pip install openai-whisper`

## Dependencies

```
librosa
numpy
```

System: `ffmpeg`, `ffprobe` (for audio decoding)

## Sandbox rules

- Keep experiments in `skills/music-analysis/` only
- Audio files go in `skills/music-analysis/tmp/` (gitignored)
- Do not modify trading scripts, gateway config, or global runtime
