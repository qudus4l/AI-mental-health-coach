"""Models for clinical assessments and mood tracking.

This module defines the database models for standardized mental health 
assessments (GAD-7, PHQ-9) and mood ratings, which are essential for 
tracking therapeutic progress and risk assessment.
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from src.mental_health_coach.database import Base


class AssessmentType(str, Enum):
    """Types of standardized assessments used in the application."""
    
    GAD7 = "gad7"  # Generalized Anxiety Disorder 7-item scale
    PHQ9 = "phq9"  # Patient Health Questionnaire 9-item scale
    MOOD = "mood"  # Simple mood rating (1-10)
    
    
class Assessment(Base):
    """Model for storing clinical assessment results.
    
    This model stores the results of standardized assessments like
    GAD-7 for anxiety and PHQ-9 for depression, as well as simple
    mood ratings. These are essential for tracking therapeutic progress
    and guiding intervention selection.
    
    Attributes:
        id: Unique identifier for the assessment.
        user_id: ID of the user who completed the assessment.
        type: Type of assessment (GAD-7, PHQ-9, MOOD).
        score: Overall score of the assessment.
        taken_at: When the assessment was taken.
        conversation_id: Optional link to conversation where assessment was taken.
        responses: JSON-serialized individual question responses (for GAD-7/PHQ-9).
        notes: Optional clinical notes about the assessment.
    """
    
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(10), nullable=False)
    score = Column(Float, nullable=False)
    taken_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    responses = Column(Text, nullable=True)  # JSON string of individual responses
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    conversation = relationship("Conversation", back_populates="assessments")


class SessionMoodRating(Base):
    """Model for tracking mood before and after therapy sessions.
    
    This model captures mood ratings at the start and end of formal
    therapy sessions, allowing for immediate impact assessment.
    
    Attributes:
        id: Unique identifier for the mood rating entry.
        conversation_id: ID of the formal session conversation.
        user_id: ID of the user.
        mood_before: Mood rating (1-10) at the start of the session.
        mood_after: Mood rating (1-10) at the end of the session.
        notes: Optional notes about mood changes.
    """
    
    __tablename__ = "session_mood_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_before = Column(Integer, nullable=False)
    mood_after = Column(Integer, nullable=True)  # May be null if session not completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="mood_rating")
    user = relationship("User", back_populates="mood_ratings") 