# tests/test_data_loader.py

import pytest
import pandas as pd
from fastapi import UploadFile
from io import BytesIO

from src.core.data_loader import load_data

# Mock UploadFile class for testing purposes
class FakeUploadFile(UploadFile):
    def __init__(self, content: str, filename: str):
        super().__init__(filename=filename, file=BytesIO(content.encode("utf-8")))

# Test loading CSV file
@pytest.mark.asyncio
async def test_load_csv_file():
    csv_data = "col1,col2\n1,2\n3,4"
    file = FakeUploadFile(content=csv_data, filename="test.csv")
    df = await load_data(file)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)

# Test loading JSON file
@pytest.mark.asyncio
async def test_load_json_file():
    json_data = '[{"col1": 1, "col2": 2}, {"col1": 3, "col2": 4}]'
    file = FakeUploadFile(content=json_data, filename="test.json")
    df = await load_data(file)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)

# Test loading XML file
@pytest.mark.asyncio
async def test_load_xml_file():
    xml_data = '''
    <root>
        <row><col1>1</col1><col2>2</col2></row>
        <row><col1>3</col1><col2>4</col2></row>
    </root>
    '''
    file = FakeUploadFile(content=xml_data, filename="test.xml")
    df = await load_data(file)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)