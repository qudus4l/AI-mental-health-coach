"""API endpoints for crisis detection and emergency resources."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_current_active_user
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.user import User
from src.mental_health_coach.services.crisis_detection import CrisisDetector, EMERGENCY_RESOURCES

router = APIRouter()


@router.post("/analyze")
def analyze_message_for_crisis(
    message: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Analyze a message for potential crisis indicators.
    
    Args:
        message: The message to analyze.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Contains crisis detection results.
    """
    # Initialize crisis detector
    crisis_detector = CrisisDetector()
    
    # Detect potential crisis
    is_crisis, categories, resources = crisis_detector.detect_crisis(message)
    
    # Package results
    result = {
        "is_crisis": is_crisis,
        "categories": categories,
        "resources": resources,
    }
    
    return result


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