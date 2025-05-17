from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.db.models import CheckSummaryView
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Create an API router for this module
router = APIRouter()


# Dependency that provides a new database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db  # yield the session to the route
    finally:
        db.close()  # close session after response


# Pydantic response schema for a single row in check_summary_view
class CheckSummaryOut(BaseModel):
    session_id: int
    filename: str
    file_format: str
    created_at: datetime
    issue_count: int
    high_severity_issues: int

    class Config:
        orm_mode = True  # allows compatibility with SQLAlchemy ORM objects


# GET endpoint to fetch all summarized check sessions
@router.get("/checks/summary", response_model=List[CheckSummaryOut])
def get_check_summary(db: Session = Depends(get_db)):
    """
    Returns summarized data from the check_summary_view.
    Each record includes aggregated issue stats for a session.
    """
    return db.query(CheckSummaryView).order_by(CheckSummaryView.created_at.desc()).all()
