"""Loaded datasets resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional


async def get_loaded_datasets() -> dict:
    """List all datasets currently in memory."""
    try:
        datasets = []
        total_memory = 0
        
        for name in DatasetManager.list_datasets():
            info = DatasetManager.get_dataset_info(name)
            memory_mb = info["memory_usage_mb"]
            total_memory += memory_mb
            
            datasets.append({
                "name": name,
                "rows": info["shape"][0],
                "columns": info["shape"][1],
                "memory_mb": round(memory_mb, 1),
                "column_types": {
                    role: len([c for c, col_info in info["schema"]["columns"].items() 
                             if col_info["suggested_role"] == role])
                    for role in ["numerical", "categorical", "temporal", "identifier"]
                }
            })
        
        return {
            "datasets": datasets,
            "total_datasets": len(datasets),
            "total_memory_mb": round(total_memory, 1),
            "status": "loaded" if datasets else "empty"
        }
        
    except Exception as e:
        return {"error": f"Failed to list datasets: {str(e)}"}