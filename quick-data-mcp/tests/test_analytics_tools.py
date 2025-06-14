"""Tests for analytics tools functionality."""

import pytest
import pandas as pd
import json
import tempfile
import os

from mcp_server import tools
from mcp_server.models.schemas import DatasetManager, loaded_datasets, dataset_schemas


@pytest.fixture
def sample_dataset():
    """Create a sample dataset for testing."""
    data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C'],
        'value': [10, 20, 15, 30, 25, 12, 35, 22, 18, 28],
        'score': [85, 90, 78, 92, 88, 82, 95, 89, 76, 91],
        'status': ['active', 'active', 'inactive', 'active', 'active', 'inactive', 'active', 'active', 'inactive', 'active']
    }
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        yield f.name
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def sample_dataset_with_missing():
    """Create a sample dataset with missing values for testing."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', None, 'Diana', 'Eve'],
        'score': [85, None, 78, 92, 88],
        'category': ['A', 'B', 'A', None, 'B']
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


class TestValidateDataQuality:
    """Test data quality validation functionality."""
    
    @pytest.mark.asyncio
    async def test_validate_clean_data(self, sample_dataset):
        """Test data quality validation on clean data."""
        # Load dataset first
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        result = await tools.validate_data_quality('test_data')
        
        assert result['dataset_name'] == 'test_data'
        assert result['total_rows'] == 10
        assert result['total_columns'] == 5
        assert isinstance(result['quality_score'], float)
        assert result['quality_score'] >= 0
        assert result['quality_score'] <= 100
        assert isinstance(result['potential_issues'], list)
        assert isinstance(result['recommendations'], list)
    
    @pytest.mark.asyncio
    async def test_validate_data_with_missing_values(self, sample_dataset_with_missing):
        """Test data quality validation on data with missing values."""
        DatasetManager.load_dataset(sample_dataset_with_missing, 'test_data')
        
        result = await tools.validate_data_quality('test_data')
        
        assert result['dataset_name'] == 'test_data'
        assert len(result['missing_data']) > 0  # Should detect missing values
        # Check that missing data was detected (either in issues or missing_data dict)
        assert len(result['missing_data']) > 0 or any('missing' in issue.lower() for issue in result['potential_issues'])
    
    @pytest.mark.asyncio
    async def test_validate_nonexistent_dataset(self):
        """Test error handling for non-existent dataset."""
        result = await tools.validate_data_quality('nonexistent')
        
        assert 'error' in result


class TestCompareDatasets:
    """Test dataset comparison functionality."""
    
    @pytest.mark.asyncio
    async def test_compare_datasets(self, sample_dataset):
        """Test comparing two datasets."""
        # Load same dataset with different names
        DatasetManager.load_dataset(sample_dataset, 'dataset_a')
        DatasetManager.load_dataset(sample_dataset, 'dataset_b')
        
        result = await tools.compare_datasets('dataset_a', 'dataset_b')
        
        assert result['dataset_a'] == 'dataset_a'
        assert result['dataset_b'] == 'dataset_b'
        assert 'shape_comparison' in result
        assert 'common_columns' in result
        assert 'column_comparisons' in result
    
    @pytest.mark.asyncio
    async def test_compare_datasets_with_specified_columns(self, sample_dataset):
        """Test comparing datasets with specified common columns."""
        DatasetManager.load_dataset(sample_dataset, 'dataset_a')
        DatasetManager.load_dataset(sample_dataset, 'dataset_b')
        
        result = await tools.compare_datasets('dataset_a', 'dataset_b', ['id', 'value'])
        
        assert len(result['common_columns']) == 2
        assert 'id' in result['common_columns']
        assert 'value' in result['common_columns']
    
    @pytest.mark.asyncio
    async def test_compare_nonexistent_datasets(self):
        """Test error handling for non-existent datasets."""
        result = await tools.compare_datasets('nonexistent_a', 'nonexistent_b')
        
        assert 'error' in result


class TestMergeDatasets:
    """Test dataset merging functionality."""
    
    @pytest.mark.asyncio
    async def test_merge_datasets_concatenation(self, sample_dataset):
        """Test merging datasets by concatenation."""
        DatasetManager.load_dataset(sample_dataset, 'dataset_a')
        DatasetManager.load_dataset(sample_dataset, 'dataset_b')
        
        dataset_configs = [
            {'dataset_name': 'dataset_a'},
            {'dataset_name': 'dataset_b'}
        ]
        
        result = await tools.merge_datasets(dataset_configs, 'inner')
        
        assert result['merge_strategy'] == 'inner'
        assert len(result['datasets_merged']) == 2
        assert 'merged_dataset_name' in result
        assert result['status'] == 'success'
        
        # Check that merged dataset was created
        merged_name = result['merged_dataset_name']
        assert merged_name in loaded_datasets
    
    @pytest.mark.asyncio
    async def test_merge_datasets_with_join_column(self, sample_dataset):
        """Test merging datasets with a join column."""
        DatasetManager.load_dataset(sample_dataset, 'dataset_a')
        DatasetManager.load_dataset(sample_dataset, 'dataset_b')
        
        dataset_configs = [
            {'dataset_name': 'dataset_a'},
            {'dataset_name': 'dataset_b', 'join_column': 'id'}
        ]
        
        result = await tools.merge_datasets(dataset_configs, 'inner')
        
        assert 'merge_steps' in result
        assert len(result['merge_steps']) > 0
        assert result['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_merge_insufficient_datasets(self):
        """Test error handling for insufficient datasets."""
        dataset_configs = [{'dataset_name': 'dataset_a'}]
        
        result = await tools.merge_datasets(dataset_configs)
        
        assert 'error' in result
        assert 'Need at least 2 datasets' in result['error']


class TestGenerateDashboard:
    """Test dashboard generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_dashboard_empty_configs(self, sample_dataset):
        """Test error handling for empty chart configurations."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        result = await tools.generate_dashboard('test_data', [])
        
        assert 'error' in result
        assert 'No chart configurations' in result['error']
    
    @pytest.mark.asyncio
    async def test_generate_dashboard_with_charts(self, sample_dataset):
        """Test generating dashboard with chart configurations."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        chart_configs = [
            {
                'chart_type': 'bar',
                'x_column': 'category',
                'y_column': 'value',
                'title': 'Value by Category'
            },
            {
                'chart_type': 'histogram',
                'x_column': 'score',
                'title': 'Score Distribution'
            }
        ]
        
        result = await tools.generate_dashboard('test_data', chart_configs)
        
        assert result['dataset'] == 'test_data'
        assert 'charts' in result
        assert 'summary' in result
        assert len(result['charts']) == 2


