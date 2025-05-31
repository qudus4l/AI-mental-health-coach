"""API endpoints for homework assignments."""

from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_current_active_user
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.homework import HomeworkAssignment, HomeworkProgressNote
from src.mental_health_coach.models.conversation import Conversation
from src.mental_health_coach.models.user import User
from src.mental_health_coach.schemas.homework import (
    HomeworkAssignment as HomeworkAssignmentSchema,
    HomeworkAssignmentCreate,
    HomeworkAssignmentUpdate,
    HomeworkProgressNote as HomeworkProgressNoteSchema,
    HomeworkProgressNoteCreate,
)

router = APIRouter()


@router.post("/", response_model=HomeworkAssignmentSchema, status_code=status.HTTP_201_CREATED)
def create_homework_assignment(
    homework_in: HomeworkAssignmentCreate,
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new homework assignment.
    
    Args:
        homework_in: Homework assignment creation data.
        conversation_id: ID of the conversation that generated the homework.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        HomeworkAssignmentSchema: The created homework assignment.
        
    Raises:
        HTTPException: If the conversation does not exist or does not belong to the user.
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_homework = HomeworkAssignment(
        user_id=current_user.id,
        conversation_id=conversation_id,
        title=homework_in.title,
        description=homework_in.description,
        technique=homework_in.technique,
        due_date=homework_in.due_date,
    )
    db.add(db_homework)
    db.commit()
    db.refresh(db_homework)
    return db_homework


@router.get("/", response_model=List[HomeworkAssignmentSchema])
def read_homework_assignments(
    skip: int = 0,
    limit: int = 100,
    completed: bool = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get all homework assignments for the current user.
    
    Args:
        skip: Number of homework assignments to skip.
        limit: Maximum number of homework assignments to return.
        completed: Optional filter for completed/incomplete assignments.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List[HomeworkAssignmentSchema]: List of homework assignments.
    """
    query = db.query(HomeworkAssignment).filter(HomeworkAssignment.user_id == current_user.id)
    
    if completed is not None:
        query = query.filter(HomeworkAssignment.is_completed == completed)
    
    homework_assignments = query.order_by(HomeworkAssignment.due_date).offset(skip).limit(limit).all()
    return homework_assignments


@router.get("/{homework_id}", response_model=HomeworkAssignmentSchema)
def read_homework_assignment(
    homework_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific homework assignment.
    
    Args:
        homework_id: ID of the homework assignment to get.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        HomeworkAssignmentSchema: The requested homework assignment.
        
    Raises:
        HTTPException: If the homework assignment does not exist or does not belong to the user.
    """
    homework = db.query(HomeworkAssignment).filter(HomeworkAssignment.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework assignment not found")
    if homework.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return homework


@router.put("/{homework_id}", response_model=HomeworkAssignmentSchema)
def update_homework_assignment(
    homework_id: int,
    homework_in: HomeworkAssignmentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update a homework assignment.
    
    Args:
        homework_id: ID of the homework assignment to update.
        homework_in: Homework assignment update data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        HomeworkAssignmentSchema: The updated homework assignment.
        
    Raises:
        HTTPException: If the homework assignment does not exist or does not belong to the user.
    """
    homework = db.query(HomeworkAssignment).filter(HomeworkAssignment.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework assignment not found")
    if homework.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update fields
    update_data = homework_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(homework, key, value)
    
    # If marking as completed, set completion date
    if homework_in.is_completed and not homework.completion_date:
        homework.completion_date = datetime.utcnow()
    
    db.commit()
    db.refresh(homework)
    return homework


@router.post(
    "/{homework_id}/progress-notes",
    response_model=HomeworkProgressNoteSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_progress_note(
    homework_id: int,
    note_in: HomeworkProgressNoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new progress note for a homework assignment.
    
    Args:
        homework_id: ID of the homework assignment to add the note to.
        note_in: Progress note creation data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        HomeworkProgressNoteSchema: The created progress note.
        
    Raises:
        HTTPException: If the homework assignment does not exist or does not belong to the user.
    """
    homework = db.query(HomeworkAssignment).filter(HomeworkAssignment.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework assignment not found")
    if homework.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_note = HomeworkProgressNote(
        homework_assignment_id=homework_id,
        content=note_in.content,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get("/{homework_id}/progress-notes", response_model=List[HomeworkProgressNoteSchema])
def read_progress_notes(
    homework_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get all progress notes for a homework assignment.
    
    Args:
        homework_id: ID of the homework assignment to get notes for.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List[HomeworkProgressNoteSchema]: List of progress notes.
        
    Raises:
        HTTPException: If the homework assignment does not exist or does not belong to the user.
    """
    homework = db.query(HomeworkAssignment).filter(HomeworkAssignment.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework assignment not found")
    if homework.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    notes = (
        db.query(HomeworkProgressNote)
        .filter(HomeworkProgressNote.homework_assignment_id == homework_id)
        .order_by(HomeworkProgressNote.created_at)
        .all()
    )
    return notes 