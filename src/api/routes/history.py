from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.db.models import CheckSession
from pydantic import BaseModel
from typing import List
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


# Pydantic response schema for a check session (used to serialize ORM output)
class CheckSessionOut(BaseModel):
    id: int
    filename: str
    file_format: str
    rows: int
    issues_found: int
    created_at: datetime

    class Config:
        orm_mode = True  # Tells Pydantic to work with SQLAlchemy models


# GET endpoint that returns all check sessions from the database
@router.get("/checks/history", response_model=List[CheckSessionOut])
def get_check_sessions(db: Session = Depends(get_db)):
    """
    Returns a list of all check session records in descending order of creation time.
    """
    return db.query(CheckSession).order_by(CheckSession.created_at.desc()).all()
