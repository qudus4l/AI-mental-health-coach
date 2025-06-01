"""Pydantic schemas for assessment models.

This module defines the request and response schemas for the assessment API.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class AssessmentBase(BaseModel):
    """Base schema for assessments."""
    
    type: str = Field(..., description="Type of assessment (gad7, phq9, mood)")
    score: float = Field(..., description="Overall assessment score")
    responses: Optional[Dict[str, Any]] = Field(None, description="Individual question responses")
    conversation_id: Optional[int] = Field(None, description="ID of the conversation where assessment was taken")
    notes: Optional[str] = Field(None, description="Clinical notes about the assessment")


class AssessmentCreate(AssessmentBase):
    """Schema for creating a new assessment."""
    
    @validator("type")
    def validate_assessment_type(cls, v):
        """Validate assessment type."""
        valid_types = ["gad7", "phq9", "mood"]
        if v not in valid_types:
            raise ValueError(f"Invalid assessment type: {v}. Must be one of {valid_types}")
        return v
    
    @validator("score")
    def validate_score(cls, v, values):
        """Validate score is within appropriate range for assessment type."""
        assessment_type = values.get("type")
        
        if assessment_type == "gad7" and (v < 0 or v > 21):
            raise ValueError("GAD-7 score must be between 0 and 21")
        
        if assessment_type == "phq9" and (v < 0 or v > 27):
            raise ValueError("PHQ-9 score must be between 0 and 27")
        
        if assessment_type == "mood" and (v < 1 or v > 10):
            raise ValueError("Mood score must be between 1 and 10")
        
        return v


class AssessmentResponse(AssessmentBase):
    """Schema for assessment response."""
    
    id: int = Field(..., description="Assessment ID")
    user_id: int = Field(..., description="User ID")
    taken_at: datetime = Field(..., description="When the assessment was taken")
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True


class AssessmentList(BaseModel):
    """Schema for a list of assessments."""
    
    items: List[AssessmentResponse]
    total: int


class MoodRatingBase(BaseModel):
    """Base schema for session mood ratings."""
    
    mood_before: int = Field(..., description="Mood rating (1-10) at the start of the session", ge=1, le=10)
    mood_after: Optional[int] = Field(None, description="Mood rating (1-10) at the end of the session", ge=1, le=10)
    notes: Optional[str] = Field(None, description="Notes about mood changes")


class MoodRatingCreate(MoodRatingBase):
    """Schema for creating a new mood rating."""
    
    conversation_id: int = Field(..., description="ID of the conversation (formal session)")


class MoodRatingUpdate(BaseModel):
    """Schema for updating a mood rating."""
    
    mood_after: int = Field(..., description="Mood rating (1-10) at the end of the session", ge=1, le=10)
    notes: Optional[str] = Field(None, description="Notes about mood changes")


class MoodRatingResponse(MoodRatingBase):
    """Schema for mood rating response."""
    
    id: int = Field(..., description="Mood rating ID")
    user_id: int = Field(..., description="User ID")
    conversation_id: int = Field(..., description="Conversation ID")
    created_at: datetime = Field(..., description="When the rating was created")
    updated_at: datetime = Field(..., description="When the rating was last updated")
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True


class GAD7Assessment(BaseModel):
    """Schema for GAD-7 anxiety assessment questionnaire."""
    
    q1: int = Field(..., description="Feeling nervous, anxious, or on edge", ge=0, le=3)
    q2: int = Field(..., description="Not being able to stop or control worrying", ge=0, le=3)
    q3: int = Field(..., description="Worrying too much about different things", ge=0, le=3)
    q4: int = Field(..., description="Trouble relaxing", ge=0, le=3)
    q5: int = Field(..., description="Being so restless that it's hard to sit still", ge=0, le=3)
    q6: int = Field(..., description="Becoming easily annoyed or irritable", ge=0, le=3)
    q7: int = Field(..., description="Feeling afraid as if something awful might happen", ge=0, le=3)
    
    @property
    def total_score(self) -> int:
        """Calculate the total GAD-7 score."""
        return self.q1 + self.q2 + self.q3 + self.q4 + self.q5 + self.q6 + self.q7
    
    @property
    def responses_dict(self) -> Dict[str, int]:
        """Get responses as a dictionary."""
        return {
            "q1": self.q1,
            "q2": self.q2,
            "q3": self.q3,
            "q4": self.q4,
            "q5": self.q5,
            "q6": self.q6,
            "q7": self.q7,
        }


class PHQ9Assessment(BaseModel):
    """Schema for PHQ-9 depression assessment questionnaire."""
    
    q1: int = Field(..., description="Little interest or pleasure in doing things", ge=0, le=3)
    q2: int = Field(..., description="Feeling down, depressed, or hopeless", ge=0, le=3)
    q3: int = Field(..., description="Trouble falling/staying asleep, sleeping too much", ge=0, le=3)
    q4: int = Field(..., description="Feeling tired or having little energy", ge=0, le=3)
    q5: int = Field(..., description="Poor appetite or overeating", ge=0, le=3)
    q6: int = Field(..., description="Feeling bad about yourself", ge=0, le=3)
    q7: int = Field(..., description="Trouble concentrating on things", ge=0, le=3)
    q8: int = Field(..., description="Moving or speaking slowly/being fidgety or restless", ge=0, le=3)
    q9: int = Field(..., description="Thoughts that you would be better off dead", ge=0, le=3)
    
    @property
    def total_score(self) -> int:
        """Calculate the total PHQ-9 score."""
        return self.q1 + self.q2 + self.q3 + self.q4 + self.q5 + self.q6 + self.q7 + self.q8 + self.q9
    
    @property
    def responses_dict(self) -> Dict[str, int]:
        """Get responses as a dictionary."""
        return {
            "q1": self.q1,
            "q2": self.q2,
            "q3": self.q3,
            "q4": self.q4,
            "q5": self.q5,
            "q6": self.q6,
            "q7": self.q7,
            "q8": self.q8,
            "q9": self.q9,
        }


class AssessmentTrend(BaseModel):
    """Schema for assessment trend data."""
    
    date: str = Field(..., description="Date of assessment (YYYY-MM-DD)")
    score: float = Field(..., description="Assessment score")


class AssessmentTrendList(BaseModel):
    """Schema for a list of assessment trend data points."""
    
    items: List[AssessmentTrend]
    assessment_type: str = Field(..., description="Type of assessment (gad7, phq9, mood)")


class MoodTrendPoint(BaseModel):
    """Schema for a single mood trend data point."""
    
    date: str = Field(..., description="Date of mood rating (YYYY-MM-DD)")
    score: float = Field(..., description="Mood score (1-10)")
    type: str = Field(..., description="Type of mood measurement (session_before, session_after, assessment)")


class MoodTrendResponse(BaseModel):
    """Schema for mood trend response."""
    
    trends: List[MoodTrendPoint] = Field(..., description="List of mood trend data points")
    avg_session_improvement: float = Field(..., description="Average mood improvement during sessions")
    total_measurements: int = Field(..., description="Total number of mood measurements")
    most_recent_mood: Optional[float] = Field(None, description="Most recent mood score")
    most_recent_date: Optional[str] = Field(None, description="Date of most recent mood measurement")


class RiskScoreResponse(BaseModel):
    """Schema for risk score response."""
    
    composite_score: float = Field(..., description="Composite risk score (0-100)")
    anxiety_score: float = Field(..., description="GAD-7 anxiety score (0-21)")
    depression_score: float = Field(..., description="PHQ-9 depression score (0-27)")
    risk_level: str = Field(..., description="Risk level (low, mild, moderate, severe, unknown)")
    has_recent_data: bool = Field(..., description="Whether recent assessment data is available")
    anxiety_date: Optional[str] = Field(None, description="Date of most recent anxiety assessment")
    depression_date: Optional[str] = Field(None, description="Date of most recent depression assessment") 