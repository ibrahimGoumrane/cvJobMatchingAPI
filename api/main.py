from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.controller.job_controller import router as job_router
from api.socket.job_socket import router as socket_router
from api.config.database import engine
from api.entity.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: (optional cleanup)

app = FastAPI(title="AI Recruiter API", version="1.0", lifespan=lifespan)

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
