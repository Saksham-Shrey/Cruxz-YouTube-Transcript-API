from xml.etree import ElementTree as ET
import os
import logging
import requests
from flask import Flask, request, jsonify
import innertube

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = os.getenv("API_KEY")


def validate_api_key(request):
    """
    Validate the API key from the request headers.
    """
    provided_key = request.headers.get("x-api-key")
    return provided_key == API_KEY


@app.before_request
def enforce_api_key():
    """
    Enforce API key validation for all routes.
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized access. Invalid API key.'}), 403


@app.route('/')
def home():
    """
    Home endpoint for testing and basic information.
    """
    return jsonify({
        "message": "Welcome to the YouTube Caption API Service.",
        "endpoints": {
            "/captions": {
                "description": "Fetch and parse captions for a YouTube video.",
                "parameters": {
                    "video_id": "Required. The YouTube video ID.",
                    "timestamps": "Optional. Set to 'true' to include timestamps in the response."
                }
            }
        },
        "status": "API is operational."
    })


@app.route('/captions', methods=['GET'])
def get_captions():
    """
    Fetch and parse captions for a YouTube video by video ID.
    Includes options for timestamps and English subtitle preferences.
    """
    video_id = request.args.get('video_id')
    timestamps = request.args.get('timestamps', 'false').lower() == 'true'

    if not video_id or not video_id.isalnum() or len(video_id) not in range(10, 15):
        return jsonify({'error': 'Invalid or missing video_id parameter.'}), 400

    try:
        # Initialize InnerTube client
        client = innertube.InnerTube("WEB")

        # Fetch video metadata
        logging.info(f"Fetching video metadata for video_id: {video_id}")
        player_data = client.player(video_id=video_id)
        captions = player_data.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])

        if not captions:
            logging.warning(f"No captions available for video_id: {video_id}")
            return jsonify({'error': 'No captions available for this video.'}), 404

        # English subtitle preferences in order
        preferred_languages = ['en-US', 'en-UK', 'en-IN', 'en', 'a.en']

        english_caption = None
        for lang in preferred_languages:
            english_caption = next((c for c in captions if c['languageCode'] == lang), None)
            if english_caption:
                break

        if not english_caption:
            logging.warning(f"No preferred English captions available for video_id: {video_id}")
            return jsonify({'error': 'No preferred English captions available for this video.'}), 404

        # Fetch the raw XML captions
        logging.info(f"Fetching captions for video_id: {video_id}, language: {english_caption['languageCode']}")
        try:
            response = requests.get(english_caption['baseUrl'], timeout=10)
            response.raise_for_status()  # Raise an error for bad HTTP responses
        except requests.RequestException as e:
            logging.error(f"Failed to fetch captions for video_id {video_id}: {e}")
            return jsonify({'error': 'Failed to fetch captions from YouTube.'}), 500

        # Parse XML
        try:
            root = ET.fromstring(response.text)
            parsed_captions = [
                {
                    "start": float(text.attrib["start"]),
                    "duration": float(text.attrib["dur"]),
                    "text": text.text or ""
                }
                for text in root.findall("text")
            ]
        except ET.ParseError as e:
            logging.error(f"Failed to parse captions XML for video_id {video_id}: {e}")
            return jsonify({'error': 'Failed to parse captions XML.'}), 500

        if timestamps:
            # Return captions with timestamps
            return jsonify({
                "video_id": video_id,
                "language": english_caption['languageCode'],
                "captions": parsed_captions
            })
        else:
            # Combine captions text without timestamps
            combined_text = "\n".join([entry["text"] for entry in parsed_captions])
            return jsonify({
                "video_id": video_id,
                "language": english_caption['languageCode'],
                "captions": combined_text
            })

    except Exception as e:
        logging.error(f"Unexpected error while processing video_id {video_id}: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500


def run_server():
    """
    Start the Flask server.
    """
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_server()
