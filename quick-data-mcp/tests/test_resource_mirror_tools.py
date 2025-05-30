"""Tests for resource mirror tools that provide tool-only client compatibility."""

import pytest
import sys
from mcp_server.server import (
    resource_datasets_loaded,
    resource_datasets_schema,
    resource_datasets_summary,
    resource_datasets_sample,
    resource_analytics_current_dataset,
    resource_analytics_available_analyses,
    resource_analytics_column_types,
    resource_analytics_suggested_insights,
    resource_analytics_memory_usage,
    resource_config_server,
    resource_users_profile,
    resource_system_status
)
from mcp_server.resources import data_resources
from mcp_server.models.schemas import DatasetManager


@pytest.mark.asyncio
class TestResourceMirrorTools:
    """Test resource mirror tools provide identical functionality to resources."""
    
    async def test_resource_datasets_loaded_matches_resource(self):
        """Ensure tool matches resource output for loaded datasets."""
        # Test both empty and loaded states
        tool_result = await resource_datasets_loaded()
        resource_result = await data_resources.get_loaded_datasets()
        
        assert tool_result == resource_result
        assert "datasets" in tool_result
        assert "total_datasets" in tool_result
        assert "status" in tool_result
        assert isinstance(tool_result["datasets"], list)

    async def test_resource_config_server_matches_resource(self):
        """Ensure tool matches resource output for server config."""
        tool_result = await resource_config_server()
        resource_result = await data_resources.get_server_config()
        
        assert tool_result == resource_result
        assert "name" in tool_result
        assert "version" in tool_result
        assert "analytics_features" in tool_result
        assert isinstance(tool_result["analytics_features"], list)

    async def test_resource_users_profile_matches_resource(self):
        """Ensure tool matches resource output for user profiles."""
        user_id = "test123"
        
        tool_result = await resource_users_profile(user_id)
        resource_result = await data_resources.get_user_profile(user_id)
        
        assert tool_result == resource_result
        assert tool_result["id"] == user_id
        assert "name" in tool_result
        assert "email" in tool_result
        assert "preferences" in tool_result

    async def test_resource_system_status_matches_resource(self):
        """Ensure tool matches resource output for system status."""
        tool_result = await resource_system_status()
        resource_result = await data_resources.get_system_status()
        
        assert tool_result == resource_result
        assert tool_result["status"] == "healthy"
        assert "features" in tool_result
        assert "dependencies" in tool_result

    async def test_resource_analytics_current_dataset_matches_resource(self):
        """Ensure tool matches resource output for current dataset."""
        tool_result = await resource_analytics_current_dataset()
        resource_result = await data_resources.get_current_dataset()
        
        assert tool_result == resource_result
        # Should handle both empty and loaded states
        assert "status" in tool_result or "current_dataset" in tool_result

    async def test_resource_analytics_memory_usage_matches_resource(self):
        """Ensure tool matches resource output for memory usage."""
        tool_result = await resource_analytics_memory_usage()
        resource_result = await data_resources.get_memory_usage()
        
        assert tool_result == resource_result
        assert "datasets" in tool_result
        assert "total_memory_mb" in tool_result
        assert isinstance(tool_result["datasets"], list)

    async def test_resource_analytics_available_analyses_matches_resource(self):
        """Ensure tool matches resource output for available analyses."""
        tool_result = await resource_analytics_available_analyses()
        resource_result = await data_resources.get_available_analyses(None)
        
        assert tool_result == resource_result

    async def test_resource_analytics_column_types_matches_resource(self):
        """Ensure tool matches resource output for column types."""
        tool_result = await resource_analytics_column_types()
        resource_result = await data_resources.get_column_types(None)
        
        assert tool_result == resource_result

    async def test_resource_analytics_suggested_insights_matches_resource(self):
        """Ensure tool matches resource output for suggested insights."""
        tool_result = await resource_analytics_suggested_insights()
        resource_result = await data_resources.get_analysis_suggestions(None)
        
        assert tool_result == resource_result

    async def test_all_resource_tools_available(self):
        """Verify all 12 resource mirror tools are implemented and callable."""
        expected_tools = [
            "resource_datasets_loaded",
            "resource_datasets_schema", 
            "resource_datasets_summary",
            "resource_datasets_sample",
            "resource_analytics_current_dataset",
            "resource_analytics_available_analyses",
            "resource_analytics_column_types", 
            "resource_analytics_suggested_insights",
            "resource_analytics_memory_usage",
            "resource_config_server",
            "resource_users_profile",
            "resource_system_status"
        ]
        
        # Get current module
        current_module = sys.modules[__name__]
        
        # Verify all tools exist and are callable
        for tool_name in expected_tools:
            # Check in the server module
            from mcp_server import server
            assert hasattr(server, tool_name), f"Tool {tool_name} not found in server module"
            tool_func = getattr(server, tool_name)
            assert callable(tool_func), f"Tool {tool_name} is not callable"

    async def test_resource_tools_parameter_validation(self):
        """Test parameter validation for tools that require parameters."""
        # Test tools that require dataset_name parameter
        dataset_tools = [
            (resource_datasets_schema, "nonexistent_dataset"),
            (resource_datasets_summary, "nonexistent_dataset"), 
            (resource_datasets_sample, "nonexistent_dataset")
        ]
        
        for tool_func, invalid_dataset in dataset_tools:
            result = await tool_func(invalid_dataset)
            # Should return error for nonexistent dataset
            assert "error" in result
            assert "not loaded" in result["error"].lower()

        # Test user profile tool with different user IDs
        user_profiles = await resource_users_profile("unique_test_id")
        assert user_profiles["id"] == "unique_test_id"

    async def test_dataset_specific_tools_with_loaded_data(self):
        """Test dataset-specific tools when datasets are loaded."""
        # First check if any datasets are loaded
        datasets_result = await resource_datasets_loaded()
        loaded_datasets_list = datasets_result.get("datasets", [])
        
        if not loaded_datasets_list:
            # Skip this test if no datasets are loaded
            pytest.skip("No datasets loaded for testing dataset-specific tools")
            return
        
        # Use the first loaded dataset for testing
        dataset_name = loaded_datasets_list[0]["name"]
        
        # Test schema tool
        schema_result = await resource_datasets_schema(dataset_name)
        assert "dataset_name" in schema_result
        assert schema_result["dataset_name"] == dataset_name
        assert "columns_by_type" in schema_result
        
        # Test summary tool
        summary_result = await resource_datasets_summary(dataset_name)
        assert "dataset_name" in summary_result
        assert summary_result["dataset_name"] == dataset_name
        assert "shape" in summary_result
        
        # Test sample tool
        sample_result = await resource_datasets_sample(dataset_name)
        assert "dataset_name" in sample_result
        assert sample_result["dataset_name"] == dataset_name
        assert "sample_data" in sample_result
        assert isinstance(sample_result["sample_data"], list)

    async def test_error_handling_consistency(self):
        """Verify error handling is consistent between tools and resources."""
        # Test with invalid dataset name
        invalid_dataset = "definitely_nonexistent_dataset_12345"
        
        # Schema tools
        tool_error = await resource_datasets_schema(invalid_dataset)
        resource_error = await data_resources.get_dataset_schema(invalid_dataset)
        assert tool_error == resource_error
        assert "error" in tool_error
        
        # Summary tools
        tool_error = await resource_datasets_summary(invalid_dataset)
        resource_error = await data_resources.get_dataset_summary(invalid_dataset)
        assert tool_error == resource_error
        assert "error" in tool_error
        
        # Sample tools
        tool_error = await resource_datasets_sample(invalid_dataset)
        resource_error = await data_resources.get_dataset_sample(invalid_dataset, 5)
        assert tool_error == resource_error
        assert "error" in tool_error

    async def test_data_structure_consistency(self):
        """Verify data structures returned by tools match exactly."""
        # Test user profile structure
        user_id = "structure_test"
        profile = await resource_users_profile(user_id)
        
        required_fields = ["id", "name", "email", "status", "preferences"]
        for field in required_fields:
            assert field in profile, f"Missing field {field} in user profile"
        
        # Test preferences structure
        prefs = profile["preferences"]
        pref_fields = ["theme", "notifications", "language"]
        for field in pref_fields:
            assert field in prefs, f"Missing preference field {field}"

    async def test_memory_usage_tool_output_format(self):
        """Test memory usage tool returns properly formatted data."""
        memory_result = await resource_analytics_memory_usage()
        
        assert "datasets" in memory_result
        assert "total_memory_mb" in memory_result
        assert "dataset_count" in memory_result
        assert "memory_recommendations" in memory_result
        
        # Check datasets list structure
        datasets = memory_result["datasets"]
        assert isinstance(datasets, list)
        
        # If datasets exist, check their structure
        for dataset in datasets:
            required_fields = ["dataset", "memory_mb", "rows", "columns"]
            for field in required_fields:
                assert field in dataset, f"Missing field {field} in dataset memory info"

    async def test_loaded_datasets_tool_output_format(self):
        """Test loaded datasets tool returns properly formatted data."""
        datasets_result = await resource_datasets_loaded()
        
        assert "datasets" in datasets_result
        assert "total_datasets" in datasets_result
        assert "total_memory_mb" in datasets_result
        assert "status" in datasets_result
        
        # Check datasets list structure
        datasets = datasets_result["datasets"]
        assert isinstance(datasets, list)
        
        # If datasets exist, check their structure  
        for dataset in datasets:
            required_fields = ["name", "rows", "columns", "memory_mb"]
            for field in required_fields:
                assert field in dataset, f"Missing field {field} in dataset info"