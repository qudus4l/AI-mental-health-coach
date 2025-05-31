"""Voice conversation manager for the mental health coach application."""

import os
import logging
import threading
import tempfile
from typing import Optional, Callable, Dict, Any, List

from src.mental_health_coach.voice.audio_io import AudioRecorder, AudioPlayer, AudioIOFactory
from src.mental_health_coach.voice.speech_to_text import SpeechToTextEngine, SpeechToTextFactory
from src.mental_health_coach.voice.text_to_speech import TextToSpeechEngine, TextToSpeechFactory

logger = logging.getLogger(__name__)


class VoiceConversationManager:
    """Manager for voice-based conversations.
    
    This class integrates audio recording/playback with speech-to-text and
    text-to-speech to enable voice conversations with the AI coach.
    
    Attributes:
        recorder: Audio recorder instance.
        player: Audio player instance.
        stt_engine: Speech-to-text engine.
        tts_engine: Text-to-speech engine.
        config: Configuration dictionary for the conversation manager.
        on_transcription_complete: Callback function for transcription completion.
        on_speech_complete: Callback function for speech synthesis completion.
        temp_dir: Directory for temporary audio files.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the voice conversation manager.
        
        Args:
            config: Configuration dictionary with the following keys:
                - recorder_type: Type of audio recorder to use.
                - player_type: Type of audio player to use.
                - stt_engine_type: Type of speech-to-text engine to use.
                - tts_engine_type: Type of text-to-speech engine to use.
                - recorder_config: Configuration for the audio recorder.
                - player_config: Configuration for the audio player.
                - stt_config: Configuration for the speech-to-text engine.
                - tts_config: Configuration for the text-to-speech engine.
        """
        self.config = config
        
        # Create audio I/O components
        self.recorder = AudioIOFactory.create_recorder(
            config.get("recorder_type", "mock"),
            config.get("recorder_config", {})
        )
        self.player = AudioIOFactory.create_player(
            config.get("player_type", "mock"),
            config.get("player_config", {})
        )
        
        # Create speech processing engines
        self.stt_engine = SpeechToTextFactory.create_engine(
            config.get("stt_engine_type", "mock"),
            config.get("stt_config", {})
        )
        self.tts_engine = TextToSpeechFactory.create_engine(
            config.get("tts_engine_type", "mock"),
            config.get("tts_config", {})
        )
        
        # Set up temporary directory for audio files
        self.temp_dir = tempfile.mkdtemp(prefix="mental_health_coach_")
        
        # Callback functions
        self.on_transcription_complete: Optional[Callable[[str], None]] = None
        self.on_speech_complete: Optional[Callable[[], None]] = None
        
        # State variables
        self._recording_thread: Optional[threading.Thread] = None
        self._playback_thread: Optional[threading.Thread] = None
    
    def start_listening(self) -> None:
        """Start listening for user speech.
        
        This method starts recording audio and processes it for transcription.
        The transcription result is passed to the on_transcription_complete callback.
        """
        if self.recorder.is_recording():
            logger.warning("Already recording, ignoring start_listening call")
            return
        
        def record_and_transcribe() -> None:
            """Record audio and transcribe it."""
            try:
                # Start recording
                self.recorder.start_recording()
                
                # Record until manually stopped
                while self.recorder.is_recording():
                    threading.Event().wait(0.1)  # Check every 100ms
                
                # Get the recorded audio and save it to a temp file
                audio_data = self.recorder.stop_recording()
                temp_audio_path = os.path.join(self.temp_dir, "recording.wav")
                self.recorder.save_recording(temp_audio_path)
                
                # Transcribe the audio
                with open(temp_audio_path, "rb") as audio_file:
                    transcription = self.stt_engine.transcribe_audio(audio_file)
                
                # Call the callback with the transcription result
                if self.on_transcription_complete and transcription:
                    self.on_transcription_complete(transcription)
                
            except Exception as e:
                logger.error(f"Error in recording thread: {e}", exc_info=True)
        
        # Start the recording in a separate thread
        self._recording_thread = threading.Thread(target=record_and_transcribe)
        self._recording_thread.daemon = True
        self._recording_thread.start()
    
    def stop_listening(self) -> None:
        """Stop listening for user speech.
        
        This method stops the audio recording and triggers transcription.
        """
        if not self.recorder.is_recording():
            logger.warning("Not recording, ignoring stop_listening call")
            return
        
        # Stop recording (the transcription will happen in the recording thread)
        self.recorder.stop_recording()
        
        # Wait for the recording thread to complete
        if self._recording_thread:
            self._recording_thread.join(timeout=5.0)
            self._recording_thread = None
    
    def speak_response(self, text: str) -> None:
        """Speak a text response to the user.
        
        Args:
            text: The text to speak.
        """
        if self.player.is_playing():
            logger.warning("Already playing audio, stopping current playback")
            self.player.stop_playback()
        
        def synthesize_and_play() -> None:
            """Synthesize speech and play it."""
            try:
                # Synthesize speech
                audio_data = self.tts_engine.synthesize_speech(text)
                
                # Save to a temp file
                temp_audio_path = os.path.join(self.temp_dir, "response.wav")
                self.tts_engine.save_to_file(text, temp_audio_path)
                
                # Play the audio
                self.player.play_file(temp_audio_path)
                
                # Wait for playback to complete
                while self.player.is_playing():
                    threading.Event().wait(0.1)  # Check every 100ms
                
                # Call the callback when speech is complete
                if self.on_speech_complete:
                    self.on_speech_complete()
                
            except Exception as e:
                logger.error(f"Error in playback thread: {e}", exc_info=True)
        
        # Start the playback in a separate thread
        self._playback_thread = threading.Thread(target=synthesize_and_play)
        self._playback_thread.daemon = True
        self._playback_thread.start()
    
    def stop_speaking(self) -> None:
        """Stop speaking the current response."""
        if not self.player.is_playing():
            logger.warning("Not playing audio, ignoring stop_speaking call")
            return
        
        # Stop playback
        self.player.stop_playback()
        
        # Wait for the playback thread to complete
        if self._playback_thread:
            self._playback_thread.join(timeout=5.0)
            self._playback_thread = None
    
    def set_on_transcription_complete(self, callback: Callable[[str], None]) -> None:
        """Set the callback for transcription completion.
        
        Args:
            callback: Function to call when transcription is complete.
                     The function should take a string parameter for the transcription.
        """
        self.on_transcription_complete = callback
    
    def set_on_speech_complete(self, callback: Callable[[], None]) -> None:
        """Set the callback for speech synthesis completion.
        
        Args:
            callback: Function to call when speech synthesis is complete.
        """
        self.on_speech_complete = callback
    
    def cleanup(self) -> None:
        """Clean up resources used by the conversation manager."""
        # Stop any ongoing recording or playback
        if self.recorder.is_recording():
            self.recorder.stop_recording()
        
        if self.player.is_playing():
            self.player.stop_playback()
        
        # Clean up temporary files
        for filename in os.listdir(self.temp_dir):
            try:
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.error(f"Error deleting temp file {filename}: {e}")
        
        try:
            os.rmdir(self.temp_dir)
        except Exception as e:
            logger.error(f"Error removing temp directory {self.temp_dir}: {e}") 