# CruxIt YouTube Transcript API

Welcome to the **CruxIt YouTube Transcript API**, a robust and secure API service for fetching YouTube video transcripts with support for English prioritization and timestamp inclusion. This project leverages the power of the **`youtube-transcript-api`** Python library, integrating it with Flask to create secure and user-friendly API endpoints.

## Features

- **Transcript Retrieval**: Fetch YouTube video transcripts with a focus on English (`en-US`, `en-UK`).
- **Timestamp Support**: Optionally include timestamps (start and duration) for each segment.
- **Secure API Access**: All endpoints are protected by an API key to prevent unauthorized access.
- **Health Checks**: Comprehensive health checks to ensure operational stability.
- **Logging**: Detailed logging for requests and errors to enhance traceability.
- **Scalable Deployment**: Hosted securely on Railway for reliable performance.

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
- **Online Hosting Service** for deployment (e.g., Railway, Render, or AWS; Railway is recommended for simplicity and scalability)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cruxit-youtube-transcript-api.git
   cd cruxit-youtube-transcript-api
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
    "message": "Welcome to the YouTube Transcript API Service. API is operational."
  }
  ```

---

### **2. Fetch Transcript**
- **URL**: `/transcript`
- **Method**: `GET`
- **Description**: Fetch the transcript of a YouTube video.
- **Query Parameters**:
  - `video_id` (required): The YouTube video ID.
  - `timestamps` (optional): Set to `true` to include start and duration timestamps.
- **Headers**:
  - `x-api-key`: Your secure API key.
- **Response**:
  - **With Timestamps**:
    ```json
    {
      "video_id": "dQw4w9WgXcQ",
      "transcript": [
        {
          "start": 0.0,
          "duration": 5.2,
          "text": "Hello world."
        },
        {
          "start": 5.2,
          "duration": 4.5,
          "text": "This is a test transcript."
        }
      ]
    }
    ```
  - **Without Timestamps**:
    ```json
    {
      "video_id": "dQw4w9WgXcQ",
      "transcript": "Hello world.\nThis is a test transcript."
    }
    ```

---

### **3. Validate API Key**
- **URL**: `/validate_key`
- **Method**: `GET`
- **Description**: Verifies if the provided API key is valid.
- **Headers**:
  - `x-api-key`: Your secure API key.
- **Response**:
  ```json
  {
    "message": "Valid API Key"
  }
  ```

---

### **4. Health Check with Dependencies**
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Checks the health of the service and its dependencies.
- **Headers**:
  - `x-api-key`: Your secure API key.
- **Response**:
  ```json
  {
    "status": "Service is running.",
    "youtube_access": "OK"
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
4. The live deployment URL for this project:
   ```
   https://cruxit.up.railway.app/
   ```

---

## Security

- **API Key Enforcement**: All routes are protected by the `x-api-key` header.
- **HTTPS**: Ensure the Railway project uses HTTPS for secure communication.
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
   curl -H "x-api-key: <your_api_key>" https://cruxit.up.railway.app/
   ```

2. Fetch a transcript:
   ```bash
   curl -H "x-api-key: <your_api_key>" "https://cruxit.up.railway.app/transcript?video_id=dQw4w9WgXcQ&timestamps=true"
   ```

3. Validate API key:
   ```bash
   curl -H "x-api-key: <your_api_key>" https://cruxit.up.railway.app/validate_key
   ```

---

## Credits

- **`youtube-transcript-api` Library**:
  - This project uses the `youtube-transcript-api` library for fetching video transcripts.
  - GitHub: [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

---

## Additional Notes

The deployment of this project at **[https://cruxit.up.railway.app/](https://cruxit.up.railway.app/)** is restricted with **API key requirements** to prevent abuse. Unauthorized access attempts will result in a `403 Forbidden` response.

For any questions or support, feel free to reach out !!
