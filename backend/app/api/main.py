from fastapi import APIRouter

from app.api.routes import game

api_router = APIRouter()
api_router.include_router(game.router)
