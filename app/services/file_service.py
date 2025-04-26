"""
Service for file handling, including uploads and processing.
"""
import os
import logging
import shutil
from typing import Dict, Any, Optional, BinaryIO, Tuple
import mimetypes
from fastapi import UploadFile
import pydub
import speech_recognition as sr
import PyPDF2
import validators
from pytube import YouTube
from app.core.config import settings
from app.models.files import FileType

class FileService:
    """
    Service for handling file uploads and processing.
    """
    
    def __init__(self):
        """
        Initialize the file service.
        """
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_upload_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Save an uploaded file to the upload directory.
        
        Args:
            file: The uploaded file
            
        Returns:
            Dict with file information
        """
        # Generate a unique filename to avoid collisions
        filename = file.filename
        file_path = os.path.join(self.upload_dir, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Determine file type
        mime_type, _ = mimetypes.guess_type(file_path)
        file_type = self._determine_file_type(mime_type)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return {
            "filename": filename,
            "saved_path": file_path,
            "file_type": file_type,
            "size": file_size
        }
    
    def _determine_file_type(self, mime_type: Optional[str]) -> FileType:
        """
        Determine the file type based on MIME type.
        
        Args:
            mime_type: MIME type of the file
            
        Returns:
            FileType enum value
        """
        if mime_type is None:
            return FileType.PDF  # Default
        
        if mime_type.startswith("audio/"):
            return FileType.AUDIO
        elif mime_type.startswith("video/"):
            return FileType.VIDEO
        elif mime_type == "application/pdf":
            return FileType.PDF
        else:
            # Default to PDF for unknown types
            return FileType.PDF
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from PDF {file_path}: {e}")
            raise
    
    def extract_audio_from_video(self, video_path: str) -> str:
        """
        Extract audio from a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Path to the extracted audio file
        """
        try:
            # Extract filename without extension
            basename = os.path.basename(video_path)
            filename, _ = os.path.splitext(basename)
            
            # Generate output audio path
            audio_path = os.path.join(self.upload_dir, f"{filename}.wav")
            
            # Extract audio using pydub
            video = pydub.AudioSegment.from_file(video_path)
            video.export(audio_path, format="wav")
            
            return audio_path
        except Exception as e:
            logging.error(f"Error extracting audio from video {video_path}: {e}")
            raise
    
    def transcribe_audio_using_sr(self, audio_path: str) -> str:
        """
        Transcribe audio using SpeechRecognition (as fallback).
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                return text
        except Exception as e:
            logging.error(f"Error transcribing audio {audio_path} with SpeechRecognition: {e}")
            return "Error transcribing audio. The quality may be too low or the format is unsupported."
    
    async def download_youtube_video(self, video_url: str) -> Optional[str]:
        """
        Download a YouTube video for processing.
        
        Args:
            video_url: URL of the YouTube video
            
        Returns:
            Path to the downloaded video file or None if failed
        """
        try:
            # Validate URL
            if not validators.url(video_url) or "youtube.com" not in video_url and "youtu.be" not in video_url:
                raise ValueError("Invalid YouTube URL")
            
            # Download video
            yt = YouTube(video_url)
            stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
            
            if not stream:
                raise ValueError("No suitable video stream found")
            
            # Download to our upload directory
            video_path = stream.download(output_path=self.upload_dir)
            return video_path
            
        except Exception as e:
            logging.error(f"Error downloading YouTube video {video_url}: {e}")
            return None 