# Data Quality Checker

**Automated data quality analysis tool using FastAPI and pandas.**

Data Quality Checker is a lightweight and modular tool for validating the structural and semantic quality of datasets. It supports CSV, JSON, and XML files as input and provides:

- Validation reports on missing values, duplicates, and data types  
- Recommendations for ML-readiness  
- Flexible output formats: JSON, CSV, and HTML  
- Future integration with LangChain agents for advanced AI-based data analysis

The project is designed for data analysts, QA engineers, and ML practitioners working with raw or user-submitted datasets.

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the API Server

To start the API server:

```bash
uvicorn src.api.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` to access Swagger UI for testing endpoints.

## Running Tests

### Run all tests with coverage:

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

### Run tests without coverage:

```bash
pytest
```

### Run specific test file:

```bash
pytest tests/test_validator.py
```

### Run tests with verbose output:

```bash
pytest -v
```

### Run only unit tests:

```bash
pytest -m unit
```

### Run only integration tests:

```bash
pytest -m integration
```

### Coverage Report

After running tests with coverage, view the HTML report:

```bash
# Open htmlcov/index.html in your browser
```

Coverage threshold is set to **85%** minimum (currently **87.67%**).

## Project Structure

- `src/api/` — FastAPI endpoints  
- `src/core/` — data loading, validation, ML advising, and reporting  
- `src/utils/` — helper utilities  
- `tests/` — comprehensive test suite (unit + integration tests)
- `data/` — sample input files  
- `reports/` — generated output reports  

## Features

- ✅ File upload via API (`/upload-data/`)
- ✅ File upload from URL (`/upload-from-url/`)
- ✅ Comprehensive data validation
- ✅ ML readiness recommendations
- ✅ Report generation (Markdown, HTML, PDF)
- ✅ Database storage of validation results
- ✅ History and summary endpoints
- ✅ Full test coverage (≥90%)