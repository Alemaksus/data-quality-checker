# 📚 Examples - Data Quality Checker API

Examples of using the Data Quality Checker API.

## 📋 Table of Contents

- [Basic Examples](#basic-examples)
- [Upload File via API](#upload-file-via-api)
- [Upload File from URL](#upload-file-from-url)
- [Get Check History](#get-check-history)
- [Get Summary Statistics](#get-summary-statistics)
- [Compare Checks](#compare-checks)
- [Python Requests Examples](#python-requests-examples)
- [cURL Examples](#curl-examples)
- [Response Examples](#response-examples)

---

## 🚀 Basic Examples

### Base URL

All examples use the base URL:
```
http://localhost:8000
```

For production, replace with your domain:
```
https://yourdomain.com
```

---

## 📤 Upload File via API

### Python (requests)

```python
import requests

url = "http://localhost:8000/upload-data/"
files = {
    'file': ('data.csv', open('data.csv', 'rb'), 'text/csv')
}
data = {
    'report_format': 'html',  # 'md', 'html', 'pdf', 'xlsx', or 'all'
    'include_ai_insights': True,
    'client_name': 'Example Client'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### curl

```bash
curl -X POST "http://localhost:8000/upload-data/" \
  -F "file=@data.csv" \
  -F "report_format=html" \
  -F "include_ai_insights=true" \
  -F "client_name=Example Client"
```

### JavaScript (fetch)

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('report_format', 'html');
formData.append('include_ai_insights', 'true');
formData.append('client_name', 'Example Client');

fetch('http://localhost:8000/upload-data/', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

---

## 🌐 Upload File from URL

### Python (requests)

```python
import requests

url = "http://localhost:8000/upload-from-url/"
data = {
    'url': 'https://example.com/data.csv',
    'report_format': 'all',  # 'md', 'html', 'pdf', 'xlsx', or 'all'
    'include_ai_insights': True,
    'client_name': 'Remote Data Source'
}

response = requests.post(url, data=data)
print(response.json())
```

### curl

```bash
curl -X POST "http://localhost:8000/upload-from-url/" \
  -F "url=https://example.com/data.csv" \
  -F "report_format=all" \
  -F "include_ai_insights=true" \
  -F "client_name=Remote Data Source"
```

---

## 📜 Get Check History

### Without issues

```python
import requests

url = "http://localhost:8000/checks/history"
response = requests.get(url)
print(response.json())
```

```bash
curl "http://localhost:8000/checks/history"
```

### With issues

```python
import requests

url = "http://localhost:8000/checks/history"
params = {'with_issues': True}
response = requests.get(url, params=params)
print(response.json())
```

```bash
curl "http://localhost:8000/checks/history?with_issues=true"
```

---

## 📊 Get Summary Statistics

### Python (requests)

```python
import requests

url = "http://localhost:8000/checks/summary"
response = requests.get(url)
print(response.json())
```

### curl

```bash
curl "http://localhost:8000/checks/summary"
```

---

## 🔍 Compare Checks

### Compare Two Sessions

```python
import requests

url = "http://localhost:8000/checks/compare"
params = {
    'session_id1': 1,  # Older/previous session
    'session_id2': 2   # Newer/current session
}
response = requests.get(url, params=params)
print(response.json())
```

```bash
curl "http://localhost:8000/checks/compare?session_id1=1&session_id2=2"
```

### Get Quality Trend

```python
import requests

url = "http://localhost:8000/checks/2/trend"
params = {'days_back': 30}
response = requests.get(url, params=params)
print(response.json())
```

```bash
curl "http://localhost:8000/checks/2/trend?days_back=30"
```

---

## 🐍 Complete Python Requests Examples

### Example 1: Complete API Workflow

```python
import requests
import json
import time

BASE_URL = "http://localhost:8000"

# 1. Upload file for validation
print("Uploading file...")
with open('data.csv', 'rb') as f:
    files = {'file': ('data.csv', f, 'text/csv')}
    data = {
        'report_format': 'all',
        'include_ai_insights': True,
        'client_name': 'Test Client'
    }
    response = requests.post(f"{BASE_URL}/upload-data/", files=files, data=data)
    result = response.json()
    print(f"✅ Upload completed: {result['message']}")
    session_id = result.get('report_paths', {}).get('session_id')
    print(f"Session ID: {session_id}")

# 2. Get check history
print("\nGetting check history...")
response = requests.get(f"{BASE_URL}/checks/history")
history = response.json()
print(f"✅ Found {len(history)} checks")
for check in history[:3]:  # Show first 3
    print(f"  - {check['filename']}: {check['issues_found']} issues")

# 3. Get summary statistics
print("\nGetting summary statistics...")
response = requests.get(f"{BASE_URL}/checks/summary")
summary = response.json()
print(f"✅ Summary statistics:")
for item in summary[:3]:  # Show first 3
    print(f"  - {item['filename']}: {item['issue_count']} issues")

# 4. Compare sessions (if we have at least 2)
if len(history) >= 2:
    print("\nComparing sessions...")
    response = requests.get(
        f"{BASE_URL}/checks/compare",
        params={'session_id1': history[1]['id'], 'session_id2': history[0]['id']}
    )
    comparison = response.json()
    print(f"✅ Trend: {comparison['comparison']['trend']}")
```

### Example 2: Error Handling

```python
import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:8000"

def upload_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (filepath, f, 'text/csv')}
            data = {'report_format': 'html'}
            
            response = requests.post(
                f"{BASE_URL}/upload-data/",
                files=files,
                data=data,
                timeout=30
            )
            response.raise_for_status()  # Raises exception on HTTP error
            return response.json()
    
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None
    
    except RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

# Usage
result = upload_file('data.csv')
if result:
    print(f"✅ Success: {result['message']}")
```

---

## 🖥️ cURL Examples

### Example 1: Upload CSV File

```bash
# Simple upload
curl -X POST "http://localhost:8000/upload-data/" \
  -F "file=@data.csv" \
  -F "report_format=html"

# With additional parameters
curl -X POST "http://localhost:8000/upload-data/" \
  -F "file=@data.csv" \
  -F "report_format=all" \
  -F "include_ai_insights=true" \
  -F "client_name=My Company"
```

### Example 2: Upload from URL

```bash
curl -X POST "http://localhost:8000/upload-from-url/" \
  -F "url=https://raw.githubusercontent.com/user/repo/main/data.csv" \
  -F "report_format=html"
```

### Example 3: Get History with Issues

```bash
# Simple history
curl "http://localhost:8000/checks/history"

# With detailed issues
curl "http://localhost:8000/checks/history?with_issues=true" | python -m json.tool
```

### Example 4: Get Statistics

```bash
curl "http://localhost:8000/checks/summary" | python -m json.tool
```

### Example 5: Compare Sessions

```bash
curl "http://localhost:8000/checks/compare?session_id1=1&session_id2=2" | python -m json.tool
```

---

## 📥 Response Examples

### Successful File Upload

```json
{
  "message": "✅ Report successfully generated from 'data.csv'",
  "report_paths": {
    "markdown": "reports/data_20240101_120000.md",
    "html": "reports/data_20240101_120000.html",
    "pdf": "reports/data_20240101_120000.pdf",
    "excel": "reports/data_20240101_120000.xlsx",
    "session_id": 1,
    "issues_count": 15
  }
}
```

### Check History (without issues)

```json
[
  {
    "id": 1,
    "filename": "data.csv",
    "file_format": "csv",
    "rows": 1000,
    "issues_found": 15,
    "created_at": "2024-01-01T12:00:00"
  }
]
```

### Check Comparison

```json
{
  "session1": {
    "id": 1,
    "filename": "data.csv",
    "total_issues": 20,
    "issues_by_severity": {"high": 5, "medium": 10, "low": 5}
  },
  "session2": {
    "id": 2,
    "filename": "data.csv",
    "total_issues": 15,
    "issues_by_severity": {"high": 3, "medium": 8, "low": 4}
  },
  "comparison": {
    "total_issues_change": -5,
    "total_issues_change_pct": -25.0,
    "trend": "improving",
    "trend_icon": "📈"
  }
}
```

### Quality Trend

```json
{
  "current_session": {
    "id": 2,
    "filename": "data.csv",
    "total_issues": 15
  },
  "comparison": {
    "previous_sessions_count": 5,
    "average_issues_in_period": 18.5,
    "difference_from_average": -3.5,
    "difference_pct": -18.92
  },
  "trend": "improving",
  "period_days": 30
}
```

### Upload Error

```json
{
  "detail": "❌ Unsupported file format. Only CSV and JSON are supported."
}
```

---

## 🔧 Useful Commands

### Check API Availability

```bash
# Check health
curl "http://localhost:8000/docs"

# Check version (if endpoint added)
curl "http://localhost:8000/health"
```

### Download Reports

After successful upload, reports are saved in the `reports/` directory.
You can retrieve them via API or directly from the file system.

---

## 📝 Notes

- All examples use `http://localhost:8000` - replace with your production URL
- For large files, use increased timeout
- API supports CSV and JSON input file formats
- Maximum file size by default: 100MB (configurable in `.env`)
- Excel export requires `openpyxl` library

---

**Last updated:** 2024

