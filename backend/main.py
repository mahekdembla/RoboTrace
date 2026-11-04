"""RoboTrace 3D — Main FastAPI Application.

Initializes FastAPI, registers CORS for frontend (http://localhost:5173),
initializes the SQLite database, configures exception handlers, Swagger documentation,
registers REST and WebSocket routers, and manages live simulation broadcasting.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

# Ensure both project root and backend directory are in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

for path_str in (str(ROOT_DIR), str(BACKEND_DIR)):
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.db import close_db, init_db, get_db_session
from database.models import Mission as DBMission, Agent as DBAgent
from backend.api.routes import router as api_router, backend as backend_state
from backend.api.websocket import router as ws_router, ws_manager

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("robotrace.main")


# ---------------------------------------------------------------------------
# Application Lifespan (Startup & Shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Clean startup and shutdown lifecycle management.

    Initializes SQLite database tables on startup, starts WebSocket
    telemetry broadcast loop, and cleanly disposes all resources on shutdown.
    """
    logger.info("Initializing RoboTrace 3D SQLite database...")
    try:
        await init_db()
        logger.info("SQLite database tables verified / created successfully.")
        async with get_db_session() as session:
            stmt = select(DBMission).where(DBMission.id == 1)
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing is None:
                m1 = DBMission(
                    id=1,
                    name="Warehouse Alpha Run",
                    description="Full warehouse cycle: pickup, inspect, transport.",
                    status="PENDING",
                    environment="warehouse_floor_1",
                )
                await session.merge(m1)
                for agent_name in ["ATLAS", "NOVA", "TITAN"]:
                    await session.merge(DBAgent(
                        mission_id=1,
                        name=agent_name,
                        agent_type=agent_name,
                        status="IDLE",
                    ))
    except Exception as exc:
        logger.error("Failed to initialize database: %s", exc, exc_info=True)
        raise

    # Start WebSocket live telemetry broadcasting
    try:
        ws_manager.start_broadcasting(backend_state.simulation)
    except Exception as exc:
        logger.warning("Could not start background telemetry broadcast: %s", exc)

    yield

    logger.info("Shutting down RoboTrace 3D backend...")
    ws_manager.stop_broadcasting()
    try:
        await close_db()
        logger.info("Database connections cleanly closed.")
    except Exception as exc:
        logger.error("Error during database shutdown: %s", exc, exc_info=True)


# ---------------------------------------------------------------------------
# FastAPI Initialization & Swagger Documentation
# ---------------------------------------------------------------------------

tags_metadata = [
    {
        "name": "System",
        "description": "Core system status, health checks, and API information.",
    },
    {
        "name": "Agents",
        "description": "Autonomous robotic agents: ATLAS, NOVA, and TITAN.",
    },
    {
        "name": "Missions",
        "description": "Mission orchestration, configurations, and lifecycle actions.",
    },
    {
        "name": "Trajectory",
        "description": "Spatial trajectory tracking (Z-up), observations, decisions, and outcomes.",
    },
    {
        "name": "Errors",
        "description": "AgentGuard automated error logging and suggested categories.",
    },
    {
        "name": "Annotations",
        "description": "Human review records and corrected error categories.",
    },
    {
        "name": "Analytics",
        "description": "Aggregated metrics for missions, agents, and error categories.",
    },
]

app = FastAPI(
    title="RoboTrace 3D API",
    description=(
        "RoboTrace 3D — Autonomous robotics simulation, spatial tracing, "
        "and error annotation platform backend."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------

# Primary support for React frontend development on localhost:5173
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Allow additional origins from environment variable if present
env_cors = os.getenv("CORS_ORIGINS")
if env_cors:
    for origin in env_cors.split(","):
        clean_origin = origin.strip()
        if clean_origin and clean_origin not in allowed_origins:
            allowed_origins.append(clean_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle standard HTTP exceptions with consistent detail JSON format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic request validation errors."""
    logger.warning("Validation error on %s %s: %s", request.method, request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request validation error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors safely without leaking internal details."""
    logger.error("Database error on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again."},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected server exceptions."""
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# ---------------------------------------------------------------------------
# Root & Health Endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["System"], summary="API Root Overview")
async def root():
    """Return welcome message and documentation links."""
    return {
        "app": "RoboTrace3D",
        "version": "1.0.0",
        "message": "Welcome to RoboTrace 3D API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_url": "/health",
    }


@app.get("/health", tags=["System"], summary="System health check")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "app": "RoboTrace3D",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Register API & WebSocket Routers
# ---------------------------------------------------------------------------

app.include_router(api_router)
app.include_router(ws_router)


# ---------------------------------------------------------------------------
# Direct Execution Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
