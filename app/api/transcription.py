"""
Router for file transcription operations.
"""
import os
import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from typing import Optional

from app.core.dependencies import verify_api_key, get_upload_dir
from app.core.config import settings
from app.services.file_service import FileService
from app.services.openai_service import OpenAIService
from app.models.openai import TranscriptionResponse
from app.models.files import FileType, UploadFileResponse

router = APIRouter(prefix="/transcribe", tags=["Transcription"])

# Initialize services
file_service = FileService()
openai_service = OpenAIService()

@router.post("/upload", response_model=UploadFileResponse)
async def upload_file(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Upload a file (PDF, audio, or video) for transcription.
    
    Returns information about the uploaded file.
    """
    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024 * 1024)}MB."
        )
    
    try:
        # Save the uploaded file
        file_info = await file_service.save_upload_file(file)
        
        return UploadFileResponse(
            filename=file_info["filename"],
            saved_path=file_info["saved_path"],
            file_type=file_info["file_type"],
            size=file_info["size"]
        )
        
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.post("/file", response_model=TranscriptionResponse)
async def transcribe_file(
    file_path: str = Form(..., description="Path to the uploaded file to transcribe"),
    summarize: bool = Form(False, description="Whether to summarize the transcription"),
    api_key: str = Depends(verify_api_key)
):
    """
    Transcribe an uploaded file.
    
    Supports PDF, audio, and video files.
    For PDF, extracts text directly.
    For audio, uses OpenAI's Whisper API.
    For video, extracts audio first, then transcribes it.
    
    Optionally summarizes the transcription.
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found. Please upload the file first."
            )
        
        # Determine file type
        mime_type, _ = os.path.splitext(file_path)
        mime_type = mime_type.lower()
        
        # Variable to store transcribed text
        transcribed_text = ""
        duration = None
        token_usage = None
        
        # Process based on file type
        if file_path.lower().endswith(".pdf"):
            # Extract text from PDF
            transcribed_text = file_service.extract_text_from_pdf(file_path)
        
        elif any(file_path.lower().endswith(ext) for ext in [".mp3", ".wav", ".m4a", ".flac"]):
            # Transcribe audio directly
            transcribed_text, token_usage = openai_service.transcribe_audio(file_path)
        
        elif any(file_path.lower().endswith(ext) for ext in [".mp4", ".avi", ".mov", ".mkv"]):
            # Extract audio from video, then transcribe
            audio_path = file_service.extract_audio_from_video(file_path)
            transcribed_text, token_usage = openai_service.transcribe_audio(audio_path)
        
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type. Please upload a PDF, audio, or video file."
            )
        
        # Summarize if requested
        if summarize and transcribed_text:
            summary, summary_token_usage = openai_service.summarize_text(transcribed_text)
            
            response = TranscriptionResponse(
                filename=os.path.basename(file_path),
                text=transcribed_text,
                duration=duration,
                token_usage=token_usage or summary_token_usage,
                summary=summary
            )
        else:
            response = TranscriptionResponse(
                filename=os.path.basename(file_path),
                text=transcribed_text,
                duration=duration,
                token_usage=token_usage
            )
        
        return response
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error transcribing file {file_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe file: {str(e)}"
        )

@router.post("/youtube", response_model=TranscriptionResponse)
async def transcribe_from_youtube(
    video_url: str = Form(..., description="YouTube video URL"),
    summarize: bool = Form(False, description="Whether to summarize the transcription"),
    api_key: str = Depends(verify_api_key)
):
    """
    Download a YouTube video and transcribe its audio.
    
    Optionally summarizes the transcription.
    """
    try:
        # Download the YouTube video
        video_path = await file_service.download_youtube_video(video_url)
        
        if not video_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to download the YouTube video. Please check the URL."
            )
        
        # Extract audio from the video
        audio_path = file_service.extract_audio_from_video(video_path)
        
        # Transcribe the audio
        transcribed_text, token_usage = openai_service.transcribe_audio(audio_path)
        
        # Summarize if requested
        if summarize and transcribed_text:
            summary, summary_token_usage = openai_service.summarize_text(transcribed_text)
            
            response = TranscriptionResponse(
                filename=os.path.basename(video_path),
                text=transcribed_text,
                token_usage=token_usage or summary_token_usage,
                summary=summary
            )
        else:
            response = TranscriptionResponse(
                filename=os.path.basename(video_path),
                text=transcribed_text,
                token_usage=token_usage
            )
        
        return response
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error transcribing YouTube video {video_url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe YouTube video: {str(e)}"
        ) 