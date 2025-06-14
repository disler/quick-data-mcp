"""Test the enhanced advanced code executor."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from mcp_server.advanced.advanced_code_executor import AdvancedCodeExecutor
from mcp_server.managers.enhanced_dataset_manager import EnhancedDatasetManager


@pytest.fixture
def setup_executor():
    """Setup executor with test data."""
    manager = EnhancedDatasetManager()
    executor = AdvancedCodeExecutor(manager)
    
    # Load test dataset
    manager.load_dataset("data/ecommerce_orders.json", "test_data")
    
    return executor, manager


@pytest.mark.asyncio
async def test_basic_code_execution(setup_executor):
    """Test basic code execution functionality."""
    executor, manager = setup_executor
    
    code = """
print("Testing basic execution")
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
"""
    
    result = await executor.execute_enhanced_analytics_code("test_data", code)
    
    assert result["status"] == "success"
    assert "Dataset shape: (15, 8)" in result["execution_output"]
    assert "Columns:" in result["execution_output"]


@pytest.mark.asyncio
async def test_ai_helper_functions(setup_executor):
    """Test AI helper functions."""
    executor, manager = setup_executor
    
    code = """
# Test smart_describe
smart_describe(df, 'order_value')

# Test safe_groupby
result = safe_groupby(df, 'product_category', {'order_value': ['mean', 'count']})

# Test analysis suggestions
get_analysis_suggestions()

# Test performance check
performance_check()
"""
    
    result = await executor.execute_enhanced_analytics_code("test_data", code, include_ai_context=True)
    
    assert result["status"] == "success"
    assert "Analysis of 'order_value'" in result["execution_output"]
    assert "Grouped by 'product_category'" in result["execution_output"]
    assert "Analysis Suggestions" in result["execution_output"]
    assert "Performance:" in result["execution_output"]


@pytest.mark.asyncio
async def test_security_features(setup_executor):
    """Test security and safety features."""
    executor, manager = setup_executor
    
    dangerous_code = """
import os
import subprocess
exec("print('dangerous')")
eval("print('very dangerous')")
"""
    
    result = await executor.execute_enhanced_analytics_code("test_data", dangerous_code)
    
    assert result["status"] == "analysis_error"
    assert "OS module imports not allowed" in str(result["errors"])
    assert "Subprocess imports not allowed" in str(result["errors"])
    assert "exec() calls not allowed" in str(result["errors"])
    assert "eval() calls not allowed" in str(result["errors"])


@pytest.mark.asyncio
async def test_error_handling(setup_executor):
    """Test intelligent error handling."""
    executor, manager = setup_executor
    
    # Test with non-existent column
    code = """
df['nonexistent_column'].mean()
"""
    
    result = await executor.execute_enhanced_analytics_code("test_data", code)
    
    # Should either be an analysis_error or error with helpful message
    assert result["status"] in ["analysis_error", "error"]
    
    # Should provide helpful suggestions (check both possible keys)
    assert "suggestions" in result or "follow_up_suggestions" in result
    suggestions = result.get("suggestions", result.get("follow_up_suggestions", []))
    assert len(suggestions) > 0


@pytest.mark.asyncio
async def test_analytics_workflow(setup_executor):
    """Test complete analytics workflow."""
    executor, manager = setup_executor
    
    workflow_code = """
print("🔍 Complete Analytics Workflow")

# 1. Dataset overview
smart_describe(df)

# 2. Category analysis
category_stats = safe_groupby(df, 'product_category', {
    'order_value': ['mean', 'sum', 'count']
})

# 3. Customer segment analysis
segment_stats = safe_groupby(df, 'customer_segment', {
    'order_value': ['mean', 'count']
})

