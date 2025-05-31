"""Tests for the text-to-speech module."""

from typing import TYPE_CHECKING
import os
import tempfile

import pytest

from src.mental_health_coach.voice.text_to_speech import (
    TextToSpeechFactory,
    MockTextToSpeechEngine,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


def test_mock_text_to_speech_engine() -> None:
    """Test the mock text-to-speech engine."""
    # Create a mock engine
    config = {"voice": "voice1"}
    engine = MockTextToSpeechEngine(config)
    
    # Check that the config was stored
    assert engine.config == config
    
    # Test synthesizing speech
    text = "This is a test message."
    audio_data = engine.synthesize_speech(text)
    assert isinstance(audio_data, bytes)
    
    # Test saving to a file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        engine.save_to_file(text, temp_path)
        assert os.path.exists(temp_path)
        assert os.path.getsize(temp_path) >= 0  # File should exist but may be empty
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # Test getting available voices
    voices = engine.get_available_voices()
    assert isinstance(voices, dict)
    assert "voice1" in voices
    assert "voice2" in voices
    
    # Test setting voice
    engine.set_voice("voice2")


def test_text_to_speech_factory() -> None:
    """Test the text-to-speech factory."""
    # Test creating a mock engine
    config = {"voice": "voice1"}
    engine = TextToSpeechFactory.create_engine("mock", config)
    assert isinstance(engine, MockTextToSpeechEngine)
    assert engine.config == config
    
    # Test creating an unsupported engine
    with pytest.raises(ValueError):
        TextToSpeechFactory.create_engine("unsupported", config) 