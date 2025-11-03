"""
Tests for visualization utilities.
"""
import pytest
import pandas as pd
import base64
from src.core.visualizations import (
    generate_missing_values_chart,
    generate_missing_percentage_chart,
    generate_numeric_distribution_chart,
    generate_all_numeric_distributions,
    generate_issues_severity_chart
)


@pytest.mark.unit
class TestMissingValuesChart:
    """Tests for missing values chart generation."""
    
    def test_generate_missing_values_chart_with_missing(self, sample_dataframe):
        """Test chart generation when there are missing values."""
        chart = generate_missing_values_chart(sample_dataframe)
        
        assert chart is not None
        assert isinstance(chart, str)
        assert len(chart) > 0
        
        # Should be base64 encoded image
        try:
            decoded = base64.b64decode(chart)
            assert len(decoded) > 0
        except Exception:
            pytest.fail("Chart should be valid base64 encoded image")
    
    def test_generate_missing_values_chart_no_missing(self, clean_dataframe):
        """Test chart generation when there are no missing values."""
        chart = generate_missing_values_chart(clean_dataframe)
        
        # Should return None when no missing values
        assert chart is None
    
    def test_generate_missing_values_chart_empty_dataframe(self):
        """Test chart generation with empty DataFrame."""
        df = pd.DataFrame()
        chart = generate_missing_values_chart(df)
        
        assert chart is None


@pytest.mark.unit
class TestMissingPercentageChart:
    """Tests for missing percentage chart generation."""
    
    def test_generate_missing_percentage_chart_with_missing(self, sample_dataframe):
        """Test percentage chart generation when there are missing values."""
        chart = generate_missing_percentage_chart(sample_dataframe)
        
        assert chart is not None
        assert isinstance(chart, str)
        assert len(chart) > 0
        
        # Should be base64 encoded image
        try:
            decoded = base64.b64decode(chart)
            assert len(decoded) > 0
        except Exception:
            pytest.fail("Chart should be valid base64 encoded image")
    
    def test_generate_missing_percentage_chart_no_missing(self, clean_dataframe):
        """Test percentage chart generation when there are no missing values."""
        chart = generate_missing_percentage_chart(clean_dataframe)
        
        assert chart is None


@pytest.mark.unit
class TestNumericDistributionChart:
    """Tests for numeric distribution chart generation."""
    
    def test_generate_numeric_distribution_chart_valid_column(self, sample_dataframe):
        """Test distribution chart for valid numeric column."""
        chart = generate_numeric_distribution_chart(sample_dataframe, 'salary')
        
        assert chart is not None
        assert isinstance(chart, str)
        assert len(chart) > 0
    
    def test_generate_numeric_distribution_chart_invalid_column(self, sample_dataframe):
        """Test distribution chart for non-existent column."""
        chart = generate_numeric_distribution_chart(sample_dataframe, 'nonexistent')
        
        assert chart is None
    
    def test_generate_numeric_distribution_chart_non_numeric(self, sample_dataframe):
        """Test distribution chart for non-numeric column."""
        chart = generate_numeric_distribution_chart(sample_dataframe, 'name')
        
        # Should handle gracefully
        assert chart is None or isinstance(chart, str)
    
    def test_generate_numeric_distribution_chart_all_nulls(self):
        """Test distribution chart for column with all nulls."""
        df = pd.DataFrame({'col': [None, None, None]})
        chart = generate_numeric_distribution_chart(df, 'col')
        
        assert chart is None


@pytest.mark.unit
class TestAllNumericDistributions:
    """Tests for generating all numeric distributions."""
    
    def test_generate_all_numeric_distributions(self, sample_dataframe):
        """Test generating distributions for all numeric columns."""
        distributions = generate_all_numeric_distributions(sample_dataframe)
        
        assert isinstance(distributions, dict)
        assert len(distributions) > 0
        
        # Should contain numeric columns
        for col_name, chart_img in distributions.items():
            assert isinstance(col_name, str)
            assert isinstance(chart_img, str)
            assert len(chart_img) > 0
    
    def test_generate_all_numeric_distributions_max_columns(self, sample_dataframe):
        """Test limiting number of columns."""
        distributions = generate_all_numeric_distributions(sample_dataframe, max_columns=2)
        
        assert len(distributions) <= 2
    
    def test_generate_all_numeric_distributions_no_numeric(self):
        """Test with DataFrame containing no numeric columns."""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'email': ['a@test.com', 'b@test.com']
        })
        distributions = generate_all_numeric_distributions(df)
        
        assert isinstance(distributions, dict)
        assert len(distributions) == 0


@pytest.mark.unit
class TestIssuesSeverityChart:
    """Tests for issues severity chart generation."""
    
    def test_generate_issues_severity_chart_with_issues(self):
        """Test severity chart generation with issues."""
        validation_issues = [
            {'severity': 'high', 'description': 'Issue 1'},
            {'severity': 'high', 'description': 'Issue 2'},
            {'severity': 'medium', 'description': 'Issue 3'},
            {'severity': 'medium', 'description': 'Issue 4'},
            {'severity': 'low', 'description': 'Issue 5'},
        ]
        
        chart = generate_issues_severity_chart(validation_issues)
        
        assert chart is not None
        assert isinstance(chart, str)
        assert len(chart) > 0
    
    def test_generate_issues_severity_chart_no_issues(self):
        """Test severity chart generation with no issues."""
        chart = generate_issues_severity_chart([])
        
        assert chart is None
    
    def test_generate_issues_severity_chart_mixed_severities(self):
        """Test severity chart with mixed severity levels."""
        validation_issues = [
            {'severity': 'high', 'description': 'Issue 1'},
            {'severity': 'medium', 'description': 'Issue 2'},
            {'severity': 'low', 'description': 'Issue 3'},
            {'severity': None, 'description': 'Issue 4'},  # Missing severity
        ]
        
        chart = generate_issues_severity_chart(validation_issues)
        
        assert chart is not None
        assert isinstance(chart, str)
    
    def test_generate_issues_severity_chart_default_severity(self):
        """Test severity chart when severity is missing (should default to medium)."""
        validation_issues = [
            {'description': 'Issue 1'},  # No severity
            {'description': 'Issue 2'},  # No severity
        ]
        
        chart = generate_issues_severity_chart(validation_issues)
        
        assert chart is not None

