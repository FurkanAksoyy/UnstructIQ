from google import genai
from google.genai import types
from app.config import settings
import json

# Configure Gemini Client
client = None
if settings.GEMINI_API_KEY:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_insights(df_info: dict, statistics: dict, cleaning_report: dict) -> str:
    """
    Generate AI-powered insights using Gemini

    Args:
        df_info: DataFrame information
        statistics: Statistical analysis results
        cleaning_report: Data cleaning report

    Returns:
        AI-generated insights as string
    """
    try:
        if not client or not settings.GEMINI_API_KEY:
            return "⚠️ Gemini API key not configured. Please add GEMINI_API_KEY to your .env file."

        # Prepare prompt
        prompt = f"""
You are a data analyst AI. Analyze the following dataset information and provide insightful observations.

Dataset Information:
- Total Rows: {df_info.get('rows', 0)}
- Total Columns: {df_info.get('columns', 0)}
- Column Names: {', '.join(df_info.get('column_names', []))}

Data Cleaning Report:
{json.dumps(cleaning_report, indent=2)}

Statistical Summary:
{json.dumps(statistics, indent=2)}

Please provide:
1. **Key Findings** (3-5 bullet points) - Most important insights about the data
2. **Data Quality Assessment** - Brief assessment of data quality based on cleaning report
3. **Notable Patterns** - Any interesting patterns or trends you observe
4. **Recommendations** - 2-3 actionable recommendations based on the analysis

Format your response in clear markdown with headers and bullet points.
Keep it concise and business-focused.
"""

        # Call Gemini API
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )

        if response and response.text:
            return response.text
        else:
            return "⚠️ Unable to generate insights. Please try again."

    except Exception as e:
        return f"⚠️ Error generating insights: {str(e)}\n\nPlease check your Gemini API key."