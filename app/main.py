"""
Main application entry point.
"""
import logging
import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="Cruxz Transcript API",
    description="API for transcribing YouTube videos, PDFs, and media files, with optional summarization.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API router
app.include_router(api_router)

# Add exception handler for any unhandled exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions."""
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logging.info("Starting Cruxz Transcript API...")
    
    # Ensure the uploads directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    logging.info(f"Environment: {settings.ENVIRONMENT}")
    logging.info(f"API is running on port {settings.PORT}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logging.info("Shutting down Cruxz Transcript API...") 