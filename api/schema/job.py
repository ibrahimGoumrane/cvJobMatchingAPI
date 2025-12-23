from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class Status(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobProcessingBase(BaseModel):
    id: str
    user_id: str
    jobdesc_path: str
    cv_path: str
    decision: Optional[str] = None
    report_path: Optional[str] = None
    progress: int = 0
    status: Status
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class JobSubmissionResponse(BaseModel):
    job_id: str
    status: str
