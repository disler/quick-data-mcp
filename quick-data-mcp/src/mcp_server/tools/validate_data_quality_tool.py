"""Data quality validation tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from ..models.schemas import DatasetManager, DataQualityReport, AnalysisResult, loaded_datasets, dataset_schemas


async def validate_data_quality(dataset_name: str) -> dict:
    """Comprehensive data quality assessment."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        schema = dataset_schemas[dataset_name]
        
        # Missing data analysis
        missing_data = {}
        for col in df.columns:
            null_pct = df[col].isnull().mean() * 100
            if null_pct > 0:
                missing_data[col] = round(null_pct, 2)
        
        # Duplicate rows
        duplicate_rows = df.duplicated().sum()
        
        # Potential issues detection
        issues = []
        recommendations = []
        
        # High missing data
        high_missing = [col for col, pct in missing_data.items() if pct > 50]
        if high_missing:
            issues.append(f"High missing data in columns: {', '.join(high_missing)}")
            recommendations.append("Consider dropping columns with >50% missing data or investigate data collection process")
        
        # Duplicate rows
        if duplicate_rows > 0:
            issues.append(f"{duplicate_rows} duplicate rows found")
            recommendations.append("Remove duplicate rows or investigate if duplicates are intentional")
        
        # Potential ID columns that aren't unique
        for col_name, col_info in schema.columns.items():
            if col_info.suggested_role == 'identifier' and col_info.unique_values < len(df):
                issues.append(f"Column '{col_name}' appears to be an ID but has duplicates")
                recommendations.append(f"Investigate duplicate values in '{col_name}' column")
        
        # Mixed data types in object columns
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            sample_types = set(type(x).__name__ for x in df[col].dropna().head(100))
            if len(sample_types) > 1:
                issues.append(f"Mixed data types in column '{col}': {sample_types}")
                recommendations.append(f"Standardize data types in column '{col}'")
        
        # Calculate quality score (0-100)
        score = 100
        score -= len(missing_data) * 5  # Penalize for missing data
        score -= (duplicate_rows / len(df)) * 20  # Penalize for duplicates
        score -= len([col for col, pct in missing_data.items() if pct > 10]) * 10  # High missing penalty
        score = max(0, score)
        
        if not issues:
            recommendations.append("Data quality looks good! Proceed with analysis.")
        
        quality_report = DataQualityReport(
            dataset_name=dataset_name,
            total_rows=len(df),
            total_columns=len(df.columns),
            missing_data=missing_data,
            duplicate_rows=duplicate_rows,
            potential_issues=issues,
            quality_score=round(score, 1),
            recommendations=recommendations
        )
        
        return quality_report.model_dump()
        
    except Exception as e:
        return {"error": f"Data quality validation failed: {str(e)}"}