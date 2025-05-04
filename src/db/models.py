# src/db/models.py

from sqlalchemy import Column, Integer, String, DateTime
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
