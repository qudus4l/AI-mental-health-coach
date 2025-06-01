"""Assessment service for managing clinical assessments and mood ratings.

This module provides functionality for creating, retrieving, and analyzing
standardized clinical assessments (GAD-7, PHQ-9) and mood ratings.
"""

from typing import Dict, List, Optional, Any
import json
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation
from src.mental_health_coach.models.assessment import Assessment, SessionMoodRating, AssessmentType


class AssessmentService:
    """Service for managing clinical assessments and mood ratings.
    
    This service provides methods for creating and retrieving assessments,
    calculating risk scores, and tracking mood changes over time.
    
    Attributes:
        db: Database session.
    """
    
    def __init__(self, db: Session) -> None:
        """Initialize the assessment service.
        
        Args:
            db: Database session.
        """
        self.db = db
    
    def create_assessment(
        self,
        user_id: int,
        assessment_type: str,
        score: float,
        responses: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Assessment:
        """Create a new assessment record.
        
        Args:
            user_id: ID of the user taking the assessment.
            assessment_type: Type of assessment (GAD7, PHQ9, MOOD).
            score: Overall assessment score.
            responses: Optional dictionary of question responses.
            conversation_id: Optional ID of the conversation during which the assessment was taken.
            notes: Optional clinical notes about the assessment.
            
        Returns:
            The created Assessment object.
        """
        # Validate assessment type
        if assessment_type not in [t.value for t in AssessmentType]:
            raise ValueError(f"Invalid assessment type: {assessment_type}")
        
        # Create assessment
        assessment = Assessment(
            user_id=user_id,
            type=assessment_type,
            score=score,
            conversation_id=conversation_id,
            responses=json.dumps(responses) if responses else None,
            notes=notes,
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        return assessment
    
    def get_user_assessments(
        self,
        user_id: int,
        assessment_type: Optional[str] = None,
        limit: int = 10,
        skip: int = 0,
    ) -> List[Assessment]:
        """Get assessments for a user.
        
        Args:
            user_id: ID of the user.
            assessment_type: Optional filter by assessment type.
            limit: Maximum number of assessments to return.
            skip: Number of assessments to skip (for pagination).
            
        Returns:
            List of Assessment objects.
        """
        query = self.db.query(Assessment).filter(Assessment.user_id == user_id)
        
        if assessment_type:
            query = query.filter(Assessment.type == assessment_type)
        
        return query.order_by(desc(Assessment.taken_at)).offset(skip).limit(limit).all()
    
    def get_latest_assessment(
        self,
        user_id: int,
        assessment_type: str,
    ) -> Optional[Assessment]:
        """Get the most recent assessment of a specific type for a user.
        
        Args:
            user_id: ID of the user.
            assessment_type: Type of assessment to retrieve.
            
        Returns:
            The most recent Assessment object, or None if no assessments found.
        """
        return (
            self.db.query(Assessment)
            .filter(
                Assessment.user_id == user_id,
                Assessment.type == assessment_type,
            )
            .order_by(desc(Assessment.taken_at))
            .first()
        )
    
    def get_assessment_trends(
        self,
        user_id: int,
        assessment_type: str,
        days: int = 90,
    ) -> List[Dict[str, Any]]:
        """Get trends for a specific assessment type over time.
        
        Args:
            user_id: ID of the user.
            assessment_type: Type of assessment to analyze.
            days: Number of days to look back.
            
        Returns:
            List of dictionaries containing date and score information.
        """
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        assessments = (
            self.db.query(Assessment)
            .filter(
                Assessment.user_id == user_id,
                Assessment.type == assessment_type,
                Assessment.taken_at >= cutoff_date,
            )
            .order_by(Assessment.taken_at)
            .all()
        )
        
        return [
            {
                "date": assessment.taken_at.strftime("%Y-%m-%d"),
                "score": assessment.score,
            }
            for assessment in assessments
        ]
    
    def calculate_risk_score(self, user_id: int) -> Dict[str, Any]:
        """Calculate a composite risk score based on recent assessments.
        
        This method combines GAD-7 and PHQ-9 scores to estimate overall
        risk level for crisis intervention purposes.
        
        Args:
            user_id: ID of the user.
            
        Returns:
            Dictionary with risk score and component information.
        """
        # Get latest GAD-7 and PHQ-9 scores
        gad7 = self.get_latest_assessment(user_id, AssessmentType.GAD7.value)
        phq9 = self.get_latest_assessment(user_id, AssessmentType.PHQ9.value)
        
        # Default values if assessments don't exist
        gad7_score = 0.0
        phq9_score = 0.0
        risk_level = "unknown"
        
        # Update with actual values if available
        if gad7:
            gad7_score = gad7.score
        
        if phq9:
            phq9_score = phq9.score
        
        # Calculate combined risk score (normalized to 0-100)
        # GAD-7 max is 21, PHQ-9 max is 27
        anxiety_component = (gad7_score / 21.0) * 100.0 if gad7 else 0.0
        depression_component = (phq9_score / 27.0) * 100.0 if phq9 else 0.0
        
        # Simple weighted average (can be refined with clinical guidance)
        composite_score = (anxiety_component + depression_component) / 2.0
        
        # Determine risk level
        if composite_score >= 75.0:
            risk_level = "severe"
        elif composite_score >= 50.0:
            risk_level = "moderate"
        elif composite_score >= 25.0:
            risk_level = "mild"
        else:
            risk_level = "low"
        
        return {
            "composite_score": composite_score,
            "anxiety_score": gad7_score,
            "depression_score": phq9_score,
            "risk_level": risk_level,
            "has_recent_data": bool(gad7 or phq9),
            "anxiety_date": gad7.taken_at.strftime("%Y-%m-%d") if gad7 else None,
            "depression_date": phq9.taken_at.strftime("%Y-%m-%d") if phq9 else None,
        }
    
    def create_session_mood_rating(
        self,
        user_id: int,
        conversation_id: int,
        mood_before: int,
        mood_after: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> SessionMoodRating:
        """Create a mood rating for a therapy session.
        
        Args:
            user_id: ID of the user.
            conversation_id: ID of the conversation (formal session).
            mood_before: Mood rating (1-10) at the start of the session.
            mood_after: Optional mood rating (1-10) at the end of the session.
            notes: Optional notes about mood changes.
            
        Returns:
            The created SessionMoodRating object.
        """
        # Validate mood ratings are in range 1-10
        if mood_before < 1 or mood_before > 10:
            raise ValueError("Mood rating must be between 1 and 10")
        
        if mood_after is not None and (mood_after < 1 or mood_after > 10):
            raise ValueError("Mood rating must be between 1 and 10")
        
        # Create mood rating
        mood_rating = SessionMoodRating(
            user_id=user_id,
            conversation_id=conversation_id,
            mood_before=mood_before,
            mood_after=mood_after,
            notes=notes,
        )
        
        self.db.add(mood_rating)
        self.db.commit()
        self.db.refresh(mood_rating)
        
        return mood_rating
    
    def update_session_mood_after(
        self,
        mood_rating_id: int,
        mood_after: int,
        notes: Optional[str] = None,
    ) -> SessionMoodRating:
        """Update the mood rating at the end of a session.
        
        Args:
            mood_rating_id: ID of the SessionMoodRating to update.
            mood_after: Mood rating (1-10) at the end of the session.
            notes: Optional notes about mood changes.
            
        Returns:
            The updated SessionMoodRating object.
        """
        # Validate mood rating is in range 1-10
        if mood_after < 1 or mood_after > 10:
            raise ValueError("Mood rating must be between 1 and 10")
        
        # Get mood rating
        mood_rating = self.db.query(SessionMoodRating).filter(SessionMoodRating.id == mood_rating_id).first()
        if not mood_rating:
            raise ValueError(f"Mood rating with ID {mood_rating_id} not found")
        
        # Update mood rating
        mood_rating.mood_after = mood_after
        if notes:
            mood_rating.notes = notes
        
        self.db.commit()
        self.db.refresh(mood_rating)
        
        return mood_rating
    
    def get_mood_trends(
        self,
        user_id: int,
        days: int = 90,
    ) -> Dict[str, Any]:
        """Get mood trends for a user over time.
        
        Args:
            user_id: ID of the user.
            days: Number of days to look back.
            
        Returns:
            Dictionary with mood trend information.
        """
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        # Get session mood ratings
        session_ratings = (
            self.db.query(SessionMoodRating)
            .filter(
                SessionMoodRating.user_id == user_id,
                SessionMoodRating.created_at >= cutoff_date,
            )
            .order_by(SessionMoodRating.created_at)
            .all()
        )
        
        # Get simple mood assessments
        mood_assessments = (
            self.db.query(Assessment)
            .filter(
                Assessment.user_id == user_id,
                Assessment.type == AssessmentType.MOOD.value,
                Assessment.taken_at >= cutoff_date,
            )
            .order_by(Assessment.taken_at)
            .all()
        )
        
        # Compile trend data
        before_trend = [
            {
                "date": rating.created_at.strftime("%Y-%m-%d"),
                "score": rating.mood_before,
                "type": "session_before",
            }
            for rating in session_ratings
        ]
        
        after_trend = [
            {
                "date": rating.created_at.strftime("%Y-%m-%d"),
                "score": rating.mood_after,
                "type": "session_after",
            }
            for rating in session_ratings
            if rating.mood_after is not None
        ]
        
        assessment_trend = [
            {
                "date": assessment.taken_at.strftime("%Y-%m-%d"),
                "score": assessment.score,
                "type": "assessment",
            }
            for assessment in mood_assessments
        ]
        
        # Combine all trends
        all_trends = before_trend + after_trend + assessment_trend
        all_trends.sort(key=lambda x: x["date"])
        
        # Calculate average changes for sessions
        session_improvements = [
            rating.mood_after - rating.mood_before
            for rating in session_ratings
            if rating.mood_after is not None
        ]
        
        avg_session_improvement = (
            sum(session_improvements) / len(session_improvements)
            if session_improvements
            else 0.0
        )
        
        return {
            "trends": all_trends,
            "avg_session_improvement": avg_session_improvement,
            "total_measurements": len(all_trends),
            "most_recent_mood": all_trends[-1]["score"] if all_trends else None,
            "most_recent_date": all_trends[-1]["date"] if all_trends else None,
        } 