import os
import json
from datetime import datetime
from app.utils.file_parser import parse_file, get_dataframe_info
from app.utils.data_cleaner import clean_dataframe
from app.services.chart_service import generate_charts
from app.config import settings


def process_file(job_id: str) -> dict:
    """
    Process uploaded file

    Steps:
    1. Load metadata
    2. Parse file
    3. Clean data
    4. Generate statistics
    5. Generate charts
    6. Save processed data
    """
    try:
        # Load metadata
        job_dir = os.path.join(settings.UPLOAD_DIR, job_id)
        metadata_path = os.path.join(job_dir, "metadata.json")

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        file_path = metadata["file_path"]

        # Update status
        metadata["status"] = "processing"
        metadata["updated_at"] = datetime.now().isoformat()

        # Step 1: Parse file
        df = parse_file(file_path)
        original_info = get_dataframe_info(df)

        # Step 2: Clean data
        df_cleaned, cleaning_report = clean_dataframe(df)
        cleaned_info = get_dataframe_info(df_cleaned)

        # Step 3: Generate basic statistics
        statistics = generate_statistics(df_cleaned)

        # Step 4: Generate charts
        charts = generate_charts(df_cleaned)

        # Save processed data
        processed_dir = os.path.join(settings.PROCESSED_DIR, job_id)
        os.makedirs(processed_dir, exist_ok=True)

        # Save cleaned CSV
        cleaned_csv_path = os.path.join(processed_dir, "cleaned_data.csv")
        df_cleaned.to_csv(cleaned_csv_path, index=False)

        # Save processing results
        results = {
            "job_id": job_id,
            "status": "completed",
            "original_data_info": original_info,
            "cleaned_data_info": cleaned_info,
            "cleaning_report": cleaning_report,
            "statistics": statistics,
            "charts": charts,
            "processed_at": datetime.now().isoformat()
        }

        results_path = os.path.join(processed_dir, "results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)

        # Update metadata
        metadata["status"] = "completed"
        metadata["updated_at"] = datetime.now().isoformat()
        metadata["results_path"] = results_path

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return results

    except Exception as e:
        # Update metadata with error
        try:
            metadata["status"] = "failed"
            metadata["error"] = str(e)
            metadata["updated_at"] = datetime.now().isoformat()
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except:
            pass

        raise Exception(f"Processing failed: {str(e)}")


def generate_statistics(df):
    """Generate basic statistics from DataFrame"""
    stats = {
        "summary": {},
        "numeric_stats": {},
        "categorical_stats": {}
    }

    # Overall summary
    stats["summary"] = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "numeric_columns": len(df.select_dtypes(include=['number']).columns),
        "categorical_columns": len(df.select_dtypes(include=['object']).columns)
    }

    # Numeric columns statistics
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        stats["numeric_stats"][col] = {
            "mean": float(df[col].mean()),
            "median": float(df[col].median()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "max": float(df[col].max())
        }

    # Categorical columns statistics
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        value_counts = df[col].value_counts().head(10).to_dict()
        stats["categorical_stats"][col] = {
            "unique_values": int(df[col].nunique()),
            "most_common": value_counts
        }

    return stats