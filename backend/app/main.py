"""FastAPI application entry point.

Serves the REST API under /api and the static frontend from the frontend folder.
"""
import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import engine
from .migrations import upgrade_schema
from .routers import applications, certificates, citizens
from .services.approval import approval_worker
from .validation_errors import friendly_errors

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.ensure_dirs()
    upgrade_schema(engine)
    task = None
    if settings.approval_worker_enabled:
        task = asyncio.create_task(approval_worker())
    yield
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(
    title="Maharashtra Citizen Certificate Portal",
    description="Prototype REST API. Officer approval and payments are simulated by the system.",
    version="1.1.0",
    lifespan=lifespan,
)

app.include_router(certificates.router)
app.include_router(applications.router)
app.include_router(citizens.router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    """Return citizen-friendly, per-field messages instead of raw Pydantic text."""
    fields, general = friendly_errors(exc.errors())
    message = general or "Please correct the highlighted fields."
    return JSONResponse(status_code=422, content={"detail": {"message": message, "fields": fields}})


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "approval_delay_seconds": settings.approval_delay_seconds}


# Mounted last so /api routes take priority.
app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
