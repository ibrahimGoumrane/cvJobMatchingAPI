from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws/jobs/{job_id}")
async def job_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()
    await websocket.send_json({
        "stage": "STARTED",
        "job_id": job_id
    })
