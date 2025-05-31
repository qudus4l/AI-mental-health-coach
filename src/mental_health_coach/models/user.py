"""User models for the mental health coach application."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.mental_health_coach.models.base import Base


class User(Base):
    """User model representing application users.
    
    This model stores user authentication information, basic profile data,
    and references to associated entities like conversations and homework.
    
    Attributes:
        id: Primary key for the user.
        email: User's email address, used for authentication.
        hashed_password: Securely hashed password.
        first_name: User's first name.
        last_name: User's last name.
        is_active: Flag indicating if the user account is active.
        created_at: Timestamp when the user was created.
        updated_at: Timestamp when the user was last updated.
        conversations: List of conversations associated with this user.
        important_memories: List of important memories for this user.
        homework_assignments: List of homework assignments for this user.
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    important_memories = relationship("ImportantMemory", back_populates="user")
    homework_assignments = relationship("HomeworkAssignment", back_populates="user")


class UserProfile(Base):
    """Extended user profile information.
    
    Stores additional user information including demographic data and 
    mental health preferences.
    
    Attributes:
        id: Primary key for the profile.
        user_id: Foreign key reference to the associated user.
        age: User's age.
        location: User's location (for providing localized crisis resources).
        anxiety_score: Initial GAD-7 anxiety assessment score.
        depression_score: Initial PHQ-9 depression assessment score.
        communication_preference: Preferred communication method (voice/text).
        session_frequency: Preferred frequency of formal sessions.
        created_at: Timestamp when the profile was created.
        updated_at: Timestamp when the profile was last updated.
        user: Reference to the associated User object.
    """
    
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    age = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    anxiety_score = Column(Integer, nullable=True)
    depression_score = Column(Integer, nullable=True)
    communication_preference = Column(String, default="text")  # text, voice, both
    session_frequency = Column(Integer, default=2)  # sessions per week
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="profile", uselist=False)


class SessionSchedule(Base):
    """User's scheduled therapy sessions.
    
    Tracks when formal therapy sessions are scheduled for each user.
    
    Attributes:
        id: Primary key for the schedule entry.
        user_id: Foreign key reference to the associated user.
        day_of_week: Day of the week for the session (0-6 for Monday-Sunday).
        hour: Hour of the day for the session (0-23).
        minute: Minute of the hour for the session (0-59).
        is_active: Whether this schedule entry is active.
        created_at: Timestamp when the schedule was created.
        updated_at: Timestamp when the schedule was last updated.
        user: Reference to the associated User object.
    """
    
    __tablename__ = "session_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day_of_week = Column(Integer)  # 0-6 for Monday-Sunday
    hour = Column(Integer)  # 0-23
    minute = Column(Integer)  # 0-59
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="session_schedules") 