print("✅ Workflow completed successfully")
"""
    
    result = await executor.execute_enhanced_analytics_code("test_data", workflow_code, include_ai_context=True)
    
    assert result["status"] == "success"
    assert "Complete Analytics Workflow" in result["execution_output"]
    assert "Dataset Overview" in result["execution_output"]
    assert "Grouped by 'product_category'" in result["execution_output"]
    assert "Workflow completed successfully" in result["execution_output"]
    
    # Should generate insights and suggestions
    assert "insights" in result
    assert "follow_up_suggestions" in result


@pytest.mark.asyncio
async def test_performance_monitoring(setup_executor):
    """Test performance monitoring features."""
    executor, manager = setup_executor
    
    code = """
# Test performance monitoring
performance_check()

# Test with some calculations
total_value = df['order_value'].sum()
avg_value = df['order_value'].mean()
print(f"Total: ${total_value:,.2f}, Average: ${avg_value:.2f}")
"""
    
    result = await executor.execute_enhanced_analytics_code("test_data", code, include_ai_context=True)
    
    assert result["status"] == "success"
    assert "Performance:" in result["execution_output"]
    assert "Total:" in result["execution_output"]
    assert "Average:" in result["execution_output"]
    
    # Should have performance metrics
    assert "performance_metrics" in result
    assert "timeout_seconds" in result["performance_metrics"]
    assert "memory_limit_mb" in result["performance_metrics"]


@pytest.mark.asyncio
async def test_dataset_access_validation(setup_executor):
    """Test that executor properly validates dataset access."""
    executor, manager = setup_executor
    
    # Try to access non-existent dataset
    code = "print(df.shape)"
    
    result = await executor.execute_enhanced_analytics_code("nonexistent_dataset", code)
    
    assert result["status"] == "system_error"
    assert "not loaded" in result["error"]


@pytest.mark.asyncio
async def test_execution_history_tracking(setup_executor):
    """Test that execution history is properly tracked."""
    executor, manager = setup_executor
    
    # Execute some code
    code1 = "print('First execution')"
    code2 = "print('Second execution')"
    
    result1 = await executor.execute_enhanced_analytics_code("test_data", code1)
    result2 = await executor.execute_enhanced_analytics_code("test_data", code2)
    
    assert result1["status"] == "success"
    assert result2["status"] == "success"
    
    # Check that history count increases
    assert result1["execution_history_count"] == 1
    assert result2["execution_history_count"] == 2


@pytest.mark.asyncio
async def test_comprehensive_ai_functions(setup_executor):
    """Test all AI helper functions comprehensively."""
    executor, manager = setup_executor
    
    code = """
# Test all AI functions with different scenarios

# 1. Smart describe with specific column (numerical)
smart_describe(df, 'order_value')

# 2. Smart describe with categorical column
smart_describe(df, 'product_category')

# 3. Smart describe full dataset
smart_describe(df)

# 4. Safe groupby with multiple aggregations
result1 = safe_groupby(df, 'region', {
    'order_value': ['mean', 'sum', 'count'],
    'customer_id': 'nunique'
})

# 5. Safe groupby with non-existent column (should handle gracefully)
result2 = safe_groupby(df, 'nonexistent_column', {'order_value': 'mean'})

# 6. Quick visualization test
quick_viz(df, 'order_value')
quick_viz(df, 'product_category')

# 7. Analysis suggestions
get_analysis_suggestions()

# 8. Performance check
performance_check()

print("All AI functions tested successfully")
"""
    
    result = await executor.execute_enhanced_analytics_code("test_data", code, include_ai_context=True)
    
    assert result["status"] == "success"
    assert "Analysis of 'order_value'" in result["execution_output"]
    assert "Analysis of 'product_category'" in result["execution_output"]
    assert "Dataset Overview" in result["execution_output"]
    assert "Grouped by 'region'" in result["execution_output"]
    assert "Groupby column 'nonexistent_column' not found" in result["execution_output"]
    assert "Quick visualization" in result["execution_output"]
    assert "Analysis Suggestions" in result["execution_output"]
    assert "Performance:" in result["execution_output"]
    assert "All AI functions tested successfully" in result["execution_output"]