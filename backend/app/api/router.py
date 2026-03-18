from fastapi import APIRouter

from app.api.routes import candles, health

api_router = APIRouter()
api_router.include_router(candles.router, tags=["candles"])
api_router.include_router(health.router, tags=["health"])
