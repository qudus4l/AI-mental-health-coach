"""Voice conversation service for the mental health coach application."""

import os
import logging
import threading
from typing import Optional, Dict, Any, List, Callable

from sqlalchemy.orm import Session

from src.mental_health_coach.voice.conversation_manager import VoiceConversationManager
from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation, Message

logger = logging.getLogger(__name__)


class VoiceConversationService:
    """Service for managing voice-based conversations.
    
    This service integrates the voice conversation manager with the
    database models and business logic for AI-powered conversations.
    
    Attributes:
        voice_manager: The voice conversation manager.
        db: Database session.
        current_user: The current user.
        current_conversation: The current conversation.
        on_message_received: Callback for when a user message is received.
        on_response_ready: Callback for when an AI response is ready.
        config: Configuration dictionary.
    """
    
    def __init__(self, db: Session, user: User, config: Dict[str, Any]) -> None:
        """Initialize the voice conversation service.
        
        Args:
            db: Database session.
            user: The current user.
            config: Configuration dictionary.
        """
        self.db = db
        self.current_user = user
        self.config = config
        
        # Initialize voice conversation manager
        self.voice_manager = VoiceConversationManager(config.get("voice_config", {}))
        
        # Set up callbacks
        self.voice_manager.set_on_transcription_complete(self._handle_transcription)
        self.voice_manager.set_on_speech_complete(self._handle_speech_complete)
        
        # Set up conversation state
        self.current_conversation: Optional[Conversation] = None
        
        # External callbacks
        self.on_message_received: Optional[Callable[[str], None]] = None
        self.on_response_ready: Optional[Callable[[str], None]] = None
        
        # State variables
        self._processing_message = False
        self._response_queue: List[str] = []
    
    def start_conversation(self, is_formal_session: bool = False, title: Optional[str] = None) -> Conversation:
        """Start a new conversation.
        
        Args:
            is_formal_session: Whether this is a formal therapy session.
            title: Optional title for the conversation.
            
        Returns:
            Conversation: The created conversation object.
        """
        # Create a new conversation in the database
        conversation = Conversation(
            user_id=self.current_user.id,
            title=title or "Voice conversation",
            is_formal_session=is_formal_session,
        )
        
        # Get the session number if this is a formal session
        if is_formal_session:
            # Count existing formal sessions for this user
            session_count = self.db.query(Conversation).filter(
                Conversation.user_id == self.current_user.id,
                Conversation.is_formal_session == True
            ).count()
            conversation.session_number = session_count + 1
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        # Store as current conversation
        self.current_conversation = conversation
        
        return conversation
    
    def start_voice_input(self) -> None:
        """Start listening for voice input."""
        if not self.current_conversation:
            logger.error("Cannot start voice input without an active conversation")
            return
        
        # Start listening for voice input
        self.voice_manager.start_listening()
    
    def stop_voice_input(self) -> None:
        """Stop listening for voice input."""
        self.voice_manager.stop_listening()
    
    def send_text_message(self, message_text: str) -> Message:
        """Send a text message in the current conversation.
        
        Args:
            message_text: The message text.
            
        Returns:
            Message: The created message object.
            
        Raises:
            ValueError: If there is no active conversation.
        """
        if not self.current_conversation:
            raise ValueError("No active conversation")
        
        # Create the message in the database
        message = Message(
            conversation_id=self.current_conversation.id,
            is_from_user=True,
            content=message_text,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Process the message
        self._process_user_message(message)
        
        return message
    
    def _handle_transcription(self, transcription: str) -> None:
        """Handle a completed transcription.
        
        This method is called when the speech-to-text process completes.
        
        Args:
            transcription: The transcribed text.
        """
        if not transcription:
            logger.warning("Received empty transcription")
            return
        
        logger.info(f"Transcription received: {transcription}")
        
        # Notify external listeners
        if self.on_message_received:
            self.on_message_received(transcription)
        
        # Send the transcribed message
        try:
            self.send_text_message(transcription)
        except ValueError as e:
            logger.error(f"Error sending transcribed message: {e}")
    
    def _process_user_message(self, message: Message) -> None:
        """Process a user message and generate a response.
        
        Args:
            message: The user message to process.
        """
        if self._processing_message:
            logger.warning("Already processing a message, queuing response")
            return
        
        self._processing_message = True
        
        try:
            # In a real implementation, this would call an LLM or other AI service
            # to generate a response based on the conversation history
            
            # For now, we'll use a simple mock response
            response_text = self._generate_mock_response(message.content)
            
            # Create the AI response message
            ai_message = Message(
                conversation_id=self.current_conversation.id,
                is_from_user=False,
                content=response_text,
            )
            self.db.add(ai_message)
            self.db.commit()
            self.db.refresh(ai_message)
            
            # Queue the response for speech synthesis
            self._response_queue.append(response_text)
            
            # Notify external listeners
            if self.on_response_ready:
                self.on_response_ready(response_text)
            
            # Speak the response if not already speaking
            if not self.voice_manager.player.is_playing():
                self._speak_next_response()
                
        finally:
            self._processing_message = False
    
    def _speak_next_response(self) -> None:
        """Speak the next response in the queue."""
        if not self._response_queue:
            return
        
        # Get the next response
        response_text = self._response_queue.pop(0)
        
        # Speak the response
        self.voice_manager.speak_response(response_text)
    
    def _handle_speech_complete(self) -> None:
        """Handle completion of speech synthesis.
        
        This method is called when the text-to-speech process completes.
        """
        logger.info("Speech playback complete")
        
        # Speak the next response if there are more in the queue
        if self._response_queue:
            self._speak_next_response()
    
    def _generate_mock_response(self, user_message: str) -> str:
        """Generate a mock AI response for testing.
        
        Args:
            user_message: The user's message.
            
        Returns:
            str: A mock response.
        """
        # Simple mock responses based on keywords
        if "hello" in user_message.lower() or "hi" in user_message.lower():
            return "Hello! How are you feeling today?"
        
        if "anxiety" in user_message.lower() or "anxious" in user_message.lower():
            return "I hear that you're feeling anxious. Can you tell me more about what's causing your anxiety?"
        
        if "sad" in user_message.lower() or "depress" in user_message.lower():
            return "I'm sorry to hear that you're feeling down. What specific thoughts or situations have been contributing to these feelings?"
        
        if "help" in user_message.lower():
            return "I'm here to help. Let's work through this together. Would you like to try a breathing exercise to help calm your mind?"
        
        # Default response
        return "Thank you for sharing. Could you tell me more about your experience?"
    
    def end_conversation(self) -> None:
        """End the current conversation."""
        if not self.current_conversation:
            logger.warning("No active conversation to end")
            return
        
        # Stop any active voice I/O
        if self.voice_manager.recorder.is_recording():
            self.voice_manager.stop_listening()
        
        if self.voice_manager.player.is_playing():
            self.voice_manager.stop_speaking()
        
        # Mark the conversation as ended in the database
        from datetime import datetime
        self.current_conversation.ended_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(self.current_conversation)
        
        # Clear the current conversation
        self.current_conversation = None
    
    def cleanup(self) -> None:
        """Clean up resources used by the service."""
        # End any active conversation
        if self.current_conversation:
            self.end_conversation()
        
        # Clean up voice manager resources
        self.voice_manager.cleanup() 