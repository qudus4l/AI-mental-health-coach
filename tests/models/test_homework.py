"""Tests for the homework models."""

from typing import TYPE_CHECKING
from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation
from src.mental_health_coach.models.homework import HomeworkAssignment, HomeworkProgressNote

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def user(db: Session) -> User:
    """Create a test user.
    
    Args:
        db: Database session.
        
    Returns:
        User: Test user.
    """
    user_data = {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "first_name": "Test",
        "last_name": "User",
    }
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def conversation(db: Session, user: User) -> Conversation:
    """Create a test conversation.
    
    Args:
        db: Database session.
        user: Test user.
        
    Returns:
        Conversation: Test conversation.
    """
    conversation = Conversation(
        user_id=user.id,
        title="Test Conversation",
        is_formal_session=True,
        session_number=1,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def test_create_homework_assignment(db: Session, user: User, conversation: Conversation) -> None:
    """Test creating a homework assignment.
    
    Args:
        db: Database session.
        user: Test user.
        conversation: Test conversation.
    """
    # Create a homework assignment
    due_date = datetime.utcnow() + timedelta(days=7)
    homework_data = {
        "user_id": user.id,
        "conversation_id": conversation.id,
        "title": "Breathing Exercises",
        "description": "Practice deep breathing for 5 minutes twice daily.",
        "technique": "cbt",
        "due_date": due_date,
    }
    homework = HomeworkAssignment(**homework_data)
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    # Check the homework was created with the correct data
    assert homework.id is not None
    assert homework.user_id == user.id
    assert homework.conversation_id == conversation.id
    assert homework.title == homework_data["title"]
    assert homework.description == homework_data["description"]
    assert homework.technique == homework_data["technique"]
    assert homework.due_date == due_date
    assert homework.is_completed is False
    assert homework.completion_date is None
    assert homework.completion_notes is None
    assert isinstance(homework.created_at, datetime)
    assert isinstance(homework.updated_at, datetime)
    
    # Check the relationships
    assert homework.user == user
    assert homework.conversation == conversation
    assert homework in user.homework_assignments
    assert homework in conversation.homework_assignments


def test_create_homework_progress_note(
    db: Session, user: User, conversation: Conversation
) -> None:
    """Test creating a homework progress note.
    
    Args:
        db: Database session.
        user: Test user.
        conversation: Test conversation.
    """
    # Create a homework assignment
    due_date = datetime.utcnow() + timedelta(days=7)
    homework = HomeworkAssignment(
        user_id=user.id,
        conversation_id=conversation.id,
        title="Breathing Exercises",
        description="Practice deep breathing for 5 minutes twice daily.",
        technique="cbt",
        due_date=due_date,
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    # Create a progress note
    note_data = {
        "homework_assignment_id": homework.id,
        "content": "I practiced for 5 minutes this morning and felt calmer afterward.",
    }
    note = HomeworkProgressNote(**note_data)
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # Check the note was created with the correct data
    assert note.id is not None
    assert note.homework_assignment_id == homework.id
    assert note.content == note_data["content"]
    assert isinstance(note.created_at, datetime)
    
    # Check the relationship
    assert note.homework_assignment == homework
    assert note in homework.progress_notes


def test_complete_homework_assignment(
    db: Session, user: User, conversation: Conversation
) -> None:
    """Test completing a homework assignment.
    
    Args:
        db: Database session.
        user: Test user.
        conversation: Test conversation.
    """
    # Create a homework assignment
    due_date = datetime.utcnow() + timedelta(days=7)
    homework = HomeworkAssignment(
        user_id=user.id,
        conversation_id=conversation.id,
        title="Breathing Exercises",
        description="Practice deep breathing for 5 minutes twice daily.",
        technique="cbt",
        due_date=due_date,
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    # Complete the homework
    completion_notes = "I found this exercise very helpful for reducing anxiety."
    homework.is_completed = True
    homework.completion_notes = completion_notes
    homework.completion_date = datetime.utcnow()
    db.commit()
    db.refresh(homework)
    
    # Check the homework was updated correctly
    assert homework.is_completed is True
    assert homework.completion_notes == completion_notes
    assert isinstance(homework.completion_date, datetime) 