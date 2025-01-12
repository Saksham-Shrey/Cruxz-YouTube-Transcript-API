from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

# Priority list of English language codes
ENGLISH_LANGUAGES = ['en-US', 'en-UK', 'en-IN', 'en-CA', 'en-AU', 'en-NZ', 'en-ZA', 'en']


@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the API!'})


@app.route('/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({'error': 'Missing video_id parameter'}), 400

    try:
        # Attempt to fetch transcript with English preferences
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=ENGLISH_LANGUAGES)

        # Format transcript into a single string
        transcript_text = "\n".join([entry['text'] for entry in transcript_data])

        return jsonify({
            'video_id': video_id,
            'transcript': transcript_text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
