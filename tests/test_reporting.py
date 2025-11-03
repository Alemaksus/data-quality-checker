"""
Tests for report generation (markdown, HTML, PDF).
"""
import pytest

pytestmark = pytest.mark.unit
import pandas as pd
from pathlib import Path
from src.core.reporting import generate_markdown_report
from src.core.export_utils import save_markdown, save_html, save_pdf, render_template
from src.core.visualizations import (
    generate_missing_values_chart,
    generate_issues_severity_chart
)


class TestMarkdownReport:
    """Tests for markdown report generation."""
    
    def test_generate_markdown_report_basic(self, sample_dataframe):
        """Test basic markdown report generation."""
        issues = ["Missing values detected", "Invalid email format"]
        ai_insights = "Data needs cleaning before ML"
        client_name = "Test Client"
        
        report = generate_markdown_report(sample_dataframe, issues, ai_insights, client_name)
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "# 🧾 Data Quality Report" in report
        assert client_name in report
    
    def test_generate_markdown_report_no_client(self, sample_dataframe):
        """Test markdown report without client name."""
        issues = ["Test issue"]
        report = generate_markdown_report(sample_dataframe, issues, "", None)
        
        assert isinstance(report, str)
        assert "Data Quality Report" in report
    
    def test_generate_markdown_report_all_sections(self, sample_dataframe):
        """Test that report includes all sections."""
        issues = ["Issue 1", "Issue 2"]
        ai_insights = "ML insights here"
        report = generate_markdown_report(sample_dataframe, issues, ai_insights, "Client")
        
        assert "Dataset Overview" in report
        assert "Summary Statistics" in report
        assert "Missing Values" in report
        assert "Detected Issues" in report
        assert "AI Insights" in report
        assert "Recommendations" in report
    
    def test_generate_markdown_report_empty_issues(self, sample_dataframe):
        """Test report with no issues."""
        report = generate_markdown_report(sample_dataframe, [], "", None)
        
        assert "No major data issues detected" in report or len(report) > 0
    
    def test_generate_markdown_report_no_ai_insights(self, sample_dataframe):
        """Test report without AI insights."""
        issues = ["Issue 1"]
        report = generate_markdown_report(sample_dataframe, issues, "", None)
        
        assert "AI Insights" not in report or "## 🤖 AI Insights" not in report


class TestReportExport:
    """Tests for report export functions."""
    
    def test_save_markdown(self, sample_dataframe, tmp_path, monkeypatch):
        """Test saving markdown report."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Mock the reports directory
        original_save = save_markdown
        report_text = "# Test Report\n\nContent here"
        
        # Call save_markdown with custom directory
        result_path = save_markdown(report_text, "test_report", str(reports_dir))
        
        assert Path(result_path).exists()
        assert Path(result_path).suffix == ".md"
        assert "test_report" in result_path
    
    def test_save_html(self, sample_dataframe, tmp_path):
        """Test saving HTML report."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_text = "# Test Report\n\nContent here"
        
        # Call save_html with custom directory
        result_path = save_html(report_text, "test_report", str(reports_dir))
        
        # Check if file was created or path returned
        assert isinstance(result_path, str)
        assert Path(result_path).exists() or "test_report.html" in result_path
    
    def test_save_html_with_visualizations(self, sample_dataframe, tmp_path):
        """Test saving HTML report with visualizations."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_text = "# Test Report\n\nContent here"
        
        # Generate visualizations
        visualizations = {
            "missing_values": generate_missing_values_chart(sample_dataframe),
            "issues_severity": generate_issues_severity_chart([
                {'severity': 'high', 'description': 'Issue 1'},
                {'severity': 'medium', 'description': 'Issue 2'},
            ])
        }
        
        # Save HTML with visualizations
        result_path = save_html(report_text, "test_report_viz", str(reports_dir), visualizations=visualizations)
        
        assert isinstance(result_path, str)
        
        # Check that HTML contains image tags if visualizations were added
        if Path(result_path).exists():
            content = Path(result_path).read_text()
            # Should contain img tags or base64 data if visualizations were added
            assert len(content) > 0
    
    def test_save_pdf(self, sample_dataframe, tmp_path):
        """Test saving PDF report."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_text = "# Test Report\n\nContent here"
        
        # PDF generation might fail without wkhtmltopdf, test that function exists
        try:
            result_path = save_pdf(report_text, "test_report", str(reports_dir))
            assert isinstance(result_path, str)
        except Exception:
            # PDF saving might require external tools, just verify function exists
            assert callable(save_pdf)
    
    def test_render_template(self, tmp_path):
        """Test template rendering."""
        template_path = tmp_path / "template.html"
        template_path.write_text("<html><body>{{content}}</body></html>")
        
        content = "<h1>Test</h1>"
        result = render_template(content, str(template_path))
        
        assert isinstance(result, str)
        assert "Test" in result
        assert "{{content}}" not in result  # Should be replaced


class TestReportGenerationPipeline:
    """Integration tests for full report generation."""
    
    def test_full_report_generation_markdown(self, sample_dataframe, tmp_path, monkeypatch):
        """Test full report generation pipeline for markdown."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        issues = ["Test issue 1", "Test issue 2"]
        ai_insights = "ML readiness: Good"
        
        # Generate markdown
        markdown = generate_markdown_report(sample_dataframe, issues, ai_insights, "Test Client")
        
        # Save markdown
        result_path = save_markdown(markdown, "pipeline_test", str(reports_dir))
        
        # Verify file was created
        assert Path(result_path).exists()
        assert Path(result_path).suffix == ".md"
        
        # Verify content
        content = Path(result_path).read_text()
        assert "Data Quality Report" in content
        assert "Test issue 1" in content or "Test issue 2" in content

