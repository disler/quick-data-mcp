# Generic Data Analytics MCP Server

A MCP (Model Context Protocol) server that transforms any structured dataset (JSON/CSV) into intelligent, AI-guided analytics workflows. This server demonstrates advanced modular architecture with **dataset-agnostic design** - it automatically adapts to ANY data without hardcoded schemas.

## 🚀 Quick Setup

1. **Configure for your MCP client**:
   ```bash
   cp .mcp.json.sample .mcp.json
   # Edit .mcp.json and update paths to your system
   ```

2. **Find your UV path and update configuration**:
   ```bash
   which uv
   # Example output: /Users/yourusername/.local/bin/uv
   
   pwd  
   # Example output: /Users/yourusername/path/to/quick-data-mcp
   ```

3. **Test the server**:
   ```bash
   uv run python main.py
   ```

## 🚀 Getting Started in Claude Code

Once your MCP server is configured and running, **start with this slash command in Claude Code to get oriented**:

```
/quick-data:list_mcp_assets_prompt
```

This will show you all available tools, resources, and prompts with descriptions - your complete toolkit for data analytics!

## 🚀 What Makes This Special

### Universal Data Analytics
- **Works with ANY JSON/CSV dataset** - no schema definition required
- **Automatic column type detection** - numerical, categorical, temporal, identifier
- **AI-powered analysis suggestions** - recommends analyses based on your data characteristics
- **Adaptive conversation prompts** - guides users through analytics workflows using actual column names

### Tested Architecture
- **32 Analytics Tools** (20 analytics + 12 resource mirrors) for comprehensive data analysis
- **12 Dynamic Resources** providing real-time data context  
- **7 Adaptive Prompts** for AI-guided exploration
- **100% Test Coverage** (103 tests passing)
- **Universal MCP Client Compatibility** (supports tool-only clients)
- **Memory optimization** with usage monitoring

## 📊 Complete Capabilities

### 🔧 Analytics Tools (32 total)

#### **Data Loading & Management**
- `load_dataset(file_path, dataset_name, sample_size?)` - Load any JSON/CSV with automatic schema discovery
- `list_loaded_datasets()` - Show all datasets currently in memory with statistics
- `clear_dataset(dataset_name)` - Remove specific dataset from memory
- `clear_all_datasets()` - Clear all datasets from memory
- `get_dataset_info(dataset_name)` - Get comprehensive dataset information

#### **Core Analytics**
- `segment_by_column(dataset_name, column_name, method?, top_n?)` - Generic segmentation on any categorical column
- `find_correlations(dataset_name, columns?, threshold?)` - Correlation analysis with configurable thresholds
- `analyze_distributions(dataset_name, column_name)` - Statistical distribution analysis for any column
- `detect_outliers(dataset_name, columns?, method)` - Outlier detection (IQR, Z-score methods)
- `time_series_analysis(dataset_name, date_column, value_column, frequency?)` - Temporal analysis with trend detection

#### **Advanced Analytics**
- `validate_data_quality(dataset_name)` - Comprehensive data quality assessment (0-100 scoring)
- `compare_datasets(dataset_a, dataset_b, common_columns?)` - Multi-dataset comparison analysis
- `merge_datasets(dataset_configs, join_strategy?)` - Join datasets with flexible strategies
- `calculate_feature_importance(dataset_name, target_column, feature_columns?)` - ML feature importance
- `memory_optimization_report(dataset_name)` - Performance analysis and optimization suggestions

#### **Visualization & Export**
- `create_chart(dataset_name, chart_type, x_column, y_column?, groupby_column?, title?, save_path?)` - Generate charts (bar, scatter, histogram, line, box)
- `generate_dashboard(dataset_name, chart_configs)` - Multi-chart interactive dashboards
- `export_insights(dataset_name, format?, include_charts?)` - Export in JSON, CSV, HTML formats

#### **AI-Powered Assistance**
- `suggest_analysis(dataset_name)` - AI recommendations based on data characteristics
- `execute_custom_analytics_code(dataset_name, python_code)` - Execute custom Python code against datasets with full pandas/numpy/plotly support

