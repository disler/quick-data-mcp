"""Distribution analysis tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig


async def analyze_distributions(dataset_name: str, column_name: str) -> dict:
    """Analyze distribution of any column."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        if column_name not in df.columns:
            return {"error": f"Column '{column_name}' not found in dataset"}
        
        series = df[column_name]
        
        result = {
            "dataset": dataset_name,
            "column": column_name,
            "dtype": str(series.dtype),
            "total_values": len(series),
            "unique_values": series.nunique(),
            "null_values": series.isnull().sum(),
            "null_percentage": round(series.isnull().mean() * 100, 2)
        }
        
        if pd.api.types.is_numeric_dtype(series):
            # Numerical distribution
            result.update({
                "distribution_type": "numerical",
                "mean": round(series.mean(), 3),
                "median": round(series.median(), 3),
                "std": round(series.std(), 3),
                "min": series.min(),
                "max": series.max(),
                "quartiles": {
                    "q25": round(series.quantile(0.25), 3),
                    "q50": round(series.quantile(0.50), 3),
                    "q75": round(series.quantile(0.75), 3)
                },
                "skewness": round(series.skew(), 3),
                "kurtosis": round(series.kurtosis(), 3)
            })
        else:
            # Categorical distribution
            value_counts = series.value_counts().head(10)
            result.update({
                "distribution_type": "categorical",
                "most_frequent": value_counts.index[0] if len(value_counts) > 0 else None,
                "frequency_of_most_common": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                "top_10_values": value_counts.to_dict()
            })
        
        return result
        
    except Exception as e:
        return {"error": f"Distribution analysis failed: {str(e)}"}