# CruxIt YouTube Caption API

This is **CruxIt YouTube Caption API**, a robust and secure API service for fetching YouTube video captions with enhanced functionality. This project leverages the power of the **`innertube`** library, integrating it with Flask to create secure and user-friendly API endpoints.

## Features

- **Caption Retrieval**: Fetch YouTube video captions in various languages.
- **Language Support**: Return available languages for captions if a specific one isn’t provided.
- **Timestamp Support**: Optionally include timestamps (start and duration) for each caption segment.
- **Video Metadata**: Fetch video title, thumbnail, channel name, and channel logo.
- **Secure API Access**: All endpoints are protected by an API key to prevent unauthorized access.
- **Logging**: Detailed logging for requests and errors to enhance traceability.
- **Scalable Deployment**: Hosted securely on platforms like Railway for reliable performance.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [API Endpoints](#api-endpoints)
3. [Deployment](#deployment)
4. [Security](#security)
5. [Environment Variables](#environment-variables)
6. [Testing](#testing)
7. [Credits](#credits)
8. [Additional Notes](#additional-notes)

---

## Getting Started

### Prerequisites
- Python **3.8** or higher
- `pip` package manager (for managing dependencies)
- Hosting platform (e.g., Railway, Render, AWS)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cruxit-youtube-caption-api.git
   cd cruxit-youtube-caption-api
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```bash
   export API_KEY=your_secure_api_key
   export PORT=5000
   ```

4. Run the Flask server locally:
   ```bash
   python app.py
   ```

5. Access the API locally:
   ```
   http://127.0.0.1:5000/
   ```

---

## API Endpoints

### **1. Health Check**
- **URL**: `/`
- **Method**: `GET`
- **Description**: Verifies that the service is running.
- **Headers**:
  - `x-api-key`: Your secure API key.
- **Response**:
  ```json
   {
    "endpoints": {
        "/captions": {
            "description": "Fetch and parse captions for a YouTube video.",
            "notes": "If the 'language' parameter is not provided, the API returns available languages for the video.",
            "parameters": {
                "language": "Optional. The language code to fetch captions in a specific language.",
                "timestamps": "Optional. Set to 'true' to include timestamps in the response.",
                "video_id": "Required. The YouTube video ID."
            }
        }
    },
    "message": "Welcome to the YouTube Caption API Service.",
    "status": "API is operational."
   }
  ```

---

### **2. Fetch Captions**
- **URL**: `/captions`
- **Method**: `GET`
- **Description**: Fetch the captions for a YouTube video.
- **Query Parameters**:
  - `video_id` (required): The YouTube video ID.
  - `language` (optional): Specify a language code for captions.
  - `timestamps` (optional): Set to `true` to include start and duration timestamps.
- **Headers**:
  - `x-api-key`: Your secure API key.
- **Response**:
  - **With Timestamps**:
    ```json
    {
      "video_id": "dQw4w9WgXcQ",
      "video_title": "Video Title",
      "thumbnail": "https://example.com/thumbnail.jpg",
      "channel_name": "Channel Name",
      "channel_logo": "https://example.com/logo.jpg",
      "languageCode": "en",
      "captions": [
        {
          "start": 0.0,
          "duration": 5.2,
          "text": "Hello world."
        },
        {
          "start": 5.2,
          "duration": 4.5,
          "text": "This is a test caption."
        }
      ]
    }
    ```
  - **Without Timestamps**:
    ```json
    {
      "video_id": "dQw4w9WgXcQ",
      "video_title": "Video Title",
      "thumbnail": "https://example.com/thumbnail.jpg",
      "channel_name": "Channel Name",
      "channel_logo": "https://example.com/logo.jpg",
      "languageCode": "en",
      "captions": "Hello world. This is a test caption."
    }
    ```

---

### **3. Available Languages**
- **Description**: If the `language` parameter is not provided, the API returns available languages for the video.
- **Response**:
  ```json
  {
    "video_id": "dQw4w9WgXcQ",
    "video_title": "Video Title",
    "thumbnail": "https://example.com/thumbnail.jpg",
    "channel_name": "Channel Name",
    "channel_logo": "https://example.com/logo.jpg",
    "available_languages": [
      {
        "languageCode": "en",
        "name": "English"
      },
      {
        "languageCode": "fr",
        "name": "French"
      }
    ]
  }
  ```

---

## Deployment

### Steps for Deploying to Railway
1. Create a new Railway project and link your GitHub repository.
2. Add environment variables under the **Settings** tab:
   - `API_KEY`: Your secure API key.
   - `PORT`: The port to run the application (default: 5000).
3. Deploy the project. Railway will handle hosting and scaling.

---

## Security

- **API Key Enforcement**: All routes are protected by the `x-api-key` header.
- **HTTPS**: Ensure the deployment uses HTTPS for secure communication.
- **Rate Limiting**: Consider implementing rate-limiting to prevent abuse.

---

## Environment Variables

| Variable   | Description                             | Example Value      |
|------------|-----------------------------------------|--------------------|
| `API_KEY`  | The API key required to access the API. | `your_secure_api_key` |
| `PORT`     | The port to run the Flask application.  | `5000`             |

---

## Testing

### Using `curl`
1. Test the health check:
   ```bash
   curl -H "x-api-key: <your_api_key>" http://127.0.0.1:5000/
   ```

2. Fetch captions:
   ```bash
   curl -H "x-api-key: <your_api_key>" "http://127.0.0.1:5000/captions?video_id=dQw4w9WgXcQ&timestamps=true"
   ```

---

## Credits

- **`innertube` Library**:
  - This project uses the `innertube` library for fetching video metadata and captions.
  - GitHub: [innertube](https://github.com/tombulled/innertube)

---

## Additional Notes

This project is designed to securely fetch captions and metadata for YouTube videos. For any questions or support, feel free to reach out !!
