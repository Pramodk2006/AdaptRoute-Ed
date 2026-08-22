"""
AdaptRoute-Edu FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.utils.logger import logger, setup_logging

# ── Settings ───────────────────────────────────────────────────────────────────
settings = get_settings()

# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Startup and shutdown logic."""
    setup_logging()
    logger.info(
        f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting "
        f"[env={settings.ENVIRONMENT}]"
    )
    # Ensure all ORM tables exist — skipped in test environments where
    # get_db is overridden with an in-memory SQLite session.
    try:
        from app.database import Base, engine as real_engine
        import app.models  # noqa: F401 — registers all ORM models
        Base.metadata.create_all(bind=real_engine)
        logger.info("Database tables initialized successfully.")
    except Exception as exc:
        logger.warning(f"DB create_all skipped: {exc}")
    yield
    logger.info(f"👋 {settings.APP_NAME} shutting down.")


# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AdaptRoute-Edu: AI-powered Adaptive Intelligent Tutoring System. "
        "MVP stage — single LLM, no routing logic."
    ),
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url="/api/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
origins = settings.allowed_origins_list
if settings.DEBUG:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True if origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Exception Handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception on {request.method} {request.url}: {exc}")
    origin = request.headers.get("origin", "*")
    headers = {"Access-Control-Allow-Origin": origin} if origin else {}
    detail = str(exc) if settings.DEBUG else "An unexpected error occurred. Please try again later."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
        headers=headers,
    )

# ── Routers ────────────────────────────────────────────────────────────────────
from app.routers import auth, profile, roadmap, quiz, dashboard, routing, knowledge, socratic, rag  # noqa: E402

API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(profile.router, prefix=API_PREFIX)
app.include_router(roadmap.router, prefix=API_PREFIX)
app.include_router(quiz.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(routing.router, prefix=API_PREFIX)
app.include_router(knowledge.router, prefix=API_PREFIX)
app.include_router(socratic.router, prefix=API_PREFIX)
app.include_router(rag.router, prefix=API_PREFIX)

# ── Health Check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"], summary="Health check endpoint")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
