# AI Mental Health Coach

An AI-powered mental health coaching platform that provides support for anxiety and depression through voice-enabled conversations, maintains contextual memory across sessions, and delivers structured therapeutic interventions using evidence-based approaches.

## Features

- 24/7 access to mental health support
- Voice-enabled conversations for natural interaction
- Personalized memory that remembers progress, triggers, and coping strategies
- Structured support combining casual chat with formal therapeutic sessions
- Evidence-based approaches using CBT and behavioral activation techniques
- Progressive care with homework assignments and progress tracking

## Project Structure

```
AI-mental-health-coach/
├── src/                   # Source code
│   └── mental_health_coach/   # Main package
│       ├── api/           # API endpoints
│       ├── auth/          # Authentication functionality
│       ├── models/        # Database models
│       ├── schemas/       # Pydantic schemas
│       ├── services/      # Business logic services
│       └── voice/         # Voice processing functionality
├── tests/                 # Test suite
├── docs/                  # Documentation
├── config/                # Configuration files
└── scripts/               # Utility scripts
```

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js (for web interface)
- Optional: Audio dependencies for voice features
  - PyAudio
  - SpeechRecognition
  - pyttsx3

### Installation

1. Clone the repository:
   ```
   git clone [repository-url]
   cd AI-mental-health-coach
   ```

2. Set up virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -e .
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Application

For development:
```
python -m src.mental_health_coach.app
```

### Running Tests

```
pytest
```

## Voice Conversation API

The platform includes a WebSocket-based API for voice conversations:

- `/api/voice/conversations` - Start a new voice conversation
- `/api/voice/conversations/{id}/end` - End a voice conversation
- `/api/voice/ws/{user_id}` - WebSocket endpoint for real-time voice communication

## License

[License information]

## Contributors

[Contributor information] 