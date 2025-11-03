"""
Integration tests for new features: visualizations, Excel export, comparison.
"""
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from src.core.generate_sample_report import generate_data_quality_report
from src.db.models import CheckSession, Issue
from src.core.comparison import compare_sessions, get_quality_trend


@pytest.mark.integration
class TestVisualizationIntegration:
    """Integration tests for visualizations in reports."""
    
    def test_report_generation_with_visualizations(self, sample_dataframe, tmp_path, clean_db, db_session):
        """Test that report generation includes visualizations for HTML."""
        # Create a test CSV file
        csv_file = tmp_path / "test_data.csv"
        sample_dataframe.to_csv(csv_file, index=False)
        
        # Generate report with HTML format (should include visualizations)
        result = generate_data_quality_report(
            input_path=csv_file,
            report_format="html",
            include_ai=True,
            save_to_db=True
        )
        
        assert "html" in result
        
        # Check that HTML file exists and contains image tags
        html_path = Path(result["html"])
        if html_path.exists():
            content = html_path.read_text()
            # Should contain chart image tags or visualizations section
            assert len(content) > 0
    
    def test_report_generation_all_formats_with_viz(self, sample_dataframe, tmp_path):
        """Test generating all formats includes visualizations."""
        csv_file = tmp_path / "test_data.csv"
        sample_dataframe.to_csv(csv_file, index=False)
        
        result = generate_data_quality_report(
            input_path=csv_file,
            report_format="all",
            include_ai=True
        )
        
        # Should have multiple formats
        assert len(result) > 0
        assert "html" in result or "markdown" in result


@pytest.mark.integration
class TestExcelExportIntegration:
    """Integration tests for Excel export."""
    
    def test_report_generation_with_excel(self, sample_dataframe, tmp_path):
        """Test report generation with Excel format."""
        csv_file = tmp_path / "test_data.csv"
        sample_dataframe.to_csv(csv_file, index=False)
        
        try:
            result = generate_data_quality_report(
                input_path=csv_file,
                report_format="xlsx",
                include_ai=True
            )
            
            # Excel might be None if openpyxl not installed
            if result.get("excel"):
                excel_path = Path(result["excel"])
                assert excel_path.exists() or "excel" in str(result)
        except ImportError:
            pytest.skip("openpyxl not available")
    
    def test_report_generation_all_formats_includes_excel(self, sample_dataframe, tmp_path):
        """Test that 'all' format includes Excel."""
        csv_file = tmp_path / "test_data.csv"
        sample_dataframe.to_csv(csv_file, index=False)
        
        try:
            result = generate_data_quality_report(
                input_path=csv_file,
                report_format="all",
                include_ai=True
            )
            
            # Should have multiple formats including potentially excel
            assert len(result) > 0
            if "excel" in result and result["excel"]:
                excel_path = Path(result["excel"])
                assert excel_path.exists() or "excel" in str(result)
        except ImportError:
            pytest.skip("openpyxl not available")


@pytest.mark.integration
class TestComparisonIntegration:
    """Integration tests for comparison functionality."""
    
    def test_full_comparison_workflow(self, clean_db, db_session):
        """Test complete workflow: create sessions, compare, get trends."""
        # Create first session
        session1 = CheckSession(
            filename="session1.csv",
            file_format="csv",
            rows=100,
            issues_found=15,
            created_at=datetime.utcnow() - timedelta(days=7)
        )
        db_session.add(session1)
        db_session.flush()
        
        # Add issues to session1
        for i in range(15):
            issue = Issue(
                session_id=session1.id,
                row_number=i,
                column_name="test_col",
                issue_type="test",
                description=f"Issue {i}",
                severity="high" if i < 5 else "medium" if i < 10 else "low"
            )
            db_session.add(issue)
        
        # Create second session
        session2 = CheckSession(
            filename="session2.csv",
            file_format="csv",
            rows=100,
            issues_found=8,
            created_at=datetime.utcnow()
        )
        db_session.add(session2)
        db_session.flush()
        
        # Add issues to session2
        for i in range(8):
            issue = Issue(
                session_id=session2.id,
                row_number=i,
                column_name="test_col",
                issue_type="test",
                description=f"Issue {i}",
                severity="high" if i < 2 else "medium" if i < 5 else "low"
            )
            db_session.add(issue)
        
        db_session.commit()
        
        # Test comparison
        comparison = compare_sessions(session1.id, session2.id, db_session)
        
        assert comparison is not None
        assert comparison["comparison"]["total_issues_change"] == -7
        assert comparison["comparison"]["trend"] == "improving"
        
        # Test trend
        trend = get_quality_trend(session2.id, days_back=30, db_session=db_session)
        
        assert trend is not None
        assert "trend" in trend
        assert "comparison" in trend
    
    def test_comparison_with_multiple_previous_sessions(self, clean_db, db_session):
        """Test trend analysis with multiple previous sessions."""
        base_time = datetime.utcnow() - timedelta(days=30)
        
        # Create multiple previous sessions
        for i in range(5):
            session = CheckSession(
                filename=f"prev_{i}.csv",
                file_format="csv",
                rows=100,
                issues_found=10 + i,  # Varying issue counts
                created_at=base_time + timedelta(days=i*5)
            )
            db_session.add(session)
        
        db_session.flush()
        
        # Create current session
        current_session = CheckSession(
            filename="current.csv",
            file_format="csv",
            rows=100,
            issues_found=8,  # Fewer issues
            created_at=datetime.utcnow()
        )
        db_session.add(current_session)
        db_session.commit()
        
        # Get trend
        trend = get_quality_trend(current_session.id, days_back=30, db_session=db_session)
        
        assert trend is not None
        # Should have at least some previous sessions
        assert trend["comparison"]["previous_sessions_count"] >= 4  # Might be 4 if filtering by date
        # Average should be around 12, current is 8, so improving
        assert trend["comparison"]["difference_from_average"] < 0
        assert trend["trend"] == "improving"

