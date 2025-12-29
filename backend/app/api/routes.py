from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from app.schemas import UploadResponse
from app.utils.file_handler import generate_job_id, validate_file, save_upload_file
from app.services.processing_service import process_file
from app.config import settings
from datetime import datetime
import json
import os

router = APIRouter()


# ==================== UPLOAD ENDPOINT ====================

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
        validate_file(file)
        job_id = generate_job_id()
        file_info = await save_upload_file(file, job_id)

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


# ==================== PROCESSING ENDPOINT ====================

@router.post("/process/{job_id}")
async def start_processing(job_id: str):
    """
    Start processing uploaded file

    - **job_id**: Job ID from upload response
    """
    try:
        job_dir = os.path.join(settings.UPLOAD_DIR, job_id)
        if not os.path.exists(job_dir):
            raise HTTPException(status_code=404, detail="Job not found")

        results = process_file(job_id)

        return {
            "message": "Processing completed successfully",
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STATUS ENDPOINT ====================

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """
    Get processing status for a job

    - **job_id**: Job ID from upload response
    """
    try:
        job_dir = os.path.join(settings.UPLOAD_DIR, job_id)
        metadata_path = os.path.join(job_dir, "metadata.json")

        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=404, detail="Job not found")

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        return {
            "job_id": job_id,
            "status": metadata.get("status", "unknown"),
            "filename": metadata.get("filename"),
            "created_at": metadata.get("created_at"),
            "updated_at": metadata.get("updated_at"),
            "error": metadata.get("error")
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== RESULTS ENDPOINT ====================

@router.get("/results/{job_id}")
async def get_results(job_id: str):
    """
    Get processing results for a completed job

    - **job_id**: Job ID from upload response
    """
    try:
        processed_dir = os.path.join(settings.PROCESSED_DIR, job_id)
        results_path = os.path.join(processed_dir, "results.json")

        if not os.path.exists(results_path):
            raise HTTPException(
                status_code=404,
                detail="Results not found. Job may not be completed yet."
            )

        with open(results_path, 'r') as f:
            results = json.load(f)

        return results

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EXPORT ENDPOINTS ====================

@router.get("/export/csv/{job_id}")
async def export_csv(job_id: str):
    """
    Download cleaned CSV file
    """
    try:
        processed_dir = os.path.join(settings.PROCESSED_DIR, job_id)
        csv_path = os.path.join(processed_dir, "cleaned_data.csv")

        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="Cleaned CSV not found")

        return FileResponse(
            path=csv_path,
            filename=f"cleaned_data_{job_id}.csv",
            media_type="text/csv"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/json/{job_id}")
async def export_json(job_id: str):
    """
    Download full results JSON
    """
    try:
        processed_dir = os.path.join(settings.PROCESSED_DIR, job_id)
        results_path = os.path.join(processed_dir, "results.json")

        if not os.path.exists(results_path):
            raise HTTPException(status_code=404, detail="Results JSON not found")

        return FileResponse(
            path=results_path,
            filename=f"results_{job_id}.json",
            media_type="application/json"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))