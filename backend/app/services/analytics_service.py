import pandas as pd
import numpy as np
from typing import Dict, Any, List


def generate_correlation_matrix(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate correlation matrix for numeric columns
    """
    try:
        numeric_df = df.select_dtypes(include=['number'])

        if len(numeric_df.columns) < 2:
            return None

        # Calculate correlation
        corr_matrix = numeric_df.corr()

        # Convert to format suitable for heatmap
        correlation_data = {
            "columns": corr_matrix.columns.tolist(),
            "matrix": corr_matrix.values.tolist(),
            "pairs": []
        }

        # Find strong correlations (|r| > 0.7)
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    correlation_data["pairs"].append({
                        "col1": corr_matrix.columns[i],
                        "col2": corr_matrix.columns[j],
                        "correlation": float(corr_val),
                        "strength": "strong positive" if corr_val > 0.7 else "strong negative"
                    })

        return correlation_data

    except Exception as e:
        print(f"Correlation matrix error: {e}")
        return None


def detect_outliers(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect outliers using IQR method
    """
    outliers_report = {}

    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

        if len(outliers) > 0:
            outliers_report[col] = {
                "count": len(outliers),
                "percentage": round(len(outliers) / len(df) * 100, 2),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "outlier_values": outliers[col].tolist()[:10]  # First 10
            }

    return outliers_report


def detect_anomalies(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Simple anomaly detection
    """
    anomalies = {
        "duplicate_rows": int(df.duplicated().sum()),
        "columns_with_single_value": [],
        "columns_with_high_null_rate": []
    }

    # Columns with single unique value
    for col in df.columns:
        if df[col].nunique() == 1:
            anomalies["columns_with_single_value"].append(col)

    # Columns with >50% null values
    for col in df.columns:
        null_rate = df[col].isnull().sum() / len(df)
        if null_rate > 0.5:
            anomalies["columns_with_high_null_rate"].append({
                "column": col,
                "null_percentage": round(null_rate * 100, 2)
            })

    return anomalies


def generate_trends(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze trends for numeric columns
    """
    trends = {}

    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        # Calculate rolling statistics
        values = df[col].dropna()

        if len(values) > 2:
            # Simple trend detection
            first_half_mean = values.iloc[:len(values) // 2].mean()
            second_half_mean = values.iloc[len(values) // 2:].mean()

            change = second_half_mean - first_half_mean
            change_percent = (change / first_half_mean * 100) if first_half_mean != 0 else 0

            if abs(change_percent) > 5:
                trends[col] = {
                    "direction": "increasing" if change > 0 else "decreasing",
                    "change_percent": round(change_percent, 2),
                    "first_half_mean": round(first_half_mean, 2),
                    "second_half_mean": round(second_half_mean, 2)
                }

    return trends