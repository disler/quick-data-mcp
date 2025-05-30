"""Time series analysis tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig


async def time_series_analysis(
    dataset_name: str, 
    date_column: str, 
    value_column: str,
    frequency: str = "auto"
) -> dict:
    """Temporal analysis when dates are detected."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        if date_column not in df.columns:
            return {"error": f"Date column '{date_column}' not found"}
        if value_column not in df.columns:
            return {"error": f"Value column '{value_column}' not found"}
        
        # Ensure date column is datetime
        df_ts = df.copy()
        df_ts[date_column] = pd.to_datetime(df_ts[date_column])
        
        # Sort by date
        df_ts = df_ts.sort_values(date_column)
        
        # Basic time series statistics
        date_range = df_ts[date_column].max() - df_ts[date_column].min()
        
        # Group by date and aggregate value
        if frequency == "auto":
            # Determine frequency based on data span
            if date_range.days > 365:
                freq = "M"  # Monthly
            elif date_range.days > 31:
                freq = "W"  # Weekly
            else:
                freq = "D"  # Daily
        else:
            freq = frequency
        
        # Resample time series
        df_ts.set_index(date_column, inplace=True)
        ts_resampled = df_ts[value_column].resample(freq).mean()
        
        # Calculate trend (simple linear)
        x = np.arange(len(ts_resampled))
        y = ts_resampled.values
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate basic statistics
        result = {
            "dataset": dataset_name,
            "date_column": date_column,
            "value_column": value_column,
            "frequency": freq,
            "date_range": {
                "start": df_ts.index.min().isoformat(),
                "end": df_ts.index.max().isoformat(),
                "days": date_range.days
            },
            "trend": {
                "slope": round(slope, 4),
                "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
            },
            "statistics": {
                "mean": round(ts_resampled.mean(), 3),
                "std": round(ts_resampled.std(), 3),
                "min": round(ts_resampled.min(), 3),
                "max": round(ts_resampled.max(), 3)
            },
            "data_points": len(ts_resampled),
            "sample_values": ts_resampled.head(10).to_dict()
        }
        
        return result
        
    except Exception as e:
        return {"error": f"Time series analysis failed: {str(e)}"}