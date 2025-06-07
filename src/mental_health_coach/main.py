"""Main application module for the AI mental health coach.

This module sets up the FastAPI application, database, middleware, and routes.
"""

import os
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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
from src.mental_health_coach.database import Base, engine, init_db

# Load environment variables
load_dotenv()

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="AI Mental Health Coach API",
    description="API for an AI-powered mental health coaching platform",
    version="0.1.0",
)

# Configure CORS
allowed_origins = os.getenv("FRONTEND_URL", "http://localhost:3000").split(",")
if os.getenv("ENVIRONMENT") == "development":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint.
    
    Returns:
        Dict[str, Any]: Dictionary with service status.
    """
    return {"status": "ok", "service": "ai-mental-health-coach"} 