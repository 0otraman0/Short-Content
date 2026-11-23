# CHANGELOG.md - Project Change Log

All finished tasks and notable updates are logged here.

## [2026-11-23] - Phase 0
- **T0.1**: Initialized `.gitignore`, `.env.example` (Gemini API key placeholder), and `config.yaml` (TTS voice defaults, pacing presets, Gemini model, video dimensions). Test passed.

## [2026-11-23] - Planning Phase
- **Planner**: Read `AGENTS.md` and `SPEC.md`.
- Created `DECISIONS.md` documenting technical decisions D1-D7 (FastAPI, Vanilla JS, JSON project storage, edge-tts + Kokoro fallback, faster-whisper + ASS captions, FFmpeg NVENC/CPU render, official google-genai SDK).
- Created `PLAN.md` breaking requirements into 8 phases (Phase 0 to Phase 7) and 20 discrete tasks with strict file ownership and testing guidelines.
