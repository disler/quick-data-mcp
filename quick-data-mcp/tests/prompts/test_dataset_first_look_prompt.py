"""Tests for dataset first look prompt functionality."""

import pytest
import pandas as pd
import tempfile
import os

from mcp_server.prompts.dataset_first_look_prompt import dataset_first_look
from mcp_server.models.schemas import DatasetManager, loaded_datasets, dataset_schemas


@pytest.fixture
def sample_dataset():
    """Create a sample dataset for testing."""
    data = {
        'order_id': ['ord_001', 'ord_002', 'ord_003', 'ord_004', 'ord_005'],
        'customer_id': ['cust_123', 'cust_124', 'cust_125', 'cust_126', 'cust_127'],
        'product_category': ['electronics', 'books', 'clothing', 'electronics', 'home_garden'],
        'order_value': [299.99, 29.99, 89.50, 599.99, 149.99],
        'order_date': ['2024-11-15', '2024-11-14', '2024-11-13', '2024-11-12', '2024-11-11'],
        'region': ['west_coast', 'midwest', 'east_coast', 'west_coast', 'south'],
        'customer_segment': ['premium', 'standard', 'premium', 'premium', 'standard']
    }
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        yield f.name
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def simple_dataset():
    """Create a simple dataset with limited columns for testing edge cases."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
    }
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        yield f.name
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture(autouse=True)
def clear_datasets():
    """Clear datasets before and after each test."""
    loaded_datasets.clear()
    dataset_schemas.clear()
    yield
    loaded_datasets.clear()
    dataset_schemas.clear()


class TestDatasetFirstLook:
    """Test dataset first look prompt functionality."""
    
    @pytest.mark.asyncio
    async def test_dataset_first_look_comprehensive(self, sample_dataset):
        """Test first look prompt with comprehensive dataset."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await dataset_first_look('ecommerce')
        
        assert isinstance(result, str)
        assert 'ecommerce' in result
        assert '5 records' in result
        assert 'columns' in result
        assert '📊 Numerical columns' in result
        assert '🏷️ Categorical columns' in result
        # Date columns might be detected as identifiers if all dates are unique
        assert ('📅 Date/Time columns' in result or '🔑 Identifier columns' in result)
        assert '🎯 Recommended starting points' in result
        assert 'find_correlations' in result or 'segment_by_column' in result
    
    @pytest.mark.asyncio
    async def test_dataset_first_look_simple(self, simple_dataset):
        """Test first look prompt with simple dataset."""
        DatasetManager.load_dataset(simple_dataset, 'simple')
        
        result = await dataset_first_look('simple')
        
        assert isinstance(result, str)
        assert 'simple' in result
        assert '5 records' in result
        # Should still provide useful guidance even with limited data
        assert 'What aspect' in result
    
    @pytest.mark.asyncio
    async def test_dataset_first_look_nonexistent(self):
        """Test error handling for non-existent dataset."""
        result = await dataset_first_look('nonexistent')
        
        assert isinstance(result, str)
        assert 'not loaded' in result
        assert 'load_dataset()' in result


if __name__ == '__main__':
    pytest.main([__file__])