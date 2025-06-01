"""Unit tests for the assessment service.

This module contains tests for the AssessmentService class.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.mental_health_coach.models.assessment import AssessmentType

# Create a test module to patch
class MockAssessment:
    """Mock Assessment class for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@patch('src.mental_health_coach.services.assessment_service.Assessment', MockAssessment)
class TestAssessmentService:
    """Tests for the AssessmentService class."""
    
    def setup_method(self):
        """Setup test environment."""
        # Import here to apply patch
        from src.mental_health_coach.services.assessment_service import AssessmentService
        self.AssessmentService = AssessmentService
    
    def test_create_assessment(self):
        """Test creating an assessment."""
        # Setup
        mock_db = Mock()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Create service with mock DB
        service = self.AssessmentService(mock_db)
        
        # Call method
        result = service.create_assessment(
            user_id=1,
            assessment_type=AssessmentType.GAD7.value,
            score=10.0,
            responses={"q1": 2, "q2": 1},
            notes="Test notes",
        )
        
        # Verify DB interactions
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
        
        # Verify assessment properties
        assert result.user_id == 1
        assert result.type == AssessmentType.GAD7.value
        assert result.score == 10.0
        assert json.loads(result.responses) == {"q1": 2, "q2": 1}
        assert result.notes == "Test notes"
    
    def test_invalid_assessment_type(self):
        """Test creating an assessment with invalid type raises error."""
        # Setup
        mock_db = Mock()
        service = self.AssessmentService(mock_db)
        
        # Verify error is raised
        with pytest.raises(ValueError):
            service.create_assessment(
                user_id=1,
                assessment_type="invalid_type",
                score=10.0,
            )
    
    @patch('src.mental_health_coach.services.assessment_service.AssessmentService.get_latest_assessment')
    def test_calculate_risk_score(self, mock_get_latest):
        """Test calculating risk score from assessments."""
        # Setup
        mock_db = Mock()
        service = self.AssessmentService(mock_db)
        
        # Set up mock return values for GAD-7 and PHQ-9
        gad7_mock = Mock()
        gad7_mock.score = 15.0
        gad7_mock.taken_at = datetime.utcnow()
        
        phq9_mock = Mock()
        phq9_mock.score = 12.0
        phq9_mock.taken_at = datetime.utcnow()
        
        # Configure the mock to return different values for different calls
        mock_get_latest.side_effect = lambda user_id, assessment_type: {
            AssessmentType.GAD7.value: gad7_mock,
            AssessmentType.PHQ9.value: phq9_mock,
        }.get(assessment_type)
        
        # Call method
        risk_score = service.calculate_risk_score(user_id=1)
        
        # Verify results
        assert risk_score["anxiety_score"] == 15.0
        assert risk_score["depression_score"] == 12.0
        assert risk_score["has_recent_data"] is True
        
        # Calculate expected score
        # Anxiety: 15/21 = 0.714 * 100 = 71.4%
        # Depression: 12/27 = 0.444 * 100 = 44.4%
        # Average: (71.4 + 44.4) / 2 = 57.9%
        expected_score = ((15.0 / 21.0) * 100 + (12.0 / 27.0) * 100) / 2
        assert risk_score["composite_score"] == expected_score
        assert risk_score["risk_level"] == "moderate"  # Based on composite score 