"""Analysis suggestion tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig


async def suggest_analysis(dataset_name: str) -> dict:
    """AI recommendations based on data characteristics."""
    try:
        if dataset_name not in dataset_schemas:
            return {"error": f"Dataset '{dataset_name}' not loaded"}
            
        schema = dataset_schemas[dataset_name]
        
        # Get columns by type
        numerical_cols = [name for name, info in schema.columns.items() 
                         if info.suggested_role == 'numerical']
        categorical_cols = [name for name, info in schema.columns.items() 
                           if info.suggested_role == 'categorical']
        temporal_cols = [name for name, info in schema.columns.items() 
                        if info.suggested_role == 'temporal']
        
        suggestions = []
        
        # Numerical columns → correlation analysis
        if len(numerical_cols) >= 2:
            suggestions.append({
                "type": "correlation_analysis",
                "description": f"Find relationships between {len(numerical_cols)} numerical variables",
                "columns": numerical_cols,
                "tool": "find_correlations",
                "priority": "high",
                "command": f"find_correlations('{dataset_name}')"
            })
        
        # Categorical columns → segmentation
        if categorical_cols and numerical_cols:
            suggestions.append({
                "type": "segmentation",
                "description": f"Group data by {len(categorical_cols)} categorical variables",
                "columns": categorical_cols,
                "tool": "segment_by_column", 
                "priority": "high",
                "command": f"segment_by_column('{dataset_name}', '{categorical_cols[0]}')"
            })
        
        # Date columns → time series
        if temporal_cols and numerical_cols:
            suggestions.append({
                "type": "time_series",
                "description": f"Analyze trends over time using {len(temporal_cols)} date columns",
                "columns": temporal_cols,
                "tool": "time_series_analysis",
                "priority": "medium",
                "command": f"time_series_analysis('{dataset_name}', '{temporal_cols[0]}', '{numerical_cols[0]}')"
            })
        
        # Distribution analysis for interesting columns
        high_cardinality_cols = [name for name, info in schema.columns.items() 
                               if info.unique_values > 10 and info.suggested_role in ['numerical', 'categorical']]
        if high_cardinality_cols:
            suggestions.append({
                "type": "distribution_analysis",
                "description": "Analyze distributions of high-variance columns",
                "columns": high_cardinality_cols[:3],
                "tool": "analyze_distributions",
                "priority": "medium",
                "command": f"analyze_distributions('{dataset_name}', '{high_cardinality_cols[0]}')"
            })
        
        # Outlier detection for numerical columns
        if numerical_cols:
            suggestions.append({
                "type": "outlier_detection",
                "description": f"Find outliers in {len(numerical_cols)} numerical columns",
                "columns": numerical_cols,
                "tool": "detect_outliers",
                "priority": "medium",
                "command": f"detect_outliers('{dataset_name}')"
            })
        
        # Data quality checks
        high_null_cols = [name for name, info in schema.columns.items() 
                         if info.null_percentage > 10]
        if high_null_cols:
            suggestions.append({
                "type": "data_quality",
                "description": f"Review data quality - {len(high_null_cols)} columns have >10% missing values",
                "columns": high_null_cols,
                "tool": "validate_data_quality",
                "priority": "low",
                "command": f"validate_data_quality('{dataset_name}')"
            })
        
        return {
            "dataset_name": dataset_name,
            "suggestions": suggestions,
            "dataset_summary": {
                "numerical_columns": len(numerical_cols),
                "categorical_columns": len(categorical_cols),
                "temporal_columns": len(temporal_cols),
                "total_rows": schema.row_count
            }
        }
        
    except Exception as e:
        return {"error": f"Analysis suggestion failed: {str(e)}"}