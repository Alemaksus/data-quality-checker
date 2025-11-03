"""
Comparison utilities for comparing data quality checks over time.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.db.models import CheckSession, Issue
from src.db.database import SessionLocal


def get_recent_sessions(limit: int = 10, db_session: Session = None) -> List[CheckSession]:
    """
    Get recent check sessions ordered by creation date.
    
    Args:
        limit: Maximum number of sessions to return
        db_session: Optional database session
        
    Returns:
        List of CheckSession objects
    """
    session_created = False
    if db_session is None:
        db_session = SessionLocal()
        session_created = True
    
    try:
        sessions = db_session.query(CheckSession)\
            .order_by(CheckSession.created_at.desc())\
            .limit(limit)\
            .all()
        return sessions
    finally:
        if session_created:
            db_session.close()


def compare_sessions(session_id1: int, session_id2: int, db_session: Session = None) -> Dict:
    """
    Compare two check sessions and return detailed comparison.
    
    Args:
        session_id1: ID of the first session (older/previous)
        session_id2: ID of the second session (newer/current)
        db_session: Optional database session
        
    Returns:
        Dictionary with comparison results
    """
    session_created = False
    if db_session is None:
        db_session = SessionLocal()
        session_created = True
    
    try:
        session1 = db_session.query(CheckSession).filter(CheckSession.id == session_id1).first()
        session2 = db_session.query(CheckSession).filter(CheckSession.id == session_id2).first()
        
        if not session1 or not session2:
            return {"error": "One or both sessions not found"}
        
        # Get issues for both sessions
        issues1 = db_session.query(Issue).filter(Issue.session_id == session_id1).all()
        issues2 = db_session.query(Issue).filter(Issue.session_id == session_id2).all()
        
        # Count issues by severity
        def count_by_severity(issues_list):
            counts = {"high": 0, "medium": 0, "low": 0}
            for issue in issues_list:
                severity = issue.severity or "medium"
                counts[severity] = counts.get(severity, 0) + 1
            return counts
        
        severity1 = count_by_severity(issues1)
        severity2 = count_by_severity(issues2)
        
        # Calculate changes
        total_change = session2.issues_found - session1.issues_found
        total_change_pct = ((session2.issues_found - session1.issues_found) / max(session1.issues_found, 1)) * 100
        
        high_change = severity2["high"] - severity1["high"]
        medium_change = severity2["medium"] - severity1["medium"]
        low_change = severity2["low"] - severity1["low"]
        
        # Determine trend
        if total_change < 0:
            trend = "improving"
            trend_icon = "📈"
        elif total_change > 0:
            trend = "degrading"
            trend_icon = "📉"
        else:
            trend = "stable"
            trend_icon = "➡️"
        
        return {
            "session1": {
                "id": session1.id,
                "filename": session1.filename,
                "created_at": session1.created_at.isoformat() if session1.created_at else None,
                "rows": session1.rows,
                "total_issues": session1.issues_found,
                "issues_by_severity": severity1
            },
            "session2": {
                "id": session2.id,
                "filename": session2.filename,
                "created_at": session2.created_at.isoformat() if session2.created_at else None,
                "rows": session2.rows,
                "total_issues": session2.issues_found,
                "issues_by_severity": severity2
            },
            "comparison": {
                "total_issues_change": total_change,
                "total_issues_change_pct": round(total_change_pct, 2),
                "high_severity_change": high_change,
                "medium_severity_change": medium_change,
                "low_severity_change": low_change,
                "trend": trend,
                "trend_icon": trend_icon,
                "time_difference_days": (
                    (session2.created_at - session1.created_at).days
                    if session2.created_at and session1.created_at
                    else None
                )
            }
        }
    finally:
        if session_created:
            db_session.close()


def get_quality_trend(session_id: int, days_back: int = 30, db_session: Session = None) -> Dict:
    """
    Get quality trend for a session compared to previous sessions within a time period.
    
    Args:
        session_id: ID of the current session
        days_back: Number of days to look back for comparison
        db_session: Optional database session
        
    Returns:
        Dictionary with trend analysis
    """
    session_created = False
    if db_session is None:
        db_session = SessionLocal()
        session_created = True
    
    try:
        current_session = db_session.query(CheckSession).filter(CheckSession.id == session_id).first()
        
        if not current_session:
            return {"error": "Session not found"}
        
        # Get previous sessions within the time period
        cutoff_date = current_session.created_at - timedelta(days=days_back) if current_session.created_at else None
        
        query = db_session.query(CheckSession)\
            .filter(CheckSession.id != session_id)
        
        if cutoff_date:
            query = query.filter(CheckSession.created_at >= cutoff_date)
        
        previous_sessions = query.order_by(CheckSession.created_at.desc()).all()
        
        if not previous_sessions:
            return {
                "current_session": {
                    "id": current_session.id,
                    "filename": current_session.filename,
                    "total_issues": current_session.issues_found
                },
                "trend": "no_previous_data",
                "message": "No previous sessions found for comparison"
            }
        
        # Calculate average issues from previous sessions
        avg_issues = sum(s.issues_found for s in previous_sessions) / len(previous_sessions)
        
        trend = "stable"
        if current_session.issues_found < avg_issues * 0.9:
            trend = "improving"
        elif current_session.issues_found > avg_issues * 1.1:
            trend = "degrading"
        
        return {
            "current_session": {
                "id": current_session.id,
                "filename": current_session.filename,
                "total_issues": current_session.issues_found,
                "created_at": current_session.created_at.isoformat() if current_session.created_at else None
            },
            "comparison": {
                "previous_sessions_count": len(previous_sessions),
                "average_issues_in_period": round(avg_issues, 2),
                "current_issues": current_session.issues_found,
                "difference_from_average": round(current_session.issues_found - avg_issues, 2),
                "difference_pct": round(((current_session.issues_found - avg_issues) / max(avg_issues, 1)) * 100, 2)
            },
            "trend": trend,
            "period_days": days_back
        }
    finally:
        if session_created:
            db_session.close()

