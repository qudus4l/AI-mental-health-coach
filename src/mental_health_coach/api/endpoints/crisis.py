"""API endpoints for crisis detection and emergency resources."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_current_active_user
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation, Message
from src.mental_health_coach.services.crisis_detection import CrisisDetector, EMERGENCY_RESOURCES
from src.mental_health_coach.services.emergency_contact import EmergencyContactService

router = APIRouter()


class MessageAnalysisRequest(BaseModel):
    """Schema for message analysis request."""
    
    message: str
    conversation_id: Optional[int] = None
    include_message_history: bool = False


class HistoricalAnalysisRequest(BaseModel):
    """Schema for historical analysis request."""
    
    conversation_id: int
    message_limit: Optional[int] = 20


@router.post("/analyze")
def analyze_message_for_crisis(
    analysis_in: MessageAnalysisRequest = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Analyze a message for potential crisis indicators with enhanced detection.
    
    Args:
        analysis_in: The message analysis request.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Contains crisis detection results.
    """
    # Initialize crisis detector
    crisis_detector = CrisisDetector()
    
    # Get message history if requested
    message_history = None
    if analysis_in.include_message_history and analysis_in.conversation_id:
        # Get previous messages from this conversation
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == analysis_in.conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        
        message_history = [msg.content for msg in messages if msg.is_from_user]
    
    # Get user profile data for context-aware detection
    user_profile = None
    
    # Find user profile - handle profile access safely
    # In case of profile being a list (for SQLAlchemy relationship)
    if hasattr(current_user, 'profile'):
        if current_user.profile and isinstance(current_user.profile, list) and len(current_user.profile) > 0:
            profile = current_user.profile[0]
            user_profile = {
                "anxiety_score": getattr(profile, 'anxiety_score', 0),
                "depression_score": getattr(profile, 'depression_score', 0),
            }
        elif current_user.profile and not isinstance(current_user.profile, list):
            user_profile = {
                "anxiety_score": getattr(current_user.profile, 'anxiety_score', 0),
                "depression_score": getattr(current_user.profile, 'depression_score', 0),
            }
    
    # Detect potential crisis with enhanced context
    is_crisis, categories, resources, analysis_details = crisis_detector.detect_crisis(
        analysis_in.message, message_history, user_profile
    )
    
    # Get appropriate response based on detection results
    crisis_response = None
    if is_crisis:
        response_text = crisis_detector.get_crisis_response(categories, analysis_details)
        formatted_resources = crisis_detector.format_resources(resources)
        crisis_response = response_text + formatted_resources
    
    # Package results
    result = {
        "is_crisis": is_crisis,
        "categories": categories,
        "risk_level": analysis_details.get("risk_level", "low"),
        "confidence_score": analysis_details.get("confidence_score", 0.0),
        "resources": resources,
        "crisis_response": crisis_response,
        "analysis_details": analysis_details,
    }
    
    return result


@router.post("/historical-analysis")
def analyze_message_history(
    analysis_in: HistoricalAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Analyze message history for crisis patterns over time.
    
    Args:
        analysis_in: The historical analysis request.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Contains historical analysis results.
    """
    # Check if conversation exists and belongs to user
    conversation = db.query(Conversation).filter(Conversation.id == analysis_in.conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get messages from this conversation
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == analysis_in.conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    
    # Extract user messages
    message_history = [msg.content for msg in messages if msg.is_from_user]
    
    # Limit the number of messages if specified
    if analysis_in.message_limit and len(message_history) > analysis_in.message_limit:
        message_history = message_history[-analysis_in.message_limit:]
    
    # Initialize crisis detector
    crisis_detector = CrisisDetector()
    
    # Analyze message history
    results = crisis_detector.get_historical_crisis_indicators(message_history)
    
    return results


@router.get("/resources/{category}")
def get_resources_by_category(
    category: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get emergency resources for a specific crisis category.
    
    Args:
        category: The crisis category to get resources for.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List: Contains resources for the requested category.
        
    Raises:
        HTTPException: If the category is not found.
    """
    # Check if category exists
    if category not in EMERGENCY_RESOURCES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resources for category '{category}' not found",
        )
    
    # Return resources for the category
    return EMERGENCY_RESOURCES[category]


@router.get("/categories")
def get_crisis_categories(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get available crisis categories.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        List[str]: List of available crisis categories.
    """
    crisis_detector = CrisisDetector()
    return list(crisis_detector.crisis_keywords.keys()) 