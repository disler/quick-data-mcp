# POC Initiative: Generic Data Analytics MCP Server

## Problem Statement

Teams have data in JSON/CSV files but lack an easy, AI-assisted way to explore, analyze, and generate insights from ANY dataset. Current solutions require custom coding for each data source, making analysis slow and inaccessible to non-technical users.

## Solution Vision

Build a **dataset-agnostic** MCP server that automatically adapts to any structured data (JSON/CSV), discovers schemas dynamically, and provides intelligent analytics capabilities. The AI can analyze customer data, sales records, survey responses, inventory data, or any business dataset through the same interface.

## Core Design Principles

### 1. Dataset Agnostic
- Works with any structured data without hardcoded schemas
- Automatically discovers column types, relationships, and constraints
- Adapts analysis techniques to data characteristics

### 2. Schema Discovery
- Dynamic column detection and type inference
- Automatic identification of categorical vs numerical vs temporal data
- Intelligent suggestions for analysis based on data patterns

### 3. Adaptive Analytics
- Generic segmentation that works on any categorical columns
- Correlation analysis that adapts to available numerical data
- Time series analysis when temporal columns are detected

### 4. Conversational Guidance
- AI prompts that guide users through data exploration
- Context-aware suggestions based on current dataset
- Interactive tutorials for complex analytics operations

## Test Data Flexibility

### Example Dataset A: E-commerce Orders
```json
[
  {
    "order_id": "ord_001",
    "customer_id": "cust_123", 
    "product_category": "electronics",
    "order_value": 299.99,
    "order_date": "2024-11-15",
    "region": "west_coast",
    "payment_method": "credit_card",
    "customer_segment": "premium"
  }
]
```

### Example Dataset B: Employee Survey
```csv
employee_id,department,satisfaction_score,tenure_years,remote_work,salary_band
emp_001,engineering,8.5,3.2,yes,senior
emp_002,sales,6.2,1.8,no,mid
emp_003,marketing,9.1,5.5,hybrid,senior
```

### Example Dataset C: Product Performance
```csv
product_id,category,monthly_sales,inventory_level,supplier,launch_date,rating
prod_001,widgets,1250,45,supplier_a,2024-01-15,4.2
prod_002,gadgets,890,12,supplier_b,2023-08-22,3.8
```

## Generic MCP Architecture

### Tools (Dataset-Agnostic Actions)

#### Data Discovery & Loading
- `load_dataset(file_path, format)` - Load any JSON/CSV with automatic schema detection
- `analyze_schema(dataset_name)` - Discover column types, distributions, missing values
- `suggest_analysis(dataset_name)` - AI recommendations based on data characteristics
- `validate_data_quality(dataset_name)` - Generic data quality assessment

#### Flexible Analytics
- `segment_by_column(dataset_name, column_name, method)` - Generic segmentation on any categorical column
- `find_correlations(dataset_name, columns)` - Correlation analysis on any numerical columns
- `analyze_distributions(dataset_name, column_name)` - Distribution analysis for any column
- `detect_outliers(dataset_name, columns)` - Outlier detection using configurable methods
- `time_series_analysis(dataset_name, date_column, value_column)` - Temporal analysis when dates detected

#### Adaptive Visualization
- `create_chart(dataset_name, chart_type, x_column, y_column, groupby)` - Generic chart creation
- `generate_dashboard(dataset_name, chart_configs)` - Multi-chart dashboards from any data
- `export_insights(dataset_name, format)` - Export analysis in multiple formats

#### Cross-Dataset Operations
- `compare_datasets(dataset_a, dataset_b, common_columns)` - Compare multiple datasets
- `merge_datasets(dataset_configs, join_strategy)` - Join datasets on common keys

### Resources (Dynamic Data Context)

#### Dataset Metadata
- `datasets://loaded` - List of all currently loaded datasets with basic info
- `datasets://{name}/schema` - Dynamic schema for any loaded dataset
- `datasets://{name}/summary` - Statistical summary (pandas.describe() equivalent)
- `datasets://{name}/sample` - Sample rows for data preview

#### Analysis Context
- `analytics://current_dataset` - Currently active dataset name and basic stats
- `analytics://available_analyses` - List of applicable analysis types for current data
- `analytics://column_types` - Column classification (categorical, numerical, temporal, text)
- `analytics://suggested_insights` - AI-generated analysis recommendations

