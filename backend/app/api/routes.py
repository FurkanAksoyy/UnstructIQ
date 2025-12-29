from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.schemas import UploadResponse
from app.utils.file_handler import generate_job_id, validate_file, save_upload_file
from datetime import datetime
import json
import os

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
        file: UploadFile = File(...),
        prompt: Optional[str] = Form(None)
):
    """
    Upload file for processing

    - **file**: File to upload (CSV, JSON, Excel, TXT, PDF)
    - **prompt**: Optional processing instructions
    """
    try:
        # Validate file
        validate_file(file)

        # Generate job ID
        job_id = generate_job_id()

        # Save file
        file_info = await save_upload_file(file, job_id)

        # Save metadata
        metadata = {
            "job_id": job_id,
            "filename": file.filename,
            "file_path": file_info["file_path"],
            "file_size": file_info["file_size"],
            "prompt": prompt or "",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        metadata_path = os.path.join(file_info["job_dir"], "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return UploadResponse(
            job_id=job_id,
            filename=file.filename,
            file_size=file_info["file_size"],
            status="uploaded",
            message="File uploaded successfully. Processing will start shortly."
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")