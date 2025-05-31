"""Speech-to-text functionality for voice conversations."""

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO, Dict, Any

logger = logging.getLogger(__name__)


class SpeechToTextEngine(ABC):
    """Abstract base class for speech-to-text engines.
    
    This class defines the interface that all speech-to-text implementations
    must follow to ensure they can be used interchangeably.
    
    Attributes:
        config: Configuration dictionary for the engine.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the speech-to-text engine.
        
        Args:
            config: Configuration dictionary for the engine.
        """
        self.config = config
    
    @abstractmethod
    def transcribe_audio(self, audio_file: BinaryIO) -> str:
        """Transcribe audio data to text.
        
        Args:
            audio_file: A file-like object containing audio data.
            
        Returns:
            str: The transcribed text.
        """
        pass
    
    @abstractmethod
    def start_streaming(self) -> None:
        """Start streaming audio for real-time transcription.
        
        This method initializes resources for streaming audio transcription.
        """
        pass
    
    @abstractmethod
    def process_audio_chunk(self, audio_chunk: bytes) -> Optional[str]:
        """Process a chunk of audio data in streaming mode.
        
        Args:
            audio_chunk: A chunk of audio data.
            
        Returns:
            Optional[str]: Transcribed text if a complete utterance is detected,
                           None otherwise.
        """
        pass
    
    @abstractmethod
    def stop_streaming(self) -> None:
        """Stop streaming audio and release resources."""
        pass


class MockSpeechToTextEngine(SpeechToTextEngine):
    """Mock implementation of speech-to-text for testing purposes.
    
    This implementation doesn't perform actual speech recognition but
    can be used for testing without external dependencies.
    """
    
    def transcribe_audio(self, audio_file: BinaryIO) -> str:
        """Return a mock transcription for testing.
        
        Args:
            audio_file: A file-like object containing audio data.
            
        Returns:
            str: A mock transcription.
        """
        logger.info("Mock STT: Transcribing audio file")
        return "This is a mock transcription for testing purposes."
    
    def start_streaming(self) -> None:
        """Initialize mock streaming session."""
        logger.info("Mock STT: Starting streaming session")
    
    def process_audio_chunk(self, audio_chunk: bytes) -> Optional[str]:
        """Return mock transcription for audio chunk.
        
        Args:
            audio_chunk: A chunk of audio data.
            
        Returns:
            str: A mock transcription if the chunk is long enough.
        """
        # Simulate detecting a complete utterance based on chunk size
        if len(audio_chunk) > 1000:
            return "Mock streaming transcription result."
        return None
    
    def stop_streaming(self) -> None:
        """Stop mock streaming session."""
        logger.info("Mock STT: Stopping streaming session")


class SpeechToTextFactory:
    """Factory for creating speech-to-text engine instances.
    
    This factory creates the appropriate speech-to-text engine based on
    configuration settings.
    """
    
    @staticmethod
    def create_engine(engine_type: str, config: Dict[str, Any]) -> SpeechToTextEngine:
        """Create a speech-to-text engine instance.
        
        Args:
            engine_type: The type of engine to create ("mock", "google", etc.).
            config: Configuration dictionary for the engine.
            
        Returns:
            SpeechToTextEngine: An instance of the requested engine type.
            
        Raises:
            ValueError: If the requested engine type is not supported.
        """
        if engine_type == "mock":
            return MockSpeechToTextEngine(config)
        # Additional engine implementations would be added here
        else:
            raise ValueError(f"Unsupported speech-to-text engine: {engine_type}") 