#### **🔄 Resource Mirror Tools** (Tool-Only Client Support)
*For MCP clients that don't support resources, all resource functionality is available through mirror tools:*

**Dataset Context Tools (4)**
- `resource_datasets_loaded()` - List all loaded datasets (mirrors `datasets://loaded`)
- `resource_datasets_schema(dataset_name)` - Get dataset schema (mirrors `datasets://{name}/schema`)
- `resource_datasets_summary(dataset_name)` - Statistical summary (mirrors `datasets://{name}/summary`)
- `resource_datasets_sample(dataset_name)` - Sample data rows (mirrors `datasets://{name}/sample`)

**Analytics Intelligence Tools (5)**
- `resource_analytics_current_dataset()` - Currently active dataset (mirrors `analytics://current_dataset`)
- `resource_analytics_available_analyses()` - Applicable analysis types (mirrors `analytics://available_analyses`)
- `resource_analytics_column_types()` - Column classifications (mirrors `analytics://column_types`)
- `resource_analytics_suggested_insights()` - AI recommendations (mirrors `analytics://suggested_insights`)
- `resource_analytics_memory_usage()` - Memory monitoring (mirrors `analytics://memory_usage`)

**System Tools (3)**
- `resource_config_server()` - Server configuration (mirrors `config://server`)
- `resource_users_profile(user_id)` - User profile access (mirrors `users://{user_id}/profile`)
- `resource_system_status()` - System health info (mirrors `system://status`)

### 📚 Dynamic Resources (12 total)

#### **Dataset Context Resources**
- `datasets://loaded` - Real-time inventory of all loaded datasets
- `datasets://{dataset_name}/schema` - Dynamic schema with column classification
- `datasets://{dataset_name}/summary` - Statistical summary (pandas.describe() equivalent)
- `datasets://{dataset_name}/sample` - Sample rows for data preview

#### **Analytics Intelligence Resources**
- `analytics://current_dataset` - Currently active dataset context
- `analytics://available_analyses` - Applicable analysis types for current data
- `analytics://column_types` - Column role classification (numerical, categorical, temporal, identifier)
- `analytics://suggested_insights` - AI-generated analysis recommendations
- `analytics://memory_usage` - Real-time memory monitoring

#### **System Resources** (Legacy Compatibility)
- `config://server` - Server configuration information
- `users://{user_id}/profile` - User profile access by ID
- `system://status` - System health and status information

### 💬 Adaptive Prompts (7 total)

#### **Data Exploration Prompts**
- `dataset_first_look(dataset_name)` - Personalized initial exploration guide based on actual data structure
- `segmentation_workshop(dataset_name)` - Interactive segmentation strategy using real column names
- `data_quality_assessment(dataset_name)` - Systematic quality review with specific recommendations

#### **Analysis Workflow Prompts**
- `correlation_investigation(dataset_name)` - Guided correlation analysis workflow
- `pattern_discovery_session(dataset_name)` - Open-ended pattern mining conversation

#### **Business Intelligence Prompts**
- `insight_generation_workshop(dataset_name, business_context?)` - Business insight generation with domain context
- `dashboard_design_consultation(dataset_name, audience?)` - Audience-specific dashboard planning

## 🏗️ Project Structure

