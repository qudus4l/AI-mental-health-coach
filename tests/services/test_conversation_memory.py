"""Tests for the conversation memory service."""

from typing import TYPE_CHECKING
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy.orm import Session
from scipy.sparse import csr_matrix

from src.mental_health_coach.services.rag.conversation_memory import ConversationMemoryService
from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory
from src.mental_health_coach.models.homework import HomeworkAssignment

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def user() -> User:
    """Create a test user.
    
    Returns:
        User: The test user.
    """
    return User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def db_mock() -> MagicMock:
    """Create a mock database session.
    
    Returns:
        MagicMock: The mock database session.
    """
    mock_db = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.join.return_value = mock_query
    mock_query.group_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    
    return mock_db


@patch('src.mental_health_coach.services.rag.conversation_memory.TfidfVectorizer')
def test_index_conversations(mock_vectorizer, user: User, db_mock: MagicMock) -> None:
    """Test indexing conversations.
    
    Args:
        mock_vectorizer: Mock for TfidfVectorizer.
        user: The test user.
        db_mock: The mock database session.
    """
    # Set up mock vectorizer
    vectorizer_instance = MagicMock()
    mock_vectorizer.return_value = vectorizer_instance
    mock_sparse_matrix = MagicMock(spec=csr_matrix)
    vectorizer_instance.fit_transform.return_value = mock_sparse_matrix
    
    # Set up mock conversations and messages
    now = datetime.now()
    
    conversation1 = Conversation(
        id=1,
        user_id=user.id,
        title="Test Conversation 1",
        is_formal_session=True,
        session_number=1,
        started_at=now - timedelta(days=3),
    )
    
    message1 = Message(
        id=1,
        conversation_id=1,
        is_from_user=True,
        content="Hello, I'm feeling anxious today.",
        created_at=now - timedelta(days=3, hours=1),
    )
    
    message2 = Message(
        id=2,
        conversation_id=1,
        is_from_user=False,
        content="I'm sorry to hear that. Can you tell me more about what's causing your anxiety?",
        created_at=now - timedelta(days=3, hours=1, minutes=1),
    )
    
    message3 = Message(
        id=3,
        conversation_id=1,
        is_from_user=True,
        content="I have a big presentation tomorrow and I'm worried about it.",
        created_at=now - timedelta(days=3, hours=1, minutes=2),
    )
    
    # Mock database queries
    mock_query = db_mock.query.return_value
    mock_query.all.side_effect = [
        [conversation1],  # For conversations query
        [message1, message2, message3],  # For messages query
    ]
    
    # Create memory service
    memory_service = ConversationMemoryService(db=db_mock, user=user)
    memory_service.vectorizer = vectorizer_instance
    
    # Test indexing
    chunks, metadata, vectors = memory_service.index_conversations()
    
    # Verify results
    assert len(chunks) == 1  # One chunk for the 3 messages
    assert len(metadata) == 1
    
    # Verify chunk content
    assert "User: Hello, I'm feeling anxious today." in chunks[0]
    assert "Coach: I'm sorry to hear that." in chunks[0]
    assert "User: I have a big presentation tomorrow" in chunks[0]
    
    # Verify metadata
    assert metadata[0]["conversation_id"] == 1
    assert metadata[0]["is_formal_session"] is True
    assert metadata[0]["session_number"] == 1
    
    # Verify vectorizer was called correctly
    vectorizer_instance.fit_transform.assert_called_once()


@patch('src.mental_health_coach.services.rag.conversation_memory.cosine_similarity')
def test_retrieve_relevant_context(mock_cosine, user: User, db_mock: MagicMock) -> None:
    """Test retrieving relevant context.
    
    Args:
        mock_cosine: Mock for cosine_similarity.
        user: The test user.
        db_mock: The mock database session.
    """
    # Create memory service
    memory_service = ConversationMemoryService(db=db_mock, user=user)
    
    # Create test chunks, metadata, and vectors
    chunks = [
        "User: I'm feeling anxious about my presentation tomorrow.\nCoach: What specifically worries you?\nUser: I'm afraid I'll forget what to say.",
        "User: I've been practicing meditation.\nCoach: How has that been helping?\nUser: It's been calming my nerves.",
        "User: I had a panic attack yesterday.\nCoach: That sounds difficult. What happened before it?\nUser: I was thinking about my deadline.",
    ]
    
    metadata = [
        {"conversation_id": 1, "date": "2023-01-01"},
        {"conversation_id": 2, "date": "2023-01-02"},
        {"conversation_id": 3, "date": "2023-01-03"},
    ]
    
    # Mock index_conversations and vectorizer transform
    memory_service.index_conversations = MagicMock(return_value=(chunks, metadata, np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]])))
    memory_service.vectorizer = MagicMock()
    memory_service.vectorizer.transform.return_value = np.array([[0.1, 0.2, 0.3]])
    
    # Set up mock for cosine_similarity
    mock_cosine.return_value = np.array([[0.2, 0.5, 0.9]])
    
    # Test retrieving relevant context
    results = memory_service.retrieve_relevant_context("anxiety and panic", max_results=2)
    
    # Verify results
    assert len(results) == 2
    assert results[0]["text"] == chunks[2]  # Highest similarity
    assert results[0]["metadata"] == metadata[2]
    assert results[0]["similarity_score"] == 0.9
    
    assert results[1]["text"] == chunks[1]  # Second highest similarity
    assert results[1]["metadata"] == metadata[1]
    assert results[1]["similarity_score"] == 0.5


