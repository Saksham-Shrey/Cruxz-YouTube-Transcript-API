import os
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# Load environment variables
API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_DATA_API_KEY")

# Base URL for YouTube Data API
YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"

# FastAPI app initialization
app = FastAPI()

# Response model for captions
class CaptionsResponse(BaseModel):
    video_id: str
    captions: str


@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {"message": "Welcome to the YouTube Captions API Service!"}


@app.get("/captions", response_model=CaptionsResponse)
async def get_captions(video_id: str = Query(..., description="YouTube video ID to fetch captions for")):
    """
    Fetch combined captions as a single string for a given YouTube video ID.
    Gives preference to all English variants (e.g., en, en-GB, en-US).
    """
    try:
        # Step 1: Retrieve the caption tracks for the video
        captions_url = f"{YOUTUBE_API_BASE_URL}/captions"
        params = {
            "videoId": video_id,
            "part": "snippet",
            "key": API_KEY,
        }
        response = requests.get(captions_url, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error retrieving captions: {response.text}")

        captions_data = response.json()
        if "items" not in captions_data or not captions_data["items"]:
            raise HTTPException(status_code=404, detail="No captions available for this video.")

        # Step 2: Find an English caption track (any variant of English)
        caption_tracks = captions_data["items"]
        english_caption = next(
            (
                track
                for track in caption_tracks
                if track["snippet"]["language"].startswith("en")  # Match all "en" variants
            ),
            None,
        )

        if not english_caption:
            raise HTTPException(status_code=404, detail="No English captions available for this video.")

        # Step 3: Download the caption
        caption_id = english_caption["id"]
        download_url = f"{YOUTUBE_API_BASE_URL}/captions/{caption_id}"
        download_params = {
            "tfmt": "srt",  # Use 'srt' for subtitle format
            "key": API_KEY,
        }
        download_response = requests.get(download_url, params=download_params)

        if download_response.status_code != 200:
            raise HTTPException(
                status_code=download_response.status_code,
                detail=f"Error downloading caption: {download_response.text}",
            )

        # Parse and combine the captions into a single string
        srt_captions = download_response.text
        combined_captions = "\n".join(
            line.strip()
            for line in srt_captions.splitlines()
            if not line.isdigit() and "-->" not in line  # Skip line numbers and timestamps
        )

        # Return as JSON
        return {"video_id": video_id, "captions": combined_captions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")