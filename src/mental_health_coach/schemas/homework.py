"""Pydantic schemas for homework-related operations."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class HomeworkProgressNoteBase(BaseModel):
    """Base schema for homework progress note data.
    
    Attributes:
        content: The text content of the progress note.
    """
    
    homework_id: int = Field(..., description="ID of the homework assignment")
    content: str = Field(..., description="Content of the progress note")


class HomeworkProgressNoteCreate(HomeworkProgressNoteBase):
    """Schema for creating a new homework progress note."""
    
    pass


class HomeworkProgressNote(HomeworkProgressNoteBase):
    """Schema for homework progress note data.
    
    Attributes:
        id: Primary key for the progress note.
        homework_assignment_id: Foreign key reference to the associated homework.
        created_at: Timestamp when the note was created.
    """
    
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID of the progress note")
    homework_assignment_id: int
    created_at: datetime = Field(..., description="When the note was created")
    updated_at: datetime = Field(..., description="When the note was last updated")


class HomeworkAssignmentBase(BaseModel):
    """Base schema for homework assignment data.
    
    Attributes:
        title: Short title describing the homework.
        description: Detailed instructions for the homework.
        technique: The therapeutic technique being practiced.
        due_date: When the homework should be completed by.
    """
    
    title: str = Field(..., description="Title of the homework")
    description: str = Field(..., description="Description of the homework")
    technique: str
    due_date: Optional[datetime] = Field(None, description="Due date of the homework")


class HomeworkAssignmentCreate(HomeworkAssignmentBase):
    """Schema for creating a new homework assignment."""
    
    pass


class HomeworkAssignmentUpdate(BaseModel):
    """Schema for updating a homework assignment.
    
    Attributes:
        is_completed: Whether the homework has been marked complete.
        completion_notes: User notes about their homework experience.
    """
    
    is_completed: Optional[bool] = None
    completion_notes: Optional[str] = None


class HomeworkAssignment(HomeworkAssignmentBase):
    """Schema for homework assignment data.
    
    Attributes:
        id: Primary key for the homework assignment.
        user_id: Foreign key reference to the associated user.
        conversation_id: Foreign key reference to the conversation that generated it.
        is_completed: Whether the homework has been marked complete.
        completion_date: When the homework was completed.
        completion_notes: User notes about their homework experience.
        created_at: Timestamp when the homework was created.
        updated_at: Timestamp when the homework was last updated.
        progress_notes: List of progress notes for this homework.
    """
    
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID of the homework assignment")
    user_id: int
    conversation_id: Optional[int] = Field(None, description="ID of the conversation")
    is_completed: bool = Field(False, description="Whether the homework is completed")
    completion_date: Optional[datetime] = Field(None, description="When the homework was completed")
    completion_notes: Optional[str] = None
    created_at: datetime = Field(..., description="When the homework was created")
    updated_at: datetime = Field(..., description="When the homework was last updated")
    progress_notes: List[HomeworkProgressNote] = [] 