"""Main MCP server implementation with analytics tools, resources, and prompts."""

from mcp.server import FastMCP
from .config.settings import settings
from .models.schemas import ChartConfig
from . import tools
from .resources import data_resources
from .prompts import (
    dataset_first_look, segmentation_workshop, data_quality_assessment, correlation_investigation,
    pattern_discovery_session, insight_generation_workshop, dashboard_design_consultation, find_datasources, list_mcp_assets
)
from typing import List, Optional, Dict, Any


# Create the FastMCP server instance
mcp = FastMCP(
    name=settings.server_name,
    version=settings.version,
    dependencies=["pydantic>=2.0.0", "pandas>=2.2.3", "plotly>=6.1.2"]
)


# ============================================================================
# ANALYTICS TOOLS - Pandas-powered data analysis functions
# ============================================================================

@mcp.tool()
async def load_dataset(file_path: str, dataset_name: str, sample_size: Optional[int] = None) -> dict:
    """Load any JSON/CSV dataset into memory with automatic schema discovery."""
    return await tools.load_dataset(file_path, dataset_name, sample_size)


@mcp.tool()
async def list_loaded_datasets() -> dict:
    """Show all datasets currently in memory."""
    return await tools.list_loaded_datasets()


@mcp.tool()
async def segment_by_column(
    dataset_name: str, 
    column_name: str, 
    method: str = "auto",
    top_n: int = 10
) -> dict:
    """Generic segmentation that works on any categorical column."""
    return await tools.segment_by_column(dataset_name, column_name, method, top_n)


@mcp.tool()
async def find_correlations(
    dataset_name: str, 
    columns: Optional[List[str]] = None,
    threshold: float = 0.3
) -> dict:
    """Find correlations between numerical columns."""
    return await tools.find_correlations(dataset_name, columns, threshold)


@mcp.tool()
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
    return await tools.create_chart(
        dataset_name, chart_type, x_column, y_column, groupby_column, title, save_path
    )


@mcp.tool()
async def analyze_distributions(dataset_name: str, column_name: str) -> dict:
    """Analyze distribution of any column."""
    return await tools.analyze_distributions(dataset_name, column_name)


@mcp.tool()
async def detect_outliers(
    dataset_name: str, 
    columns: Optional[List[str]] = None,
    method: str = "iqr"
) -> dict:
    """Detect outliers using configurable methods."""
    return await tools.detect_outliers(dataset_name, columns, method)


@mcp.tool()
async def time_series_analysis(
    dataset_name: str, 
    date_column: str, 
    value_column: str,
    frequency: str = "auto"
) -> dict:
    """Temporal analysis when dates are detected."""
    return await tools.time_series_analysis(dataset_name, date_column, value_column, frequency)


@mcp.tool()
async def suggest_analysis(dataset_name: str) -> dict:
    """AI recommendations based on data characteristics."""
    return await tools.suggest_analysis(dataset_name)


# ============================================================================
# ADVANCED ANALYTICS TOOLS - Data quality and advanced operations
# ============================================================================

@mcp.tool()
async def validate_data_quality(dataset_name: str) -> dict:
    """Comprehensive data quality assessment."""
    return await tools.validate_data_quality(dataset_name)


@mcp.tool()
async def compare_datasets(dataset_a: str, dataset_b: str, common_columns: Optional[List[str]] = None) -> dict:
    """Compare multiple datasets."""
    return await tools.compare_datasets(dataset_a, dataset_b, common_columns)


@mcp.tool()
async def merge_datasets(
    dataset_configs: List[Dict[str, Any]], 
    join_strategy: str = "inner"
) -> dict:
    """Join datasets on common keys."""
    return await tools.merge_datasets(dataset_configs, join_strategy)


@mcp.tool()
async def generate_dashboard(dataset_name: str, chart_configs: List[Dict[str, Any]]) -> dict:
    """Generate multi-chart dashboards from any data."""
    return await tools.generate_dashboard(dataset_name, chart_configs)


@mcp.tool()
async def export_insights(dataset_name: str, format: str = "json", include_charts: bool = False) -> dict:
    """Export analysis in multiple formats."""
    return await tools.export_insights(dataset_name, format, include_charts)


@mcp.tool()
async def calculate_feature_importance(
    dataset_name: str, 
    target_column: str, 
    feature_columns: Optional[List[str]] = None
) -> dict:
    """Calculate feature importance for predictive modeling."""
    return await tools.calculate_feature_importance(dataset_name, target_column, feature_columns)


@mcp.tool()
async def memory_optimization_report(dataset_name: str) -> dict:
    """Analyze memory usage and suggest optimizations."""
    return await tools.memory_optimization_report(dataset_name)


