import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

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
            # Optional: gracefully close the old one if needed, or just let it be GC'd/closed by logic
            pass
        self.active_connections[job_id] = websocket

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            if self.active_connections[job_id] == websocket:
                del self.active_connections[job_id]

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
            except Exception:
                # Handle broken connections gracefully
                pass

manager = ConnectionManager()

@router.websocket("/ws/jobs/{job_id}")
async def job_websocket(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    try:
        # Send initial status
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "job_id": job_id, 
            "message": "Connected to job stream"
        })
        while True:
            # Keep connection alive, we don't expect messages from client
            # Just wait indefinitely until disconnect
            await asyncio.sleep(60) 
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
