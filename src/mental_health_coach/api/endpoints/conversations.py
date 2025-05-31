"""API endpoints for conversations."""

from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_current_active_user
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory
from src.mental_health_coach.models.user import User, SessionSchedule
from src.mental_health_coach.services.crisis_detection import CrisisDetector
from src.mental_health_coach.services.emergency_contact import EmergencyContactService
from src.mental_health_coach.services.rag.conversation_memory import ConversationMemoryService
from src.mental_health_coach.services.llm_service import LLMService
from src.mental_health_coach.schemas.conversation import (
    Conversation as ConversationSchema,
    ConversationCreate,
    Message as MessageSchema,
    MessageCreate,
    ImportantMemory as ImportantMemorySchema,
    ImportantMemoryCreate,
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize LLM service
llm_service = LLMService()


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
    is_crisis = False
    if message_in.is_from_user:
        # Initialize crisis detector
        crisis_detector = CrisisDetector()
        
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
        
        # Get message history for context
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        
        message_history = [msg.content for msg in messages if msg.is_from_user and msg.id != db_message.id]
        
        # Detect potential crisis with enhanced context
        is_crisis, categories, resources, analysis_details = crisis_detector.detect_crisis(
            message_in.content, message_history, user_profile
        )
        
        if is_crisis and categories:
            # Generate crisis response
            response_text = crisis_detector.get_crisis_response(categories, analysis_details)
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
            
            # Record crisis event
            emergency_service = EmergencyContactService(db=db, user=current_user)
            crisis_event = emergency_service.record_crisis_event(
                crisis_level=analysis_details.get("risk_level", "medium"),
                conversation_id=conversation_id,
                message_id=db_message.id,
                action_taken="Automated response with resources",
            )
            
            # Package crisis information for the response
            crisis_info = {
                "is_crisis": True,
                "categories": categories,
                "risk_level": analysis_details.get("risk_level", "medium"),
                "resources": resources,
                "ai_response": MessageSchema.model_validate(ai_response),
                "event_id": crisis_event.get("id"),
            }
        else:
            # If no crisis detected, use the LLM to generate a regular response
            
            # Get conversation history in the right format for the LLM
            conversation_history = []
            for msg in messages:
                if msg.id != db_message.id:  # Exclude the current message
                    conversation_history.append({
                        "is_from_user": msg.is_from_user,
                        "content": msg.content
                    })
            
            # Get relevant memories from the conversation memory service
            memory_service = ConversationMemoryService(db=db, user=current_user)
            relevant_memories = memory_service.retrieve_relevant_context(message_in.content, max_results=3)
            
            # Generate AI response using the LLM service
            ai_response_text = llm_service.generate_response(
                user_message=message_in.content,
                conversation_history=conversation_history,
                relevant_memories=relevant_memories,
                user_profile=user_profile,
                is_formal_session=conversation.is_formal_session,
                crisis_detected=False,
            )
            
            # Create AI response message in the database
            ai_response = Message(
                conversation_id=conversation_id,
                is_from_user=False,
                content=ai_response_text,
            )
            db.add(ai_response)
            db.commit()
            db.refresh(ai_response)
            
            # Try to extract an important memory from the conversation
            try:
                # Add the current user message to history for memory extraction
                full_history = conversation_history + [
                    {"is_from_user": True, "content": message_in.content},
                    {"is_from_user": False, "content": ai_response_text}
                ]
                
                memory_data = llm_service.extract_important_memory(
                    conversation_history=full_history,
                    user_profile=user_profile
                )
                
                # If a memory was extracted, save it
                if memory_data and 'content' in memory_data and memory_data['content']:
                    importance_score = float(memory_data.get('importance_score', 0.5))
                    if importance_score > 0.6:  # Only save memories above a certain threshold
                        important_memory = ImportantMemory(
                            user_id=current_user.id,
                            content=memory_data['content'],
                            category=memory_data.get('category', 'insights'),
                            importance_score=importance_score,
                            source_message_id=db_message.id,
                        )
                        db.add(important_memory)
                        db.commit()
            except Exception as e:
                logger.error(f"Error extracting memory: {str(e)}")
                # Don't let memory extraction errors affect the response
                pass
    
    # Return the created message and additional information
    result = {
        "message": MessageSchema.model_validate(db_message),
        "crisis_info": crisis_info,
        "relevant_memories": relevant_memories if 'relevant_memories' in locals() else None,
    }
    
    # If we generated an AI response automatically, include it in the result
    if message_in.is_from_user and ('ai_response' in locals()):
        result["ai_response"] = MessageSchema.model_validate(ai_response)
    
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


@router.get("/{conversation_id}/relevant-context")
def get_relevant_context_for_conversation(
    conversation_id: int,
    query: str,
    max_results: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get relevant context from past conversations for the current conversation.
    
    Args:
        conversation_id: ID of the current conversation.
        query: The query text to find relevant conversation history for.
        max_results: Maximum number of results to return.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List: Contains relevant conversation chunks and their metadata.
        
    Raises:
        HTTPException: If the conversation does not exist or does not belong to the user.
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get relevant context
    memory_service = ConversationMemoryService(db=db, user=current_user)
    return memory_service.retrieve_relevant_context(query=query, max_results=max_results)


@router.get("/{conversation_id}/themes")
def get_conversation_themes(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get common themes from a specific conversation.
    
    Args:
        conversation_id: ID of the conversation to analyze.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List: Common themes from the conversation.
        
    Raises:
        HTTPException: If the conversation does not exist or does not belong to the user.
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get messages from this conversation
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    
    # Extract user messages
    message_history = [msg.content for msg in messages if msg.is_from_user]
    
    # Create a temporary conversation memory service for this conversation only
    memory_service = ConversationMemoryService(db=db, user=current_user)
    
    # Use the same TF-IDF based approach from get_recent_themes but on this conversation only
    vectorizer = memory_service.vectorizer
    
    # Join all user messages
    user_messages = " ".join(message_history)
    
    # Extract themes using the same approach as in get_recent_themes
    if not user_messages.strip():
        return []
    
    try:
        tfidf_matrix = vectorizer.fit_transform([user_messages])
        feature_names = vectorizer.get_feature_names_out()
        
        # Get scores for each term
        scores = tfidf_matrix.toarray()[0]
        
        # Create theme entries
        themes = []
        for term, score in zip(feature_names, scores):
            if score > 0.01:  # Threshold to consider significant
                themes.append({
                    "theme": term,
                    "importance_score": float(score),
                })
        
        # Sort by importance
        themes.sort(key=lambda x: x["importance_score"], reverse=True)
        
        return themes[:10]  # Return top 10 themes
    except ValueError:
        # Handle case where vectorizer couldn't be fitted
        return [] 