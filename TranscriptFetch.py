import os
import time
import logging
import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global variables to toggle proxy usage
USE_PROXY = False  # Set to False to disable proxying entirely
USE_SCRAPERAPI = True  # Set to False to use Bright Data (if USE_PROXY is True)

# ScraperAPI settings
SCRAPERAPI_URL = "http://api.scraperapi.com"
SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY", "your_scraperapi_key_here")  # Use environment variable or default

# Bright Data proxy settings
BRIGHT_DATA_PROXY = os.getenv("BRIGHT_DATA_PROXY", "http://username:password@proxy-server:port")  # Use environment variable or default


class TranscriptResponse(BaseModel):
    video_id: str
    transcript: str


@app.get("/")
async def home():
    """Home endpoint for health checks."""
    return {"message": "Welcome to the YouTube Transcript API Service with Proxy Support!"}


@app.get("/transcript", response_model=TranscriptResponse)
async def get_transcript(video_id: str = Query(..., description="YouTube video ID to fetch transcript for")):
    """
    Fetches the transcript for a given YouTube video ID.
    """
    logging.info(f"Fetching transcript for video_id: {video_id}")

    try:
        # Add delay to avoid potential rate limiting
        time.sleep(1)

        # Use proxy configuration if enabled
        proxies = None
        if USE_PROXY:
            if USE_SCRAPERAPI:
                # ScraperAPI URL
                url = f"{SCRAPERAPI_URL}?api_key={SCRAPERAPI_KEY}&url=https://www.youtube.com/watch?v={video_id}"
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to fetch video page via ScraperAPI: {response.status_code}"
                    )
            else:
                # Bright Data Proxy
                proxies = {
                    "http": BRIGHT_DATA_PROXY,
                    "https": BRIGHT_DATA_PROXY
                }

        # Fetch transcript using youtube-transcript-api with or without proxy
        transcript_data = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=['en'],
            proxies=proxies  # Proxies for Bright Data
        )

        # Combine transcript into a single string
        transcript_text = "\n".join([entry['text'] for entry in transcript_data])
        logging.info(f"Transcript fetched successfully for video_id: {video_id}")
        return {
            "video_id": video_id,
            "transcript": transcript_text
        }

    except Exception as e:
        logging.error(f"Error fetching transcript for video_id {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/youtube_test")
async def youtube_test():
    """
    Test endpoint to verify connectivity to YouTube using proxy.
    """
    logging.info("Testing connectivity to YouTube via proxy...")
    try:
        proxies = None
        if USE_PROXY and not USE_SCRAPERAPI:
            proxies = {
                "http": BRIGHT_DATA_PROXY,
                "https": BRIGHT_DATA_PROXY
            }
        response = requests.get("https://www.youtube.com", proxies=proxies, timeout=5)
        logging.info(f"YouTube connectivity test successful: {response.status_code}")
        return {"status": "success", "code": response.status_code}
    except Exception as e:
        logging.error(f"YouTube connectivity test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 5050))
    uvicorn.run(app, host="0.0.0.0", port=port)