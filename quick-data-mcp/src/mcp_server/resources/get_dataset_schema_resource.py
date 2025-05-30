"""Dataset schema resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional


async def get_dataset_schema(dataset_name: str) -> dict:
    """Get dynamic schema for any loaded dataset."""
    try:
        if dataset_name not in dataset_schemas:
            return {"error": f"Dataset '{dataset_name}' not loaded"}
        
        schema = dataset_schemas[dataset_name]
        
        # Organize columns by type
        columns_by_type = {
            "numerical": [],
            "categorical": [], 
            "temporal": [],
            "identifier": []
        }
        
        for col_name, col_info in schema.columns.items():
            columns_by_type[col_info.suggested_role].append({
                "name": col_name,
                "dtype": col_info.dtype,
                "unique_values": col_info.unique_values,
                "null_percentage": round(col_info.null_percentage, 1),
                "sample_values": col_info.sample_values
            })
        
        return {
            "dataset_name": dataset_name,
            "total_rows": schema.row_count,
            "total_columns": len(schema.columns),
            "columns_by_type": columns_by_type,
            "suggested_analyses": schema.suggested_analyses,
            "schema_generated": True
        }
        
    except Exception as e:
        return {"error": f"Failed to get schema: {str(e)}"}