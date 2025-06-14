"""Comprehensive tests for AdvancedCodeExecutor."""

import pytest
import pandas as pd
import json
from unittest.mock import AsyncMock, patch, MagicMock
from src.mcp_server.advanced.advanced_code_executor import AdvancedCodeExecutor, CodeExecutionContext
from src.mcp_server.models.schemas import DatasetManager, DatasetSchema, ColumnInfo


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'department': ['IT', 'HR', 'IT', 'Finance', 'HR']
    })


@pytest.fixture
def mock_dataset_manager(sample_dataframe):
    """Mock DatasetManager for testing."""
    with patch.object(DatasetManager, 'get_dataset', return_value=sample_dataframe):
        yield


@pytest.fixture
def mock_dataset_schema():
    """Mock dataset schema for testing."""
    schema = DatasetSchema(
        name='test_dataset',
        columns={
            'id': ColumnInfo(name='id', dtype='int64', unique_values=5, 
                           null_percentage=0.0, sample_values=[1, 2, 3], suggested_role='identifier'),
            'name': ColumnInfo(name='name', dtype='object', unique_values=5, 
                             null_percentage=0.0, sample_values=['Alice', 'Bob', 'Charlie'], suggested_role='categorical'),
            'age': ColumnInfo(name='age', dtype='int64', unique_values=5, 
                            null_percentage=0.0, sample_values=[25, 30, 35], suggested_role='numerical'),
            'salary': ColumnInfo(name='salary', dtype='int64', unique_values=5, 
                               null_percentage=0.0, sample_values=[50000, 60000, 70000], suggested_role='numerical'),
            'department': ColumnInfo(name='department', dtype='object', unique_values=3, 
                                   null_percentage=0.0, sample_values=['IT', 'HR', 'Finance'], suggested_role='categorical')
        },
        row_count=5,
        suggested_analyses=['correlation_analysis', 'segmentation_analysis']
    )
    
    with patch('src.mcp_server.advanced.advanced_code_executor.dataset_schemas', {'test_dataset': schema}):
        yield schema


