"""Unit tests for conversation memory service.

This module contains tests for the ConversationMemoryService class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from datetime import datetime, timedelta
import numpy as np
import json

# Create mock classes
class MockUser:
    """Mock User class for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockConversation:
    """Mock Conversation class for testing."""
    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.session_number = kwargs.get('session_number', 1)  # Default to 1
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockImportantMemory:
    """Mock ImportantMemory class for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.fixture
def user():
    """Create a test user.
    
    Returns:
        User: The test user.
    """
    return MockUser(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def conversations(user):
    """Create test conversations.
    
    Args:
        user: The test user.
        
    Returns:
        List[Conversation]: List of test conversations.
    """
    return [
        MockConversation(
            id=1,
            user_id=user.id,
            title="First Conversation",
            is_formal_session=True,
            session_number=1,
            started_at=datetime.now() - timedelta(days=10),
            ended_at=datetime.now() - timedelta(days=10, hours=1),
            summary="This was about anxiety",
        ),
        MockConversation(
            id=2,
            user_id=user.id,
            title="Second Conversation",
            is_formal_session=False,
            session_number=None,
            started_at=datetime.now() - timedelta(days=5),
            ended_at=datetime.now() - timedelta(days=5, hours=1),
            summary="This was about depression",
        ),
        MockConversation(
            id=3,
            user_id=user.id,
            title="Latest Conversation",
            is_formal_session=True,
            session_number=2,
            started_at=datetime.now() - timedelta(days=1),
            ended_at=datetime.now() - timedelta(hours=23),
            summary="This was about social anxiety",
        ),
    ]


@pytest.fixture
def memories(user, conversations):
    """Create test memories.
    
    Args:
        user: The test user.
        conversations: List of test conversations.
        
    Returns:
        List[ImportantMemory]: List of test memories.
    """
    return [
        MockImportantMemory(
            id=1,
            user_id=user.id,
            conversation_id=conversations[0].id,
            content="User mentioned having anxiety in social settings",
            category="triggers",
            importance_score=0.8,
            created_at=datetime.now() - timedelta(days=10),
        ),
        MockImportantMemory(
            id=2,
            user_id=user.id,
            conversation_id=conversations[1].id,
            content="User feels depressed when alone for long periods",
            category="triggers",
            importance_score=0.9,
            created_at=datetime.now() - timedelta(days=5),
        ),
        MockImportantMemory(
            id=3,
            user_id=user.id,
            conversation_id=conversations[2].id,
            content="User developed a new coping strategy for anxiety",
            category="coping_strategies",
            importance_score=0.7,
            created_at=datetime.now() - timedelta(days=1),
        ),
    ]


def test_index_conversations():
    """Test indexing conversations for semantic search."""
    # Import the class to patch
    from src.mental_health_coach.services.rag.conversation_memory import ConversationMemoryService
    from src.mental_health_coach.models.conversation import Conversation, Message
    
    # Setup
    mock_db = Mock()
    mock_user = MockUser(id=1)
    
    # Mock queries
    mock_query = Mock()
    mock_filter = Mock()
    mock_order_by = Mock()
    
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.order_by.return_value = mock_order_by
    
    # Create mock conversations
    mock_conversations = [
        MockConversation(
            id=1,
            user_id=1,
            title="First Conversation",
            is_formal_session=True,
            session_number=1,
            started_at=datetime.now() - timedelta(days=10),
            ended_at=datetime.now() - timedelta(days=10, hours=1),
            summary="This was about anxiety",
        ),
        MockConversation(
            id=2,
            user_id=1,
            title="Second Conversation",
            is_formal_session=False,
            session_number=None,
            started_at=datetime.now() - timedelta(days=5),
            ended_at=datetime.now() - timedelta(days=5, hours=1),
            summary="This was about depression",
        ),
    ]
    mock_order_by.all.return_value = mock_conversations
    
    # Mock message queries
    mock_message_query = Mock()
    mock_message_filter = Mock()
    mock_message_order_by = Mock()
    
    mock_db.query.side_effect = [mock_query, mock_message_query, mock_message_query]
    mock_message_query.filter.return_value = mock_message_filter
    mock_message_filter.order_by.return_value = mock_message_order_by
    
    # Create mock messages for each conversation
    mock_messages_1 = [
        Mock(
            id=1,
            conversation_id=1,
            is_from_user=True,
            content="I'm feeling anxious today",
            created_at=datetime.now() - timedelta(days=10, hours=1)
        ),
        Mock(
            id=2,
            conversation_id=1,
            is_from_user=False,
            content="I'm sorry to hear that. Can you tell me more?",
            created_at=datetime.now() - timedelta(days=10, hours=1, minutes=5)
        )
    ]
    
    mock_messages_2 = [
        Mock(
            id=3,
            conversation_id=2,
            is_from_user=True,
            content="I've been feeling down lately",
            created_at=datetime.now() - timedelta(days=5, hours=1)
        ),
        Mock(
            id=4,
            conversation_id=2,
            is_from_user=False,
            content="Let's talk about that. When did this start?",
            created_at=datetime.now() - timedelta(days=5, hours=1, minutes=5)
        )
    ]
    
    mock_message_order_by.all.side_effect = [mock_messages_1, mock_messages_2]
    
    # Create service with mock DB
    service = ConversationMemoryService(db=mock_db, user=mock_user)
    
    # Mock vectorizer
    service.vectorizer = Mock()
    mock_matrix = Mock()
    mock_matrix.toarray.return_value = np.array([[0.1, 0.2, 0.3]])
    service.vectorizer.fit_transform.return_value = mock_matrix
    
    # Call method
    chunks, metadata, vectors = service.index_conversations()
    
    # Verify results
    assert len(chunks) > 0
    assert len(metadata) > 0
    assert isinstance(vectors, np.ndarray) or hasattr(vectors, 'toarray')


def test_store_important_memory():
    """Test storing an important memory."""
    # Import here to apply patch
    from src.mental_health_coach.services.rag.conversation_memory import ConversationMemoryService, ImportantMemory
    
    # Setup
    mock_db = Mock()
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Create service with mock DB
    service = ConversationMemoryService(db=mock_db, user=MockUser(id=1))
    
    # Create patch for ImportantMemory to return our mock instead
    mock_memory = Mock()
    mock_memory.user_id = 1
    mock_memory.conversation_id = 1
    mock_memory.content = "User mentioned having anxiety in social settings"
    mock_memory.category = "triggers"
    mock_memory.importance_score = 0.8
    
    with patch('src.mental_health_coach.services.rag.conversation_memory.ImportantMemory', return_value=mock_memory):
        # Call method
        memory = service.store_important_memory(
            content="User mentioned having anxiety in social settings",
            category="triggers",
            importance_score=0.8,
            conversation_id=1,
        )
        
        # Verify DB interactions
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
        
        # Verify memory properties
        assert memory.user_id == 1
        assert memory.conversation_id == 1
        assert memory.content == "User mentioned having anxiety in social settings"
        assert memory.category == "triggers"
        assert memory.importance_score == 0.8


def test_get_user_memories():
    """Test retrieving user memories."""
    # Import here to apply patch
    from src.mental_health_coach.services.rag.conversation_memory import ConversationMemoryService
    
    # Setup
    mock_db = Mock()
    mock_user = MockUser(id=1)
    
    # Create a simpler solution with direct return of the mock query result
    mock_memories = [
        Mock(
            id=1,
            user_id=1,
            conversation_id=1,
            content="User mentioned having anxiety in social settings",
            category="triggers",
            importance_score=0.8,
            created_at=datetime.now() - timedelta(days=10)
        ),
        Mock(
            id=2,
            user_id=1,
            conversation_id=2,
            content="User feels depressed when alone for long periods",
            category="triggers",
            importance_score=0.9,
            created_at=datetime.now() - timedelta(days=5)
        )
    ]
    
    # Setup a more straightforward mock structure
    mock_db.query = Mock()
    mock_db.query().filter = Mock()
    mock_db.query().filter().filter = Mock()
    mock_db.query().filter().filter().order_by = Mock()
    mock_db.query().filter().filter().order_by().limit = Mock()
    mock_db.query().filter().filter().order_by().limit().all = Mock(return_value=mock_memories)
    
    # Create service with mock DB
    service = ConversationMemoryService(db=mock_db, user=mock_user)
    
    # Patch the models for the query
    with patch('src.mental_health_coach.models.conversation.ImportantMemory'):
        memories = service.get_important_memories()
    
    # Verify that memories were retrieved
    assert len(memories) == 2
    assert memories[0].content == "User mentioned having anxiety in social settings"
    assert memories[1].content == "User feels depressed when alone for long periods" 