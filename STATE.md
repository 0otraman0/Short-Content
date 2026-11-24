# Project State (2026-11-24)
- Scope: YouTube Shorts Narration Tool (Gemini script + Fact-check + Pacing TTS + SRT + sources.txt).
- Git: Branch `master`, commit `0aa7b7f` (T5.2 completed).
- Completed: Phase 0 (T0.1-T0.3), Phase 1 (T1.1-T1.2), Phase 2 (T2.1-T2.3), Phase 3 (T3.1-T3.2), Phase 4 (T4.1-T4.3), Phase 5 (T5.1, T5.2).
- In progress: None.
- Next task: T5.3 - Pre-Export Safety Check & `sources.txt` Export (safety warning on unverified claims).
- Active files: `main.py`, `static/app.js`.
- Verification: 29 tests passing across `tests/` (`test_factcheck_api.py`, `test_gemini_api.py`, etc.).
- Runtime: Windows, Python 3.13 venv, FastAPI on http://127.0.0.1:8000 via `start.bat`.
