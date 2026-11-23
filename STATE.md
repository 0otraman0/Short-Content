# Project State (2026-11-23)
- Scope: YouTube Shorts Narration Tool (Gemini script + Fact-check + Pacing TTS + SRT + sources.txt). Video rendering removed.
- Git: Branch `master`, commit `ae63c75` (STATE.md & reading rules updated).
- Completed: Phase 0 (T0.1-T0.3), Phase 1 (T1.1-T1.2), Phase 2 (T2.1-T2.3), Phase 3 (T3.1-T3.2).
- In progress: None.
- Next task: T4.1 - Gemini Client with `google-genai` SDK (`gemini_client.py`, model config, retry, R3.4 prompt rules).
- Active files: `gemini_client.py`, `requirements.txt`.
- Verification: 18 tests passing (`tests/test_pacing.py`, `test_tts.py`, `test_captions.py`, `test_export_pipeline.py`).
- Runtime: Windows, Python 3.13 venv, FastAPI on http://127.0.0.1:8000 via `start.bat`.
