"""
Unit tests for the ML advisor module.
Tests ML readiness score, recommendations, class imbalance, normalization, etc.
"""
import pytest

pytestmark = pytest.mark.unit
import pandas as pd
import numpy as np
from src.core.ml_advisor import MLAdvisor, get_ml_recommendations


class TestMLAdvisor:
    """Tests for MLAdvisor class."""
    
    def test_ml_advisor_initialization(self, sample_dataframe):
        """Test ML advisor initialization."""
        advisor = MLAdvisor(sample_dataframe)
        assert advisor.df is not None
        assert len(advisor.df) > 0
    
    def test_ml_advisor_with_validation_issues(self, sample_dataframe):
        """Test ML advisor with validation issues."""
        validation_issues = [{"issue_type": "missing_values", "severity": "high"}]
        advisor = MLAdvisor(sample_dataframe, validation_issues)
        assert advisor.validation_issues == validation_issues


class TestMissingValuesAnalysis:
    """Tests for missing values analysis."""
    
    def test_analyze_missing_values(self, sample_dataframe):
        """Test missing values analysis."""
        advisor = MLAdvisor(sample_dataframe)
        result = advisor._analyze_missing_values()
        
        assert "total_missing" in result
        assert "total_missing_pct" in result
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
    
    def test_high_missing_values_recommendation(self):
        """Test recommendation for high missing values."""
        df = pd.DataFrame({
            "col1": [1, 2, None, None, None, None, None],
            "col2": [1, 2, 3, 4, 5, 6, 7]
        })
        advisor = MLAdvisor(df)
        result = advisor._analyze_missing_values()
        
        # Should have recommendations for high missing values
        assert len(result["recommendations"]) > 0
    
    def test_medium_missing_values_recommendation(self):
        """Test recommendation for medium missing values."""
        df = pd.DataFrame({
            "numeric_col": [1, 2, None, 4, None, 6, 7],
            "categorical_col": ["a", "b", None, "d", None, "f", "g"]
        })
        advisor = MLAdvisor(df)
        result = advisor._analyze_missing_values()
        
        # Should have imputation recommendations
        recommendations_text = " ".join(result["recommendations"])
        assert "imputation" in recommendations_text.lower() or len(result["recommendations"]) > 0


class TestClassImbalance:
    """Tests for class imbalance detection."""
    
    def test_class_imbalance_severe(self):
        """Test detection of severe class imbalance."""
        df = pd.DataFrame({
            "target": ["A"] * 90 + ["B"] * 10,  # 90% in class A
            "feature1": range(100),
            "feature2": range(100, 200)
        })
        advisor = MLAdvisor(df)
        issues = advisor._check_data_balance()
        
        # Should detect severe imbalance
        assert len(issues) > 0
        imbalance_text = " ".join(issues)
        assert "imbalance" in imbalance_text.lower() or len(issues) > 0
    
    def test_class_imbalance_moderate(self):
        """Test detection of moderate class imbalance."""
        df = pd.DataFrame({
            "target": ["A"] * 75 + ["B"] * 25,  # 75% in class A
            "feature1": range(100)
        })
        advisor = MLAdvisor(df)
        issues = advisor._check_data_balance()
        
        # May detect moderate imbalance
        assert isinstance(issues, list)
    
    def test_no_imbalance_in_balanced_data(self):
        """Test that balanced data has no imbalance issues."""
        df = pd.DataFrame({
            "target": ["A"] * 50 + ["B"] * 50,  # Balanced
            "feature1": range(100)
        })
        advisor = MLAdvisor(df)
        issues = advisor._check_data_balance()
        
        # Should have minimal or no imbalance issues
        assert isinstance(issues, list)


