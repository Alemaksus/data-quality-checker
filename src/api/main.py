"""
FastAPI application for the Data Quality Checker project.

Purpose:
  Accepts dataset files (CSV, JSON, XML), converts them to pandas DataFrame,
  performs data quality analysis, and generates recommendations and reports.

Endpoints:
  - POST /upload-data/ — upload a file for validation and analysis (customizable)
  - (planned) POST /upload-from-url/ — upload a file via URL instead of direct upload

Supported formats:
  Input: CSV, JSON, XML
  Output: JSON, CSV, HTML (planned: Markdown and PDF)

Architecture:
  - src/api/main.py        — API layer
  - src/core/*.py          — data loading, validation, ML advice, and reporting logic
  - src/utils/*.py         — helper utilities
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Literal, Optional
from pathlib import Path
import shutil
import uuid
import os

from src.api.routes import history, summary
from src.core.data_loader import load_data  # will be implemented
from src.core.generate_sample_report import generate_data_quality_report
from src.core.url_loader import download_file_from_url

app = FastAPI(title="Data Quality Checker")

# CORS configuration - more secure defaults
# For production, set CORS_ORIGINS environment variable (comma-separated list)
# Example: CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Specific origins only (not "*")
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(history.router)
app.include_router(summary.router)


@app.post("/upload-data/")
async def upload_data(
    file: UploadFile = File(...),
    report_format: Literal["md", "html", "pdf", "all"] = Form("pdf"),
    include_ai_insights: bool = Form(True),
    client_name: Optional[str] = Form(None)
):
    temp_file_path = None
    try:
        # Save uploaded file to a temporary folder
        temp_dir = Path("tmp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_file_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Generate report with given parameters
        paths = generate_data_quality_report(
            input_path=temp_file_path,
            report_format=report_format,
            include_ai=include_ai_insights,
            client_name=client_name
        )

        return JSONResponse(content={
            "message": f"✅ Report successfully generated from '{file.filename}'",
            "report_paths": paths
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ {str(e)}")

    finally:
        # Clean up temporary file if it was created
        if temp_file_path is not None:
            try:
                temp_file_path.unlink(missing_ok=True)
            except Exception:
                pass


@app.post("/upload-from-url/")
async def upload_from_url(
    url: str = Form(..., description="HTTP/HTTPS URL to download file from"),
    report_format: Literal["md", "html", "pdf", "all"] = Form("pdf"),
    include_ai_insights: bool = Form(True),
    client_name: Optional[str] = Form(None)
):
    """
    Upload and analyze a dataset file from a URL.
    
    Supports CSV, JSON, and XML files from HTTP/HTTPS URLs.
    Maximum file size: 100MB
    """
    temp_file_path = None
    try:
        # Download file from URL
        temp_file_path = await download_file_from_url(url)
        
        # Generate report with given parameters
        paths = generate_data_quality_report(
            input_path=temp_file_path,
            report_format=report_format,
            include_ai=include_ai_insights,
            client_name=client_name
        )
        
        filename = temp_file_path.name
        return JSONResponse(content={
            "message": f"✅ Report successfully generated from URL '{url[:50]}...'",
            "filename": filename,
            "report_paths": paths
        })
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ {str(e)}")
    
    finally:
        # Clean up temporary file if it was created
        if temp_file_path is not None:
            try:
                temp_file_path.unlink(missing_ok=True)
            except Exception:
                pass