```
quick-data-mcp/
├── .mcp.json                      # Ready-to-use MCP client configuration
├── data/                          # Sample datasets
│   ├── ecommerce_orders.json      # E-commerce transaction data
│   ├── employee_survey.csv        # HR analytics dataset
│   ├── product_performance.csv    # Product metrics dataset
│   └── README.md                  # Data documentation
├── src/mcp_server/               # Core server implementation
│   ├── server.py                 # Main server with 31 tools, 12 resources, 7 prompts
│   ├── tools/                    # Tool implementations
│   │   ├── pandas_tools.py       # Pandas-based tools grouped module
│   │   ├── __init__.py           # All tools (32 total)
│   │   └── [individual_tool_files.py]  # Individual tool implementations
│   ├── resources/                # Resource handlers
│   │   └── data_resources.py     # Dynamic data access (12 resources)
│   ├── prompts/                  # Conversation starters
│   │   ├── __init__.py           # All prompts (9 total)
│   │   └── [individual_prompt_files.py]  # Individual prompt implementations
│   ├── models/                   # Data models and schemas
│   │   └── schemas.py            # DatasetManager, ColumnInfo, DatasetSchema
│   └── config/                   # Configuration
│       └── settings.py           # Server settings
├── tests/                            # Comprehensive test suite (130 tests)
│   ├── test_pandas_tools.py              # Pandas tools tests
│   ├── test_analytics_tools.py           # Advanced tools tests
│   ├── test_analytics_prompts.py         # Prompts functionality tests
│   ├── test_data_resources.py            # Resource access tests
│   ├── test_resource_mirror_tools.py     # Resource mirror tool tests
│   └── test_custom_analytics_code.py     # Custom code execution tests
├── outputs/                      # Generated files (excluded from git)
│   ├── charts/                   # Generated HTML charts and dashboards
│   └── reports/                  # Exported insights and reports
└── main.py                       # Entry point
```

## 📦 Dependencies

### Core Analytics Stack
- `mcp[cli]>=1.9.2` - Official MCP Python SDK
- `pandas>=2.2.3` - Data manipulation and analysis
- `plotly>=6.1.2` - Interactive visualizations

### Testing & Development
- `pytest>=8.3.5` - Testing framework
- `pytest-asyncio>=1.0.0` - Async testing support

## 🚀 Usage

### MCP Client Integration

Once configured, your MCP client can access all **32 tools**, **12 resources**, and **9 prompts** for comprehensive data analytics.

### Example Analytics Workflow

```python
# 1. Load any dataset
await load_dataset("data/ecommerce_orders.json", "sales")

# 2. Get AI-powered first look guidance
await dataset_first_look("sales")
# → Returns personalized exploration guide with actual column names

# 3. Automatic analysis suggestions
await suggest_analysis("sales")
# → AI recommends: correlation_analysis, segmentation_analysis based on detected columns

# 4. Perform suggested analyses
await find_correlations("sales")
# → Finds relationships between numerical columns

await segment_by_column("sales", "customer_segment")
# → Groups data and calculates statistics automatically

# 5. Create adaptive visualizations
await create_chart("sales", "bar", "region", "order_value")
# → Generates interactive plotly charts

# 6. Comprehensive data quality assessment
await validate_data_quality("sales")
# → Returns 0-100 quality score with detailed recommendations
```

### Advanced Multi-Dataset Analysis

```python
# Load multiple datasets
await load_dataset("data/employee_survey.csv", "hr")
await load_dataset("data/product_performance.csv", "products")

# Compare datasets
await compare_datasets("sales", "products", ["category"])

# Generate business insights
await insight_generation_workshop("sales", "e-commerce")

# Create executive dashboard
await dashboard_design_consultation("hr", "executive")
```

### 🔥 Custom Analytics Code Execution

Execute any Python code against your datasets with full pandas/numpy/plotly support:

