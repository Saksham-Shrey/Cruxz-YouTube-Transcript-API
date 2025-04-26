"""
Models for file uploads and processing.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

class FileType(str, Enum):
    """
    Enum for supported file types.
    """
    PDF = "pdf"
    AUDIO = "audio"
    VIDEO = "video"

class UploadFileResponse(BaseModel):
    """
    Model for file upload response.
    """
    filename: str = Field(..., description="Original filename")
    saved_path: str = Field(..., description="Path where the file was saved")
    file_type: FileType = Field(..., description="Type of the uploaded file")
    size: int = Field(..., description="Size of the file in bytes")

class ProcessFileRequest(BaseModel):
    """
    Model for file processing request.
    """
    file_path: str = Field(..., description="Path to the file to process")
    summarize: bool = Field(False, description="Whether to summarize the transcription")
    max_summary_length: Optional[int] = Field(1000, description="Maximum length of the summary in tokens")
    temperature: Optional[float] = Field(0.7, description="Temperature for summarization")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0 or v > 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v 