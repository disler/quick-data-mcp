"""Analytics-focused data resources implementation."""

from ..models.schemas import (
    UserProfile, DatasetManager, loaded_datasets, dataset_schemas
)
from ..config.settings import settings
from typing import Dict, Any, Optional


async def get_server_config() -> dict:
    """Get server configuration."""
    config = settings.server_info.copy()
    config.update({
        "analytics_features": [
            "dataset_loading",
            "schema_discovery",
            "correlation_analysis",
            "segmentation",
            "data_quality_assessment",
            "visualization",
            "outlier_detection",
            "time_series_analysis"
        ],
        "supported_formats": ["CSV", "JSON"],
        "memory_storage": "in_memory_dataframes"
    })
    return config


async def get_loaded_datasets() -> dict:
    """List all datasets currently in memory."""
    try:
        datasets = []
        total_memory = 0
        
        for name in DatasetManager.list_datasets():
            info = DatasetManager.get_dataset_info(name)
            memory_mb = info["memory_usage_mb"]
            total_memory += memory_mb
            
            datasets.append({
                "name": name,
                "rows": info["shape"][0],
                "columns": info["shape"][1],
                "memory_mb": round(memory_mb, 1),
                "column_types": {
                    role: len([c for c, col_info in info["schema"]["columns"].items() 
                             if col_info["suggested_role"] == role])
                    for role in ["numerical", "categorical", "temporal", "identifier"]
                }
            })
        
        return {
            "datasets": datasets,
            "total_datasets": len(datasets),
            "total_memory_mb": round(total_memory, 1),
            "status": "loaded" if datasets else "empty"
        }
        
    except Exception as e:
        return {"error": f"Failed to list datasets: {str(e)}"}


async def get_dataset_schema(dataset_name: str) -> dict:
    """Get dynamic schema for any loaded dataset."""
    try:
        if dataset_name not in dataset_schemas:
            return {"error": f"Dataset '{dataset_name}' not loaded"}
        
        schema = dataset_schemas[dataset_name]
        
        # Organize columns by type
        columns_by_type = {
            "numerical": [],
            "categorical": [], 
            "temporal": [],
            "identifier": []
        }
        
        for col_name, col_info in schema.columns.items():
            columns_by_type[col_info.suggested_role].append({
                "name": col_name,
                "dtype": col_info.dtype,
                "unique_values": col_info.unique_values,
                "null_percentage": round(col_info.null_percentage, 1),
                "sample_values": col_info.sample_values
            })
        
        return {
            "dataset_name": dataset_name,
            "total_rows": schema.row_count,
            "total_columns": len(schema.columns),
            "columns_by_type": columns_by_type,
            "suggested_analyses": schema.suggested_analyses,
            "schema_generated": True
        }
        
    except Exception as e:
        return {"error": f"Failed to get schema: {str(e)}"}


async def get_dataset_summary(dataset_name: str) -> dict:
    """Statistical summary (pandas.describe() equivalent)."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        # Get basic info
        summary = {
            "dataset_name": dataset_name,
            "shape": df.shape,
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        }
        
        # Numerical summary
        numerical_cols = df.select_dtypes(include=['number']).columns
        if len(numerical_cols) > 0:
            summary["numerical_summary"] = df[numerical_cols].describe().to_dict()
        
        # Categorical summary
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            summary["categorical_summary"] = {}
            for col in categorical_cols:
                summary["categorical_summary"][col] = {
                    "unique_count": df[col].nunique(),
                    "top_values": df[col].value_counts().head(5).to_dict(),
                    "null_count": df[col].isnull().sum()
                }
        
        # Missing data summary
        missing_data = df.isnull().sum()
        summary["missing_data"] = {
            "total_missing": int(missing_data.sum()),
            "columns_with_missing": missing_data[missing_data > 0].to_dict()
        }
        
        return summary
        
    except Exception as e:
        return {"error": f"Failed to generate summary: {str(e)}"}


async def get_dataset_sample(dataset_name: str, n_rows: int = 5) -> dict:
    """Sample rows for data preview."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        # Get sample rows
        sample_df = df.head(n_rows)
        
        return {
            "dataset_name": dataset_name,
            "sample_size": len(sample_df),
            "total_rows": len(df),
            "columns": list(df.columns),
            "sample_data": sample_df.to_dict('records')
        }
        
    except Exception as e:
        return {"error": f"Failed to get sample: {str(e)}"}


