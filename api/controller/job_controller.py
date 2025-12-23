from fastapi import APIRouter, UploadFile, Request, Form
from fastapi.responses import Response
import mimetypes
from api.utils.ApiResponse import ApiResponse
from api.entity.base import JobProcessing
from api.schema.job import JobProcessingBase, JobSubmissionResponse
from api.service import job_service
from api.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=ApiResponse)
async def submit_job(user_id: str = Form(...), cv: UploadFile = None, jobdesc: UploadFile = None):
    """
    Submit a job for processing
    """
    logger.info(f"[POST /jobs] User {user_id} submitting job with CV: {cv.filename}, JD: {jobdesc.filename}")
    result = await job_service.create_job(user_id, cv, jobdesc)
    logger.info(f"[POST /jobs] Job {result['job_id']} created successfully")
    
    return ApiResponse.success(
        status_code=201,
        message="Job submitted successfully",
        data=result
    )


@router.get("", response_model=ApiResponse[list[JobProcessingBase]])
async def get_jobs():
    """
    Get all jobs
    """
    logger.info("[GET /jobs] Fetching all jobs")
    jobs = await job_service.get_all_jobs()
    logger.info(f"[GET /jobs] Returning {len(jobs)} jobs")
    return ApiResponse.success(
        status_code=200,
        message="Jobs retrieved successfully",
        data=jobs
    )

@router.get("/user/{user_id}", response_model=ApiResponse[list[JobProcessingBase]])
async def get_user_jobs(user_id: str):
    """
    Get all jobs for a specific user
    """
    logger.info(f"[GET /jobs/user/{{user_id}}] Fetching jobs for user {user_id}")
    jobs = await job_service.get_jobs_by_user(user_id)
    logger.info(f"[GET /jobs/user/{{user_id}}] Returning {len(jobs)} jobs for user {user_id}")
    return ApiResponse.success(
        status_code=200,
        message="User jobs retrieved successfully",
        data=jobs
    )

@router.get("/files")
async def download_file(path: str):
    """
    Download a file given its path.
    """
    logger.info(f"[GET /jobs/files] Downloading file: {path}")
    try:
        content = await job_service.get_file_content(path)
        
        # Guess mime type
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            mime_type = "application/octet-stream"
            
        filename = path.split("/")[-1].split("\\")[-1] 
        
        logger.info(f"[GET /jobs/files] File downloaded: {filename}")
            
        return Response(
            content=content, 
            media_type=mime_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'} 
        )
    except FileNotFoundError:
        logger.error(f"[ERROR] File not found: {path}")
        return ApiResponse.error(
            status_code=404,
            message="File not found"
        )