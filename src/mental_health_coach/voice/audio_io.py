"""Audio input/output functionality for voice conversations."""

import os
import logging
import threading
from abc import ABC, abstractmethod
from typing import Optional, Callable, BinaryIO, Dict, Any, List

logger = logging.getLogger(__name__)


class AudioRecorder(ABC):
    """Abstract base class for audio recording.
    
    This class defines the interface that all audio recorder implementations
    must follow to ensure they can be used interchangeably.
    
    Attributes:
        config: Configuration dictionary for the recorder.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the audio recorder.
        
        Args:
            config: Configuration dictionary for the recorder.
        """
        self.config = config
    
    @abstractmethod
    def start_recording(self) -> None:
        """Start recording audio.
        
        This method should initialize the audio recording session.
        """
        pass
    
    @abstractmethod
    def stop_recording(self) -> bytes:
        """Stop recording audio and return the recorded data.
        
        Returns:
            bytes: The recorded audio data.
        """
        pass
    
    @abstractmethod
    def save_recording(self, filename: str) -> None:
        """Save the last recording to a file.
        
        Args:
            filename: The name of the file to save the recording to.
        """
        pass
    
    @abstractmethod
    def is_recording(self) -> bool:
        """Check if recording is in progress.
        
        Returns:
            bool: True if recording is in progress, False otherwise.
        """
        pass


class AudioPlayer(ABC):
    """Abstract base class for audio playback.
    
    This class defines the interface that all audio player implementations
    must follow to ensure they can be used interchangeably.
    
    Attributes:
        config: Configuration dictionary for the player.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the audio player.
        
        Args:
            config: Configuration dictionary for the player.
        """
        self.config = config
    
    @abstractmethod
    def play_audio(self, audio_data: bytes) -> None:
        """Play audio from memory.
        
        Args:
            audio_data: The audio data to play.
        """
        pass
    
    @abstractmethod
    def play_file(self, filename: str) -> None:
        """Play audio from a file.
        
        Args:
            filename: The name of the file to play.
        """
        pass
    
    @abstractmethod
    def stop_playback(self) -> None:
        """Stop audio playback."""
        pass
    
    @abstractmethod
    def is_playing(self) -> bool:
        """Check if audio is currently playing.
        
        Returns:
            bool: True if audio is playing, False otherwise.
        """
        pass


class MockAudioRecorder(AudioRecorder):
    """Mock implementation of audio recorder for testing purposes.
    
    This implementation doesn't perform actual audio recording but
    can be used for testing without external dependencies.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the mock audio recorder.
        
        Args:
            config: Configuration dictionary for the recorder.
        """
        super().__init__(config)
        self._recording = False
        self._last_recording = b""
    
    def start_recording(self) -> None:
        """Start mock recording session."""
        logger.info("Mock Recorder: Starting recording")
        self._recording = True
    
    def stop_recording(self) -> bytes:
        """Stop mock recording and return dummy data.
        
        Returns:
            bytes: Empty bytes representing mock audio data.
        """
        logger.info("Mock Recorder: Stopping recording")
        self._recording = False
        self._last_recording = b"mock_audio_data"
        return self._last_recording
    
    def save_recording(self, filename: str) -> None:
        """Save mock recording to a file.
        
        Args:
            filename: The name of the file to save the recording to.
        """
        logger.info(f"Mock Recorder: Saving recording to {filename}")
        with open(filename, "wb") as f:
            f.write(self._last_recording)
    
    def is_recording(self) -> bool:
        """Check if mock recording is in progress.
        
        Returns:
            bool: The current recording state.
        """
        return self._recording


class MockAudioPlayer(AudioPlayer):
    """Mock implementation of audio player for testing purposes.
    
    This implementation doesn't perform actual audio playback but
    can be used for testing without external dependencies.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the mock audio player.
        
        Args:
            config: Configuration dictionary for the player.
        """
        super().__init__(config)
        self._playing = False
    
    def play_audio(self, audio_data: bytes) -> None:
        """Mock playing audio from memory.
        
        Args:
            audio_data: The audio data to play.
        """
        logger.info(f"Mock Player: Playing audio data ({len(audio_data)} bytes)")
        self._playing = True
        # Simulate playback completion after a short delay
        threading.Timer(0.5, self._complete_playback).start()
    
    def play_file(self, filename: str) -> None:
        """Mock playing audio from a file.
        
        Args:
            filename: The name of the file to play.
        """
        logger.info(f"Mock Player: Playing audio file {filename}")
        self._playing = True
        # Simulate playback completion after a short delay
        threading.Timer(0.5, self._complete_playback).start()
    
    def _complete_playback(self) -> None:
        """Mark playback as complete."""
        self._playing = False
        logger.info("Mock Player: Playback complete")
    
    def stop_playback(self) -> None:
        """Stop mock audio playback."""
        logger.info("Mock Player: Stopping playback")
        self._playing = False
    
    def is_playing(self) -> bool:
        """Check if mock audio is currently playing.
        
        Returns:
            bool: The current playback state.
        """
        return self._playing


class AudioIOFactory:
    """Factory for creating audio I/O components.
    
    This factory creates the appropriate audio recorder and player
    based on configuration settings.
    """
    
    @staticmethod
    def create_recorder(recorder_type: str, config: Dict[str, Any]) -> AudioRecorder:
        """Create an audio recorder instance.
        
        Args:
            recorder_type: The type of recorder to create ("mock", "pyaudio", etc.).
            config: Configuration dictionary for the recorder.
            
        Returns:
            AudioRecorder: An instance of the requested recorder type.
            
        Raises:
            ValueError: If the requested recorder type is not supported.
        """
        if recorder_type == "mock":
            return MockAudioRecorder(config)
        # Additional recorder implementations would be added here
        else:
            raise ValueError(f"Unsupported audio recorder: {recorder_type}")
    
    @staticmethod
    def create_player(player_type: str, config: Dict[str, Any]) -> AudioPlayer:
        """Create an audio player instance.
        
        Args:
            player_type: The type of player to create ("mock", "pyaudio", etc.).
            config: Configuration dictionary for the player.
            
        Returns:
            AudioPlayer: An instance of the requested player type.
            
        Raises:
            ValueError: If the requested player type is not supported.
        """
        if player_type == "mock":
            return MockAudioPlayer(config)
        # Additional player implementations would be added here
        else:
            raise ValueError(f"Unsupported audio player: {player_type}") 