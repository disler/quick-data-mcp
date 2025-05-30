"""Memory usage resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional


async def get_memory_usage() -> dict:
    """Monitor memory usage of loaded datasets."""
    try:
        usage = []
        total_memory = 0
        
        for name in DatasetManager.list_datasets():
            info = DatasetManager.get_dataset_info(name)
            memory_mb = info["memory_usage_mb"]
            total_memory += memory_mb
            
            usage.append({
                "dataset": name,
                "memory_mb": round(memory_mb, 1),
                "rows": info["shape"][0],
                "columns": info["shape"][1],
                "memory_per_row_kb": round(memory_mb * 1024 / info["shape"][0], 2) if info["shape"][0] > 0 else 0
            })
        
        # Sort by memory usage
        usage.sort(key=lambda x: x["memory_mb"], reverse=True)
        
        return {
            "datasets": usage,
            "total_memory_mb": round(total_memory, 1),
            "dataset_count": len(usage),
            "memory_recommendations": [
                "Consider sampling large datasets before analysis",
                "Clear unused datasets with clear_dataset()",
                "Use memory_optimization_report() for optimization tips"
            ] if total_memory > 100 else ["Memory usage is optimal"]
        }
        
    except Exception as e:
        return {"error": f"Failed to get memory usage: {str(e)}"}