def test_retrieve_therapeutic_timeline(user: User, db_mock: MagicMock) -> None:
    """Test retrieving therapeutic timeline.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
    """
    # Set up mock data
    now = datetime.now()
    
    # Mock formal sessions
    session1 = Conversation(
        id=1,
        user_id=user.id,
        title="First Session",
        is_formal_session=True,
        session_number=1,
        started_at=now - timedelta(days=10),
        ended_at=now - timedelta(days=10, minutes=45),
    )
    
    # Mock important memories
    memory1 = ImportantMemory(
        id=1,
        user_id=user.id,
        content="User mentioned childhood trauma",
        category="triggers",
        importance_score=80,
        created_at=now - timedelta(days=9),
    )
    
    # Mock homework assignments
    assignment1 = HomeworkAssignment(
        id=1,
        user_id=user.id,
        title="Daily Meditation",
        description="Practice 10 minutes of mindfulness meditation daily",
        created_at=now - timedelta(days=10),
        due_date=now - timedelta(days=3),
        is_completed=True,
        completion_date=now - timedelta(days=4),
    )
    
    # Mock database queries
    mock_query = db_mock.query.return_value
    mock_query.all.side_effect = [
        [session1],  # For formal sessions query
        [memory1],   # For important memories query
        [assignment1],  # For homework assignments query
    ]
    
    # Create memory service
    memory_service = ConversationMemoryService(db=db_mock, user=user)
    
    # Test retrieving timeline
    timeline = memory_service.retrieve_therapeutic_timeline()
    
    # Verify results - there are 4 entries (1 session, 1 memory, 1 homework assignment, 1 homework completion)
    assert len(timeline) == 4
    
    # Check all entries are present and in chronological order
    session_entry = next((entry for entry in timeline if entry["type"] == "formal_session"), None)
    assert session_entry is not None
    assert session_entry["title"] == "First Session"
    
    memory_entry = next((entry for entry in timeline if entry["type"] == "important_memory"), None)
    assert memory_entry is not None
    assert memory_entry["details"]["category"] == "triggers"
    
    homework_assigned = next((entry for entry in timeline if entry["type"] == "homework_assigned"), None)
    assert homework_assigned is not None
    assert homework_assigned["title"] == "Homework: Daily Meditation"
    
    homework_completed = next((entry for entry in timeline if entry["type"] == "homework_completed"), None)
    assert homework_completed is not None
    assert homework_completed["details"]["homework_id"] == 1


def test_get_recent_themes(user: User, db_mock: MagicMock) -> None:
    """Test getting recent themes.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
    """
    # Set up mock conversations and messages
    now = datetime.now()
    
    conversation1 = Conversation(
        id=1,
        user_id=user.id,
        started_at=now - timedelta(days=3),
    )
    
    # Create messages with repeating themes
    messages = [
        Message(id=1, conversation_id=1, is_from_user=True, content="I've been feeling anxious about work lately."),
        Message(id=2, conversation_id=1, is_from_user=False, content="Tell me more about your work anxiety."),
        Message(id=3, conversation_id=1, is_from_user=True, content="My boss keeps giving me too many deadlines."),
        Message(id=4, conversation_id=1, is_from_user=False, content="How have you been managing these deadlines?"),
        Message(id=5, conversation_id=1, is_from_user=True, content="I try to prioritize but still feel anxious about work."),
    ]
    
    # Mock database queries
    mock_query = db_mock.query.return_value
    mock_query.all.side_effect = [
        [conversation1],  # For conversations query
        messages,  # For messages query
    ]
    
    # Create memory service
    memory_service = ConversationMemoryService(db=db_mock, user=user)
    
    # Create a real vectorizer with mocked output
    with patch('src.mental_health_coach.services.rag.conversation_memory.TfidfVectorizer') as mock_vectorizer_class:
        # Mock vectorizer instance
        mock_vectorizer = MagicMock()
        mock_vectorizer_class.return_value = mock_vectorizer
        
        # Mock fit_transform to return a sparse matrix that can be converted to array
        mock_matrix = MagicMock()
        mock_matrix.toarray.return_value = np.array([[0.5, 0.8, 0.3, 0.2]])
        mock_vectorizer.fit_transform.return_value = mock_matrix
        
        # Mock feature names
        mock_vectorizer.get_feature_names_out.return_value = np.array(["anxious", "work", "deadlines", "prioritize"])
        
        # Test getting themes
        themes = memory_service.get_recent_themes()
        
        # Verify results
        assert len(themes) == 4
        assert themes[0]["theme"] == "work"  # Highest score
        assert themes[0]["importance_score"] == 0.8
        assert themes[1]["theme"] == "anxious"
        assert themes[1]["importance_score"] == 0.5 