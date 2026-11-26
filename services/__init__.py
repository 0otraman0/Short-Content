"""
services - Business Logic Layer.

Domain services:
- project_service: project CRUD orchestration + word-count stats.
- tts_service: narration synthesis pipeline.
- pacing_service: pacing markup parsing and segments.
- gemini_service: AI writing assistant (suggest-next, rewrite, outline, auto-pace).
- factcheck_service: claims extraction and verification.
- export_service: end-to-end export pipeline (audio + SRT + sources).
"""

from services.pacing_service import parse_script, SpeechSegment, PauseSegment, Segment
from services.tts_service import synthesize_narration, TTSService
from services.gemini_service import GeminiService, generate_text
from services.factcheck_service import FactCheckService
from services.project_service import ProjectService
from services.export_service import ExportService

