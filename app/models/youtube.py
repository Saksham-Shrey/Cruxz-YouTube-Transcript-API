"""
Models for YouTube transcript data.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, HttpUrl

class CaptionSegment(BaseModel):
    """
    Model for a single caption segment.
    """
    start: float = Field(..., description="Start time in seconds")
    duration: float = Field(..., description="Duration in seconds")
    text: str = Field(..., description="Caption text")

class Language(BaseModel):
    """
    Model for caption language info.
    """
    languageCode: str = Field(..., description="Language code (e.g., 'en')")
    name: str = Field(..., description="Language name (e.g., 'English')")

class CaptionsResponse(BaseModel):
    """
    Model for captions response without timestamps.
    """
    video_id: str = Field(..., description="YouTube video ID")
    video_title: str = Field(..., description="Title of the video")
    thumbnail: str = Field(..., description="URL to video thumbnail")
    channel_name: str = Field(..., description="Channel name")
    channel_logo: str = Field(..., description="URL to channel logo")
    languageCode: str = Field(..., description="Language code of captions")
    captions: str = Field(..., description="Concatenated caption text")

class TimestampedCaptionsResponse(BaseModel):
    """
    Model for captions response with timestamps.
    """
    video_id: str = Field(..., description="YouTube video ID")
    video_title: str = Field(..., description="Title of the video")
    thumbnail: str = Field(..., description="URL to video thumbnail")
    channel_name: str = Field(..., description="Channel name")
    channel_logo: str = Field(..., description="URL to channel logo")
    languageCode: str = Field(..., description="Language code of captions")
    timestamped_captions: List[CaptionSegment] = Field(..., description="List of caption segments with timestamps")

class AvailableLanguagesResponse(BaseModel):
    """
    Model for available languages response.
    """
    video_id: str = Field(..., description="YouTube video ID")
    video_title: str = Field(..., description="Title of the video")
    thumbnail: str = Field(..., description="URL to video thumbnail")
    channel_name: str = Field(..., description="Channel name")
    channel_logo: str = Field(..., description="URL to channel logo")
    available_languages: List[Language] = Field(..., description="List of available caption languages") 