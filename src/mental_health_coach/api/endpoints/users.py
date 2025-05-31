"""API endpoints for user management."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import (
    get_current_active_user,
    get_password_hash,
)
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.user import User, UserProfile, SessionSchedule
from src.mental_health_coach.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserProfile as UserProfileSchema,
    UserProfileCreate,
    UserProfileUpdate,
    SessionSchedule as SessionScheduleSchema,
    SessionScheduleCreate,
)

router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """Create a new user.
    
    Args:
        user_in: User creation data.
        db: Database session.
        
    Returns:
        UserSchema: The created user.
        
    Raises:
        HTTPException: If a user with the given email already exists.
    """
    # Check if user with this email already exists
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserSchema)
def read_current_user(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get the current authenticated user.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        UserSchema: The current user.
    """
    return current_user


@router.post("/me/profile", response_model=UserProfileSchema)
def create_user_profile(
    profile_in: UserProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a profile for the current user.
    
    Args:
        profile_in: Profile creation data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        UserProfileSchema: The created profile.
        
    Raises:
        HTTPException: If the user already has a profile.
    """
    # Check if user already has a profile
    if hasattr(current_user, "profile") and current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a profile",
        )
    
    # Create new profile
    db_profile = UserProfile(
        user_id=current_user.id,
        age=profile_in.age,
        location=profile_in.location,
        anxiety_score=profile_in.anxiety_score,
        depression_score=profile_in.depression_score,
        communication_preference=profile_in.communication_preference,
        session_frequency=profile_in.session_frequency,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.put("/me/profile", response_model=UserProfileSchema)
def update_user_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update the current user's profile.
    
    Args:
        profile_in: Profile update data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        UserProfileSchema: The updated profile.
        
    Raises:
        HTTPException: If the profile does not exist.
    """
    # Check if profile exists
    db_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )
    
    # Update profile
    profile_data = profile_in.model_dump(exclude_unset=True)
    for key, value in profile_data.items():
        setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.post("/me/schedule", response_model=SessionScheduleSchema, status_code=status.HTTP_201_CREATED)
def create_session_schedule(
    schedule_in: SessionScheduleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new session schedule for the current user.
    
    Args:
        schedule_in: Session schedule creation data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        SessionScheduleSchema: The created session schedule.
    """
    # Validate the schedule data
    if not (0 <= schedule_in.day_of_week <= 6):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Day of week must be between 0 (Monday) and 6 (Sunday)",
        )
    
    if not (0 <= schedule_in.hour <= 23):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hour must be between 0 and 23",
        )
    
    if not (0 <= schedule_in.minute <= 59):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minute must be between 0 and 59",
        )
    
    # Create new session schedule
    db_schedule = SessionSchedule(
        user_id=current_user.id,
        day_of_week=schedule_in.day_of_week,
        hour=schedule_in.hour,
        minute=schedule_in.minute,
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.get("/me/schedule", response_model=List[SessionScheduleSchema])
def read_session_schedules(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get all session schedules for the current user.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List[SessionScheduleSchema]: List of session schedules.
    """
    schedules = (
        db.query(SessionSchedule)
        .filter(SessionSchedule.user_id == current_user.id, SessionSchedule.is_active == True)
        .order_by(SessionSchedule.day_of_week, SessionSchedule.hour, SessionSchedule.minute)
        .all()
    )
    return schedules


@router.put("/me/schedule/{schedule_id}", response_model=SessionScheduleSchema)
def update_session_schedule(
    schedule_id: int,
    schedule_in: SessionScheduleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update a session schedule.
    
    Args:
        schedule_id: ID of the schedule to update.
        schedule_in: Session schedule update data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        SessionScheduleSchema: The updated session schedule.
        
    Raises:
        HTTPException: If the schedule does not exist or does not belong to the user.
    """
    # Get the schedule
    db_schedule = db.query(SessionSchedule).filter(SessionSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session schedule not found",
        )
    
    if db_schedule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Validate the schedule data
    if not (0 <= schedule_in.day_of_week <= 6):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Day of week must be between 0 (Monday) and 6 (Sunday)",
        )
    
    if not (0 <= schedule_in.hour <= 23):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hour must be between 0 and 23",
        )
    
    if not (0 <= schedule_in.minute <= 59):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minute must be between 0 and 59",
        )
    
    # Update schedule fields
    db_schedule.day_of_week = schedule_in.day_of_week
    db_schedule.hour = schedule_in.hour
    db_schedule.minute = schedule_in.minute
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.delete("/me/schedule/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_session_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a session schedule.
    
    Args:
        schedule_id: ID of the schedule to delete.
        current_user: The current authenticated user.
        db: Database session.
        
    Raises:
        HTTPException: If the schedule does not exist or does not belong to the user.
    """
    # Get the schedule
    db_schedule = db.query(SessionSchedule).filter(SessionSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session schedule not found",
        )
    
    if db_schedule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Instead of hard delete, mark as inactive
    db_schedule.is_active = False
    db.commit() 