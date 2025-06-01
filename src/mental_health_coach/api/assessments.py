"""API endpoints for clinical assessments and mood ratings.

This module provides API endpoints for submitting, retrieving, and analyzing
standardized clinical assessments (GAD-7, PHQ-9) and mood ratings.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.user import User
from src.mental_health_coach.api.auth import get_current_active_user
from src.mental_health_coach.models.assessment import AssessmentType
from src.mental_health_coach.services.assessment_service import AssessmentService
from src.mental_health_coach.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentList,
    AssessmentTrendList,
    GAD7Assessment,
    PHQ9Assessment,
    MoodRatingCreate,
    MoodRatingUpdate,
    MoodRatingResponse,
    MoodTrendResponse,
    RiskScoreResponse,
)

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment: AssessmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new assessment record.
    
    This endpoint creates a new assessment record for the authenticated user.
    
    Args:
        assessment: Assessment data to create.
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        The created assessment.
    """
    service = AssessmentService(db)
    
    created_assessment = service.create_assessment(
        user_id=current_user.id,
        assessment_type=assessment.type,
        score=assessment.score,
        responses=assessment.responses,
        conversation_id=assessment.conversation_id,
        notes=assessment.notes,
    )
    
    return created_assessment


@router.post("/gad7", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def submit_gad7_assessment(
    assessment: GAD7Assessment,
    conversation_id: Optional[int] = None,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit a GAD-7 anxiety assessment.
    
    This endpoint provides a structured way to submit the GAD-7 anxiety
    assessment questionnaire.
    
    Args:
        assessment: GAD-7 assessment data.
        conversation_id: Optional conversation ID where assessment was taken.
        notes: Optional clinical notes.
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        The created assessment.
    """
    service = AssessmentService(db)
    
    created_assessment = service.create_assessment(
        user_id=current_user.id,
        assessment_type=AssessmentType.GAD7.value,
        score=assessment.total_score,
        responses=assessment.responses_dict,
        conversation_id=conversation_id,
        notes=notes,
    )
    
    return created_assessment


@router.post("/phq9", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def submit_phq9_assessment(
    assessment: PHQ9Assessment,
    conversation_id: Optional[int] = None,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit a PHQ-9 depression assessment.
    
    This endpoint provides a structured way to submit the PHQ-9 depression
    assessment questionnaire.
    
    Args:
        assessment: PHQ-9 assessment data.
        conversation_id: Optional conversation ID where assessment was taken.
        notes: Optional clinical notes.
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        The created assessment.
    """
    service = AssessmentService(db)
    
    created_assessment = service.create_assessment(
        user_id=current_user.id,
        assessment_type=AssessmentType.PHQ9.value,
        score=assessment.total_score,
        responses=assessment.responses_dict,
        conversation_id=conversation_id,
        notes=notes,
    )
    
    return created_assessment


@router.get("/", response_model=AssessmentList)
async def get_assessments(
    assessment_type: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get assessments for the current user.
    
    This endpoint retrieves assessments for the authenticated user,
    with optional filtering by assessment type.
    
    Args:
        assessment_type: Optional filter by assessment type.
        limit: Maximum number of assessments to return.
        skip: Number of assessments to skip (for pagination).
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        List of assessments and total count.
    """
    service = AssessmentService(db)
    
    assessments = service.get_user_assessments(
        user_id=current_user.id,
        assessment_type=assessment_type,
        limit=limit,
        skip=skip,
    )
    
    # Count total assessments for pagination
    query = db.query(AssessmentService)
    if assessment_type:
        query = query.filter_by(type=assessment_type)
    total = query.count()
    
    return {"items": assessments, "total": total}


@router.get("/latest/{assessment_type}", response_model=AssessmentResponse)
async def get_latest_assessment(
    assessment_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the most recent assessment of a specific type.
    
    This endpoint retrieves the most recent assessment of the specified type
    for the authenticated user.
    
    Args:
        assessment_type: Type of assessment to retrieve.
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        The most recent assessment.
    """
    service = AssessmentService(db)
    
    assessment = service.get_latest_assessment(
        user_id=current_user.id,
        assessment_type=assessment_type,
    )
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {assessment_type} assessment found for user",
        )
    
    return assessment


@router.get("/trends/{assessment_type}", response_model=AssessmentTrendList)
async def get_assessment_trends(
    assessment_type: str,
    days: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trends for a specific assessment type over time.
    
    This endpoint retrieves trend data for the specified assessment type
    over the specified time period.
    
    Args:
        assessment_type: Type of assessment to analyze.
        days: Number of days to look back.
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        List of assessment trend data points.
    """
    service = AssessmentService(db)
    
    trends = service.get_assessment_trends(
        user_id=current_user.id,
        assessment_type=assessment_type,
        days=days,
    )
    
    return {"items": trends, "assessment_type": assessment_type}


@router.get("/risk-score", response_model=RiskScoreResponse)
async def get_risk_score(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Calculate a composite risk score based on recent assessments.
    
    This endpoint calculates a risk score based on the user's recent
    GAD-7 and PHQ-9 assessments.
    
    Args:
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        Risk score information.
    """
    service = AssessmentService(db)
    
    risk_score = service.calculate_risk_score(user_id=current_user.id)
    
    return risk_score


@router.post("/mood-ratings", response_model=MoodRatingResponse, status_code=status.HTTP_201_CREATED)
async def create_mood_rating(
    mood_rating: MoodRatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a mood rating for a therapy session.
    
    This endpoint creates a new mood rating for a formal therapy session.
    
    Args:
        mood_rating: Mood rating data to create.
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        The created mood rating.
    """
    service = AssessmentService(db)
    
    created_rating = service.create_session_mood_rating(
        user_id=current_user.id,
        conversation_id=mood_rating.conversation_id,
        mood_before=mood_rating.mood_before,
        mood_after=mood_rating.mood_after,
        notes=mood_rating.notes,
    )
    
    return created_rating


@router.put("/mood-ratings/{mood_rating_id}", response_model=MoodRatingResponse)
async def update_mood_rating(
    mood_rating_id: int,
    mood_update: MoodRatingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update the mood rating at the end of a session.
    
    This endpoint updates an existing mood rating with the post-session
    mood score.
    
    Args:
        mood_rating_id: ID of the mood rating to update.
        mood_update: Updated mood rating data.
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        The updated mood rating.
    """
    service = AssessmentService(db)
    
    try:
        updated_rating = service.update_session_mood_after(
            mood_rating_id=mood_rating_id,
            mood_after=mood_update.mood_after,
            notes=mood_update.notes,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
    return updated_rating


@router.get("/mood-trends", response_model=MoodTrendResponse)
async def get_mood_trends(
    days: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get mood trends for the current user over time.
    
    This endpoint retrieves mood trend data from session ratings and
    mood assessments over the specified time period.
    
    Args:
        days: Number of days to look back.
        current_user: Currently authenticated user.
        db: Database session.
        
    Returns:
        Mood trend information.
    """
    service = AssessmentService(db)
    
    trends = service.get_mood_trends(
        user_id=current_user.id,
        days=days,
    )
    
    return trends 