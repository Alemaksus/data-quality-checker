from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from src.db.database import SessionLocal
from src.db.models import CheckSession, Issue
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Create a new router instance
router = APIRouter()


# Dependency that provides a database session for each request
def get_db():
    db = SessionLocal()  # Create new DB connection
    try:
        yield db  # Provide the session to the route
    finally:
        db.close()  # Ensure it's closed after response is returned


class IssueOut(BaseModel):
    row_number: Optional[int]
    column_name: Optional[str]
    issue_type: Optional[str]
    description: Optional[str]
    severity: Optional[str]

    class Config:
        orm_mode = True


# Pydantic response schema for a check session (used to serialize ORM output) with nested issues
class CheckSessionOut(BaseModel):
    id: int
    filename: str
    file_format: str
    rows: int
    issues_found: int
    created_at: datetime
    issues: Optional[List[IssueOut]] = []

    class Config:
        orm_mode = True  # Tells Pydantic to work with SQLAlchemy models


# GET endpoint that returns all check sessions from the database
@router.get("/checks/history", response_model=List[CheckSessionOut])
def get_check_sessions(
        with_issues: bool = Query(False, description="Include issues in response"),
        db: Session = Depends(get_db)
):
    """
    Returns a list of all check session records in descending order of creation time.
    """
    query = db.query(CheckSession)
    if with_issues:
        query = query.options(joinedload(CheckSession.issues))
    return query.order_by(CheckSession.created_at.desc()).all()
