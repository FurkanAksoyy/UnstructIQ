import pandas as pd
import json
import os
from typing import Dict, Any
from fastapi import HTTPException
from datetime import datetime


def parse_file(file_path: str) -> pd.DataFrame:
    """
    Parse various file formats and return pandas DataFrame

    Supported formats: CSV, JSON, Excel (xlsx, xls)
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.csv':
            # Try different encodings
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin-1')

        elif file_ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("JSON must be a list or dict")

        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)

        elif file_ext == '.txt':
            for delimiter in [',', '\t', ';', '|']:
                try:
                    df = pd.read_csv(file_path, delimiter=delimiter)
                    if len(df.columns) > 1:
                        break
                except:
                    continue

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}"
            )

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="File is empty or couldn't be parsed"
            )

        # Auto-detect and parse datetime columns
        df = auto_parse_dates(df)

        return df

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse file: {str(e)}"
        )


def auto_parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Automatically detect and parse datetime columns
    """
    for col in df.columns:
        # Skip if already datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue

        # Check for common datetime column names
        datetime_keywords = ['date', 'time', 'timestamp', 'created', 'updated', 'dt']
        if any(keyword in col.lower() for keyword in datetime_keywords):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                print(f"Parsed datetime column: {col}")
            except:
                pass

        # Try parsing if column is object type and sample looks like date
        elif df[col].dtype == 'object':
            try:
                sample = df[col].dropna().head(10).astype(str)
                if sample.str.match(r'\d{4}[-/]\d{2}[-/]\d{2}').any():
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    print(f"Auto-detected and parsed datetime column: {col}")
            except:
                pass

    return df


def get_dataframe_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get basic information about the DataFrame
    """
    info = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "column_types": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
    }
    return info


def get_data_preview(df: pd.DataFrame, rows: int = 10) -> Dict[str, Any]:
    """
    Get preview of DataFrame (first N rows)
    """
    preview_df = df.head(rows)

    # Convert to JSON-serializable format
    preview_data = []
    for _, row in preview_df.iterrows():
        row_dict = {}
        for col in df.columns:
            val = row[col]
            # Handle different types
            if pd.isna(val):
                row_dict[col] = None
            elif isinstance(val, (pd.Timestamp, datetime)):
                row_dict[col] = val.isoformat()
            else:
                row_dict[col] = str(val)
        preview_data.append(row_dict)

    return {
        "columns": df.columns.tolist(),
        "data": preview_data,
        "total_rows": len(df)
    }