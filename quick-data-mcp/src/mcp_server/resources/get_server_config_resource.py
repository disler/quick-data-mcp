"""Server configuration resource implementation."""

from ..config.settings import settings
from typing import Dict, Any, Optional


async def get_server_config() -> dict:
    """Get server configuration."""
    config = settings.server_info.copy()
    config.update({
        "analytics_features": [
            "dataset_loading",
            "schema_discovery",
            "correlation_analysis",
            "segmentation",
            "data_quality_assessment",
            "visualization",
            "outlier_detection",
            "time_series_analysis"
        ],
        "supported_formats": ["CSV", "JSON"],
        "memory_storage": "in_memory_dataframes"
    })
    return config