#### Results & History
- `results://recent_analyses` - Recently performed analyses and their outputs
- `results://generated_charts` - Available visualizations with metadata
- `results://export_ready` - Datasets/analyses ready for export

### Prompts (Adaptive Conversation Starters)

#### Data Exploration
- `dataset_first_look(dataset_name)` - Guide initial exploration of any new dataset
- `column_deep_dive(dataset_name, column_name)` - Detailed analysis of specific columns
- `data_quality_review(dataset_name)` - Systematic data quality assessment

#### Analysis Strategy
- `segmentation_planning(dataset_name)` - Plan segmentation strategy based on available columns
- `correlation_investigation(dataset_name)` - Guide correlation analysis workflow
- `pattern_discovery_session(dataset_name)` - Open-ended pattern mining conversation

#### Business Intelligence
- `insight_generation_workshop(dataset_name, business_context)` - Generate business insights
- `dashboard_design_consultation(dataset_name, audience)` - Plan dashboards for specific audiences
- `export_strategy_planning(dataset_name, use_case)` - Plan data export and sharing strategy

## Implementation Architecture

### In-Memory Dataset Storage (Simple & Fast)

```python
# Global in-memory storage - simple and effective
loaded_datasets: Dict[str, pd.DataFrame] = {}
dataset_schemas: Dict[str, DatasetSchema] = {}

class DatasetManager:
    """Simple in-memory dataset management"""
    
    @staticmethod
    def load_dataset(file_path: str, dataset_name: str) -> dict:
        """Load dataset into memory with automatic schema discovery"""
        
        # Load based on file extension
        if file_path.endswith('.json'):
            df = pd.read_json(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        # Store in global memory
        loaded_datasets[dataset_name] = df
        
        # Discover and cache schema
        schema = DatasetSchema.from_dataframe(df, dataset_name)
        dataset_schemas[dataset_name] = schema
        
        return {
            "status": "loaded",
            "dataset_name": dataset_name,
            "rows": len(df),
            "columns": list(df.columns),
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB"
        }
    
    @staticmethod
    def get_dataset(dataset_name: str) -> pd.DataFrame:
        """Retrieve dataset from memory"""
        if dataset_name not in loaded_datasets:
            raise ValueError(f"Dataset '{dataset_name}' not loaded. Use load_dataset() first.")
        return loaded_datasets[dataset_name]
    
    @staticmethod
    def list_datasets() -> List[str]:
        """Get names of all loaded datasets"""
        return list(loaded_datasets.keys())
    
    @staticmethod
    def get_dataset_info(dataset_name: str) -> dict:
        """Get basic info about loaded dataset"""
        if dataset_name not in loaded_datasets:
            raise ValueError(f"Dataset '{dataset_name}' not loaded")
            
        df = loaded_datasets[dataset_name]
        schema = dataset_schemas[dataset_name]
        
        return {
            "name": dataset_name,
            "shape": df.shape,
            "columns": list(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "schema": schema.model_dump()
        }

class DatasetSchema:
    """Dynamically discovered dataset schema"""
    name: str
    columns: Dict[str, ColumnInfo]
    row_count: int
    suggested_analyses: List[str]
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, name: str) -> 'DatasetSchema':
        """Auto-discover schema from pandas DataFrame"""
        columns = {}
        for col in df.columns:
            columns[col] = ColumnInfo.from_series(df[col], col)
        
        # Generate analysis suggestions based on column types
        suggestions = []
        numerical_cols = [col for col, info in columns.items() if info.suggested_role == 'numerical']
        categorical_cols = [col for col, info in columns.items() if info.suggested_role == 'categorical']
        temporal_cols = [col for col, info in columns.items() if info.suggested_role == 'temporal']
        
        if len(numerical_cols) >= 2:
            suggestions.append("correlation_analysis")
        if categorical_cols:
            suggestions.append("segmentation_analysis")
        if temporal_cols:
            suggestions.append("time_series_analysis")
            
        return cls(
            name=name,
            columns=columns,
            row_count=len(df),
            suggested_analyses=suggestions
        )
    
class ColumnInfo:
    """Column metadata and characteristics"""
    name: str
    dtype: str
    unique_values: int
    null_percentage: float
    sample_values: List[Any]
    suggested_role: str  # 'categorical', 'numerical', 'temporal', 'identifier'
    
    @classmethod
    def from_series(cls, series: pd.Series, name: str) -> 'ColumnInfo':
        """Auto-discover column characteristics from pandas Series"""
        
        # Determine suggested role
        if pd.api.types.is_numeric_dtype(series):
            role = 'numerical'
        elif pd.api.types.is_datetime64_any_dtype(series):
            role = 'temporal'
        elif series.nunique() / len(series) < 0.5:  # High cardinality = categorical
            role = 'categorical'
        elif series.nunique() == len(series):  # Unique values = identifier
            role = 'identifier'
        else:
            role = 'categorical'
            
        return cls(
            name=name,
            dtype=str(series.dtype),
            unique_values=series.nunique(),
            null_percentage=series.isnull().mean() * 100,
            sample_values=series.dropna().head(3).tolist(),
            suggested_role=role
        )
```

