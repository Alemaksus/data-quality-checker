# Data Quality Checker

**Automated data quality analysis tool using FastAPI and pandas.**

Data Quality Checker is a professional-grade tool for validating the structural and semantic quality of datasets. It supports CSV, JSON, and XML files as input and provides comprehensive validation reports, ML readiness recommendations, and flexible output formats.

## What It Does

The Data Quality Checker performs:
- **Data Validation**: Missing values, duplicates, data types, ranges, email/phone/date validation, outliers detection
- **ML Readiness Analysis**: Provides ML readiness score and recommendations for feature engineering
- **Comprehensive Reporting**: Generates reports in multiple formats (Markdown, HTML, PDF, Excel, JSON, CSV, XML, Parquet) with visualizations
- **API Integration**: RESTful API with customized Swagger UI documentation
- **History Tracking**: Stores validation sessions with pagination and provides comparison/trend analysis capabilities
- **Batch Processing**: Process multiple files at once with detailed results
- **Webhooks**: Automated notifications for validation events with HMAC signature verification
- **Custom Validation Rules**: Configure custom validation rules via API (thresholds, ranges, formats, etc.)
- **Monitoring & Metrics**: Health checks, API usage metrics, structured logging, rate limiting

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running the API Server

```bash
uvicorn src.api.main:app --reload
```

Access the API documentation at: `http://127.0.0.1:8000/docs`

### Running Tests

```bash
pytest --cov=src --cov-report=term-missing
```

Coverage threshold: **90%** (currently **91.80%**)

## Project Structure

```
├── src/               # Source code
│   ├── api/          # FastAPI endpoints and middleware
│   ├── core/         # Business logic (validation, ML advisor, reporting)
│   └── db/           # Database models and configuration
├── tests/            # Test suite (unit, integration, e2e)
├── docker/           # Docker configuration files
├── data/             # Sample data and database files
│   └── db/          # SQLite database files
├── logs/             # Application logs and coverage reports
├── reports/          # Generated validation reports
├── tmp/              # Temporary files (uploads, test files)
│   └── uploads/      # Temporary uploaded files
└── Documentation/    # Comprehensive documentation
```

## Features

- ✅ File upload via API
- ✅ URL-based file upload
- ✅ Comprehensive data validation
- ✅ ML readiness recommendations
- ✅ Multiple report formats (MD, HTML, PDF, Excel, JSON, CSV, XML, Parquet)
- ✅ Database storage of validation history
- ✅ Comparison and trend analysis
- ✅ Batch file processing
- ✅ Webhook notifications
- ✅ Custom validation rules
- ✅ Rate limiting and structured request logging
- ✅ Health checks and API usage metrics
- ✅ Data visualizations (charts for missing values, distributions, issues by severity)
- ✅ Pagination for history endpoints
- ✅ Customized Swagger UI
- ✅ Full test coverage (≥90%)

## Documentation

For detailed documentation, see the [`Documentation/`](Documentation/) folder:

- **[DEPLOYMENT.md](Documentation/DEPLOYMENT.md)** - Deployment instructions (Docker, production setup)
- **[EXAMPLES.md](Documentation/EXAMPLES.md)** - API usage examples
- **[TESTING_GUIDE.md](Documentation/TESTING_GUIDE.md)** - Testing guide and best practices
- **[USE_CASES.md](Documentation/USE_CASES.md)** - Use case descriptions and integration examples

## Docker Deployment

```bash
cd docker
docker-compose up -d
```

For detailed Docker setup, see [Documentation/DEPLOYMENT.md](Documentation/DEPLOYMENT.md).

## License

Aleks Mаksakov – QA Automation Engineer focused on AI systems testing, LangChain workflows, and test strategy for LLMs.
