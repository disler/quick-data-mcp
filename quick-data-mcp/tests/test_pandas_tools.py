"""Tests for pandas tools functionality."""

import pytest
import pandas as pd
import json
import tempfile
import os
from pathlib import Path

from mcp_server.tools import pandas_tools
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
    
    # Cleanup
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
    """Test dataset loading functionality."""
    
    @pytest.mark.asyncio
    async def test_load_csv_dataset(self, sample_csv_file):
        """Test loading a CSV dataset."""
        result = await pandas_tools.load_dataset(sample_csv_file, 'test_csv')
        
        assert result['status'] == 'loaded'
        assert result['dataset_name'] == 'test_csv'
        assert result['rows'] == 5
        assert len(result['columns']) == 4
        assert 'test_csv' in loaded_datasets
        assert 'test_csv' in dataset_schemas
    
    @pytest.mark.asyncio
    async def test_load_json_dataset(self, sample_json_file):
        """Test loading a JSON dataset."""
        result = await pandas_tools.load_dataset(sample_json_file, 'test_json')
        
        assert result['status'] == 'loaded'
        assert result['dataset_name'] == 'test_json'
        assert result['rows'] == 5
        assert len(result['columns']) == 4
        assert 'test_json' in loaded_datasets
        assert 'test_json' in dataset_schemas
    
    @pytest.mark.asyncio
    async def test_load_with_sampling(self, sample_csv_file):
        """Test loading dataset with sampling."""
        result = await pandas_tools.load_dataset(sample_csv_file, 'test_sample', sample_size=3)
        
        assert result['status'] == 'loaded'
        assert result['rows'] == 3
        assert result['sampled'] is True
        assert result['original_rows'] == 5
    
    @pytest.mark.asyncio
    async def test_load_unsupported_format(self):
        """Test error handling for unsupported file format."""
        result = await pandas_tools.load_dataset('test.txt', 'test_unsupported')
        
        assert result['status'] == 'error'
        assert 'Unsupported file format' in result['message']


class TestListLoadedDatasets:
    """Test dataset listing functionality."""
    
    @pytest.mark.asyncio
    async def test_list_empty_datasets(self):
        """Test listing when no datasets are loaded."""
        result = await pandas_tools.list_loaded_datasets()
        
        assert result['loaded_datasets'] == []
        assert result['total_datasets'] == 0
        assert result['total_memory_mb'] == 0
    
    @pytest.mark.asyncio
    async def test_list_loaded_datasets(self, sample_csv_file):
        """Test listing loaded datasets."""
        await pandas_tools.load_dataset(sample_csv_file, 'test1')
        await pandas_tools.load_dataset(sample_csv_file, 'test2')
        
        result = await pandas_tools.list_loaded_datasets()
        
        assert len(result['loaded_datasets']) == 2
        assert result['total_datasets'] == 2
        assert result['total_memory_mb'] >= 0  # Small datasets might have 0.0 MB
        
        dataset_names = [ds['name'] for ds in result['loaded_datasets']]
        assert 'test1' in dataset_names
        assert 'test2' in dataset_names


class TestSegmentByColumn:
    """Test segmentation functionality."""
    
    @pytest.mark.asyncio
    async def test_segment_by_categorical_column(self, sample_csv_file):
        """Test segmentation by categorical column."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.segment_by_column('test_data', 'category')
        
        assert result['dataset'] == 'test_data'
        assert result['segmented_by'] == 'category'
        assert result['segment_count'] > 0
        assert 'segments' in result
        assert result['total_rows'] == 5
    
    @pytest.mark.asyncio
    async def test_segment_nonexistent_column(self, sample_csv_file):
        """Test error handling for non-existent column."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.segment_by_column('test_data', 'nonexistent')
        
        assert 'error' in result
        assert 'not found' in result['error']
    
    @pytest.mark.asyncio
    async def test_segment_nonexistent_dataset(self):
        """Test error handling for non-existent dataset."""
        result = await pandas_tools.segment_by_column('nonexistent', 'column')
        
        assert 'error' in result


