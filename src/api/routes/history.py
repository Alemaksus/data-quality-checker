from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from src.db.database import SessionLocal
from src.db.models import CheckSession, Issue
from pydantic import BaseModel
from typing import List, Optional, Dict
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
        from_attributes = True


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
        from_attributes = True  # Tells Pydantic to work with SQLAlchemy models (Pydantic v2)


# GET endpoint that returns all check sessions from the database with pagination
@router.get("/checks/history", response_model=dict)
def get_check_sessions(
        with_issues: bool = Query(False, description="Include issues in response"),
        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
        db: Session = Depends(get_db)
):
    """
    Returns a paginated list of check session records in descending order of creation time.
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get total count
    total_count = db.query(func.count(CheckSession.id)).scalar()
    
    # Get paginated results
    query = db.query(CheckSession)
    if with_issues:
        query = query.options(joinedload(CheckSession.issues))
    
    sessions = query.order_by(CheckSession.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Calculate pagination metadata
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
    
    # Serialize sessions using Pydantic models
    items = [CheckSessionOut.model_validate(session) for session in sessions]
    
    return {
        "items": [item.model_dump() for item in items],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }
