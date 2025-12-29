import pandas as pd
import json
import os
from typing import Dict, Any
from fastapi import HTTPException


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
            # Handle both list of dicts and dict
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("JSON must be a list or dict")

        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)

        elif file_ext == '.txt':
            # Try to read as CSV with different delimiters
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

        return df

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse file: {str(e)}"
        )


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