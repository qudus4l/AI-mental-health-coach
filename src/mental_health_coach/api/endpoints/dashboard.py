"""API endpoints for user dashboard data."""

from typing import Any, Dict, List
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_current_active_user
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.user import User
from src.mental_health_coach.services.dashboard import DashboardService

router = APIRouter()


@router.get("/me")
def get_dashboard_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get dashboard data for the current user.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Dashboard data including session stats, homework stats,
              engagement metrics, and progress over time.
    """
    # Create dashboard service
    dashboard_service = DashboardService(db=db, user=current_user)
    
    # Get dashboard data
    dashboard_data = dashboard_service.get_dashboard_data()
    
    return dashboard_data


@router.get("/me/session-stats")
def get_session_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get session statistics for the current user.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Session statistics.
    """
    dashboard_service = DashboardService(db=db, user=current_user)
    return dashboard_service.get_session_stats()


@router.get("/me/homework-stats")
def get_homework_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get homework statistics for the current user.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Homework statistics.
    """
    dashboard_service = DashboardService(db=db, user=current_user)
    return dashboard_service.get_homework_stats()


@router.get("/me/engagement-metrics")
def get_engagement_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get engagement metrics for the current user.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Engagement metrics.
    """
    dashboard_service = DashboardService(db=db, user=current_user)
    return dashboard_service.get_engagement_metrics()


@router.get("/me/progress-over-time")
def get_progress_over_time(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get progress over time for the current user.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Progress data over time.
    """
    dashboard_service = DashboardService(db=db, user=current_user)
    return dashboard_service.get_progress_over_time()


@router.get("/me/upcoming-sessions")
def get_upcoming_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get upcoming scheduled sessions for the current user.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List: Upcoming sessions.
    """
    dashboard_service = DashboardService(db=db, user=current_user)
    return dashboard_service.get_upcoming_sessions() 


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get dashboard statistics.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Dashboard statistics including mood score, session count, etc.
    """
    # This would normally use the dashboard service, but for now return placeholder data
    return {
        "mood_score": 7.5,
        "total_sessions": 0,
        "completed_homework": 0,
        "streak_days": 0,
        "last_session": None,
        "next_session": None
    }


class PeriodType(str, Enum):
    """Time period options for filtering data."""
    
    week = "week"
    month = "month"
    year = "year"


@router.get("/mood-history")
def get_mood_history(
    period: PeriodType = Query(PeriodType.week, description="Time period for mood history"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get mood history data for the specified period.
    
    Args:
        period: Time period (week, month, year).
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List[Dict]: Mood history data points.
    """
    # Return placeholder data
    if period == PeriodType.week:
        return [
            {"date": "2025-05-26", "score": 6},
            {"date": "2025-05-27", "score": 6.5},
            {"date": "2025-05-28", "score": 7},
            {"date": "2025-05-29", "score": 6.5},
            {"date": "2025-05-30", "score": 7.5},
            {"date": "2025-05-31", "score": 8},
            {"date": "2025-06-01", "score": 7.5}
        ]
    elif period == PeriodType.month:
        # Return month data (simplified)
        return [
            {"date": "2025-05-01", "score": 6},
            {"date": "2025-05-08", "score": 6.5},
            {"date": "2025-05-15", "score": 7},
            {"date": "2025-05-22", "score": 7.5},
            {"date": "2025-06-01", "score": 7.5}
        ]
    else:  # year
        # Return year data (simplified)
        return [
            {"date": "2024-06-01", "score": 5},
            {"date": "2024-09-01", "score": 6},
            {"date": "2024-12-01", "score": 6.5},
            {"date": "2025-03-01", "score": 7},
            {"date": "2025-06-01", "score": 7.5}
        ]


@router.get("/recommended-exercises")
def get_recommended_exercises(
    limit: int = Query(3, ge=1, le=10, description="Number of exercises to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get recommended exercises based on user's profile and progress.
    
    Args:
        limit: Maximum number of exercises to return.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List[Dict]: Recommended exercises.
    """
    # Return placeholder data
    exercises = [
        {
            "id": 1,
            "title": "5-Minute Mindful Breathing",
            "description": "A quick breathing exercise to reduce anxiety and center yourself.",
            "duration_minutes": 5,
            "difficulty": "easy",
            "category": "mindfulness"
        },
        {
            "id": 2,
            "title": "Gratitude Journaling",
            "description": "Write down three things you're grateful for today.",
            "duration_minutes": 10,
            "difficulty": "easy",
            "category": "reflection"
        },
        {
            "id": 3,
            "title": "Progressive Muscle Relaxation",
            "description": "Systematically tense and relax muscle groups to reduce physical tension.",
            "duration_minutes": 15,
            "difficulty": "medium",
            "category": "relaxation"
        },
        {
            "id": 4,
            "title": "Thought Challenging Worksheet",
            "description": "Identify and challenge negative thought patterns.",
            "duration_minutes": 20,
            "difficulty": "hard",
            "category": "cognitive"
        },
        {
            "id": 5,
            "title": "Mindful Walking",
            "description": "Practice mindfulness while taking a short walk outdoors.",
            "duration_minutes": 15,
            "difficulty": "medium",
            "category": "mindfulness"
        }
    ]
    
    # Return only the requested number of exercises
    return exercises[:limit] 