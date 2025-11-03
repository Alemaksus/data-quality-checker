"""
Health check and monitoring endpoints.
"""
from fastapi import APIRouter
from datetime import datetime
from typing import Dict
import psutil
import os
from pathlib import Path

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Health status with timestamp and basic system info
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Data Quality Checker API",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict:
    """
    Detailed health check with system metrics.
    
    Returns:
        Detailed health status with system resources
    """
    try:
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check database
        db_path = Path("data/db/db.sqlite3")
        db_status = "ok" if db_path.exists() else "missing"
        
        # Check directories
        reports_dir = Path("reports")
        reports_status = "ok" if reports_dir.exists() else "missing"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "Data Quality Checker API",
            "version": "1.0.0",
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": round((disk.used / disk.total) * 100, 2)
                }
            },
            "components": {
                "database": db_status,
                "reports_directory": reports_status
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

