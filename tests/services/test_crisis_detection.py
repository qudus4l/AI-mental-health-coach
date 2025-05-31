"""Tests for the crisis detection service."""

from typing import TYPE_CHECKING, Dict, List, Any
from unittest.mock import MagicMock, patch

import pytest

from src.mental_health_coach.services.crisis_detection import CrisisDetector

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


def test_detect_crisis_with_suicide_keywords() -> None:
    """Test crisis detection with suicide-related keywords."""
    detector = CrisisDetector()
    
    # Test with suicide-related content
    message = "I've been thinking about suicide a lot lately. I don't see a reason to live anymore."
    is_crisis, categories, resources, analysis_details = detector.detect_crisis(message)
    
    assert is_crisis is True
    assert "suicide" in categories
    assert any("Suicide" in resource["name"] for resource in resources)
    assert "risk_level" in analysis_details


def test_detect_crisis_with_multiple_categories() -> None:
    """Test crisis detection with keywords from multiple categories."""
    detector = CrisisDetector()
    
    # Test with content that hits multiple categories
    message = (
        "I've been feeling so hopeless and worthless. I've been drinking too much "
        "to cope and sometimes think about hurting myself."
    )
    is_crisis, categories, resources, analysis_details = detector.detect_crisis(message)
    
    assert is_crisis is True
    assert "self_harm" in categories
    assert "severe_depression" in categories
    assert "substance_abuse" in categories
    assert len(categories) >= 3
    assert len(resources) >= 3
    assert "risk_level" in analysis_details


def test_detect_crisis_with_no_crisis() -> None:
    """Test crisis detection with non-crisis content."""
    detector = CrisisDetector()
    
    # Test with non-crisis content
    message = "I've been feeling a bit down today, but I'm managing okay. Just wanted to talk."
    is_crisis, categories, resources, analysis_details = detector.detect_crisis(message)
    
    assert is_crisis is False
    assert len(categories) == 0
    assert len(resources) == 0
    assert "risk_level" in analysis_details


def test_detect_crisis_with_context() -> None:
    """Test crisis detection with message history and user profile context."""
    detector = CrisisDetector()
    
    # Test with a message that contains a direct crisis keyword
    message = "I want to kill myself"
    
    # This should trigger as a crisis even without context
    is_crisis1, categories1, _, _ = detector.detect_crisis(message)
    assert is_crisis1 is True
    assert "suicide" in categories1
    
    # With additional context
    message_history = [
        "I've been feeling worse every day",
        "Nothing seems to help with my depression",
        "I can't sleep and have no appetite",
    ]
    
    user_profile = {
        "depression_score": 9,  # High depression score
        "anxiety_score": 7,
    }
    
    # Should still detect crisis with additional context
    is_crisis2, categories2, resources, analysis_details = detector.detect_crisis(
        message, message_history, user_profile
    )
    
    assert is_crisis2 is True
    assert "suicide" in categories2
    assert len(resources) > 0
    # Check that analysis details include expected fields
    assert "risk_level" in analysis_details
    assert "confidence_score" in analysis_details


def test_get_crisis_response() -> None:
    """Test generating crisis responses."""
    detector = CrisisDetector()
    
    # Test response for suicide
    suicide_response = detector.get_crisis_response(
        ["suicide"], {"risk_level": "high", "confidence_score": 0.9}
    )
    assert "suicide" in suicide_response.lower()
    assert "crisis helpline" in suicide_response.lower()
    
    # Test response for self-harm
    self_harm_response = detector.get_crisis_response(
        ["self_harm"], {"risk_level": "medium", "confidence_score": 0.7}
    )
    assert "self-harm" in self_harm_response.lower()
    assert "coping strategies" in self_harm_response.lower()
    
    # Test response for multiple categories
    multi_response = detector.get_crisis_response(
        ["severe_depression", "substance_abuse"],
        {"risk_level": "medium", "confidence_score": 0.6}
    )
    assert "depression" in multi_response.lower()
    assert "substance" in multi_response.lower()


def test_format_resources() -> None:
    """Test formatting emergency resources."""
    detector = CrisisDetector()
    
    # Create test resources
    resources = [
        {
            "name": "Test Resource 1",
            "contact": "123-456-7890",
            "description": "Test description 1",
        },
        {
            "name": "Test Resource 2",
            "contact": "test@example.com",
            "description": "Test description 2",
        },
    ]
    
    # Format resources
    formatted = detector.format_resources(resources)
    
    # Check formatting
    assert "Emergency Resources:" in formatted
    assert "Test Resource 1" in formatted
    assert "123-456-7890" in formatted
    assert "Test Resource 2" in formatted
    assert "test@example.com" in formatted
    
    # Test with empty resources
    empty_formatted = detector.format_resources([])
    assert empty_formatted == ""


def test_custom_crisis_keywords() -> None:
    """Test using custom crisis keywords."""
    custom_keywords = {
        "custom_category": ["unique_keyword", "special_phrase"],
    }
    
    detector = CrisisDetector(crisis_keywords=custom_keywords)
    
    # Test with custom keywords
    message = "This contains a unique_keyword that should trigger detection."
    is_crisis, categories, resources, analysis_details = detector.detect_crisis(message)
    
    assert is_crisis is True
    assert "custom_category" in categories
    
    # Test with non-matching message
    non_matching = "This doesn't contain any trigger words."
    is_crisis2, categories2, _, _ = detector.detect_crisis(non_matching)
    
    assert is_crisis2 is False
    assert len(categories2) == 0


def test_custom_emergency_resources() -> None:
    """Test using custom emergency resources."""
    custom_resources = {
        "custom_category": [
            {
                "name": "Custom Helpline",
                "contact": "999-999-9999",
                "description": "A custom helpline",
            }
        ],
        "general": [
            {
                "name": "General Help",
                "contact": "111-111-1111",
                "description": "General help resource",
            }
        ],
    }
    
    custom_keywords = {
        "custom_category": ["test_keyword"],
    }
    
    detector = CrisisDetector(
        crisis_keywords=custom_keywords,
        emergency_resources=custom_resources,
    )
    
    # Test with custom category
    message = "This contains test_keyword that should trigger custom resources."
    is_crisis, categories, resources, _ = detector.detect_crisis(message)
    
    assert is_crisis is True
    assert "custom_category" in categories
    assert any(resource["name"] == "Custom Helpline" for resource in resources)
    assert any(resource["name"] == "General Help" for resource in resources)


def test_historical_analysis() -> None:
    """Test historical analysis of message patterns."""
    detector = CrisisDetector()
    
    # Create a message history with increasing crisis indicators
    message_history = [
        "I'm having a hard day today.",
        "Things are getting worse for me.",
        "I feel really hopeless about everything.",
        "I don't know how much longer I can take this pain.",
    ]
    
    result = detector.get_historical_crisis_indicators(message_history)
    
    assert "pattern_found" in result
    assert "increasing_pattern" in result
    assert "persistent_categories" in result
    assert "category_persistence" in result
    assert isinstance(result["category_persistence"], dict) 