class TestAdvancedCodeExecutor:
    """Test suite for AdvancedCodeExecutor."""
    
    def test_init(self):
        """Test executor initialization."""
        executor = AdvancedCodeExecutor()
        
        assert isinstance(executor.execution_history, dict)
        assert isinstance(executor.code_templates, dict)
        assert isinstance(executor.safety_patterns, dict)
        assert len(executor.safety_patterns) > 0
        assert len(executor.code_templates) > 0
    
    @pytest.mark.asyncio
    async def test_create_execution_context(self, mock_dataset_manager, mock_dataset_schema, sample_dataframe):
        """Test execution context creation."""
        executor = AdvancedCodeExecutor()
        
        context = await executor._create_execution_context('test_dataset', 'print(df.head())')
        
        assert isinstance(context, CodeExecutionContext)
        assert context.dataset_name == 'test_dataset'
        assert 'columns' in context.schema_info
        assert context.schema_info['row_count'] == 5
        assert 'pandas' in context.available_libraries
        assert 'numpy' in context.available_libraries
        assert isinstance(context.performance_hints, list)
    
    @pytest.mark.asyncio
    async def test_analyze_code_syntax_error(self, mock_dataset_manager, mock_dataset_schema):
        """Test code analysis with syntax error."""
        executor = AdvancedCodeExecutor()
        context = await executor._create_execution_context('test_dataset', 'invalid syntax(')
        
        result = await executor._analyze_code('invalid syntax(', context)
        
        assert result['has_errors'] is True
        assert len(result['errors']) > 0
        assert 'syntax error' in result['errors'][0].lower()
    
    @pytest.mark.asyncio
    async def test_analyze_code_security_violations(self, mock_dataset_manager, mock_dataset_schema):
        """Test code analysis with security violations."""
        executor = AdvancedCodeExecutor()
        context = await executor._create_execution_context('test_dataset', 'import os')
        
        result = await executor._analyze_code('import os', context)
        
        assert result['has_errors'] is True
        assert any('security violation' in error.lower() for error in result['errors'])
    
    @pytest.mark.asyncio
    async def test_analyze_code_performance_warnings(self, mock_dataset_manager, mock_dataset_schema):
        """Test code analysis with performance warnings."""
        executor = AdvancedCodeExecutor()
        context = await executor._create_execution_context('test_dataset', 'for index, row in df.iterrows(): pass')
        
        result = await executor._analyze_code('for index, row in df.iterrows(): pass', context)
        
        assert result['has_errors'] is False
        assert len(result['warnings']) > 0
        assert any('iterrows' in warning for warning in result['warnings'])
        assert len(result['suggestions']) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_code_column_check(self, mock_dataset_manager, mock_dataset_schema):
        """Test code analysis with column existence check."""
        executor = AdvancedCodeExecutor()
        context = await executor._create_execution_context('test_dataset', 'print(df["nonexistent_column"])')
        
        result = await executor._analyze_code('print(df["nonexistent_column"])', context)
        
        assert result['has_errors'] is False
        assert len(result['warnings']) > 0
        assert any('column' in warning.lower() and 'not found' in warning.lower() for warning in result['warnings'])
    
    @pytest.mark.asyncio
    async def test_prepare_enhanced_code(self, mock_dataset_manager, mock_dataset_schema, sample_dataframe):
        """Test enhanced code preparation."""
        executor = AdvancedCodeExecutor()
        context = await executor._create_execution_context('test_dataset', 'print(df.head())')
        
        enhanced_code = await executor._prepare_enhanced_code(
            'print(df.head())', context, include_ai_context=True, execution_mode='safe'
        )
        
        assert 'import pandas as pd' in enhanced_code
        assert 'import numpy as np' in enhanced_code
        assert 'smart_describe' in enhanced_code
        assert 'safe_groupby' in enhanced_code
        assert 'quick_viz' in enhanced_code
        assert 'performance_check' in enhanced_code
        assert 'print(df.head())' in enhanced_code
        assert 'Dataset loaded:' in enhanced_code
    
    @pytest.mark.asyncio
    async def test_execute_with_monitoring_success(self):
        """Test successful code execution with monitoring."""
        executor = AdvancedCodeExecutor()
        
        # Mock successful subprocess execution
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b'Success output', b'')
        mock_process.returncode = 0
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('asyncio.wait_for', return_value=(b'Success output', b'')):
                result = await executor._execute_with_monitoring('print("test")', 30, 1024)
        
        assert result['status'] == 'success'
        assert result['output'] == 'Success output'
        assert result['return_code'] == 0
    
    @pytest.mark.asyncio
    async def test_execute_with_monitoring_timeout(self):
        """Test code execution timeout."""
        executor = AdvancedCodeExecutor()
        
        # Mock timeout
        mock_process = AsyncMock()
        mock_process.kill = AsyncMock()
        mock_process.wait = AsyncMock()
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError()):
                result = await executor._execute_with_monitoring('while True: pass', 1, 1024)
        
        assert result['status'] == 'timeout'
        assert 'timed out' in result['output']
        assert result['return_code'] == -1
        mock_process.kill.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_execution_result(self, mock_dataset_manager, mock_dataset_schema):
        """Test execution result processing."""
        executor = AdvancedCodeExecutor()
        context = await executor._create_execution_context('test_dataset', 'print(df.head())')
        
        execution_result = {
            'status': 'success',
            'output': 'DataFrame output with correlation analysis',
            'return_code': 0
        }
        
        processed_result = await executor._process_execution_result(
            execution_result, 'test_dataset', 'print(df.head())', context
        )
        
        assert processed_result['status'] == 'success'
        assert 'DataFrame output with correlation analysis' in processed_result['execution_output']
        assert isinstance(processed_result['insights'], list)
        assert isinstance(processed_result['follow_up_suggestions'], list)
        assert 'performance_metrics' in processed_result
        assert 'execution_history_count' in processed_result
        
        # Check execution history was updated
        assert 'test_dataset' in executor.execution_history
        assert len(executor.execution_history['test_dataset']) == 1
    
    @pytest.mark.asyncio
    async def test_full_execution_workflow_success(self, mock_dataset_manager, mock_dataset_schema, sample_dataframe):
        """Test the complete execution workflow."""
        executor = AdvancedCodeExecutor()
        
        # Mock successful subprocess execution
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b'Analysis completed successfully!', b'')
        mock_process.returncode = 0
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('asyncio.wait_for', return_value=(b'Analysis completed successfully!', b'')):
                result = await executor.execute_enhanced_analytics_code(
                    dataset_name='test_dataset',
                    python_code='print(df.describe())',
                    execution_mode='safe',
                    include_ai_context=True,
                    timeout_seconds=30
                )
        
        assert result['status'] == 'success'
        assert 'execution_output' in result
        assert isinstance(result['insights'], list)
        assert isinstance(result['follow_up_suggestions'], list)
        assert 'performance_metrics' in result
    
    @pytest.mark.asyncio
    async def test_full_execution_workflow_analysis_error(self, mock_dataset_manager, mock_dataset_schema):
        """Test execution workflow with analysis errors."""
        executor = AdvancedCodeExecutor()
        
        result = await executor.execute_enhanced_analytics_code(
            dataset_name='test_dataset',
            python_code='invalid syntax(',
            execution_mode='safe',
            include_ai_context=True,
            timeout_seconds=30
        )
        
        assert result['status'] == 'analysis_error'
        assert len(result['errors']) > 0
        assert result['execution_output'] is None
        assert isinstance(result['suggestions'], list)
    
    def test_detect_required_libraries(self):
        """Test library detection from code."""
        executor = AdvancedCodeExecutor()
        
        # Test basic libraries (always included)
        libs = executor._detect_required_libraries('print(df.head())')
        assert 'pandas' in libs
        assert 'numpy' in libs
        
        # Test plotly detection
        libs = executor._detect_required_libraries('px.scatter(df, x="col1", y="col2")')
        assert 'plotly' in libs
        
        # Test sklearn detection
        libs = executor._detect_required_libraries('from sklearn.linear_model import LinearRegression')
        assert 'scikit-learn' in libs
        
        # Test matplotlib detection
        libs = executor._detect_required_libraries('plt.plot(x, y)')
        assert 'matplotlib' in libs
    
    def test_generate_performance_hints(self):
        """Test performance hint generation."""
        executor = AdvancedCodeExecutor()
        
        # Test with small dataset
        small_df = pd.DataFrame({'col1': [1, 2, 3]})
        hints = executor._generate_performance_hints(small_df, 'df.groupby("col1").sum()')
        assert len(hints) == 0  # No hints for small dataset
        
        # Test with large dataset
        large_df = pd.DataFrame({'col1': range(2000000)})
        hints = executor._generate_performance_hints(large_df, 'df.groupby("col1").sum()')
        assert len(hints) > 0
        assert any('large dataset' in hint.lower() for hint in hints)
    
    def test_extract_insights_from_output(self):
        """Test insight extraction from execution output."""
        executor = AdvancedCodeExecutor()
        
        # Test correlation insight
        output = "Correlation analysis shows strong relationship between variables"
        insights = executor._extract_insights_from_output(output)
        assert any('correlation' in insight.lower() for insight in insights)
        
        # Test outlier insight
        output = "Found 5 outliers in the dataset"
        insights = executor._extract_insights_from_output(output)
        assert any('outlier' in insight.lower() for insight in insights)
        
        # Test missing data insight
        output = "Missing values detected in column X"
        insights = executor._extract_insights_from_output(output)
        assert any('missing' in insight.lower() for insight in insights)
    
    def test_generate_follow_up_suggestions(self, mock_dataset_manager, mock_dataset_schema):
        """Test follow-up suggestion generation."""
        executor = AdvancedCodeExecutor()
        
        # Mock context
        context = CodeExecutionContext(
            dataset_name='test_dataset',
            schema_info={},
            previous_results={},
            execution_history=[],
            available_libraries=['pandas', 'numpy'],
            performance_hints=[]
        )
        
        # Test successful correlation analysis
        result = {'status': 'success'}
        suggestions = executor._generate_follow_up_suggestions('df.corr()', result, context)
        assert len(suggestions) > 0
        assert any('scatter plot' in suggestion.lower() for suggestion in suggestions)
        
        # Test error case
        result = {'status': 'error'}
        suggestions = executor._generate_follow_up_suggestions('invalid code', result, context)
        assert len(suggestions) > 0
        assert any('column' in suggestion.lower() for suggestion in suggestions)
    
    def test_safety_patterns_loaded(self):
        """Test that safety patterns are properly loaded."""
        executor = AdvancedCodeExecutor()
        
        patterns = executor.safety_patterns
        assert len(patterns) > 0
        assert any('os' in pattern for pattern in patterns.keys())
        assert any('subprocess' in pattern for pattern in patterns.keys())
        assert any('exec' in pattern for pattern in patterns.keys())
        assert any('eval' in pattern for pattern in patterns.keys())
    
    def test_code_templates_loaded(self):
        """Test that code templates are properly loaded."""
        executor = AdvancedCodeExecutor()
        
        templates = executor.code_templates
        assert len(templates) > 0
        assert 'correlation_analysis' in templates
        assert 'segmentation_analysis' in templates
        assert 'correlation' in templates['correlation_analysis']
        assert 'groupby' in templates['segmentation_analysis']


class TestCodeExecutionContext:
    """Test suite for CodeExecutionContext dataclass."""
    
    def test_context_creation(self):
        """Test CodeExecutionContext creation."""
        context = CodeExecutionContext(
            dataset_name='test',
            schema_info={'columns': {}},
            previous_results={},
            execution_history=[],
            available_libraries=['pandas'],
            performance_hints=['hint1']
        )
        
        assert context.dataset_name == 'test'
        assert isinstance(context.schema_info, dict)
        assert isinstance(context.previous_results, dict)
        assert isinstance(context.execution_history, list)
        assert isinstance(context.available_libraries, list)
        assert isinstance(context.performance_hints, list)


if __name__ == '__main__':
    pytest.main([__file__])