### Storage Benefits

**✅ Zero Complexity**: No file management, caching, or persistence logic
**✅ Immediate Access**: Instant dataset operations without I/O overhead  
**✅ Perfect for Demos**: Load sample data and start analyzing immediately
**✅ Memory Efficient**: Pandas DataFrames are already optimized for memory usage
**✅ Session-Based**: Clean slate on each restart - perfect for experimentation

### Memory Considerations

**Typical Dataset Sizes**:
- 1K rows × 10 columns = ~1MB memory
- 10K rows × 20 columns = ~10MB memory  
- 100K rows × 50 columns = ~100MB memory

**Best Practices**:
- Sample large datasets before loading (`df.sample(10000)`)
- Provide memory usage feedback to users
- Clear datasets when no longer needed (`del loaded_datasets[name]`)

### Generic Tool Implementation Examples

```python
@mcp.tool()
async def load_dataset(file_path: str, dataset_name: str) -> dict:
    """Load any JSON/CSV dataset into memory"""
    return DatasetManager.load_dataset(file_path, dataset_name)

@mcp.tool()
async def list_loaded_datasets() -> dict:
    """Show all datasets currently in memory"""
    datasets = []
    for name in DatasetManager.list_datasets():
        info = DatasetManager.get_dataset_info(name)
        datasets.append(info)
    
    return {
        "loaded_datasets": datasets,
        "total_memory_mb": sum(d["memory_usage_mb"] for d in datasets)
    }

@mcp.tool()
async def segment_by_column(
    dataset_name: str, 
    column_name: str, 
    method: str = "auto"
) -> dict:
    """Generic segmentation that works on any categorical column"""
    df = DatasetManager.get_dataset(dataset_name)
    
    if column_name not in df.columns:
        return {"error": f"Column '{column_name}' not found in dataset '{dataset_name}'"}
    
    # Auto-select aggregation based on available numerical columns
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    agg_dict = {}
    for col in numerical_cols:
        if col != column_name:  # Don't aggregate the groupby column
            agg_dict[col] = ['count', 'mean', 'sum']
    
    if not agg_dict:
        # No numerical columns - just count
        segments = df.groupby(column_name).size().to_frame('count')
    else:
        segments = df.groupby(column_name).agg(agg_dict)
    
    return {
        "dataset": dataset_name,
        "segmented_by": column_name,
        "segment_count": len(segments),
        "segments": segments.to_dict(),
        "total_rows": len(df)
    }

@mcp.tool()
async def find_correlations(dataset_name: str, columns: List[str] = None) -> dict:
    """Find correlations between numerical columns"""
    df = DatasetManager.get_dataset(dataset_name)
    
    # Auto-select numerical columns if none specified
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(columns) < 2:
        return {"error": "Need at least 2 numerical columns for correlation analysis"}
    
    # Calculate correlation matrix
    corr_matrix = df[columns].corr()
    
    # Find strongest correlations (excluding self-correlations)
    strong_correlations = []
    for i in range(len(columns)):
        for j in range(i+1, len(columns)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) > 0.3:  # Threshold for "interesting" correlation
                strong_correlations.append({
                    "column_1": columns[i],
                    "column_2": columns[j],
                    "correlation": round(corr_value, 3),
                    "strength": "strong" if abs(corr_value) > 0.7 else "moderate"
                })
    
    return {
        "dataset": dataset_name,
        "correlation_matrix": corr_matrix.to_dict(),
        "strong_correlations": strong_correlations,
        "columns_analyzed": columns
    }

@mcp.tool()
async def create_chart(
    dataset_name: str,
    chart_type: str,
    x_column: str,
    y_column: str = None,
    groupby_column: str = None
) -> dict:
    """Create generic charts that adapt to any dataset"""
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
    
    # Generate chart based on type
    if chart_type == "bar":
        if groupby_column:
            chart_data = df.groupby([x_column, groupby_column])[y_column].mean().unstack()
        else:
            chart_data = df.groupby(x_column)[y_column].mean()
    elif chart_type == "histogram":
        chart_data = df[x_column].value_counts()
    else:
        return {"error": f"Unsupported chart type: {chart_type}"}
    
    # In a real implementation, this would generate plotly charts
    return {
        "dataset": dataset_name,
        "chart_type": chart_type,
        "chart_data": chart_data.to_dict(),
        "chart_config": {
            "x_column": x_column,
            "y_column": y_column,
            "groupby_column": groupby_column
        }
    }
```

