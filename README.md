# Cruxz YouTube Caption API

This is **Cruxz YouTube Caption API**, a robust and secure API service built with FastAPI for fetching YouTube video captions and metadata. It leverages the **`youtube-transcript-api`** library for interacting with YouTube captions and **`pytube`** for fetching video metadata, with API key authentication for security.

## Features

- **Secure API Access**: Endpoints protected by an API key (`x-api-key` header).
- **Caption Retrieval**: Fetch YouTube video captions by video ID.
- **Language Selection**: Specify the desired caption language or retrieve a list of available languages.
- **Translation Support**: Automatically translates captions if available for the requested language.
- **Timestamp Support**: Optionally include start and duration timestamps for each caption segment.
- **Video Metadata**: Retrieve video title, thumbnail URL, channel name, and channel information.
- **Clear Error Handling**: Provides informative JSON responses for common errors (e.g., invalid API key, captions not found).
- **Logging**: Basic logging for monitoring requests and errors.
- **Easy Deployment**: Designed for straightforward deployment on platforms like Railway or Render using Uvicorn.

---

## Table of Contents

1.  [Directory Structure](#directory-structure)
2.  [Code Overview](#code-overview)
3.  [Dependencies](#dependencies)
4.  [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
    -   [Running Locally](#running-locally)
5.  [API Endpoints](#api-endpoints)
    -   [Health Check (`/`)](#1-health-check)
    -   [Fetch Captions (`/captions`)](#2-fetch-captions)
    -   [Available Languages](#3-available-languages)
6.  [Error Handling](#error-handling)
7.  [Environment Variables](#environment-variables)
8.  [Security](#security)
9.  [Deployment](#deployment)
    -   [Railway Example](#steps-for-deploying-to-railway)
10. [Testing](#testing)
    -   [Using `curl`](#using-curl)
11. [Credits](#credits)
12. [License](#license)
13. [Additional Notes](#additional-notes)

---

## Directory Structure

The project follows a simple structure:

```
.
├── .git/               # Git repository data
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── LICENSE             # Project license file (MIT License)
├── Procfile            # Defines process types for Heroku/Railway (web: uvicorn ...)
├── README.md           # This documentation file
├── TranscriptFetch.py  # Main FastAPI application script
└── requirements.txt    # Python package dependencies
```

---

## Code Overview

The core logic resides in `TranscriptFetch.py`:

-   **FastAPI App Initialization**: Sets up the FastAPI application instance.
-   **Logging Configuration**: Configures basic logging to output information and errors.
-   **API Key Middleware**: A middleware function (`api_key_middleware`) intercepts all incoming requests to validate the `x-api-key` header against the `API_KEY` environment variable. Unauthorized requests receive a `403 Forbidden` response.
-   **Home Endpoint (`/`)**: A simple `GET` endpoint that serves as a health check and provides basic API information.
-   **Video Metadata Retrieval**: Uses `pytube` to fetch video details like title, thumbnail, and channel information.
-   **Captions Endpoint (`/captions`)**:
    -   The main `GET` endpoint for fetching captions.
    -   Accepts `video_id` (required), `language` (optional), and `timestamps` (optional, defaults to `false`) as query parameters.
    -   Uses the `youtube-transcript-api` to fetch available transcripts for the given `video_id`.
    -   If `language` is not provided, it returns a list of available languages.
    -   If `language` is provided, it finds the corresponding transcript, with fallback to translation if available.
    -   Returns captions either as a single concatenated string or as a list of objects with `start`, `duration`, and `text` (if `timestamps=true`).
    -   Includes error handling for cases like missing captions or invalid language codes.
-   **Server Execution**: The `run_server` function starts the Uvicorn ASGI server to serve the FastAPI application, listening on the host and port specified by environment variables (`0.0.0.0` and `PORT`). The script runs this function when executed directly (`if __name__ == "__main__":`).

---

## Dependencies

The project relies on the following Python packages (listed in `requirements.txt`):

-   **`fastapi`**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
-   **`youtube-transcript-api`**: A library that allows you to get the transcript/subtitles of a given YouTube video, with language support.
-   **`pytube`**: A lightweight, dependency-free Python library to download YouTube videos and retrieve metadata.
-   **`requests`**: A simple, yet elegant HTTP library for making HTTP requests.
-   **`python-dotenv`**: Reads key-value pairs from a `.env` file and can set them as environment variables. Useful for local development.
-   **`uvicorn`**: An ASGI (Asynchronous Server Gateway Interface) server implementation, used to run the FastAPI application.

---

## Getting Started

### Prerequisites

-   Python **3.8** or higher installed.
-   `pip` (Python package installer).
-   Git (for cloning the repository).

### Installation

1.  Clone the repository:
   ```bash
    git clone https://github.com/CruxzTom/Cruxz-YouTube-Transcript-API.git # Or your fork
    cd Cruxz-YouTube-Transcript-API
   ```

2.  Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3.  Set up environment variables. You can create a `.env` file in the project root for local development:
    ```.env
    API_KEY=your_secret_api_key_here
    PORT=5050 # Optional, defaults to 5050 if not set
    ```
    *Replace `your_secret_api_key_here` with a strong, unique key.*

### Running Locally

1.  Run the FastAPI server using Uvicorn (which `TranscriptFetch.py` does automatically):
   ```bash
   python TranscriptFetch.py
   ```
    The server will start, typically listening on `http://0.0.0.0:5050` (or the port specified in `PORT`).

2.  You can access the API endpoints using tools like `curl` or a web browser (for the home endpoint). Ensure you include your API key in the `x-api-key` header for protected endpoints.
    ```bash
    # Example: Accessing the home endpoint
    curl -H "x-api-key: your_secret_api_key_here" http://127.0.0.1:5050/
   ```

---

## API Endpoints

All endpoints require the `x-api-key` header for authentication.

### **1. Health Check (`/`)**

-   **Method**: `GET`
-   **Description**: Provides basic API information and confirms the service is operational.
-   **Headers**:
    -   `x-api-key`: Your API key.
-   **Success Response (`200 OK`)**:
  ```json
   {
     "message": "Welcome to the YouTube Caption API Service.",
    "endpoints": {
        "/captions": {
            "description": "Fetch and parse captions for a YouTube video.",
            "parameters": {
                 "video_id": "Required. The YouTube video ID.",
                "language": "Optional. The language code to fetch captions in a specific language.",
                 "timestamps": "Optional. Set to 'true' to include timestamps in the response."
             },
             "notes": "If the 'language' parameter is not provided, the API returns available languages for the video."
            }
     },
    "status": "API is operational."
   }
  ```

---

### **2. Fetch Captions (`/captions`)**

-   **Method**: `GET`
-   **Description**: Fetches captions for a specified YouTube video. Can return available languages, concatenated text, or timestamped text.
-   **Query Parameters**:
    -   `video_id` (string, **required**): The unique ID of the YouTube video.
    -   `language` (string, *optional*): The language code (e.g., `en`, `es`, `fr`) for the desired captions. If omitted, the API returns available languages (see section 3).
    -   `timestamps` (string, *optional*): Set to `true` (case-insensitive) to receive captions with start and duration timestamps. Defaults to `false` (concatenated text).
-   **Headers**:
    -   `x-api-key`: Your API key.
-   **Success Response (`200 OK`)**:
    -   **With Timestamps (`timestamps=true`)**:
    ```json
    {
      "video_id": "dQw4w9WgXcQ",
          "video_title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
          "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg", // Example URL
          "channel_name": "Rick Astley",
          "channel_logo": "https://yt3.ggpht.com/...", // Example URL
      "languageCode": "en",
          "timestamped_captions": [
        {
              "start": 1.0, // Example value
              "duration": 3.5, // Example value
              "text": "We're no strangers to love"
        },
        {
              "start": 4.5,
              "duration": 3.8,
              "text": "You know the rules and so do I"
            }
            // ... more caption segments
      ]
    }
    ```
    -   **Without Timestamps (`timestamps=false` or omitted)**:
    ```json
    {
      "video_id": "dQw4w9WgXcQ",
          "video_title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
          "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
          "channel_name": "Rick Astley",
          "channel_logo": "https://yt3.ggpht.com/...",
      "languageCode": "en",
          "captions": "We're no strangers to love You know the rules and so do I A full commitment's what I'm thinking of..." // Concatenated string
    }
    ```

---

### **3. Available Languages**

-   **Trigger**: Call the `/captions` endpoint with a valid `video_id` but *without* the `language` parameter.
-   **Description**: Returns metadata about the video and a list of caption languages available for it.
-   **Success Response (`200 OK`)**:
  ```json
  {
    "video_id": "dQw4w9WgXcQ",
      "video_title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
      "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
      "channel_name": "Rick Astley",
      "channel_logo": "https://yt3.ggpht.com/...",
    "available_languages": [
      {
        "languageCode": "en",
          "name": "English" // Name might vary (e.g., "English (auto-generated)")
      },
      {
          "languageCode": "es",
          "name": "Spanish"
      }
        // ... other available languages
    ]
  }
  ```

---

## Error Handling

The API attempts to return informative JSON error messages with appropriate HTTP status codes:

-   **`403 Forbidden`**: Returned by the middleware if the `x-api-key` header is missing or invalid.
    ```json
    { "error": "Unauthorized access. Invalid API key." }
    ```
-   **`404 Not Found`**: Returned by the `/captions` endpoint if:
    -   No captions are available at all for the video.
        ```json
        {
          "error": "No captions available for this video.",
          "video_title": "...", "thumbnail": "...", "channel_name": "...", "channel_logo": "..."
        }
        ```
    -   Captions are available, but not for the specified `language`.
        ```json
        {
          "error": "No captions available for the selected language: <language_code>",
          "video_title": "...", "thumbnail": "...", "channel_name": "...", "channel_logo": "..."
        }
        ```
-   **`422 Unprocessable Entity`**: Returned by FastAPI if required query parameters (like `video_id`) are missing or have the wrong type. The response format is standard FastAPI validation error output.
-   **`500 Internal Server Error`**: Returned for unexpected errors during processing (e.g., issues communicating with YouTube, parsing errors, other exceptions). The specific error message might be included in the `detail` field.
    ```json
    { "detail": "Specific error message from the exception" }
    ```
    *Check server logs for more detailed traceback information in case of 500 errors.*

---

## Environment Variables

These variables configure the application's behavior. Set them in your deployment environment or a local `.env` file.

| Variable | Description                                     | Required | Default | Example Value          |
| :------- | :---------------------------------------------- | :------- | :------ | :--------------------- |
| `API_KEY`| The secret key required in the `x-api-key` header. | Yes      | -       | `your_secure_api_key`  |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key for better metadata retrieval | No | - | `your_youtube_api_key` |
| `PORT`   | The network port the Uvicorn server listens on. | No       | `5050`  | `8000`                 |

### Important Note on Metadata Retrieval

The API uses a multi-layered approach to retrieve video metadata (title, thumbnail, channel info):

1. **YouTube Data API v3** (most reliable): Used if `YOUTUBE_API_KEY` is provided
2. **pytube Library**: Default fallback if YouTube API key is not available
3. **YouTube oEmbed API**: Used as a secondary fallback
4. **Direct Thumbnail URL**: Used as a last resort when all else fails

For the best experience, we recommend providing a YouTube Data API key in the `.env` file.

---

## Security

-   **API Key Authentication**: Access is controlled via the `API_KEY` environment variable and the `x-api-key` request header. **Keep your API key secret.**
-   **HTTPS**: Always deploy the API behind a reverse proxy (like Nginx or Traefik) or use a hosting provider (like Railway, Render, Heroku) that handles TLS/SSL termination to ensure communication is encrypted via HTTPS.
-   **Input Validation**: FastAPI provides basic validation for query parameter types. `video_id` is treated as a string.
-   **Rate Limiting**: *Not implemented.* For production environments, consider adding rate limiting (e.g., using `slowapi` middleware) to prevent abuse.
-   **Dependency Security**: Keep dependencies updated (`pip install -U -r requirements.txt`) to patch potential vulnerabilities.

---

## Deployment

This FastAPI application can be deployed to any platform supporting Python ASGI applications.

### Steps for Deploying to Railway

1.  **Fork/Clone**: Ensure your code is in a GitHub (or similar) repository.
2.  **Create Railway Project**: Create a new project on Railway and link it to your repository.
3.  **Add Environment Variables**: Navigate to your service settings in Railway, go to the "Variables" tab, and add:
    -   `API_KEY`: Your chosen secure API key.
    -   `PORT`: Railway typically sets this automatically, but you can set it if needed (e.g., `8080`). The `Procfile` tells Railway how to start the app.
4.  **Deployment**: Railway should automatically detect the `Procfile` (or you might need to configure the start command `uvicorn TranscriptFetch:app --host 0.0.0.0 --port $PORT`) and deploy the application. It will provide a public URL.
5.  **Ensure HTTPS**: Railway handles HTTPS automatically.

*(Similar steps apply to platforms like Render, Heroku, Google Cloud Run, AWS App Runner, etc.)*

---

## Testing

### Using `curl`

Replace `your_api_key` with the actual key set in your environment variables and adjust the URL/port if running locally or deployed.

1.  **Test Health Check**:
    ```bash
    curl -H "x-api-key: your_api_key" http://127.0.0.1:5050/
    ```

2.  **Fetch Available Languages**:
    ```bash
    curl -H "x-api-key: your_api_key" "http://127.0.0.1:5050/captions?video_id=dQw4w9WgXcQ"
    ```

3.  **Fetch English Captions (Concatenated)**:
    ```bash
    curl -H "x-api-key: your_api_key" "http://127.0.0.1:5050/captions?video_id=dQw4w9WgXcQ&language=en"
    ```

4.  **Fetch English Captions (With Timestamps)**:
    ```bash
    curl -H "x-api-key: your_api_key" "http://127.0.0.1:5050/captions?video_id=dQw4w9WgXcQ&language=en&timestamps=true"
    ```

5.  **Test Invalid API Key**:
   ```bash
    curl -H "x-api-key: invalid_key" "http://127.0.0.1:5050/captions?video_id=dQw4w9WgXcQ"
    # Expected: 403 Forbidden
   ```

6.  **Test Missing API Key**:
   ```bash
    curl "http://127.0.0.1:5050/captions?video_id=dQw4w9WgXcQ"
    # Expected: 403 Forbidden
   ```

---

## Credits

-   **`youtube-transcript-api`**: This project heavily relies on the `youtube-transcript-api` library for fetching YouTube captions.
    -   GitHub: [jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
-   **`pytube`**: Used for fetching YouTube video metadata.
    -   GitHub: [pytube/pytube](https://github.com/pytube/pytube)
-   **FastAPI**: The web framework used to build the API.
    -   Website: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
-   **Uvicorn**: The ASGI server used to run the application.
    -   Website: [www.uvicorn.org](https://www.uvicorn.org/)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Additional Notes

-   This API relies on YouTube's internal structures, which can change without notice. While `youtube-transcript-api` aims to adapt, breakage is possible.
-   Be mindful of YouTube's terms of service when using this API. Avoid excessive requests that could lead to rate limiting or blocking.
-   For questions or support, please open an issue on the GitHub repository.
