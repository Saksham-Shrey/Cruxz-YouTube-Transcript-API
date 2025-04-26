"""
Models for OpenAI API responses and requests.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, conint, validator

class SummarizationRequest(BaseModel):
    """
    Model for text summarization request.
    """
    text: str = Field(..., description="The text to summarize")
    max_length: Optional[int] = Field(1000, description="Maximum length of the summary in tokens")
    temperature: Optional[float] = Field(0.7, description="Temperature for generation")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0 or v > 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v

class SummarizationResponse(BaseModel):
    """
    Model for text summarization response.
    """
    original_length: int = Field(..., description="Length of the original text")
    summary: str = Field(..., description="Generated summary")
    token_usage: Dict[str, int] = Field(..., description="Token usage information")

class TranscriptionResponse(BaseModel):
    """
    Model for file transcription response.
    """
    filename: str = Field(..., description="Name of the transcribed file")
    text: str = Field(..., description="Transcribed text")
    duration: Optional[float] = Field(None, description="Duration of the audio in seconds")
    token_usage: Optional[Dict[str, int]] = Field(None, description="Token usage information")
    summary: Optional[str] = Field(None, description="Summary of the transcribed text (if requested)") 