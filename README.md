# AI Mental Health Coach

An AI-powered mental health coaching platform that provides support for anxiety and depression through text-based conversations, maintains contextual memory across sessions, and delivers structured therapeutic interventions using evidence-based approaches.

## Phase 1: Text-Based Coach MVP

This is the initial implementation of the AI Mental Health Coach focusing on:

- Web app with text chat interface
- User authentication (email/social login)
- Conversation storage
- Important memory tracking
- CBT-based AI coaching
- Homework assignment features

## Tech Stack

- **Backend:** TypeScript + Node 18, Fastify, Prisma ORM, PostgreSQL
- **LLM Integration:** OpenAI API
- **Frontend:** Next.js 14, React 18, Tailwind CSS
- **Authentication:** NextAuth.js (email + Google)
- **Testing:** Vitest + Supertest (API) and React Testing Library (UI)
- **DevOps:** Docker Compose, GitHub Actions CI

## Getting Started

### Prerequisites

- Node.js 18 or later
- Docker and Docker Compose
- OpenAI API key

### Installation

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in the required environment variables
3. Install dependencies:

```bash
npm install
```

4. Start the development environment:

```bash
docker-compose up --build
```

The application will be available at:
- Web app: http://localhost:3000
- API: http://localhost:3001

### Development

```bash
# Start development servers
npm run dev

# Run tests
npm run test

# Run linting
npm run lint

# Build for production
npm run build

# Seed the database with demo data
npm run db:seed
```

## Future Phases

### Phase 2: Voice Integration

- Browser-based speech-to-text/text-to-speech
- Voice conversation capabilities
- Conversation transcription

### Phase 3: Session Structure & Safety

- Session scheduling
- Formal vs casual chat distinction
- Crisis detection improvements
- Homework tracking enhancements

## Project Structure

```
apps/web      # Next.js frontend application
apps/api      # Fastify backend API
packages/db   # Prisma schema & database migrations
packages/core # Shared types, memory utils, CBT prompts
docs/         # Documentation
compliance/   # Compliance documentation (placeholder)
```

## License

Proprietary - All Rights Reserved 