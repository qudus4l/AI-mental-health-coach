"""API endpoints for conversations."""

from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_current_active_user
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory
from src.mental_health_coach.models.user import User, SessionSchedule
from src.mental_health_coach.services.crisis_detection import CrisisDetector
from src.mental_health_coach.schemas.conversation import (
    Conversation as ConversationSchema,
    ConversationCreate,
    Message as MessageSchema,
    MessageCreate,
    ImportantMemory as ImportantMemorySchema,
    ImportantMemoryCreate,
)

router = APIRouter()


@router.post("/", response_model=ConversationSchema, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation_in: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new conversation.
    
    Args:
        conversation_in: Conversation creation data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        ConversationSchema: The created conversation.
    """
    # If this is a formal session, check if it aligns with the user's schedule
    is_formal_session = conversation_in.is_formal_session
    session_number = conversation_in.session_number
    
    if is_formal_session:
        # If no session number provided, calculate the next one
        if not session_number:
            # Count existing formal sessions for this user
            session_count = (
                db.query(Conversation)
                .filter(
                    Conversation.user_id == current_user.id,
                    Conversation.is_formal_session == True,
                )
                .count()
            )
            session_number = session_count + 1
        
        # Check if this aligns with a scheduled session time
        now = datetime.utcnow()
        current_weekday = now.weekday()  # 0 = Monday, 6 = Sunday
        current_hour = now.hour
        current_minute = now.minute
        
        # Find a scheduled session that matches the current time (within 15 minutes)
        matching_schedule = (
            db.query(SessionSchedule)
            .filter(
                SessionSchedule.user_id == current_user.id,
                SessionSchedule.is_active == True,
                SessionSchedule.day_of_week == current_weekday,
            )
            .all()
        )
        
        time_matched = False
        for schedule in matching_schedule:
            # Check if current time is within 15 minutes of scheduled time
            scheduled_minutes = schedule.hour * 60 + schedule.minute
            current_minutes = current_hour * 60 + current_minute
            if abs(scheduled_minutes - current_minutes) <= 15:
                time_matched = True
                break
        
        # For now, we'll allow the session even if it doesn't match a schedule,
        # but in a production system, this might be enforced
    
    db_conversation = Conversation(
        user_id=current_user.id,
        title=conversation_in.title,
        is_formal_session=is_formal_session,
        session_number=session_number,
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.get("/", response_model=List[ConversationSchema])
def read_conversations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get all conversations for the current user.
    
    Args:
        skip: Number of conversations to skip.
        limit: Maximum number of conversations to return.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List[ConversationSchema]: List of conversations.
    """
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.started_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return conversations


@router.get("/{conversation_id}", response_model=ConversationSchema)
def read_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific conversation.
    
    Args:
        conversation_id: ID of the conversation to get.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        ConversationSchema: The requested conversation.
        
    Raises:
        HTTPException: If the conversation does not exist or does not belong to the user.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return conversation


@router.post(
    "/{conversation_id}/messages", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED
)
def create_message(
    conversation_id: int,
    message_in: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new message in a conversation.
    
    This endpoint also performs crisis detection on user messages and provides
    appropriate responses and resources if a crisis is detected.
    
    Args:
        conversation_id: ID of the conversation to add the message to.
        message_in: Message creation data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Contains the created message and crisis information if detected.
        
    Raises:
        HTTPException: If the conversation does not exist or does not belong to the user.
    """
    # Get the conversation
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # If conversation is ended, don't allow new messages
    if conversation.ended_at:
        raise HTTPException(status_code=400, detail="Cannot add messages to ended conversation")
    
    # Create and save the message
    db_message = Message(
        conversation_id=conversation_id,
        is_from_user=message_in.is_from_user,
        content=message_in.content,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Check for crisis indicators in user messages
    crisis_info = None
    if message_in.is_from_user:
        # Initialize crisis detector
        crisis_detector = CrisisDetector()
        
        # Detect potential crisis
        is_crisis, categories, resources = crisis_detector.detect_crisis(message_in.content)
        
        if is_crisis and categories:
            # Generate crisis response
            response_text = crisis_detector.get_crisis_response(categories)
            formatted_resources = crisis_detector.format_resources(resources)
            
            # Create AI response message with crisis information
            ai_response = Message(
                conversation_id=conversation_id,
                is_from_user=False,
                content=response_text + formatted_resources,
            )
            db.add(ai_response)
            db.commit()
            db.refresh(ai_response)
            
            # Package crisis information for the response
            crisis_info = {
                "is_crisis": True,
                "categories": categories,
                "resources": resources,
                "ai_response": MessageSchema.model_validate(ai_response),
            }
    
    # Return the created message and crisis information
    result = {
        "message": MessageSchema.model_validate(db_message),
        "crisis_info": crisis_info,
    }
    
    return result


@router.put("/{conversation_id}/end", response_model=ConversationSchema)
def end_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """End a conversation.
    
    Args:
        conversation_id: ID of the conversation to end.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        ConversationSchema: The updated conversation.
        
    Raises:
        HTTPException: If the conversation does not exist, does not belong to the user,
            or is already ended.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if conversation.ended_at:
        raise HTTPException(status_code=400, detail="Conversation already ended")
    
    conversation.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    return conversation


@router.post(
    "/memories",
    response_model=ImportantMemorySchema,
    status_code=status.HTTP_201_CREATED,
)
def create_important_memory(
    memory_in: ImportantMemoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new important memory.
    
    Args:
        memory_in: Memory creation data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        ImportantMemorySchema: The created memory.
        
    Raises:
        HTTPException: If the source message does not exist or does not belong to the user.
    """
    # Validate source message if provided
    if memory_in.source_message_id:
        message = db.query(Message).filter(Message.id == memory_in.source_message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Source message not found")
        conversation = db.query(Conversation).filter(Conversation.id == message.conversation_id).first()
        if conversation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_memory = ImportantMemory(
        user_id=current_user.id,
        content=memory_in.content,
        category=memory_in.category,
        importance_score=memory_in.importance_score,
        source_message_id=memory_in.source_message_id,
    )
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory


@router.get("/memories", response_model=List[ImportantMemorySchema])
def read_important_memories(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get all important memories for the current user.
    
    Args:
        skip: Number of memories to skip.
        limit: Maximum number of memories to return.
        category: Optional category to filter by.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List[ImportantMemorySchema]: List of important memories.
    """
    query = db.query(ImportantMemory).filter(ImportantMemory.user_id == current_user.id)
    
    if category:
        query = query.filter(ImportantMemory.category == category)
    
    memories = query.order_by(ImportantMemory.importance_score.desc()).offset(skip).limit(limit).all()
    return memories 