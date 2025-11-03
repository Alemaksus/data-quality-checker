# Testing Guide

This document provides comprehensive instructions for running tests in the Data Quality Checker project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Coverage Reports](#coverage-reports)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before running tests, ensure you have installed all dependencies:

```bash
pip install -r requirements.txt
```

Required packages for testing:
- `pytest>=8.3.5`
- `pytest-cov>=4.1.0`
- `pytest-asyncio>=0.21.0`

## Running Tests

### Run All Tests

Execute all tests in the project:

```bash
pytest
```

Or using the Makefile:

```bash
make test
```

### Run Tests with Coverage

Generate coverage reports while running tests:

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

Or using the Makefile:

```bash
make test-cov
```

This will:
- Display coverage in terminal
- Generate HTML report in `htmlcov/` directory
- Generate XML report in `coverage.xml`

### Run Specific Test Categories

#### Unit Tests Only

Run only unit tests (marked with `@pytest.mark.unit`):

```bash
pytest -m unit
```

Or:

```bash
make test-unit
```

#### Integration Tests Only

Run only integration tests (marked with `@pytest.mark.integration`):

```bash
pytest -m integration
```

Or:

```bash
make test-integration
```

### Run Specific Test File

Run tests from a specific file:

```bash
pytest tests/test_validator.py
pytest tests/test_ml_advisor.py
pytest tests/test_api.py
```

### Run Specific Test Function

Run a single test function:

```bash
pytest tests/test_validator.py::TestMissingValues::test_missing_values_detection
```

### Verbose Output

Get detailed output for each test:

```bash
pytest -v
```

### Stop on First Failure

Stop test execution after the first failure:

```bash
pytest -x
```

## Test Structure

The test suite is organized as follows:

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── sample_data.csv          # Sample test data
├── test_api.py             # API endpoint tests (integration)
├── test_data_loader.py     # Data loading tests (unit)
├── test_database.py        # Database operations tests (unit)
├── test_ml_advisor.py      # ML advisor tests (unit)
├── test_pipeline.py        # Full pipeline tests (integration)
├── test_reporting.py       # Report generation tests (unit)
├── test_url_loader.py      # URL loader tests (unit)
└── test_validator.py       # Validator tests (unit)
```

### Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for full workflows
- `@pytest.mark.asyncio` - Async tests (for async functions)

## Coverage Reports

### Coverage Threshold

The project requires **minimum 90% test coverage**. This is enforced in `pytest.ini`:

```ini
--cov-fail-under=90
```

Current coverage: **93%**

### Viewing Coverage Reports

#### Terminal Report

Coverage is displayed in the terminal with missing lines:

```bash
pytest --cov=src --cov-report=term-missing
```

#### HTML Report

Generate and view HTML coverage report:

```bash
pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser for an interactive coverage report.

#### XML Report

Generate XML report (useful for CI/CD):

```bash
pytest --cov=src --cov-report=xml
```

This creates `coverage.xml` for integration with tools like Codecov.

### Coverage by Module

After running tests with coverage, you'll see output like:

```
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src/api/main.py                         53      6    89%   94-95, 135-136
src/core/validator.py                  162     15    91%   106-118, 136-137
src/core/ml_advisor.py                 162      8    95%   241, 258, 298
------------------------------------------------------------------
TOTAL                                  722     52    93%
```

## Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `db_session` - Database session for tests
- `clean_db` - Cleaned database before each test
- `sample_dataframe` - DataFrame with various data quality issues
- `clean_dataframe` - Clean DataFrame for comparison
- `sample_csv_file` - Temporary CSV file
- `sample_json_file` - Temporary JSON file
- `temp_reports_dir` - Temporary directory for reports
- `temp_uploads_dir` - Temporary directory for uploads

## Example Test Runs

### Quick Test Check

Run all tests quickly:

```bash
pytest -q
```

### Full Coverage Check

Run with full coverage and view HTML report:

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
open htmlcov/index.html  # On macOS/Linux
start htmlcov/index.html  # On Windows
```

### Continuous Testing

Watch for file changes and rerun tests (requires `pytest-watch`):

```bash
pip install pytest-watch
ptw
```

## Troubleshooting

### Common Issues

#### Import Errors

If you see import errors, ensure you're running from the project root:

```bash
# From project root
pytest
```

#### Database Errors

Tests use an in-memory SQLite database. If you see database errors:

1. Ensure `src/db/database.py` is configured correctly
2. Check that tables are created in `conftest.py`

#### Missing Dependencies

If tests fail with missing module errors:

```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio httpx python-multipart
```

#### Coverage Not Reaching 90%

If coverage is below 90%, check:

1. Run `pytest --cov=src --cov-report=term-missing` to see missing lines
2. Add tests for uncovered code paths
3. Check HTML report for detailed coverage visualization

#### Async Test Issues

For async tests, ensure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

## CI/CD Integration

Tests automatically run in GitHub Actions CI:

- Runs on Python 3.9, 3.10, and 3.11
- Enforces 90% coverage threshold
- Uploads coverage to Codecov
- Runs linting checks

See `.github/workflows/ci.yml` for details.

## Best Practices

1. **Run tests before committing**: Ensure all tests pass locally
2. **Check coverage**: Use `make test-cov` to verify coverage
3. **Run specific tests**: When developing, run relevant test files
4. **Keep coverage high**: Add tests for new features
5. **Use fixtures**: Leverage shared fixtures from `conftest.py`

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- Project README.md for general setup instructions

