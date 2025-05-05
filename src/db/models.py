# src/db/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class CheckSession(Base):
    __tablename__ = "check_sessions"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_format = Column(String, nullable=False)
    rows = Column(Integer)
    issues_found = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CheckSession(filename={self.filename}, issues={self.issues_found})>"

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("check_sessions.id"), nullable=False)
    row_number = Column(Integer)
    column_name = Column(String)
    issue_type = Column(String)
    description = Column(String)
    severity = Column(String)
    detected_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to CheckSession
    session = relationship("CheckSession", back_populates="issues")

    def __repr__(self):
        return f"<Issue(type={self.issue_type}, column={self.column_name}, severity={self.severity})>"

# Add reverse relationship to CheckSession
CheckSession.issues = relationship("Issue", back_populates="session", cascade="all, delete-orphan")
