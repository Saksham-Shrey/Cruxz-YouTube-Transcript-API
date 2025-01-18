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
    Allows users to select a specific language for captions.
    """
    video_id = request.args.get('video_id')
    selected_language = request.args.get('language')
    timestamps = request.args.get('timestamps', 'false').lower() == 'true'  # Defaults to true

    if not video_id:
        return jsonify({'error': 'Missing video_id parameter'}), 400

    try:
        # Initialize InnerTube client
        client = innertube.InnerTube("WEB")

        # Fetch video metadata
        player_data = client.player(video_id=video_id)
        captions = player_data.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])

        if not captions:
            return jsonify({'error': 'No captions available for this video.'}), 404

        # If no specific language is selected, return available languages
        if not selected_language:
            available_languages = [
                {
                    "languageCode": caption['languageCode'],
                    "name": caption['name']['simpleText']
                }
                for caption in captions
            ]
            return jsonify({
                "video_id": video_id,
                "available_languages": available_languages
            })

        # Find the caption track for the selected language
        selected_caption = next(
            (c for c in captions if c['languageCode'] == selected_language),
            None
        )

        if not selected_caption:
            return jsonify({'error': f'No captions available for the selected language: {selected_language}'}), 404

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
            return jsonify({
                "video_id": video_id,
                "languageCode": selected_language,
                "captions": parsed_captions
            })
        else:
            # Concatenate captions into a single string
            concatenated_text = " ".join(
                text["text"] for text in parsed_captions if text["text"]
            )
            concatenated_text = concatenated_text.replace("&#39;", "'")

            return jsonify({
                "video_id": video_id,
                "languageCode": selected_language,
                "captions": concatenated_text
            })

    except Exception as e:
        logging.error(f"Error while fetching captions for video_id {video_id}: {e}")
        return jsonify({'error': str(e)}), 500




def run_server():
    """
    Start the Flask server.
    """
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_server()