@mcp.tool()
async def execute_custom_analytics_code(dataset_name: str, python_code: str) -> str:
    """
    Execute custom Python code against a loaded dataset and return the output.
    
    IMPORTANT FOR AGENTS:
    - The dataset will be available as 'df' (pandas DataFrame) in your code
    - Libraries pre-imported: pandas as pd, numpy as np, plotly.express as px
    - To see results, you MUST print() them - only stdout output is returned
    - Any errors will be captured and returned so you can fix your code
    - Code runs in isolated subprocess with 30 second timeout
    
    USAGE EXAMPLES:
    
    Basic analysis:
    ```python
    print("Dataset shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("Summary stats:")
    print(df.describe())
    ```
    
    Custom calculations:
    ```python
    # Calculate customer metrics
    customer_stats = df.groupby('customer_id').agg({
        'order_value': ['sum', 'mean', 'count']
    }).round(2)
    print("Top 5 customers by total value:")
    print(customer_stats.sort_values(('order_value', 'sum'), ascending=False).head())
    ```
    
    Data analysis:
    ```python
    # Find correlations
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = df[numeric_cols].corr()
    print("Correlation matrix:")
    print(correlations)
    
    # Custom insights
    if 'sales' in df.columns and 'date' in df.columns:
        monthly_sales = df.groupby(pd.to_datetime(df['date']).dt.to_period('M'))['sales'].sum()
        print("Monthly sales trend:")
        print(monthly_sales)
    ```
    
    Args:
        dataset_name: Name of the loaded dataset to analyze
        python_code: Python code to execute (must print() results to see output)
        
    Returns:
        str: Combined stdout and stderr output from code execution
    """
    return await tools.execute_custom_analytics_code(dataset_name, python_code)


# ============================================================================
# DATASET MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
async def clear_dataset(dataset_name: str) -> dict:
    """Remove dataset from memory."""
    from .models.schemas import DatasetManager
    return DatasetManager.clear_dataset(dataset_name)


@mcp.tool()
async def clear_all_datasets() -> dict:
    """Clear all datasets from memory."""
    from .models.schemas import DatasetManager
    return DatasetManager.clear_all_datasets()


@mcp.tool()
async def get_dataset_info(dataset_name: str) -> dict:
    """Get basic info about loaded dataset."""
    from .models.schemas import DatasetManager
    try:
        return DatasetManager.get_dataset_info(dataset_name)
    except ValueError as e:
        return {"error": str(e)}


# ============================================================================
# ANALYTICS RESOURCES - Dynamic data context
# ============================================================================

@mcp.resource("datasets://loaded")
async def get_loaded_datasets_resource() -> dict:
    """List of all currently loaded datasets with basic info."""
    return await data_resources.get_loaded_datasets()


@mcp.resource("datasets://{dataset_name}/schema")
async def get_dataset_schema(dataset_name: str) -> dict:
    """Dynamic schema for any loaded dataset."""
    return await data_resources.get_dataset_schema(dataset_name)


@mcp.resource("datasets://{dataset_name}/summary")
async def get_dataset_summary(dataset_name: str) -> dict:
    """Statistical summary (pandas.describe() equivalent)."""
    return await data_resources.get_dataset_summary(dataset_name)


@mcp.resource("datasets://{dataset_name}/sample")
async def get_dataset_sample(dataset_name: str) -> dict:
    """Sample rows for data preview."""
    return await data_resources.get_dataset_sample(dataset_name, 5)


@mcp.resource("analytics://current_dataset")
async def get_current_dataset() -> dict:
    """Currently active dataset name and basic stats."""
    return await data_resources.get_current_dataset()


@mcp.resource("analytics://available_analyses")
async def get_available_analyses() -> dict:
    """List of applicable analysis types for current data."""
    return await data_resources.get_available_analyses(None)


@mcp.resource("analytics://column_types")
async def get_column_types() -> dict:
    """Column classification (categorical, numerical, temporal, text)."""
    return await data_resources.get_column_types(None)


@mcp.resource("analytics://suggested_insights")
async def get_analysis_suggestions() -> dict:
    """AI-generated analysis recommendations."""
    return await data_resources.get_analysis_suggestions(None)


@mcp.resource("analytics://memory_usage")
async def get_memory_usage() -> dict:
    """Monitor memory usage of loaded datasets."""
    return await data_resources.get_memory_usage()


# ============================================================================
# ANALYTICS PROMPTS - Adaptive conversation starters
# ============================================================================

@mcp.prompt()
async def dataset_first_look_prompt(dataset_name: str) -> str:
    """Guide initial exploration of any new dataset."""
    return await dataset_first_look(dataset_name)


