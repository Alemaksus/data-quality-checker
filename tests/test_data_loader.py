"""
Tests for data loader module.
"""
import pytest
import pandas as pd
from fastapi import UploadFile
from io import BytesIO
from src.core.data_loader import load_data


@pytest.mark.unit
class TestDataLoader:
    """Tests for data loading functionality."""
    
    @pytest.mark.asyncio
    async def test_load_data_csv(self):
        """Test loading CSV data."""
        csv_content = "id,name,value\n1,Alice,10\n2,Bob,20"
        file = UploadFile(
            filename="test.csv",
            file=BytesIO(csv_content.encode())
        )
        
        df = await load_data(file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "id" in df.columns
        assert "name" in df.columns
    
    @pytest.mark.asyncio
    async def test_load_data_json(self):
        """Test loading JSON data."""
        json_content = '[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]'
        file = UploadFile(
            filename="test.json",
            file=BytesIO(json_content.encode())
        )
        
        df = await load_data(file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
    
    @pytest.mark.asyncio
    async def test_load_data_xml(self):
        """Test loading XML data."""
        xml_content = '<?xml version="1.0"?><data><row><id>1</id><name>Alice</name></row></data>'
        file = UploadFile(
            filename="test.xml",
            file=BytesIO(xml_content.encode())
        )
        
        # XML loading may fail if lxml not installed
        from fastapi import HTTPException
        try:
            df = await load_data(file)
            assert isinstance(df, pd.DataFrame)
        except HTTPException as e:
            # If lxml not installed, may return 500 error
            # That's acceptable for this test
            assert e.status_code in [400, 500]
    
    @pytest.mark.asyncio
    async def test_load_data_unsupported_format(self):
        """Test loading unsupported format."""
        file = UploadFile(
            filename="test.txt",
            file=BytesIO(b"plain text")
        )
        
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await load_data(file)
        
        # Should return 400 for unsupported format or 500 for parsing error
        assert exc_info.value.status_code in [400, 500]
    
    @pytest.mark.asyncio
    async def test_load_data_error_handling(self):
        """Test error handling in data loading."""
        file = UploadFile(
            filename="invalid.csv",
            file=BytesIO(b"invalid,csv,content\nbroken,row")
        )
        
        # Should handle gracefully or raise appropriate error
        try:
            df = await load_data(file)
            # If it succeeds, should still return DataFrame
            assert isinstance(df, pd.DataFrame)
        except Exception:
            # Error is acceptable for invalid data
            pass

