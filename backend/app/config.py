import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv(".env")
load_dotenv("../.env")
load_dotenv("backend/.env")

from pydantic_settings import BaseSettings

DEFAULT_DB_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jansahay.db")).replace("\\", "/")
DEFAULT_SECRET_KEY = "jansahay-civic-secret-key-presentation-2026-production-ready"

class Settings(BaseSettings):
    PROJECT_NAME: str = "JanSahay AI Government Scheme Recommendation System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    APP_ENV: str = os.getenv("APP_ENV", "development").lower()
    ENABLE_DEMO_ACCOUNTS: bool = os.getenv(
        "ENABLE_DEMO_ACCOUNTS",
        "true" if os.getenv("APP_ENV", "development").lower() != "production" else "false",
    ).lower() in {"1", "true", "yes"}
    ADMIN_BOOTSTRAP_EMAIL: str = os.getenv("ADMIN_BOOTSTRAP_EMAIL", "")
    ADMIN_BOOTSTRAP_PASSWORD: str = os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "")
    
    # Optional LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Host & Port
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # CORS
    CORS_ALLOWED_ORIGINS: str = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    )

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()

if settings.APP_ENV == "production":
    if settings.SECRET_KEY == DEFAULT_SECRET_KEY or len(settings.SECRET_KEY) < 32:
        raise RuntimeError("Production requires a unique SECRET_KEY of at least 32 characters.")
    if not settings.CORS_ALLOWED_ORIGINS.strip() or "*" in settings.CORS_ALLOWED_ORIGINS:
        raise RuntimeError("Production requires explicit CORS_ALLOWED_ORIGINS; wildcards are not allowed.")
    if settings.ADMIN_BOOTSTRAP_PASSWORD and len(settings.ADMIN_BOOTSTRAP_PASSWORD) < 12:
        raise RuntimeError("ADMIN_BOOTSTRAP_PASSWORD must be at least 12 characters.")
    if settings.ENABLE_DEMO_ACCOUNTS:
        raise RuntimeError("ENABLE_DEMO_ACCOUNTS must be false in production.")
