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

## D8. Gemini AI Model Selection: Gemini 3.1 Flash Lite
- **Choice**: Set `gemini.model: "gemini-3.1-flash-lite"` in `config.yaml`.
- **Reason**: Configured per user request for rapid script generation, lower latency, and optimal resource consumption on the free tier quota. Model identifier is dynamic and resolved from `config.yaml` as per SPEC constraint.

## D9. Removal of Video Rendering & Adoption of Audio + SRT Export
- **Choice**: Removed FFmpeg video encoding pipeline (and Minecraft footage requirements). The application now focuses purely on: script writing with Gemini, fact-checking, pacing markup, and exporting `narration.mp3` (or `.wav`) + standard `subtitles.srt` (5-8 words per line) + `sources.txt` into the project folder.
- **Reason**: Requested by user to streamline the workflow and decouple video editing. Users import the exported narration audio and SRT subtitles directly into their preferred video editor (CapCut, Premiere, DaVinci, etc.). Eliminates heavy video rendering load, GPU dependencies, and Minecraft footage management.

## D10. Audition Bar Interactive State, Repeat-Click Prevention & AbortController Cancellation
- **Choice**: Added generation loading indicator to the in-editor audition bar (`#audio-preview-bar`), disabled audition buttons (`disabled = true`) during generation to prevent repeated/spam clicks, and implemented `AbortController` cancellation linked to an active `⏹ Hủy` button (`#btn-cancel-preview`) and the close button (`#btn-close-audio`).
- **Reason**: Provides immediate visual feedback of which scope (`Đoạn này` or `Toàn bài`) is generating, protects TTS endpoints against duplicate/wasted API requests, and gives users the freedom to abort in-flight TTS generation and audio playback at any moment.

## D11. Extended Pacing Tags Architecture (10 Distinct Styles)
- **Choice**: Expand pacing tags beyond the initial 5 (`[pause]`, `[slow]`, `[fast]`, `*emphasis*`, `[whisper]`) to include 5 additional expressive narration styles: `[deep]` (mysterious bass: -6Hz pitch, -8% rate, +10% volume), `[shock]` (climax revelation: +6Hz pitch, +15% rate, +15% volume), `[urgent]` (ticking clock: +22% rate, +10% volume), `[solemn]` (reflective closing: -20% rate, -3Hz pitch), and `[loud]` (wake-up warning: +30% volume, +2Hz pitch).
- **Reason**: Enhances storytelling dynamics for YouTube Shorts and science fact narrations, giving users full creative control and richer automatic AI pacing.

## D12. 3-Layer Architecture (Presentation / Services / Infrastructure+Repositories)
- **Choice**: Reorganize codebase into 3 distinct layers: (1) **Presentation** — `main.py` (bootstrap) + `routers/` (HTTP endpoints, Pydantic request/response models); (2) **Business Logic** — `services/` (project orchestration, TTS pipeline, Gemini assistant, factcheck, export); (3) **Data Access & Infrastructure** — `repositories/` (project.json CRUD) + `infrastructure/` (FFmpeg processing, TTS provider implementations, faster-whisper adapter).
- **Reason**: The original `main.py` had grown to 943 lines mixing HTTP routing, business logic, file I/O, and FFmpeg calls. 3-Layer separation improves testability, makes each concern independently modifiable, and mirrors industry-standard FastAPI project structures. Root modules (`pacing.py`, `tts.py`, `gemini_client.py`, `factcheck.py`, `captions.py`) are kept intact as facades so existing tests continue to pass with zero changes.
