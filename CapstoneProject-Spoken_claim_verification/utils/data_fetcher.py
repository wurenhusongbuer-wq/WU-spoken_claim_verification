"""
Data Fetcher Utility

Handles downloading and managing video and audio data from various sources.

Author: Capstone Team
Date: 2024
"""

import os
import logging
import subprocess
from typing import List, Dict, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches and manages video and audio data."""
    
    def __init__(self, data_dir: str = "./data"):
        """
        Initialize data fetcher.
        
        Args:
            data_dir: Base directory for storing data
        """
        self.data_dir = Path(data_dir)
        self.video_dir = self.data_dir / "videos"
        self.audio_dir = self.data_dir / "audio"
        self.transcript_dir = self.data_dir / "transcripts"
        
        # Create directories if they don't exist
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Data fetcher initialized with base directory: {self.data_dir}")
    
    def download_youtube_video(
        self,
        url: str,
        output_filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Download video from YouTube.
        
        Args:
            url: YouTube URL
            output_filename: Optional custom filename
            
        Returns:
            Path to downloaded video or None if failed
        """
        try:
            logger.info(f"Downloading YouTube video: {url}")
            
            output_template = str(self.video_dir / (output_filename or "%(title)s.%(ext)s"))
            
            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]",
                "-o", output_template,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded video from {url}")
                # Find the downloaded file
                files = list(self.video_dir.glob("*.mp4"))
                if files:
                    return str(files[-1])  # Return the most recently modified file
            else:
                logger.error(f"Failed to download video: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading YouTube video: {str(e)}")
            return None
    
    def extract_audio(
        self,
        video_path: str,
        output_filename: Optional[str] = None,
        audio_format: str = "wav",
        sample_rate: int = 16000
    ) -> Optional[str]:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to video file
            output_filename: Optional custom filename
            audio_format: Audio format (wav, mp3, etc.)
            sample_rate: Sample rate in Hz
            
        Returns:
            Path to extracted audio or None if failed
        """
        try:
            logger.info(f"Extracting audio from: {video_path}")
            
            video_name = Path(video_path).stem
            output_filename = output_filename or f"{video_name}.{audio_format}"
            output_path = self.audio_dir / output_filename
            
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-acodec", "pcm_s16le",
                "-ar", str(sample_rate),
                "-ac", "1",  # Mono
                "-y",  # Overwrite output file
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info(f"Audio extracted successfully: {output_path}")
                return str(output_path)
            else:
                logger.error(f"Failed to extract audio: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            return None
    
    def load_local_video(self, video_path: str) -> bool:
        """
        Load local video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if file exists and is valid
        """
        path = Path(video_path)
        if path.exists() and path.is_file():
            logger.info(f"Local video file loaded: {video_path}")
            return True
        else:
            logger.warning(f"Video file not found: {video_path}")
            return False
    
    def save_metadata(
        self,
        video_id: str,
        metadata: Dict
    ) -> bool:
        """
        Save metadata for a video.
        
        Args:
            video_id: Video identifier
            metadata: Metadata dictionary
            
        Returns:
            True if saved successfully
        """
        try:
            metadata_file = self.data_dir / f"{video_id}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Metadata saved: {metadata_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
            return False
    
    def load_metadata(self, video_id: str) -> Optional[Dict]:
        """
        Load metadata for a video.
        
        Args:
            video_id: Video identifier
            
        Returns:
            Metadata dictionary or None if not found
        """
        try:
            metadata_file = self.data_dir / f"{video_id}_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Metadata file not found: {metadata_file}")
                return None
        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            return None
    
    def list_videos(self) -> List[str]:
        """
        List all downloaded videos.
        
        Returns:
            List of video file paths
        """
        video_files = list(self.video_dir.glob("*.*"))
        logger.info(f"Found {len(video_files)} video files")
        return [str(f) for f in video_files]
    
    def list_audio_files(self) -> List[str]:
        """
        List all extracted audio files.
        
        Returns:
            List of audio file paths
        """
        audio_files = list(self.audio_dir.glob("*.wav"))
        logger.info(f"Found {len(audio_files)} audio files")
        return [str(f) for f in audio_files]
    
    def cleanup_temp_files(self, keep_audio: bool = True) -> None:
        """
        Clean up temporary files.
        
        Args:
            keep_audio: Whether to keep audio files
        """
        try:
            if not keep_audio:
                for audio_file in self.audio_dir.glob("*"):
                    audio_file.unlink()
                logger.info("Cleaned up audio files")
            
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
