"""
Custom validation rules engine.
Allows configuration of custom validation rules.
"""
from typing import Dict, List, Optional, Callable
import pandas as pd
import re


class ValidationRuleEngine:
    """
    Engine for executing custom validation rules.
    """
    
    def __init__(self, rules: List[Dict] = None):
        """
        Initialize validation rule engine.
        
        Args:
            rules: List of validation rule dictionaries
        """
        self.rules = rules or []
        self.rule_handlers = {
            "missing_threshold": self._check_missing_threshold,
            "range_check": self._check_range,
            "format_check": self._check_format,
            "required_column": self._check_required_column,
            "unique_check": self._check_unique,
            "value_in_list": self._check_value_in_list,
        }
    
    def validate(self, df: pd.DataFrame) -> List[Dict]:
        """
        Validate DataFrame against configured rules.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            List of validation issues found
        """
        issues = []
        
        for rule in self.rules:
            if not rule.get("enabled", True):
                continue
            
            rule_type = rule.get("rule_type")
            rule_name = rule.get("rule_name", "unknown")
            parameters = rule.get("parameters", {})
            
            if rule_type in self.rule_handlers:
                handler = self.rule_handlers[rule_type]
                rule_issues = handler(df, rule_name, parameters)
                issues.extend(rule_issues)
            else:
                issues.append({
                    "rule_name": rule_name,
                    "issue_type": "unknown_rule_type",
                    "description": f"Unknown rule type: {rule_type}",
                    "severity": "medium"
                })
        
        return issues
    
    def _check_missing_threshold(self, df: pd.DataFrame, rule_name: str, params: Dict) -> List[Dict]:
        """Check missing values threshold."""
        issues = []
        column = params.get("column")
        threshold = params.get("threshold", 0)
        
        if column and column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_pct = (missing_count / len(df)) * 100
            
            if missing_pct > threshold:
                issues.append({
                    "rule_name": rule_name,
                    "issue_type": "missing_threshold_exceeded",
                    "column_name": column,
                    "description": f"Column '{column}' has {missing_pct:.2f}% missing values (threshold: {threshold}%)",
                    "severity": "high" if missing_pct > 50 else "medium"
                })
        
        return issues
    
    def _check_range(self, df: pd.DataFrame, rule_name: str, params: Dict) -> List[Dict]:
        """Check numeric range."""
        issues = []
        column = params.get("column")
        min_val = params.get("min")
        max_val = params.get("max")
        
        if column and column in df.columns:
            numeric_data = pd.to_numeric(df[column], errors='coerce')
            
            if min_val is not None:
                below_min = (numeric_data < min_val).sum()
                if below_min > 0:
                    issues.append({
                        "rule_name": rule_name,
                        "issue_type": "below_minimum",
                        "column_name": column,
                        "description": f"Column '{column}' has {below_min} values below minimum {min_val}",
                        "severity": "high"
                    })
            
            if max_val is not None:
                above_max = (numeric_data > max_val).sum()
                if above_max > 0:
                    issues.append({
                        "rule_name": rule_name,
                        "issue_type": "above_maximum",
                        "column_name": column,
                        "description": f"Column '{column}' has {above_max} values above maximum {max_val}",
                        "severity": "high"
                    })
        
        return issues
    
    def _check_format(self, df: pd.DataFrame, rule_name: str, params: Dict) -> List[Dict]:
        """Check format (email, phone, etc.)."""
        issues = []
        column = params.get("column")
        format_type = params.get("format", "email")
        
        if column and column in df.columns:
            if format_type == "email":
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                invalid = df[column].apply(
                    lambda x: pd.notna(x) and not bool(re.match(email_pattern, str(x)))
                ).sum()
                
                if invalid > 0:
                    issues.append({
                        "rule_name": rule_name,
                        "issue_type": "invalid_format",
                        "column_name": column,
                        "description": f"Column '{column}' has {invalid} invalid email formats",
                        "severity": "medium"
                    })
            
            elif format_type == "phone":
                phone_pattern = r'^\+?[\d\s\-\(\)]{10,}$'
                invalid = df[column].apply(
                    lambda x: pd.notna(x) and not bool(re.match(phone_pattern, str(x)))
                ).sum()
                
                if invalid > 0:
                    issues.append({
                        "rule_name": rule_name,
                        "issue_type": "invalid_format",
                        "column_name": column,
                        "description": f"Column '{column}' has {invalid} invalid phone formats",
                        "severity": "medium"
                    })
        
        return issues
    
    def _check_required_column(self, df: pd.DataFrame, rule_name: str, params: Dict) -> List[Dict]:
        """Check if required column exists."""
        issues = []
        column = params.get("column")
        
        if column and column not in df.columns:
            issues.append({
                "rule_name": rule_name,
                "issue_type": "missing_column",
                "column_name": column,
                "description": f"Required column '{column}' is missing",
                "severity": "high"
            })
        
        return issues
    
    def _check_unique(self, df: pd.DataFrame, rule_name: str, params: Dict) -> List[Dict]:
        """Check if column values are unique."""
        issues = []
        column = params.get("column")
        
        if column and column in df.columns:
            duplicates = df[column].duplicated().sum()
            
            if duplicates > 0:
                issues.append({
                    "rule_name": rule_name,
                    "issue_type": "duplicate_values",
                    "column_name": column,
                    "description": f"Column '{column}' has {duplicates} duplicate values",
                    "severity": "medium"
                })
        
        return issues
    
    def _check_value_in_list(self, df: pd.DataFrame, rule_name: str, params: Dict) -> List[Dict]:
        """Check if column values are in allowed list."""
        issues = []
        column = params.get("column")
        allowed_values = params.get("allowed_values", [])
        
        if column and column in df.columns and allowed_values:
            invalid = ~df[column].isin(allowed_values + [None, pd.NA])
            invalid_count = invalid.sum()
            
            if invalid_count > 0:
                issues.append({
                    "rule_name": rule_name,
                    "issue_type": "invalid_value",
                    "column_name": column,
                    "description": f"Column '{column}' has {invalid_count} values not in allowed list",
                    "severity": "medium"
                })
        
        return issues

