# Custom Analytics Code Execution Tool

## Problem Statement

Current analytics tools provide predefined operations (correlations, segmentation, charts), but AI agents often need to perform **custom analysis** that goes beyond these fixed patterns. Agents should be able to write and execute their own Python code against loaded datasets for:

- **Novel analysis patterns** not covered by existing tools
- **Custom calculations** (financial metrics, scientific formulas, etc.)
- **Complex data transformations** requiring multi-step operations
- **Domain-specific analysis** tailored to specific business needs
- **Experimental algorithms** for pattern detection and insights

## Solution Overview

Implement an **`execute_custom_analytics_code()`** tool that:
- Accepts dataset name and Python code as parameters
- Executes code in a **subprocess** with access to the specified dataset
- Returns **stdout/stderr output** as a string for agent iteration
- Provides **basic error capture** so agents can debug and fix code
- Uses **subprocess isolation** for safety

## Architecture Design

### Simplified Flow

```
┌─────────────────────────────────────────────┐
│           MCP Server (Main Process)         │
├─────────────────────────────────────────────┤
│  execute_custom_analytics_code()            │
│       │                                     │
│       ▼                                     │
│  1. Get dataset from DatasetManager         │
│  2. Serialize to JSON                       │
│  3. Wrap code in execution template         │
│  4. Launch subprocess with uv run           │
│  5. Capture stdout/stderr                   │
│  6. Return output string                    │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│        Python Subprocess (Isolated)         │
├─────────────────────────────────────────────┤
│  - pandas, numpy, plotly imported           │
│  - Dataset loaded as 'df' DataFrame         │
│  - User code executed with try/catch        │
│  - All output printed to stdout             │
│  - 30 second timeout enforced              │
└─────────────────────────────────────────────┘
```

### Data Flow

1. **Agent Request**: `execute_custom_analytics_code(dataset_name, python_code)`
2. **Dataset Access**: Get DataFrame from loaded datasets
3. **Serialization**: Convert dataset to JSON for subprocess
4. **Code Wrapping**: Embed user code in safe execution template
5. **Subprocess Launch**: `uv run --with pandas python -c "..."`
6. **Output Capture**: Collect all stdout/stderr output
7. **Return Result**: Simple string with all output for agent parsing

## API Specification

### Tool Definition

```python
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
```

### Execution Template

The tool automatically wraps user code in a safe execution environment:

```python
# Agent provides this:
user_code = """
print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())

# Calculate customer lifetime value
customer_ltv = df.groupby('customer_id')['order_value'].sum()
print("Top 5 customers by total value:")
print(customer_ltv.sort_values(ascending=False).head())

# Basic statistics
print("Average order value:", df['order_value'].mean())
print("Total customers:", df['customer_id'].nunique())
"""

# Tool wraps it in execution template:
execution_template = f"""
import pandas as pd
import numpy as np
import plotly.express as px

# Load dataset
try:
    # Dataset serialized as JSON from DatasetManager
    dataset_data = {serialized_dataset}
    df = pd.DataFrame(dataset_data)
    
    # Execute user code
    {user_code}
    
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
    import traceback
    print("Traceback:")
    print(traceback.format_exc())
"""
```

### Response Format

Simple string return with stdout/stderr combined:

```python
# Success case:
"Dataset shape: (1000, 5)
Columns: ['customer_id', 'order_value', 'date', 'category', 'region']
Top 5 customers by total value:
customer_id
C001    5670.50
C043    4320.75
C012    3890.25
C087    3456.80
C234    3201.40
Average order value: 125.45
Total customers: 250"

# Error case:
"ERROR: KeyError: 'invalid_column'
Traceback:
  File \"<string>\", line 8, in <module>
    result = df['invalid_column'].sum()
KeyError: 'invalid_column'"

# Timeout case:
"TIMEOUT: Code execution exceeded 30 second limit"
```

## Security Model

### Subprocess Isolation

- **Process isolation**: Code runs in separate Python process via `uv run`
- **30 second timeout**: Prevents infinite loops and resource exhaustion
- **No file system access**: Subprocess cannot access host files
- **Limited imports**: Only safe libraries (pandas, numpy, plotly) available
- **Read-only dataset access**: Dataset copied as JSON, not referenced

### Basic Safety Measures

```python
# Execute in isolated subprocess
process = await asyncio.create_subprocess_exec(
    'uv', 'run', '--with', 'pandas', '--with', 'numpy', '--with', 'plotly',
    'python', '-c', execution_code,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.STDOUT,
    timeout=30  # Hard timeout limit
)
```

## Implementation Plan

### Core Implementation

Add to `analytics_tools.py`:

