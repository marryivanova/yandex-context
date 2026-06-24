from fastapi import APIRouter

from src.api.endpoints import bookings, health

api_router = APIRouter()

api_router.include_router(bookings.router)
api_router.include_router(health.router)
