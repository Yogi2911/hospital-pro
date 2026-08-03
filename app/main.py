import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from . import models
from .database import Base, engine, SessionLocal
from .routers import patients

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hospital-api")

# Creates tables on startup if they don't exist yet.
# For a production system prefer Alembic migrations instead of create_all().
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hospital API",
    description=(
        "Simple Patients CRUD service used across the Azure DevOps task guide "
        "(Docker/ACR, Container Apps, PostgreSQL + Key Vault, Application "
        "Insights, and API Management)."
    ),
    version="1.0.0",
    contact={"name": "Hospital API"},
)

# Open CORS for local/dev use. Tighten allow_origins before production use.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)


# ---------------------------------------------------------------------------
# Centralized error handling so the API never leaks a raw stack trace and
# every error comes back as consistent JSON.
# ---------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error on %s %s: %s", request.method, request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data.", "errors": exc.errors()},
    )


@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Database error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database error. Please try again later."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"], summary="Health check (used by Container Apps / App Gateway probes)")
def health_check():
    db_status = "up"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except SQLAlchemyError:
        db_status = "down"
    return {"status": "healthy", "database": db_status}
