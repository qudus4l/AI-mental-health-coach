# AI Mental Health Coach - Architecture

## System Overview

The AI Mental Health Coach is a full-stack application designed to provide mental health support through text-based conversations, with a focus on anxiety and depression. The application follows a modular architecture to support future expansion into voice interactions, scheduling, and crisis detection.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Web Frontend  │────▶│    API Server   │────▶│  Database Layer │
│   (Next.js 14)  │     │    (Fastify)    │     │   (PostgreSQL)  │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └─────────────────┘
         │                       │
         │                       │
         │               ┌───────▼───────┐     ┌─────────────────┐
         │               │               │     │                 │
         └──────────────▶│  Core Package │────▶│    OpenAI API   │
                         │ (Shared Logic) │     │                 │
                         │               │     └─────────────────┘
                         └───────┬───────┘
                                 │
                                 │
                         ┌───────▼───────┐
                         │               │
                         │ Memory System │
                         │               │
                         └───────────────┘
```

## Architecture Layers

### 1. Web Frontend (Next.js 14)
- **Purpose**: Provides the user interface for authentication, profile management, and chat interactions
- **Technology**: Next.js 14, React 18, Tailwind CSS
- **Key Components**:
  - Authentication flows (NextAuth.js)
  - Chat interface with message history
  - User profile management
  - Homework assignment tracking
  - Future placeholders for voice interface and session scheduling

### 2. API Server (Fastify)
- **Purpose**: Handles HTTP requests, business logic, and coordinates between the frontend, database, and LLM
- **Technology**: TypeScript, Node.js 18, Fastify
- **Key Components**:
  - REST API endpoints with OpenAPI 3.1 specification
  - Zod validation for request/response schemas
  - Authentication middleware
  - LLM interaction service
  - Memory management service

### 3. Database Layer (PostgreSQL + Prisma)
- **Purpose**: Stores user data, conversations, and important memories
- **Technology**: PostgreSQL, Prisma ORM
- **Key Components**:
  - User profiles (encrypted sensitive fields)
  - Conversation history
  - Important memories storage
  - Homework assignments
  - Data migrations and seeding

### 4. Core Package (Shared Logic)
- **Purpose**: Contains shared types, utilities, and business logic
- **Technology**: TypeScript
- **Key Components**:
  - TypeScript interfaces and types
  - CBT prompt templates
  - Memory utility functions
  - Encryption utilities
  - Testing utilities

### 5. Memory System
- **Purpose**: Manages storage and retrieval of important memories from conversations
- **Technology**: Repository pattern with PostgreSQL implementation
- **Key Components**:
  - Memory storage service
  - Memory retrieval service
  - Memory categorization
  - Repository interfaces for future vector database implementation

### 6. External Integrations
- **OpenAI API**: For LLM-based conversation processing and CBT implementation
- **NextAuth.js**: For email and social authentication

## Data Flow

1. **User Authentication**: 
   - User logs in through Next.js frontend using NextAuth.js
   - Session tokens are managed by NextAuth.js and passed to the API

2. **Conversation Flow**:
   - User submits a message through the frontend
   - Message is sent to the API server
   - API server processes the message, storing it in the database
   - The conversation context and relevant memories are retrieved
   - The message, context, and CBT prompt are sent to the OpenAI API
   - The AI response is processed, and any important memories are extracted
   - Response is returned to the frontend and displayed to the user

3. **Memory Management**:
   - After each user message, the system analyzes the conversation
   - Important insights are identified and stored as memories
   - Memories are categorized by type (trigger, coping, breakthrough, goal)
   - When needed, relevant memories are retrieved to provide context

4. **Homework Assignment**:
   - The LLM may suggest homework as part of its response
   - Homework assignments are stored in the database
   - User can view, track, and mark homework as complete

## Future Expansion

The architecture is designed with future phases in mind:

- **Phase 2**: Voice processing components will be added as separate services
- **Phase 3**: Session scheduling and structure will be implemented
- **Phase 4**: The memory system can be upgraded to use vector databases

## Security Considerations

- **Data Encryption**: Sensitive user data (user IDs, emails) are encrypted at rest
- **Authentication**: Secure token-based authentication with NextAuth.js
- **API Security**: Request validation, rate limiting, and CSRF protection
- **Privacy**: GDPR-compliant data handling with user data control

## Development and Deployment

- **Local Development**: Docker Compose for running the database, API, and web services
- **CI/CD**: GitHub Actions for linting, testing, and building
- **Testing**: Vitest for backend, React Testing Library for frontend
- **API Documentation**: OpenAPI 3.1 specification for all endpoints 