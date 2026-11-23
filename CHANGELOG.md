# CHANGELOG.md - Project Change Log

All finished tasks and notable updates are logged here.

## [2026-11-23] - Phase 3
- **T3.2**: Replaced video rendering with export pipeline in `main.py` and web UI. Implemented `POST /api/projects/{id}/export`, polling `GET /export-status/{job_id}`, and download endpoints (`/narration`, `/subtitles`, `/sources`). UI updated with "Xuất Audio & Phụ đề" button, export progress tracking modal, and direct download cards for `narration.mp3`, `subtitles.srt`, and `sources.txt`. Removed legacy `render.py` and video tests. Created and passed integration test `tests/test_export_pipeline.py`. Test passed.
- **T3.1**: Updated `captions.py` to generate standard `.srt` subtitle files with full natural phrases (5-8 words per line) and precision millisecond timestamps (`HH:MM:SS,mmm --> HH:MM:SS,mmm`). Updated test suite `tests/test_captions.py` with 4/4 passing unit tests. Test passed.

## [2026-11-23] - Change Request: Scope Streamlined to Audio + SRT + Sources
- **Scope Change**: Approved change request to remove video rendering, GPU encoding dependencies, and Minecraft footage handling. The tool now focuses on: Gemini script writing, Fact-checking, Pacing markup, and exporting `narration.mp3` (or `.wav`) + standard `subtitles.srt` (5-8 words per line) + `sources.txt` into the project folder.
- Updated `SPEC.md`, `DECISIONS.md` (Decision D9), `config.yaml`, and restructured `PLAN.md` into 6 streamlined phases.

## [2026-11-23] - Bug Fix
- **Fix (PyAV av.open compatibility)**: Resolved `TypeError: open() got an unexpected keyword argument 'metadata_errors'` when transcribing audio with `faster-whisper` in environments running newer PyAV (`av >= 14`, specifically `av 19.0.2` in `venv`). Added backwards-compatible monkey-patch for `av.open` in `captions.py` and unit test in `tests/test_av_compat.py`.

## [2026-11-23] - Phase 3
- **T3.3**: Built background rendering pipeline in `main.py` (`POST /api/projects/{id}/render`, `GET /render-status/{job_id}`, `GET /video`), modal progress tracking (TTS -> Whisper -> FFmpeg), duration warning check (<60s / >180s), and embedded video player with MP4 download button in `static/index.html` & `static/app.js`. Full end-to-end integration verified via automated test `tests/test_render_pipeline.py`. Test passed.
- **T3.2**: Implemented core FFmpeg video rendering engine in `render.py`. Features: auto-detection of hardware encoder (`h264_nvenc` vs `libx264`), 1080x1920 30fps vertical video composition with dark placeholder background, Windows filter path escaping, .ass subtitle burning, AAC audio muxing, and YouTube Shorts MP4 export (`+faststart`). Added unit test suite `tests/test_render.py` passing 3/3 tests. Test passed.
- **T3.1**: Implemented word-level transcription and ASS subtitle generation in `captions.py` using `faster-whisper`. Configured 1080x1920 vertical video safe-area styling (Arial Black 72pt, black outline, bottom-margin 860), 2-4 word chunking, and dynamic active-word color highlights (`{\c&H0000FFFF&}`). Created unit test suite `tests/test_captions.py` passing 5/5 tests. Test passed.

## [2026-11-23] - Phase 2
- **T2.3**: Integrated TTS preview and voice selection: added `/api/tts/preview`, `/api/tts/voices`, and `/api/tts/lock-voice` in `main.py`. Updated `static/index.html` and `static/app.js` with functional "Nghe thử" button for highlighted text/paragraph with in-browser audio playback, pacing preset selector, and a voice selection modal to pick and permanently lock English male voices into `config.yaml`. Handled edge cases with punctuation-only segments. Automated test `tests/test_tts_preview.py` passed. Test passed.
- **T2.2**: Implemented TTS Engine in `tts.py` with `TTSProvider` interface and `EdgeTTSProvider`. Added voice locking to `config.yaml`, segment audio synthesis with pacing modifiers, FFmpeg silence generation via `anullsrc`, concat demuxer, and EBU R128 loudness normalization (`loudnorm`). Added automated test suite `tests/test_tts.py` verifying voice listing, silence generation, and full narration audio synthesis. Test passed.
- **T2.1**: Implemented `pacing.py` to tokenize and parse script pacing markup (`[pause]`, `[slow]`, `[fast]`, `*emphasis*`, `[whisper]`), supporting presets (Mystery, Hype, Calm) and natural sentence pauses. Created automated test suite `tests/test_pacing.py` with 8 passing unit tests. Test passed.

## [2026-11-23] - Bug Fix
- **Fix (start.bat Windows Compatibility)**: Fixed batch file parsing errors (`... was unexpected at this time`) caused by unescaped parentheses `(venv)` inside `if` block and `&` in title. Added `cd /d "%~dp0"` to guarantee correct working directory when double-clicked from File Explorer, converted line endings to CRLF (`\r\n`), and added fallback error pause.

