"""Main application module for the AI mental health coach.

This module sets up the FastAPI application, database, middleware, and routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.mental_health_coach.api import (
    auth, 
    users, 
    conversations, 
    homework, 
    crisis, 
    dashboard,
    voice, 
    emergencies,
    assessments,
)
from src.mental_health_coach.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="AI Mental Health Coach API",
    description="API for an AI-powered mental health coaching platform",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(homework.router)
app.include_router(crisis.router)
app.include_router(dashboard.router)
app.include_router(voice.router)
app.include_router(emergencies.router)
app.include_router(assessments.router)


@app.get("/", tags=["health"])
async def health_check():
    """Basic health check endpoint.
    
    Returns:
        Dictionary with service status.
    """
    return {"status": "ok", "service": "ai-mental-health-coach"} 