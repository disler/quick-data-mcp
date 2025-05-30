"""Chart creation tool implementation."""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig


async def create_chart(
    dataset_name: str,
    chart_type: str,
    x_column: str,
    y_column: Optional[str] = None,
    groupby_column: Optional[str] = None,
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> dict:
    """Create generic charts that adapt to any dataset."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        # Validate columns exist
        required_cols = [x_column]
        if y_column:
            required_cols.append(y_column)
        if groupby_column:
            required_cols.append(groupby_column)
            
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return {"error": f"Columns not found: {missing_cols}"}
        
        # Generate title if not provided
        if title is None:
            title = f"{chart_type.title()} Chart: {x_column}"
            if y_column:
                title += f" vs {y_column}"
            if groupby_column:
                title += f" (grouped by {groupby_column})"
        
        # Create chart based on type
        fig = None
        chart_data = None
        
        if chart_type == "histogram":
            fig = px.histogram(df, x=x_column, color=groupby_column, title=title)
            chart_data = df[x_column].value_counts().head(20).to_dict()
            
        elif chart_type == "bar":
            if not y_column:
                # Count plot
                if groupby_column:
                    chart_data = df.groupby([x_column, groupby_column]).size().unstack(fill_value=0)
                    fig = px.bar(chart_data, title=title)
                else:
                    chart_data = df[x_column].value_counts().head(20)
                    fig = px.bar(x=chart_data.index, y=chart_data.values, title=title)
            else:
                # Aggregated bar chart
                if groupby_column:
                    agg_data = df.groupby([x_column, groupby_column])[y_column].mean().unstack(fill_value=0)
                    fig = px.bar(agg_data, title=title)
                    chart_data = agg_data.to_dict()
                else:
                    agg_data = df.groupby(x_column)[y_column].mean()
                    fig = px.bar(x=agg_data.index, y=agg_data.values, title=title, 
                                labels={'x': x_column, 'y': f'Mean {y_column}'})
                    chart_data = agg_data.to_dict()
                    
        elif chart_type == "scatter":
            if not y_column:
                return {"error": "Scatter plot requires both x_column and y_column"}
            fig = px.scatter(df, x=x_column, y=y_column, color=groupby_column, title=title)
            chart_data = {"x_mean": df[x_column].mean(), "y_mean": df[y_column].mean()}
            
        elif chart_type == "line":
            if not y_column:
                return {"error": "Line plot requires both x_column and y_column"}
            
            # Sort by x_column for proper line plotting
            df_sorted = df.sort_values(x_column)
            
            if groupby_column:
                fig = px.line(df_sorted, x=x_column, y=y_column, color=groupby_column, title=title)
            else:
                # Group by x_column and aggregate y_column
                line_data = df_sorted.groupby(x_column)[y_column].mean().reset_index()
                fig = px.line(line_data, x=x_column, y=y_column, title=title)
                
            chart_data = {"trend": "line_chart_generated"}
            
        elif chart_type == "box":
            if not y_column:
                fig = px.box(df, x=x_column, title=title)
            else:
                fig = px.box(df, x=x_column, y=y_column, title=title)
            chart_data = {"quartiles": "box_plot_generated"}
            
        else:
            return {"error": f"Unsupported chart type: {chart_type}. Supported: histogram, bar, scatter, line, box"}
        
        # Save chart if path provided
        chart_file = None
        if save_path or fig:
            if save_path is None:
                # Create outputs/charts directory if it doesn't exist
                outputs_dir = Path("outputs/charts")
                outputs_dir.mkdir(parents=True, exist_ok=True)
                save_path = outputs_dir / f"chart_{dataset_name}_{chart_type}_{x_column}.html"
            
            chart_file = str(Path(save_path).with_suffix('.html'))
            fig.write_html(chart_file)
        
        return {
            "dataset": dataset_name,
            "chart_type": chart_type,
            "chart_config": {
                "x_column": x_column,
                "y_column": y_column,
                "groupby_column": groupby_column,
                "title": title
            },
            "chart_data_sample": chart_data,
            "chart_file": chart_file,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": f"Chart creation failed: {str(e)}"}