"""
ML Advisor - Provides recommendations for preparing data for machine learning.

Analyzes datasets and provides actionable insights on:
- Feature engineering opportunities
- Data encoding requirements
- Missing value handling strategies
- Data normalization needs
- Feature selection recommendations
- Data readiness score for ML
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from collections import Counter


class MLAdvisor:
    """Provides ML-focused recommendations for data preparation."""
    
    def __init__(self, df: pd.DataFrame, validation_issues: Optional[List[Dict]] = None):
        self.df = df.copy()
        self.validation_issues = validation_issues or []
        self.recommendations: List[str] = []
        self.readiness_score: float = 0.0
    
    def analyze(self) -> Dict:
        """
        Perform comprehensive ML readiness analysis.
        
        Returns:
            Dictionary with recommendations and readiness score
        """
        self.recommendations = []
        
        # Basic dataset analysis
        total_rows = len(self.df)
        total_cols = len(self.df.columns)
        
        # Analyze data types
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Check missing values
        missing_analysis = self._analyze_missing_values()
        
        # Check data balance
        balance_issues = self._check_data_balance()
        
        # Feature engineering recommendations
        feature_recs = self._recommend_feature_engineering(numeric_cols, categorical_cols, datetime_cols)
        
        # Encoding recommendations
        encoding_recs = self._recommend_encoding(categorical_cols)
        
        # Normalization recommendations
        normalization_recs = self._recommend_normalization(numeric_cols)
        
        # Feature selection recommendations
        feature_selection_recs = self._recommend_feature_selection()
        
        # Calculate readiness score
        self.readiness_score = self._calculate_readiness_score(
            missing_analysis, len(numeric_cols), len(categorical_cols), total_rows
        )
        
        # Combine all recommendations
        all_recommendations = [
            *missing_analysis['recommendations'],
            *balance_issues,
            *feature_recs,
            *encoding_recs,
            *normalization_recs,
            *feature_selection_recs
        ]
        
        return {
            "readiness_score": round(self.readiness_score, 2),
            "readiness_level": self._get_readiness_level(self.readiness_score),
            "recommendations": all_recommendations,
            "summary": {
                "total_rows": total_rows,
                "total_columns": total_cols,
                "numeric_columns": len(numeric_cols),
                "categorical_columns": len(categorical_cols),
                "datetime_columns": len(datetime_cols),
                "missing_data_pct": missing_analysis['total_missing_pct']
            }
        }
    
    def _analyze_missing_values(self) -> Dict:
        """Analyze missing values and provide handling strategies."""
        recommendations = []
        missing = self.df.isnull().sum()
        total_missing = missing.sum()
        total_cells = len(self.df) * len(self.df.columns)
        total_missing_pct = (total_missing / total_cells) * 100 if total_cells > 0 else 0
        
        if total_missing > 0:
            # High missing values threshold
            high_missing_cols = missing[missing > len(self.df) * 0.5].index.tolist()
            
            if high_missing_cols:
                recommendations.append(
                    f"⚠️ **High Missing Values**: {len(high_missing_cols)} column(s) have >50% missing data. "
                    f"Consider dropping: {', '.join(high_missing_cols[:3])}"
                )
            
            # Medium missing values - imputation strategies
            medium_missing_cols = missing[(missing > len(self.df) * 0.1) & (missing <= len(self.df) * 0.5)].index.tolist()
            
            if medium_missing_cols:
                for col in medium_missing_cols[:5]:
                    col_type = self.df[col].dtype
                    if pd.api.types.is_numeric_dtype(col_type):
                        recommendations.append(
                            f"📊 **Missing Values**: Column '{col}' ({col_type}) - "
                            f"Consider imputation: mean/median for numeric, mode for categorical"
                        )
                    else:
                        recommendations.append(
                            f"📊 **Missing Values**: Column '{col}' (categorical) - "
                            f"Consider: mode imputation, 'unknown' category, or dropping if missing >30%"
                        )
        
        return {
            "total_missing": int(total_missing),
            "total_missing_pct": round(total_missing_pct, 2),
            "recommendations": recommendations
        }
    
    def _check_data_balance(self) -> List[str]:
        """Check for class imbalance in target-like columns."""
        recommendations = []
        
        # Look for columns that might be target variables
        potential_targets = [col for col in self.df.columns 
                           if self.df[col].dtype in ['object', 'int64'] 
                           and self.df[col].nunique() < 20]
        
        for col in potential_targets[:3]:  # Check first 3 potential targets
            value_counts = self.df[col].value_counts()
            
            if len(value_counts) > 1:
                max_class_pct = (value_counts.iloc[0] / len(self.df)) * 100
                
                # Severe imbalance (>80% in one class)
                if max_class_pct > 80:
                    recommendations.append(
                        f"⚖️ **Class Imbalance**: Column '{col}' is highly imbalanced ({max_class_pct:.1f}% in dominant class). "
                        f"Consider: SMOTE, undersampling, or weighted loss functions"
                    )
                # Moderate imbalance (70-80%)
                elif max_class_pct > 70:
                    recommendations.append(
                        f"⚖️ **Class Imbalance**: Column '{col}' shows moderate imbalance ({max_class_pct:.1f}%). "
                        f"Monitor during training, consider class weights"
                    )
        
        return recommendations
    
    def _recommend_feature_engineering(self, numeric_cols: List, categorical_cols: List, datetime_cols: List) -> List[str]:
        """Provide feature engineering recommendations."""
        recommendations = []
        
        # Date feature engineering
        if datetime_cols:
            recommendations.append(
                f"📅 **Date Features**: Extract features from {len(datetime_cols)} datetime column(s): "
                f"year, month, day_of_week, is_weekend, time_since_epoch"
            )
        
        # Numeric feature engineering
        if len(numeric_cols) >= 3:
            # Check for potential interaction features
            recommendations.append(
                f"🔢 **Numeric Features**: {len(numeric_cols)} numeric column(s) detected. "
                f"Consider: polynomial features, ratios, or interactions between top features"
            )
            
            # Check for high correlation pairs (potential for feature selection)
            if len(numeric_cols) > 1:
                corr_matrix = self.df[numeric_cols].corr().abs()
                high_corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        if corr_matrix.iloc[i, j] > 0.8:
                            high_corr_pairs.append(
                                f"{corr_matrix.columns[i]} & {corr_matrix.columns[j]}"
                            )
                
                if high_corr_pairs:
                    recommendations.append(
                        f"🔗 **High Correlation**: {len(high_corr_pairs)} highly correlated pairs detected (>0.8). "
                        f"Consider removing one from each pair to reduce multicollinearity"
                    )
        
        # Categorical feature engineering
        if categorical_cols:
            high_cardinality = [col for col in categorical_cols 
                              if self.df[col].nunique() > 20]
            
            if high_cardinality:
                recommendations.append(
                    f"🏷️ **High Cardinality**: {len(high_cardinality)} categorical column(s) with >20 unique values. "
                    f"Consider: grouping rare categories, target encoding, or feature hashing"
                )
            
            # Check for potential ordinal encoding opportunities
            low_cardinality = [col for col in categorical_cols 
                             if 2 <= self.df[col].nunique() <= 10]
            
            if low_cardinality:
                recommendations.append(
                    f"✅ **Encoding Ready**: {len(low_cardinality)} categorical column(s) suitable for one-hot encoding"
                )
        
        return recommendations
    
    def _recommend_encoding(self, categorical_cols: List) -> List[str]:
        """Recommend encoding strategies for categorical variables."""
        recommendations = []
        
        if not categorical_cols:
            return recommendations
        
        for col in categorical_cols[:5]:  # Analyze first 5
            unique_count = self.df[col].nunique()
            
            if unique_count == 2:
                recommendations.append(
                    f"🔤 **Encoding**: Column '{col}' (binary) - Use label encoding (0/1)"
                )
            elif 3 <= unique_count <= 10:
                recommendations.append(
                    f"🔤 **Encoding**: Column '{col}' ({unique_count} categories) - Use one-hot encoding or ordinal if ordered"
                )
            elif 11 <= unique_count <= 50:
                recommendations.append(
                    f"🔤 **Encoding**: Column '{col}' ({unique_count} categories) - "
                    f"Consider: one-hot (if <20), target encoding, or embedding for deep learning"
                )
            else:
                recommendations.append(
                    f"🔤 **Encoding**: Column '{col}' ({unique_count} categories) - "
                    f"High cardinality - Use target encoding, frequency encoding, or feature hashing"
                )
        
        return recommendations
    
    def _recommend_normalization(self, numeric_cols: List) -> List[str]:
        """Recommend normalization/standardization strategies."""
        recommendations = []
        
        if not numeric_cols:
            return recommendations
        
        # Check for wide ranges (need normalization)
        for col in numeric_cols[:5]:
            if self.df[col].notna().any():
                col_min = self.df[col].min()
                col_max = self.df[col].max()
                col_std = self.df[col].std()
                
                # Large range or high variance
                if col_std > 0:
                    cv = col_std / abs(self.df[col].mean()) if self.df[col].mean() != 0 else float('inf')
                    
                    if abs(col_max - col_min) > 1000 or cv > 1:
                        recommendations.append(
                            f"📏 **Normalization**: Column '{col}' has wide range ({col_min:.2f} to {col_max:.2f}). "
                            f"Apply: StandardScaler or MinMaxScaler before training"
                        )
        
        if numeric_cols:
            recommendations.append(
                f"📏 **Scaling**: {len(numeric_cols)} numeric column(s) - "
                f"Recommend StandardScaler (if normal distribution) or MinMaxScaler (if bounded)"
            )
        
        return recommendations
    
    def _recommend_feature_selection(self) -> List[str]:
        """Recommend feature selection strategies."""
        recommendations = []
        
        total_cols = len(self.df.columns)
        
        # Too many features
        if total_cols > 50:
            recommendations.append(
                f"🎯 **Feature Selection**: {total_cols} features detected - "
                f"Consider: PCA, feature importance (tree-based), or correlation-based selection"
            )
        elif total_cols > 20:
            recommendations.append(
                f"🎯 **Feature Selection**: {total_cols} features - "
                f"Consider evaluating feature importance to reduce dimensionality"
            )
        
        # Check for low variance features
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            low_variance = []
            for col in numeric_cols:
                if self.df[col].std() < 0.01:  # Very low variance
                    low_variance.append(col)
            
            if low_variance:
                recommendations.append(
                    f"🎯 **Low Variance**: {len(low_variance)} feature(s) with very low variance - "
                    f"Consider removing: {', '.join(low_variance[:3])}"
                )
        
        return recommendations
    
    def _calculate_readiness_score(
        self, 
        missing_analysis: Dict, 
        num_numeric: int, 
        num_categorical: int, 
        total_rows: int
    ) -> float:
        """
        Calculate ML readiness score (0-100).
        
        Higher score = more ready for ML.
        """
        score = 100.0
        
        # Penalize for missing data
        missing_pct = missing_analysis['total_missing_pct']
        if missing_pct > 50:
            score -= 40
        elif missing_pct > 30:
            score -= 25
        elif missing_pct > 10:
            score -= 15
        elif missing_pct > 5:
            score -= 5
        
        # Penalize for too few rows
        if total_rows < 100:
            score -= 20
        elif total_rows < 500:
            score -= 10
        elif total_rows < 1000:
            score -= 5
        
        # Penalize for no numeric features (most ML algorithms need numeric)
        if num_numeric == 0:
            score -= 15
        
        # Bonus for having both numeric and categorical (more flexible)
        if num_numeric > 0 and num_categorical > 0:
            score += 5
        
        # Penalize for too many categorical with high cardinality
        if num_categorical > 10:
            score -= 10
        
        # Ensure score is between 0 and 100
        return max(0, min(100, score))
    
    def _get_readiness_level(self, score: float) -> str:
        """Get human-readable readiness level."""
        if score >= 80:
            return "Excellent - Ready for ML"
        elif score >= 65:
            return "Good - Minor preparation needed"
        elif score >= 50:
            return "Fair - Moderate preparation required"
        elif score >= 35:
            return "Poor - Significant preparation needed"
        else:
            return "Very Poor - Major data issues"


def get_ml_recommendations(df: pd.DataFrame, validation_issues: Optional[List[Dict]] = None) -> Dict:
    """
    Main function to get ML recommendations.
    
    Args:
        df: pandas DataFrame to analyze
        validation_issues: Optional list of validation issues from validator
        
    Returns:
        Dictionary with recommendations and readiness score
    """
    advisor = MLAdvisor(df, validation_issues)
    return advisor.analyze()

