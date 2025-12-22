from fastapi import APIRouter, UploadFile, Request
from api.utils.ApiResponse import ApiResponse
from api.entity.job_processing import JobProcessing

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=ApiResponse[JobProcessing])
async def submit_job(user_id: int, cv: UploadFile, jobdesc: UploadFile):
    """
    Submit a job for processing
    """
    return ApiResponse.success(
        status_code=201,
        message="Job submitted successfully",
        data={
            "job_id": "generated-id",
            "status": "PROCESSING"
        }
    )


@router.get("", response_model=ApiResponse[list[JobProcessing]])
async def get_jobs():
    """
    Get all jobs
    """
    return ApiResponse.success(
        status_code=200,
        message="Jobs retrieved successfully",
        data=[]
    )

@router.get("/files")
async def download_file(request:Request):
    """
    Download files from the server
    The body will contain the file path stored in JobProcessing table
    """
    
    return ApiResponse.success(
        status_code=200,
        message="Files retrieved successfully",
        data=request.files
    )