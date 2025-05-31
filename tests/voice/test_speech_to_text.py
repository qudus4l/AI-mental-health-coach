"""Tests for the speech-to-text module."""

from typing import TYPE_CHECKING
import io

import pytest

from src.mental_health_coach.voice.speech_to_text import (
    SpeechToTextFactory,
    MockSpeechToTextEngine,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


def test_mock_speech_to_text_engine() -> None:
    """Test the mock speech-to-text engine."""
    # Create a mock engine
    config = {"sample_rate": 16000}
    engine = MockSpeechToTextEngine(config)
    
    # Check that the config was stored
    assert engine.config == config
    
    # Test transcribing an audio file
    mock_audio = io.BytesIO(b"mock audio data")
    transcription = engine.transcribe_audio(mock_audio)
    assert isinstance(transcription, str)
    assert len(transcription) > 0
    
    # Test streaming
    engine.start_streaming()
    
    # Test processing a small chunk (should return None)
    small_chunk = b"small"
    result = engine.process_audio_chunk(small_chunk)
    assert result is None
    
    # Test processing a large chunk (should return a transcription)
    large_chunk = b"x" * 1001  # More than 1000 bytes
    result = engine.process_audio_chunk(large_chunk)
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Test stopping streaming
    engine.stop_streaming()


def test_speech_to_text_factory() -> None:
    """Test the speech-to-text factory."""
    # Test creating a mock engine
    config = {"sample_rate": 16000}
    engine = SpeechToTextFactory.create_engine("mock", config)
    assert isinstance(engine, MockSpeechToTextEngine)
    assert engine.config == config
    
    # Test creating an unsupported engine
    with pytest.raises(ValueError):
        SpeechToTextFactory.create_engine("unsupported", config) 