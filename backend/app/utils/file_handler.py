import os
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.config import settings


def generate_job_id() -> str:
    """Generate unique job ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = settings.get_allowed_extensions()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Note: File size will be checked during upload


async def save_upload_file(file: UploadFile, job_id: str) -> dict:
    """Save uploaded file to disk"""
    try:
        # Create job directory
        job_dir = os.path.join(settings.UPLOAD_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(job_dir, file.filename)

        content = await file.read()
        file_size = len(content)

        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1_000_000}MB"
            )

        with open(file_path, "wb") as f:
            f.write(content)

        return {
            "file_path": file_path,
            "file_size": file_size,
            "job_dir": job_dir
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")