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

# Helper function to get video metadata using oEmbed as fallback
def get_video_metadata_oembed(video_id):
    """
    Fetch video metadata using YouTube's oEmbed API.
    """
    try:
        logging.info(f"Fetching metadata via oEmbed for video ID: {video_id}")
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url)
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Successfully retrieved oEmbed data for {video_id}")
            
            # Extract the available metadata
            video_title = data.get('title', 'Unknown Title')
            channel_name = data.get('author_name', 'Unknown Channel')
            channel_url = data.get('author_url', '')
            
            # YouTube thumbnail URL formats
            thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            # Channel logo isn't available in oEmbed, use a fallback
            channel_logo = f"https://www.youtube.com/channel/{channel_url.split('/')[-1]}/about" if channel_url else "No Channel Logo Available"
            
            return {
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo
            }
        else:
            logging.error(f"oEmbed API returned status code {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error fetching video metadata via oEmbed: {str(e)}")
        return None

# Helper function to get video metadata using YouTube Data API
def get_video_metadata_api(video_id):
    """
    Fetch video metadata using YouTube Data API v3.
    Requires YOUTUBE_API_KEY environment variable to be set.
    """
    if not YOUTUBE_API_KEY:
        logging.info("YouTube API key not found in environment variables")
        return None
        
    try:
        logging.info(f"Fetching metadata via YouTube Data API for video ID: {video_id}")
        api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={YOUTUBE_API_KEY}&part=snippet,contentDetails,statistics"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Successfully retrieved YouTube API data for {video_id}")
            
            if not data.get('items'):
                logging.error(f"No items found in YouTube API response for {video_id}")
                return None
                
            # Extract the metadata from the first item
            snippet = data['items'][0]['snippet']
            
            video_title = snippet.get('title', 'Unknown Title')
            channel_name = snippet.get('channelTitle', 'Unknown Channel')
            channel_id = snippet.get('channelId', '')
            
            # Get the highest resolution thumbnail available
            thumbnails = snippet.get('thumbnails', {})
            thumbnail_url = thumbnails.get('maxres', {}).get('url') or \
                            thumbnails.get('high', {}).get('url') or \
                            thumbnails.get('medium', {}).get('url') or \
                            thumbnails.get('default', {}).get('url') or \
                            f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            return {
                "video_title": video_title,
                "thumbnail": thumbnail_url,
                "channel_name": channel_name,
                "channel_logo": f"https://www.youtube.com/channel/{channel_id}/about" if channel_id else "No Channel Logo Available"
            }
        else:
            logging.error(f"YouTube API returned status code {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error fetching video metadata via YouTube API: {str(e)}")
        return None

# Helper function to get video title from YouTube page
def get_video_title_from_page(video_id):
    """
    Extract video title directly from the YouTube video page HTML.
    This is a more reliable method when pytube or API methods fail.
    """
    try:
        logging.info(f"Fetching title from YouTube page for video ID: {video_id}")
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Extract title using regex
            title_match = re.search(r'<title>(.*?) - YouTube</title>', response.text)
            if title_match:
                title = title_match.group(1)
                logging.info(f"Successfully extracted title from page: {title}")
                return title
            else:
                logging.error("Could not find title pattern in YouTube page")
        else:
            logging.error(f"YouTube page request returned status code {response.status_code}")
        
        return "Unknown Title"
    except Exception as e:
        logging.error(f"Error fetching title from YouTube page: {str(e)}")
        return "Unknown Title"

# Helper function to get video metadata
def get_video_metadata(video_id):
    """
    Fetch video metadata using multiple methods with fallbacks.
    1. YouTube Data API (if API key is available)
    2. pytube
    3. YouTube oEmbed API
    4. Direct page scraping for title
    5. Fallback to default values with thumbnail URL
    """
    result = {
        "video_title": "Unknown Title",
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        "channel_name": "Unknown Channel",
        "channel_logo": "No Channel Logo Available"
    }
    
    # First try YouTube Data API if key is available
    if YOUTUBE_API_KEY:
        api_data = get_video_metadata_api(video_id)
        if api_data:
            logging.info(f"Successfully retrieved metadata via YouTube Data API for {video_id}")
            return api_data
    
    # Then try pytube
    try:
        logging.info(f"Fetching metadata for video ID: {video_id}")
        # Create a YouTube object
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        
        logging.info(f"Video object created successfully for {video_id}")
        
        # Get video details with extensive error handling
        try:
            video_title = yt.title
            logging.info(f"Retrieved title: {video_title}")
            result["video_title"] = video_title
        except Exception as e:
            logging.error(f"Error getting video title: {e}")
        
        try:
            thumbnail = yt.thumbnail_url
            logging.info(f"Retrieved thumbnail URL: {thumbnail}")
            if thumbnail:
                result["thumbnail"] = thumbnail
        except Exception as e:
            logging.error(f"Error getting thumbnail: {e}")
        
        try:
            channel_name = yt.author
            logging.info(f"Retrieved channel name: {channel_name}")
            if channel_name:
                result["channel_name"] = channel_name
        except Exception as e:
            logging.error(f"Error getting channel name: {e}")
        
        try:
            channel_id = yt.channel_id
            channel_logo = f"https://www.youtube.com/channel/{channel_id}/about"
            logging.info(f"Retrieved channel ID: {channel_id}")
            if channel_id:
                result["channel_logo"] = channel_logo
        except Exception as e:
            logging.error(f"Error getting channel ID: {e}")
        
        # Validate the results, if title was retrieved, return what we have
        if result["video_title"] != "Unknown Title":
            return result
            
    except Exception as e:
        logging.error(f"Error fetching video metadata via pytube: {str(e)}")
    
    # Next, try the oEmbed API as fallback
    oembed_data = get_video_metadata_oembed(video_id)
    if oembed_data:
        logging.info(f"Successfully fell back to oEmbed for video {video_id}")
        return oembed_data
    
    # If we still don't have a title, try direct page scraping for the title
    if result["video_title"] == "Unknown Title":
        title = get_video_title_from_page(video_id)
        if title != "Unknown Title":
            result["video_title"] = title
            
    return result

