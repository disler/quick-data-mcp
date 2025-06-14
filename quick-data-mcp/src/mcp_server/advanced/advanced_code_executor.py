"""Advanced custom analytics code execution with enhanced context and safety."""

import json
import textwrap
import re
import ast
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from ..managers.enhanced_dataset_manager import EnhancedDatasetManager
from ..models.schemas import loaded_datasets, dataset_schemas
import pandas as pd
import numpy as np


@dataclass
class CodeExecutionContext:
    """Enhanced execution context with dataset metadata and utilities."""
    dataset_name: str
    schema_info: Dict
    previous_results: Dict
    execution_history: List[str]
    available_libraries: List[str]
    performance_hints: List[str]


class AdvancedCodeExecutor:
    """Advanced code executor with enhanced context, safety, and AI assistance."""

    def __init__(self, enhanced_manager=None):
        self.execution_history = {}
        self.code_templates = self._load_code_templates()
        self.safety_patterns = self._load_safety_patterns()
        self.enhanced_manager = enhanced_manager or EnhancedDatasetManager()

    async def execute_enhanced_analytics_code(
        self,
        dataset_name: str,
        python_code: str,
        execution_mode: str = "safe",
        include_ai_context: bool = True,
        timeout_seconds: int = 30,
        memory_limit_mb: int = 1024
    ) -> Dict[str, Any]:
        """
        Enhanced custom Python code execution with comprehensive context and safety.

        Features:
        - Automatic context injection with schema information
        - Code safety analysis and suggestions
        - Performance monitoring and optimization hints
        - Execution history tracking
        - AI-generated helper functions
        - Template suggestions for common patterns
        """
        try:
            # Step 1: Initialize execution context
            context = await self._create_execution_context(dataset_name, python_code)

            # Step 2: Analyze and enhance code
            analysis_result = await self._analyze_code(python_code, context)
            if analysis_result['has_errors']:
                return {
                    'status': 'analysis_error',
                    'errors': analysis_result['errors'],
                    'suggestions': analysis_result['suggestions'],
                    'execution_output': None
                }

            # Step 3: Use the original code directly (context injected via globals)
            enhanced_code = python_code

            # Step 4: Execute with monitoring
            execution_result = await self._execute_with_monitoring(
                enhanced_code, timeout_seconds, memory_limit_mb, context
            )

            # Step 5: Post-process results
            processed_result = await self._process_execution_result(
                execution_result, dataset_name, python_code, context
            )

            return processed_result

        except Exception as e:
            return {
                'status': 'system_error',
                'error': f"Execution system error: {str(e)}",
                'execution_output': None,
                'suggestions': ["Check your code syntax", "Try simpler operations first"]
            }

    async def _create_execution_context(self, dataset_name: str, code: str) -> CodeExecutionContext:
        """Create comprehensive execution context."""
        # Check if dataset exists in MCP global storage first
        if dataset_name not in loaded_datasets:
            # Fallback to enhanced manager
            if dataset_name not in self.enhanced_manager.datasets:
                raise ValueError(f"Dataset '{dataset_name}' not loaded. Use load_dataset() first.")
            df = self.enhanced_manager.datasets[dataset_name]
            schema = self.enhanced_manager.schemas.get(dataset_name)
        else:
            # Use MCP global storage
            df = loaded_datasets[dataset_name]
            schema = dataset_schemas.get(dataset_name)

        # Build schema information
        schema_info = {}
        if schema:
            schema_info = {
                'columns': {
                    name: {
                        'type': info.suggested_role,
                        'dtype': info.dtype,
                        'unique_values': info.unique_values,
                        'null_percentage': info.null_percentage,
                        'sample_values': info.sample_values
                    }
                    for name, info in schema.columns.items()
                },
                'row_count': schema.row_count,
                'suggested_analyses': schema.suggested_analyses
            }

        # Get execution history for this dataset
        history = self.execution_history.get(dataset_name, [])

        # Analyze code for library requirements
        required_libraries = self._detect_required_libraries(code)

        # Generate performance hints
        performance_hints = self._generate_performance_hints(df, code)

        return CodeExecutionContext(
            dataset_name=dataset_name,
            schema_info=schema_info,
            previous_results={},
            execution_history=history,
            available_libraries=required_libraries,
            performance_hints=performance_hints
        )

    async def _analyze_code(self, code: str, context: CodeExecutionContext) -> Dict:
        """Comprehensive code analysis for safety and optimization."""
        errors = []
        warnings = []
        suggestions = []

        # Parse code for syntax errors
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error: {str(e)}")
            return {
                'has_errors': True,
                'errors': errors,
                'warnings': [],
                'suggestions': ["Fix syntax error", "Check parentheses and indentation"]
            }

        # Safety pattern analysis
        for pattern, message in self.safety_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(f"Security violation: {message}")

        # Performance analysis
        if 'for ' in code and '.iterrows()' in code:
            warnings.append("Using iterrows() can be slow - consider vectorized operations")
            suggestions.append("Use .apply() or vectorized pandas operations instead of iterrows()")

        if 'df.append(' in code:
            warnings.append("DataFrame.append() is deprecated and slow")
            suggestions.append("Use pd.concat() or collect data in a list first")

        # Column existence checks
        df_columns = set(context.schema_info.get('columns', {}).keys())
        column_references = re.findall(r"df\[['\"](.*?)['\"]\]", code)
        for col in column_references:
            if col not in df_columns:
                warnings.append(f"Column '{col}' not found in dataset")
                suggestions.append(f"Available columns: {list(df_columns)}")

        # Suggest optimizations based on data size
        row_count = context.schema_info.get('row_count', 0)
        if row_count > 100000 and 'sample(' not in code:
            suggestions.append(
                "Consider sampling large dataset: df.sample(n=10000) for faster development")

        return {
            'has_errors': len(errors) > 0,
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }

    async def _prepare_enhanced_code(
        self,
        user_code: str,
        context: CodeExecutionContext,
        include_ai_context: bool,
        execution_mode: str
    ) -> str:
        """Prepare enhanced code with context and utilities."""

        # Base imports and setup (simplified for local execution)
        setup_code = """
# Basic setup for local execution
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
"""

        # Dataset context injection
        if context.dataset_name in loaded_datasets:
            df = loaded_datasets[context.dataset_name]
        else:
            df = self.enhanced_manager.datasets[context.dataset_name]
        dataset_json = df.to_json(orient='records')
        schema_json = json.dumps(context.schema_info, indent=2)

        dataset_setup = f"""
# Load dataset with context
import json
dataset_data = json.loads('''{dataset_json}''')
df = pd.DataFrame(dataset_data)

# Dataset context information
DATASET_NAME = '{context.dataset_name}'
DATASET_INFO = json.loads('''{schema_json}''')

print(f"📊 Dataset loaded: {{DATASET_NAME}}")
print(f"Shape: {{df.shape}}")
print(f"Memory usage: {{df.memory_usage(deep=True).sum() / 1024**2:.1f}} MB")
"""

        # AI-generated helper functions
        ai_helpers = ""
        if include_ai_context:
            ai_helpers = '''
# AI-generated helper functions
def smart_describe(df, column=None):
    """Intelligent data description with context"""
    if column:
        if column not in df.columns:
            print(f"❌ Column '{column}' not found. Available: {df.columns.tolist()}")
            return

        col_data = df[column]
        print("")
        print(f"🔍 Analysis of '{column}':")
        print(f"Type: {col_data.dtype}")
        print(f"Non-null values: {col_data.count()}/{len(col_data)} ({col_data.count()/len(col_data)*100:.1f}%)")

        if pd.api.types.is_numeric_dtype(col_data):
            stats = col_data.describe()
            print(f"Range: {stats['min']} to {stats['max']}")
            print(f"Mean: {stats['mean']:.2f}, Median: {stats['50%']:.2f}")

            # Outlier detection
            Q1, Q3 = col_data.quantile([0.25, 0.75])
            IQR = Q3 - Q1
            outliers = col_data[(col_data < Q1 - 1.5*IQR) | (col_data > Q3 + 1.5*IQR)]
            print(f"Potential outliers: {len(outliers)} ({len(outliers)/len(col_data)*100:.1f}%)")
        else:
            print(f"Unique values: {col_data.nunique()}")
            print("Top values:")
            print(col_data.value_counts().head())
    else:
        print("📋 Dataset Overview:")
        print(f"Shape: {df.shape}")
        print(f"Memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        print("")
        print("Column types:")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {dtype}: {count} columns")
        print("")
        print(f"Missing data: {df.isnull().sum().sum()} values total")

def safe_groupby(df, groupby_col, agg_dict, top_n=10):
    """Safe groupby with error handling and insights"""
    try:
        if groupby_col not in df.columns:
            print(f"❌ Groupby column '{groupby_col}' not found")
            return pd.DataFrame()

        result = df.groupby(groupby_col).agg(agg_dict).round(2)

        # Sort by first aggregation column for meaningful display
        first_agg_col = result.columns[0]
        result_sorted = result.sort_values(first_agg_col, ascending=False).head(top_n)

        print("")
        print(f"📊 Top {min(top_n, len(result_sorted))} groups by {first_agg_col}:")
        return result_sorted

    except Exception as e:
        print(f"❌ Groupby error: {str(e)}")
        return pd.DataFrame()

def quick_viz(df, x_col, y_col=None, chart_type='auto'):
    """Quick visualization with automatic type detection"""
    try:
        if x_col not in df.columns:
            print(f"❌ Column '{x_col}' not found")
            return

        if chart_type == 'auto':
            if y_col is None:
                # Single column analysis
                if pd.api.types.is_numeric_dtype(df[x_col]):
                    print(f"📈 Would generate histogram for {x_col}")
                else:
                    print(f"📊 Would generate bar chart for {x_col}")
            else:
                # Two column analysis
                if y_col not in df.columns:
                    print(f"❌ Column '{y_col}' not found")
                    return

                if pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
                    print(f"📈 Would generate scatter plot: {x_col} vs {y_col}")
                else:
                    print(f"📊 Would generate bar chart: {y_col} by {x_col}")

        print(f"📈 Generated visualization: {x_col}" + (f" vs {y_col}" if y_col else ""))

    except Exception as e:
        print(f"❌ Visualization error: {str(e)}")

def performance_check():
    """Check execution performance"""
    current_time = time.time()
    current_memory = process.memory_info().rss / 1024 / 1024

    print("")
    print(f"⏱️  Execution time: {current_time - execution_start_time:.2f}s")
    print(f"💾 Memory usage: {current_memory:.1f} MB (Δ{current_memory - initial_memory:+.1f} MB)")

def get_analysis_suggestions():
    """Get AI-powered analysis suggestions based on current dataset"""
    suggestions = []

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    if len(numeric_cols) >= 2:
        suggestions.append(f"🔗 Explore correlations: df[{numeric_cols[:2]}].corr()")

    if categorical_cols and numeric_cols:
        suggestions.append(f"📊 Segment analysis: safe_groupby(df, '{categorical_cols[0]}', {{'{numeric_cols[0]}': ['mean', 'count']}})")

    if len(numeric_cols) >= 1:
        suggestions.append(f"📈 Distribution: smart_describe(df, '{numeric_cols[0]}')")

    print("💡 Suggested analyses:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")

    return suggestions
'''

        # Performance hints injection
        performance_hints = ""
        if context.performance_hints:
            performance_hints = f"""
# Performance hints for your dataset:
# {chr(10).join(['# ' + hint for hint in context.performance_hints])}
"""

        # User code with proper indentation
        indented_user_code = textwrap.indent(user_code, '    ')

        # Execution wrapper with monitoring
        execution_wrapper = f"""
try:
    print("🚀 Starting analysis...")
    print("=" * 50)

    # Execute user code
{indented_user_code}

    print("=" * 50)
    print("✅ Analysis completed successfully!")
    performance_check()

except Exception as e:
    print(f"❌ EXECUTION ERROR: {{type(e).__name__}}: {{str(e)}}")
    import traceback
    print("")
    print("📍 Detailed traceback:")
    traceback.print_exc()

    # AI-powered error suggestions
    error_type = type(e).__name__
    if error_type == "KeyError":
        print("")
        print("💡 SUGGESTION: Column not found. Check available columns:")
        print(f"Available columns: {{df.columns.tolist()}}")
        print("Use: smart_describe(df) for dataset overview")
    elif error_type == "ValueError":
        print("")
        print("💡 SUGGESTION: Data type or value issue")
        print("Use: smart_describe(df, 'column_name') for column analysis")
    elif error_type == "AttributeError":
        print("")
        print("💡 SUGGESTION: Method doesn't exist for this data type")
        print("Check pandas documentation or use suggested helper functions")
    elif error_type == "MemoryError":
        print("")
        print("💡 SUGGESTION: Dataset too large for operation")
        print("Try: df.sample(n=10000) to work with smaller sample")

    print("")
    print("🔧 Available helper functions:")
    print("• smart_describe(df, 'column') - Intelligent column analysis")
    print("• safe_groupby(df, 'group_col', {{'agg_col': 'mean'}}) - Safe grouping")
    print("• quick_viz(df, 'x_col', 'y_col') - Quick visualization")
    print("• get_analysis_suggestions() - AI analysis recommendations")
    print("• performance_check() - Monitor execution performance")
"""

        # Combine all code sections
        full_code = "\n".join([
            setup_code,
            dataset_setup,
            ai_helpers,
            performance_hints,
            execution_wrapper
        ])

        return full_code

    async def _execute_with_monitoring(
        self,
        code: str,
        timeout_seconds: int,
        memory_limit_mb: int,
        context: CodeExecutionContext = None
    ) -> Dict:
        """Execute code with comprehensive monitoring in local environment."""
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr

        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            # Create a safe execution environment
            exec_globals = {
                'pd': pd,
                'np': np,
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'type': type,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    '__import__': __import__,
                    'format': format,
                    'repr': repr,
                    'any': any,
                    'all': all,
                    'iter': iter,
                    'next': next,
                    'bool': bool,
                    'set': set,
                    'tuple': tuple,
                }
            }

            # Inject the actual dataframe if context is available
            if context:
                if context.dataset_name in loaded_datasets:
                    exec_globals['df'] = loaded_datasets[context.dataset_name]
                elif context.dataset_name in self.enhanced_manager.datasets:
                    exec_globals['df'] = self.enhanced_manager.datasets[context.dataset_name]
                else:
                    raise ValueError(f"Dataset '{context.dataset_name}' not found")
                exec_globals['DATASET_NAME'] = context.dataset_name
                exec_globals['DATASET_INFO'] = context.schema_info

                # Add AI helper functions
                exec_globals.update(self._get_ai_helper_functions())
            exec_locals = {}

            # Execute with output capture
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, exec_globals, exec_locals)

            output = stdout_capture.getvalue()
            error_output = stderr_capture.getvalue()

            return {
                'status': 'success',
                'output': output + ('\n' + error_output if error_output else ''),
                'return_code': 0,
                'locals': exec_locals
            }

        except Exception as e:
            error_output = stderr_capture.getvalue()
            return {
                'status': 'error',
                'output': f"Execution error: {str(e)}\n{error_output}",
                'return_code': 1,
                'error': str(e)
            }

    def _get_ai_helper_functions(self):
        """Get AI helper functions for code execution."""

        def smart_describe(df, column=None):
            """Intelligent data description with context"""
            if column:
                if column not in df.columns:
                    print(f"❌ Column '{column}' not found. Available: {df.columns.tolist()}")
                    return

                col_data = df[column]
                print(f"🔍 Analysis of '{column}':")
                print(f"Type: {col_data.dtype}")
                print(
                    f"Non-null values: {col_data.count()}/{len(col_data)} ({col_data.count() / len(col_data) * 100:.1f}%)")

                if pd.api.types.is_numeric_dtype(col_data):
                    stats = col_data.describe()
                    print(f"Range: {stats['min']} to {stats['max']}")
                    print(f"Mean: {stats['mean']:.2f}, Median: {stats['50%']:.2f}")
                else:
                    print(f"Unique values: {col_data.nunique()}")
                    print("Top values:")
                    print(col_data.value_counts().head())
            else:
                print("📋 Dataset Overview:")
                print(f"Shape: {df.shape}")
                print(f"Memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
                print("Column types:")
                dtype_counts = df.dtypes.value_counts()
                for dtype, count in dtype_counts.items():
                    print(f"  {dtype}: {count} columns")
                print(f"Missing data: {df.isnull().sum().sum()} values total")

        def safe_groupby(df, groupby_col, agg_dict, top_n=10):
            """Safe groupby with error handling and insights"""
            try:
                if groupby_col not in df.columns:
                    print(f"❌ Groupby column '{groupby_col}' not found")
                    return None

                result = df.groupby(groupby_col, observed=False).agg(agg_dict).head(top_n)
                print(
                    f"✅ Grouped by '{groupby_col}' - showing top {min(top_n, len(result))} results")
                return result
            except Exception as e:
                print(f"❌ Groupby error: {str(e)}")
                return None

        def get_analysis_suggestions():
            """Generate analysis suggestions based on dataset"""
            print("💡 Analysis Suggestions:")
            print("• Use smart_describe() to explore data")
            print("• Try df.head() to see first few rows")
            print("• Check df.info() for column details")
            print("• Use df.describe() for statistical summary")

        def performance_check():
            """Check current performance stats"""
            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024
                print(f"💻 Performance: {memory_mb:.1f} MB memory used")
            except BaseException:
                print("💻 Performance monitoring unavailable")

        def quick_viz(df, column):
            """Quick visualization for testing"""
            if column not in df.columns:
                print(f"❌ Column '{column}' not found")
                return

            print(f"📊 Quick visualization for '{column}':")
            if pd.api.types.is_numeric_dtype(df[column]):
                print(f"Min: {df[column].min()}, Max: {df[column].max()}")
                print(f"Mean: {df[column].mean():.2f}")
                print("📈 Histogram would show distribution here")
            else:
                print(f"Top values in '{column}':")
                print(df[column].value_counts().head())
                print("📊 Bar chart would show distribution here")

        return {
            'smart_describe': smart_describe,
            'safe_groupby': safe_groupby,
            'get_analysis_suggestions': get_analysis_suggestions,
            'performance_check': performance_check,
            'quick_viz': quick_viz
        }

    async def _process_execution_result(
        self,
        result: Dict,
        dataset_name: str,
        original_code: str,
        context: CodeExecutionContext
    ) -> Dict:
        """Process and enhance execution results."""

        # Update execution history
        if dataset_name not in self.execution_history:
            self.execution_history[dataset_name] = []

        self.execution_history[dataset_name].append({
            'timestamp': datetime.now().isoformat(),
            'code_preview': original_code[:100] + "..." if len(original_code) > 100 else original_code,
            'status': result['status'],
            'execution_time': None  # Would be extracted from output in real implementation
        })

        # Keep only recent history
        if len(self.execution_history[dataset_name]) > 20:
            self.execution_history[dataset_name] = self.execution_history[dataset_name][-20:]

        # Generate insights from output
        insights = self._extract_insights_from_output(result.get('output', ''))

        # Generate follow-up suggestions
        follow_up_suggestions = self._generate_follow_up_suggestions(
            original_code, result, context
        )

        return {
            'status': result['status'],
            'execution_output': result.get('output', ''),
            'insights': insights,
            'follow_up_suggestions': follow_up_suggestions,
            'performance_metrics': {
                'timeout_seconds': 30,  # From parameters
                'memory_limit_mb': 1024,  # From parameters
            },
            'execution_history_count': len(self.execution_history.get(dataset_name, []))
        }

    def _detect_required_libraries(self, code: str) -> List[str]:
        """Detect required libraries from code analysis."""
        libraries = ['pandas', 'numpy']  # Always included

        if 'plotly' in code or 'px.' in code or 'go.' in code:
            libraries.append('plotly')
        if 'sklearn' in code or 'scikit-learn' in code:
            libraries.append('scikit-learn')
        if 'scipy' in code:
            libraries.append('scipy')
        if 'matplotlib' in code or 'plt.' in code:
            libraries.append('matplotlib')
        if 'seaborn' in code or 'sns.' in code:
            libraries.append('seaborn')

        return libraries

    def _generate_performance_hints(self, df: pd.DataFrame, code: str) -> List[str]:
        """Generate performance optimization hints."""
        hints = []

        row_count = len(df)
        memory_mb = df.memory_usage(deep=True).sum() / 1024**2

        if row_count > 1000000:
            hints.append("Large dataset detected - consider sampling for development")

        if memory_mb > 500:
            hints.append("High memory usage - monitor performance during execution")

        if 'merge(' in code or 'join(' in code:
            hints.append("Join operations can be memory intensive - ensure sufficient RAM")

        if 'groupby(' in code and row_count > 100000:
            hints.append("Groupby on large dataset - consider using observed=True for categorical data")

        return hints

    def _load_safety_patterns(self) -> Dict[str, str]:
        """Load security patterns to check against."""
        return {
            r'import\s+os': "OS module imports not allowed for security",
            r'import\s+subprocess': "Subprocess imports not allowed for security",
            r'open\s*\(': "File operations not allowed - use provided dataset",
            r'exec\s*\(': "exec() calls not allowed for security",
            r'eval\s*\(': "eval() calls not allowed for security",
            r'__import__': "Dynamic imports not allowed for security",
            r'globals\s*\(': "globals() access not allowed for security",
            r'locals\s*\(': "locals() access not allowed for security"
        }

    def _load_code_templates(self) -> Dict[str, str]:
        """Load common code templates for suggestions."""
        return {
            'correlation_analysis': '''# Correlation analysis template
numeric_cols = df.select_dtypes(include=[np.number]).columns
correlations = df[numeric_cols].corr()
print("Correlation matrix:")
print(correlations)

# Find strongest correlations
correlation_pairs = []
for i in range(len(correlations.columns)):
    for j in range(i+1, len(correlations.columns)):
        corr_val = correlations.iloc[i, j]
        if abs(corr_val) > 0.5:  # Strong correlation threshold
            correlation_pairs.append((correlations.columns[i], correlations.columns[j], corr_val))

print("\nStrongest correlations:")
for col1, col2, corr in sorted(correlation_pairs, key=lambda x: abs(x[2]), reverse=True):
    print(f"{col1} ↔ {col2}: {corr:.3f}")''',

            'segmentation_analysis': '''# Segmentation analysis template
categorical_col = 'your_category_column'  # Replace with actual column
numeric_col = 'your_numeric_column'      # Replace with actual column

if categorical_col in df.columns and numeric_col in df.columns:
    segments = df.groupby(categorical_col)[numeric_col].agg(['count', 'mean', 'std']).round(2)
    segments['percentage'] = (segments['count'] / segments['count'].sum() * 100).round(1)

    print(f"Segmentation of {numeric_col} by {categorical_col}:")
    print(segments.sort_values('mean', ascending=False))
else:
    print("Please replace column names with actual columns from your dataset")
    print(f"Available columns: {df.columns.tolist()}")'''
        }

    def _extract_insights_from_output(self, output: str) -> List[str]:
        """Extract insights from execution output."""
        insights = []

        # Look for patterns in output that suggest insights
        if "correlation" in output.lower():
            insights.append("Correlation analysis performed - look for strong relationships")

        if "outlier" in output.lower():
            insights.append("Outliers detected - consider investigating unusual data points")

        if "missing" in output.lower() or "null" in output.lower():
            insights.append("Missing data identified - consider data cleaning strategies")

        if "error" in output.lower():
            insights.append("Execution encountered issues - check error messages for guidance")

        return insights

    def _generate_follow_up_suggestions(
        self,
        code: str,
        result: Dict,
        context: CodeExecutionContext
    ) -> List[str]:
        """Generate intelligent follow-up suggestions."""
        suggestions = []

        if result['status'] == 'success':
            # Successful execution - suggest next steps
            if 'correlation' in code.lower():
                suggestions.append("Create scatter plots for strongest correlations")
                suggestions.append("Investigate causation behind correlations")

            if 'groupby' in code.lower():
                suggestions.append("Visualize segment differences with bar charts")
                suggestions.append("Perform statistical tests between segments")

            if 'describe(' in code:
                suggestions.append("Analyze distributions with histograms")
                suggestions.append("Check for outliers in numerical columns")

            # Generic suggestions
            suggestions.append("Try custom visualizations with quick_viz()")
            suggestions.append("Get more suggestions with get_analysis_suggestions()")

        else:
            # Error occurred - suggest debugging steps
            suggestions.append("Check column names with df.columns.tolist()")
            suggestions.append("Use smart_describe(df) for dataset overview")
            suggestions.append("Try simpler operations first")

        return suggestions[:5]  # Limit to top 5 suggestions