### Adaptive Resource System
```python
@mcp.resource("datasets://loaded")
async def get_loaded_datasets() -> dict:
    """List all datasets currently in memory"""
    datasets = []
    for name in DatasetManager.list_datasets():
        info = DatasetManager.get_dataset_info(name)
        datasets.append({
            "name": name,
            "rows": info["shape"][0],
            "columns": info["shape"][1],
            "memory_mb": round(info["memory_usage_mb"], 1)
        })
    
    return {
        "datasets": datasets,
        "total_datasets": len(datasets),
        "total_memory_mb": sum(d["memory_mb"] for d in datasets)
    }

@mcp.resource("datasets://{dataset_name}/schema")
async def get_dataset_schema(dataset_name: str) -> dict:
    """Get dynamic schema for any loaded dataset"""
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
        "suggested_analyses": schema.suggested_analyses
    }

@mcp.resource("datasets://{dataset_name}/analysis_suggestions")
async def get_analysis_suggestions(dataset_name: str) -> dict:
    """AI-powered analysis recommendations based on dataset characteristics"""
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
            "priority": "high"
        })
    
    # Categorical columns → segmentation
    if categorical_cols and numerical_cols:
        suggestions.append({
            "type": "segmentation",
            "description": f"Group data by {len(categorical_cols)} categorical variables",
            "columns": categorical_cols,
            "tool": "segment_by_column", 
            "priority": "high"
        })
    
    # Date columns → time series
    if temporal_cols and numerical_cols:
        suggestions.append({
            "type": "time_series",
            "description": f"Analyze trends over time using {len(temporal_cols)} date columns",
            "columns": temporal_cols,
            "tool": "time_series_analysis",
            "priority": "medium"
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
            "priority": "medium"
        })
    
    return {
        "dataset_name": dataset_name,
        "suggestions": suggestions,
        "dataset_summary": {
            "numerical_columns": len(numerical_cols),
            "categorical_columns": len(categorical_cols),
            "temporal_columns": len(temporal_cols)
        }
    }

@mcp.resource("analytics://memory_usage")
async def get_memory_usage() -> dict:
    """Monitor memory usage of loaded datasets"""
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
            "columns": info["shape"][1]
        })
    
    # Sort by memory usage
    usage.sort(key=lambda x: x["memory_mb"], reverse=True)
    
    return {
        "datasets": usage,
        "total_memory_mb": round(total_memory, 1),
        "dataset_count": len(usage)
    }
```

