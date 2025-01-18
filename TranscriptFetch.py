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

app = Flask(__name__)

@app.route('/captions', methods=['GET'])
def get_captions():
    """
    Fetch and parse captions for a YouTube video by video ID.
    """
    video_id = request.args.get('video_id')
    timestamps = request.args.get('timestamps', 'false').lower() == 'true'  # Defaults to true

    if not video_id:
        return jsonify({'error': 'Missing video_id parameter'}), 400

    try:
        # Initialize InnerTube client
        client = innertube.InnerTube("WEB")

        # Fetch video metadata
        player_data = client.player(video_id=video_id)
        captions = player_data.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])

        if captions:
            # Preferred English language codes
            preferred_languages = ['en', 'en-US', 'en-UK', 'en-IN', 'en-auto']

            # Search for captions in preferred order
            english_caption = next(
                (c for lang in preferred_languages for c in captions if c['languageCode'] == lang),
                None
            )

            if english_caption:
                # Fetch the raw XML captions
                response = requests.get(english_caption['baseUrl'])
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
                        "languageCode": english_caption['languageCode'],
                        "captions": parsed_captions
                    })
                else:
                    # Concatenate captions into a single string
                    concatenated_text = " ".join(
                        text["text"] for text in parsed_captions if text["text"]
                    )

                    concatenated_text = concatenated_text.replace("&#39", " ")
                    return jsonify({
                        "video_id": video_id,
                        "languageCode": english_caption['languageCode'],
                        "captions": concatenated_text
                    })
            else:
                return jsonify({'error': 'No preferred English captions available for this video.'}), 404
        else:
            return jsonify({'error': 'No captions available for this video.'}), 404

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
