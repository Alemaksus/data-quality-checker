"""
Visualization utilities for data quality reports.
Generates charts for missing values, distributions, and data quality metrics.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import base64
import io
from typing import List, Dict, Optional
import os


def generate_missing_values_chart(df: pd.DataFrame) -> Optional[str]:
    """
    Generate a bar chart of missing values per column.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Base64 encoded PNG image string or None if no missing values
    """
    missing_counts = df.isnull().sum()
    missing_counts = missing_counts[missing_counts > 0]  # Only columns with missing values
    
    if len(missing_counts) == 0:
        return None
    
    # Create figure
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(missing_counts)), missing_counts.values, color='#ff6b6b')
    plt.xlabel('Columns', fontsize=12)
    plt.ylabel('Missing Values Count', fontsize=12)
    plt.title('Missing Values per Column', fontsize=14, fontweight='bold')
    plt.xticks(range(len(missing_counts)), missing_counts.index, rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # Convert to base64 string
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.read()).decode()
    plt.close()
    
    return img_str


def generate_missing_percentage_chart(df: pd.DataFrame) -> Optional[str]:
    """
    Generate a bar chart of missing values percentage per column.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Base64 encoded PNG image string or None if no missing values
    """
    missing_pct = (df.isnull().sum() / len(df)) * 100
    missing_pct = missing_pct[missing_pct > 0]  # Only columns with missing values
    
    if len(missing_pct) == 0:
        return None
    
    # Create figure
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(missing_pct)), missing_pct.values, color='#feca57')
    plt.xlabel('Columns', fontsize=12)
    plt.ylabel('Missing Values Percentage (%)', fontsize=12)
    plt.title('Missing Values Percentage per Column', fontsize=14, fontweight='bold')
    plt.xticks(range(len(missing_pct)), missing_pct.index, rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # Convert to base64 string
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.read()).decode()
    plt.close()
    
    return img_str


def generate_numeric_distribution_chart(df: pd.DataFrame, column: str) -> Optional[str]:
    """
    Generate a histogram for a numeric column.
    
    Args:
        df: Input DataFrame
        column: Column name to plot
        
    Returns:
        Base64 encoded PNG image string or None if column is not numeric
    """
    if column not in df.columns:
        return None
    
    try:
        numeric_data = pd.to_numeric(df[column], errors='coerce')
        numeric_data = numeric_data.dropna()
        
        if len(numeric_data) == 0:
            return None
        
        # Create figure
        plt.figure(figsize=(10, 6))
        plt.hist(numeric_data, bins=30, color='#48dbfb', edgecolor='black', alpha=0.7)
        plt.xlabel(column, fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title(f'Distribution of {column}', fontsize=14, fontweight='bold')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return img_str
    except Exception:
        return None


def generate_all_numeric_distributions(df: pd.DataFrame, max_columns: int = 4) -> Dict[str, str]:
    """
    Generate distribution charts for all numeric columns.
    
    Args:
        df: Input DataFrame
        max_columns: Maximum number of columns to plot
        
    Returns:
        Dictionary mapping column names to base64 encoded PNG strings
    """
    distributions = {}
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    for column in numeric_columns[:max_columns]:
        chart = generate_numeric_distribution_chart(df, column)
        if chart:
            distributions[column] = chart
    
    return distributions


def generate_issues_severity_chart(validation_issues: List[Dict]) -> Optional[str]:
    """
    Generate a pie chart of issues by severity.
    
    Args:
        validation_issues: List of validation issue dictionaries
        
    Returns:
        Base64 encoded PNG image string or None if no issues
    """
    if not validation_issues:
        return None
    
    # Count issues by severity
    severity_counts = {}
    for issue in validation_issues:
        severity = issue.get('severity', 'medium')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    if not severity_counts:
        return None
    
    # Create figure
    plt.figure(figsize=(8, 8))
    colors = {
        'high': '#ee5a6f',
        'medium': '#feca57',
        'low': '#48dbfb'
    }
    labels = list(severity_counts.keys())
    sizes = list(severity_counts.values())
    chart_colors = [colors.get(s, '#999999') for s in labels]
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=chart_colors, textprops={'fontsize': 12, 'fontweight': 'bold'})
    plt.title('Issues by Severity', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Convert to base64 string
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.read()).decode()
    plt.close()
    
    return img_str

