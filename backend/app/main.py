import os

from fastapi import FastAPI
from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.config import settings
from app.api import api_router
from app.database.session import Base, engine, SessionLocal, ensure_schemas
from app.models.models import Scheme, User, AuditLog
from app.database.seed import seed_database
from app.services.auth_service import hash_password

# Create tables
ensure_schemas()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Based Government Scheme Recommendation System for Indian Citizens"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def enforce_cookie_auth_origin(request: Request, call_next):
    unsafe_method = request.method in {"POST", "PUT", "PATCH", "DELETE"}
    has_cookie_session = bool(request.cookies.get("jansahay_session"))
    has_bearer = request.headers.get("authorization", "").lower().startswith("bearer ")
    allowed_origins = {
        origin.strip()
        for origin in settings.CORS_ALLOWED_ORIGINS.split(",")
        if origin.strip()
    }
    if unsafe_method and has_cookie_session and not has_bearer:
        origin = request.headers.get("origin")
        if not origin or origin not in allowed_origins:
            return JSONResponse(status_code=403, content={"detail": "Request origin is not allowed."})
    return await call_next(request)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        if settings.APP_ENV == "production":
            demo_emails = ["admin@jansahay.gov.in", "demo@citizen.in"]
            disabled_demo_count = db.query(User).filter(
                User.email.in_(demo_emails), User.is_active == True
            ).update({User.is_active: False}, synchronize_session=False)
            if disabled_demo_count:
                db.add(AuditLog(
                    action="DEMO_ACCOUNTS_DISABLED",
                    entity_type="User",
                    details=f"Disabled {disabled_demo_count} shared development demo account(s) in production.",
                ))
                db.commit()

            has_active_admin = db.query(User).filter(
                User.is_admin == True, User.is_active == True
            ).first()
            if not has_active_admin and settings.ADMIN_BOOTSTRAP_EMAIL and settings.ADMIN_BOOTSTRAP_PASSWORD:
                bootstrap_admin = db.query(User).filter(
                    User.email == settings.ADMIN_BOOTSTRAP_EMAIL
                ).first()
                if bootstrap_admin:
                    bootstrap_admin.is_active = True
                    bootstrap_admin.is_admin = True
                    bootstrap_admin.hashed_password = hash_password(settings.ADMIN_BOOTSTRAP_PASSWORD)
                else:
                    db.add(User(
                        email=settings.ADMIN_BOOTSTRAP_EMAIL,
                        hashed_password=hash_password(settings.ADMIN_BOOTSTRAP_PASSWORD),
                        full_name="JanSahay Administrator",
                        is_active=True,
                        is_admin=True,
                    ))
                db.commit()
                has_active_admin = db.query(User).filter(
                    User.email == settings.ADMIN_BOOTSTRAP_EMAIL,
                    User.is_admin == True,
                    User.is_active == True,
                ).first()

            if not has_active_admin:
                raise RuntimeError(
                    "Production requires an active administrator. Set ADMIN_BOOTSTRAP_EMAIL and "
                    "ADMIN_BOOTSTRAP_PASSWORD for first startup."
                )

        # Automatically seed the scheme catalog if empty.
        count = db.query(Scheme).count()
        if count == 0:
            print("Database empty. Auto-seeding initial schemes...")
            seed_database()
        else:
            print(f"Database ready with {count} schemes.")
    finally:
        db.close()

# Mount API
app.include_router(api_router, prefix=settings.API_V1_STR)

# In the Render container, serve the Vite build from the same origin as the
# API. This keeps cookie authentication and /api requests on one host.
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.isdir(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

@app.get("/")
def root():
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "portal_name": "JanSahay"
    }

@app.get("/api/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "service": "JanSahay AI Engine",
            "database": "connected",
            "database_engine": engine.dialect.name,
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "database": "disconnected"},
        )


if os.path.isfile(os.path.join(FRONTEND_DIST, "index.html")):
    @app.get("/{frontend_path:path}", include_in_schema=False)
    def frontend_routes(frontend_path: str):
        # Client-side routes (e.g. /dashboard) should load the SPA entrypoint.
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