```python
import asyncio
import json
import subprocess
from typing import Dict, Any
from pathlib import Path

async def execute_custom_analytics_code(dataset_name: str, python_code: str) -> str:
    """
    Execute custom Python code against a loaded dataset.
    
    Implementation steps:
    1. Get dataset from DatasetManager
    2. Serialize dataset to JSON for subprocess
    3. Wrap user code in execution template
    4. Execute via subprocess with uv run python -c
    5. Capture and return stdout/stderr
    """
    try:
        # Step 1: Get dataset
        df = DatasetManager.get_dataset(dataset_name)
        
        # Step 2: Serialize dataset
        dataset_json = df.to_json(orient='records')
        
        # Step 3: Create execution template
        execution_code = f'''
import pandas as pd
import numpy as np
import plotly.express as px
import json

try:
    # Load dataset
    dataset_data = {dataset_json}
    df = pd.DataFrame(dataset_data)
    
    # Execute user code
    {python_code}
    
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
    import traceback
    print("Traceback:")
    print(traceback.format_exc())
'''
        
        # Step 4: Execute subprocess
        process = await asyncio.create_subprocess_exec(
            'uv', 'run', '--with', 'pandas', '--with', 'numpy', '--with', 'plotly',
            'python', '-c', execution_code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            timeout=30
        )
        
        # Step 5: Get output
        stdout, _ = await process.communicate()
        return stdout.decode('utf-8')
        
    except subprocess.TimeoutExpired:
        return "TIMEOUT: Code execution exceeded 30 second limit"
    except Exception as e:
        return f"EXECUTION ERROR: {type(e).__name__}: {str(e)}"
```

### Integration with Server

Add to `server.py`:

```python
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
    
    Args:
        dataset_name: Name of the loaded dataset to analyze
        python_code: Python code to execute (must print() results to see output)
        
    Returns:
        str: Combined stdout and stderr output from code execution
    """
    return await analytics_tools.execute_custom_analytics_code(dataset_name, python_code)
```

## Usage Examples

### Basic Data Analysis

```python
output = await execute_custom_analytics_code(
    dataset_name="sales_data",
    python_code="""
print("Dataset Info:")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Basic statistics
print("\\nBasic Statistics:")
print(f"Total sales: ${df['order_value'].sum():,.2f}")
print(f"Average order: ${df['order_value'].mean():.2f}")
print(f"Unique customers: {df['customer_id'].nunique()}")

# Top customers
top_customers = df.groupby('customer_id')['order_value'].sum().sort_values(ascending=False).head()
print("\\nTop 5 Customers:")
for customer, total in top_customers.items():
    print(f"{customer}: ${total:.2f}")
"""
)

# Output:
# Dataset Info:
# Shape: (1500, 5) 
# Columns: ['customer_id', 'order_value', 'order_date', 'category', 'region']
# 
# Basic Statistics:
# Total sales: $125,430.50
# Average order: $83.62
# Unique customers: 250
# 
# Top 5 Customers:
# C001: $5,670.50
# C043: $4,320.75
# ...
```

### Custom Calculations

```python
output = await execute_custom_analytics_code(
    dataset_name="employee_survey",
    python_code="""
# Employee satisfaction analysis
satisfaction_cols = ['work_life_balance', 'compensation', 'career_growth']

print("Satisfaction Metrics:")
for col in satisfaction_cols:
    avg_score = df[col].mean()
    print(f"{col.replace('_', ' ').title()}: {avg_score:.2f}/5")

# Department comparison
dept_satisfaction = df.groupby('department')[satisfaction_cols].mean()
print("\\nDepartment Satisfaction Averages:")
print(dept_satisfaction.round(2))

# Find correlation
if len(satisfaction_cols) >= 2:
    correlation = df[satisfaction_cols].corr()
    print("\\nCorrelation Matrix:")
    print(correlation.round(3))
"""
)
```

### Error Handling Example

```python
# Agent tries invalid code
output = await execute_custom_analytics_code(
    dataset_name="sales_data", 
    python_code="""
# This will cause an error
result = df['nonexistent_column'].sum()
print(f"Result: {result}")
"""
)

# Output:
# ERROR: KeyError: 'nonexistent_column'
# Traceback:
#   File "<string>", line 9, in <module>
#     result = df['nonexistent_column'].sum()
# KeyError: 'nonexistent_column'

# Agent can then fix the code
output = await execute_custom_analytics_code(
    dataset_name="sales_data",
    python_code="""
# Check available columns first
print("Available columns:", df.columns.tolist())

# Use correct column name
result = df['order_value'].sum()
print(f"Total sales: ${result:.2f}")
"""
)
```

## Error Handling Strategy

### Code Execution Errors

