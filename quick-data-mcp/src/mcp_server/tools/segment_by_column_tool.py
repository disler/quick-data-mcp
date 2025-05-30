"""Segmentation by column tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig


async def segment_by_column(
    dataset_name: str, 
    column_name: str, 
    method: str = "auto",
    top_n: int = 10
) -> dict:
    """Generic segmentation that works on any categorical column."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        if column_name not in df.columns:
            return {"error": f"Column '{column_name}' not found in dataset '{dataset_name}'"}
        
        # Auto-select aggregation based on available numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove the groupby column from numerical columns if it's there
        if column_name in numerical_cols:
            numerical_cols.remove(column_name)
        
        if not numerical_cols:
            # No numerical columns - just count
            segments = df.groupby(column_name).size().to_frame('count')
            segments = segments.sort_values('count', ascending=False).head(top_n)
        else:
            # Aggregate numerical columns
            agg_dict = {}
            for col in numerical_cols:
                agg_dict[col] = ['count', 'mean', 'sum', 'std']
            
            segments = df.groupby(column_name).agg(agg_dict)
            # Flatten column names
            segments.columns = ['_'.join(col).strip() for col in segments.columns]
            segments = segments.head(top_n)
        
        # Calculate percentages
        total_rows = len(df)
        if 'count' in segments.columns:
            segments['percentage'] = (segments['count'] / total_rows * 100).round(2)
        else:
            # Calculate counts for percentage
            counts = df.groupby(column_name).size()
            segments['count'] = counts
            segments['percentage'] = (counts / total_rows * 100).round(2)
        
        return {
            "dataset": dataset_name,
            "segmented_by": column_name,
            "segment_count": len(segments),
            "segments": segments.to_dict(),
            "total_rows": total_rows,
            "numerical_columns_analyzed": numerical_cols
        }
        
    except Exception as e:
        return {"error": f"Segmentation failed: {str(e)}"}