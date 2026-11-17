from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.schemes import router as schemes_router
from app.api.recommendations import router as rec_router
from app.api.eligibility import router as elig_router
from app.api.chat import router as chat_router
from app.api.admin import router as admin_router
from app.api.documents import router as documents_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(schemes_router)
api_router.include_router(rec_router)
api_router.include_router(elig_router)
api_router.include_router(chat_router)
api_router.include_router(admin_router)
api_router.include_router(documents_router)
