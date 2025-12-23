import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
from api.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Map job_id to active websocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        # If a connection exists for this job_id, close it or overwrite it
        # Assuming last connection wins or simple replacement
        if job_id in self.active_connections:
            logger.warning(f"[WS] Replacing existing connection for job {job_id}")
            # Optional: gracefully close the old one if needed, or just let it be GC'd/closed by logic
            pass
        self.active_connections[job_id] = websocket
        logger.info(f"[WS] Client connected for job {job_id}")

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            if self.active_connections[job_id] == websocket:
                del self.active_connections[job_id]
                logger.info(f"[WS] Client disconnected for job {job_id}")

    async def send_progress(self, job_id: str, message: str, progress: int):
        if job_id in self.active_connections:
            payload = {
                "type": "PROGRESS",
                "job_id": job_id,
                "message": message,
                "progress": progress
            }
            connection = self.active_connections[job_id]
            try:
                await connection.send_json(payload)
                logger.debug(f"[WS] Sent progress to job {job_id}: {message} ({progress}%)")
            except Exception as e:
                # Handle broken connections gracefully
                logger.error(f"[ERROR] WebSocket - Failed to send message to job {job_id}: {e}")
                pass
        else:
            logger.debug(f"[WS] No active connection for job {job_id}, skipping progress update")

manager = ConnectionManager()

@router.websocket("/ws/jobs/{job_id}")
async def job_websocket(websocket: WebSocket, job_id: str):
    logger.info(f"[WS] New connection request for job {job_id}")
    await manager.connect(websocket, job_id)
    try:
        # Send initial status
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "job_id": job_id, 
            "message": "Connected to job stream"
        })
        logger.info(f"[WS] Connection established for job {job_id}")
        while True:
            # Keep connection alive, we don't expect messages from client
            # Just wait indefinitely until disconnect
            await asyncio.sleep(60) 
    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected for job {job_id}")
        manager.disconnect(websocket, job_id)
