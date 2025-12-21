from fastapi import FastAPI
from api.controller.job_controller import router as job_router
from api.socket.job_socket import router as socket_router

app = FastAPI(title="AI Recruiter API", version="1.0")

app.include_router(job_router, prefix="/api/v1")
app.include_router(socket_router)
