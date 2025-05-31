"""Tests for the crisis detection service."""

from typing import TYPE_CHECKING, List, Dict

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
    is_crisis, categories, resources = detector.detect_crisis(message)
    
    assert is_crisis is True
    assert "suicide" in categories
    assert len(resources) > 0
    
    # Verify resources contain suicide-specific resources
    suicide_resources = [
        r for r in resources if r in detector.emergency_resources.get("suicide", [])
    ]
    assert len(suicide_resources) > 0


def test_detect_crisis_with_multiple_categories() -> None:
    """Test crisis detection with keywords from multiple categories."""
    detector = CrisisDetector()
    
    # Test with content that hits multiple categories
    message = (
        "I've been feeling so hopeless and worthless. I've been drinking too much "
        "to cope and sometimes think about hurting myself."
    )
    is_crisis, categories, resources = detector.detect_crisis(message)
    
    assert is_crisis is True
    assert "severe_depression" in categories
    assert "substance_abuse" in categories
    assert "self_harm" in categories
    assert len(resources) > 0
    
    # Verify we have resources from multiple categories
    category_matches = set()
    for resource in resources:
        for category, category_resources in detector.emergency_resources.items():
            if resource in category_resources:
                category_matches.add(category)
    
    assert len(category_matches) >= 3  # At least 3 categories matched


def test_detect_crisis_with_no_crisis() -> None:
    """Test crisis detection with non-crisis content."""
    detector = CrisisDetector()
    
    # Test with non-crisis content
    message = "I've been feeling a bit down today, but I'm managing okay. Just wanted to talk."
    is_crisis, categories, resources = detector.detect_crisis(message)
    
    assert is_crisis is False
    assert len(categories) == 0
    assert len(resources) == 0


def test_get_crisis_response() -> None:
    """Test getting appropriate crisis responses for different categories."""
    detector = CrisisDetector()
    
    # Test response for suicide
    suicide_response = detector.get_crisis_response(["suicide"])
    assert "safety" in suicide_response.lower()
    assert "helpline" in suicide_response.lower() or "crisis" in suicide_response.lower()
    
    # Test response for depression
    depression_response = detector.get_crisis_response(["severe_depression"])
    assert "depression" in depression_response.lower()
    assert "professional support" in depression_response.lower()
    
    # Test response for multiple categories
    multi_response = detector.get_crisis_response(["suicide", "substance_abuse"])
    assert "safety" in multi_response.lower()
    assert "substance" in multi_response.lower()


def test_format_resources() -> None:
    """Test formatting of resources into a readable string."""
    detector = CrisisDetector()
    
    # Sample resources
    resources = [
        {
            "name": "Test Helpline",
            "contact": "123-456-7890",
            "description": "A test helpline for testing",
        },
        {
            "name": "Test Crisis Center",
            "contact": "test@example.com",
            "description": "A test crisis center",
        },
    ]
    
    formatted = detector.format_resources(resources)
    
    # Verify all resource information is included
    assert "Emergency Resources" in formatted
    assert "Test Helpline" in formatted
    assert "123-456-7890" in formatted
    assert "A test helpline for testing" in formatted
    assert "Test Crisis Center" in formatted
    assert "test@example.com" in formatted
    assert "A test crisis center" in formatted


def test_custom_crisis_keywords() -> None:
    """Test using custom crisis keywords."""
    custom_keywords = {
        "custom_category": ["unique_keyword", "special_phrase"],
    }
    
    detector = CrisisDetector(crisis_keywords=custom_keywords)
    
    # Test with custom keywords
    message = "This contains a unique_keyword that should trigger detection."
    is_crisis, categories, resources = detector.detect_crisis(message)
    
    assert is_crisis is True
    assert "custom_category" in categories


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
    is_crisis, categories, resources = detector.detect_crisis(message)
    
    assert is_crisis is True
    assert "custom_category" in categories
    
    # Verify custom resources are included
    assert any(r["name"] == "Custom Helpline" for r in resources)
    assert any(r["name"] == "General Help" for r in resources) 