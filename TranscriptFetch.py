import os
import time
import logging
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Priority list of English language codes
ENGLISH_LANGUAGES = ['en-US', 'en-UK', 'en-IN', 'en-CA', 'en-AU', 'en-NZ', 'en-ZA', 'en']

@app.route('/')
def home():
    """Home endpoint for health check."""
    return jsonify({'message': 'Welcome to the YouTube Transcript API Service!'})

@app.route('/transcript', methods=['GET'])
def get_transcript():
    """
    Fetches the transcript for a given YouTube video ID.
    """
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({'error': 'Missing video_id parameter'}), 400

    logging.info(f"Fetching transcript for video_id: {video_id}")
    try:
        # Add delay to prevent rate limiting
        time.sleep(1)
        
        # Fetch transcript using preferred English languages
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=ENGLISH_LANGUAGES)

        # Combine transcript into a single string
        transcript_text = "\n".join([entry['text'] for entry in transcript_data])

        logging.info(f"Transcript fetched successfully for video_id: {video_id}")
        return jsonify({
            'video_id': video_id,
            'transcript': transcript_text
        })

    except Exception as e:
        logging.error(f"Error fetching transcript for video_id {video_id}: {e}")
        if "Subtitles are disabled" in str(e):
            return jsonify({'error': 'Subtitles are disabled or unavailable for this video.'}), 404
        return jsonify({'error': str(e)}), 500

@app.route('/debug_transcripts', methods=['GET'])
def debug_transcripts():
    """
    Debugging endpoint to list available transcripts for a given video ID.
    """
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({'error': 'Missing video_id parameter'}), 400

    logging.info(f"Listing transcripts for video_id: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = [t.language_code for t in transcript_list]
        logging.info(f"Available transcripts for video_id {video_id}: {available_languages}")
        return jsonify({
            'video_id': video_id,
            'available_languages': available_languages
        })
    except Exception as e:
        logging.error(f"Error listing transcripts for video_id {video_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/youtube_test', methods=['GET'])
def youtube_test():
    """
    Test endpoint to verify connectivity to YouTube from the hosted environment.
    """
    logging.info("Testing connectivity to YouTube...")
    try:
        import requests
        response = requests.get("https://www.youtube.com", timeout=5)
        logging.info("YouTube connectivity test successful.")
        return jsonify({"status": "success", "code": response.status_code})
    except Exception as e:
        logging.error(f"YouTube connectivity test failed: {e}")
        return jsonify({"status": "failed", "error": str(e)})

if __name__ == '__main__':
    # Use dynamic port for hosting (default: 5000)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
