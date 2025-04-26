"""
Service for fetching and processing YouTube captions.
"""
import logging
import requests
from xml.etree import ElementTree as ET
from typing import List, Dict, Any, Optional
import innertube

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YouTubeService:
    """
    Service for fetching and processing YouTube captions.
    """
    
    def __init__(self):
        """
        Initialize the YouTube service with a innertube client.
        """
        self.client = innertube.InnerTube("WEB")
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Fetch video details from YouTube.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dict containing video details
        """
        try:
            # Fetch video metadata
            player_data = self.client.player(video_id=video_id)
            video_details = player_data.get("videoDetails", {})
            
            # Extract basic information
            metadata = {
                "video_id": video_id,
                "video_title": video_details.get("title", "Unknown Title"),
                "channel_name": video_details.get("author", "Unknown Channel")
            }
            
            # Extract thumbnail (safely handle missing or empty list)
            thumbnails = video_details.get("thumbnail", {}).get("thumbnails", [])
            metadata["thumbnail"] = thumbnails[-1]["url"] if thumbnails else "No Thumbnail Available"
            
            # Extract channel logo (safely handle missing or empty list)
            channel_thumbnails = (
                video_details.get("channelThumbnailSupportedRenderers", {})
                .get("channelThumbnailWithLinkRenderer", {})
                .get("thumbnail", {})
                .get("thumbnails", [])
            )
            metadata["channel_logo"] = channel_thumbnails[-1]["url"] if channel_thumbnails else "No Channel Logo Available"
            
            # Get captions metadata
            captions_data = player_data.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])
            metadata["captions_data"] = captions_data
            
            return metadata
        
        except Exception as e:
            logging.error(f"Error fetching video details for {video_id}: {e}")
            raise
    
    def get_available_languages(self, captions_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract available languages from captions data.
        
        Args:
            captions_data: List of caption tracks
            
        Returns:
            List of available languages with codes and names
        """
        return [
            {
                "languageCode": caption['languageCode'],
                "name": caption['name']['simpleText']
            }
            for caption in captions_data
        ]
    
    def get_caption_track(self, captions_data: List[Dict[str, Any]], language: str) -> Optional[Dict[str, Any]]:
        """
        Get the caption track for a specific language.
        
        Args:
            captions_data: List of caption tracks
            language: Language code to fetch
            
        Returns:
            Caption track data if found, None otherwise
        """
        return next(
            (c for c in captions_data if c['languageCode'] == language),
            None
        )
    
    def fetch_and_parse_captions(self, base_url: str, with_timestamps: bool = False) -> Any:
        """
        Fetch and parse captions from a base URL.
        
        Args:
            base_url: URL to fetch captions from
            with_timestamps: Whether to include timestamps
            
        Returns:
            Parsed captions (either a string or list of segments)
        """
        # Fetch the raw XML captions
        response = requests.get(base_url)
        raw_captions = response.text
        
        # Parse XML
        root = ET.fromstring(raw_captions)
        parsed_captions = [
            {
                "start": float(text.attrib.get("start", 0)),
                "duration": float(text.attrib.get("dur", 0)),
                "text": text.text or ""
            }
            for text in root.findall("text")
        ]
        
        if with_timestamps:
            return parsed_captions
        else:
            # Concatenate captions into a single string
            concatenated_text = " ".join(
                text["text"] for text in parsed_captions if text["text"]
            )
            
            # Clean up the text
            concatenated_text = concatenated_text.replace("&#39;", "'")
            concatenated_text = concatenated_text.replace("\n", " ")
            
            return concatenated_text 