# CHANGELOG.md - Project Change Log

All finished tasks and notable updates are logged here.

## [2026-11-23] - Phase 1
- **T1.1**: Implemented project storage backend in `main.py` (CRUD endpoints `/api/projects`, duplicate, delete, and autosave update). Verified folder creation, `project.json` persistence, and input sanitization via automated test `tests/test_projects.py`. Test passed.

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
