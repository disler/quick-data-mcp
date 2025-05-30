"""Correlation finding tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig


async def find_correlations(
    dataset_name: str, 
    columns: Optional[List[str]] = None,
    threshold: float = 0.3
) -> dict:
    """Find correlations between numerical columns."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        # Auto-select numerical columns if none specified
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(columns) < 2:
            return {"error": "Need at least 2 numerical columns for correlation analysis"}
        
        # Filter to only existing columns
        existing_columns = [col for col in columns if col in df.columns]
        if len(existing_columns) < 2:
            return {"error": f"Only {len(existing_columns)} of specified columns exist in dataset"}
        
        # Calculate correlation matrix
        corr_matrix = df[existing_columns].corr()
        
        # Find strongest correlations (excluding self-correlations)
        strong_correlations = []
        for i in range(len(existing_columns)):
            for j in range(i+1, len(existing_columns)):
                corr_value = corr_matrix.iloc[i, j]
                if not pd.isna(corr_value) and abs(corr_value) > threshold:
                    strength = "strong" if abs(corr_value) > 0.7 else "moderate"
                    direction = "positive" if corr_value > 0 else "negative"
                    
                    strong_correlations.append({
                        "column_1": existing_columns[i],
                        "column_2": existing_columns[j],
                        "correlation": round(corr_value, 3),
                        "strength": strength,
                        "direction": direction
                    })
        
        # Sort by absolute correlation value
        strong_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        return {
            "dataset": dataset_name,
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "columns_analyzed": existing_columns,
            "threshold": threshold
        }
        
    except Exception as e:
        return {"error": f"Correlation analysis failed: {str(e)}"}