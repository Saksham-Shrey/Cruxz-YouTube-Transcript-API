import os
import time
import logging
import requests
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

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

@app.route('/')
def home():
    """Home endpoint for health checks."""
    return jsonify({'message': 'Welcome to the YouTube Transcript API Service with Proxy Support!'})


@app.route('/transcript', methods=['GET'])
def get_transcript():
    """
    Fetches the transcript for a given YouTube video ID.
    Optional query parameter `timestamps=true` includes start and duration timestamps.
    """
    video_id = request.args.get('video_id')
    timestamps = request.args.get('timestamps', 'false').lower() == 'true'

    if not video_id:
        return jsonify({'error': 'Missing video_id parameter'}), 400

    logging.info(f"Fetching transcript for video_id: {video_id} with timestamps={timestamps}")

    try:
        # Fetch transcript using youtube-transcript-api
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US', 'en-UK', 'en'])

        if timestamps:
            # Include timestamps
            transcript = [
                {'start': entry['start'], 'duration': entry['duration'], 'text': entry['text']}
                for entry in transcript_data
            ]
        else:
            # Combine transcript into a single string
            transcript = "\n".join([entry['text'] for entry in transcript_data])

        logging.info(f"Transcript fetched successfully for video_id: {video_id}")
        return jsonify({
            'video_id': video_id,
            'transcript': transcript
        })

    except Exception as e:
        logging.error(f"Error fetching transcript for video_id {video_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/youtube_test', methods=['GET'])
def youtube_test():
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
        return jsonify({"status": "success", "code": response.status_code})
    except Exception as e:
        logging.error(f"YouTube connectivity test failed: {e}")
        return jsonify({"status": "failed", "error": str(e)})

if __name__ == '__main__':
    # Use dynamic port for hosting (default: 5000)
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port)
