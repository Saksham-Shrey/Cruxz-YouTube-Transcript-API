"""
Router for the root path of the API.
"""
from fastapi import APIRouter, Depends

from app.core.dependencies import verify_api_key

router = APIRouter(tags=["Root"])

@router.get("/")
async def home(api_key: str = Depends(verify_api_key)):
    """
    Home endpoint providing information about the API.
    """
    return {
        "message": "Welcome to the Cruxz Transcript API Service.",
        "endpoints": {
            "/captions": {
                "description": "Fetch and parse captions for a YouTube video.",
                "parameters": {
                    "video_id": "Required. The YouTube video ID.",
                    "language": "Optional. The language code to fetch captions in a specific language.",
                    "timestamps": "Optional. Set to 'true' to include timestamps in the response.",
                    "summarize": "Optional. Set to 'true' to summarize captions using OpenAI API."
                },
                "notes": "If the 'language' parameter is not provided, the API returns available languages for the video."
            },
            "/summarize": {
                "description": "Summarize text using OpenAI's API.",
                "method": "POST",
                "parameters": {
                    "text": "Required. The text to summarize.",
                    "max_length": "Optional. Maximum length of the summary in tokens.",
                    "temperature": "Optional. Temperature for generation."
                }
            },
            "/transcribe/upload": {
                "description": "Upload a file (PDF, audio, or video) for transcription.",
                "method": "POST",
                "parameters": {
                    "file": "Required. The file to upload."
                }
            },
            "/transcribe/file": {
                "description": "Transcribe an uploaded file.",
                "method": "POST",
                "parameters": {
                    "file_path": "Required. Path to the uploaded file to transcribe.",
                    "summarize": "Optional. Whether to summarize the transcription."
                }
            },
            "/transcribe/youtube": {
                "description": "Download a YouTube video and transcribe its audio.",
                "method": "POST",
                "parameters": {
                    "video_url": "Required. YouTube video URL.",
                    "summarize": "Optional. Whether to summarize the transcription."
                }
            }
        },
        "status": "API is operational."
    } 