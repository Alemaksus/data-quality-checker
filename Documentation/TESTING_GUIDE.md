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
- Generate HTML report in `logs/htmlcov/` directory
- Generate XML report in `logs/coverage.xml`

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

### Run Stage 2 Tests

Run tests for Stage 2 features (visualizations, Excel export, comparison):

```bash
# All Stage 2 tests
pytest tests/test_visualizations.py tests/test_excel_export.py tests/test_comparison.py tests/test_integration_new_features.py

# Visualizations only
pytest tests/test_visualizations.py -v

# Excel export only
pytest tests/test_excel_export.py -v

# Comparison functionality only
pytest tests/test_comparison.py -v

# Integration tests for new features
pytest tests/test_integration_new_features.py -v
```

### Test Stage 2 Features with Coverage

Run Stage 2 tests with coverage report:

```bash
# Test Stage 2 modules with coverage
pytest tests/test_visualizations.py tests/test_excel_export.py tests/test_comparison.py tests/test_integration_new_features.py \
  --cov=src/core/visualizations \
  --cov=src/core/export_utils \
  --cov=src/core/comparison \
  --cov=src/api/routes/comparison \
  --cov-report=term-missing \
  --cov-report=html

# View coverage for specific Stage 2 module
pytest tests/test_visualizations.py --cov=src/core/visualizations --cov-report=term-missing
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
├── conftest.py                      # Shared fixtures and configuration
├── sample_data.csv                  # Sample test data
├── test_api.py                     # API endpoint tests (integration)
├── test_data_loader.py             # Data loading tests (unit)
├── test_database.py                # Database operations tests (unit)
├── test_ml_advisor.py              # ML advisor tests (unit)
├── test_pipeline.py                # Full pipeline tests (integration)
├── test_reporting.py               # Report generation tests (unit)
├── test_url_loader.py              # URL loader tests (unit)
├── test_validator.py               # Validator tests (unit)
│
├── # Stage 2 Tests (New Features)
├── test_visualizations.py          # Visualization tests (unit)
├── test_excel_export.py            # Excel export tests (unit)
├── test_comparison.py              # Comparison functionality tests (integration)
└── test_integration_new_features.py # Integration tests for Stage 2 features
```

### Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for full workflows
- `@pytest.mark.asyncio` - Async tests (for async functions)

## Stage 2 Testing

### Overview

Stage 2 introduces new features that require comprehensive testing:

1. **Data Visualizations** - Chart generation for reports
2. **Excel Export** - Multi-sheet Excel file generation
3. **Comparison Functionality** - Compare data quality checks over time
4. **Enhanced HTML Reports** - Interactive features (sorting, search, filtering)

### Test Files for Stage 2

#### `test_visualizations.py`

Tests for chart generation functionality:
- Missing values charts (count and percentage)
- Numeric distribution charts (histograms)
- Issues severity charts (pie charts)
- Edge cases (empty data, no missing values, etc.)

**Coverage**: 97% (16 unit tests)

Run tests:
```bash
pytest tests/test_visualizations.py -v
```

#### `test_excel_export.py`

Tests for Excel export functionality:
- Basic Excel export with multiple sheets
- Excel export with ML recommendations
- Severity color coding
- Multiple sheet creation (Overview, Missing Values, Issues, Statistics)
- Error handling when openpyxl is missing

**Coverage**: 99% (6 tests)

Run tests:
```bash
pytest tests/test_excel_export.py -v
```

#### `test_comparison.py`

Tests for comparison functionality:
- Session comparison (improving, degrading, stable trends)
- Quality trend analysis
- Recent sessions retrieval
- Edge cases (non-existent sessions, no previous data)

**Coverage**: 88% (8 integration tests)

Run tests:
```bash
pytest tests/test_comparison.py -v
```

#### `test_integration_new_features.py`

Integration tests for full Stage 2 workflows:
- Report generation with visualizations
- Excel export integration
- Full comparison workflow
- Multiple previous sessions trend analysis

**Coverage**: Full integration coverage (6 tests)

Run tests:
```bash
pytest tests/test_integration_new_features.py -v
```

### Stage 2 API Tests

New API endpoints are tested in `test_api.py::TestComparisonEndpoints`:

- `GET /checks/compare` - Compare two sessions
- `GET /checks/{id}/trend` - Get quality trend
- Excel format support in upload endpoints

Run Stage 2 API tests:
```bash
pytest tests/test_api.py::TestComparisonEndpoints -v
```

### Running All Stage 2 Tests

Run all Stage 2 related tests at once:

```bash
# All Stage 2 tests
pytest tests/test_visualizations.py \
       tests/test_excel_export.py \
       tests/test_comparison.py \
       tests/test_integration_new_features.py \
       tests/test_api.py::TestComparisonEndpoints \
       tests/test_reporting.py::TestReportExport::test_save_html_with_visualizations \
       -v
```

### Stage 2 Test Coverage

Stage 2 features have excellent test coverage:

| Module | Coverage | Test Count |
|--------|----------|------------|
| `visualizations.py` | 97% | 16 tests |
| `export_utils.py` | 99% | 6 tests (Excel) |
| `comparison.py` | 88% | 8 tests |
| `api/routes/comparison.py` | 100% | 7 tests |

**Total new tests**: 43 tests (all passing)

### Prerequisites for Stage 2 Tests

Stage 2 tests require additional dependencies:

```bash
pip install matplotlib>=3.8.0  # For visualizations
pip install openpyxl>=3.1.2    # For Excel export
```

These are already included in `requirements.txt`.

### Testing Visualizations

Visualization tests generate charts as base64-encoded images. The tests verify:
- Charts are generated correctly
- Base64 encoding is valid
- Charts handle edge cases (empty data, no missing values)
- All chart types work correctly

