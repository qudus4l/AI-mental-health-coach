"""API endpoints for user dashboard data."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
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