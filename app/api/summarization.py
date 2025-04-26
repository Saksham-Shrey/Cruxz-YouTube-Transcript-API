"""
Router for text summarization operations.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Body, status
from typing import Optional

from app.core.dependencies import verify_api_key
from app.services.openai_service import OpenAIService
from app.models.openai import SummarizationRequest, SummarizationResponse

router = APIRouter(prefix="/summarize", tags=["Summarization"])

# Initialize OpenAI service
openai_service = OpenAIService()

@router.post("/", response_model=SummarizationResponse)
async def summarize_text(
    request: SummarizationRequest = Body(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Summarize text using OpenAI's API.
    
    Accepts a JSON body with the text to summarize and optional parameters.
    Returns a summary and token usage information.
    """
    try:
        summary, token_usage = openai_service.summarize_text(
            request.text,
            max_length=request.max_length,
            temperature=request.temperature
        )
        
        return SummarizationResponse(
            original_length=len(request.text),
            summary=summary,
            token_usage=token_usage
        )
        
    except Exception as e:
        logging.error(f"Error summarizing text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to summarize text: {str(e)}"
        ) 