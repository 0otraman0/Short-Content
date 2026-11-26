"""
routers - Presentation Layer: FastAPI routers for all application domains.
"""
from .projects_router import router as projects_router
from .tts_router import router as tts_router
from .gemini_router import router as gemini_router
from .factcheck_router import router as factcheck_router
from .export_router import router as export_router

__all__ = [
    "projects_router",
    "tts_router",
    "gemini_router",
    "factcheck_router",
    "export_router",
]

