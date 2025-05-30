"""Tests for load_dataset tool functionality."""

import pytest
import pandas as pd
import json
import tempfile
import os

from mcp_server.tools.load_dataset_tool import load_dataset
from mcp_server.models.schemas import DatasetManager, loaded_datasets, dataset_schemas


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file for testing."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'category': ['A', 'B', 'A', 'C', 'B'],
        'value': [10.5, 20.0, 15.5, 30.0, 25.5],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
    }
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        yield f.name
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def sample_json_file():
    """Create a temporary JSON file for testing."""
    data = [
        {'id': 1, 'name': 'Alice', 'score': 85, 'department': 'engineering'},
        {'id': 2, 'name': 'Bob', 'score': 90, 'department': 'sales'},
        {'id': 3, 'name': 'Charlie', 'score': 78, 'department': 'engineering'},
        {'id': 4, 'name': 'Diana', 'score': 92, 'department': 'marketing'},
        {'id': 5, 'name': 'Eve', 'score': 88, 'department': 'sales'}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        f.flush()  # Ensure data is written
        temp_file = f.name
    
    yield temp_file
    os.unlink(temp_file)


@pytest.fixture(autouse=True)
def clear_datasets():
    """Clear datasets before and after each test."""
    loaded_datasets.clear()
    dataset_schemas.clear()
    yield
    loaded_datasets.clear()
    dataset_schemas.clear()


class TestLoadDataset:
    """Test load_dataset tool functionality."""
    
    @pytest.mark.asyncio
    async def test_load_csv_dataset(self, sample_csv_file):
        """Test loading a CSV dataset."""
        result = await load_dataset(sample_csv_file, 'test_csv')
        
        assert result["status"] == "loaded"
        assert result["dataset_name"] == "test_csv"
        assert result["rows"] == 5
        assert len(result["columns"]) == 4
        assert result["format"] == "csv"
        assert "test_csv" in loaded_datasets
        assert "test_csv" in dataset_schemas
    
    @pytest.mark.asyncio
    async def test_load_json_dataset(self, sample_json_file):
        """Test loading a JSON dataset."""
        result = await load_dataset(sample_json_file, 'test_json')
        
        assert result["status"] == "loaded"
        assert result["dataset_name"] == "test_json"
        assert result["rows"] == 5
        assert len(result["columns"]) == 4
        assert result["format"] == "json"
        assert "test_json" in loaded_datasets
        assert "test_json" in dataset_schemas
    
    @pytest.mark.asyncio
    async def test_load_dataset_with_sampling(self, sample_csv_file):
        """Test loading a dataset with sampling."""
        result = await load_dataset(sample_csv_file, 'test_sampled', sample_size=3)
        
        assert result["status"] == "loaded"
        assert result["dataset_name"] == "test_sampled"
        assert result["rows"] == 3  # Should be sampled to 3 rows
        assert result["sampled"] == True
        assert result["original_rows"] == 5
        assert "test_sampled" in loaded_datasets
        assert len(loaded_datasets["test_sampled"]) == 3
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_file(self):
        """Test loading a non-existent file."""
        result = await load_dataset('nonexistent.csv', 'test_fail')
        
        assert result["status"] == "error"
        assert "Failed to load dataset" in result["message"]
        assert "test_fail" not in loaded_datasets


if __name__ == '__main__':
    pytest.main([__file__])