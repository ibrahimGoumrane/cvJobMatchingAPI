from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add cvJobMatching to sys.path to allow internal imports within that module to work
# This addresses the issue where cvJobMatching imports 'pipeline' assuming it is in the root
sys.path.append(str(Path(__file__).resolve().parent.parent / "cvJobMatching"))

# Initialize logging
from api.config.logging_config import setup_logging, get_logger
setup_logging()
logger = get_logger(__name__)

from api.controller.job_controller import router as job_router
from api.socket.job_socket import router as socket_router
from api.config.database import engine
from api.entity.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    logger.info("[STARTUP] Starting AI Recruiter API...")
    logger.info("[STARTUP] Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("[STARTUP] Database tables initialized successfully")
    logger.info("[STARTUP] Application startup complete")
    yield
    # Shutdown: (optional cleanup)
    logger.info("[SHUTDOWN] Shutting down AI Recruiter API...")

app = FastAPI(title="AI Recruiter API", version="1.0", lifespan=lifespan)

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors (422) with detailed logging"""
    errors = exc.errors()
    body = await request.body()
    logger.error(f"[ERROR] Validation Error on {request.method} {request.url.path}")
    logger.error(f"   Errors: {errors}")
    logger.error(f"   Body: {body.decode('utf-8') if body else 'Empty'}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": 422,
            "message": "Validation Error",
            "data": {
                "detail": errors
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"[ERROR] Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": 500,
            "message": f"Internal Server Error: {str(exc)}",
            "data": None
        }
    )

# CORS Configuration
origins = ["*"] # Adjust this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_router, prefix="/api/v1")
app.include_router(socket_router)
