# Data Analytics MCP Server

An MCP (Model Context Protocol) server that provides analytics capabilities for structured datasets (JSON/CSV). The server features a modular architecture with dataset-agnostic design, allowing it to work with any data structure without predefined schemas.

## Setup

1. **Configure MCP client**:
   ```bash
   cp .mcp.json.sample .mcp.json
   # Edit .mcp.json and update paths to your system
   ```

2. **Update paths in configuration**:
   ```bash
   which uv  # Get your UV path
   pwd       # Get project path
   # Update these paths in .mcp.json
   ```

3. **Run the server**:
   ```bash
   uv run python main.py
   ```

## Architecture

### Components
- **Tools** (32): Data manipulation, analysis, and visualization functions
- **Resources** (12): Dynamic data providers for real-time context
- **Prompts** (8): Conversation starters for analytics workflows
- **Dataset Manager**: Centralized dataset handling and state management
- **Code Executor**: Python code execution with safety features

### Key Features
- Dataset-agnostic design - works with any JSON/CSV structure
- Automatic column type detection (numerical, categorical, temporal, identifier)
- Safe Python code execution with import blocking
- Memory usage monitoring (512MB limit)
- Comprehensive error handling with actionable messages

## Usage Examples

### Loading Data
```python
# Load a JSON dataset
await load_dataset(
    file_path="data/ecommerce_orders.json",
    dataset_name="orders"
)

# Load a CSV dataset
await load_dataset(
    file_path="data/employee_survey.csv", 
    dataset_name="survey"
)
```

### Basic Analysis
```python
# Get dataset information
await get_dataset_info(dataset_name="orders")

# Analyze distributions
await analyze_distributions(
    dataset_name="orders",
    column_name="order_value"
)

# Find correlations
await find_correlations(
    dataset_name="survey",
    threshold=0.3
)
```

### Visualization
```python
# Create a chart
await create_chart(
    dataset_name="orders",
    chart_type="bar",
    x_column="product_category",
    y_column="order_value"
)

# Generate dashboard
await generate_dashboard(
    dataset_name="orders",
    chart_configs=[
        {"type": "bar", "x": "category", "y": "sales"},
        {"type": "line", "x": "date", "y": "revenue"}
    ]
)
```

### Custom Analysis
```python
# Execute custom Python code
await execute_enhanced_analytics_code_tool(
    dataset_name="orders",
    python_code="""
print(df.shape)
print(df.columns.tolist())
print(df.describe())
""",
    execution_mode="safe"
)
```

## Available Tools

### Data Management
- `load_dataset` - Load JSON/CSV data into memory
- `list_loaded_datasets` - Show all loaded datasets
- `clear_dataset` - Remove dataset from memory
- `get_dataset_info` - Get basic dataset information

### Analysis Tools
- `segment_by_column` - Segment data by categorical columns
- `find_correlations` - Find correlations between numerical columns
- `analyze_distributions` - Analyze column distributions
- `detect_outliers` - Detect outliers using IQR or Z-score
- `time_series_analysis` - Temporal analysis for date columns
- `calculate_feature_importance` - Feature importance for modeling

### Visualization
- `create_chart` - Create various chart types (bar, line, scatter, etc.)
- `generate_dashboard` - Multi-chart dashboards

### Advanced Features
- `execute_enhanced_analytics_code_tool` - Run custom Python analysis
- `suggest_analysis` - AI-powered analysis recommendations
- `validate_data_quality` - Data quality assessment
- `compare_datasets` - Compare multiple datasets
- `merge_datasets` - Join datasets on common keys

## Resources

Resources provide real-time context about loaded data:

- `datasets://loaded` - List of loaded datasets
- `datasets://{name}/schema` - Dataset schema information
- `datasets://{name}/summary` - Statistical summary
- `datasets://{name}/sample` - Sample data rows
- `analytics://current_dataset` - Currently active dataset
- `analytics://suggested_insights` - AI-generated insights

## Prompts

Interactive prompts guide analytics workflows:

- `list_mcp_assets_prompt` - Show all available tools and resources
- `quick_start_analysis_prompt` - Step-by-step analysis guide
- `dashboard_creation_prompt` - Dashboard building workflow
- `insight_generation_prompt` - Generate data insights
- `time_series_workflow_prompt` - Time series analysis guide

## Development

### Requirements
- Python 3.12+
- Dependencies: `mcp[cli]`, `pandas`, `plotly`, `pytest`, `pytest-asyncio`

### Testing
```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test module
uv run python -m pytest tests/test_pandas_tools.py -v

# Run integration tests
uv run python -m pytest tests/integration/ -v
```

### Project Structure
```
src/mcp_server/
├── server.py          # Main MCP server
├── tools/             # Analytics tools
├── resources/         # Data resources
├── prompts/           # Conversation prompts
├── models/            # Data models
├── managers/          # Dataset management
├── orchestration/     # Workflow coordination
└── advanced/          # Advanced features
```

## Configuration

### Environment Variables
- `LOG_LEVEL` - Logging level (default: INFO)
- `SERVER_NAME` - Server name for MCP

### MCP Configuration
The `.mcp.json` file configures the MCP server:
```json
{
  "mcpServers": {
    "quick-data": {
      "command": "path/to/uv",
      "args": ["run", "python", "main.py"],
      "cwd": "path/to/quick-data-mcp"
    }
  }
}
```

## Safety Features

### Code Execution
- Import blocking for dangerous modules (os, subprocess, etc.)
- Memory limit enforcement (512MB)
- Timeout protection (30 seconds default)
- Subprocess isolation

### Error Handling
- Comprehensive error messages
- Actionable debugging hints
- Safety violation detection
- Performance monitoring

## License

MIT License - see LICENSE file for details.