Example:
```bash
pytest tests/test_visualizations.py::TestMissingValuesChart::test_generate_missing_values_chart_with_missing -v
```

### Testing Excel Export

Excel export tests create actual Excel files and verify:
- Multiple sheets are created
- Data is formatted correctly
- Severity colors are applied
- ML recommendations are included when available

Example:
```bash
pytest tests/test_excel_export.py::TestExcelExport::test_save_excel_multiple_sheets -v
```

### Testing Comparison

Comparison tests verify:
- Trend detection (improving/degrading/stable)
- Session comparison accuracy
- Quality trend calculation
- Edge cases handling

Example:
```bash
pytest tests/test_comparison.py::TestCompareSessions::test_compare_sessions_improving -v
```

## Coverage Reports

### Coverage Threshold

The project requires **minimum 90% test coverage**. This is enforced in `pytest.ini`:

```ini
--cov-fail-under=90
```

Overall project coverage: **93%**  
Stage 2 features coverage: **>90%** (where applicable)

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

Then open `logs/htmlcov/index.html` in your browser for an interactive coverage report.

#### XML Report

Generate XML report (useful for CI/CD):

```bash
pytest --cov=src --cov-report=xml
```

This creates `logs/coverage.xml` for integration with tools like Codecov.

### Coverage by Module

After running tests with coverage, you'll see output like:

```
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src/api/main.py                         54     19    65%   87-88, 95-96, 112-145
src/core/validator.py                  162     19    88%   106-118, 130, 136-137
src/core/ml_advisor.py                 162     38    77%   ...
src/core/visualizations.py             106      3    97%   143-144, 189
src/core/export_utils.py               152      2    99%   263-264
src/core/comparison.py                  76      9    88%   25-26, 36, 53-54, 131, 148-149, 207
src/api/routes/comparison.py            23      0   100%
------------------------------------------------------------------
TOTAL                                 1057    199    81%
```

### Stage 2 Coverage Details

For Stage 2 features specifically:

```bash
# Get detailed coverage for Stage 2 modules
pytest tests/test_visualizations.py tests/test_excel_export.py tests/test_comparison.py \
  --cov=src/core/visualizations \
  --cov=src/core/export_utils \
  --cov=src/core/comparison \
  --cov-report=term-missing
```

Expected coverage for Stage 2 modules:
- `visualizations.py`: **97%** ✅
- `export_utils.py`: **99%** ✅
- `comparison.py`: **88%** (near threshold)
- `api/routes/comparison.py`: **100%** ✅

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

### Stage 2 Test Fixtures

Stage 2 tests use the same fixtures as Stage 1, plus:

- `sample_dataframe` - Used for visualization and Excel export tests
- `clean_db` - Used for comparison tests requiring database access
- `tmp_path` - Used for creating temporary Excel and HTML files

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
open logs/htmlcov/index.html  # On macOS/Linux
start logs/htmlcov/index.html  # On Windows
```

### Continuous Testing

Watch for file changes and rerun tests (requires `pytest-watch`):

```bash
pip install pytest-watch
ptw
```

### Stage 2 Test Examples

#### Test All Stage 2 Features

Run all Stage 2 tests with coverage:

```bash
pytest tests/test_visualizations.py \
       tests/test_excel_export.py \
       tests/test_comparison.py \
       tests/test_integration_new_features.py \
       tests/test_api.py::TestComparisonEndpoints \
       --cov=src/core/visualizations \
       --cov=src/core/export_utils \
       --cov=src/core/comparison \
       --cov=src/api/routes/comparison \
       --cov-report=term-missing \
       -v
```

#### Test Visualizations Only

Test chart generation functionality:

```bash
pytest tests/test_visualizations.py -v --cov=src/core/visualizations --cov-report=term-missing
```

#### Test Excel Export Only

Test Excel export functionality:

```bash
pytest tests/test_excel_export.py -v --cov=src/core/export_utils --cov-report=term-missing
```

#### Test Comparison Functionality

Test comparison and trend analysis:

```bash
pytest tests/test_comparison.py -v --cov=src/core/comparison --cov-report=term-missing
```

#### Test Stage 2 API Endpoints

Test new comparison API endpoints:

```bash
pytest tests/test_api.py::TestComparisonEndpoints -v
```

#### Quick Stage 2 Test Check

Run Stage 2 tests quickly without coverage:

```bash
pytest tests/test_visualizations.py tests/test_excel_export.py tests/test_comparison.py tests/test_integration_new_features.py -q
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

For Stage 2 features specifically:
1. Run Stage 2 tests with coverage: `pytest tests/test_visualizations.py tests/test_excel_export.py tests/test_comparison.py --cov=src/core/visualizations --cov=src/core/export_utils --cov=src/core/comparison --cov-report=term-missing`
2. Check which lines are missing in Stage 2 modules
3. Add tests for uncovered paths in Stage 2 features

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
4. **Keep coverage high**: Add tests for new features (aim for >90%)
5. **Use fixtures**: Leverage shared fixtures from `conftest.py`
6. **Test Stage 2 features separately**: Run Stage 2 tests to verify new functionality
7. **Verify visualizations**: Ensure charts are generated correctly in tests
8. **Check Excel files**: Verify Excel export creates valid files with correct structure
9. **Test comparison logic**: Ensure trend detection works correctly
10. **Run integration tests**: Verify full workflows work end-to-end

### Stage 2 Specific Best Practices

1. **Install dependencies**: Ensure matplotlib and openpyxl are installed before testing
2. **Check chart generation**: Verify base64 encoding is valid
3. **Test Excel structure**: Verify all sheets are created correctly
4. **Test comparison accuracy**: Ensure trend calculations are correct
5. **Verify API endpoints**: Test new comparison endpoints thoroughly

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- Project README.md for general setup instructions

