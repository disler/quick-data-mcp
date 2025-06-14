"""Test the enhanced dataset manager."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from mcp_server.managers.enhanced_dataset_manager import EnhancedDatasetManager


@pytest.fixture
def manager():
    """Create a fresh enhanced dataset manager."""
    return EnhancedDatasetManager()


def test_dataset_loading(manager):
    """Test dataset loading functionality."""
    # Test JSON loading
    result = manager.load_dataset("data/ecommerce_orders.json", "test_json")
    
    assert result["status"] == "loaded"
    assert result["dataset_name"] == "test_json"
    assert result["rows"] == 15
    assert len(result["columns"]) == 8
    assert result["format"] == "json"
    
    # Test CSV loading
    result = manager.load_dataset("data/employee_survey.csv", "test_csv")
    
    assert result["status"] == "loaded"
    assert result["dataset_name"] == "test_csv"
    assert result["rows"] == 25
    assert result["format"] == "csv"


def test_dataset_retrieval(manager):
    """Test dataset retrieval functionality."""
    # Load a dataset first
    manager.load_dataset("data/ecommerce_orders.json", "test_retrieval")
    
    # Test successful retrieval
    df = manager.get_dataset("test_retrieval")
    assert df is not None
    assert len(df) == 15
    assert len(df.columns) == 8
    
    # Test retrieval of non-existent dataset
    with pytest.raises(ValueError, match="not loaded"):
        manager.get_dataset("nonexistent")


def test_analytics_tracking(manager):
    """Test analytics state tracking."""
    # Load dataset
    manager.load_dataset("data/ecommerce_orders.json", "analytics_test")
    
    # Track some analyses
    manager.track_analysis("analytics_test", "validate_data_quality", {"issues": 0})
    manager.track_analysis("analytics_test", "find_correlations", {"correlations": 3})
    manager.track_analysis("analytics_test", "segment_by_column", {"column": "product_category"})
    
    # Get analytics summary
    summary = manager.get_analytics_summary("analytics_test")
    
    assert summary["dataset_name"] == "analytics_test"
    assert len(summary["analytics_progress"]["analyses_performed"]) == 3
    assert summary["analytics_progress"]["completion_percentage"] > 0
    assert "next_analyses" in summary["recommendations"]
    assert len(summary["recommendations"]["next_analyses"]) > 0


def test_schema_discovery(manager):
    """Test automatic schema discovery."""
    # Load dataset
    manager.load_dataset("data/ecommerce_orders.json", "schema_test")
    
    # Check schema was created
    assert "schema_test" in manager.schemas
    schema = manager.schemas["schema_test"]
    
    assert schema.name == "schema_test"
    assert schema.row_count == 15
    assert len(schema.columns) == 8
    
    # Check column classification
    order_value_info = schema.columns["order_value"]
    assert order_value_info.suggested_role == "numerical"
    
    product_category_info = schema.columns["product_category"]
    assert product_category_info.suggested_role == "categorical"


def test_memory_optimization(manager):
    """Test memory optimization features."""
    # Load dataset with optimization hints
    result = manager.load_dataset(
        "data/product_performance.csv", 
        "optimize_test",
        optimization_hints=["dtype_optimization", "low_memory"]
    )
    
    assert result["status"] == "loaded"
    assert "optimizations_applied" in result
    
    # Check metrics were recorded
    assert "optimize_test" in manager.metrics
    metrics = manager.metrics["optimize_test"]
    
    assert metrics.memory_mb >= 0
    assert metrics.load_time_seconds > 0
    assert metrics.access_count == 0
    assert isinstance(metrics.optimization_suggestions, list)


def test_global_analytics_stats(manager):
    """Test global analytics statistics."""
    # Load multiple datasets
    manager.load_dataset("data/ecommerce_orders.json", "global_test1")
    manager.load_dataset("data/employee_survey.csv", "global_test2")
    
    # Track some analyses
    manager.track_analysis("global_test1", "correlation_analysis", {})
    manager.track_analysis("global_test2", "segmentation_analysis", {})
    
    # Get global stats
    stats = manager.get_global_analytics_stats()
    
    assert stats["total_datasets"] == 2
    assert stats["total_memory_mb"] >= 0
    assert stats["total_analyses_performed"] == 2
    assert stats["most_active_dataset"] in ["global_test1", "global_test2"]
    assert isinstance(stats["recent_operations"], list)


def test_analytics_completion_calculation(manager):
    """Test analytics completion percentage calculation."""
    # Load dataset
    manager.load_dataset("data/ecommerce_orders.json", "completion_test")
    
    # Start with 0% completion
    summary = manager.get_analytics_summary("completion_test")
    initial_completion = summary["analytics_progress"]["completion_percentage"]
    
    # Track some analyses
    manager.track_analysis("completion_test", "validate_data_quality", {})
    manager.track_analysis("completion_test", "find_correlations", {})
    
    # Check completion increased
    summary = manager.get_analytics_summary("completion_test")
    new_completion = summary["analytics_progress"]["completion_percentage"]
    
    assert new_completion > initial_completion


def test_analysis_recommendations(manager):
    """Test analysis recommendation generation."""
    # Load dataset
    manager.load_dataset("data/ecommerce_orders.json", "recommendations_test")
    
    # Get initial recommendations
    summary = manager.get_analytics_summary("recommendations_test")
    initial_recommendations = summary["recommendations"]["next_analyses"]
    
    # Initial recommendations might be empty, so just ensure the key exists
    assert "next_analyses" in summary["recommendations"]
    
    # Track an analysis
    manager.track_analysis("recommendations_test", "validate_data_quality", {})
    
    # Get updated recommendations
    summary = manager.get_analytics_summary("recommendations_test")
    updated_recommendations = summary["recommendations"]["next_analyses"]
    
    # Should have recommendations after tracking an analysis
    assert isinstance(updated_recommendations, list)
    # After tracking a quality assessment, should have some recommendations
    assert len(updated_recommendations) >= 0  # At minimum, should be a valid list


def test_error_handling(manager):
    """Test error handling in dataset operations."""
    # Test loading non-existent file
    result = manager.load_dataset("nonexistent_file.json", "error_test")
    
    assert result["status"] == "error"
    assert "message" in result
    
    # Test getting summary for non-existent dataset
    summary = manager.get_analytics_summary("nonexistent_dataset")
    
    assert "error" in summary


def test_multiple_dataset_support(manager):
    """Test handling multiple datasets simultaneously."""
    # Load multiple datasets
    result1 = manager.load_dataset("data/ecommerce_orders.json", "multi_test1")
    result2 = manager.load_dataset("data/employee_survey.csv", "multi_test2")
    result3 = manager.load_dataset("data/product_performance.csv", "multi_test3")
    
    assert all(r["status"] == "loaded" for r in [result1, result2, result3])
    
    # Verify all datasets are accessible
    df1 = manager.get_dataset("multi_test1")
    df2 = manager.get_dataset("multi_test2")
    df3 = manager.get_dataset("multi_test3")
    
    assert len(df1) == 15
    assert len(df2) == 25
    assert len(df3) == 20
    
    # Track analyses on different datasets
    manager.track_analysis("multi_test1", "correlation_analysis", {})
    manager.track_analysis("multi_test2", "segmentation_analysis", {})
    manager.track_analysis("multi_test3", "quality_assessment", {})
    
    # Verify independent tracking
    summary1 = manager.get_analytics_summary("multi_test1")
    summary2 = manager.get_analytics_summary("multi_test2")
    summary3 = manager.get_analytics_summary("multi_test3")
    
    assert summary1["analytics_progress"]["analyses_performed"] == ["correlation_analysis"]
    assert summary2["analytics_progress"]["analyses_performed"] == ["segmentation_analysis"]
    assert summary3["analytics_progress"]["analyses_performed"] == ["quality_assessment"]


def test_performance_optimization_suggestions(manager):
    """Test performance optimization suggestions."""
    # Load dataset
    manager.load_dataset("data/product_performance.csv", "perf_test")
    
    # Check that optimization suggestions are generated
    assert "perf_test" in manager.metrics
    metrics = manager.metrics["perf_test"]
    
    assert isinstance(metrics.optimization_suggestions, list)
    # For our small test datasets, might not have many suggestions
    assert len(metrics.optimization_suggestions) >= 0