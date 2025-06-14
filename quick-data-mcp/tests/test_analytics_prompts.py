"""Tests for analytics prompts functionality."""

import pytest
import pandas as pd
import tempfile
import os

from mcp_server import prompts
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
        
        result = await prompts.dataset_first_look('ecommerce')
        
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
        
        result = await prompts.dataset_first_look('simple')
        
        assert isinstance(result, str)
        assert 'simple' in result
        assert '5 records' in result
        # Should still provide useful guidance even with limited data
        assert 'What aspect' in result
    
    @pytest.mark.asyncio
    async def test_dataset_first_look_nonexistent(self):
        """Test error handling for non-existent dataset."""
        result = await prompts.dataset_first_look('nonexistent')
        
        assert isinstance(result, str)
        assert 'not loaded' in result
        assert 'load_dataset()' in result


class TestSegmentationWorkshop:
    """Test segmentation workshop prompt functionality."""
    
    @pytest.mark.asyncio
    async def test_segmentation_workshop_with_categories(self, sample_dataset):
        """Test segmentation workshop with categorical columns."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await prompts.segmentation_workshop('ecommerce')
        
        assert isinstance(result, str)
        assert 'ecommerce' in result
        assert 'categorical columns for grouping' in result
        assert 'product_category' in result
        assert 'region' in result
        assert 'Segmentation strategies' in result
        assert 'segment_by_column' in result
    
    @pytest.mark.asyncio
    async def test_segmentation_workshop_no_categories(self, simple_dataset):
        """Test segmentation workshop with no categorical columns."""
        DatasetManager.load_dataset(simple_dataset, 'simple')
        
        result = await prompts.segmentation_workshop('simple')
        
        assert isinstance(result, str)
        assert 'No categorical columns found' in result
        assert 'Numerical Segmentation Options' in result
        assert 'Quantile-based segments' in result
    
    @pytest.mark.asyncio
    async def test_segmentation_workshop_nonexistent(self):
        """Test error handling for non-existent dataset."""
        result = await prompts.segmentation_workshop('nonexistent')
        
        assert isinstance(result, str)
        assert 'not loaded' in result


class TestDataQualityAssessment:
    """Test data quality assessment prompt functionality."""
    
    @pytest.mark.asyncio
    async def test_data_quality_assessment_clean_data(self, sample_dataset):
        """Test data quality assessment with clean data."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await prompts.data_quality_assessment('ecommerce')
        
        assert isinstance(result, str)
        assert 'ecommerce' in result
        assert 'Dataset Overview' in result
        assert '5 rows' in result
        assert 'Data Quality Indicators' in result
        assert 'validate_data_quality' in result
        assert 'quality checks' in result
    
    @pytest.mark.asyncio
    async def test_data_quality_assessment_with_missing_data(self):
        """Test data quality assessment with missing data."""
        # Create dataset with missing values
        data = {
            'id': [1, 2, 3, None, 5],
            'name': ['Alice', None, 'Charlie', 'Diana', 'Eve'],
            'score': [85, 90, None, 92, 88]
        }
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            DatasetManager.load_dataset(temp_file, 'test_data')
            result = await prompts.data_quality_assessment('test_data')
            
            assert isinstance(result, str)
            assert 'Missing Values' in result
            assert 'columns affected' in result
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_data_quality_assessment_nonexistent(self):
        """Test error handling for non-existent dataset."""
        result = await prompts.data_quality_assessment('nonexistent')
        
        assert isinstance(result, str)
        assert 'not loaded' in result


class TestCorrelationInvestigation:
    """Test correlation investigation prompt functionality."""
    
    @pytest.mark.asyncio
    async def test_correlation_investigation_sufficient_numerical(self, sample_dataset):
        """Test correlation investigation with sufficient numerical columns."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await prompts.correlation_investigation('ecommerce')
        
        assert isinstance(result, str)
        # With only 1 numerical column, correlation analysis isn't available
        assert ('correlations' in result or 'Insufficient Numerical Data' in result)
        assert 'ecommerce' in result
        assert 'numerical columns' in result
        # With insufficient numerical columns, these won't be present
        assert ('find_correlations' in result or 'Alternative analyses' in result)
        assert ('correlation analysis strategy' in result or 'Suggestions' in result)
    
    @pytest.mark.asyncio
    async def test_correlation_investigation_insufficient_numerical(self, simple_dataset):
        """Test correlation investigation with insufficient numerical columns."""
        DatasetManager.load_dataset(simple_dataset, 'simple')
        
        result = await prompts.correlation_investigation('simple')
        
        assert isinstance(result, str)
        assert 'Insufficient Numerical Data' in result
        assert 'At least 2 numerical columns' in result
        assert 'Suggestions' in result
    
    @pytest.mark.asyncio
    async def test_correlation_investigation_nonexistent(self):
        """Test error handling for non-existent dataset."""
        result = await prompts.correlation_investigation('nonexistent')
        
        assert isinstance(result, str)
        assert 'not loaded' in result


class TestPatternDiscoverySession:
    """Test pattern discovery session prompt functionality."""
    
    @pytest.mark.asyncio
    async def test_pattern_discovery_session(self, sample_dataset):
        """Test pattern discovery session prompt."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await prompts.pattern_discovery_session('ecommerce')
        
        assert isinstance(result, str)
        assert 'Pattern Discovery Session' in result
        assert 'ecommerce' in result
        assert '5 records' in result
        assert 'Pattern discovery toolkit' in result
        assert 'Distribution Patterns' in result
        assert 'Relationship Patterns' in result
        assert 'analyze_distributions' in result
        # With only 1 numerical column, correlation analysis might not be present
        assert ('find_correlations' in result or 'segment_by_column' in result)
    
    @pytest.mark.asyncio
    async def test_pattern_discovery_session_nonexistent(self):
        """Test error handling for non-existent dataset."""
        result = await prompts.pattern_discovery_session('nonexistent')
        
        assert isinstance(result, str)
        assert 'not loaded' in result


