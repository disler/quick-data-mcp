"""Outlier detection tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig


async def detect_outliers(
    dataset_name: str, 
    columns: Optional[List[str]] = None,
    method: str = "iqr"
) -> dict:
    """Detect outliers using configurable methods."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        # Auto-select numerical columns if none specified
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not columns:
            return {"error": "No numerical columns found for outlier detection"}
        
        # Filter to existing columns
        existing_columns = [col for col in columns if col in df.columns]
        
        outliers_info = {}
        total_outliers = 0
        
        for col in existing_columns:
            series = df[col].dropna()
            
            if method == "iqr":
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
                
            elif method == "zscore":
                z_scores = np.abs((series - series.mean()) / series.std())
                outlier_indices = z_scores > 3
                outliers = series[outlier_indices]
                lower_bound = series.mean() - 3 * series.std()
                upper_bound = series.mean() + 3 * series.std()
                
            else:
                return {"error": f"Unsupported method: {method}. Use 'iqr' or 'zscore'"}
            
            outlier_count = len(outliers)
            total_outliers += outlier_count
            
            outliers_info[col] = {
                "outlier_count": outlier_count,
                "outlier_percentage": round(outlier_count / len(series) * 100, 2),
                "lower_bound": round(lower_bound, 3),
                "upper_bound": round(upper_bound, 3),
                "outlier_values": outliers.head(10).tolist(),
                "method": method
            }
        
        return {
            "dataset": dataset_name,
            "method": method,
            "columns_analyzed": existing_columns,
            "total_outliers": total_outliers,
            "outliers_by_column": outliers_info
        }
        
    except Exception as e:
        return {"error": f"Outlier detection failed: {str(e)}"}