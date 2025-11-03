"""
Data Quality Validator

Comprehensive data validation module that checks for:
- Data type consistency
- Missing values
- Duplicates
- Format validation (email, phone, dates)
- Range validation for numeric data
- Outliers detection
"""

import pandas as pd
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np


class ValidationIssue:
    """Represents a single validation issue found in the dataset."""
    
    def __init__(
        self,
        issue_type: str,
        description: str,
        severity: str = "medium",
        row_number: Optional[int] = None,
        column_name: Optional[str] = None
    ):
        self.issue_type = issue_type
        self.description = description
        self.severity = severity  # "low", "medium", "high"
        self.row_number = row_number
        self.column_name = column_name
    
    def to_dict(self) -> Dict:
        """Convert issue to dictionary format for database storage."""
        return {
            "issue_type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
            "row_number": self.row_number,
            "column_name": self.column_name
        }


class DataValidator:
    """Main validator class for data quality checks."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.issues: List[ValidationIssue] = []
    
    def validate_all(self) -> List[ValidationIssue]:
        """
        Run all validation checks and return list of issues.
        
        Returns:
            List of ValidationIssue objects
        """
        self.issues = []
        
        # Basic checks
        self._check_missing_values()
        self._check_duplicates()
        self._check_data_types()
        
        # Format validation
        self._validate_emails()
        self._validate_phones()
        self._validate_dates()
        
        # Numeric validation
        self._check_numeric_ranges()
        self._detect_outliers()
        
        # String validation
        self._check_empty_strings()
        self._check_string_lengths()
        
        return self.issues
    
    def _check_missing_values(self):
        """Check for missing/null values in the dataset."""
        missing = self.df.isnull().sum()
        
        for col in missing[missing > 0].index:
            missing_count = int(missing[col])
            missing_pct = (missing_count / len(self.df)) * 100
            
            severity = "high" if missing_pct > 50 else "medium" if missing_pct > 20 else "low"
            
            self.issues.append(ValidationIssue(
                issue_type="missing_values",
                description=f"Column '{col}' has {missing_count} missing values ({missing_pct:.1f}%)",
                severity=severity,
                column_name=col
            ))
    
    def _check_duplicates(self):
        """Check for duplicate rows."""
        duplicate_count = self.df.duplicated().sum()
        
        if duplicate_count > 0:
            duplicate_pct = (duplicate_count / len(self.df)) * 100
            severity = "high" if duplicate_pct > 10 else "medium"
            
            self.issues.append(ValidationIssue(
                issue_type="duplicates",
                description=f"Found {duplicate_count} duplicate rows ({duplicate_pct:.1f}% of dataset)",
                severity=severity
            ))
            
            # Find specific duplicate rows
            duplicates = self.df[self.df.duplicated(keep=False)]
            for idx in duplicates.index[:10]:  # Limit to first 10 for performance
                self.issues.append(ValidationIssue(
                    issue_type="duplicate_row",
                    description=f"Row {idx + 1} is a duplicate",
                    severity="medium",
                    row_number=int(idx)
                ))
    
    def _check_data_types(self):
        """Check for inconsistent data types within columns."""
        for col in self.df.columns:
            # Skip if column is all null
            if self.df[col].isnull().all():
                continue
            
            # Check numeric columns for non-numeric values
            if self.df[col].dtype in ['int64', 'float64']:
                non_numeric = pd.to_numeric(self.df[col], errors='coerce').isnull() & self.df[col].notnull()
                if non_numeric.any():
                    count = non_numeric.sum()
                    self.issues.append(ValidationIssue(
                        issue_type="type_inconsistency",
                        description=f"Column '{col}' (numeric) contains {count} non-numeric value(s)",
                        severity="high",
                        column_name=col
                    ))
            
            # Check for mixed types in object columns
            elif self.df[col].dtype == 'object':
                # Sample values to check for type mixing
                sample_values = self.df[col].dropna().head(100)
                if len(sample_values) > 0:
                    # Check if we have both strings and numbers
                    has_strings = any(isinstance(v, str) for v in sample_values)
                    has_numbers = any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in sample_values)
                    
                    if has_strings and has_numbers:
                        self.issues.append(ValidationIssue(
                            issue_type="mixed_types",
                            description=f"Column '{col}' contains mixed data types (strings and numbers)",
                            severity="medium",
                            column_name=col
                        ))
    
    def _validate_emails(self):
        """Validate email format in columns that appear to contain emails."""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        for col in self.df.columns:
            # Heuristic: column name contains 'email' or 'mail'
            if 'email' in col.lower() or 'mail' in col.lower():
                if self.df[col].dtype == 'object':
                    invalid_emails = []
                    for idx, value in self.df[col].items():
                        if pd.notna(value) and isinstance(value, str):
                            if not email_pattern.match(value):
                                invalid_emails.append((idx, value))
                                if len(invalid_emails) >= 50:  # Limit for performance
                                    break
                    
                    if invalid_emails:
                        self.issues.append(ValidationIssue(
                            issue_type="invalid_email_format",
                            description=f"Column '{col}' contains {len(invalid_emails)} invalid email format(s)",
                            severity="medium",
                            column_name=col
                        ))
                        
                        # Add specific row issues
                        for idx, value in invalid_emails[:10]:
                            self.issues.append(ValidationIssue(
                                issue_type="invalid_email",
                                description=f"Row {idx + 1}: Invalid email format '{value}'",
                                severity="medium",
                                row_number=int(idx),
                                column_name=col
                            ))
    
    def _validate_phones(self):
        """Validate phone number format."""
        # Common phone patterns (US, international)
        phone_pattern = re.compile(r'^[\d\s\-\+\(\)]{7,20}$')
        
        for col in self.df.columns:
            if 'phone' in col.lower() or 'tel' in col.lower():
                if self.df[col].dtype == 'object':
                    invalid_phones = []
                    for idx, value in self.df[col].items():
                        if pd.notna(value) and isinstance(value, str):
                            # Remove spaces and common formatting for validation
                            cleaned = re.sub(r'[\s\-\(\)]', '', str(value))
                            if not (cleaned.isdigit() and 7 <= len(cleaned) <= 15):
                                invalid_phones.append((idx, value))
                                if len(invalid_phones) >= 50:
                                    break
                    
                    if invalid_phones:
                        self.issues.append(ValidationIssue(
                            issue_type="invalid_phone_format",
                            description=f"Column '{col}' contains {len(invalid_phones)} invalid phone number(s)",
                            severity="low",
                            column_name=col
                        ))
    
    def _validate_dates(self):
        """Validate date format and detect date-like columns."""
        for col in self.df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                if self.df[col].dtype == 'object':
                    invalid_dates = []
                    for idx, value in self.df[col].items():
                        if pd.notna(value):
                            try:
                                pd.to_datetime(value)
                            except (ValueError, TypeError):
                                invalid_dates.append((idx, value))
                                if len(invalid_dates) >= 50:
                                    break
                    
                    if invalid_dates:
                        self.issues.append(ValidationIssue(
                            issue_type="invalid_date_format",
                            description=f"Column '{col}' contains {len(invalid_dates)} invalid date format(s)",
                            severity="medium",
                            column_name=col
                        ))
    
    def _check_numeric_ranges(self):
        """Check numeric columns for values outside reasonable ranges."""
        for col in self.df.select_dtypes(include=[np.number]).columns:
            if self.df[col].notna().any():
                # Use IQR method for range detection
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 3 * IQR  # Extended range
                upper_bound = Q3 + 3 * IQR
                
                outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()
                
                if outliers > 0:
                    # Check for negative values in columns that shouldn't have them
                    if col.lower() in ['age', 'price', 'amount', 'count', 'quantity', 'id']:
                        negatives = (self.df[col] < 0).sum()
                        if negatives > 0:
                            self.issues.append(ValidationIssue(
                                issue_type="negative_values",
                                description=f"Column '{col}' contains {negatives} negative value(s)",
                                severity="medium",
                                column_name=col
                            ))
    
    def _detect_outliers(self):
        """Detect statistical outliers using IQR method."""
        for col in self.df.select_dtypes(include=[np.number]).columns:
            if self.df[col].notna().sum() > 4:  # Need at least 5 values
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                if IQR > 0:  # Avoid division by zero
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                    outlier_count = outlier_mask.sum()
                    
                    if outlier_count > 0:
                        outlier_pct = (outlier_count / len(self.df)) * 100
                        severity = "high" if outlier_pct > 10 else "medium"
                        
                        self.issues.append(ValidationIssue(
                            issue_type="outliers",
                            description=f"Column '{col}' has {outlier_count} outlier(s) ({outlier_pct:.1f}%)",
                            severity=severity,
                            column_name=col
                        ))
    
    def _check_empty_strings(self):
        """Check for empty strings that should be null."""
        for col in self.df.select_dtypes(include=['object']).columns:
            empty_count = (self.df[col] == '').sum()
            
            if empty_count > 0:
                self.issues.append(ValidationIssue(
                    issue_type="empty_strings",
                    description=f"Column '{col}' contains {empty_count} empty string(s) (consider converting to null)",
                    severity="low",
                    column_name=col
                ))
    
    def _check_string_lengths(self):
        """Check for unusually long or short string values."""
        for col in self.df.select_dtypes(include=['object']).columns:
            if self.df[col].notna().any():
                lengths = self.df[col].astype(str).str.len()
                max_length = lengths.max()
                min_length = lengths.min()
                
                # Flag if there's a huge variation in string lengths (potential data quality issue)
                if max_length > min_length * 10 and max_length > 100:
                    self.issues.append(ValidationIssue(
                        issue_type="string_length_variation",
                        description=f"Column '{col}' has high variation in string lengths (min: {min_length}, max: {max_length})",
                        severity="low",
                        column_name=col
                    ))
    
    def get_summary(self) -> Dict:
        """Get summary statistics about validation issues."""
        severity_counts = {"low": 0, "medium": 0, "high": 0}
        type_counts = {}
        
        for issue in self.issues:
            severity_counts[issue.severity] += 1
            type_counts[issue.issue_type] = type_counts.get(issue.issue_type, 0) + 1
        
        return {
            "total_issues": len(self.issues),
            "by_severity": severity_counts,
            "by_type": type_counts,
            "dataset_rows": len(self.df),
            "dataset_columns": len(self.df.columns)
        }


def validate_dataframe(df: pd.DataFrame) -> Tuple[List[Dict], Dict]:
    """
    Main validation function.
    
    Args:
        df: pandas DataFrame to validate
        
    Returns:
        Tuple of (list of issue dictionaries, summary dictionary)
    """
    validator = DataValidator(df)
    issues = validator.validate_all()
    
    return (
        [issue.to_dict() for issue in issues],
        validator.get_summary()
    )

