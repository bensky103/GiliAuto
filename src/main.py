"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.core.config import get_settings
from src.core.logging import get_logger, setup_logging
from src.db.session import init_db
from src.routers import monday, meta
from src.services.scheduler import scheduler_service

settings = get_settings()
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Starting Lead Automation Service")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Start scheduler
    scheduler_service.start()
    logger.info("Scheduler started")

    yield

    # Stop scheduler
    scheduler_service.stop()
    logger.info("Scheduler stopped")

    logger.info("Shutting down Lead Automation Service")


app = FastAPI(
    title="Lead Automation Service",
    description="Automation service connecting Monday.com and WhatsApp",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# Include routers
app.include_router(monday.router)
app.include_router(meta.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Lead Automation Service is running"}


@app.post("/admin/trigger-scheduler")
async def trigger_scheduler(secret: str = "") -> dict[str, str]:
    """
    Manually trigger the scheduler to process pending follow-ups.
    
    Requires the admin secret as a query parameter for security.
    Usage: POST /admin/trigger-scheduler?secret=your-admin-secret
    """
    if secret != settings.admin_secret:
        return {"status": "error", "message": "Invalid secret"}
    
    await scheduler_service.process_pending_followups()
    return {"status": "triggered", "message": "Scheduler job executed"}


@app.post("/admin/sync-monday")
async def sync_monday(secret: str = "") -> dict[str, str]:
    """
    Manually trigger sync of new leads from Monday.com.
    
    Requires the admin secret as a query parameter for security.
    Usage: POST /admin/sync-monday?secret=your-admin-secret
    """
    if secret != settings.admin_secret:
        return {"status": "error", "message": "Invalid secret"}
    
    await scheduler_service.sync_new_leads_from_monday()
    return {"status": "triggered", "message": "Monday sync job executed"}
