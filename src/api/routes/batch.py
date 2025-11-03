"""
Batch processing endpoints for multiple files.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Literal
from pathlib import Path
import uuid
import shutil
import asyncio
from datetime import datetime

from src.core.generate_sample_report import generate_data_quality_report
from src.api.routes.history import get_db
from src.db.database import SessionLocal

router = APIRouter()


@router.post("/upload-batch/", tags=["Upload"])
async def upload_batch(
    files: List[UploadFile] = File(..., description="Multiple data files to validate"),
    report_format: Literal["md", "html", "pdf", "xlsx", "excel", "json", "all"] = Form("pdf", description="Report format for all files"),
    include_ai_insights: bool = Form(True, description="Include ML readiness recommendations"),
    client_name: Optional[str] = Form(None, description="Optional client name for reports")
):
    """
    Process multiple files in batch.
    
    Accepts up to 10 files at once. Each file is processed sequentially.
    Returns results for all files processed.
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per batch request"
        )
    
    results = []
    temp_files = []
    
    try:
        for file in files:
            try:
                # Save uploaded file
                temp_dir = Path("tmp/uploads")
                temp_dir.mkdir(parents=True, exist_ok=True)
                temp_file_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"
                temp_files.append(temp_file_path)
                
                with open(temp_file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Generate report
                paths = generate_data_quality_report(
                    input_path=temp_file_path,
                    report_format=report_format,
                    include_ai=include_ai_insights,
                    client_name=client_name
                )
                
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "report_paths": paths
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        successful_count = len([r for r in results if r["status"] == "success"])
        failed_count = len([r for r in results if r["status"] == "error"])
        
        # Send batch completion webhook
        try:
            from src.api.routes.webhooks import send_webhook, WebhookEvent
            from src.api.routes.webhooks import webhooks as webhook_configs
            
            batch_data = {
                "total_files": len(files),
                "successful": successful_count,
                "failed": failed_count,
                "results": results
            }
            
            for webhook_id in webhook_configs.keys():
                await send_webhook(webhook_id, WebhookEvent.BATCH_COMPLETED, batch_data)
        except Exception:
            pass
        
        return JSONResponse(content={
            "message": f"Processed {len(files)} file(s)",
            "results": results,
            "total_files": len(files),
            "successful": successful_count,
            "failed": failed_count
        })
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass

