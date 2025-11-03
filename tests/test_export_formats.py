"""
Unit tests for extended export formats.
"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import json
from src.core.export_formats import (
    export_to_csv,
    export_to_json,
    export_to_xml,
    export_to_parquet,
    export_validation_results,
    export_data_with_metadata
)


pytestmark = pytest.mark.unit


class TestExportFormats:
    """Tests for export format functions."""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame."""
        return pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [30, 25, 35]
        })
    
    @pytest.fixture
    def sample_issues(self):
        """Create sample validation issues."""
        return [
            {
                "row_number": 0,
                "column_name": "email",
                "issue_type": "missing_value",
                "description": "Missing email",
                "severity": "high"
            },
            {
                "row_number": 1,
                "column_name": "age",
                "issue_type": "outlier",
                "description": "Age is too high",
                "severity": "medium"
            }
        ]
    
    def test_export_to_csv(self, sample_df, tmp_path):
        """Test CSV export."""
        output_path = tmp_path / "test.csv"
        result = export_to_csv(sample_df, output_path)
        
        assert result == str(output_path)
        assert output_path.exists()
        
        # Verify content
        df_read = pd.read_csv(output_path)
        assert len(df_read) == 3
        assert list(df_read.columns) == ["id", "name", "age"]
    
    def test_export_to_json(self, sample_df, tmp_path):
        """Test JSON export."""
        output_path = tmp_path / "test.json"
        result = export_to_json(sample_df, output_path)
        
        assert result == str(output_path)
        assert output_path.exists()
        
        # Verify content
        with open(output_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 3
    
    def test_export_to_json_orient(self, sample_df, tmp_path):
        """Test JSON export with different orientations."""
        output_path = tmp_path / "test_index.json"
        result = export_to_json(sample_df, output_path, orient="index")
        
        assert result == str(output_path)
        assert output_path.exists()
    
    def test_export_to_xml(self, sample_df, tmp_path):
        """Test XML export."""
        try:
            output_path = tmp_path / "test.xml"
            result = export_to_xml(sample_df, output_path)
            
            assert result == str(output_path)
            assert output_path.exists()
            
            # Verify XML structure
            with open(output_path, 'r') as f:
                content = f.read()
                assert '<?xml' in content or '<data>' in content or '<root>' in content
        except (ImportError, AttributeError) as e:
            # pandas to_xml might not be available or lxml might not be installed
            pytest.skip(f"XML export not available: {e}")
    
    @pytest.mark.skipif(
        not hasattr(pd.DataFrame, 'to_parquet'),
        reason="Parquet export requires pyarrow"
    )
    def test_export_to_parquet(self, sample_df, tmp_path):
        """Test Parquet export."""
        try:
            output_path = tmp_path / "test.parquet"
            result = export_to_parquet(sample_df, output_path)
            
            assert result == str(output_path)
            assert output_path.exists()
            
            # Verify content
            df_read = pd.read_parquet(output_path)
            assert len(df_read) == 3
            assert list(df_read.columns) == ["id", "name", "age"]
        except ImportError:
            pytest.skip("pyarrow not installed")
    
    def test_export_validation_results_json(self, sample_issues, tmp_path):
        """Test validation results export to JSON."""
        output_path = tmp_path / "issues.json"
        result = export_validation_results(sample_issues, output_path, format="json")
        
        assert result == str(output_path)
        assert output_path.exists()
        
        # Verify content
        with open(output_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]["issue_type"] == "missing_value"
    
    def test_export_validation_results_csv(self, sample_issues, tmp_path):
        """Test validation results export to CSV."""
        output_path = tmp_path / "issues.csv"
        result = export_validation_results(sample_issues, output_path, format="csv")
        
        assert result == str(output_path)
        assert output_path.exists()
        
        # Verify content
        df = pd.read_csv(output_path)
        assert len(df) == 2
    
    def test_export_validation_results_xml(self, sample_issues, tmp_path):
        """Test validation results export to XML."""
        output_path = tmp_path / "issues.xml"
        result = export_validation_results(sample_issues, output_path, format="xml")
        
        assert result == str(output_path)
        assert output_path.exists()
        
        # Verify XML structure
        with open(output_path, 'r') as f:
            content = f.read()
            assert '<?xml' in content
    
    def test_export_data_with_metadata(self, sample_df, tmp_path):
        """Test data export with metadata."""
        metadata = {
            "session_id": 1,
            "timestamp": "2024-01-01T00:00:00",
            "issues_count": 5
        }
        
        output_path = tmp_path / "data_with_metadata.json"
        result = export_data_with_metadata(sample_df, metadata, output_path)
        
        assert result == str(output_path)
        assert output_path.exists()
        
        # Verify structure
        with open(output_path, 'r') as f:
            data = json.load(f)
            assert "metadata" in data
            assert "data" in data
            assert data["metadata"]["session_id"] == 1
            assert len(data["data"]) == 3
    
    def test_export_validation_results_invalid_format(self, sample_issues, tmp_path):
        """Test validation results export with invalid format."""
        output_path = tmp_path / "issues.txt"
        
        with pytest.raises(ValueError, match="Unsupported export format"):
            export_validation_results(sample_issues, output_path, format="txt")