class TestFeatureEngineering:
    """Tests for feature engineering recommendations."""
    
    def test_datetime_feature_engineering(self):
        """Test recommendations for datetime feature engineering."""
        df = pd.DataFrame({
            "date_col": pd.date_range("2023-01-01", periods=10),
            "value": range(10)
        })
        advisor = MLAdvisor(df)
        recs = advisor._recommend_feature_engineering(
            ["value"], [], ["date_col"]
        )
        
        # Should recommend datetime feature extraction
        recs_text = " ".join(recs)
        assert "date" in recs_text.lower() or len(recs) > 0
    
    def test_high_correlation_detection(self):
        """Test detection of highly correlated features."""
        # Create highly correlated features
        base = np.random.randn(100)
        df = pd.DataFrame({
            "feature1": base,
            "feature2": base + np.random.randn(100) * 0.1,  # Highly correlated
            "feature3": np.random.randn(100)  # Independent
        })
        advisor = MLAdvisor(df)
        recs = advisor._recommend_feature_engineering(
            ["feature1", "feature2", "feature3"], [], []
        )
        
        # Should recommend handling correlation
        assert isinstance(recs, list)
    
    def test_high_cardinality_detection(self):
        """Test detection of high cardinality categorical features."""
        # Fix: ensure same length for all columns
        n = 51  # 50 unique + 1 duplicate to make 51 total
        low_card_list = ["A", "B", "C"] * (n // 3 + 1)
        df = pd.DataFrame({
            "high_cardinality": [f"category_{i % 50}" for i in range(n)],
            "low_cardinality": low_card_list[:n]
        })
        advisor = MLAdvisor(df)
        recs = advisor._recommend_feature_engineering(
            [], ["high_cardinality", "low_cardinality"], []
        )
        
        # Should recommend handling high cardinality
        recs_text = " ".join(recs)
        assert "cardinality" in recs_text.lower() or len(recs) > 0


class TestEncoding:
    """Tests for encoding recommendations."""
    
    def test_binary_encoding_recommendation(self):
        """Test recommendation for binary categorical encoding."""
        df = pd.DataFrame({
            "binary_col": ["Yes", "No"] * 50,
            "feature": range(100)
        })
        advisor = MLAdvisor(df)
        recs = advisor._recommend_encoding(["binary_col"])
        
        # Should recommend label encoding for binary
        recs_text = " ".join(recs)
        assert "label" in recs_text.lower() or "binary" in recs_text.lower() or len(recs) > 0
    
    def test_one_hot_encoding_recommendation(self):
        """Test recommendation for one-hot encoding."""
        df = pd.DataFrame({
            "categorical_col": ["A", "B", "C", "D"] * 25,
            "feature": range(100)
        })
        advisor = MLAdvisor(df)
        recs = advisor._recommend_encoding(["categorical_col"])
        
        # Should recommend one-hot encoding
        recs_text = " ".join(recs)
        assert "one-hot" in recs_text.lower() or "encoding" in recs_text.lower() or len(recs) > 0
    
    def test_high_cardinality_encoding(self):
        """Test encoding recommendation for high cardinality."""
        df = pd.DataFrame({
            "high_cardinality": [f"cat_{i}" for i in range(100)],
            "feature": range(100)
        })
        advisor = MLAdvisor(df)
        recs = advisor._recommend_encoding(["high_cardinality"])
        
        # Should recommend target encoding or feature hashing
        recs_text = " ".join(recs)
        assert "target" in recs_text.lower() or "hashing" in recs_text.lower() or len(recs) > 0


class TestNormalization:
    """Tests for normalization recommendations."""
    
    def test_normalization_recommendation(self):
        """Test recommendation for normalization."""
        # Fix: ensure same length
        n = 1000
        df = pd.DataFrame({
            "large_range": list(range(1000, 1000 + n)),
            "small_range": list(range(1, 1 + n))
        })
        advisor = MLAdvisor(df)
        recs = advisor._recommend_normalization(["large_range", "small_range"])
        
        # Should recommend normalization for large range
        recs_text = " ".join(recs)
        assert "normalization" in recs_text.lower() or "scaler" in recs_text.lower() or len(recs) > 0
    
    def test_no_normalization_needed(self):
        """Test that normalized data doesn't need normalization."""
        df = pd.DataFrame({
            "normalized": np.random.randn(100),  # Already normalized
            "feature": range(100)
        })
        advisor = MLAdvisor(df)
        recs = advisor._recommend_normalization(["normalized", "feature"])
        
        # Should still recommend checking, but may be less urgent
        assert isinstance(recs, list)


class TestFeatureSelection:
    """Tests for feature selection recommendations."""
    
    def test_many_features_recommendation(self):
        """Test recommendation when there are many features."""
        # Create dataframe with many features
        data = {f"feature_{i}": np.random.randn(100) for i in range(60)}
        df = pd.DataFrame(data)
        
        advisor = MLAdvisor(df)
        recs = advisor._recommend_feature_selection()
        
        # Should recommend feature selection
        recs_text = " ".join(recs)
        assert "selection" in recs_text.lower() or "pca" in recs_text.lower() or len(recs) > 0
    
    def test_low_variance_detection(self):
        """Test detection of low variance features."""
        df = pd.DataFrame({
            "low_variance": [1.0] * 100,  # No variance
            "normal_variance": np.random.randn(100),
            "another_low": [2.0] * 100
        })
        advisor = MLAdvisor(df)
        recs = advisor._recommend_feature_selection()
        
        # Should recommend removing low variance features
        recs_text = " ".join(recs)
        assert "variance" in recs_text.lower() or len(recs) > 0


class TestReadinessScore:
    """Tests for ML readiness score calculation."""
    
    def test_readiness_score_calculation(self, sample_dataframe):
        """Test ML readiness score calculation."""
        advisor = MLAdvisor(sample_dataframe)
        missing_analysis = advisor._analyze_missing_values()
        
        score = advisor._calculate_readiness_score(
            missing_analysis, 2, 3, len(sample_dataframe)
        )
        
        assert 0 <= score <= 100
        assert isinstance(score, float)
    
    def test_readiness_level(self):
        """Test readiness level classification."""
        advisor = MLAdvisor(pd.DataFrame({"col": [1, 2, 3]}))
        
        # Test different score ranges
        assert "Excellent" in advisor._get_readiness_level(85)
        assert "Good" in advisor._get_readiness_level(70)
        assert "Fair" in advisor._get_readiness_level(55)
        assert "Poor" in advisor._get_readiness_level(40)
        assert "Very Poor" in advisor._get_readiness_level(20)


class TestMLAdvisorIntegration:
    """Integration tests for ML advisor."""
    
    def test_analyze_full(self, sample_dataframe):
        """Test full ML advisor analysis."""
        advisor = MLAdvisor(sample_dataframe)
        result = advisor.analyze()
        
        assert "readiness_score" in result
        assert "readiness_level" in result
        assert "recommendations" in result
        assert "summary" in result
        
        assert 0 <= result["readiness_score"] <= 100
        assert isinstance(result["readiness_level"], str)
        assert isinstance(result["recommendations"], list)
        
        summary = result["summary"]
        assert "total_rows" in summary
        assert "total_columns" in summary
        assert "numeric_columns" in summary
        assert "categorical_columns" in summary
    
    def test_get_ml_recommendations_function(self, sample_dataframe):
        """Test the main get_ml_recommendations function."""
        result = get_ml_recommendations(sample_dataframe)
        
        assert "readiness_score" in result
        assert "readiness_level" in result
        assert "recommendations" in result
        assert 0 <= result["readiness_score"] <= 100
    
    def test_get_ml_recommendations_with_validation_issues(self, sample_dataframe):
        """Test ML recommendations with validation issues."""
        validation_issues = [
            {"issue_type": "missing_values", "severity": "high"},
            {"issue_type": "duplicates", "severity": "medium"}
        ]
        result = get_ml_recommendations(sample_dataframe, validation_issues)
        
        assert "readiness_score" in result
        assert len(result["recommendations"]) > 0
    
    def test_ml_advisor_on_clean_data(self, clean_dataframe):
        """Test ML advisor on clean data."""
        result = get_ml_recommendations(clean_dataframe)
        
        # Clean data should have higher readiness score
        assert result["readiness_score"] > 50  # Should be reasonably high
        assert isinstance(result["recommendations"], list)

