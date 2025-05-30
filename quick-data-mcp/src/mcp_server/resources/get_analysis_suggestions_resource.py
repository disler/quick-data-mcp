"""Analysis suggestions resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional


async def get_analysis_suggestions(dataset_name: Optional[str] = None) -> dict:
    """AI-generated analysis recommendations."""
    try:
        if dataset_name is None:
            datasets = DatasetManager.list_datasets()
            if not datasets:
                return {"error": "No datasets loaded"}
            dataset_name = datasets[-1]
        
        # Import here to avoid circular imports
        from ..tools.pandas_tools import suggest_analysis
        return await suggest_analysis(dataset_name)
        
    except Exception as e:
        return {"error": f"Failed to get suggestions: {str(e)}"}