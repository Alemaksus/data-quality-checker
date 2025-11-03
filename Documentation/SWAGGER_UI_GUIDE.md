# 📸 Swagger UI Guide - Making Screenshots

Guide for running the API server and taking screenshots of Swagger UI interface.

## 🚀 Quick Start

### 1. Start the API Server

Open a terminal in the project root and run:

```bash
# Windows PowerShell (recommended):
uvicorn src.api.main:app --reload

# Linux/Mac (if make is installed):
make run

# Or use direct command on any OS:
uvicorn src.api.main:app --reload
```

The server will start and be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 2. Access Swagger UI

Open your browser and navigate to:
```
http://localhost:8000/docs
```

## 📊 Recommended Screenshots

### Main Swagger UI Overview
1. **Main page** - Show all available endpoints grouped by tags:
   - Upload
   - History
   - Summary
   - Comparison
   - Health
   - Metrics
   - Batch
   - Configuration
   - Webhooks
   - Export

### Upload Endpoints
2. **POST /upload-data/** - Expand the endpoint to show:
   - Request body parameters (file, report_format, include_ai_insights, client_name)
   - Example request
   - Response schema

3. **POST /upload-from-url/** - Show URL-based upload option

### Interactive Testing
4. **Try it out** - Expand an endpoint and click "Try it out" to show:
   - Parameter input fields
   - Execute button
   - Response preview

### Example Request
5. **Upload example** - Use the test file:
   - File: `tests/sample_data.csv` or `data/test_data.csv`
   - Parameters:
     - `report_format`: "html" or "all"
     - `include_ai_insights`: true
     - `client_name`: "Demo Client"

### History & Analysis
6. **GET /checks/history** - Show pagination parameters
7. **GET /checks/summary** - Show summary endpoint
8. **GET /checks/compare** - Show comparison feature
9. **GET /checks/{session_id}/trend** - Show trend analysis

### Advanced Features
10. **Webhooks** - Show webhook management endpoints:
    - POST /webhooks (create)
    - GET /webhooks (list)
    - PUT /webhooks/{webhook_id} (update)

11. **Configuration** - Show validation rules configuration:
    - POST /config/validation-rules (create)
    - GET /config/validation-rules (list)

12. **Export** - Show export endpoints:
    - GET /export/session/{session_id}
    - GET /export/history

13. **Health & Metrics**:
    - GET /health
    - GET /health/detailed
    - GET /metrics/usage
    - GET /metrics/summary

### Batch Processing
14. **POST /upload-batch/** - Show batch upload interface

## 🎨 Tips for Better Screenshots

1. **Browser Settings**:
   - Use full-screen mode (F11)
   - Set browser zoom to 100%
   - Use a clean browser window (hide bookmarks bar)

2. **Swagger UI Features**:
   - Expand all endpoint groups for overview
   - Use "Try it out" to show interactive interface
   - Show successful response examples

3. **Recommended Order**:
   1. Main overview (all endpoints)
   2. Upload endpoints (most important)
   3. History and analysis
   4. Advanced features (webhooks, config, export)
   5. Health and metrics

4. **Browser DevTools**:
   - Press F12 to open DevTools
   - Use Responsive Design Mode if needed
   - Hide DevTools before taking screenshots

## 📁 Test Data Files

Use these files for testing and screenshots:

- **Sample CSV**: `tests/sample_data.csv` or `data/test_data.csv`
  ```
  id,name,email,age
  1,Alice,alice@example.com,30
  2,Bob,,27
  3,Charlie,charlie@example.com,not_a_number
  4,,david@example.com,45
  5,Eve,eve@example.com,
  ```

## 🔧 Pre-flight Checklist

Before taking screenshots:

- [ ] API server is running (check http://localhost:8000/docs)
- [ ] Swagger UI loads correctly
- [ ] All endpoint groups are visible
- [ ] Test data files are ready
- [ ] Browser is in full-screen mode
- [ ] Browser zoom is set to 100%

## 📸 Quick Test

1. Start server: `make run`
2. Open: http://localhost:8000/docs
3. Expand "Upload" → "POST /upload-data/"
4. Click "Try it out"
5. Upload `tests/sample_data.csv`
6. Click "Execute"
7. Check response - should show success with report paths

## 💡 Additional Notes

- Swagger UI is customized with enhanced styling
- All endpoints include detailed descriptions
- Parameters have helpful descriptions
- Response schemas are fully documented
- Authentication is not required (can be added later for production)

