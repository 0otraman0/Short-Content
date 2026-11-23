# DECISIONS.md - Technical Choices and Rationale
(Append only)

## D1. Architectural Pattern: Local FastAPI + Vanilla HTML/JS
- **Choice**: FastAPI backend serving static HTML/JS/CSS without any frontend build step (no React, no Node.js/npm).
- **Reason**: The user is on Windows, building via vibe coding, and needs a zero-friction setup. Running Python and serving vanilla web files ensures everything starts from a single `start.bat`.

## D2. Storage: Folder & JSON Based (No SQL Database)
- **Choice**: Store each project in `projects/<id>/` containing `project.json`, audio, subtitles, and exported files.
- **Reason**: Avoids database setup, schema migrations, and external dependencies. The user can easily back up, inspect, or delete project folders directly in Windows File Explorer.

## D3. TTS & Narration Pacing Architecture
- **Choice**: Abstract `TTSProvider` base interface with `EdgeTTSProvider` (primary, free online) and `KokoroTTSProvider` (secondary, offline fallback).
- **Reason**: `edge-tts` provides high-quality speech without cost. Splitting narration into segments by markup (`[slow]`, `[fast]`, `[pause]`, `*emphasis*`, `[whisper]`), synthesizing individually, generating precise silence intervals, and concatenating with FFmpeg `loudnorm` normalization produces dynamic pacing without complex SSML vendor lock-in. Voice is locked once in `config.yaml`.

## D4. Word-Level Captions via faster-whisper and .ass
- **Choice**: Use `faster-whisper` on narration audio to obtain word-level timestamps, then generate `.ass` (Advanced SubStation Alpha) subtitle files.
- **Reason**: `faster-whisper` runs fast locally on CPU/NVIDIA GPU. Burning `.ass` subtitles with FFmpeg allows vertical 9:16 safe area positioning, custom fonts, chunking into 2-4 words, and karaoke active-word color highlights.

## D5. Video Rendering Pipeline via FFmpeg Subprocess
- **Choice**: Direct FFmpeg commands managed through Python's `subprocess` and `pathlib.Path`. Auto-detect NVIDIA GPU (`h264_nvenc`), falling back to `libx264`.
- **Reason**: Heavy Python video libraries (like MoviePy) are often slow, memory-intensive, and prone to Windows binary issues. Direct FFmpeg CLI gives precise control over filters (crop/pad 1080x1920, audio ducking, subtitle burning, concatenation).

## D6. Gemini Client & Search Grounding
- **Choice**: Official `google-genai` Python SDK. Read API key from `.env` and model name from `config.yaml`.
- **Reason**: Compliance with latest Google AI Studio standards; keeping the model configurable avoids hardcoding models that may deprecate. Search grounding is used for fact-checking when available in the user's free tier.

## D7. Windows Compatibility & Startup
- **Choice**: Use Python `pathlib.Path` exclusively (no hardcoded `/` or `\\`), with `start.bat` automating venv creation, dependency installation, FFmpeg check via winget, and browser launch.
- **Reason**: Strict Windows 10/11 environment requirement (C1, C3).
