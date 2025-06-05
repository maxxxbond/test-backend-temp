from fastapi import APIRouter

from app.api.endpoints import auth, videos, users, course

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(course.router, prefix="/course", tags=["course-dashboard"])
