# AI Mental Health Coach

An AI-powered mental health coaching platform designed to provide support for anxiety and depression through conversational AI.

## Features

- **Conversation System**: Text-based chat interface with AI-generated responses
- **Memory Management**: Remembers important details from past conversations using RAG (Retrieval Augmented Generation)
- **Crisis Detection**: Identifies potential crisis situations and provides appropriate resources
- **Therapeutic Framework**: Based on Cognitive Behavioral Therapy (CBT) principles
- **Session Management**: Distinguishes between formal therapy sessions and casual chats
- **Emergency Contact System**: Manages emergency contacts and crisis notifications

## Technical Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: SQLite (development), PostgreSQL (production)
- **LLM Integration**: OpenAI's `gpt-4.1-mini-2025-04-14` model
- **Memory System**: TF-IDF based retrieval for conversation context
- **Authentication**: JWT-based authentication

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-mental-health-coach.git
   cd ai-mental-health-coach
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp env.example .env
   ```
   Edit `.env` to add your OpenAI API key and other configuration.

5. Initialize the database:
   ```
   alembic upgrade head
   ```

6. Run the application:
   ```
   uvicorn src.mental_health_coach.app:app --reload
   ```

7. Open the API documentation at http://localhost:8000/docs

## Usage

1. Register a user account using the `/api/users/` endpoint
2. Log in to get an access token with `/api/auth/login`
3. Create a conversation with `/api/conversations/`
4. Send messages to the conversation with `/api/conversations/{id}/messages`

## LLM Integration

The system uses OpenAI's `gpt-4.1-mini-2025-04-14` model to generate responses:

- When a user sends a message, the system performs crisis detection
- If no crisis is detected, the LLM generates a therapeutic response
- The system extracts important memories from the conversation
- Context from past conversations is retrieved using RAG to improve responses

To use your own model:
1. Set the `OPENAI_API_KEY` in your `.env` file
2. Optionally modify the model name in `src/mental_health_coach/services/llm_service.py`

## Project Structure

- `src/mental_health_coach/`: Main package
  - `api/`: API endpoints and routers
  - `models/`: Database models
  - `schemas/`: Pydantic schemas for validation
  - `services/`: Business logic and services
    - `rag/`: Retrieval Augmented Generation system
    - `crisis_detection.py`: Crisis detection service
    - `emergency_contact.py`: Emergency contact management
    - `llm_service.py`: LLM integration service
  - `auth/`: Authentication and security
  - `app.py`: Main application entry point

## License

[MIT License](LICENSE) 