```python
# Custom analysis that goes beyond predefined tools
output = await execute_custom_analytics_code("sales", """
print("=== Custom Customer Segmentation ===")

# Advanced customer scoring algorithm
customer_scores = df.groupby('customer_id').agg({
    'order_value': ['sum', 'mean', 'count'],
    'date': ['min', 'max']
}).round(2)

# Flatten column names
customer_scores.columns = ['total_spent', 'avg_order', 'order_count', 'first_order', 'last_order']

# Calculate customer lifetime (days)
customer_scores['lifetime_days'] = (
    pd.to_datetime(customer_scores['last_order']) - 
    pd.to_datetime(customer_scores['first_order'])
).dt.days

# Custom scoring formula
customer_scores['loyalty_score'] = (
    customer_scores['total_spent'] * 0.4 + 
    customer_scores['order_count'] * 50 + 
    customer_scores['lifetime_days'] * 0.1
).round(1)

# Segment customers
def segment_customer(score):
    if score >= 1000: return 'VIP'
    elif score >= 500: return 'Gold'
    elif score >= 200: return 'Silver'
    else: return 'Bronze'

customer_scores['segment'] = customer_scores['loyalty_score'].apply(segment_customer)

print("Customer Segments:")
print(customer_scores['segment'].value_counts())

print("\\nTop 5 Customers:")
top_customers = customer_scores.sort_values('loyalty_score', ascending=False).head()
for idx, (customer_id, data) in enumerate(top_customers.iterrows(), 1):
    print(f"{idx}. {customer_id}: {data['segment']} (Score: {data['loyalty_score']})")
""")

# Agents can iterate on code based on output
if "ERROR:" in output:
    # Fix the code and try again
    pass
else:
    print("Analysis completed successfully!")
```

### 🔄 Resource Mirror Tools Usage (Tool-Only Clients)

For MCP clients that don't support resources, use the resource mirror tools for identical functionality:

```python
# Instead of accessing resource: datasets://loaded
datasets = await resource_datasets_loaded()
# → Returns: {"datasets": [...], "total_datasets": 2, "status": "loaded"}

# Instead of accessing resource: datasets://sales/schema  
schema = await resource_datasets_schema("sales")
# → Returns: {"dataset_name": "sales", "columns_by_type": {...}}

# Instead of accessing resource: analytics://memory_usage
memory = await resource_analytics_memory_usage()
# → Returns: {"datasets": [...], "total_memory_mb": 15.2}

# Instead of accessing resource: config://server
config = await resource_config_server()
# → Returns: {"name": "Generic Data Analytics MCP", "features": [...]}

# All 12 resource mirror tools provide identical data to their resource counterparts
# Perfect for tool-only MCP clients or when resource support is unavailable
```

## 🧪 Testing

```bash
# Run all 130 tests
uv run python -m pytest tests/ -v

# Test specific functionality
uv run python -m pytest tests/test_pandas_tools.py -v              # Pandas tools
uv run python -m pytest tests/test_analytics_tools.py -v           # Advanced tools
uv run python -m pytest tests/test_analytics_prompts.py -v         # Prompts functionality
uv run python -m pytest tests/test_resource_mirror_tools.py -v     # Resource mirror tools
uv run python -m pytest tests/test_custom_analytics_code.py -v     # Custom code execution

# Quick test run
uv run python -m pytest tests/ -q
# Expected: 130 passed
```

## 🔧 MCP Client Configuration

### Quick Setup (Recommended)

This project includes a sample configuration that you can customize:

1. **Copy the sample configuration**:
   ```bash
   cp .mcp.json.sample .mcp.json
   ```

2. **Update paths in `.mcp.json`** to match your system:
   ```json
   {
     "mcpServers": {
       "quick-data": {
         "command": "/path/to/uv",
         "args": [
           "--directory",
           "/path/to/your/quick-data-mcp",
           "run",
           "python",
           "main.py"
         ],
         "env": {
           "LOG_LEVEL": "INFO"
         }
       }
     }
   }
   ```

3. **Find your UV path**:
   ```bash
   which uv
   # Example output: /Users/yourusername/.local/bin/uv
   ```

4. **Get absolute path to this directory**:
   ```bash
   pwd
   # Example output: /Users/yourusername/path/to/quick-data-mcp
   ```

5. **Update `.mcp.json`** with your actual paths:
   - Replace `/path/to/uv` with your UV path
   - Replace `/path/to/your/quick-data-mcp` with your absolute directory path

6. **Copy to your MCP client** or reference directly if supported

### Option 2: Manual Configuration

If you prefer to configure manually, add to your MCP client configuration:

