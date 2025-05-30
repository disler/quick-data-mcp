"""System status resource implementation (legacy)."""

from ..models.schemas import DatasetManager
from ..config.settings import settings
from typing import Dict, Any, Optional


async def get_system_status() -> dict:
    """Get system status information."""
    datasets = DatasetManager.list_datasets()
    total_memory = sum(DatasetManager.get_dataset_info(name)["memory_usage_mb"] for name in datasets)
    
    return {
        "status": "healthy",
        "uptime": "Active session",
        "version": settings.version,
        "features": [
            "dataset_loading",
            "schema_discovery", 
            "correlation_analysis",
            "segmentation",
            "data_quality_assessment",
            "visualization",
            "outlier_detection",
            "time_series_analysis"
        ],
        "datasets_loaded": len(datasets),
        "total_memory_mb": round(total_memory, 1),
        "dependencies": {
            "mcp": "1.9.2",
            "pandas": "2.2.3+",
            "plotly": "6.1.2+",
            "pydantic": "2.11.5"
        }
    }