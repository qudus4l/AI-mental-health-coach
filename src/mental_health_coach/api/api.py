"""API router that combines all endpoints."""

from fastapi import APIRouter

from src.mental_health_coach.api.endpoints import auth, users, conversations, homework, voice, dashboard, crisis, memory, emergency

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(homework.router, prefix="/homework", tags=["homework"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(crisis.router, prefix="/crisis", tags=["crisis"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(emergency.router, prefix="/emergency", tags=["emergency"]) 