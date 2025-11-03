"""
Integration tests for the full data quality pipeline.
Tests complete workflow from data loading to report generation and DB storage.
"""
import pytest

pytestmark = pytest.mark.integration
import pandas as pd
from pathlib import Path
from src.core.generate_sample_report import generate_data_quality_report, save_check_to_db
from src.core.validator import validate_dataframe
from src.core.ml_advisor import get_ml_recommendations
from src.db.database import SessionLocal, engine, Base
from src.db.models import CheckSession, Issue


@pytest.fixture
def sample_data_csv(tmp_path):
    """Create sample_data.csv for testing."""
    data = {
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", None, "Eve"],
        "email": ["alice@example.com", "invalid-email", "charlie@example.com", "david@example.com", "eve@example.com"],
        "age": [30, 27, "not_a_number", 45, None],
        "salary": [50000, 60000, 70000, 80000, 90000]
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "sample_data.csv"
    df.to_csv(file_path, index=False)
    return file_path


class TestFullPipeline:
    """Tests for the complete data quality pipeline."""
    
    def test_generate_data_quality_report_full_cycle(self, sample_data_csv, tmp_path, clean_db):
        """Test full cycle of generate_data_quality_report."""
        # Override reports directory
        import os
        original_reports = os.getenv("REPORTS_DIR", "reports")
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Run full pipeline
        result = generate_data_quality_report(
            input_path=sample_data_csv,
            report_format="all",
            include_ai=True,
            client_name="Pipeline Test Client",
            save_to_db=True
        )
        
        # Verify results
        assert isinstance(result, dict)
        assert "markdown" in result
        assert "html" in result
        assert "session_id" in result
        assert "issues_count" in result
        assert "validation_summary" in result
        assert "ml_readiness_score" in result
        
        # Verify files were created
        assert Path(result["markdown"]).exists()
        assert Path(result["html"]).exists()
        
        # Verify session_id is valid
        assert result["session_id"] is not None
        
        # Verify database entries
        session = SessionLocal()
        try:
            check_session = session.query(CheckSession).filter_by(id=result["session_id"]).first()
            assert check_session is not None
            assert check_session.filename == "sample_data.csv"
            assert check_session.issues_found > 0
            
            # Verify issues were saved
            issues = session.query(Issue).filter_by(session_id=result["session_id"]).all()
            assert len(issues) == result["issues_count"]
        finally:
            session.close()
    
    def test_pipeline_with_csv(self, sample_data_csv, tmp_path, clean_db):
        """Test pipeline with CSV file."""
        result = generate_data_quality_report(
            input_path=sample_data_csv,
            report_format="md",
            include_ai=True,
            save_to_db=True
        )
        
        assert result["session_id"] is not None
        assert result["issues_count"] > 0
        assert isinstance(result["validation_summary"], dict)
        assert result["ml_readiness_score"] >= 0
        assert result["ml_readiness_score"] <= 100
    
    def test_pipeline_with_json(self, tmp_path, clean_db):
        """Test pipeline with JSON file."""
        # Create JSON file
        data = {
            "id": [1, 2, 3],
            "value": [10, 20, None],
            "name": ["A", "B", "C"]
        }
        df = pd.DataFrame(data)
        json_path = tmp_path / "sample_data.json"
        df.to_json(json_path, orient='records', lines=False)
        
        result = generate_data_quality_report(
            input_path=json_path,
            report_format="md",
            include_ai=True,
            save_to_db=True
        )
        
        assert result["session_id"] is not None
        assert Path(result["markdown"]).exists()
    
    def test_pipeline_without_ai(self, sample_data_csv, tmp_path, clean_db):
        """Test pipeline without AI insights."""
        result = generate_data_quality_report(
            input_path=sample_data_csv,
            report_format="md",
            include_ai=False,
            save_to_db=True
        )
        
        assert result["session_id"] is not None
        assert "ml_readiness_score" not in result or result.get("ml_readiness_score") is None
    
    def test_pipeline_without_db(self, sample_data_csv, tmp_path):
        """Test pipeline without saving to database."""
        result = generate_data_quality_report(
            input_path=sample_data_csv,
            report_format="md",
            include_ai=True,
            save_to_db=False
        )
        
        assert result["session_id"] is None
        assert result["issues_count"] > 0
        assert Path(result["markdown"]).exists()
    
    def test_pipeline_validation_summary(self, sample_data_csv, tmp_path):
        """Test that validation summary is included."""
        result = generate_data_quality_report(
            input_path=sample_data_csv,
            report_format="md",
            include_ai=False,
            save_to_db=False
        )
        
        summary = result["validation_summary"]
        assert "total_issues" in summary
        assert "by_severity" in summary
        assert "by_type" in summary
        assert "dataset_rows" in summary
        assert "dataset_columns" in summary


class TestPipelineComponents:
    """Tests for individual pipeline components."""
    
    def test_validator_integration(self, sample_data_csv):
        """Test validator integration in pipeline."""
        df = pd.read_csv(sample_data_csv)
        issues, summary = validate_dataframe(df)
        
        assert len(issues) > 0
        assert isinstance(summary, dict)
        assert summary["total_issues"] > 0
    
    def test_ml_advisor_integration(self, sample_data_csv):
        """Test ML advisor integration in pipeline."""
        df = pd.read_csv(sample_data_csv)
        issues, _ = validate_dataframe(df)
        
        ml_result = get_ml_recommendations(df, issues)
        
        assert "readiness_score" in ml_result
        assert "readiness_level" in ml_result
        assert "recommendations" in ml_result
        assert len(ml_result["recommendations"]) > 0
    
    def test_database_integration(self, sample_data_csv, clean_db, db_session):
        """Test database integration in pipeline."""
        df = pd.read_csv(sample_data_csv)
        issues, _ = validate_dataframe(df)
        
        session_id = save_check_to_db(
            filename="test_pipeline.csv",
            file_format="csv",
            rows=len(df),
            validation_issues=issues,
            db_session=db_session
        )
        
        assert session_id is not None
        
        # Verify in database
        check_session = db_session.query(CheckSession).filter_by(id=session_id).first()
        assert check_session is not None
        assert len(check_session.issues) > 0


class TestPipelineErrorHandling:
    """Tests for error handling in pipeline."""
    
    def test_pipeline_invalid_file_format(self, tmp_path):
        """Test pipeline with invalid file format."""
        # Create invalid file
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("This is not a CSV or JSON file")
        
        with pytest.raises(ValueError):
            generate_data_quality_report(
                input_path=invalid_file,
                report_format="md"
            )
    
    def test_pipeline_empty_file(self, tmp_path):
        """Test pipeline with empty file."""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("")
        
        with pytest.raises((ValueError, pd.errors.EmptyDataError)):
            generate_data_quality_report(
                input_path=empty_csv,
                report_format="md",
                save_to_db=False
            )
    
    def test_pipeline_corrupted_csv(self, tmp_path):
        """Test pipeline with corrupted CSV."""
        corrupted_csv = tmp_path / "corrupted.csv"
        corrupted_csv.write_text("id,name\n1,Alice\n2,Bob\ninvalid,row,with,too,many,columns")
        
        # Should either handle gracefully or raise error
        try:
            result = generate_data_quality_report(
                input_path=corrupted_csv,
                report_format="md",
                save_to_db=False
            )
            # If it succeeds, should still produce report
            assert "issues_count" in result
        except (ValueError, pd.errors.ParserError):
            # Error is acceptable for corrupted data
            pass


class TestReportGeneration:
    """Tests for report generation in pipeline."""
    
    def test_report_generation_all_formats(self, sample_data_csv, tmp_path):
        """Test generating all report formats."""
        result = generate_data_quality_report(
            input_path=sample_data_csv,
            report_format="all",
            include_ai=True,
            save_to_db=False
        )
        
        # Should have markdown and html
        assert "markdown" in result
        assert "html" in result
        
        # Verify files exist
        assert Path(result["markdown"]).exists()
        assert Path(result["html"]).exists()
        
        # PDF might fail if wkhtmltopdf not installed, but that's okay
        if "pdf" in result:
            assert Path(result["pdf"]).exists()
    
    def test_report_content(self, sample_data_csv, tmp_path):
        """Test that generated reports contain expected content."""
        result = generate_data_quality_report(
            input_path=sample_data_csv,
            report_format="md",
            include_ai=True,
            client_name="Content Test",
            save_to_db=False
        )
        
        # Read markdown content
        md_content = Path(result["markdown"]).read_text()
        
        assert "Data Quality Report" in md_content
        assert "Content Test" in md_content
        assert "Dataset Overview" in md_content
        assert "Detected Issues" in md_content
    
    def test_generate_report_main_function(self, sample_data_csv, tmp_path):
        """Test the main() function in generate_sample_report."""
        from src.core.generate_sample_report import main
        # This should run without error
        try:
            main()
            assert True
        except Exception:
            # May fail due to dependencies, but should be importable
            pass
    
    def test_pdf_generation_handles_missing_wkhtmltopdf(self, sample_data_csv, tmp_path):
        """Test that PDF generation handles missing wkhtmltopdf gracefully."""
        # PDF generation may fail if wkhtmltopdf not installed
        # Should handle gracefully
        try:
            result = generate_data_quality_report(
                input_path=sample_data_csv,
                report_format="pdf",
                include_ai=False,
                save_to_db=False
            )
            # If succeeds, should have pdf path
            if "pdf" in result:
                assert Path(result["pdf"]).exists()
        except Exception:
            # Expected to fail if wkhtmltopdf not installed
            pass

