"""
ElevenLabs TTS Client for Audio Generation

This module demonstrates production-ready API integration for text-to-speech
conversion, showcasing patterns commonly evaluated in technical interviews.

Key Interview Concepts:
- Audio processing and streaming
- API client design and error handling
- File management and cleanup
- Performance optimization for media files
"""

import asyncio
import io
import logging
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path

import httpx
from elevenlabs import ElevenLabs

# Configure logging
logger = logging.getLogger(__name__)


class ElevenLabsProcessor:
    """
    Production-ready ElevenLabs TTS client for audio generation.
    
    Interview Focus Areas:
    - Audio processing pipeline design
    - Streaming and file handling
    - Error recovery and retry logic
    - Resource management and cleanup
    """
    
    def __init__(
        self, 
        api_key: str, 
        voice_id: str = "vBaThRCUhBj6DkxqB593",  # Your cloned voice
        model_id: str = "eleven_multilingual_v2"
    ):
        """
        Initialize ElevenLabs client with voice configuration.
        
        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID to use (default: Your cloned voice - personalized)
            model_id: TTS model to use (updated to latest model)
        """
        if not api_key or api_key == "your_elevenlabs_api_key_here":
            raise ValueError("Valid ElevenLabs API key required")
        
        # Initialize the new ElevenLabs client
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.model_id = model_id
        self.output_format = "mp3_44100_128"  # High-quality MP3
        
        logger.info(f"ElevenLabs client initialized with voice: {voice_id}")
    
    def estimate_audio_duration(self, text: str, words_per_minute: int = 150) -> float:
        """
        Estimate audio duration from text length.
        
        Interview Concept: Shows understanding of:
        - Media processing calculations
        - Performance estimation
        - User experience considerations
        
        Args:
            text: Input text for TTS
            words_per_minute: Average speaking rate
            
        Returns:
            Estimated duration in minutes
        """
        word_count = len(text.split())
        duration_minutes = word_count / words_per_minute
        
        logger.info(f"Estimated audio duration: {duration_minutes:.1f} minutes for {word_count} words")
        return duration_minutes
    
    def validate_text_length(self, text: str, max_chars: int = 5000) -> str:
        """
        Validate and potentially truncate text for TTS processing.
        
        Interview Concept: Input validation and graceful degradation
        
        Args:
            text: Input text
            max_chars: Maximum character limit for API
            
        Returns:
            Validated/truncated text
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(text) <= max_chars:
            return text
        
        logger.warning(f"Text length ({len(text)}) exceeds limit. Truncating to {max_chars} chars.")
        
        # Truncate at sentence boundary if possible
        truncated = text[:max_chars]
        last_sentence = truncated.rfind('.')
        
        if last_sentence > max_chars * 0.8:  # If we find a good break point
            truncated = truncated[:last_sentence + 1]
        
        return truncated
    
    async def generate_audio(self, text: str) -> bytes:
        """
        Generate audio from text using ElevenLabs API.
        
        Interview Concept: Async audio processing with proper error handling
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data as bytes (MP3 format)
            
        Raises:
            ValueError: For invalid input
            httpx.HTTPError: For API communication errors
        """
        # Validate input
        processed_text = self.validate_text_length(text)
        duration_estimate = self.estimate_audio_duration(processed_text)
        
        logger.info(f"Generating audio for {len(processed_text)} characters")
        
        try:
            # Generate audio using ElevenLabs client
            # Note: ElevenLabs API calls are synchronous, so we wrap them
            audio_data = await asyncio.to_thread(
                self._generate_sync,
                processed_text
            )
            
            logger.info(f"Audio generation successful. Size: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            # Re-raise with more context
            raise RuntimeError(f"Failed to generate audio: {str(e)}") from e
    
    def _generate_sync(self, text: str) -> bytes:
        """
        Synchronous audio generation wrapped for async execution.
        
        Interview Concept: Thread pool integration for blocking operations
        """
        try:
            # Use the new ElevenLabs API
            audio = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                output_format=self.output_format,
                text=text,
                model_id=self.model_id
            )
            
            # The new API returns a generator, so we need to collect the bytes
            if hasattr(audio, '__iter__') and not isinstance(audio, (str, bytes)):
                # It's a generator, collect all bytes
                audio_bytes = b''.join(audio)
                return audio_bytes
            else:
                # It's already bytes
                return audio
            
        except Exception as e:
            logger.error(f"ElevenLabs API call failed: {e}")
            raise
    
    def create_audio_file(self, audio_data: bytes, filename: str = "summary.mp3") -> io.BytesIO:
        """
        Create in-memory audio file for download.
        
        Interview Concept: Memory-efficient file handling for web apps
        
        Args:
            audio_data: Audio bytes from TTS
            filename: Desired filename for download
            
        Returns:
            BytesIO object ready for download
        """
        audio_buffer = io.BytesIO(audio_data)
        audio_buffer.name = filename  # Set filename for Streamlit download
        audio_buffer.seek(0)  # Reset pointer to beginning
        
        logger.info(f"Created audio file buffer: {filename}")
        return audio_buffer
    
    async def text_to_audio_file(self, text: str, filename: str = "summary.mp3") -> io.BytesIO:
        """
        Complete pipeline: text to downloadable audio file.
        
        Interview Concept: End-to-end pipeline design with error handling
        
        Args:
            text: Text to convert
            filename: Output filename
            
        Returns:
            Audio file ready for download
        """
        logger.info("Starting text-to-audio pipeline")
        
        try:
            # Generate audio
            audio_data = await self.generate_audio(text)
            
            # Create downloadable file
            audio_file = self.create_audio_file(audio_data, filename)
            
            logger.info("Text-to-audio pipeline completed successfully")
            return audio_file
            
        except Exception as e:
            logger.error(f"Text-to-audio pipeline failed: {e}")
            raise
    
    def get_voice_info(self) -> Dict[str, Any]:
        """
        Get information about the configured voice.
        
        Interview Concept: API introspection and configuration management
        """
        return {
            "voice_id": self.voice_id,
            "model_id": self.model_id,
            "output_format": self.output_format,
            "optimized_for": "Scientific content narration",
            "estimated_cost_per_minute": "$0.30"  # Rough estimate
        }
    
    async def test_connection(self) -> bool:
        """
        Test ElevenLabs API connection and configuration.
        
        Interview Concept: Health checks and system validation
        """
        try:
            # Test with minimal text
            test_audio = await self.generate_audio("Testing connection.")
            return len(test_audio) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False