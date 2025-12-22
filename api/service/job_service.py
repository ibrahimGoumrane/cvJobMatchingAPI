import uuid
import asyncio
from fastapi import UploadFile
from api.entity.base import JobProcessing, Status
from api.config.database import AsyncSessionLocal, UPLOAD_FOLDER
from sqlalchemy import select
from datetime import datetime

import sys
from pathlib import Path
# Ensure root is in path to import cvJobMatching
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from cvJobMatching.pipeline import RecruitmentPipeline
from api.socket.job_socket import manager
import aiofiles
import os

async def run_evaluation(job_id: str, cv_path: str, jd_path: str, cv_type: str = "pdf", jd_type: str = "pdf"):
    """
    Background task to run the recruitment pipeline.
    """
    print(f"Starting evaluation for Job {job_id}")
    
    # Callback to update websocket
    # Capture the main event loop to schedule updates from the worker thread
    main_loop = asyncio.get_running_loop()

    # Callback to update websocket
    def progress_callback(msg: str, progress: int):
        try:
             asyncio.run_coroutine_threadsafe(
                 manager.send_progress(job_id, msg, progress), 
                 main_loop
             )
        except Exception as e:
            print(f"Socket update failed: {e}")

    try:
        # Initialize pipeline (this might take a moment)
        pipeline = RecruitmentPipeline()
        
        # Prepare output path in the job folder
        # We need to extract the directory from cv_path or jd_path since they are in uploads/{job_id}/
        job_dir = Path(cv_path).parent
        output_path = str(job_dir / "evaluation_report.json")
        
        # Run pipeline (blocking call, so we should run it in an executor to not block the event loop)
        loop = asyncio.get_running_loop()
        

        # We run the synchronous pipeline.run method in a separate thread
        # to avoid blocking the main asyncio loop of FastAPI
        evaluation_report = await loop.run_in_executor(
            None,
            lambda: pipeline.run(
                cv_path=cv_path,
                jd_path=jd_path,
                cv_type=cv_type,
                jd_type=jd_type,
                output_path=output_path,
                on_step_progress=progress_callback
            )
        )
        
        # Update final status
        print(f"Job {job_id} completed successfully.")
        await manager.send_progress(job_id, "Evaluation Complete", 100)
        
        if evaluation_report:
            decision_val = evaluation_report.decision
            
            # Update database status to COMPLETED and save report path
            async with AsyncSessionLocal() as session:
                job = await session.get(JobProcessing, job_id)
                if job:
                    job.status = Status.COMPLETED
                    job.decision = decision_val
                    job.report_path = output_path
                    job.progress = 100
                    job.updated_at = datetime.now()
                    await session.commit()
    
    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        await manager.send_progress(job_id, f"Error: {str(e)}", 0)
        # Update database status to FAILED
        async with AsyncSessionLocal() as session:
            job = await session.get(JobProcessing, job_id)
            if job:
                job.status = Status.FAILED
                job.progress = 0
                job.updated_at = datetime.now()
                await session.commit()

async def create_job(user_id: int, cv: UploadFile, jobdesc: UploadFile) -> dict:
    job_id = str(uuid.uuid4())
    
    # Logic to save files to storage and get paths
    # Resolve UPLOAD_FOLDER relative to project root if it's relative
    base_upload_path = Path(UPLOAD_FOLDER)
    if not base_upload_path.is_absolute():
        # Assuming project root is 3 levels up from this file: api/service/job_service.py -> api/service/ -> api/ -> root/
        project_root = Path(__file__).resolve().parent.parent.parent
        base_upload_path = project_root / base_upload_path
        
    upload_dir = base_upload_path / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    cv_path = upload_dir / f"cv_{cv.filename}"
    jd_path = upload_dir / f"jd_{jobdesc.filename}"
    
    async with aiofiles.open(cv_path, 'wb') as out_file:
        content = await cv.read()
        await out_file.write(content)
        
    async with aiofiles.open(jd_path, 'wb') as out_file:
        content = await jobdesc.read()
        await out_file.write(content)

    # Convert to absolute paths for the pipeline
    cv_path = str(cv_path.resolve())
    jd_path = str(jd_path.resolve())
    
    # Determine file types
    cv_type = Path(cv_path).suffix.lstrip(".").lower()
    if cv_type not in ["pdf", "docx", "txt"]:
        cv_type = "pdf" # Default fallback
        
    jd_type = Path(jd_path).suffix.lstrip(".").lower()
    if jd_type not in ["pdf", "docx", "txt"]:
        jd_type = "pdf" # Default fallback

    # Trigger the evaluation pipeline as a background task
    asyncio.create_task(run_evaluation(job_id, cv_path, jd_path, cv_type, jd_type))
    
    # Save initial job record to database
    async with AsyncSessionLocal() as session:
        new_job = JobProcessing(
            id=job_id,
            user_id=user_id,
            cv_path=cv_path,
            jobdesc_path=jd_path,
            status=Status.PENDING,
            progress=0
        )
        session.add(new_job)
        await session.commit()

    return {
        "job_id": job_id,
        "status": "PROCESSING"
    }

async def get_all_jobs() -> list[JobProcessing]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(JobProcessing))
        jobs = result.scalars().all()
        return jobs

async def get_file_content(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    return content
