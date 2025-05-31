"""Main application module for the mental health coach."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.mental_health_coach.api.api import api_router
from src.mental_health_coach.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Mental Health Coach API",
    description="API for the AI-powered mental health coaching platform",
    version="0.1.0",
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


@app.on_event("startup")
def startup_event() -> None:
    """Application startup event.
    
    This function is called when the application starts up.
    It initializes the database and performs other startup tasks.
    """
    logger.info("Starting up the application")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
def shutdown_event() -> None:
    """Application shutdown event.
    
    This function is called when the application shuts down.
    """
    logger.info("Shutting down the application")


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