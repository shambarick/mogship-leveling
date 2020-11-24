from fastapi import APIRouter

from mogship_leveling.api.api_v1.endpoints import routes

api_router = APIRouter()
api_router.include_router(routes.router, prefix="/routes")
