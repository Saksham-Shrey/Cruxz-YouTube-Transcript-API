"""
Service for OpenAI-based text summarization and audio transcription.
"""
import logging
import os
from typing import Dict, Any, Optional, Tuple
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings

# Configure OpenAI API
openai.api_key = settings.OPENAI_API_KEY

class OpenAIService:
    """
    Service for OpenAI-based text summarization and audio transcription.
    """
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(openai.error.RateLimitError)
    )
    def summarize_text(self, text: str, max_length: int = 1000, temperature: float = 0.7) -> Tuple[str, Dict[str, int]]:
        """
        Summarize text using OpenAI's API.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of the summary in tokens
            temperature: Temperature for generation
            
        Returns:
            Tuple of (summary, token_usage)
        """
        try:
            logging.info(f"Summarizing text of length {len(text)} with max_length={max_length}")
            
            prompt = f"Please summarize the following text concisely, capturing the key points and important details:\n\n{text}"
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text accurately and concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=temperature
            )
            
            summary = response.choices[0].message.content.strip()
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return summary, token_usage
            
        except Exception as e:
            logging.error(f"Error summarizing text: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(openai.error.RateLimitError)
    )
    def transcribe_audio(self, audio_file_path: str) -> Tuple[str, Optional[Dict[str, int]]]:
        """
        Transcribe audio using OpenAI's Whisper API.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Tuple of (transcription_text, token_usage)
        """
        try:
            logging.info(f"Transcribing audio file: {audio_file_path}")
            
            with open(audio_file_path, "rb") as audio_file:
                response = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Extract transcription text
            transcription_text = response.text
            
            # OpenAI doesn't provide token usage for audio transcriptions,
            # so we return None for token_usage
            return transcription_text, None
            
        except Exception as e:
            logging.error(f"Error transcribing audio: {e}")
            raise 