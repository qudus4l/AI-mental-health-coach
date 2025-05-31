"""API endpoints for memory-related operations."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_current_active_user
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.user import User
from src.mental_health_coach.services.rag.conversation_memory import ConversationMemoryService

router = APIRouter()


@router.get("/relevant-context")
def get_relevant_context(
    query: str,
    max_results: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve relevant context from past conversations.
    
    Args:
        query: The query text to find relevant conversation history for.
        max_results: Maximum number of results to return.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List: Contains relevant conversation chunks and their metadata.
    """
    memory_service = ConversationMemoryService(db=db, user=current_user)
    return memory_service.retrieve_relevant_context(query=query, max_results=max_results)


@router.get("/timeline")
def get_therapeutic_timeline(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a chronological timeline of key therapeutic events.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List: A chronological timeline of therapeutic events.
    """
    memory_service = ConversationMemoryService(db=db, user=current_user)
    return memory_service.retrieve_therapeutic_timeline()


@router.get("/themes")
def get_recent_themes(
    days: int = 30,
    min_occurrences: int = 2,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get common themes from recent conversations.
    
    Args:
        days: Number of days to look back.
        min_occurrences: Minimum occurrences to consider a theme significant.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List: Common themes from recent conversations.
    """
    memory_service = ConversationMemoryService(db=db, user=current_user)
    return memory_service.get_recent_themes(days=days, min_occurrences=min_occurrences) 