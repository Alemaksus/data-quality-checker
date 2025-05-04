# Data Quality Checker

**Automated data quality analysis tool using FastAPI and pandas.**

Data Quality Checker is a lightweight and modular tool for validating the structural and semantic quality of datasets. It supports CSV, JSON, and XML files as input and provides:

- Validation reports on missing values, duplicates, and data types  
- Recommendations for ML-readiness  
- Flexible output formats: JSON, CSV, and HTML  
- Future integration with LangChain agents for advanced AI-based data analysis

The project is designed for data analysts, QA engineers, and ML practitioners working with raw or user-submitted datasets.

To start the API server:

```
uvicorn src.api.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` to access Swagger UI for testing endpoints.

Project structure:
- `src/api/` — FastAPI endpoints  
- `src/core/` — data loading, validation, ML advising, and reporting  
- `src/utils/` — helper utilities  
- `tests/` — test cases  
- `data/` — sample input files  
- `reports/` — generated output reports  

Planned features include: file upload via URL, Markdown/PDF reports, and full LLMChain integration.