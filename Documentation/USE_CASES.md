# Use Cases - Data Quality Checker

This document describes common use cases and scenarios for the Data Quality Checker API.

## Table of Contents

- [Overview](#overview)
- [Use Case 1: Daily Data Quality Monitoring](#use-case-1-daily-data-quality-monitoring)
- [Use Case 2: ETL Pipeline Validation](#use-case-2-etl-pipeline-validation)
- [Use Case 3: Customer Data Onboarding](#use-case-3-customer-data-onboarding)
- [Use Case 4: ML Data Preparation](#use-case-4-ml-data-preparation)
- [Use Case 5: Regulatory Compliance](#use-case-5-regulatory-compliance)
- [Use Case 6: Batch Processing Workflows](#use-case-6-batch-processing-workflows)
- [Integration Examples](#integration-examples)

---

## Overview

The Data Quality Checker API is designed for various scenarios where data quality validation is critical:

- **Data Engineering**: Automated data quality checks in ETL pipelines
- **Data Science**: ML data preparation and validation
- **Business Operations**: Customer data onboarding and validation
- **Compliance**: Regulatory data quality requirements
- **Monitoring**: Continuous data quality monitoring

---

## Use Case 1: Daily Data Quality Monitoring

### Scenario

A data team needs to monitor daily data quality metrics and track improvements over time.

### Solution

Use the API to automatically check daily data exports and track trends:

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

# 1. Upload daily export
with open(f"daily_export_{datetime.today().strftime('%Y%m%d')}.csv", 'rb') as f:
    files = {'file': ('daily_export.csv', f, 'text/csv')}
    data = {'report_format': 'all'}
    response = requests.post(f"{BASE_URL}/upload-data/", files=files, data=data)
    result = response.json()
    session_id = result['report_paths']['session_id']

# 2. Compare with previous day
previous_day_id = get_previous_session_id()
comparison = requests.get(
    f"{BASE_URL}/checks/compare",
    params={"session_id1": previous_day_id, "session_id2": session_id}
).json()

# 3. Get quality trend
trend = requests.get(f"{BASE_URL}/checks/{session_id}/trend", params={"days_back": 30}).json()

# 4. Check metrics
metrics = requests.get(f"{BASE_URL}/metrics/usage", params={"days": 7}).json()

# 5. Send webhook if quality degraded
if comparison['comparison']['trend'] == 'degrading':
    send_alert_to_slack(comparison)
```

### Benefits

- Automated daily checks
- Trend tracking over time
- Alerting on quality degradation
- Historical metrics analysis

---

## Use Case 2: ETL Pipeline Validation

### Scenario

An ETL pipeline processes data from multiple sources and needs validation at each stage.

### Solution

Integrate API calls into the ETL pipeline for validation:

```python
import requests

def validate_stage_data(data_file, stage_name):
    """Validate data at a specific ETL stage."""
    url = "http://localhost:8000/upload-data/"
    
    with open(data_file, 'rb') as f:
        files = {'file': (data_file, f, 'text/csv')}
        data = {
            'report_format': 'json',
            'client_name': stage_name
        }
        response = requests.post(url, files=files, data=data)
        result = response.json()
        
        # Check if validation passed
        issues_count = result['report_paths']['issues_count']
        
        if issues_count > 100:
            raise ValueError(f"Too many issues found at {stage_name}: {issues_count}")
        
        return result

# Use in pipeline
try:
    validate_stage_data("staging/users.csv", "staging")
    validate_stage_data("transformed/users.csv", "transformation")
    validate_stage_data("final/users.csv", "final")
except ValueError as e:
    send_to_dead_letter_queue(e)
```

### Benefits

- Automated validation at each stage
- Early error detection
- Quality gates in pipeline
- Detailed issue reporting

---

## Use Case 3: Customer Data Onboarding

### Scenario

A SaaS company receives customer data uploads and needs to validate them before processing.

### Solution

Use the API with webhooks for real-time validation:

```python
from fastapi import FastAPI, File, UploadFile
import requests

app = FastAPI()

@app.post("/customer/upload")
async def customer_upload(file: UploadFile):
    """Handle customer data upload."""
    
    # Forward to validation API
    files = {'file': (file.filename, await file.read(), file.content_type)}
    data = {
        'report_format': 'all',
        'client_name': 'Customer Onboarding'
    }
    
    response = requests.post(
        "http://localhost:8000/upload-data/",
        files=files,
        data=data
    )
    
    result = response.json()
    session_id = result['report_paths']['session_id']
    
    # Configure webhook for notifications
    webhook_response = requests.post(
        "http://localhost:8000/webhooks",
        json={
            "webhook_id": f"customer_{session_id}",
            "url": "https://your-app.com/webhooks/data-quality",
            "events": ["check.completed"],
            "secret": "your_secret_key",
            "enabled": True
        }
    )
    
    return {
        "status": "processing",
        "session_id": session_id,
        "webhook_url": "https://your-app.com/webhooks/data-quality"
    }

# Webhook handler in your app
@app.post("/webhooks/data-quality")
async def handle_webhook(payload: dict):
    """Handle webhook notification from validation API."""
    event = payload['event']
    data = payload['data']
    
    if event == "check.completed":
        if data['issues_count'] == 0:
            # Data is clean, proceed with onboarding
            proceed_with_onboarding(data['session_id'])
        else:
            # Data has issues, notify customer
            notify_customer(data)
```

### Benefits

- Real-time validation
- Webhook notifications
- Automated workflows
- Customer-facing quality reports

---

## Use Case 4: ML Data Preparation

### Scenario

A data science team needs to prepare datasets for machine learning models.

### Solution

Use ML readiness recommendations:

```python
import requests
import pandas as pd

def prepare_ml_dataset(csv_file):
    """Prepare dataset for ML using API recommendations."""
    
    # 1. Validate data
    with open(csv_file, 'rb') as f:
        files = {'file': ('data.csv', f, 'text/csv')}
        data = {
            'report_format': 'all',
            'include_ai_insights': True
        }
        response = requests.post(
            "http://localhost:8000/upload-data/",
            files=files,
            data=data
        )
        result = response.json()
    
    # 2. Get ML readiness score
    ml_score = result['report_paths']['ml_readiness_score']
    ml_level = result['report_paths']['ml_readiness_level']
    
    print(f"ML Readiness: {ml_score}/100 ({ml_level})")
    
    # 3. Download Excel report with recommendations
    excel_path = result['report_paths']['excel']
    
    # 4. Process recommendations
    df = pd.read_csv(csv_file)
    
    # Apply recommendations from report
    # (In real scenario, would parse Excel for specific recommendations)
    
    return df, result

# Use in ML pipeline
data, validation_result = prepare_ml_dataset("raw_data.csv")

if validation_result['report_paths']['ml_readiness_score'] >= 80:
    print("Data is ready for ML training")
    train_model(data)
else:
    print("Data needs preprocessing")
    data = preprocess_data(data, validation_result)
```

### Benefits

- ML readiness assessment
- Actionable recommendations
- Automated data quality checks
- Preprocessing guidance

---

## Use Case 5: Regulatory Compliance

### Scenario

A financial institution needs to validate customer data for regulatory compliance.

### Solution

Use custom validation rules and batch processing:

```python
import requests

# 1. Create custom validation configuration
config = requests.post(
    "http://localhost:8000/config/validation-rules",
    json={
        "config_name": "regulatory_compliance",
        "description": "Strict validation for regulatory compliance",
        "rules": [
            {
                "rule_name": "no_missing_customer_id",
                "rule_type": "missing_threshold",
                "enabled": True,
                "parameters": {"column": "customer_id", "threshold": 0}
            },
            {
                "rule_name": "valid_email_required",
                "rule_type": "format_check",
                "enabled": True,
                "parameters": {"column": "email", "format": "email", "required": True}
            },
            {
                "rule_name": "age_range_check",
                "rule_type": "range_check",
                "enabled": True,
                "parameters": {"column": "age", "min": 18, "max": 120}
            }
        ]
    }
).json()

# 2. Batch process customer files
files = [
    ("file1.csv", open("customers_batch1.csv", "rb")),
    ("file2.csv", open("customers_batch2.csv", "rb")),
    ("file3.csv", open("customers_batch3.csv", "rb"))
]

upload_files = [("files", f) for _, f in files]

response = requests.post(
    "http://localhost:8000/upload-batch/",
    files=upload_files,
    data={"report_format": "xlsx"}
)

results = response.json()

# 3. Export validation results for audit
export = requests.get(
    "http://localhost:8000/export/history",
    params={"format": "csv", "limit": 1000}
)

# Save for audit trail
with open("audit_trail.csv", "wb") as f:
    f.write(export.content)
```

### Benefits

- Custom validation rules
- Batch processing
- Audit trail export
- Compliance reporting

---

## Use Case 6: Batch Processing Workflows

### Scenario

Process multiple data files in batches with progress tracking.

### Solution

Use batch endpoint with webhooks for progress tracking:

```python
import requests
import asyncio

async def process_batch_async(file_paths):
    """Process multiple files asynchronously."""
    
    files = []
    for path in file_paths:
        files.append(("files", (path.name, open(path, "rb"), "text/csv")))
    
    # Configure webhook for batch completion
    webhook = requests.post(
        "http://localhost:8000/webhooks",
        json={
            "webhook_id": "batch_processor",
            "url": "https://your-app.com/webhooks/batch-complete",
            "events": ["batch.completed"],
            "enabled": True
        }
    )
    
    # Submit batch
    response = requests.post(
        "http://localhost:8000/upload-batch/",
        files=files,
        data={"report_format": "all"}
    )
    
    return response.json()

# Process large batch
file_paths = [Path(f"data/file_{i}.csv") for i in range(1, 101)]
results = asyncio.run(process_batch_async(file_paths))

print(f"Processed {results['total_files']} files")
print(f"Successful: {results['successful']}")
print(f"Failed: {results['failed']}")
```

### Benefits

- Bulk processing
- Progress tracking
- Webhook notifications
- Error handling per file

---

## Integration Examples

### Python Integration

```python
from data_quality_checker import DataQualityClient

client = DataQualityClient("http://localhost:8000")

# Validate file
result = client.validate_file("data.csv")

# Get trends
trend = client.get_quality_trend(result.session_id)

# Export results
export = client.export_session(result.session_id, format="json")
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Validate Data Quality
  run: |
    curl -X POST "${{ secrets.API_URL }}/upload-data/" \
      -F "file=@data/export.csv" \
      -F "report_format=all"
    
    # Fail if quality score < 80
    QUALITY_SCORE=$(curl "${{ secrets.API_URL }}/checks/latest" | jq '.ml_readiness_score')
    if [ $QUALITY_SCORE -lt 80 ]; then
      exit 1
    fi
```

### Scheduled Monitoring

```python
# Cron job example
import schedule
import requests

def daily_quality_check():
    """Run daily quality check."""
    with open("daily_export.csv", "rb") as f:
        files = {"file": ("daily.csv", f, "text/csv")}
        response = requests.post(
            "http://localhost:8000/upload-data/",
            files=files,
            data={"report_format": "html"}
        )
        
        # Send to email if issues found
        if response.json()['report_paths']['issues_count'] > 50:
            send_email_alert(response.json())

schedule.every().day.at("09:00").do(daily_quality_check)
```

---

## Best Practices

1. **Use Webhooks**: Configure webhooks for real-time notifications
2. **Monitor Trends**: Regularly check quality trends for early detection
3. **Custom Rules**: Define validation rules specific to your domain
4. **Batch Processing**: Use batch endpoints for multiple files
5. **Export for Audit**: Export validation results for compliance
6. **Rate Limiting**: Respect API rate limits in production
7. **Error Handling**: Implement retry logic for failed requests

---

**Last updated:** 2024

