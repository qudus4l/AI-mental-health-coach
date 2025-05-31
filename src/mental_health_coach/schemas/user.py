"""Pydantic schemas for user-related operations."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base schema for user data.
    
    Attributes:
        email: User's email address.
        first_name: User's first name.
        last_name: User's last name.
    """
    
    email: EmailStr = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")


class UserCreate(UserBase):
    """Schema for creating a new user.
    
    Attributes:
        password: User's password (plain text, will be hashed).
    """
    
    password: str = Field(..., description="Password (will be hashed)")


class UserProfileBase(BaseModel):
    """Base schema for a user profile."""

    age: Optional[int] = Field(None, description="User age")
    location: Optional[str] = Field(None, description="User location")
    anxiety_score: Optional[int] = Field(None, description="Initial anxiety assessment score (1-10)")
    depression_score: Optional[int] = Field(None, description="Initial depression assessment score (1-10)")
    communication_preference: Optional[str] = Field(None, description="Preferred communication method (text/voice)")
    session_frequency: Optional[int] = Field(None, description="Preferred session frequency per week")


class UserProfileCreate(UserProfileBase):
    """Schema for creating a new user profile."""
    
    pass


class UserProfileUpdate(UserProfileBase):
    """Schema for updating a user profile."""
    
    pass


class UserProfile(UserProfileBase):
    """Schema for user profile data.
    
    Attributes:
        id: Primary key for the profile.
        user_id: Primary key for the user.
        created_at: Timestamp when the profile was created.
        updated_at: Timestamp when the profile was last updated.
    """
    
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Profile ID")
    user_id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="When the profile was created")
    updated_at: datetime = Field(..., description="When the profile was last updated")


class SessionScheduleBase(BaseModel):
    """Base schema for session schedule data.
    
    Attributes:
        day_of_week: Day of the week for the session (0-6 for Monday-Sunday).
        hour: Hour of the day for the session (0-23).
        minute: Minute of the hour for the session (0-59).
    """
    
    day_of_week: int = Field(..., description="Day of the week (0-6, where 0 is Monday)")
    hour: int = Field(..., description="Hour of the day (0-23)")
    minute: int = Field(..., description="Minute of the hour (0-59)")


class SessionScheduleCreate(SessionScheduleBase):
    """Schema for creating a new session schedule."""
    
    pass


class SessionSchedule(SessionScheduleBase):
    """Schema for session schedule data.
    
    Attributes:
        id: Primary key for the schedule entry.
        user_id: Primary key for the user.
        is_active: Whether this schedule entry is active.
        created_at: Timestamp when the schedule was created.
        updated_at: Timestamp when the schedule was last updated.
    """
    
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Schedule ID")
    user_id: int = Field(..., description="User ID")
    is_active: bool = Field(True, description="Whether the schedule is active")
    created_at: datetime = Field(..., description="When the schedule was created")
    updated_at: datetime = Field(..., description="When the schedule was last updated")


class User(UserBase):
    """Schema for user data.
    
    Attributes:
        id: Primary key for the user.
        is_active: Flag indicating if the user account is active.
        created_at: Timestamp when the user was created.
        updated_at: Timestamp when the user was last updated.
        profile: User profile data.
        session_schedules: List of session schedules.
    """
    
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    is_active: bool = Field(True, description="Whether the user is active")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: datetime = Field(..., description="When the user was last updated")
    profile: Optional[UserProfile] = None
    session_schedules: List[SessionSchedule] = []


class Token(BaseModel):
    """Schema for authentication token.
    
    Attributes:
        access_token: JWT token.
        token_type: Token type (always "bearer").
    """
    
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token data.
    
    Attributes:
        email: Email address from the token.
    """
    
    email: Optional[str] = None 