"""List loaded datasets tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig


async def list_loaded_datasets() -> dict:
    """Show all datasets currently in memory."""
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
                "memory_mb": round(memory_mb, 1)
            })
        
        return {
            "loaded_datasets": datasets,
            "total_datasets": len(datasets),
            "total_memory_mb": round(total_memory, 1)
        }
        
    except Exception as e:
        return {"error": f"Failed to list datasets: {str(e)}"}