"""
FastAPI application for the Data Quality Checker project.

Purpose:
  Accepts dataset files (CSV, JSON, XML), converts them to pandas DataFrame,
  performs data quality analysis, and generates recommendations and reports.

Endpoints:
  - POST /upload-data/ — upload a file for validation and analysis (supports 'format' parameter)
  - (planned) POST /upload-from-url/ — upload a file via URL instead of direct upload

Supported formats:
  Input: CSV, JSON, XML
  Output: JSON, CSV, HTML (planned: Markdown and PDF)

Architecture:
  - src/api/main.py        — API layer
  - src/core/*.py          — data loading, validation, ML advice, and reporting logic
  - src/utils/*.py         — helper utilities
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Literal

from src.core.data_loader import load_data  # мы напишем это позже

app = FastAPI(title="Data Quality Checker")


@app.post("/upload-data/")
async def upload_data(
        file: UploadFile = File(...),
        format: Literal["json", "csv", "html"] = "json"
):
    try:
        df = await load_data(file)  # обрабатываем файл (CSV/JSON/XML)
        # Здесь будет логика: валидация + отчет
        return JSONResponse(content={"message": f"Файл '{file.filename}' успешно загружен."})

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
