import uuid
import asyncio
from fastapi import UploadFile
from api.entity.job_processing import JobProcessing

async def run_evaluation(job_id: str, cv_path: str, jd_path: str):
    # call cvJobMatching pipeline here
    pass

async def create_job(user_id: int, cv: UploadFile, jobdesc: UploadFile) -> dict:
    job_id = str(uuid.uuid4())
    
    # Logic to save files to storage and get paths
    cv_path = f"uploads/{job_id}_{cv.filename}"
    jd_path = f"uploads/{job_id}_{jobdesc.filename}"
    
    # Trigger the evaluation pipeline as a background task
    asyncio.create_task(run_evaluation(job_id, cv_path, jd_path))
    
    return {
        "job_id": job_id,
        "status": "PROCESSING"
    }

async def get_all_jobs() -> list[JobProcessing]:
    # Logic to retrieve jobs from the database
    return []

async def get_file_content(file_path: str):
    # Logic to retrieve file from storage
    return file_path
