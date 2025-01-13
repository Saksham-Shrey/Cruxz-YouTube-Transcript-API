from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable, NoTranscriptFound

app = FastAPI()

class TranscriptWithTimestampsResponse(BaseModel):
    video_id: str
    transcript: list

class TranscriptResponse(BaseModel):
    video_id: str
    transcript: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the YouTube Transcript API!"}

@app.get("/transcript_with_timestamps", response_model=TranscriptWithTimestampsResponse)
def transcript_with_timestamps(video_id: str):
    try:
        # Fetch the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        # Add end timestamps to each transcript segment
        for segment in transcript_list:
            segment["end"] = segment["start"] + segment["duration"]

        response = {
            "video_id": video_id,
            "transcript": transcript_list
        }
        return response
    except TranscriptsDisabled:
        raise HTTPException(status_code=400, detail="Transcripts are disabled for this video.")
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="The video is unavailable.")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/transcript", response_model=TranscriptResponse)
def transcript(video_id: str):
    try:
        # Fetch the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine all text segments into a single string
        transcript_text = " ".join(segment["text"] for segment in transcript_list)

        response = {
            "video_id": video_id,
            "transcript": transcript_text
        }
        return response
    except TranscriptsDisabled:
        raise HTTPException(status_code=400, detail="Transcripts are disabled for this video.")
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="The video is unavailable.")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)