### Intelligent Prompt System
```python
@mcp.prompt()
async def dataset_first_look(dataset_name: str) -> str:
    """Adaptive first-look analysis based on dataset characteristics"""
    if dataset_name not in dataset_schemas:
        return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
    
    schema = dataset_schemas[dataset_name]
    
    # Organize columns by type for display
    numerical_cols = [name for name, info in schema.columns.items() 
                     if info.suggested_role == 'numerical']
    categorical_cols = [name for name, info in schema.columns.items() 
                       if info.suggested_role == 'categorical']
    temporal_cols = [name for name, info in schema.columns.items() 
                    if info.suggested_role == 'temporal']
    
    prompt = f"""Let's explore your **{dataset_name}** dataset together! 

I can see you have **{schema.row_count:,} records** with **{len(schema.columns)} columns**:

"""
    
    if numerical_cols:
        prompt += f"**📊 Numerical columns** ({len(numerical_cols)}): {', '.join(numerical_cols)}\n"
        prompt += "→ Perfect for correlation analysis, statistical summaries, and trend analysis\n\n"
    
    if categorical_cols:
        prompt += f"**🏷️ Categorical columns** ({len(categorical_cols)}): {', '.join(categorical_cols)}\n"  
        prompt += "→ Great for segmentation, group comparisons, and distribution analysis\n\n"
    
    if temporal_cols:
        prompt += f"**📅 Date/Time columns** ({len(temporal_cols)}): {', '.join(temporal_cols)}\n"
        prompt += "→ Ideal for time series analysis and trend identification\n\n"
    
    # Add specific recommendations based on data
    prompt += "**🎯 Recommended starting points:**\n"
    
    if len(numerical_cols) >= 2:
        prompt += f"• **Correlation Analysis**: Explore relationships between {numerical_cols[0]} and {numerical_cols[1]}\n"
    
    if categorical_cols and numerical_cols:
        prompt += f"• **Segmentation**: Group by {categorical_cols[0]} to analyze {numerical_cols[0]} patterns\n"
    
    if temporal_cols and numerical_cols:
        prompt += f"• **Time Trends**: Track {numerical_cols[0]} changes over {temporal_cols[0]}\n"
    
    # Data quality insights
    high_null_cols = [name for name, info in schema.columns.items() 
                     if info.null_percentage > 10]
    if high_null_cols:
        prompt += f"• **Data Quality Review**: {len(high_null_cols)} columns have missing values to investigate\n"
    
    prompt += f"\n**Available tools**: `segment_by_column`, `find_correlations`, `create_chart`, `validate_data_quality`\n"
    prompt += f"\nWhat aspect of your {dataset_name} data would you like to explore first?"
    
    return prompt

@mcp.prompt()
async def segmentation_workshop(dataset_name: str) -> str:
    """Interactive segmentation guidance based on actual dataset"""
    if dataset_name not in dataset_schemas:
        return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
    
    schema = dataset_schemas[dataset_name]
    
    # Find categorical columns suitable for segmentation
    categorical_cols = [name for name, info in schema.columns.items() 
                       if info.suggested_role == 'categorical']
    numerical_cols = [name for name, info in schema.columns.items() 
                     if info.suggested_role == 'numerical']
    
    if not categorical_cols:
        return f"No categorical columns found in {dataset_name} for segmentation. Consider creating segments from numerical columns using ranges."
    
    prompt = f"""Let's create meaningful segments from your **{dataset_name}** data!

**Available categorical columns for grouping:**
"""
    
    for col in categorical_cols:
        col_info = schema.columns[col]
        prompt += f"• **{col}**: {col_info.unique_values} unique values (examples: {', '.join(map(str, col_info.sample_values))})\n"
    
    if numerical_cols:
        prompt += f"\n**Numerical columns to analyze by segment:**\n"
        for col in numerical_cols:
            col_info = schema.columns[col]
            prompt += f"• **{col}**: {col_info.dtype} (sample values: {', '.join(map(str, col_info.sample_values))})\n"
    
    prompt += f"""
**Segmentation strategies:**

1. **Simple segmentation**: Group by one categorical column
   Example: `segment_by_column('{dataset_name}', '{categorical_cols[0]}')`

2. **Cross-segmentation**: Combine multiple categories (manual analysis)
   Example: Group by {categorical_cols[0]}, then analyze patterns within each group

3. **Value-based segments**: Focus on high/low values of numerical columns
   Example: Top 20% vs bottom 20% by {numerical_cols[0] if numerical_cols else 'value'}

Which segmentation approach interests you most? I can guide you through the specific pandas operations."""
    
    return prompt

@mcp.prompt()
async def data_quality_assessment(dataset_name: str) -> str:
    """Guide systematic data quality review"""
    if dataset_name not in dataset_schemas:
        return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
    
    schema = dataset_schemas[dataset_name]
    df = DatasetManager.get_dataset(dataset_name)
    
    prompt = f"""Let's systematically review the quality of your **{dataset_name}** dataset.

**Dataset Overview:**
• **{schema.row_count:,} rows** × **{len(schema.columns)} columns**
• **Memory usage**: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB

**Data Quality Indicators:**
"""
    
    # Missing values analysis
    missing_data = []
    for col_name, col_info in schema.columns.items():
        if col_info.null_percentage > 0:
            missing_data.append((col_name, col_info.null_percentage))
    
    if missing_data:
        missing_data.sort(key=lambda x: x[1], reverse=True)
        prompt += f"\n**📋 Missing Values** ({len(missing_data)} columns affected):\n"
        for col, pct in missing_data[:5]:  # Show top 5
            prompt += f"• **{col}**: {pct:.1f}% missing\n"
        if len(missing_data) > 5:
            prompt += f"• ... and {len(missing_data) - 5} more columns\n"
    else:
        prompt += f"\n**✅ Missing Values**: No missing values detected!\n"
    
    # Duplicates check (simple heuristic)
    potential_id_cols = [name for name, info in schema.columns.items() 
                        if info.suggested_role == 'identifier']
    
    if potential_id_cols:
        prompt += f"\n**🔍 Potential Duplicates**: Check uniqueness of {', '.join(potential_id_cols)}\n"
    
    # Data type consistency
    mixed_type_cols = [name for name, info in schema.columns.items() 
                      if info.dtype == 'object' and info.suggested_role not in ['categorical', 'identifier']]
    
    if mixed_type_cols:
        prompt += f"\n**⚠️ Mixed Data Types**: {', '.join(mixed_type_cols)} may need type conversion\n"
    
    prompt += f"""
**Recommended quality checks:**

1. **Run validation**: `validate_data_quality('{dataset_name}')` for comprehensive analysis
2. **Examine distributions**: `create_chart('{dataset_name}', 'histogram', 'column_name')` for outliers
3. **Check relationships**: `find_correlations('{dataset_name}')` for unexpected patterns

What data quality aspect would you like to investigate first?"""
    
    return prompt
```

