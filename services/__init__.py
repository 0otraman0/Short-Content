"""
services - Business Logic Layer.

Domain services:
- project_service: project CRUD orchestration + word-count stats.
- tts_service: narration synthesis pipeline.
- pacing_service: re-exports pacing parse_script for service consumers.
- gemini_service: AI writing assistant (suggest-next, rewrite, outline, auto-pace).
- factcheck_service: claims extraction and verification.
- export_service: end-to-end export pipeline (audio + SRT + sources).
"""
