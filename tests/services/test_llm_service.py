"""Tests for the LLM service."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
import os
import json

from src.mental_health_coach.services.llm_service import LLMService, DEFAULT_SYSTEM_PROMPT

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create a mock OpenAI client.
    
    Returns:
        MagicMock: A mock OpenAI client.
    """
    with patch("src.mental_health_coach.services.llm_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock chat completions
        mock_chat = MagicMock()
        mock_client.chat = mock_chat
        
        # Mock completions.create
        mock_completions = MagicMock()
        mock_chat.completions = mock_completions
        
        # Mock create method response
        mock_response = MagicMock()
        mock_completions.create.return_value = mock_response
        
        # Mock choices
        mock_choice = MagicMock()
        mock_choice.message.content = "This is a mock AI response."
        mock_response.choices = [mock_choice]
        
        yield mock_client


def test_generate_response(mock_openai_client: MagicMock) -> None:
    """Test generating a response with the LLM service.
    
    Args:
        mock_openai_client: Mock OpenAI client.
    """
    # Create an LLM service with a mock API key
    llm_service = LLMService(api_key="test_api_key")
    
    # Create test data
    user_message = "Hello, I'm feeling anxious today."
    conversation_history = [
        {"is_from_user": True, "content": "I've been struggling with anxiety."},
        {"is_from_user": False, "content": "I'm sorry to hear that. Can you tell me more?"},
    ]
    
    # Generate a response
    response = llm_service.generate_response(
        user_message=user_message,
        conversation_history=conversation_history,
    )
    
    # Assert that the OpenAI client was called correctly
    mock_openai_client.chat.completions.create.assert_called_once()
    call_args = mock_openai_client.chat.completions.create.call_args[1]
    
    # Check that the model is set correctly
    assert call_args["model"] == "gpt-4.1-mini-2025-04-14"
    
    # Check that the messages include system prompt, conversation history, and user message
    messages = call_args["messages"]
    assert len(messages) >= 3  # At least system prompt + conversation history (2) + user message
    assert messages[0]["role"] == "system"  # First message should be system prompt
    
    # Check the last message is the user message
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == user_message
    
    # Check the response is returned correctly
    assert response == "This is a mock AI response."


def test_extract_important_memory(mock_openai_client: MagicMock) -> None:
    """Test extracting important memories with the LLM service.
    
    Args:
        mock_openai_client: Mock OpenAI client.
    """
    # Set up the mock response for memory extraction
    mock_choice = MagicMock()
    mock_choice.message.content = '{"content": "User experiences anxiety when in crowded places", "category": "triggers", "importance_score": 0.8}'
    mock_openai_client.chat.completions.create.return_value.choices = [mock_choice]
    
    # Create an LLM service with a mock API key
    llm_service = LLMService(api_key="test_api_key")
    
    # Create test conversation history
    conversation_history = [
        {"is_from_user": True, "content": "I notice I get really anxious when I'm in crowded places."},
        {"is_from_user": False, "content": "That sounds difficult. How do you cope with that?"},
        {"is_from_user": True, "content": "I try to focus on my breathing, but sometimes I have to leave."},
    ]
    
    # Extract a memory
    memory = llm_service.extract_important_memory(
        conversation_history=conversation_history,
    )
    
    # Assert that the OpenAI client was called correctly
    mock_openai_client.chat.completions.create.assert_called_once()
    call_args = mock_openai_client.chat.completions.create.call_args[1]
    
    # Check that memory extraction uses JSON response format
    assert call_args.get("response_format", {}).get("type") == "json_object"
    
    # Check the extracted memory
    assert memory is not None
    assert memory["content"] == "User experiences anxiety when in crowded places"
    assert memory["category"] == "triggers"
    assert memory["importance_score"] == 0.8


def test_generate_response_with_error(mock_openai_client: MagicMock) -> None:
    """Test error handling in generate_response.
    
    Args:
        mock_openai_client: Mock OpenAI client.
    """
    # Set up the mock to raise an exception
    mock_openai_client.chat.completions.create.side_effect = Exception("API error")
    
    # Create an LLM service with a mock API key
    llm_service = LLMService(api_key="test_api_key")
    
    # Generate a response
    response = llm_service.generate_response(
        user_message="Hello",
        conversation_history=[],
    )
    
    # Check that an error message is returned
    assert "I'm sorry, I'm having trouble" in response


class TestLLMService:
    """Tests for the LLMService class."""
    
    def test_init_with_api_key(self):
        """Test initializing LLMService with an API key."""
        # Setup
        api_key = "test_api_key"
        
        # Mock OpenAI client
        with patch('src.mental_health_coach.services.llm_service.OpenAI') as mock_openai:
            # Create service
            service = LLMService(api_key=api_key)
            
            # Verify OpenAI client was created with API key
            mock_openai.assert_called_once_with(api_key=api_key)
            
            # Verify model name
            assert service.model == "gpt-4.1-mini-2025-04-14"
    
    def test_init_with_env_var(self):
        """Test initializing LLMService with API key from environment."""
        # Setup - mock environment variable
        test_api_key = "env_api_key"
        with patch.dict(os.environ, {"OPENAI_API_KEY": test_api_key}):
            # Mock OpenAI client
            with patch('src.mental_health_coach.services.llm_service.OpenAI') as mock_openai:
                # Create service without explicit API key
                service = LLMService()
                
                # Verify OpenAI client was created with API key from env
                mock_openai.assert_called_once_with(api_key=test_api_key)
    
    def test_init_without_api_key(self):
        """Test initializing LLMService without API key raises error."""
        # Setup - ensure environment variable is not set
        with patch.dict(os.environ, {}, clear=True):
            # Verify error is raised
            with pytest.raises(ValueError) as excinfo:
                LLMService()
            
            # Check error message
            assert "OpenAI API key not provided" in str(excinfo.value)
    
    @patch('src.mental_health_coach.services.llm_service.OpenAI')
    def test_generate_response_formal_session(self, mock_openai_class):
        """Test generating a response for a formal session."""
        # Setup
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mock completion response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create service and generate response
        service = LLMService(api_key="test_key")
        response = service.generate_response(
            user_message="Hello",
            conversation_history=[],
            is_formal_session=True
        )
        
        # Verify response
        assert response == "Test response"
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        
        # Get the args from the call
        call_args = mock_client.chat.completions.create.call_args[1]
        messages = call_args["messages"]
        
        # Verify system prompt
        assert messages[0]["role"] == "system"
        assert DEFAULT_SYSTEM_PROMPT in messages[0]["content"]
        assert "SESSION_MODE = formal" in messages[0]["content"]
    
    @patch('src.mental_health_coach.services.llm_service.OpenAI')
    def test_generate_response_casual_session(self, mock_openai_class):
        """Test generating a response for a casual session."""
        # Setup
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mock completion response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create service and generate response
        service = LLMService(api_key="test_key")
        response = service.generate_response(
            user_message="Hello",
            conversation_history=[],
            is_formal_session=False
        )
        
        # Verify response
        assert response == "Test response"
        
        # Get the args from the call
        call_args = mock_client.chat.completions.create.call_args[1]
        messages = call_args["messages"]
        
        # Verify system prompt
        assert "SESSION_MODE = casual" in messages[0]["content"]
    
    @patch('src.mental_health_coach.services.llm_service.OpenAI')
    def test_generate_response_with_crisis(self, mock_openai_class):
        """Test generating a response with crisis detection."""
        # Setup
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mock completion response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Crisis response"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create service and generate response
        service = LLMService(api_key="test_key")
        response = service.generate_response(
            user_message="I feel hopeless",
            conversation_history=[],
            crisis_detected=True
        )
        
        # Verify response
        assert response == "Crisis response"
        
        # Get the args from the call
        call_args = mock_client.chat.completions.create.call_args[1]
        messages = call_args["messages"]
        
        # Verify system prompt
        assert "CRISIS_FLAG = true" in messages[0]["content"]
    
    @patch('src.mental_health_coach.services.llm_service.OpenAI')
    def test_extract_important_memory(self, mock_openai_class):
        """Test extracting important memory from conversation."""
        # Setup
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Create mock memory response
        memory_data = {
            "content": "User mentioned having anxiety in social situations",
            "category": "triggers",
            "importance_score": 0.8
        }
        
        # Mock completion response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(memory_data)
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create service and extract memory
        service = LLMService(api_key="test_key")
        memory = service.extract_important_memory(
            conversation_history=[
                {"is_from_user": True, "content": "I get anxious at parties"},
                {"is_from_user": False, "content": "That sounds difficult. When did you first notice this?"}
            ]
        )
        
        # Verify memory extraction
        assert memory["content"] == "User mentioned having anxiety in social situations"
        assert memory["category"] == "triggers"
        assert memory["importance_score"] == 0.8
        
        # Verify API call
        call_args = mock_client.chat.completions.create.call_args[1]
        
        # Check that response format is set to JSON
        assert call_args["response_format"] == {"type": "json_object"} 