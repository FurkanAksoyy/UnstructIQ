import pandas as pd
from typing import List, Dict, Any


def generate_charts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generate chart configurations from DataFrame

    Returns list of chart configs ready for Chart.js
    """
    charts = []

    # Get column types
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Chart 1: Numeric columns distribution (Bar Chart)
    if len(numeric_cols) > 0:
        chart_data = {
            "type": "bar",
            "title": "Numeric Columns Overview",
            "description": "Distribution of numeric values across columns",
            "data": {
                "labels": numeric_cols,
                "datasets": [{
                    "label": "Average Value",
                    "data": [float(df[col].mean()) for col in numeric_cols],
                    "backgroundColor": "rgba(99, 102, 241, 0.6)",
                    "borderColor": "rgba(99, 102, 241, 1)",
                    "borderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"display": True},
                    "title": {"display": True, "text": "Average Values by Column"}
                }
            }
        }
        charts.append(chart_data)

    # Chart 2: First categorical column distribution (Pie Chart)
    if len(categorical_cols) > 0:
        col = categorical_cols[0]
        value_counts = df[col].value_counts().head(10)

        chart_data = {
            "type": "pie",
            "title": f"{col.title()} Distribution",
            "description": f"Distribution of values in {col} column",
            "data": {
                "labels": value_counts.index.tolist(),
                "datasets": [{
                    "label": col.title(),
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
                    ],
                    "borderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "right"},
                    "title": {"display": True, "text": f"{col.title()} Distribution"}
                }
            }
        }
        charts.append(chart_data)

    # Chart 3: Numeric correlation (if multiple numeric columns)
    if len(numeric_cols) >= 2:
        first_col = numeric_cols[0]
        second_col = numeric_cols[1]

        chart_data = {
            "type": "scatter",
            "title": f"{first_col.title()} vs {second_col.title()}",
            "description": "Scatter plot showing relationship between two numeric columns",
            "data": {
                "datasets": [{
                    "label": f"{first_col} vs {second_col}",
                    "data": [
                        {"x": float(x), "y": float(y)}
                        for x, y in zip(df[first_col], df[second_col])
                    ],
                    "backgroundColor": "rgba(236, 72, 153, 0.6)",
                    "borderColor": "rgba(236, 72, 153, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"display": True},
                    "title": {"display": True, "text": f"{first_col} vs {second_col}"}
                },
                "scales": {
                    "x": {"title": {"display": True, "text": first_col}},
                    "y": {"title": {"display": True, "text": second_col}}
                }
            }
        }
        charts.append(chart_data)

    # Chart 4: Line chart for first numeric column (if exists)
    if len(numeric_cols) > 0:
        col = numeric_cols[0]

        chart_data = {
            "type": "line",
            "title": f"{col.title()} Trend",
            "description": f"Trend visualization for {col}",
            "data": {
                "labels": [f"Row {i + 1}" for i in range(len(df))],
                "datasets": [{
                    "label": col.title(),
                    "data": df[col].tolist(),
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
                    "title": {"display": True, "text": f"{col.title()} Over Data Points"}
                }
            }
        }
        charts.append(chart_data)

    return charts