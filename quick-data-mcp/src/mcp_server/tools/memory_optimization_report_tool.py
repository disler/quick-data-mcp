"""Memory optimization report tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas


async def memory_optimization_report(dataset_name: str) -> dict:
    """Analyze memory usage and suggest optimizations."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        # Current memory usage
        memory_usage = df.memory_usage(deep=True)
        total_memory = memory_usage.sum()
        
        # Analyze each column for optimization potential
        optimization_suggestions = []
        potential_savings = 0
        
        for col in df.columns:
            col_memory = memory_usage[col]
            col_type = str(df[col].dtype)
            
            suggestion = {
                "column": col,
                "current_memory_kb": round(col_memory / 1024, 2),
                "current_dtype": col_type,
                "suggestion": None,
                "potential_savings_kb": 0
            }
            
            # String optimization
            if col_type == 'object':
                if df[col].apply(lambda x: isinstance(x, str)).all():
                    # Check if can be categorical
                    unique_ratio = df[col].nunique() / len(df)
                    if unique_ratio < 0.5:
                        suggestion["suggestion"] = "Convert to categorical"
                        suggestion["potential_savings_kb"] = round(col_memory * 0.6 / 1024, 2)
                        potential_savings += col_memory * 0.6
            
            # Integer optimization
            elif 'int64' in col_type:
                col_min, col_max = df[col].min(), df[col].max()
                if col_min >= 0 and col_max <= 255:
                    suggestion["suggestion"] = "Convert to uint8"
                    suggestion["potential_savings_kb"] = round(col_memory * 0.875 / 1024, 2)
                    potential_savings += col_memory * 0.875
                elif col_min >= -128 and col_max <= 127:
                    suggestion["suggestion"] = "Convert to int8"
                    suggestion["potential_savings_kb"] = round(col_memory * 0.875 / 1024, 2)
                    potential_savings += col_memory * 0.875
                elif col_min >= -32768 and col_max <= 32767:
                    suggestion["suggestion"] = "Convert to int16"
                    suggestion["potential_savings_kb"] = round(col_memory * 0.75 / 1024, 2)
                    potential_savings += col_memory * 0.75
                elif col_min >= -2147483648 and col_max <= 2147483647:
                    suggestion["suggestion"] = "Convert to int32"
                    suggestion["potential_savings_kb"] = round(col_memory * 0.5 / 1024, 2)
                    potential_savings += col_memory * 0.5
            
            # Float optimization
            elif 'float64' in col_type:
                # Check if values fit in float32
                if df[col].between(-3.4e38, 3.4e38).all():
                    suggestion["suggestion"] = "Convert to float32"
                    suggestion["potential_savings_kb"] = round(col_memory * 0.5 / 1024, 2)
                    potential_savings += col_memory * 0.5
            
            if suggestion["suggestion"]:
                optimization_suggestions.append(suggestion)
        
        return {
            "dataset": dataset_name,
            "current_memory_usage": {
                "total_mb": round(total_memory / 1024**2, 2),
                "per_column_kb": {col: round(mem / 1024, 2) for col, mem in memory_usage.items()}
            },
            "optimization_suggestions": optimization_suggestions,
            "potential_savings": {
                "total_mb": round(potential_savings / 1024**2, 2),
                "percentage": round(potential_savings / total_memory * 100, 2)
            },
            "recommendations": [
                "Convert low-cardinality strings to categorical",
                "Use smaller integer types when possible",
                "Consider float32 for decimal numbers",
                "Remove unused columns before analysis"
            ]
        }
        
    except Exception as e:
        return {"error": f"Memory optimization analysis failed: {str(e)}"}