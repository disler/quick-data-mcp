"""Tests for list_mcp_assets prompt functionality."""

import pytest

from mcp_server.prompts.list_mcp_assets_prompt import list_mcp_assets


class TestListMcpAssets:
    """Test list_mcp_assets prompt functionality."""
    
    @pytest.mark.asyncio
    async def test_list_mcp_assets_returns_string(self):
        """Test that list_mcp_assets returns a string."""
        result = await list_mcp_assets()
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_list_mcp_assets_contains_sections(self):
        """Test that the output contains the expected sections."""
        result = await list_mcp_assets()
        
        # Check for main sections
        assert "## 📝 Prompts" in result
        assert "## 🔧 Tools" in result
        assert "## 📊 Resources" in result
    
    @pytest.mark.asyncio
    async def test_list_mcp_assets_contains_key_prompts(self):
        """Test that key prompts are listed."""
        result = await list_mcp_assets()
        
        # Check for some key prompts
        assert "dataset_first_look" in result
        assert "find_datasources" in result
        assert "segmentation_workshop" in result
        assert "data_quality_assessment" in result
    
    @pytest.mark.asyncio
    async def test_list_mcp_assets_contains_key_tools(self):
        """Test that key tools are listed."""
        result = await list_mcp_assets()
        
        # Check for some key tools
        assert "load_dataset" in result
        assert "create_chart" in result
        assert "analyze_distributions" in result
        assert "execute_custom_analytics_code" in result
        assert "validate_data_quality" in result
    
    @pytest.mark.asyncio
    async def test_list_mcp_assets_contains_key_resources(self):
        """Test that key resources are listed."""
        result = await list_mcp_assets()
        
        # Check for some key resources
        assert "datasets://loaded" in result
        assert "analytics://current_dataset" in result
        assert "config://server" in result
        assert "system://status" in result
    
    @pytest.mark.asyncio
    async def test_list_mcp_assets_formatting(self):
        """Test that the output is properly formatted."""
        result = await list_mcp_assets()
        
        # Check for markdown formatting
        assert result.startswith("# ")  # Should start with main heading
        assert "🚀" in result  # Should have emoji
        assert "•" in result  # Should have bullet points
        assert "**" in result  # Should have bold formatting
        
        # Check for quick start section
        assert "🎯 Quick Start:" in result
        assert "💡 Pro Tips:" in result
    
    @pytest.mark.asyncio
    async def test_list_mcp_assets_subsections(self):
        """Test that tool subsections are present."""
        result = await list_mcp_assets()
        
        # Check for tool subsections
        assert "### Dataset Management" in result
        assert "### Analysis Tools" in result
        assert "### Visualization" in result
        assert "### Advanced Analytics" in result
        assert "### Resource Mirror Tools" in result
        
        # Check for resource subsections
        assert "### Dataset Resources" in result
        assert "### Analytics Resources" in result
        assert "### System Resources" in result


if __name__ == '__main__':
    pytest.main([__file__])