class TestFindCorrelations:
    """Test correlation analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_find_correlations_auto_columns(self, sample_csv_file):
        """Test correlation analysis with automatic column selection."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.find_correlations('test_data')
        
        assert result['dataset'] == 'test_data'
        assert 'correlation_matrix' in result
        assert 'strong_correlations' in result
        assert 'columns_analyzed' in result
    
    @pytest.mark.asyncio
    async def test_find_correlations_specified_columns(self, sample_csv_file):
        """Test correlation analysis with specified columns."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.find_correlations('test_data', ['id', 'value'])
        
        assert result['dataset'] == 'test_data'
        assert len(result['columns_analyzed']) == 2
        assert 'id' in result['columns_analyzed']
        assert 'value' in result['columns_analyzed']
    
    @pytest.mark.asyncio
    async def test_find_correlations_insufficient_columns(self, sample_json_file):
        """Test error handling when insufficient numerical columns."""
        # Create dataset with only one numerical column
        data = [{'id': i, 'name': f'name_{i}'} for i in range(5)]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_file = f.name
        
        try:
            await pandas_tools.load_dataset(temp_file, 'test_data')
            result = await pandas_tools.find_correlations('test_data')
            
            assert 'error' in result
            assert 'Need at least 2 numerical columns' in result['error']
        finally:
            os.unlink(temp_file)


class TestCreateChart:
    """Test chart creation functionality."""
    
    @pytest.mark.asyncio
    async def test_create_histogram(self, sample_csv_file):
        """Test creating a histogram chart."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.create_chart('test_data', 'histogram', 'value')
        
        assert result['dataset'] == 'test_data'
        assert result['chart_type'] == 'histogram'
        assert result['status'] == 'success'
        assert 'chart_config' in result
    
    @pytest.mark.asyncio
    async def test_create_bar_chart(self, sample_csv_file):
        """Test creating a bar chart."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.create_chart('test_data', 'bar', 'category', 'value')
        
        assert result['dataset'] == 'test_data'
        assert result['chart_type'] == 'bar'
        assert result['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_create_scatter_plot(self, sample_csv_file):
        """Test creating a scatter plot."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.create_chart('test_data', 'scatter', 'id', 'value')
        
        assert result['dataset'] == 'test_data'
        assert result['chart_type'] == 'scatter'
        assert result['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_create_chart_missing_column(self, sample_csv_file):
        """Test error handling for missing columns."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.create_chart('test_data', 'bar', 'nonexistent')
        
        assert 'error' in result
        assert 'not found' in result['error']
    
    @pytest.mark.asyncio
    async def test_create_chart_unsupported_type(self, sample_csv_file):
        """Test error handling for unsupported chart type."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.create_chart('test_data', 'unsupported', 'value')
        
        assert 'error' in result
        assert 'Unsupported chart type' in result['error']


class TestAnalyzeDistributions:
    """Test distribution analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_analyze_numerical_distribution(self, sample_csv_file):
        """Test analyzing numerical column distribution."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.analyze_distributions('test_data', 'value')
        
        assert result['dataset'] == 'test_data'
        assert result['column'] == 'value'
        assert result['distribution_type'] == 'numerical'
        assert 'mean' in result
        assert 'std' in result
        assert 'quartiles' in result
    
    @pytest.mark.asyncio
    async def test_analyze_categorical_distribution(self, sample_csv_file):
        """Test analyzing categorical column distribution."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.analyze_distributions('test_data', 'category')
        
        assert result['dataset'] == 'test_data'
        assert result['column'] == 'category'
        assert result['distribution_type'] == 'categorical'
        assert 'most_frequent' in result
        assert 'top_10_values' in result
    
    @pytest.mark.asyncio
    async def test_analyze_distribution_missing_column(self, sample_csv_file):
        """Test error handling for missing column."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.analyze_distributions('test_data', 'nonexistent')
        
        assert 'error' in result
        assert 'not found' in result['error']


class TestDetectOutliers:
    """Test outlier detection functionality."""
    
    @pytest.mark.asyncio
    async def test_detect_outliers_iqr_method(self, sample_csv_file):
        """Test outlier detection using IQR method."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.detect_outliers('test_data', method='iqr')
        
        assert result['dataset'] == 'test_data'
        assert result['method'] == 'iqr'
        assert 'outliers_by_column' in result
        assert 'total_outliers' in result
    
    @pytest.mark.asyncio
    async def test_detect_outliers_zscore_method(self, sample_csv_file):
        """Test outlier detection using Z-score method."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.detect_outliers('test_data', method='zscore')
        
        assert result['dataset'] == 'test_data'
        assert result['method'] == 'zscore'
        assert 'outliers_by_column' in result
    
    @pytest.mark.asyncio
    async def test_detect_outliers_unsupported_method(self, sample_csv_file):
        """Test error handling for unsupported outlier detection method."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.detect_outliers('test_data', method='unsupported')
        
        assert 'error' in result
        assert 'Unsupported method' in result['error']


class TestSuggestAnalysis:
    """Test analysis suggestion functionality."""
    
    @pytest.mark.asyncio
    async def test_suggest_analysis(self, sample_csv_file):
        """Test generating analysis suggestions."""
        await pandas_tools.load_dataset(sample_csv_file, 'test_data')
        
        result = await pandas_tools.suggest_analysis('test_data')
        
        assert result['dataset_name'] == 'test_data'
        assert 'suggestions' in result
        assert 'dataset_summary' in result
        assert isinstance(result['suggestions'], list)
    
    @pytest.mark.asyncio
    async def test_suggest_analysis_nonexistent_dataset(self):
        """Test error handling for non-existent dataset."""
        result = await pandas_tools.suggest_analysis('nonexistent')
        
        assert 'error' in result
        assert 'not loaded' in result['error']


if __name__ == '__main__':
    pytest.main([__file__])