"""
Extended export endpoints for various data formats.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Literal, Optional
from src.db.database import SessionLocal
from src.db.models import CheckSession, Issue
from src.core.export_formats import (
    export_to_csv,
    export_to_json,
    export_to_xml,
    export_to_parquet,
    export_validation_results
)
import pandas as pd
import tempfile

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/export/session/{session_id}", tags=["Export"])
async def export_session_data(
    session_id: int,
    format: Literal["csv", "json", "xml", "parquet"] = Query("json", description="Export format"),
    db: Session = Depends(get_db)
):
    """
    Export session data in various formats.
    
    Exports all issues from a specific session in the requested format.
    """
    session = db.query(CheckSession).filter(CheckSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Get issues for this session
    issues = db.query(Issue).filter(Issue.session_id == session_id).all()
    
    # Allow export even if no issues found (return empty data)
    if not issues:
        issues = []
    
    # Convert to list of dicts
    issues_data = [
        {
            "row_number": issue.row_number,
            "column_name": issue.column_name,
            "issue_type": issue.issue_type,
            "description": issue.description,
            "severity": issue.severity,
            "detected_at": issue.detected_at.isoformat() if issue.detected_at else None
        }
        for issue in issues
    ]
    
    # Create temporary file
    file_ext = {
        "csv": ".csv",
        "json": ".json",
        "xml": ".xml",
        "parquet": ".parquet"
    }[format]
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
    temp_path = Path(temp_file.name)
    temp_file.close()
    
    try:
        if format == "json":
            export_validation_results(issues_data, temp_path, format="json")
        elif format == "csv":
            export_validation_results(issues_data, temp_path, format="csv")
        elif format == "xml":
            export_validation_results(issues_data, temp_path, format="xml")
        elif format == "parquet":
            df = pd.DataFrame(issues_data)
            export_to_parquet(df, temp_path)
        
        return FileResponse(
            path=str(temp_path),
            filename=f"session_{session_id}_issues{file_ext}",
            media_type="application/octet-stream"
        )
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/export/history", tags=["Export"])
async def export_history(
    format: Literal["csv", "json", "xml", "parquet"] = Query("json", description="Export format"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Maximum number of sessions to export"),
    db: Session = Depends(get_db)
):
    """
    Export check history in various formats.
    
    Exports all check sessions with their summary information.
    """
    query = db.query(CheckSession)
    
    sessions = query.order_by(CheckSession.created_at.desc()).all()
    
    if limit:
        sessions = sessions[:limit]
    
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found")
    
    # Convert to list of dicts
    sessions_data = [
        {
            "id": session.id,
            "filename": session.filename,
            "file_format": session.file_format,
            "rows": session.rows,
            "issues_found": session.issues_found,
            "created_at": session.created_at.isoformat() if session.created_at else None
        }
        for session in sessions
    ]
    
    # Create temporary file
    file_ext = {
        "csv": ".csv",
        "json": ".json",
        "xml": ".xml",
        "parquet": ".parquet"
    }[format]
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
    temp_path = Path(temp_file.name)
    temp_file.close()
    
    try:
        df = pd.DataFrame(sessions_data)
        
        if format == "csv":
            export_to_csv(df, temp_path)
        elif format == "json":
            export_to_json(df, temp_path)
        elif format == "xml":
            export_to_xml(df, temp_path)
        elif format == "parquet":
            export_to_parquet(df, temp_path)
        
        return FileResponse(
            path=str(temp_path),
            filename=f"check_history{file_ext}",
            media_type="application/octet-stream"
        )
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