# Captions Endpoint
@app.get("/captions")
async def get_captions(video_id: str, language: str = None, timestamps: str = "false"):
    """
    Fetch and parse captions for a YouTube video by video ID.
    Allows users to select a specific language for captions.
    """
    timestamps = timestamps.lower() == 'true'  # Defaults to false

    proxies = {
         "http": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}",
        "https": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
    }

    try:
        # Get video metadata
        metadata = get_video_metadata(video_id)
        video_title = metadata["video_title"]
        thumbnail = metadata["thumbnail"]
        channel_name = metadata["channel_name"]
        channel_logo = metadata["channel_logo"]

        # Initialize Youtube Transcript API with proxy if available
        ytt_api = YouTubeTranscriptApi()

        # Get available transcripts
        try:
            transcript_list = ytt_api.list_transcripts(video_id, proxies=proxies)
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            return JSONResponse(status_code=404, content={
                'error': 'No captions available for this video.',
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo
            })

        # If no specific language is selected, return available languages
        if not language:
            available_languages = []
            
            # Manual transcripts
            for transcript in transcript_list._manually_created_transcripts.values():
                available_languages.append({
                    "languageCode": transcript.language_code,
                    "name": transcript.language
                })
            
            # Generated transcripts
            for transcript in transcript_list._generated_transcripts.values():
                available_languages.append({
                    "languageCode": transcript.language_code,
                    "name": f"{transcript.language} (auto-generated)"
                })
            
            return {
                "video_id": video_id,
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo,
                "available_languages": available_languages
            }

        # Try to get transcript in the requested language
        try:
            # Try to find the exact language match first
            transcript = transcript_list.find_transcript([language])
            
            # Get the language name for the response
            language_name = transcript.language
            
            # Safely check if _is_generated attribute exists
            is_generated = hasattr(transcript, '_is_generated') and transcript._is_generated
            if is_generated:
                language_name += " (auto-generated)"
                
        except NoTranscriptFound:
            # Try to get a transcript translated to the requested language
            try:
                # Get any available transcript and translate it
                transcript = transcript_list.find_transcript(["en", "es", "fr", "de"])  # Try common languages
                transcript = transcript.translate(language)
                language_name = transcript.language + " (translated)"
            except Exception:
                return JSONResponse(status_code=404, content={
                    'error': f'No captions available for the selected language: {language}',
                    "video_title": video_title,
                    "thumbnail": thumbnail,
                    "channel_name": channel_name,
                    "channel_logo": channel_logo
                })

        # Fetch the transcript data
        transcript_data = transcript.fetch()

        if timestamps:
            # Return parsed captions with timestamps
            # Convert transcript data to a list of dictionaries
            formatted_transcript = [
                {
                    "start": segment.start,
                    "duration": segment.duration,
                    "text": segment.text
                }
                for segment in transcript_data
            ]
            
            return {
                "video_id": video_id,
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo,
                "languageCode": language,
                "languageName": language_name,
                "timestamped_captions": formatted_transcript
            }
        else:
            # Concatenate captions into a single string
            concatenated_text = " ".join(
                segment.text for segment in transcript_data if segment.text
            )

            # Clean up the text
            concatenated_text = concatenated_text.replace("\n", " ")

            return {
                "video_id": video_id,
                "video_title": video_title,
                "thumbnail": thumbnail,
                "channel_name": channel_name,
                "channel_logo": channel_logo,
                "languageCode": language,
                "languageName": language_name,
                "captions": concatenated_text
            }

    except Exception as e:
        logging.error(f"Error while fetching captions for video_id {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New function to check proxy IP address
@app.get("/proxyCheck")
async def proxy_check():
    """
    Endpoint to check the IP address being used via the proxy.
    """
    proxies = {
        "http": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}",
        "https": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
    }
    try:
        response = requests.get("https://api.ipify.org?format=json", proxies=proxies)
        ip_info = response.json()
        logging.info(f"Proxy IP address: {ip_info}")
        return ip_info
    except Exception as e:
        logging.error(f"Error checking proxy IP: {e}")
        raise HTTPException(status_code=500, detail="Failed to check proxy IP")

# Run the server
def run_server():
    """
    Run the FastAPI server using Uvicorn.
    """
    port = int(os.getenv("PORT", 5050))
    uvicorn.run("TranscriptFetch:app", host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    run_server() 