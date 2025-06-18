import os
import logging
import json
import re
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.proxies import WebshareProxyConfig
from pytube import YouTube
import uvicorn
from dotenv import load_dotenv
import requests
from requests import Session


# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Keys and Proxy Configuration
API_KEY = os.getenv("API_KEY")  # API key for our service
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # YouTube Data API key (optional)
PROXY_USERNAME = os.getenv("PROXY_USERNAME")  # Webshare proxy username
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")  # Webshare proxy password
PROXY_HOST = os.getenv("PROXY_HOST", "p.webshare.io")  # Default Webshare proxy host
PROXY_PORT = os.getenv("PROXY_PORT", "80")  # Default Webshare proxy port



# Home Endpoint
@app.get("/")
async def home():
    """
    Home endpoint for testing and basic information.
    """
    return {
        "message": "Welcome to the YouTube Caption API Service.",
        "endpoints": {
            "/captions": {
                "description": "Fetch and parse captions for a YouTube video.",
                "parameters": {
                    "video_id": "Required. The YouTube video ID.",
                    "language": "Optional. The language code to fetch captions in a specific language.",
                    "timestamps": "Optional. Set to 'true' to include timestamps in the response."
                },
                "notes": "If the 'language' parameter is not provided, the API returns available languages for the video."
            }
        },
        "status": "API is operational."
    }
import os
import re
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

app = FastAPI()

# Logging config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Config from environment
API_KEY = os.getenv("API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
PROXY_HOST = os.getenv("PROXY_HOST", "p.webshare.io")
PROXY_PORT = os.getenv("PROXY_PORT", "80")

proxies = {
    "http": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}",
    "https": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
}

# Middleware to validate API key
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    provided_key = request.headers.get("x-api-key")
    if provided_key != API_KEY:
        return JSONResponse(content={"error": "Unauthorized access. Invalid API key."}, status_code=403)
    return await call_next(request)

# Helper: fetch URL using proxy
def fetch_with_proxy(url):
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        response.raise_for_status()
        return response
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

# Get basic video metadata using oEmbed
def get_video_metadata(video_id):
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    response = fetch_with_proxy(oembed_url)
    if response:
        data = response.json()
        return {
            "video_title": data.get("title", "Unknown Title"),
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            "channel_name": data.get("author_name", "Unknown Channel"),
            "channel_logo": f"https://www.youtube.com/{data.get('author_url', '').split('/')[-1]}" if data.get("author_url") else "Unknown"
        }
    return {
        "video_title": "Unknown Title",
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        "channel_name": "Unknown Channel",
        "channel_logo": "Unknown"
    }

@app.get("/")
async def home():
    return {
        "message": "YouTube Caption API",
        "status": "OK",
        "usage": "/captions?video_id=<ID>&language=<code>&timestamps=true"
    }

@app.get("/captions")
async def get_captions(video_id: str, language: str = None, timestamps: str = "false"):
    timestamps = timestamps.lower() == 'true'
    metadata = get_video_metadata(video_id)

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)
    except (TranscriptsDisabled, NoTranscriptFound):
        return JSONResponse(status_code=404, content={"error": "No captions available", **metadata})
    except Exception as e:
        logging.error(f"Transcript API failure: {e}")
        raise HTTPException(status_code=500, detail="Transcript retrieval failed")

    if not language:
        available = [
            {"languageCode": t.language_code, "name": t.language}
            for t in transcript_list
        ]
        return {
            "video_id": video_id,
            **metadata,
            "available_languages": available
        }

    try:
        transcript = transcript_list.find_transcript([language])
    except NoTranscriptFound:
        try:
            transcript = transcript_list.find_transcript(["en", "es", "fr"]).translate(language)
        except Exception:
            return JSONResponse(status_code=404, content={
                "error": f"No captions found for language '{language}'",
                **metadata
            })

    try:
        data = transcript.fetch()
    except Exception as e:
        logging.error(f"Error fetching transcript: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch captions")

    if timestamps:
        return {
            "video_id": video_id,
            **metadata,
            "captions": [
                {"start": seg["start"], "duration": seg["duration"], "text": seg["text"]}
                for seg in data
            ]
        }
    else:
        full_text = " ".join(seg["text"] for seg in data if seg["text"])
        return {
            "video_id": video_id,
            **metadata,
            "captions": full_text
        }

@app.get("/proxyCheck")
async def proxy_check():
    try:
        response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=10)
        return response.json()
    except Exception as e:
        logging.error(f"Proxy check failed: {e}")
        raise HTTPException(status_code=500, detail="Proxy check failed")

        
# Run the server
def run_server():
    """
    Run the FastAPI server using Uvicorn.
    """
    port = int(os.getenv("PORT", 5050))
    uvicorn.run("TranscriptFetch:app", host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    run_server() 