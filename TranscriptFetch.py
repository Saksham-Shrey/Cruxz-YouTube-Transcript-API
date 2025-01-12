import os
import requests
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

# Priority list of English language codes
ENGLISH_LANGUAGES = ['en-US', 'en-UK', 'en-IN', 'en-CA', 'en-AU', 'en-NZ', 'en-ZA', 'en']


@app.route('/test', methods=['GET'])
def test_connectivity():
    try:
        response = requests.get("https://www.youtube.com")
        return jsonify({'status': 'success', 'code': response.status_code})
    except Exception as e:
        return jsonify({'status': 'failed', 'error': str(e)})


@app.route('/')
def home():
    """Home endpoint for health checks."""
    return jsonify({'message': 'Welcome to the YouTube Transcript API Service!'})

@app.route('/transcript', methods=['GET'])
def get_transcript():
    """
    Fetches the transcript for a given YouTube video ID.
    """
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({'error': 'Missing video_id parameter'}), 400

    try:
        # Fetch transcript using preferred English languages
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=ENGLISH_LANGUAGES)

        # Combine transcript into a single string
        transcript_text = "\n".join([entry['text'] for entry in transcript_data])

        return jsonify({
            'video_id': video_id,
            'transcript': transcript_text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Use PORT environment variable for Render
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port)
