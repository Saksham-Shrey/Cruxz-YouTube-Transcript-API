import os
import logging
import requests
from flask import Flask, request, jsonify
import innertube

app = Flask(__name__)

# Configure logging for better traceability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Secure API Key Management
API_KEY = os.getenv("API_KEY")


def validate_api_key(request):
    """
    Validate the API key from the request headers.
    Returns True if valid, False otherwise.
    """
    provided_key = request.headers.get("x-api-key")
    if not provided_key or provided_key != API_KEY:
        logging.warning("Unauthorized access attempt detected.")
        return False
    return True


@app.before_request
def enforce_api_key():
    """
    Global API key enforcement for all routes.
    Prevents unauthorized access.
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized access. Invalid API key.'}), 403


@app.route('/')
def home():
    """
    Home endpoint for health checks.
    """
    return jsonify({'message': 'Welcome to the YouTube Caption API Service. API is operational.'})


@app.route('/captions', methods=['GET'])
def get_captions():
    """
    Fetch the captions of a YouTube video by its video ID.
    Query Parameters:
    - video_id: Required, the YouTube video ID.
    """
    video_id = request.args.get('video_id')

    if not video_id:
        logging.error("Missing 'video_id' parameter.")
        return jsonify({'error': 'Missing video_id parameter'}), 400

    logging.info(f"Processing captions request for video_id: {video_id}")

    try:
        # Initialize InnerTube client
        client = innertube.InnerTube("WEB")

        # Fetch video metadata
        player_data = client.player(video_id=video_id)

        # Access captions
        captions = player_data.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])

        if captions:
            logging.info(f"Available captions found for video_id: {video_id}")
            captions_list = [
                {"language": caption["name"]["simpleText"], "url": caption["baseUrl"]}
                for caption in captions
            ]

            # Check for English captions and fetch them
            english_caption = next((c for c in captions if c['languageCode'] == 'en'), None)
            if english_caption:
                response = requests.get(english_caption['baseUrl'])
                captions_content = response.text
            else:
                captions_content = None

            return jsonify({
                'video_id': video_id,
                'captions': captions_list,
                'english_captions': captions_content
            })

        else:
            logging.info(f"No captions available for video_id: {video_id}")
            return jsonify({'video_id': video_id, 'captions': [], 'english_captions': None})

    except Exception as e:
        logging.error(f"Error while fetching captions for {video_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/validate_key', methods=['GET'])
def validate_key():
    """
    Endpoint to check if the provided API key is valid.
    """
    return jsonify({'message': 'Valid API Key'}) if validate_api_key(request) else jsonify({'error': 'Invalid API Key'}), 403


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint with dependency checks.
    """
    youtube_status = test_youtube_access()
    return jsonify({
        'status': 'Service is running.',
        'youtube_access': 'OK' if youtube_status else 'FAILED'
    })


def test_youtube_access():
    """
    Test access to YouTube's caption API.
    """
    try:
        client = innertube.InnerTube("WEB")
        client.player(video_id="dQw4w9WgXcQ")  # Example video
        return True
    except Exception:
        return False


def run_server():
    """
    Starts the Flask server with dynamic port binding for production readiness.
    """
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_server()