class TestExportInsights:
    """Test insights export functionality."""
    
    @pytest.mark.asyncio
    async def test_export_insights_json(self, sample_dataset):
        """Test exporting insights in JSON format."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        result = await tools.export_insights('test_data', 'json')
        
        assert result['dataset'] == 'test_data'
        assert result['export_format'] == 'json'
        assert result['status'] == 'success'
        assert 'export_file' in result
        
        # Check if file was created
        if result.get('export_file'):
            assert os.path.exists(result['export_file'])
            # Cleanup
            os.unlink(result['export_file'])
    
    @pytest.mark.asyncio
    async def test_export_insights_csv(self, sample_dataset):
        """Test exporting insights in CSV format."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        result = await tools.export_insights('test_data', 'csv')
        
        assert result['dataset'] == 'test_data'
        assert result['export_format'] == 'csv'
        assert result['status'] == 'success'
        
        # Cleanup
        if result.get('export_file') and os.path.exists(result['export_file']):
            os.unlink(result['export_file'])
    
    @pytest.mark.asyncio
    async def test_export_insights_html(self, sample_dataset):
        """Test exporting insights in HTML format."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        result = await tools.export_insights('test_data', 'html')
        
        assert result['dataset'] == 'test_data'
        assert result['export_format'] == 'html'
        assert result['status'] == 'success'
        
        # Cleanup
        if result.get('export_file') and os.path.exists(result['export_file']):
            os.unlink(result['export_file'])
    
    @pytest.mark.asyncio
    async def test_export_insights_unsupported_format(self, sample_dataset):
        """Test error handling for unsupported export format."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        result = await tools.export_insights('test_data', 'unsupported')
        
        assert 'error' in result
        assert 'Unsupported export format' in result['error']
    
    @pytest.mark.asyncio
    async def test_export_insights_nonexistent_dataset(self):
        """Test error handling for non-existent dataset."""
        result = await tools.export_insights('nonexistent', 'json')
        
        assert 'error' in result
        assert 'not loaded' in result['error']


class TestCalculateFeatureImportance:
    """Test feature importance calculation functionality."""
    
    @pytest.mark.asyncio
    async def test_calculate_feature_importance(self, sample_dataset):
        """Test calculating feature importance."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        result = await tools.calculate_feature_importance('test_data', 'score')
        
        assert result['dataset'] == 'test_data'
        assert result['target_column'] == 'score'
        assert result['method'] == 'correlation_based'
        assert 'feature_importance' in result
        assert 'top_features' in result
    
    @pytest.mark.asyncio
    async def test_calculate_feature_importance_missing_target(self, sample_dataset):
        """Test error handling for missing target column."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        result = await tools.calculate_feature_importance('test_data', 'nonexistent')
        
        assert 'error' in result
        assert 'not found' in result['error']
    
    @pytest.mark.asyncio
    async def test_calculate_feature_importance_no_numerical_features(self):
        """Test error handling when no numerical features are available."""
        # Create dataset with only categorical columns
        data = {
            'id': ['a', 'b', 'c', 'd', 'e'],
            'category': ['A', 'B', 'A', 'C', 'B'],
            'status': ['active', 'inactive', 'active', 'active', 'inactive']
        }
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            DatasetManager.load_dataset(temp_file, 'test_data')
            result = await tools.calculate_feature_importance('test_data', 'category')
            
            assert 'error' in result
        finally:
            os.unlink(temp_file)


class TestMemoryOptimizationReport:
    """Test memory optimization reporting functionality."""
    
    @pytest.mark.asyncio
    async def test_memory_optimization_report(self, sample_dataset):
        """Test generating memory optimization report."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        result = await tools.memory_optimization_report('test_data')
        
        assert result['dataset'] == 'test_data'
        assert 'current_memory_usage' in result
        assert 'optimization_suggestions' in result
        assert 'potential_savings' in result
        assert 'recommendations' in result
        
        assert 'total_mb' in result['current_memory_usage']
        assert 'per_column_kb' in result['current_memory_usage']
    
    @pytest.mark.asyncio
    async def test_memory_optimization_nonexistent_dataset(self):
        """Test error handling for non-existent dataset."""
        result = await tools.memory_optimization_report('nonexistent')
        
        assert 'error' in result


if __name__ == '__main__':
    pytest.main([__file__])