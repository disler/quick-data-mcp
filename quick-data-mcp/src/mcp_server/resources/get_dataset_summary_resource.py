"""Dataset summary resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional


async def get_dataset_summary(dataset_name: str) -> dict:
    """Statistical summary (pandas.describe() equivalent)."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        # Get basic info
        summary = {
            "dataset_name": dataset_name,
            "shape": df.shape,
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        }
        
        # Numerical summary
        numerical_cols = df.select_dtypes(include=['number']).columns
        if len(numerical_cols) > 0:
            summary["numerical_summary"] = df[numerical_cols].describe().to_dict()
        
        # Categorical summary
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            summary["categorical_summary"] = {}
            for col in categorical_cols:
                summary["categorical_summary"][col] = {
                    "unique_count": df[col].nunique(),
                    "top_values": df[col].value_counts().head(5).to_dict(),
                    "null_count": df[col].isnull().sum()
                }
        
        # Missing data summary
        missing_data = df.isnull().sum()
        summary["missing_data"] = {
            "total_missing": int(missing_data.sum()),
            "columns_with_missing": missing_data[missing_data > 0].to_dict()
        }
        
        return summary
        
    except Exception as e:
        return {"error": f"Failed to generate summary: {str(e)}"}