```python
{
    "status": "error",
    "error_details": {
        "type": "SyntaxError",
        "message": "invalid syntax (line 5)",
        "line_number": 5,
        "code_snippet": "df.groupby('invalid_column')",
        "suggestion": "Check column names with df.columns"
    },
    "partial_outputs": {
        "stdout": "Data loaded successfully\n",
        "executed_lines": 4
    }
}
```

### Timeout Handling

```python
{
    "status": "timeout",
    "execution_time": 30.0,
    "partial_results": {
        "last_output": "Processing large dataset...",
        "completed_operations": ["data_loading", "initial_analysis"]
    },
    "recommendations": [
        "Consider sampling the dataset first",
        "Break analysis into smaller chunks",
        "Increase timeout_seconds parameter"
    ]
}
```

### Security Violations

```python
{
    "status": "error",
    "error_details": {
        "type": "SecurityViolation",
        "violations": [
            {
                "pattern": "import os",
                "line": 3,
                "severity": "high",
                "reason": "Operating system access not allowed"
            }
        ]
    },
    "suggested_alternatives": [
        "Use Path from pathlib for file operations",
        "Use pandas for data file handling"
    ]
}
```

## Testing Strategy

Add to `tests/test_custom_analytics_code.py`:

```python
import pytest
from mcp_server.tools import analytics_tools
from mcp_server.server import execute_custom_analytics_code

@pytest.mark.asyncio
class TestCustomAnalyticsCode:
    
    async def test_basic_execution(self, sample_dataset):
        """Test simple code execution with valid operations."""
        result = await execute_custom_analytics_code(
            "test_data",
            "print('Dataset shape:', df.shape)"
        )
        assert "Dataset shape:" in result
        assert "(" in result and ")" in result
    
    async def test_data_analysis(self, sample_dataset):
        """Test actual data analysis operations."""
        code = """
print("Columns:", df.columns.tolist())
print("Row count:", len(df))
if 'value' in df.columns:
    print("Sum:", df['value'].sum())
"""
        result = await execute_custom_analytics_code("test_data", code)
        assert "Columns:" in result
        assert "Row count:" in result
    
    async def test_error_handling(self, sample_dataset):
        """Test error capture and reporting."""
        result = await execute_custom_analytics_code(
            "test_data",
            "result = df['nonexistent_column'].sum()"
        )
        assert "ERROR:" in result
        assert "KeyError" in result
        
    async def test_timeout_handling(self, sample_dataset):
        """Test timeout behavior with infinite loop."""
        result = await execute_custom_analytics_code(
            "test_data", 
            "while True: pass"
        )
        assert "TIMEOUT:" in result
        
    async def test_invalid_dataset(self):
        """Test behavior with nonexistent dataset."""
        result = await execute_custom_analytics_code(
            "nonexistent_dataset",
            "print(df.shape)"
        )
        assert "EXECUTION ERROR:" in result
        
    async def test_empty_code(self, sample_dataset):
        """Test execution with empty code."""
        result = await execute_custom_analytics_code("test_data", "")
        # Should complete without error (no output)
        assert result is not None
        
    async def test_multiline_output(self, sample_dataset):
        """Test code that produces multiple lines of output."""
        code = """
for i in range(3):
    print(f"Line {i+1}")
print("Final line")
"""
        result = await execute_custom_analytics_code("test_data", code)
        lines = result.strip().split('\n')
        assert len(lines) == 4
        assert "Line 1" in result
        assert "Final line" in result
```

## Performance Considerations

### Key Constraints

- **30 second timeout** prevents infinite loops and long-running operations
- **JSON serialization** for dataset transfer (efficient for most datasets <10MB)
- **Subprocess isolation** provides security but adds ~100ms overhead
- **Memory usage** limited by subprocess environment (typically 512MB available)

### Dataset Size Recommendations

- **Small datasets** (<1MB): Optimal performance, <1 second execution
- **Medium datasets** (1-10MB): Good performance, 1-3 second execution  
- **Large datasets** (>10MB): Consider sampling first with existing tools

## Success Metrics

### Core Functionality
- ✅ **Error Capture**: All Python errors returned to agent for iteration
- ✅ **Timeout Handling**: Graceful termination of long-running code
- ✅ **Output Return**: Complete stdout/stderr captured and returned
- ✅ **Dataset Access**: All loaded datasets available via simple API

### Integration Quality
- ✅ **Agent Usability**: Clear documentation guides successful usage
- ✅ **Error Recovery**: Agents can debug and fix code based on error output
- ✅ **Performance**: Most analyses complete within reasonable time
- ✅ **Security**: Subprocess isolation prevents system access

This custom code execution capability transforms the MCP server from a **fixed-function analytics platform** into a **flexible data science environment** where AI agents can implement any analysis they can conceive, with simple error handling enabling rapid iteration.