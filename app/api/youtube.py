"""
Router for YouTube caption operations.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional

from app.core.dependencies import verify_api_key
from app.services.youtube_service import YouTubeService
from app.services.openai_service import OpenAIService

router = APIRouter(prefix="/captions", tags=["YouTube Captions"])

# Initialize services
youtube_service = YouTubeService()
openai_service = OpenAIService()

@router.get("/")
async def get_captions(
    video_id: str = Query(..., description="YouTube video ID"),
    language: Optional[str] = Query(None, description="Language code for captions (e.g., 'en')"),
    timestamps: bool = Query(False, description="Include timestamps in the response"),
    summarize: bool = Query(False, description="Summarize the captions using OpenAI API"),
    max_length: int = Query(1000, description="Maximum length of summary (only used if summarize=true)"),
    temperature: float = Query(0.7, description="Temperature for summarization (only used if summarize=true)"),
    api_key: str = Depends(verify_api_key)
):
    """
    Fetch and process captions for a YouTube video by video ID.
    Optional parameters allow language selection, timestamp inclusion, and summarization.
    """
    try:
        # Get video details
        video_details = youtube_service.get_video_details(video_id)
        captions_data = video_details.get("captions_data", [])
        
        # Check if captions exist
        if not captions_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No captions available for this video."
            )
        
        # If no specific language is selected, return available languages
        if not language:
            available_languages = youtube_service.get_available_languages(captions_data)
            return {
                "video_id": video_id,
                "video_title": video_details.get("video_title"),
                "thumbnail": video_details.get("thumbnail"),
                "channel_name": video_details.get("channel_name"),
                "channel_logo": video_details.get("channel_logo"),
                "available_languages": available_languages
            }
        
        # Find the caption track for the selected language
        selected_caption = youtube_service.get_caption_track(captions_data, language)
        
        if not selected_caption:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No captions available for the selected language: {language}"
            )
        
        # Fetch and parse the captions
        parsed_captions = youtube_service.fetch_and_parse_captions(
            selected_caption['baseUrl'], 
            with_timestamps=timestamps
        )
        
        response = {
            "video_id": video_id,
            "video_title": video_details.get("video_title"),
            "thumbnail": video_details.get("thumbnail"),
            "channel_name": video_details.get("channel_name"),
            "channel_logo": video_details.get("channel_logo"),
            "languageCode": language,
        }
        
        # Format captions in response based on timestamps
        if timestamps:
            response["timestamped_captions"] = parsed_captions
        else:
            response["captions"] = parsed_captions
        
        # Summarize if requested
        if summarize and not timestamps:
            summary, token_usage = openai_service.summarize_text(
                parsed_captions, 
                max_length=max_length, 
                temperature=temperature
            )
            response["summary"] = summary
            response["token_usage"] = token_usage
        
        return response
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error processing captions for video_id {video_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 