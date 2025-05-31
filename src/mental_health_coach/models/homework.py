"""Homework models for the mental health coach application."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.mental_health_coach.models.base import Base


class HomeworkAssignment(Base):
    """Homework assignment model for therapeutic exercises.
    
    Homework assignments are tasks given to users at the end of formal
    sessions to practice therapeutic techniques between sessions.
    
    Attributes:
        id: Primary key for the homework assignment.
        user_id: Foreign key reference to the associated user.
        conversation_id: Foreign key reference to the conversation that generated it.
        title: Short title describing the homework.
        description: Detailed instructions for the homework.
        technique: The therapeutic technique being practiced.
        due_date: When the homework should be completed by.
        is_completed: Whether the homework has been marked complete.
        completion_date: When the homework was completed.
        completion_notes: User notes about their homework experience.
        created_at: Timestamp when the homework was created.
        updated_at: Timestamp when the homework was last updated.
        user: Reference to the associated User object.
        conversation: Reference to the associated Conversation object.
        progress_notes: List of progress notes for this homework.
    """
    
    __tablename__ = "homework_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    title = Column(String)
    description = Column(Text)
    technique = Column(String)  # cbt, behavioral_activation, etc.
    due_date = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime, nullable=True)
    completion_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="homework_assignments")
    conversation = relationship("Conversation", back_populates="homework_assignments")
    progress_notes = relationship("HomeworkProgressNote", back_populates="homework_assignment", cascade="all, delete-orphan")


class HomeworkProgressNote(Base):
    """Progress notes for homework assignments.
    
    Users can add multiple progress notes to track their experience with
    a homework assignment over time.
    
    Attributes:
        id: Primary key for the progress note.
        homework_assignment_id: Foreign key reference to the associated homework.
        content: The text content of the progress note.
        created_at: Timestamp when the note was created.
        homework_assignment: Reference to the associated HomeworkAssignment object.
    """
    
    __tablename__ = "homework_progress_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    homework_assignment_id = Column(Integer, ForeignKey("homework_assignments.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    homework_assignment = relationship("HomeworkAssignment", back_populates="progress_notes") 