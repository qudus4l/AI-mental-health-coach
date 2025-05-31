"""API endpoints for voice-based conversations."""

import os
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_current_active_user
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.user import User
from src.mental_health_coach.services.voice_conversation_service import VoiceConversationService
from src.mental_health_coach.schemas.conversation import Conversation as ConversationSchema
from src.mental_health_coach.schemas.conversation import ConversationCreate

router = APIRouter()
logger = logging.getLogger(__name__)

# Dictionary to store active voice conversation services by user ID
active_services: Dict[int, VoiceConversationService] = {}


@router.post("/conversations", response_model=ConversationSchema, status_code=status.HTTP_201_CREATED)
def start_voice_conversation(
    conversation_in: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Start a new voice-based conversation.
    
    Args:
        conversation_in: Conversation creation data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        ConversationSchema: The created conversation.
    """
    # Check if user already has an active voice conversation
    if current_user.id in active_services:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active voice conversation",
        )
    
    # Create a new voice conversation service
    service = VoiceConversationService(
        db=db,
        user=current_user,
        config={
            "voice_config": {
                "recorder_type": "mock",
                "player_type": "mock",
                "stt_engine_type": "mock",
                "tts_engine_type": "mock",
            }
        },
    )
    
    # Start a new conversation
    conversation = service.start_conversation(
        is_formal_session=conversation_in.is_formal_session,
        title=conversation_in.title,
    )
    
    # Store the service
    active_services[current_user.id] = service
    
    return conversation


@router.post("/conversations/{conversation_id}/end", response_model=ConversationSchema)
def end_voice_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """End a voice-based conversation.
    
    Args:
        conversation_id: ID of the conversation to end.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        ConversationSchema: The updated conversation.
        
    Raises:
        HTTPException: If the conversation does not exist or is not active.
    """
    # Check if user has an active voice conversation
    if current_user.id not in active_services:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active voice conversation found",
        )
    
    service = active_services[current_user.id]
    
    # Check if the conversation ID matches
    if not service.current_conversation or service.current_conversation.id != conversation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation ID does not match active conversation",
        )
    
    # End the conversation
    service.end_conversation()
    
    # Remove the service
    del active_services[current_user.id]
    
    # Return the ended conversation
    conversation = db.query(service.current_conversation.__class__).get(conversation_id)
    return conversation


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    db: Session = Depends(get_db),
) -> None:
    """WebSocket endpoint for voice-based conversations.
    
    This endpoint allows for real-time communication between the client and server
    for voice-based conversations.
    
    Args:
        websocket: WebSocket connection.
        user_id: ID of the user.
        db: Database session.
    """
    await websocket.accept()
    
    try:
        # Check if user has an active voice conversation
        if user_id not in active_services:
            await websocket.send_json({"error": "No active voice conversation found"})
            await websocket.close()
            return
        
        service = active_services[user_id]
        
        # Set up WebSocket callbacks
        def on_message_received(message: str) -> None:
            """Handle received messages."""
            websocket.send_json({"type": "transcription", "message": message})
        
        def on_response_ready(response: str) -> None:
            """Handle AI responses."""
            websocket.send_json({"type": "response", "message": response})
        
        service.on_message_received = on_message_received
        service.on_response_ready = on_response_ready
        
        # Listen for messages from the client
        while True:
            data = await websocket.receive_json()
            command = data.get("command")
            
            if command == "start_listening":
                service.start_voice_input()
                await websocket.send_json({"type": "status", "status": "listening"})
            
            elif command == "stop_listening":
                service.stop_voice_input()
                await websocket.send_json({"type": "status", "status": "processing"})
            
            elif command == "send_text":
                message_text = data.get("message", "")
                if message_text:
                    service.send_text_message(message_text)
                    await websocket.send_json({"type": "status", "status": "message_sent"})
            
            elif command == "stop_speaking":
                service.voice_manager.stop_speaking()
                await websocket.send_json({"type": "status", "status": "speech_stopped"})
            
            elif command == "end_conversation":
                service.end_conversation()
                del active_services[user_id]
                await websocket.send_json({"type": "status", "status": "conversation_ended"})
                break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
        
        # Clean up if necessary
        if user_id in active_services:
            service = active_services[user_id]
            service.cleanup()
            del active_services[user_id]
    
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}", exc_info=True)
        await websocket.send_json({"error": str(e)})
        
        # Clean up if necessary
        if user_id in active_services:
            service = active_services[user_id]
            service.cleanup()
            del active_services[user_id]


@router.post("/audio/upload", status_code=status.HTTP_200_OK)
async def upload_audio(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload audio for transcription.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        dict: Success status and transcription.
        
    Raises:
        HTTPException: If the user does not have an active voice conversation.
    """
    # This is a placeholder for audio upload functionality.
    # In a real implementation, this would accept audio data from the client
    # and pass it to the speech-to-text engine.
    
    # Check if user has an active voice conversation
    if current_user.id not in active_services:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active voice conversation found",
        )
    
    return {"success": True, "message": "Audio upload is not implemented yet"}