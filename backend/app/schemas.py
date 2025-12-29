from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Upload Response
class UploadResponse(BaseModel):
    job_id: str
    filename: str
    file_size: int
    status: str
    message: str

# Processing Status Response
class StatusResponse(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: int  # 0-100
    stage: str  # "uploading", "cleaning", "structuring", "analyzing", "completed"
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Results Response
class ResultsResponse(BaseModel):
    job_id: str
    status: str
    structured_data: dict
    charts: list
    insights: str
    statistics: dict