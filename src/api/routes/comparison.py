from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.core.comparison import compare_sessions, get_quality_trend
from typing import Optional

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/checks/compare")
def compare_check_sessions(
    session_id1: int = Query(..., description="ID of the first session (older/previous)"),
    session_id2: int = Query(..., description="ID of the second session (newer/current)"),
    db: Session = Depends(get_db)
):
    """
    Compare two check sessions and return detailed comparison.
    
    Returns:
        Comparison results including:
        - Changes in total issues count
        - Changes by severity level
        - Trend (improving/degrading/stable)
        - Time difference between sessions
    """
    result = compare_sessions(session_id1, session_id2, db)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/checks/{session_id}/trend")
def get_session_trend(
    session_id: int,
    days_back: int = Query(30, description="Number of days to look back for comparison"),
    db: Session = Depends(get_db)
):
    """
    Get quality trend for a session compared to previous sessions.
    
    Returns:
        Trend analysis including:
        - Average issues in previous sessions
        - Difference from average
        - Overall trend (improving/degrading/stable)
    """
    result = get_quality_trend(session_id, days_back, db)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

