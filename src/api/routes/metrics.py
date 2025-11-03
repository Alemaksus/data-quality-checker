"""
API metrics and usage statistics endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.db.database import SessionLocal
from src.db.models import CheckSession, Issue
from datetime import datetime, timedelta
from typing import Dict, Optional

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/metrics/usage")
async def get_usage_metrics(
    days: int = 7,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get API usage metrics for the specified time period.
    
    Args:
        days: Number of days to look back (default: 7)
        
    Returns:
        Usage statistics including:
        - Total checks
        - Total issues found
        - Average issues per check
        - Checks by day
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get total checks in period
    total_checks = db.query(func.count(CheckSession.id))\
        .filter(CheckSession.created_at >= cutoff_date)\
        .scalar() or 0
    
    # Get total issues
    total_issues = db.query(func.count(Issue.id))\
        .join(CheckSession)\
        .filter(CheckSession.created_at >= cutoff_date)\
        .scalar() or 0
    
    # Get average issues per check
    avg_issues = total_issues / total_checks if total_checks > 0 else 0
    
    # Get checks by day
    checks_by_day = db.query(
        func.date(CheckSession.created_at).label('date'),
        func.count(CheckSession.id).label('count')
    ).filter(
        CheckSession.created_at >= cutoff_date
    ).group_by(
        func.date(CheckSession.created_at)
    ).order_by(
        func.date(CheckSession.created_at).desc()
    ).all()
    
    checks_by_day_dict = {str(date): count for date, count in checks_by_day}
    
    # Get checks by file format
    checks_by_format = db.query(
        CheckSession.file_format,
        func.count(CheckSession.id).label('count')
    ).filter(
        CheckSession.created_at >= cutoff_date
    ).group_by(
        CheckSession.file_format
    ).all()
    
    checks_by_format_dict = {format: count for format, count in checks_by_format}
    
    return {
        "period_days": days,
        "period_start": cutoff_date.isoformat(),
        "period_end": datetime.utcnow().isoformat(),
        "statistics": {
            "total_checks": total_checks,
            "total_issues": total_issues,
            "average_issues_per_check": round(avg_issues, 2),
            "checks_by_day": checks_by_day_dict,
            "checks_by_format": checks_by_format_dict
        }
    }


@router.get("/metrics/summary")
async def get_metrics_summary(
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get overall API metrics summary.
    
    Returns:
        Overall statistics since API start
    """
    # Total checks
    total_checks = db.query(func.count(CheckSession.id)).scalar() or 0
    
    # Total issues
    total_issues = db.query(func.count(Issue.id)).scalar() or 0
    
    # First and last check
    first_check = db.query(func.min(CheckSession.created_at)).scalar()
    last_check = db.query(func.max(CheckSession.created_at)).scalar()
    
    # Average issues per check
    avg_issues = total_issues / total_checks if total_checks > 0 else 0
    
    # Issues by severity
    issues_by_severity = db.query(
        Issue.severity,
        func.count(Issue.id).label('count')
    ).group_by(
        Issue.severity
    ).all()
    
    severity_stats = {severity: count for severity, count in issues_by_severity}
    
    return {
        "total_checks": total_checks,
        "total_issues": total_issues,
        "average_issues_per_check": round(avg_issues, 2),
        "first_check": first_check.isoformat() if first_check else None,
        "last_check": last_check.isoformat() if last_check else None,
        "issues_by_severity": severity_stats
    }

