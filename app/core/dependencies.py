"""
Core dependencies for the FastAPI application.
"""
from fastapi import Header, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from .config import settings

# API Key header
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Verify the API key provided in the request header.
    """
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access. Invalid API key."
        )
    return api_key

async def get_upload_dir():
    """
    Get the upload directory for file uploads.
    """
    return settings.UPLOAD_DIR 