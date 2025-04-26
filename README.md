# Cruxz Transcript API

This is **Cruxz Transcript API**, a robust and secure API service for fetching YouTube video captions, transcribing media files, and summarizing content. This project combines the power of FastAPI, OpenAI, and various media processing tools to create a comprehensive transcription and summarization solution.

## Features

- **YouTube Captions**: 
  - Fetch YouTube video captions in various languages
  - Return available languages for captions
  - Optionally include timestamps for each caption segment
  - Fetch video metadata (title, thumbnail, channel name, etc.)

- **File Transcription**:
  - Transcribe PDF files (text extraction)
  - Transcribe audio files (MP3, WAV, etc.) using OpenAI's Whisper API
  - Transcribe video files by extracting audio and processing it
  - Directly transcribe content from YouTube URLs

- **Summarization**:
  - Summarize any text content using OpenAI's models
  - Summarize YouTube captions
  - Summarize transcribed media files
  - Control summary length and generation parameters

- **Security and Performance**:
  - API key authentication for all endpoints
  - Optimized file handling with size limits
  - CORS support for web applications
  - Comprehensive error handling and logging

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [API Endpoints](#api-endpoints)
3. [Environment Variables](#environment-variables)
4. [Project Structure](#project-structure)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Credits](#credits)

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager
- OpenAI API key (for summarization and audio transcription)
- FFmpeg (for audio extraction from videos)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Cruxz-Transcript-API.git
   cd Cruxz-Transcript-API
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your API keys and settings:
   ```
   API_KEY=your_secure_api_key
   OPENAI_API_KEY=your_openai_api_key
   PORT=5050
   ENVIRONMENT=development
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Access the API documentation:
   ```
   http://127.0.0.1:5050/docs
   ```

---

## API Endpoints

### YouTube Captions

#### Get Captions
- **URL**: `/captions`
- **Method**: `GET`
- **Parameters**:
  - `video_id` (required): YouTube video ID
  - `language` (optional): Language code for captions (e.g., 'en')
  - `timestamps` (optional): Include timestamps in the response (true/false)
  - `summarize` (optional): Summarize the captions (true/false)
  - `max_length` (optional): Maximum length of the summary
  - `temperature` (optional): Temperature for summarization
- **Headers**:
  - `x-api-key`: Your API key

### Summarization

#### Summarize Text
- **URL**: `/summarize`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "text": "Text to summarize...",
    "max_length": 500,
    "temperature": 0.7
  }
  ```
- **Headers**:
  - `x-api-key`: Your API key

### File Transcription

#### Upload File
- **URL**: `/transcribe/upload`
- **Method**: `POST`
- **Form Data**:
  - `file`: The file to upload (PDF, audio, or video)
- **Headers**:
  - `x-api-key`: Your API key
  - `Content-Type`: `multipart/form-data`

#### Transcribe File
- **URL**: `/transcribe/file`
- **Method**: `POST`
- **Form Data**:
  - `file_path`: Path to the uploaded file
  - `summarize` (optional): Whether to summarize the transcription (true/false)
- **Headers**:
  - `x-api-key`: Your API key
  - `Content-Type`: `application/x-www-form-urlencoded`

#### Transcribe YouTube Video
- **URL**: `/transcribe/youtube`
- **Method**: `POST`
- **Form Data**:
  - `video_url`: YouTube video URL
  - `summarize` (optional): Whether to summarize the transcription (true/false)
- **Headers**:
  - `x-api-key`: Your API key
  - `Content-Type`: `application/x-www-form-urlencoded`

---

## Environment Variables

| Variable         | Description                                  | Example Value           |
|------------------|----------------------------------------------|-------------------------|
| `API_KEY`        | The API key required to access the API       | `your_secure_api_key`   |
| `OPENAI_API_KEY` | OpenAI API key for AI features               | `your_openai_api_key`   |
| `PORT`           | The port to run the FastAPI application      | `5050`                  |
| `ENVIRONMENT`    | Application environment                      | `development`           |

---

## Project Structure

```
Cruxz-Transcript-API/
│
├── app/                        # Main application package
│   ├── api/                    # API routers
│   │   ├── __init__.py         # API package initialization
│   │   ├── root.py             # Root path router
│   │   ├── youtube.py          # YouTube captions router
│   │   ├── summarization.py    # Text summarization router
│   │   └── transcription.py    # File transcription router
│   │
│   ├── core/                   # Core functionality
│   │   ├── __init__.py         # Core package initialization
│   │   ├── config.py           # Application configuration
│   │   └── dependencies.py     # API dependencies (auth, etc.)
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py         # Models package initialization
│   │   ├── youtube.py          # YouTube data models
│   │   ├── openai.py           # OpenAI-related models
│   │   └── files.py            # File handling models
│   │
│   ├── services/               # Service classes
│   │   ├── __init__.py         # Services package initialization
│   │   ├── youtube_service.py  # YouTube API service
│   │   ├── openai_service.py   # OpenAI API service
│   │   └── file_service.py     # File handling service
│   │
│   ├── utils/                  # Utility functions
│   │   └── __init__.py         # Utils package initialization
│   │
│   ├── __init__.py             # App package initialization
│   └── main.py                 # FastAPI application setup
│
├── uploads/                    # Directory for uploaded files
├── .env                        # Environment variables (not in repo)
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore file
├── LICENSE                     # License file
├── Procfile                    # Deployment configuration for Heroku/Railway
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
└── run.py                      # Script to run the application
```

---

## Testing

### Using `curl`

1. Test the API information:
   ```bash
   curl -H "x-api-key: <your_api_key>" http://127.0.0.1:5050/
   ```

2. Fetch captions:
   ```bash
   curl -H "x-api-key: <your_api_key>" "http://127.0.0.1:5050/captions?video_id=dQw4w9WgXcQ&timestamps=true"
   ```

3. Summarize text:
   ```bash
   curl -X POST -H "Content-Type: application/json" -H "x-api-key: <your_api_key>" -d '{"text":"Text to summarize..."}' http://127.0.0.1:5050/summarize
   ```

---

## Deployment

### Deployment on Railway or Heroku

1. Create a new project on the platform
2. Link your GitHub repository
3. Add the required environment variables:
   - `API_KEY`
   - `OPENAI_API_KEY`
   - `ENVIRONMENT=production`
4. Deploy the application

The provided Procfile will handle the deployment configuration.

---

## Credits

- **innertube Library**: Used for fetching YouTube video metadata and captions
- **OpenAI API**: Used for text summarization and audio transcription
- **FastAPI**: Modern web framework for building APIs
- **PyPDF2**: Used for extracting text from PDF files
- **pydub**: Used for audio processing
- **pytube**: Used for downloading YouTube videos

---

This project is designed to be easily extensible with additional features. If you have any questions or need support, feel free to reach out!
