# PowerShell script to start the Data Quality Checker API server
# Usage: .\run_server.ps1

Write-Host "Starting Data Quality Checker API Server..." -ForegroundColor Green
Write-Host ""
Write-Host "Swagger UI will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn src.api.main:app --reload

