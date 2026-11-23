# CHANGELOG.md - Project Change Log

All finished tasks and notable updates are logged here.

## [Unreleased] - In Progress
- **T2.2 (doing)**: Edge-TTS engine with voice locking and FFmpeg audio concat/loudnorm pipeline in progress.

## [2026-11-23] - Phase 2
- **T2.1**: Implemented `pacing.py` to tokenize and parse script pacing markup (`[pause]`, `[slow]`, `[fast]`, `*emphasis*`, `[whisper]`), supporting presets (Mystery, Hype, Calm) and natural sentence pauses. Created automated test suite `tests/test_pacing.py` with 8 passing unit tests. Test passed.

## [2026-11-23] - Bug Fix
- **Fix (start.bat Windows Compatibility)**: Fixed batch file parsing errors (`... was unexpected at this time`) caused by unescaped parentheses `(venv)` inside `if` block and `&` in title. Added `cd /d "%~dp0"` to guarantee correct working directory when double-clicked from File Explorer, converted line endings to CRLF (`\r\n`), and added fallback error pause.

## [2026-11-23] - Configuration
- **Config**: Updated Gemini AI model in `config.yaml` to `gemini-3.1-flash-lite` and appended architectural decision D8 in `DECISIONS.md`.

## [2026-11-23] - Phase 1
- **T1.2**: Built complete client logic in `static/app.js`, updated `static/index.html` and `static/style.css`. Features implemented: live word count and duration estimation (~150 WPM + `[pause X]` duration), random target length generator (60-180s), debounced autosave (1.5s) to `project.json`, project sidebar list with open/duplicate/delete, and clickable interactive pacing cheatsheet inserting markup at cursor. Test passed.
- **T1.1**: Implemented project storage backend in `main.py` (CRUD endpoints `/api/projects`, duplicate, delete, and autosave update). Verified folder creation, `project.json` persistence, and input sanitization via automated test `tests/test_projects.py`. Test passed.

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
