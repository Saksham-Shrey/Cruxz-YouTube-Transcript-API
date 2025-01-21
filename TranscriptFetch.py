from xml.etree import ElementTree as ET
import os
import logging
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import innertube
import uvicorn

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Key
API_KEY = os.getenv("API_KEY")  # Replace with your actual API key

# Middleware for API Key Validation
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """
    Middleware to validate API key before processing requests.
    """
    provided_key = request.headers.get("x-api-key")
    if provided_key != API_KEY:
        return JSONResponse(content={"error": "Unauthorized access. Invalid API key."}, status_code=403)
    return await call_next(request)

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

# Captions Endpoint
@app.get("/captions")
async def get_captions(video_id: str, language: str = None, timestamps: str = "false"):
    """
    Fetch and parse captions for a YouTube video by video ID.
    Allows users to select a specific language for captions.
    """
    timestamps = timestamps.lower() == 'true'  # Defaults to false

    try:
        # Initialize InnerTube client
        client = innertube.InnerTube("WEB")

        # Fetch video metadata
        player_data = client.player(video_id=video_id)
        video_details = player_data.get("videoDetails", {})
        video_title = video_details.get("title", "Unknown Title")

        # Extract thumbnail (safely handle missing or empty list)
        thumbnails = video_details.get("thumbnail", {}).get("thumbnails", [])
        thumbnail = thumbnails[-1]["url"] if thumbnails else "No Thumbnail Available"

        # Extract channel name and logo (safely handle missing or empty list)
        channel_name = video_details.get("author", "Unknown Channel")
        channel_thumbnails = (
            video_details.get("channelThumbnailSupportedRenderers", {})
            .get("channelThumbnailWithLinkRenderer", {})
            .get("thumbnail", {})
            .get("thumbnails", [])
        )
        channel_logo = channel_thumbnails[-1]["url"] if channel_thumbnails else "No Channel Logo Available"

        captions = player_data.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])

        if not captions:
            return JSONResponse(status_code=404, content={
                'error': 'No captions available for this video.',
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo
            })

        # If no specific language is selected, return available languages
        if not language:
            available_languages = [
                {
                    "languageCode": caption['languageCode'],
                    "name": caption['name']['simpleText']
                }
                for caption in captions
            ]
            return {
                "video_id": video_id,
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo,
                "available_languages": available_languages
            }

        # Find the caption track for the selected language
        selected_caption = next(
            (c for c in captions if c['languageCode'] == language),
            None
        )

        if not selected_caption:
            return JSONResponse(status_code=404, content={
                'error': f'No captions available for the selected language: {language}',
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo
            })

        # Fetch the raw XML captions
        response = requests.get(selected_caption['baseUrl'])
        raw_captions = response.text

        # Parse XML to plain text or JSON
        root = ET.fromstring(raw_captions)
        parsed_captions = [
            {
                "start": float(text.attrib.get("start", 0)),
                "duration": float(text.attrib.get("dur", 0)),
                "text": text.text or ""
            }
            for text in root.findall("text")
        ]

        if timestamps:
            # Return parsed captions with timestamps
            return {
                "video_id": video_id,
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo,
                "languageCode": language,
                "timestamped_captions": parsed_captions
            }
        else:
            # Concatenate captions into a single string
            concatenated_text = " ".join(
                text["text"] for text in parsed_captions if text["text"]
            )

            concatenated_text = concatenated_text.replace("&#39;", "'")
            concatenated_text = concatenated_text.replace("\n", " ")

            return {
                "video_id": video_id,
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo,
                "languageCode": language,
                "captions": concatenated_text
            }

    except Exception as e:
        logging.error(f"Error while fetching captions for video_id {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
def run_server():
    """
    Run the FastAPI server using Uvicorn.
    """
    port = int(os.getenv("PORT", 5050))
    uvicorn.run("TranscriptFetch:app", host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    run_server()