## [2026-11-23] - Configuration
- **Config**: Updated Gemini AI model in `config.yaml` to `gemini-3.1-flash-lite` and appended architectural decision D8 in `DECISIONS.md`.

## [2026-11-23] - Phase 1
- **T1.2**: Built complete client logic in `static/app.js`, updated `static/index.html` and `static/style.css`. Features implemented: live word count and duration estimation (~150 WPM + `[pause X]` duration), random target length generator (60-180s), debounced autosave (1.5s) to `project.json`, project sidebar list with open/duplicate/delete, and clickable interactive pacing cheatsheet inserting markup at cursor. Test passed.
- **T1.1**: Implemented project storage backend in `main.py` (CRUD endpoints `/api/projects`, duplicate, delete, and autosave update). Verified folder creation, `project.json` persistence, and input sanitization via automated test `tests/test_projects.py`. Test passed.

## [2026-11-23] - Bug Fix
- **Fix (PyAV av.open compatibility)**: Resolved `TypeError: open() got an unexpected keyword argument 'metadata_errors'` when transcribing audio with `faster-whisper` in environments running newer PyAV (`av >= 14`, specifically `av 19.0.2` in `venv`). Added backwards-compatible monkey-patch for `av.open` in `captions.py` and unit test in `tests/test_av_compat.py`.

## [2026-11-23] - Phase 3
- **T3.3**: Built background rendering pipeline in `main.py` (`POST /api/projects/{id}/render`, `GET /render-status/{job_id}`, `GET /video`), modal progress tracking (TTS -> Whisper -> FFmpeg), duration warning check (<60s / >180s), and embedded video player with MP4 download button in `static/index.html` & `static/app.js`. Full end-to-end integration verified via automated test `tests/test_render_pipeline.py`. Test passed.
- **T3.2**: Implemented core FFmpeg video rendering engine in `render.py`. Features: auto-detection of hardware encoder (`h264_nvenc` vs `libx264`), 1080x1920 30fps vertical video composition with dark placeholder background, Windows filter path escaping, .ass subtitle burning, AAC audio muxing, and YouTube Shorts MP4 export (`+faststart`). Added unit test suite `tests/test_render.py` passing 3/3 tests. Test passed.
- **T3.1**: Implemented word-level transcription and ASS subtitle generation in `captions.py` using `faster-whisper`. Configured 1080x1920 vertical video safe-area styling (Arial Black 72pt, black outline, bottom-margin 860), 2-4 word chunking, and dynamic active-word color highlights (`{\c&H0000FFFF&}`). Created unit test suite `tests/test_captions.py` passing 5/5 tests. Test passed.

## [2026-11-23] - Phase 2
- **T2.1**: Implemented `pacing.py` to tokenize and parse script pacing markup (`[pause]`, `[slow]`, `[fast]`, `*emphasis*`, `[whisper]`), supporting presets (Mystery, Hype, Calm) and natural sentence pauses. Created automated test suite `tests/test_pacing.py` with 8 passing unit tests. Test passed.

## [2026-11-23] - Bug Fix
- **Fix (FFmpeg Path Detection)**: Added automatic discovery of WinGet-installed FFmpeg (`Gyan.FFmpeg`) in `main.py` (`ensure_ffmpeg()`) and `start.bat`. This resolves the issue where newly installed FFmpeg from winget was not immediately recognized in existing command/PowerShell sessions before terminal restart. Added `tests/test_ffmpeg.py` reproducer/test.

## [2026-11-23] - Phase 0
- **T0.3**: Created Windows launcher `start.bat` (automated venv setup, dependency installation, FFmpeg winget detection, directory initialization, browser auto-launch) and comprehensive Vietnamese `README.md` guide. Test passed.
- **T0.2**: Implemented FastAPI backend in `main.py` and single-page dark UI shell (`static/index.html`, `static/style.css`). Added `/api/status` endpoint with NVIDIA GPU detection (`h264_nvenc`), FFmpeg availability check, and assets status. Created `requirements.txt`. Test passed.
- **T0.1**: Initialized `.gitignore`, `.env.example` (Gemini API key placeholder), and `config.yaml` (TTS voice defaults, pacing presets, Gemini model, video dimensions). Test passed.

## [2026-11-23] - Planning Phase
- **Planner**: Read `AGENTS.md` and `SPEC.md`.
- Created `DECISIONS.md` documenting technical decisions D1-D7 (FastAPI, Vanilla JS, JSON project storage, edge-tts + Kokoro fallback, faster-whisper + ASS captions, FFmpeg NVENC/CPU render, official google-genai SDK).
- Created `PLAN.md` breaking requirements into 8 phases (Phase 0 to Phase 7) and 20 discrete tasks with strict file ownership and testing guidelines.
