"""
Unit tests for custom validation rules engine.
"""
import pytest
import pandas as pd
from src.core.validation_rules import ValidationRuleEngine


pytestmark = pytest.mark.unit


class TestValidationRuleEngine:
    """Tests for ValidationRuleEngine."""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", None, "David", "Eve"],
            "email": ["alice@example.com", "invalid", "charlie@example.com", "david@example.com", "eve@example.com"],
            "age": [30, 150, 35, -5, 25],
            "status": ["active", "inactive", "active", "pending", "active"]
        })
    
    def test_missing_threshold_rule(self, sample_df):
        """Test missing threshold validation rule."""
        rules = [{
            "rule_name": "check_name_missing",
            "rule_type": "missing_threshold",
            "enabled": True,
            "parameters": {
                "column": "name",
                "threshold": 10  # 20% missing (1 out of 5)
            }
        }]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(sample_df)
        
        assert len(issues) > 0
        assert any("missing_threshold" in issue.get("issue_type", "") for issue in issues)
    
    def test_range_check_rule(self, sample_df):
        """Test range check validation rule."""
        rules = [{
            "rule_name": "check_age_range",
            "rule_type": "range_check",
            "enabled": True,
            "parameters": {
                "column": "age",
                "min": 0,
                "max": 120
            }
        }]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(sample_df)
        
        # Should find age 150 (above max) and age -5 (below min)
        assert len(issues) >= 2
        assert any("above_maximum" in issue.get("issue_type", "") for issue in issues)
        assert any("below_minimum" in issue.get("issue_type", "") for issue in issues)
    
    def test_format_check_email(self, sample_df):
        """Test email format check."""
        rules = [{
            "rule_name": "check_email_format",
            "rule_type": "format_check",
            "enabled": True,
            "parameters": {
                "column": "email",
                "format": "email"
            }
        }]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(sample_df)
        
        # Should find invalid email format
        assert len(issues) > 0
        assert any("invalid_format" in issue.get("issue_type", "") for issue in issues)
    
    def test_required_column_rule(self, sample_df):
        """Test required column rule."""
        rules = [{
            "rule_name": "check_required_id",
            "rule_type": "required_column",
            "enabled": True,
            "parameters": {
                "column": "id"
            }
        }]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(sample_df)
        
        # Column exists, so no issues
        assert len(issues) == 0
    
    def test_required_column_missing(self, sample_df):
        """Test required column rule when column is missing."""
        rules = [{
            "rule_name": "check_required_column",
            "rule_type": "required_column",
            "enabled": True,
            "parameters": {
                "column": "nonexistent"
            }
        }]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(sample_df)
        
        # Column missing, so should find issue
        assert len(issues) > 0
        assert any("missing_column" in issue.get("issue_type", "") for issue in issues)
    
    def test_unique_check_rule(self):
        """Test unique check rule."""
        df = pd.DataFrame({
            "id": [1, 2, 3, 1, 4],
            "name": ["A", "B", "C", "D", "E"]
        })
        
        rules = [{
            "rule_name": "check_unique_id",
            "rule_type": "unique_check",
            "enabled": True,
            "parameters": {
                "column": "id"
            }
        }]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(df)
        
        # Should find duplicate values
        assert len(issues) > 0
        assert any("duplicate_values" in issue.get("issue_type", "") for issue in issues)
    
    def test_value_in_list_rule(self, sample_df):
        """Test value in list rule."""
        rules = [{
            "rule_name": "check_status_values",
            "rule_type": "value_in_list",
            "enabled": True,
            "parameters": {
                "column": "status",
                "allowed_values": ["active", "inactive"]
            }
        }]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(sample_df)
        
        # Should find "pending" which is not in allowed list
        assert len(issues) > 0
        assert any("invalid_value" in issue.get("issue_type", "") for issue in issues)
    
    def test_disabled_rule(self, sample_df):
        """Test that disabled rules are not executed."""
        rules = [{
            "rule_name": "disabled_rule",
            "rule_type": "missing_threshold",
            "enabled": False,
            "parameters": {
                "column": "name",
                "threshold": 10
            }
        }]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(sample_df)
        
        # No issues because rule is disabled
        assert len(issues) == 0
    
    def test_multiple_rules(self, sample_df):
        """Test validation with multiple rules."""
        rules = [
            {
                "rule_name": "check_name_missing",
                "rule_type": "missing_threshold",
                "enabled": True,
                "parameters": {"column": "name", "threshold": 10}
            },
            {
                "rule_name": "check_age_range",
                "rule_type": "range_check",
                "enabled": True,
                "parameters": {"column": "age", "min": 0, "max": 120}
            }
        ]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(sample_df)
        
        # Should find issues from both rules
        assert len(issues) >= 2
    
    def test_unknown_rule_type(self, sample_df):
        """Test handling of unknown rule type."""
        rules = [{
            "rule_name": "unknown_rule",
            "rule_type": "unknown_type",
            "enabled": True,
            "parameters": {}
        }]
        
        engine = ValidationRuleEngine(rules)
        issues = engine.validate(sample_df)
        
        # Should report unknown rule type as issue
        assert len(issues) > 0
        assert any("unknown_rule_type" in issue.get("issue_type", "") for issue in issues)

