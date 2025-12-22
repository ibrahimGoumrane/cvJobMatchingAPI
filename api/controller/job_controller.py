from fastapi import APIRouter, UploadFile, Request
from fastapi.responses import Response
import mimetypes
from api.utils.ApiResponse import ApiResponse
from api.entity.base import JobProcessing
from api.schema.job import JobProcessingBase, JobSubmissionResponse
from api.service import job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=ApiResponse)
async def submit_job(user_id: int, cv: UploadFile, jobdesc: UploadFile):
    """
    Submit a job for processing
    """
    result = await job_service.create_job(user_id, cv, jobdesc)
    
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
    jobs = await job_service.get_all_jobs()
    return ApiResponse.success(
        status_code=200,
        message="Jobs retrieved successfully",
        data=jobs
    )

@router.get("/files")
async def download_file(path: str):
    """
    Download a file given its path.
    """
    try:
        content = await job_service.get_file_content(path)
        
        # Guess mime type
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            mime_type = "application/octet-stream"
            
        filename = path.split("/")[-1].split("\\")[-1] 
            
        return Response(
            content=content, 
            media_type=mime_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'} 
        )
    except FileNotFoundError:
        return ApiResponse.error(
            status_code=404,
            message="File not found"
        )