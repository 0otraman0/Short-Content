# Project State (2026-11-23)
- Scope: YouTube Shorts Narration Tool (Gemini script + Fact-check + Pacing TTS + SRT + sources.txt).
- Git: Branch `master`, commit `af59321` (T4.1 completed).
- Completed: Phase 0 (T0.1-T0.3), Phase 1 (T1.1-T1.2), Phase 2 (T2.1-T2.3), Phase 3 (T3.1-T3.2), Phase 4 (T4.1).
- In progress: None.
- Next task: T4.2 - Writing Assistant UI Side Panel (suggest next, rewrite, outline endpoints & UI cards).
- Active files: `gemini_client.py`, `main.py`, `static/index.html`, `static/app.js`.
- Verification: 21 tests passing across `tests/` (`test_gemini.py`, `test_export_pipeline.py`, etc.).
- Runtime: Windows, Python 3.13 venv, FastAPI on http://127.0.0.1:8000 via `start.bat`.