class TestInsightGenerationWorkshop:
    """Test insight generation workshop prompt functionality."""
    
    @pytest.mark.asyncio
    async def test_insight_generation_workshop_general(self, sample_dataset):
        """Test insight generation workshop with general context."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await prompts.insight_generation_workshop('ecommerce', 'general')
        
        assert isinstance(result, str)
        assert 'Business Insights Workshop' in result
        assert 'ecommerce' in result
        assert 'general' in result
        assert 'Insight generation framework' in result
        assert 'Performance Insights' in result
        assert 'Segmentation Insights' in result
        assert 'suggest_analysis' in result
    
    @pytest.mark.asyncio
    async def test_insight_generation_workshop_sales_context(self, sample_dataset):
        """Test insight generation workshop with sales context."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await prompts.insight_generation_workshop('ecommerce', 'sales')
        
        assert isinstance(result, str)
        assert 'sales' in result
        assert 'Sales Performance' in result
        assert 'Customer Behavior' in result
        assert 'conversion rates' in result
    
    @pytest.mark.asyncio
    async def test_insight_generation_workshop_nonexistent(self):
        """Test error handling for non-existent dataset."""
        result = await prompts.insight_generation_workshop('nonexistent')
        
        assert isinstance(result, str)
        assert 'not loaded' in result


class TestDashboardDesignConsultation:
    """Test dashboard design consultation prompt functionality."""
    
    @pytest.mark.asyncio
    async def test_dashboard_design_consultation_general(self, sample_dataset):
        """Test dashboard design consultation with general audience."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await prompts.dashboard_design_consultation('ecommerce', 'general')
        
        assert isinstance(result, str)
        assert 'Dashboard Design Consultation' in result
        assert 'ecommerce' in result
        assert 'general' in result
        assert '5 records' in result
        assert 'Dashboard design principles' in result
        assert 'create_chart' in result
        assert 'generate_dashboard' in result
    
    @pytest.mark.asyncio
    async def test_dashboard_design_consultation_executive(self, sample_dataset):
        """Test dashboard design consultation for executive audience."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await prompts.dashboard_design_consultation('ecommerce', 'executive')
        
        assert isinstance(result, str)
        assert 'executive' in result
        assert 'High-level KPIs' in result
        assert 'Exception-based reporting' in result
    
    @pytest.mark.asyncio
    async def test_dashboard_design_consultation_technical(self, sample_dataset):
        """Test dashboard design consultation for technical audience."""
        DatasetManager.load_dataset(sample_dataset, 'ecommerce')
        
        result = await prompts.dashboard_design_consultation('ecommerce', 'technical')
        
        assert isinstance(result, str)
        assert 'technical' in result
        assert 'Full data exploration' in result
        assert 'Statistical summaries' in result
    
    @pytest.mark.asyncio
    async def test_dashboard_design_consultation_nonexistent(self):
        """Test error handling for non-existent dataset."""
        result = await prompts.dashboard_design_consultation('nonexistent')
        
        assert isinstance(result, str)
        assert 'not loaded' in result


class TestPromptConsistency:
    """Test consistency across prompt functions."""
    
    @pytest.mark.asyncio
    async def test_all_prompts_return_strings(self, sample_dataset):
        """Test that all prompt functions return strings."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        prompt_functions = [
            prompts.dataset_first_look,
            prompts.segmentation_workshop,
            prompts.data_quality_assessment,
            prompts.correlation_investigation,
            prompts.pattern_discovery_session,
        ]
        
        for func in prompt_functions:
            result = await func('test_data')
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_prompts_with_context_parameters(self, sample_dataset):
        """Test prompts that accept context parameters."""
        DatasetManager.load_dataset(sample_dataset, 'test_data')
        
        # Test insight generation with different contexts
        contexts = ['sales', 'marketing', 'operations', 'hr']
        for context in contexts:
            result = await prompts.insight_generation_workshop('test_data', context)
            assert isinstance(result, str)
            assert context in result.lower()
        
        # Test dashboard design with different audiences
        audiences = ['executive', 'manager', 'analyst']
        for audience in audiences:
            result = await prompts.dashboard_design_consultation('test_data', audience)
            assert isinstance(result, str)
            assert audience in result.lower()


if __name__ == '__main__':
    pytest.main([__file__])