@mcp.prompt()
async def segmentation_workshop_prompt(dataset_name: str) -> str:
    """Plan segmentation strategy based on available columns."""
    return await segmentation_workshop(dataset_name)


@mcp.prompt()
async def data_quality_assessment_prompt(dataset_name: str) -> str:
    """Systematic data quality assessment."""
    return await data_quality_assessment(dataset_name)


@mcp.prompt()
async def correlation_investigation_prompt(dataset_name: str) -> str:
    """Guide correlation analysis workflow."""
    return await correlation_investigation(dataset_name)


@mcp.prompt()
async def pattern_discovery_session_prompt(dataset_name: str) -> str:
    """Open-ended pattern mining conversation."""
    return await pattern_discovery_session(dataset_name)


@mcp.prompt()
async def insight_generation_workshop_prompt(dataset_name: str, business_context: str = "general") -> str:
    """Generate business insights."""
    return await insight_generation_workshop(dataset_name, business_context)


@mcp.prompt()
async def dashboard_design_consultation_prompt(dataset_name: str, audience: str = "general") -> str:
    """Plan dashboards for specific audiences."""
    return await dashboard_design_consultation(dataset_name, audience)


@mcp.prompt()
async def find_datasources_prompt(directory_path: str = ".") -> str:
    """Discover available data files (.csv, .json) in the current directory and present them as load options."""
    return await find_datasources(directory_path)


@mcp.prompt()
async def list_mcp_assets_prompt() -> str:
    """List all available MCP server capabilities including prompts, tools, and resources."""
    return await list_mcp_assets()


# ============================================================================
# LEGACY RESOURCES - Kept for backward compatibility
# ============================================================================

@mcp.resource("config://server")
async def get_server_config() -> dict:
    """Get server configuration information."""
    return await data_resources.get_server_config()


@mcp.resource("users://{user_id}/profile")
async def get_user_profile(user_id: str) -> dict:
    """Get user profile information by ID."""
    return await data_resources.get_user_profile(user_id)


@mcp.resource("system://status")
async def get_system_status() -> dict:
    """Get system status and health information."""
    return await data_resources.get_system_status()


# ============================================================================
# RESOURCE MIRROR TOOLS - Tool versions of resources for tool-only MCP clients
# ============================================================================

@mcp.tool()
async def resource_datasets_loaded() -> dict:
    """Tool mirror of datasets://loaded resource."""
    return await data_resources.get_loaded_datasets()


@mcp.tool()
async def resource_datasets_schema(dataset_name: str) -> dict:
    """Tool mirror of datasets://{name}/schema resource."""
    return await data_resources.get_dataset_schema(dataset_name)


@mcp.tool()
async def resource_datasets_summary(dataset_name: str) -> dict:
    """Tool mirror of datasets://{name}/summary resource."""
    return await data_resources.get_dataset_summary(dataset_name)


@mcp.tool()
async def resource_datasets_sample(dataset_name: str) -> dict:
    """Tool mirror of datasets://{name}/sample resource."""
    return await data_resources.get_dataset_sample(dataset_name, 5)


@mcp.tool()
async def resource_analytics_current_dataset() -> dict:
    """Tool mirror of analytics://current_dataset resource."""
    return await data_resources.get_current_dataset()


@mcp.tool()
async def resource_analytics_available_analyses() -> dict:
    """Tool mirror of analytics://available_analyses resource."""
    return await data_resources.get_available_analyses(None)


@mcp.tool()
async def resource_analytics_column_types() -> dict:
    """Tool mirror of analytics://column_types resource."""
    return await data_resources.get_column_types(None)


@mcp.tool()
async def resource_analytics_suggested_insights() -> dict:
    """Tool mirror of analytics://suggested_insights resource."""
    return await data_resources.get_analysis_suggestions(None)


@mcp.tool()
async def resource_analytics_memory_usage() -> dict:
    """Tool mirror of analytics://memory_usage resource."""
    return await data_resources.get_memory_usage()


@mcp.tool()
async def resource_config_server() -> dict:
    """Tool mirror of config://server resource."""
    return await data_resources.get_server_config()


@mcp.tool()
async def resource_users_profile(user_id: str) -> dict:
    """Tool mirror of users://{user_id}/profile resource."""
    return await data_resources.get_user_profile(user_id)


@mcp.tool()
async def resource_system_status() -> dict:
    """Tool mirror of system://status resource."""
    return await data_resources.get_system_status()




def get_server():
    """Get the MCP server instance."""
    return mcp


if __name__ == "__main__":
    mcp.run()