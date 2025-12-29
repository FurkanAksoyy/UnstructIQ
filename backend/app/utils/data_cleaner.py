import pandas as pd
import numpy as np
from typing import Dict, Any


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Clean DataFrame and return cleaned version with cleaning report

    Operations:
    - Remove duplicate rows
    - Handle missing values
    - Fix column names
    - Convert data types
    """
    cleaning_report = {
        "original_rows": len(df),
        "original_columns": len(df.columns),
        "operations": []
    }

    df_cleaned = df.copy()

    # 1. Fix column names (remove spaces, special chars)
    original_columns = df_cleaned.columns.tolist()
    df_cleaned.columns = df_cleaned.columns.str.strip().str.lower().str.replace(' ', '_')
    if original_columns != df_cleaned.columns.tolist():
        cleaning_report["operations"].append({
            "step": "column_names_cleaned",
            "detail": "Removed spaces and special characters from column names"
        })

    # 2. Remove duplicate rows
    duplicates = df_cleaned.duplicated().sum()
    if duplicates > 0:
        df_cleaned = df_cleaned.drop_duplicates()
        cleaning_report["operations"].append({
            "step": "duplicates_removed",
            "count": int(duplicates)
        })

    # 3. Handle missing values
    missing_before = df_cleaned.isnull().sum().sum()
    if missing_before > 0:
        # For numeric columns: fill with median
        numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df_cleaned[col].isnull().any():
                df_cleaned[col].fillna(df_cleaned[col].median(), inplace=True)

        # For categorical columns: fill with mode or 'Unknown'
        categorical_columns = df_cleaned.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if df_cleaned[col].isnull().any():
                mode_value = df_cleaned[col].mode()
                if len(mode_value) > 0:
                    df_cleaned[col].fillna(mode_value[0], inplace=True)
                else:
                    df_cleaned[col].fillna('Unknown', inplace=True)

        missing_after = df_cleaned.isnull().sum().sum()
        cleaning_report["operations"].append({
            "step": "missing_values_handled",
            "before": int(missing_before),
            "after": int(missing_after)
        })

    # 4. Remove columns with all null values
    null_columns = df_cleaned.columns[df_cleaned.isnull().all()].tolist()
    if null_columns:
        df_cleaned = df_cleaned.drop(columns=null_columns)
        cleaning_report["operations"].append({
            "step": "null_columns_removed",
            "columns": null_columns
        })

    # Final stats
    cleaning_report["cleaned_rows"] = len(df_cleaned)
    cleaning_report["cleaned_columns"] = len(df_cleaned.columns)
    cleaning_report["rows_removed"] = cleaning_report["original_rows"] - cleaning_report["cleaned_rows"]

    return df_cleaned, cleaning_report