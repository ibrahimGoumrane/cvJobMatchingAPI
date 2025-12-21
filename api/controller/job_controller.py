from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("")
async def submit_job(cv: UploadFile, jd: UploadFile):
    return {
        "job_id": "generated-id",
        "status": "PROCESSING"
    }
