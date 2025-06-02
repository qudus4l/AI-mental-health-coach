"""Main application module for the mental health coach."""

import logging
import os
from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from src.mental_health_coach.api.api import api_router
from src.mental_health_coach.database import init_db, check_and_update_schema

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Check for OpenAI API key
if not os.environ.get("OPENAI_API_KEY"):
    logger.warning(
        "OPENAI_API_KEY environment variable not found. "
        "LLM functionality will not work without a valid API key."
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events handler for startup and shutdown.
    
    Args:
        app: The FastAPI application.
    """
    # Startup
    logger.info("Starting up the application")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Double-check schema after initialization
    # This ensures we catch any schema issues even if they were missed during init_db
    check_and_update_schema()
    logger.info("Database schema verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down the application")


# Create FastAPI application
app = FastAPI(
    title="Mental Health Coach API",
    description="API for the AI-powered mental health coaching platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to specific allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> Any:
    """Global exception handler.
    
    Args:
        request: The request that caused the exception.
        exc: The exception that was raised.
        
    Returns:
        JSONResponse: A JSON response with error details.
    """
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )


@app.get("/")
def root() -> Any:
    """Root endpoint.
    
    Returns:
        dict: A simple welcome message.
    """
    return {"message": "Welcome to the Mental Health Coach API"}


if __name__ == "__main__":
    import uvicorn
    
    # Run the application with uvicorn
    uvicorn.run("src.mental_health_coach.app:app", host="0.0.0.0", port=8000, reload=True) 