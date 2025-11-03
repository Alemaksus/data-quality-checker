"""
FastAPI application for the Data Quality Checker project.

Purpose:
  Accepts dataset files (CSV, JSON, XML), converts them to pandas DataFrame,
  performs data quality analysis, and generates recommendations and reports.

Endpoints:
  - POST /upload-data/ — upload a file for validation and analysis (customizable)
  - POST /upload-from-url/ — upload a file via URL instead of direct upload

Supported formats:
  Input: CSV, JSON, XML
  Output: JSON, CSV, HTML, Markdown, PDF, Excel, and more

Architecture:
  - src/api/main.py        — API layer
  - src/core/*.py          — data loading, validation, ML advice, and reporting logic
  - src/utils/*.py         — helper utilities
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from typing import Literal, Optional
from pathlib import Path
import shutil
import uuid
import os

from src.api.routes import history, summary, comparison, health, metrics, batch, config, webhooks
from src.api.middleware.logging import RequestLoggingMiddleware
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.core.data_loader import load_data
from src.core.generate_sample_report import generate_data_quality_report
from src.core.url_loader import download_file_from_url

# Get rate limit from environment or use default
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

app = FastAPI(
    title="Data Quality Checker API",
    description="Professional data quality analysis tool with validation, ML recommendations, and comprehensive reporting",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration - more secure defaults
# For production, set CORS_ORIGINS environment variable (comma-separated list)
# Example: CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

# Add middleware in order (first added is last executed)
# Request logging should be first (outermost)
app.add_middleware(RequestLoggingMiddleware)

# Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=RATE_LIMIT_PER_MINUTE)

# CORS (should be last)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Specific origins only (not "*")
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Custom Swagger UI configuration
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with enhanced styling."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_ui_parameters={
            "deepLinking": True,
            "displayRequestDuration": True,
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "tryItOutEnabled": True
        },
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )


# Include route modules
app.include_router(history.router, tags=["History"])
app.include_router(summary.router, tags=["Summary"])
app.include_router(comparison.router, tags=["Comparison"])
app.include_router(health.router, tags=["Health"])
app.include_router(metrics.router, tags=["Metrics"])
app.include_router(batch.router, tags=["Batch"])
app.include_router(config.router, tags=["Configuration"])
app.include_router(webhooks.router, tags=["Webhooks"])

# Import export router
from src.api.routes import export as export_router
app.include_router(export_router.router, tags=["Export"])


@app.post("/upload-data/", tags=["Upload"])
async def upload_data(
    file: UploadFile = File(..., description="Data file to validate (CSV or JSON)"),
    report_format: Literal["md", "html", "pdf", "xlsx", "excel", "all"] = Form("pdf", description="Report format(s) to generate"),
    include_ai_insights: bool = Form(True, description="Include ML readiness recommendations"),
    client_name: Optional[str] = Form(None, description="Optional client name for the report")
):
    temp_file_path = None
    try:
        # Save uploaded file to a temporary folder
        temp_dir = Path("tmp/uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Generate report with given parameters
        paths = generate_data_quality_report(
            input_path=temp_file_path,
            report_format=report_format,
            include_ai=include_ai_insights,
            client_name=client_name
        )

        # Send webhook notification
        try:
            from src.api.routes.webhooks import send_webhook, WebhookEvent
            from src.api.routes.webhooks import webhooks as webhook_configs
            
            session_id = paths.get("session_id")
            if session_id:
                webhook_data = {
                    "session_id": session_id,
                    "filename": file.filename,
                    "issues_count": paths.get("issues_count", 0),
                    "status": "completed",
                    "report_paths": paths
                }
                
                # Send to all configured webhooks
                for webhook_id in webhook_configs.keys():
                    await send_webhook(webhook_id, WebhookEvent.CHECK_COMPLETED, webhook_data)
        except Exception:
            # Don't fail if webhooks fail
            pass

        return JSONResponse(content={
            "message": f"✅ Report successfully generated from '{file.filename}'",
            "report_paths": paths
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ {str(e)}")

    finally:
        # Clean up temporary file if it was created
        if temp_file_path is not None:
            try:
                temp_file_path.unlink(missing_ok=True)
            except Exception:
                pass


@app.post("/upload-from-url/", tags=["Upload"])
async def upload_from_url(
    url: str = Form(..., description="HTTP/HTTPS URL to download file from"),
    report_format: Literal["md", "html", "pdf", "xlsx", "excel", "all"] = Form("pdf", description="Report format(s) to generate"),
    include_ai_insights: bool = Form(True, description="Include ML readiness recommendations"),
    client_name: Optional[str] = Form(None, description="Optional client name for the report")
):
    """
    Upload and analyze a dataset file from a URL.
    
    Supports CSV, JSON, and XML files from HTTP/HTTPS URLs.
    Maximum file size: 100MB
    """
    temp_file_path = None
    try:
        # Download file from URL
        temp_file_path = await download_file_from_url(url)
        
        # Generate report with given parameters
        paths = generate_data_quality_report(
            input_path=temp_file_path,
            report_format=report_format,
            include_ai=include_ai_insights,
            client_name=client_name
        )
        
        filename = temp_file_path.name
        return JSONResponse(content={
            "message": f"✅ Report successfully generated from URL '{url[:50]}...'",
            "filename": filename,
            "report_paths": paths
        })
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ {str(e)}")
    
    finally:
        # Clean up temporary file if it was created
        if temp_file_path is not None:
            try:
                temp_file_path.unlink(missing_ok=True)
            except Exception:
                pass
