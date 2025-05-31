"""Tests for the audio I/O module."""

from typing import TYPE_CHECKING
import os
import tempfile
import time

import pytest

from src.mental_health_coach.voice.audio_io import (
    AudioIOFactory,
    MockAudioRecorder,
    MockAudioPlayer,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


def test_mock_audio_recorder() -> None:
    """Test the mock audio recorder."""
    # Create a mock recorder
    config = {"sample_rate": 16000}
    recorder = MockAudioRecorder(config)
    
    # Check that the config was stored
    assert recorder.config == config
    
    # Check initial state
    assert not recorder.is_recording()
    
    # Test recording
    recorder.start_recording()
    assert recorder.is_recording()
    
    # Test stopping recording
    audio_data = recorder.stop_recording()
    assert isinstance(audio_data, bytes)
    assert not recorder.is_recording()
    
    # Test saving recording
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        recorder.save_recording(temp_path)
        assert os.path.exists(temp_path)
        assert os.path.getsize(temp_path) > 0  # File should not be empty
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_mock_audio_player() -> None:
    """Test the mock audio player."""
    # Create a mock player
    config = {"volume": 0.8}
    player = MockAudioPlayer(config)
    
    # Check that the config was stored
    assert player.config == config
    
    # Check initial state
    assert not player.is_playing()
    
    # Test playing audio
    player.play_audio(b"mock audio data")
    assert player.is_playing()
    
    # Wait for playback to complete (mock player completes after 0.5 seconds)
    time.sleep(0.6)
    assert not player.is_playing()
    
    # Test playing a file
    player.play_file("mock_file.wav")
    assert player.is_playing()
    
    # Test stopping playback
    player.stop_playback()
    assert not player.is_playing()


def test_audio_io_factory() -> None:
    """Test the audio I/O factory."""
    # Test creating a mock recorder
    recorder_config = {"sample_rate": 16000}
    recorder = AudioIOFactory.create_recorder("mock", recorder_config)
    assert isinstance(recorder, MockAudioRecorder)
    assert recorder.config == recorder_config
    
    # Test creating a mock player
    player_config = {"volume": 0.8}
    player = AudioIOFactory.create_player("mock", player_config)
    assert isinstance(player, MockAudioPlayer)
    assert player.config == player_config
    
    # Test creating unsupported types
    with pytest.raises(ValueError):
        AudioIOFactory.create_recorder("unsupported", {})
    
    with pytest.raises(ValueError):
        AudioIOFactory.create_player("unsupported", {}) 