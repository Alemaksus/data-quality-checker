"""
Extended export formats for data quality reports.
Supports CSV, JSON, XML, Parquet, and other formats.
"""
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Optional
import os


def export_to_csv(df: pd.DataFrame, output_path: Path) -> str:
    """
    Export DataFrame to CSV format.
    
    Args:
        df: DataFrame to export
        output_path: Output file path
        
    Returns:
        Path to created file
    """
    df.to_csv(output_path, index=False)
    return str(output_path)


def export_to_json(df: pd.DataFrame, output_path: Path, orient: str = "records") -> str:
    """
    Export DataFrame to JSON format.
    
    Args:
        df: DataFrame to export
        output_path: Output file path
        orient: JSON orientation (records, index, values, etc.)
        
    Returns:
        Path to created file
    """
    df.to_json(output_path, orient=orient, indent=2, date_format="iso")
    return str(output_path)


def export_to_xml(df: pd.DataFrame, output_path: Path) -> str:
    """
    Export DataFrame to XML format.
    
    Args:
        df: DataFrame to export
        output_path: Output file path
        
    Returns:
        Path to created file
    """
    try:
        # Use pandas built-in to_xml if available (pandas >= 1.3.0)
        df.to_xml(output_path, index=False)
    except AttributeError:
        # Fallback for older pandas versions
        import xml.etree.ElementTree as ET
        root = ET.Element("data")
        for idx, row in df.iterrows():
            record = ET.SubElement(root, "record")
            for col, val in row.items():
                elem = ET.SubElement(record, str(col))
                elem.text = str(val) if pd.notna(val) else ""
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
    
    return str(output_path)


def export_to_parquet(df: pd.DataFrame, output_path: Path) -> str:
    """
    Export DataFrame to Parquet format.
    
    Args:
        df: DataFrame to export
        output_path: Output file path
        
    Returns:
        Path to created file
    """
    df.to_parquet(output_path, index=False, engine='pyarrow')
    return str(output_path)


def export_validation_results(
    validation_issues: list,
    output_path: Path,
    format: str = "json"
) -> str:
    """
    Export validation issues to various formats.
    
    Args:
        validation_issues: List of validation issue dictionaries
        output_path: Output file path
        format: Export format (json, csv, xml)
        
    Returns:
        Path to created file
    """
    if format == "json":
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(validation_issues, f, indent=2, default=str)
        return str(output_path)
    
    elif format == "csv":
        df = pd.DataFrame(validation_issues)
        df.to_csv(output_path, index=False)
        return str(output_path)
    
    elif format == "xml":
        import xml.etree.ElementTree as ET
        root = ET.Element("validation_issues")
        for issue in validation_issues:
            record = ET.SubElement(root, "issue")
            for key, value in issue.items():
                elem = ET.SubElement(record, str(key))
                elem.text = str(value) if value is not None else ""
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        return str(output_path)
    
    else:
        raise ValueError(f"Unsupported export format: {format}")


def export_data_with_metadata(
    df: pd.DataFrame,
    metadata: Dict,
    output_path: Path,
    format: str = "json"
) -> str:
    """
    Export data with metadata in a structured format.
    
    Args:
        df: DataFrame to export
        metadata: Metadata dictionary
        output_path: Output file path
        format: Export format (json only for metadata)
        
    Returns:
        Path to created file
    """
    if format == "json":
        export_data = {
            "metadata": metadata,
            "data": df.to_dict(orient="records")
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        return str(output_path)
    else:
        raise ValueError(f"Metadata export only supports JSON format, got: {format}")