```json
{
  "mcpServers": {
    "quick-data": {
      "command": "/path/to/uv",
      "args": [
        "--directory", 
        "/absolute/path/to/quick-data-mcp",
        "run", 
        "python", 
        "main.py"
      ],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important**: Replace the placeholder paths with your actual system paths.

### Configuration Notes

- **Use absolute paths** for reliability across different working directories
- **`--directory` flag** ensures UV operates in the correct project directory  
- **`.mcp.json` is gitignored** - each user needs their own copy with local paths
- **Use `.mcp.json.sample`** as a template to avoid path conflicts
- **Environment variables** can be customized per deployment

### Environment Variables

- `LOG_LEVEL` - Logging level (default: INFO)
- `SERVER_NAME` - Server name (default: "Generic Data Analytics MCP")

## 🚀 Getting Started in Claude Code

Once your MCP server is configured and running, **start with this slash command in Claude Code to get oriented**:

```
/quick-data:list_mcp_assets_prompt
```

This will show you all available tools, resources, and prompts with descriptions - your complete toolkit for data analytics!

## 💡 Sample Datasets Included

### E-commerce Orders (`data/ecommerce_orders.json`)
- **15 orders** with customer segments, regions, product categories
- **Use cases**: Revenue analysis, customer segmentation, regional performance

### Employee Survey (`data/employee_survey.csv`) 
- **25 employees** with satisfaction scores, departments, tenure
- **Use cases**: HR analytics, satisfaction analysis, department comparisons

### Product Performance (`data/product_performance.csv`)
- **20 products** with sales, suppliers, ratings, launch dates
- **Use cases**: Product analysis, supplier performance, market trends

## 🎯 Architecture Benefits

### Dataset Agnosticism
- **Works with ANY structured data** - no hardcoded schemas required
- **Intelligent column detection** - automatically classifies data types
- **Zero configuration** - drop in data files and start analyzing immediately

### Modular Excellence  
- **Clean separation** - tools, resources, prompts, and models organized logically
- **Independent testing** - each component tested in isolation
- **Easy extension** - add new analytics without affecting existing functionality

### Production Ready
- **Comprehensive error handling** - graceful failures with actionable messages
- **Memory optimization** - efficient pandas operations with usage monitoring
- **Performance monitoring** - built-in analytics for large datasets

### AI Integration
- **Smart recommendations** - analysis suggestions based on data characteristics
- **Context-aware prompts** - conversations that reference real column names
- **Adaptive workflows** - tools that adjust behavior based on data types

## 🔮 Extension Examples

### Adding Custom Analytics
```python
# Add to tools/__init__.py or individual tool file
@staticmethod
async def custom_analysis(dataset_name: str, parameters: dict) -> dict:
    """Your custom analysis function."""
    df = DatasetManager.get_dataset(dataset_name)
    # Your analysis logic here
    return {"analysis": "results"}

# Register in server.py
@mcp.tool()
async def custom_analysis(dataset_name: str, parameters: dict) -> dict:
    return await tools.custom_analysis(dataset_name, parameters)
```

### Adding Domain-Specific Prompts
```python
# Add to prompts/__init__.py
@staticmethod
async def financial_analysis_workshop(dataset_name: str) -> str:
    """Guide financial analysis workflows."""
    # Custom financial analysis guidance
    return prompt_text

# Register in server.py  
@mcp.prompt()
async def financial_analysis_workshop(dataset_name: str) -> str:
    return await prompts.financial_analysis_workshop(dataset_name)
```

## 🏆 Success Metrics

- ✅ **Comprehensive Test Coverage** - 130 tests passing
- ✅ **Universal Data Compatibility** - Works with any JSON/CSV structure  
- ✅ **Universal MCP Client Compatibility** - Supports both resource-enabled and tool-only clients
- ✅ **Custom Code Execution** - Full Python analytics capabilities with pandas/numpy/plotly
- ✅ **AI Integration** - Smart recommendations and adaptive conversations
- ✅ **Performance Optimized** - Memory-efficient operations with monitoring

This MCP server transforms the concept of data analytics from rigid, schema-dependent tools into a flexible, AI-guided platform that adapts to any dataset while providing expert-level guidance through conversational interfaces.
