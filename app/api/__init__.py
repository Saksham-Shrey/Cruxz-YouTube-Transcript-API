"""
API router package initialization.
"""
from fastapi import APIRouter
from .root import router as root_router
from .youtube import router as youtube_router
from .summarization import router as summarization_router
from .transcription import router as transcription_router

# Create the main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(root_router)
api_router.include_router(youtube_router)
api_router.include_router(summarization_router)
api_router.include_router(transcription_router) 