## Architecture Benefits

### True Reusability
- **One Server, Any Data**: Works with customer data, sales records, surveys, inventory, etc.
- **No Hardcoding**: Zero dataset-specific assumptions in tools or prompts
- **Instant Adaptation**: Load new dataset and immediately get relevant analysis options

### Modular Excellence
- **Data Layer Abstraction**: Pandas operations work identically across any structured data
- **Analysis Portability**: Same correlation/segmentation tools work on any applicable columns
- **Visualization Flexibility**: Charts adapt to data types and characteristics

### AI-Guided Discovery
- **Smart Recommendations**: AI suggests analyses based on actual data characteristics
- **Interactive Exploration**: Conversational guidance through complex analytics workflows
- **Context-Aware Prompts**: Prompts that reference actual column names and data patterns

### Business Value
- **Immediate Utility**: Drop in ANY business dataset and start analyzing immediately
- **Non-Technical Friendly**: AI guides users through analytics without requiring pandas knowledge
- **Scalable Insights**: Same server grows from 100-row CSV to 100K-row enterprise data

## Extension Pathways

### Advanced Analytics Integration
- **ML Pipeline**: Automatic feature engineering and model suggestion based on data
- **Statistical Testing**: A/B testing, significance testing, hypothesis validation
- **Forecasting**: Time series forecasting when temporal patterns detected

### Enterprise Features
- **Multi-Dataset Workflows**: Join and compare multiple datasets intelligently
- **Automated Reporting**: Generate business reports with insights and recommendations
- **Real-Time Updates**: Stream new data and update analyses automatically

### Collaboration Tools
- **Insight Sharing**: Export findings in business-friendly formats
- **Analysis Templates**: Save and reuse analysis workflows across datasets
- **Team Dashboards**: Collaborative analytics with role-based access

This generic approach transforms our MCP server from a user analytics tool into a **universal data analysis platform** that demonstrates the true power of modular architecture - building once and adapting to infinite use cases.