async def get_current_dataset() -> dict:
    """Currently active dataset name and basic stats."""
    try:
        datasets = DatasetManager.list_datasets()
        
        if not datasets:
            return {
                "status": "no_datasets_loaded",
                "message": "No datasets currently loaded",
                "suggestion": "Use load_dataset() to load a dataset"
            }
        
        # Return info about the most recently loaded dataset
        latest_dataset = datasets[-1]  # Assuming last is most recent
        info = DatasetManager.get_dataset_info(latest_dataset)
        
        return {
            "current_dataset": latest_dataset,
            "shape": info["shape"],
            "memory_mb": round(info["memory_usage_mb"], 2),
            "all_loaded_datasets": datasets,
            "total_datasets": len(datasets)
        }
        
    except Exception as e:
        return {"error": f"Failed to get current dataset: {str(e)}"}


async def get_available_analyses(dataset_name: Optional[str] = None) -> dict:
    """List of applicable analysis types for current data."""
    try:
        if dataset_name is None:
            datasets = DatasetManager.list_datasets()
            if not datasets:
                return {"error": "No datasets loaded"}
            dataset_name = datasets[-1]  # Use most recent
        
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
        
        available_analyses = []
        
        # Basic analyses always available
        available_analyses.extend([
            {
                "type": "data_quality_assessment",
                "description": "Comprehensive data quality report",
                "requirements": "Any dataset",
                "tool": "validate_data_quality"
            },
            {
                "type": "distribution_analysis", 
                "description": "Analyze column distributions",
                "requirements": "Any columns",
                "tool": "analyze_distributions"
            }
        ])
        
        # Conditional analyses based on column types
        if len(numerical_cols) >= 2:
            available_analyses.append({
                "type": "correlation_analysis",
                "description": f"Find relationships between {len(numerical_cols)} numerical variables",
                "requirements": "2+ numerical columns",
                "tool": "find_correlations",
                "applicable_columns": numerical_cols
            })
            
            available_analyses.append({
                "type": "outlier_detection",
                "description": "Detect outliers in numerical data",
                "requirements": "Numerical columns",
                "tool": "detect_outliers",
                "applicable_columns": numerical_cols
            })
        
        if categorical_cols:
            available_analyses.append({
                "type": "segmentation",
                "description": f"Group data by {len(categorical_cols)} categorical variables",
                "requirements": "Categorical columns",
                "tool": "segment_by_column",
                "applicable_columns": categorical_cols
            })
        
        if temporal_cols and numerical_cols:
            available_analyses.append({
                "type": "time_series",
                "description": f"Analyze trends over time",
                "requirements": "Date + numerical columns",
                "tool": "time_series_analysis",
                "applicable_columns": {"date_columns": temporal_cols, "value_columns": numerical_cols}
            })
        
        if len(df := DatasetManager.get_dataset(dataset_name)) > 1:
            available_analyses.append({
                "type": "feature_importance",
                "description": "Calculate feature importance for prediction",
                "requirements": "Numerical target + feature columns",
                "tool": "calculate_feature_importance"
            })
        
        return {
            "dataset_name": dataset_name,
            "available_analyses": available_analyses,
            "dataset_summary": {
                "numerical_columns": len(numerical_cols),
                "categorical_columns": len(categorical_cols),
                "temporal_columns": len(temporal_cols),
                "total_rows": schema.row_count
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to get available analyses: {str(e)}"}


async def get_column_types(dataset_name: Optional[str] = None) -> dict:
    """Column classification (categorical, numerical, temporal, text)."""
    try:
        if dataset_name is None:
            datasets = DatasetManager.list_datasets()
            if not datasets:
                return {"error": "No datasets loaded"}
            dataset_name = datasets[-1]
        
        if dataset_name not in dataset_schemas:
            return {"error": f"Dataset '{dataset_name}' not loaded"}
        
        schema = dataset_schemas[dataset_name]
        
        column_classification = {}
        type_counts = {"numerical": 0, "categorical": 0, "temporal": 0, "identifier": 0}
        
        for col_name, col_info in schema.columns.items():
            column_classification[col_name] = {
                "suggested_role": col_info.suggested_role,
                "dtype": col_info.dtype,
                "unique_values": col_info.unique_values,
                "null_percentage": col_info.null_percentage,
                "sample_values": col_info.sample_values
            }
            type_counts[col_info.suggested_role] += 1
        
        return {
            "dataset_name": dataset_name,
            "column_classification": column_classification,
            "type_summary": type_counts,
            "total_columns": len(schema.columns)
        }
        
    except Exception as e:
        return {"error": f"Failed to get column types: {str(e)}"}


async def get_analysis_suggestions(dataset_name: Optional[str] = None) -> dict:
    """AI-generated analysis recommendations."""
    try:
        if dataset_name is None:
            datasets = DatasetManager.list_datasets()
            if not datasets:
                return {"error": "No datasets loaded"}
            dataset_name = datasets[-1]
        
        # Import here to avoid circular imports
        from ..tools.pandas_tools import suggest_analysis
        return await suggest_analysis(dataset_name)
        
    except Exception as e:
        return {"error": f"Failed to get suggestions: {str(e)}"}


async def get_memory_usage() -> dict:
    """Monitor memory usage of loaded datasets."""
    try:
        usage = []
        total_memory = 0
        
        for name in DatasetManager.list_datasets():
            info = DatasetManager.get_dataset_info(name)
            memory_mb = info["memory_usage_mb"]
            total_memory += memory_mb
            
            usage.append({
                "dataset": name,
                "memory_mb": round(memory_mb, 1),
                "rows": info["shape"][0],
                "columns": info["shape"][1],
                "memory_per_row_kb": round(memory_mb * 1024 / info["shape"][0], 2) if info["shape"][0] > 0 else 0
            })
        
        # Sort by memory usage
        usage.sort(key=lambda x: x["memory_mb"], reverse=True)
        
        return {
            "datasets": usage,
            "total_memory_mb": round(total_memory, 1),
            "dataset_count": len(usage),
            "memory_recommendations": [
                "Consider sampling large datasets before analysis",
                "Clear unused datasets with clear_dataset()",
                "Use memory_optimization_report() for optimization tips"
            ] if total_memory > 100 else ["Memory usage is optimal"]
        }
        
    except Exception as e:
        return {"error": f"Failed to get memory usage: {str(e)}"}


# Legacy functions - kept for backward compatibility
async def get_user_profile(user_id: str) -> dict:
    """Get user profile by ID."""
    # In production, this would fetch from a database
    profile = UserProfile(
        id=user_id,
        name=f"User {user_id}",
        email=f"user{user_id}@example.com",
        status="active",
        preferences={
            "theme": "dark",
            "notifications": True,
            "language": "en"
        }
    )
    
    return profile.model_dump()


async def get_system_status() -> dict:
    """Get system status information."""
    datasets = DatasetManager.list_datasets()
    total_memory = sum(DatasetManager.get_dataset_info(name)["memory_usage_mb"] for name in datasets)
    
    return {
        "status": "healthy",
        "uptime": "Active session",
        "version": settings.version,
        "features": [
            "dataset_loading",
            "schema_discovery", 
            "correlation_analysis",
            "segmentation",
            "data_quality_assessment",
            "visualization",
            "outlier_detection",
            "time_series_analysis"
        ],
        "datasets_loaded": len(datasets),
        "total_memory_mb": round(total_memory, 1),
        "dependencies": {
            "mcp": "1.9.2",
            "pandas": "2.2.3+",
            "plotly": "6.1.2+",
            "pydantic": "2.11.5"
        }
    }