import os
import logging
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

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
    return jsonify({'message': 'Welcome to the YouTube Transcript API Service. API is operational.'})


@app.route('/transcript', methods=['GET'])
def get_transcript():
    """
    Fetch the transcript of a YouTube video by its video ID.
    Query Parameters:
    - video_id: Required, the YouTube video ID.
    - timestamps: Optional, if set to 'true', includes start and duration timestamps.
    """
    video_id = request.args.get('video_id')
    timestamps = request.args.get('timestamps', 'false').lower() == 'true'

    if not video_id:
        logging.error("Missing 'video_id' parameter.")
        return jsonify({'error': 'Missing video_id parameter'}), 400

    logging.info(f"Processing transcript request for video_id: {video_id} with timestamps={timestamps}")

    try:
        # Fetch transcript data
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US', 'en-UK', 'en'])
        
        # Process transcript with or without timestamps
        if timestamps:
            transcript = [
                {
                    'start': entry['start'],
                    'duration': entry['duration'],
                    'text': entry['text']
                }
                for entry in transcript_data
            ]
        else:
            transcript = "\n".join([entry['text'] for entry in transcript_data])

        logging.info(f"Successfully fetched transcript for video_id: {video_id}")
        return jsonify({'video_id': video_id, 'transcript': transcript})

    except Exception as e:
        logging.error(f"Error while fetching transcript for {video_id}: {e}")
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
    Test access to YouTube's transcript API.
    """
    try:
        YouTubeTranscriptApi.get_transcript("dQw4w9WgXcQ", languages=['en'])
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
