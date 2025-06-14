"""Tests for custom analytics code execution tool."""

import pytest
import pandas as pd
from mcp_server import tools
from mcp_server.server import execute_custom_analytics_code
from mcp_server.models.schemas import DatasetManager, loaded_datasets, dataset_schemas


@pytest.fixture
def sample_test_dataset():
    """Create a test dataset for custom code execution."""
    # Create sample data
    data = {
        'customer_id': ['C001', 'C002', 'C003', 'C001', 'C002'],
        'order_value': [100.0, 250.0, 75.0, 150.0, 200.0],
        'category': ['A', 'B', 'A', 'C', 'B'],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'region': ['North', 'South', 'North', 'East', 'South']
    }
    df = pd.DataFrame(data)
    
    # Load into DatasetManager
    loaded_datasets['test_custom'] = df
    
    # Create basic schema
    from mcp_server.models.schemas import DatasetSchema
    schema = DatasetSchema.from_dataframe(df, 'test_custom')
    dataset_schemas['test_custom'] = schema
    
    yield 'test_custom'
    
    # Cleanup
    if 'test_custom' in loaded_datasets:
        del loaded_datasets['test_custom']
    if 'test_custom' in dataset_schemas:
        del dataset_schemas['test_custom']


@pytest.mark.asyncio
class TestCustomAnalyticsCode:
    
    async def test_basic_execution(self, sample_test_dataset):
        """Test simple code execution with valid operations."""
        result = await execute_custom_analytics_code(
            "test_custom",
            "print('Dataset shape:', df.shape)"
        )
        assert "Dataset shape:" in result
        assert "(5, 5)" in result
    
    async def test_data_analysis(self, sample_test_dataset):
        """Test actual data analysis operations."""
        code = """
print("Columns:", df.columns.tolist())
print("Row count:", len(df))
print("Customer count:", df['customer_id'].nunique())
if 'order_value' in df.columns:
    print("Total sales:", df['order_value'].sum())
"""
        result = await execute_custom_analytics_code("test_custom", code)
        assert "Columns:" in result
        assert "Row count: 5" in result
        assert "Customer count: 3" in result
        assert "Total sales: 775.0" in result
    
    async def test_error_handling(self, sample_test_dataset):
        """Test error capture and reporting."""
        result = await execute_custom_analytics_code(
            "test_custom",
            "result = df['nonexistent_column'].sum()"
        )
        assert "ERROR:" in result
        assert "KeyError" in result
        assert "nonexistent_column" in result
        
    async def test_timeout_handling(self, sample_test_dataset):
        """Test timeout behavior with long-running code."""
        result = await execute_custom_analytics_code(
            "test_custom", 
            """
import time
time.sleep(35)  # Longer than 30 second timeout
print("This should not appear")
"""
        )
        assert "TIMEOUT:" in result
        assert "30 second limit" in result
        
    async def test_invalid_dataset(self):
        """Test behavior with nonexistent dataset."""
        result = await execute_custom_analytics_code(
            "nonexistent_dataset",
            "print(df.shape)"
        )
        assert "EXECUTION ERROR:" in result
        assert "not loaded" in result or "not found" in result
        
    async def test_empty_code(self, sample_test_dataset):
        """Test execution with empty code."""
        result = await execute_custom_analytics_code("test_custom", "")
        # Should complete without error (no output)
        assert result is not None
        assert result.strip() == ""
        
    async def test_multiline_output(self, sample_test_dataset):
        """Test code that produces multiple lines of output."""
        code = """
for i in range(3):
    print(f"Line {i+1}")
print("Final line")
"""
        result = await execute_custom_analytics_code("test_custom", code)
        lines = result.strip().split('\n')
        assert len(lines) == 4
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result
        assert "Final line" in result

    async def test_pandas_operations(self, sample_test_dataset):
        """Test pandas operations work correctly."""
        code = """
# Test groupby operations
customer_totals = df.groupby('customer_id')['order_value'].sum()
print("Customer totals:")
print(customer_totals.sort_values(ascending=False))

# Test filtering
high_value = df[df['order_value'] > 150]
print("High value orders:", len(high_value))

# Test basic stats
print("Average order:", df['order_value'].mean())
"""
        result = await execute_custom_analytics_code("test_custom", code)
        assert "Customer totals:" in result
        assert "C001" in result  # Should show customer C001
        assert "High value orders: 2" in result
        assert "Average order: 155.0" in result

    async def test_numpy_operations(self, sample_test_dataset):
        """Test numpy operations work correctly."""
        code = """
import numpy as np
print("NumPy available:", hasattr(np, 'array'))
print("Array operations:")
values = np.array(df['order_value'])
print("Mean:", np.mean(values))
print("Std:", np.std(values))
"""
        result = await execute_custom_analytics_code("test_custom", code)
        assert "NumPy available: True" in result
        assert "Mean:" in result
        assert "Std:" in result

    async def test_plotly_import(self, sample_test_dataset):
        """Test plotly is available for visualization."""
        code = """
import plotly.express as px
print("Plotly available:", hasattr(px, 'bar'))
print("Can create figure:", hasattr(px, 'Figure') or callable(getattr(px, 'bar', None)))
"""
        result = await execute_custom_analytics_code("test_custom", code)
        assert "Plotly available: True" in result

    async def test_complex_analysis(self, sample_test_dataset):
        """Test complex multi-step analysis."""
        code = """
# Multi-step analysis
print("=== Sales Analysis ===")

# 1. Customer analysis
customer_metrics = df.groupby('customer_id').agg({
    'order_value': ['sum', 'mean', 'count']
}).round(2)
customer_metrics.columns = ['total', 'avg', 'orders']

print("Top customer by total sales:")
top_customer = customer_metrics.sort_values('total', ascending=False).iloc[0]
print(f"Total: ${top_customer['total']}, Avg: ${top_customer['avg']}, Orders: {int(top_customer['orders'])}")

# 2. Category analysis
category_sales = df.groupby('category')['order_value'].sum()
print("Sales by category:")
for cat, sales in category_sales.items():
    print(f"{cat}: ${sales}")

# 3. Regional analysis
region_stats = df.groupby('region').agg({
    'order_value': ['sum', 'count']
}).round(2)
print("Regional performance:")
print(region_stats)
"""
        result = await execute_custom_analytics_code("test_custom", code)
        assert "=== Sales Analysis ===" in result
        assert "Top customer by total sales:" in result
        assert "Sales by category:" in result
        assert "Regional performance:" in result
        assert "$" in result  # Should have dollar amounts

    async def test_syntax_error_handling(self, sample_test_dataset):
        """Test handling of Python syntax errors."""
        result = await execute_custom_analytics_code(
            "test_custom",
            """
print("Starting analysis"
# Missing closing parenthesis - syntax error
for i in range(5)
    print(i)
"""
        )
        # Syntax errors are caught by Python before our try/catch, so they don't have "ERROR:" prefix
        assert ("SyntaxError" in result or "invalid syntax" in result or "was never closed" in result)

    async def test_runtime_error_handling(self, sample_test_dataset):
        """Test handling of runtime errors."""
        result = await execute_custom_analytics_code(
            "test_custom",
            """
print("Before error")
result = 10 / 0  # Division by zero
print("After error - should not appear")
"""
        )
        assert "Before error" in result
        assert "ERROR:" in result
        assert "ZeroDivisionError" in result
        assert "After error - should not appear" not in result

    async def test_large_output_handling(self, sample_test_dataset):
        """Test handling of large output."""
        code = """
# Generate substantial output
for i in range(100):
    print(f"Line {i}: Data value {i * 10}")
print("Completed large output test")
"""
        result = await execute_custom_analytics_code("test_custom", code)
        assert "Line 0: Data value 0" in result
        assert "Line 99: Data value 990" in result
        assert "Completed large output test" in result
        
    async def test_direct_analytics_function(self, sample_test_dataset):
        """Test the underlying analytics function directly."""
        result = await tools.execute_custom_analytics_code(
            "test_custom",
            "print('Direct function call works:', df.shape)"
        )
        assert "Direct function call works:" in result
        assert "(5, 5)" in result