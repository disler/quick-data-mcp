"""Insights export tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas


async def export_insights(dataset_name: str, format: str = "json", include_charts: bool = False) -> dict:
    """Export analysis in multiple formats."""
    try:
        if dataset_name not in loaded_datasets:
            return {"error": f"Dataset '{dataset_name}' not loaded"}
        
        df = DatasetManager.get_dataset(dataset_name)
        schema = dataset_schemas[dataset_name]
        
        # Generate comprehensive insights
        insights = {
            "dataset_name": dataset_name,
            "export_timestamp": datetime.now().isoformat(),
            "dataset_info": {
                "shape": df.shape,
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
                "columns": list(df.columns)
            },
            "schema_summary": {
                "numerical_columns": len([c for c, info in schema.columns.items() if info.suggested_role == 'numerical']),
                "categorical_columns": len([c for c, info in schema.columns.items() if info.suggested_role == 'categorical']),
                "temporal_columns": len([c for c, info in schema.columns.items() if info.suggested_role == 'temporal']),
                "identifier_columns": len([c for c, info in schema.columns.items() if info.suggested_role == 'identifier'])
            },
            "data_quality": {
                "missing_data_columns": len([c for c in df.columns if df[c].isnull().any()]),
                "duplicate_rows": df.duplicated().sum(),
                "total_missing_values": df.isnull().sum().sum()
            },
            "suggested_analyses": schema.suggested_analyses
        }
        
        # Add statistical summaries for numerical columns
        numerical_cols = [c for c, info in schema.columns.items() if info.suggested_role == 'numerical']
        if numerical_cols:
            insights["numerical_summary"] = df[numerical_cols].describe().to_dict()
        
        # Add value counts for categorical columns
        categorical_cols = [c for c, info in schema.columns.items() if info.suggested_role == 'categorical']
        if categorical_cols:
            insights["categorical_summary"] = {}
            for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
                insights["categorical_summary"][col] = df[col].value_counts().head(10).to_dict()
        
        # Export in requested format
        export_file = None
        
        if format.lower() == "json":
            import json
            # Create outputs/reports directory if it doesn't exist
            outputs_dir = Path("outputs/reports")
            outputs_dir.mkdir(parents=True, exist_ok=True)
            export_file = outputs_dir / f"insights_{dataset_name}.json"
            with open(export_file, 'w') as f:
                json.dump(insights, f, indent=2, default=str)
                
        elif format.lower() == "csv":
            # Create a summary CSV
            # Create outputs/reports directory if it doesn't exist
            outputs_dir = Path("outputs/reports")
            outputs_dir.mkdir(parents=True, exist_ok=True)
            export_file = outputs_dir / f"insights_{dataset_name}.csv"
            
            # Create summary rows
            summary_data = []
            summary_data.append(["Dataset Name", dataset_name])
            summary_data.append(["Export Date", insights["export_timestamp"]])
            summary_data.append(["Total Rows", df.shape[0]])
            summary_data.append(["Total Columns", df.shape[1]])
            summary_data.append(["Memory Usage (MB)", insights["dataset_info"]["memory_usage_mb"]])
            summary_data.append(["Numerical Columns", insights["schema_summary"]["numerical_columns"]])
            summary_data.append(["Categorical Columns", insights["schema_summary"]["categorical_columns"]])
            summary_data.append(["Missing Values", insights["data_quality"]["total_missing_values"]])
            summary_data.append(["Duplicate Rows", insights["data_quality"]["duplicate_rows"]])
            
            summary_df = pd.DataFrame(summary_data, columns=["Metric", "Value"])
            summary_df.to_csv(export_file, index=False)
            
        elif format.lower() == "html":
            # Create HTML report
            # Create outputs/reports directory if it doesn't exist
            outputs_dir = Path("outputs/reports")
            outputs_dir.mkdir(parents=True, exist_ok=True)
            export_file = outputs_dir / f"insights_{dataset_name}.html"
            
            html_content = f"""
            <html>
            <head><title>Data Insights: {dataset_name}</title></head>
            <body>
                <h1>Data Analysis Report: {dataset_name}</h1>
                <h2>Dataset Overview</h2>
                <ul>
                    <li>Rows: {df.shape[0]:,}</li>
                    <li>Columns: {df.shape[1]}</li>
                    <li>Memory Usage: {insights['dataset_info']['memory_usage_mb']} MB</li>
                </ul>
                
                <h2>Column Types</h2>
                <ul>
                    <li>Numerical: {insights['schema_summary']['numerical_columns']}</li>
                    <li>Categorical: {insights['schema_summary']['categorical_columns']}</li>
                    <li>Temporal: {insights['schema_summary']['temporal_columns']}</li>
                    <li>Identifier: {insights['schema_summary']['identifier_columns']}</li>
                </ul>
                
                <h2>Data Quality</h2>
                <ul>
                    <li>Missing Values: {insights['data_quality']['total_missing_values']}</li>
                    <li>Duplicate Rows: {insights['data_quality']['duplicate_rows']}</li>
                </ul>
                
                <h2>Suggested Analyses</h2>
                <ul>
                    {''.join([f'<li>{analysis}</li>' for analysis in schema.suggested_analyses])}
                </ul>
            </body>
            </html>
            """
            
            with open(export_file, 'w') as f:
                f.write(html_content)
        else:
            return {"error": f"Unsupported export format: {format}. Use 'json', 'csv', or 'html'"}
        
        return {
            "dataset": dataset_name,
            "export_format": format,
            "export_file": export_file,
            "insights_summary": {
                "total_metrics": len(insights),
                "has_numerical_summary": "numerical_summary" in insights,
                "has_categorical_summary": "categorical_summary" in insights
            },
            "status": "success"
        }
        
    except Exception as e:
        return {"error": f"Export failed: {str(e)}"}