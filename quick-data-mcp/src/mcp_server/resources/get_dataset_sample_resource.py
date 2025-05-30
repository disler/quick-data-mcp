"""Dataset sample resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional


async def get_dataset_sample(dataset_name: str, n_rows: int = 5) -> dict:
    """Sample rows for data preview."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        # Get sample rows
        sample_df = df.head(n_rows)
        
        return {
            "dataset_name": dataset_name,
            "sample_size": len(sample_df),
            "total_rows": len(df),
            "columns": list(df.columns),
            "sample_data": sample_df.to_dict('records')
        }
        
    except Exception as e:
        return {"error": f"Failed to get sample: {str(e)}"}