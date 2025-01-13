# YouTube Transcript API with Proxy Support

This Python-based API uses Flask to provide YouTube video transcript fetching with optional proxy integration. It leverages the **[YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)**, an open-source library for retrieving YouTube video transcripts programmatically.

---

## **Features**
- **Fetch YouTube Transcripts**: Retrieves subtitles/transcripts for YouTube videos in English (`en`) using `youtube-transcript-api`.
- **Proxy Support**: Optional use of ScraperAPI or Bright Data proxies for enhanced reliability.
- **Health Check Endpoint**: Provides a simple endpoint to confirm API functionality.
- **YouTube Connectivity Test**: Verifies connectivity to YouTube, optionally using proxies.
- **Customizable Proxy Settings**: Flexible toggling between ScraperAPI and Bright Data for different proxy configurations.

---

## **System Requirements**
- **Python 3.8+**
- **macOS, Linux, or Windows**
- Required Libraries:
  - `Flask`
  - `youtube-transcript-api`
  - `requests`
  - `logging`

---

## **Installation**

### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/youtube-transcript-api.git
cd youtube-transcript-api
```

### 2. **Set Up a Virtual Environment**
To isolate your dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. **Install Dependencies**
Install the required Python libraries:
```bash
pip install -r requirements.txt
```

### 4. **Set Up Environment Variables**
Create a `.env` file in the project root or export environment variables directly in the terminal:
```env
SCRAPERAPI_KEY=your_scraperapi_key
BRIGHT_DATA_PROXY=http://username:password@proxy-server:port
PORT=5050
```

Alternatively, use `export` commands in the terminal:
```bash
export SCRAPERAPI_KEY=your_scraperapi_key
export BRIGHT_DATA_PROXY=http://username:password@proxy-server:port
export PORT=5050
```

---

## **Usage**

### 1. **Run the Flask Server Locally**
Start the API server:
```bash
python TranscriptFetch.py
```
The API will be hosted at `http://0.0.0.0:5050` by default.

---

## **Endpoints**

### **1. Health Check**
- **URL**: `/`
- **Method**: `GET`
- **Description**: Simple endpoint to verify the API is running.
- **Example Response**:
  ```json
  {
    "message": "Welcome to the YouTube Transcript API Service with Proxy Support!"
  }
  ```

### **2. Fetch Transcript**
- **URL**: `/transcript`
- **Method**: `GET`
- **Parameters**:
  - `video_id` (required): The YouTube video ID.
- **Description**: Fetches the transcript for a given YouTube video.
- **Example Request**:
  ```bash
  curl "http://localhost:5050/transcript?video_id=YOUR_VIDEO_ID"
  ```
- **Example Response**:
  ```json
  {
    "video_id": "VIDEO_ID",
    "transcript": "This is the transcript of the video..."
  }
  ```

### **3. Test YouTube Connectivity**
- **URL**: `/youtube_test`
- **Method**: `GET`
- **Description**: Tests connectivity to YouTube, optionally through proxies.
- **Example Request**:
  ```bash
  curl "http://localhost:5050/youtube_test"
  ```
- **Example Response**:
  ```json
  {
    "status": "success",
    "code": 200
  }
  ```

---

## **Deployment to Render**

Render is a modern cloud platform for deploying web applications. Follow these steps to deploy your Flask API on Render:

### 1. **Sign Up for Render**
- Go to [Render](https://render.com) and create an account if you don’t already have one.

### 2. **Create a New Web Service**
- Click **New** and select **Web Service**.
- Connect your GitHub repository or upload your project files.

### 3. **Set Environment Variables**
- In the Render dashboard, navigate to the **Environment** tab for your web service.
- Add the following environment variables:
  - `SCRAPERAPI_KEY`
  - `BRIGHT_DATA_PROXY`
  - `PORT=5050`

### 4. **Configure Build Settings**
- In the **Build Command** field, enter:
  ```bash
  pip install -r requirements.txt
  ```
- In the **Start Command** field, enter:
  ```bash
  python TranscriptFetch.py
  ```

### 5. **Deploy**
- Click **Deploy** to start your Flask application.
- Render will assign a URL (e.g., `https://your-app.onrender.com`) to your service.

### 6. **Test the API**
- Use `curl` or your browser to test the deployed endpoints:
  - Health Check: `https://your-app.onrender.com/`
  - Fetch Transcript: `https://your-app.onrender.com/transcript?video_id=YOUR_VIDEO_ID`
  - YouTube Test: `https://your-app.onrender.com/youtube_test`

---

## **Configuration**

### **Proxy Settings**
1. **Enable Proxies**:
   - Set `USE_PROXY = True` in `TranscriptFetch.py`.
2. **ScraperAPI**:
   - Use `USE_SCRAPERAPI = True` to enable ScraperAPI.
   - Set the `SCRAPERAPI_KEY` environment variable with your API key.
3. **Bright Data**:
   - Use `USE_SCRAPERAPI = False` to switch to Bright Data proxies.
   - Set the `BRIGHT_DATA_PROXY` environment variable with the Bright Data proxy URL.

### **Disable Proxy**
Set `USE_PROXY = False` to bypass proxy usage entirely.

---

## **Development Notes**

### **Credits**
This project uses the **[YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)** library for transcript retrieval. Special thanks to the contributors of this open-source project for making it easier to programmatically access YouTube transcripts.

### **Logging**
Logs are configured to display messages at the `INFO` level. All key operations and errors are logged for debugging purposes.

### **Rate Limiting**
The script includes a `time.sleep(1)` delay to reduce the risk of rate limiting when fetching transcripts.

### **Error Handling**
- Invalid `video_id` values or network issues will result in an error response.
- Example Error Response:
  ```json
  {
    "error": "An error occurred: VIDEO_ID_NOT_FOUND"
  }
  ```

---

## **Contributing**

Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your changes.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
