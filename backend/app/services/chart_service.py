import pandas as pd
from typing import List, Dict, Any
from google import genai
from app.config import settings
import json
import re
from datetime import datetime, date
import numpy as np
import math

# Configure Gemini Client
client = None
if settings.GEMINI_API_KEY:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_charts(df: pd.DataFrame, user_prompt: str = "") -> List[Dict[str, Any]]:
    """
    Generate chart configurations using AI
    """
    try:
        if client and settings.GEMINI_API_KEY:
            return generate_charts_with_ai(df, user_prompt)
        else:
            return generate_charts_fallback(df)
    except Exception as e:
        print(f"AI chart generation failed: {e}")
        return generate_charts_fallback(df)


def generate_charts_with_ai(df: pd.DataFrame, user_prompt: str = "") -> List[Dict[str, Any]]:
    """
    Use Gemini AI to intelligently select and configure charts
    """
    # Convert datetime columns to strings for JSON serialization
    df_safe = df.copy()
    for col in df_safe.columns:
        if pd.api.types.is_datetime64_any_dtype(df_safe[col]):
            df_safe[col] = df_safe[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Get column info
    numeric_cols = df_safe.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df_safe.select_dtypes(include=['object']).columns.tolist()

    # Prepare data summary with JSON-safe values
    data_summary = {
        "columns": df_safe.columns.tolist(),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "row_count": len(df_safe),
        "sample_values": {}
    }

    # Add sample values for each column (JSON-safe)
    for col in df_safe.columns[:10]:
        sample_vals = df_safe[col].head(5).tolist()
        # Convert any remaining numpy types
        sample_vals = [convert_to_json_safe(val) for val in sample_vals]
        data_summary["sample_values"][col] = sample_vals

    # Create prompt for Gemini
    prompt = f"""
You are a data visualization expert. Analyze this dataset and suggest the MOST MEANINGFUL charts.

Dataset Information:
{json.dumps(data_summary, indent=2)}

User's Instructions: {user_prompt if user_prompt else "No specific instructions"}

IMPORTANT RULES:
1. SKIP ID columns (record_id, user_id, id, etc.) - they should NOT be visualized
2. For timestamps/dates, create TIME-SERIES charts with proper date formatting
3. For categorical data with many unique values (>20), show only top 10
4. Choose chart types that make BUSINESS SENSE
5. Maximum 4 charts total

Suggest 3-4 charts in the following JSON format:
{{
  "charts": [
    {{
      "type": "bar|pie|line|scatter",
      "title": "Clear descriptive title",
      "columns": ["column_name1", "column_name2"],
      "aggregation": "mean|sum|count|none",
      "description": "Why this chart is useful"
    }}
  ]
}}

Respond ONLY with valid JSON.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )

        if response and response.text:
            json_text = response.text.strip()

            # Remove markdown code blocks
            if '```' in json_text:
                parts = json_text.split('```')
                for part in parts:
                    if part.strip().startswith('{') or part.strip().startswith('json'):
                        json_text = part.replace('json', '').strip()
                        break

            # Try to parse
            try:
                ai_suggestions = json.loads(json_text)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', json_text, re.DOTALL)
                if json_match:
                    ai_suggestions = json.loads(json_match.group())
                else:
                    raise

            print("=== AI CHART SUGGESTIONS ===")
            print(json.dumps(ai_suggestions, indent=2))

            # Convert AI suggestions to Chart.js configs
            charts = []
            for suggestion in ai_suggestions.get('charts', [])[:4]:
                chart_config = create_chart_from_suggestion(df, suggestion)
                if chart_config:
                    # Clean the entire chart config recursively
                    chart_config = clean_chart_data(chart_config)
                    charts.append(chart_config)

            return charts if charts else generate_charts_fallback(df)

    except Exception as e:
        print(f"AI chart generation error: {e}")
        return generate_charts_fallback(df)

    return generate_charts_fallback(df)


def create_chart_from_suggestion(df: pd.DataFrame, suggestion: dict) -> Dict[str, Any]:
    """
    Convert AI suggestion to Chart.js config
    """
    chart_type = suggestion.get('type', 'bar')
    columns = suggestion.get('columns', [])
    title = suggestion.get('title', 'Chart')
    aggregation = suggestion.get('aggregation', 'none')

    if not columns or not all(col in df.columns for col in columns):
        return None

    try:
        if chart_type == 'bar':
            col = columns[0]

            # Handle datetime columns
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df_temp = df.copy()
                df_temp[col] = df_temp[col].dt.strftime('%Y-%m-%d')
                value_counts = df_temp[col].value_counts().head(10)
                labels = value_counts.index.tolist()
                values = value_counts.values.tolist()
            elif aggregation == 'count' or df[col].dtype == 'object':
                value_counts = df[col].value_counts().head(10)
                labels = [str(x) for x in value_counts.index.tolist()]
                values = value_counts.values.tolist()
            else:
                labels = [col]
                values = [float(df[col].mean())]

            return {
                "type": "bar",
                "title": title,
                "description": suggestion.get('description', ''),
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "label": col,
                        "data": values,
                        "backgroundColor": "rgba(99, 102, 241, 0.6)",
                        "borderColor": "rgba(99, 102, 241, 1)",
                        "borderWidth": 2
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "legend": {"display": True},
                        "title": {"display": True, "text": title}
                    }
                }
            }

        elif chart_type == 'pie':
            col = columns[0]
            value_counts = df[col].value_counts().head(10)

            return {
                "type": "pie",
                "title": title,
                "description": suggestion.get('description', ''),
                "data": {
                    "labels": [str(x) for x in value_counts.index.tolist()],
                    "datasets": [{
                        "data": value_counts.values.tolist(),
                        "backgroundColor": [
                            "rgba(99, 102, 241, 0.8)",
                            "rgba(139, 92, 246, 0.8)",
                            "rgba(236, 72, 153, 0.8)",
                            "rgba(34, 211, 238, 0.8)",
                            "rgba(251, 146, 60, 0.8)",
                            "rgba(132, 204, 22, 0.8)",
                            "rgba(248, 113, 113, 0.8)",
                            "rgba(253, 224, 71, 0.8)",
                            "rgba(167, 139, 250, 0.8)",
                            "rgba(94, 234, 212, 0.8)",
                        ]
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "legend": {"position": "right"},
                        "title": {"display": True, "text": title}
                    }
                }
            }

        elif chart_type == 'line':
            col = columns[0]

            # Check if it's a datetime column
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df_sorted = df.sort_values(col)
                labels = df_sorted[col].dt.strftime('%Y-%m-%d %H:%M').tolist()[:50]
                # Count occurrences per timestamp
                data_values = df_sorted[col].value_counts().sort_index().head(50).values.tolist()
            else:
                labels = [f"Point {i + 1}" for i in range(min(len(df), 50))]
                data_values = df[col].head(50).tolist()

            return {
                "type": "line",
                "title": title,
                "description": suggestion.get('description', ''),
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "label": col,
                        "data": data_values,
                        "borderColor": "rgba(139, 92, 246, 1)",
                        "backgroundColor": "rgba(139, 92, 246, 0.1)",
                        "borderWidth": 2,
                        "fill": True,
                        "tension": 0.4
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "legend": {"display": True},
                        "title": {"display": True, "text": title}
                    }
                }
            }

        elif chart_type == 'scatter' and len(columns) >= 2:
            col1, col2 = columns[0], columns[1]

            scatter_data = []
            for x, y in zip(df[col1].head(50), df[col2].head(50)):
                scatter_data.append({
                    "x": x,
                    "y": y
                })

            return {
                "type": "scatter",
                "title": title,
                "description": suggestion.get('description', ''),
                "data": {
                    "datasets": [{
                        "label": f"{col1} vs {col2}",
                        "data": scatter_data,
                        "backgroundColor": "rgba(236, 72, 153, 0.6)",
                        "borderColor": "rgba(236, 72, 153, 1)",
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "legend": {"display": True},
                        "title": {"display": True, "text": title}
                    },
                    "scales": {
                        "x": {"title": {"display": True, "text": col1}},
                        "y": {"title": {"display": True, "text": col2}}
                    }
                }
            }

    except Exception as e:
        print(f"Chart creation error: {e}")
        return None

    return None


def generate_charts_fallback(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Fallback: Rule-based chart generation (improved)
    """
    charts = []

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Filter out ID columns
    numeric_cols = [col for col in numeric_cols if not any(x in col.lower() for x in ['id', '_id', 'index'])]
    categorical_cols = [col for col in categorical_cols if
                        not any(x in col.lower() for x in ['id', '_id', 'timestamp'])]

    # Chart 1: First meaningful numeric column
    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        chart = {
            "type": "bar",
            "title": f"{col.replace('_', ' ').title()} Overview",
            "description": f"Statistical overview of {col}",
            "data": {
                "labels": ["Mean", "Median", "Max", "Min"],
                "datasets": [{
                    "label": col,
                    "data": [
                        df[col].mean(),
                        df[col].median(),
                        df[col].max(),
                        df[col].min()
                    ],
                    "backgroundColor": "rgba(99, 102, 241, 0.6)",
                }]
            },
            "options": {"responsive": True}
        }
        charts.append(clean_chart_data(chart))

    # Chart 2: First categorical
    if len(categorical_cols) > 0:
        col = categorical_cols[0]
        value_counts = df[col].value_counts().head(10)

        chart = {
            "type": "pie",
            "title": f"{col.replace('_', ' ').title()} Distribution",
            "description": f"Distribution of {col}",
            "data": {
                "labels": [str(x) for x in value_counts.index.tolist()],
                "datasets": [{
                    "data": value_counts.values.tolist(),
                    "backgroundColor": [
                        "rgba(99, 102, 241, 0.8)",
                        "rgba(139, 92, 246, 0.8)",
                        "rgba(236, 72, 153, 0.8)",
                        "rgba(34, 211, 238, 0.8)",
                    ]
                }]
            },
            "options": {"responsive": True}
        }
        charts.append(clean_chart_data(chart))

    return charts


def clean_chart_data(obj):
    """
    Recursively clean chart data for JSON serialization
    Handles NaN, datetime, numpy types
    """
    if isinstance(obj, dict):
        return {key: clean_chart_data(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_chart_data(item) for item in obj]
    else:
        return convert_to_json_safe(obj)


def convert_to_json_safe(obj):
    """
    Convert non-JSON-serializable objects to JSON-safe format
    """
    # Handle NaN and infinity
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None

    # Handle datetime types
    if isinstance(obj, (datetime, date, pd.Timestamp)):
        return obj.isoformat()

    # Handle numpy types
    elif isinstance(obj, (np.integer, np.floating)):
        val = float(obj)
        if math.isnan(val) or math.isinf(val):
            return None
        return val

    # Handle numpy arrays
    elif isinstance(obj, np.ndarray):
        return [convert_to_json_safe(item) for item in obj.tolist()]

    # Handle pandas NA
    elif pd.isna(obj):
        return None

    # Handle basic types
    elif isinstance(obj, (int, float, str, bool)):
        return obj

    # Convert everything else to string
    else:
        return str(obj)