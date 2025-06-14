"""Enhanced DatasetManager with analytics state tracking and optimization."""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import pandas as pd
import numpy as np


@dataclass
class ColumnInfo:
    """Column metadata and characteristics."""
    name: str
    dtype: str
    unique_values: int
    null_percentage: float
    sample_values: List[Any]
    suggested_role: str  # 'categorical', 'numerical', 'temporal', 'identifier'

    @classmethod
    def from_series(cls, series: pd.Series, name: str) -> 'ColumnInfo':
        """Auto-discover column characteristics from pandas Series."""

        # Determine suggested role
        if pd.api.types.is_numeric_dtype(series):
            role = 'numerical'
        elif pd.api.types.is_datetime64_any_dtype(series):
            role = 'temporal'
        elif series.nunique() / len(series) < 0.5:  # Low cardinality = categorical
            role = 'categorical'
        elif series.nunique() == len(series):  # Unique values = identifier
            role = 'identifier'
        else:
            role = 'categorical'

        return cls(
            name=name,
            dtype=str(series.dtype),
            unique_values=series.nunique(),
            null_percentage=series.isnull().mean() * 100,
            sample_values=series.dropna().head(3).tolist(),
            suggested_role=role
        )


@dataclass
class DatasetSchema:
    """Dynamically discovered dataset schema."""
    name: str
    columns: Dict[str, ColumnInfo]
    row_count: int
    suggested_analyses: List[str]

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, name: str) -> 'DatasetSchema':
        """Auto-discover schema from pandas DataFrame."""
        columns = {}
        for col in df.columns:
            columns[col] = ColumnInfo.from_series(df[col], col)

        # Generate analysis suggestions based on column types
        suggestions = []
        numerical_cols = [
            col for col,
            info in columns.items() if info.suggested_role == 'numerical']
        categorical_cols = [
            col for col,
            info in columns.items() if info.suggested_role == 'categorical']
        temporal_cols = [col for col, info in columns.items() if info.suggested_role == 'temporal']

        if len(numerical_cols) >= 2:
            suggestions.append("correlation_analysis")
        if categorical_cols:
            suggestions.append("segmentation_analysis")
        if temporal_cols:
            suggestions.append("time_series_analysis")

        return cls(
            name=name,
            columns=columns,
            row_count=len(df),
            suggested_analyses=suggestions
        )


@dataclass
class AnalyticsState:
    """Track analytics operations performed on a dataset."""
    dataset_name: str
    analyses_performed: List[str] = field(default_factory=list)
    correlations_calculated: bool = False
    quality_assessed: bool = False
    distributions_analyzed: List[str] = field(default_factory=list)
    segments_created: List[str] = field(default_factory=list)
    charts_generated: List[Dict] = field(default_factory=list)
    custom_code_runs: int = 0
    last_analysis: Optional[datetime] = None
    analysis_recommendations: List[str] = field(default_factory=list)


@dataclass
class DatasetMetrics:
    """Performance and usage metrics for a dataset."""
    memory_mb: float
    load_time_seconds: float
    access_count: int
    last_accessed: datetime
    analysis_count: int
    optimization_suggestions: List[str] = field(default_factory=list)


class EnhancedDatasetManager:
    """Enhanced dataset manager with analytics state tracking and optimization."""

    def __init__(self):
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.schemas: Dict[str, DatasetSchema] = {}
        self.analytics_state: Dict[str, AnalyticsState] = {}
        self.metrics: Dict[str, DatasetMetrics] = {}
        self.analysis_history: List[Dict] = []

    def load_dataset(
        self,
        file_path: str,
        dataset_name: str,
        optimization_hints: Optional[List[str]] = None
    ) -> dict:
        """Enhanced dataset loading with optimization and state tracking."""
        import time
        start_time = time.time()

        try:
            # Determine format and load
            if file_path.endswith('.json'):
                df = pd.read_json(file_path)
                file_format = 'json'
            elif file_path.endswith('.csv'):
                # Enhanced CSV loading with optimization hints
                load_kwargs = {}
                if optimization_hints:
                    if 'low_memory' in optimization_hints:
                        load_kwargs['low_memory'] = False
                    if 'dtype_optimization' in optimization_hints:
                        try:
                            import pyarrow
                            load_kwargs['dtype_backend'] = 'pyarrow'
                        except ImportError:
                            # Pyarrow not available, skip this optimization
                            pass

                df = pd.read_csv(file_path, **load_kwargs)
                file_format = 'csv'
            else:
                raise ValueError(f"Unsupported file format: {file_path}")

            # Apply memory optimizations
            df_optimized = self._optimize_dataframe(df, optimization_hints or [])

            # Store dataset and metadata
            self.datasets[dataset_name] = df_optimized
            schema = DatasetSchema.from_dataframe(df_optimized, dataset_name)
            self.schemas[dataset_name] = schema

            # Initialize analytics state
            self.analytics_state[dataset_name] = AnalyticsState(dataset_name=dataset_name)

            # Calculate metrics
            load_time = time.time() - start_time
            memory_usage = df_optimized.memory_usage(deep=True).sum() / 1024**2

            self.metrics[dataset_name] = DatasetMetrics(
                memory_mb=memory_usage,
                load_time_seconds=load_time,
                access_count=0,
                last_accessed=datetime.now(),
                analysis_count=0,
                optimization_suggestions=self._generate_optimization_suggestions(df_optimized)
            )

            # Log the operation
            self._log_operation('load_dataset', dataset_name, {
                'file_path': file_path,
                'rows': len(df_optimized),
                'columns': len(df_optimized.columns),
                'memory_mb': memory_usage,
                'load_time_seconds': load_time
            })

            return {
                "status": "loaded",
                "dataset_name": dataset_name,
                "rows": len(df_optimized),
                "columns": list(df_optimized.columns),
                "format": file_format,
                "memory_usage": f"{memory_usage:.1f} MB",
                "load_time": f"{load_time:.2f}s",
                "optimizations_applied": len(self.metrics[dataset_name].optimization_suggestions),
                "suggested_analyses": schema.suggested_analyses
            }

        except Exception as e:
            self._log_operation('load_dataset_error', dataset_name, {'error': str(e)})
            return {
                "status": "error",
                "message": f"Failed to load dataset: {str(e)}"
            }

    def get_dataset(self, dataset_name: str) -> pd.DataFrame:
        """Enhanced dataset retrieval with access tracking."""
        if dataset_name not in self.datasets:
            raise ValueError(f"Dataset '{dataset_name}' not loaded. Use load_dataset() first.")

        # Update access metrics
        if dataset_name in self.metrics:
            self.metrics[dataset_name].access_count += 1
            self.metrics[dataset_name].last_accessed = datetime.now()

        return self.datasets[dataset_name]

    def track_analysis(self, dataset_name: str, analysis_type: str, details: Dict = None):
        """Track analytics operations for workflow optimization."""
        if dataset_name not in self.analytics_state:
            return

        state = self.analytics_state[dataset_name]

        # Update analysis state
        if analysis_type not in state.analyses_performed:
            state.analyses_performed.append(analysis_type)

        # Update specific flags
        if analysis_type == 'find_correlations':
            state.correlations_calculated = True
        elif analysis_type == 'validate_data_quality':
            state.quality_assessed = True
        elif analysis_type == 'analyze_distributions':
            if details and 'column' in details:
                if details['column'] not in state.distributions_analyzed:
                    state.distributions_analyzed.append(details['column'])
        elif analysis_type == 'segment_by_column':
            if details and 'column' in details:
                if details['column'] not in state.segments_created:
                    state.segments_created.append(details['column'])
        elif analysis_type == 'create_chart':
            if details:
                state.charts_generated.append(details)
        elif analysis_type == 'execute_custom_analytics_code':
            state.custom_code_runs += 1

        state.last_analysis = datetime.now()

        # Update metrics
        if dataset_name in self.metrics:
            self.metrics[dataset_name].analysis_count += 1

        # Generate new recommendations
        state.analysis_recommendations = self._generate_next_analysis_recommendations(dataset_name)

        # Log the operation
        self._log_operation('analysis', dataset_name, {
            'type': analysis_type,
            'details': details or {},
            'total_analyses': len(state.analyses_performed)
        })

    def get_analytics_summary(self, dataset_name: str) -> Dict:
        """Get comprehensive analytics summary for a dataset."""
        if dataset_name not in self.analytics_state:
            return {"error": f"No analytics state found for '{dataset_name}'"}

        state = self.analytics_state[dataset_name]
        metrics = self.metrics.get(dataset_name)
        schema = self.schemas.get(dataset_name)

        return {
            "dataset_name": dataset_name,
            "analytics_progress": {
                "analyses_performed": state.analyses_performed,
                "completion_percentage": self._calculate_completion_percentage(dataset_name),
                "correlations_calculated": state.correlations_calculated,
                "quality_assessed": state.quality_assessed,
                "distributions_analyzed": state.distributions_analyzed,
                "segments_created": state.segments_created,
                "charts_generated": len(state.charts_generated),
                "custom_code_runs": state.custom_code_runs,
                "last_analysis": state.last_analysis.isoformat() if state.last_analysis else None
            },
            "performance_metrics": {
                "memory_mb": metrics.memory_mb if metrics else 0,
                "access_count": metrics.access_count if metrics else 0,
                "analysis_count": metrics.analysis_count if metrics else 0,
                "optimization_suggestions": metrics.optimization_suggestions if metrics else []
            },
            "recommendations": {
                "next_analyses": state.analysis_recommendations,
                "workflow_suggestions": self._generate_workflow_suggestions(dataset_name)
            },
            "data_profile": {
                "rows": schema.row_count if schema else 0,
                "columns": len(schema.columns) if schema else 0,
                "suggested_analyses": schema.suggested_analyses if schema else []
            }
        }

    def _optimize_dataframe(self, df: pd.DataFrame, optimization_hints: List[str]) -> pd.DataFrame:
        """Apply memory and performance optimizations to DataFrame."""
        df_optimized = df.copy()

        # Automatic optimizations
        for col in df_optimized.columns:
            # Optimize integer columns
            if pd.api.types.is_integer_dtype(df_optimized[col]):
                col_min, col_max = df_optimized[col].min(), df_optimized[col].max()
                if col_min >= 0:  # Unsigned integers
                    if col_max < 255:
                        df_optimized[col] = df_optimized[col].astype('uint8')
                    elif col_max < 65535:
                        df_optimized[col] = df_optimized[col].astype('uint16')
                    elif col_max < 4294967295:
                        df_optimized[col] = df_optimized[col].astype('uint32')
                else:  # Signed integers
                    if col_min >= -128 and col_max <= 127:
                        df_optimized[col] = df_optimized[col].astype('int8')
                    elif col_min >= -32768 and col_max <= 32767:
                        df_optimized[col] = df_optimized[col].astype('int16')
                    elif col_min >= -2147483648 and col_max <= 2147483647:
                        df_optimized[col] = df_optimized[col].astype('int32')

            # Optimize float columns
            elif pd.api.types.is_float_dtype(df_optimized[col]):
                if 'high_precision' not in optimization_hints:
                    df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')

            # Optimize object columns to category when appropriate
            elif df_optimized[col].dtype == 'object':
                unique_ratio = df_optimized[col].nunique() / len(df_optimized)
                if unique_ratio < 0.5:  # Less than 50% unique values
                    df_optimized[col] = df_optimized[col].astype('category')

        return df_optimized

    def _generate_optimization_suggestions(self, df: pd.DataFrame) -> List[str]:
        """Generate optimization suggestions for a DataFrame."""
        suggestions = []

        memory_usage = df.memory_usage(deep=True).sum() / 1024**2

        if memory_usage > 100:  # MB
            suggestions.append("Consider sampling for initial analysis due to large size")

        # Check for object columns that could be categories
        for col in df.select_dtypes(include=['object']).columns:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.1:
                suggestions.append(f"Convert '{col}' to category type for memory savings")

        # Check for missing values
        missing_cols = df.isnull().sum()
        high_missing = missing_cols[missing_cols > len(df) * 0.5]
        if len(high_missing) > 0:
            suggestions.append(
                f"Consider dropping columns with >50% missing: {
                    list(
                        high_missing.index)}")

        return suggestions

    def _calculate_completion_percentage(self, dataset_name: str) -> float:
        """Calculate analytics completion percentage."""
        if dataset_name not in self.schemas:
            return 0.0

        schema = self.schemas[dataset_name]
        state = self.analytics_state[dataset_name]

        # Define expected analyses based on data characteristics
        expected_analyses = []

        # Basic analyses (always expected)
        expected_analyses.extend(['data_quality', 'basic_statistics'])

        # Conditional analyses based on data types
        numerical_cols = [
            name for name,
            info in schema.columns.items() if info.suggested_role == 'numerical']
        categorical_cols = [
            name for name,
            info in schema.columns.items() if info.suggested_role == 'categorical']
        temporal_cols = [
            name for name,
            info in schema.columns.items() if info.suggested_role == 'temporal']

        if len(numerical_cols) >= 2:
            expected_analyses.append('correlations')
        if categorical_cols:
            expected_analyses.append('segmentation')
        if temporal_cols:
            expected_analyses.append('time_series')
        if len(numerical_cols) >= 1:
            expected_analyses.append('distributions')

        # Calculate completion
        completed = len([a for a in expected_analyses if any(
            a in performed for performed in state.analyses_performed)])
        return (completed / len(expected_analyses)) * 100 if expected_analyses else 0.0

    def _generate_next_analysis_recommendations(self, dataset_name: str) -> List[str]:
        """Generate recommendations for next analyses."""
        if dataset_name not in self.schemas or dataset_name not in self.analytics_state:
            return []

        schema = self.schemas[dataset_name]
        state = self.analytics_state[dataset_name]
        recommendations = []

        # Basic workflow recommendations
        if not state.quality_assessed:
            recommendations.append("Assess data quality with validate_data_quality()")

        if not state.correlations_calculated and len(
                [c for c in schema.columns.values() if c.suggested_role == 'numerical']) >= 2:
            recommendations.append("Explore correlations with find_correlations()")

        # Column-specific recommendations
        numerical_cols = [
            name for name,
            info in schema.columns.items() if info.suggested_role == 'numerical']
        categorical_cols = [
            name for name,
            info in schema.columns.items() if info.suggested_role == 'categorical']

        for col in numerical_cols:
            if col not in state.distributions_analyzed:
                recommendations.append(
                    f"Analyze distribution of '{col}' with analyze_distributions()")
                break  # Only suggest one at a time

        for col in categorical_cols:
            if col not in state.segments_created:
                recommendations.append(f"Segment data by '{col}' with segment_by_column()")
                break  # Only suggest one at a time

        # Advanced recommendations
        if len(state.analyses_performed) >= 3 and state.custom_code_runs == 0:
            recommendations.append("Try custom analysis with execute_custom_analytics_code()")

        if len(state.charts_generated) == 0 and len(state.analyses_performed) >= 2:
            recommendations.append("Create visualizations with create_chart()")

        return recommendations[:3]  # Limit to top 3 recommendations

    def _generate_workflow_suggestions(self, dataset_name: str) -> List[str]:
        """Generate high-level workflow suggestions."""
        if dataset_name not in self.analytics_state:
            return []

        state = self.analytics_state[dataset_name]
        suggestions = []

        completion = self._calculate_completion_percentage(dataset_name)

        if completion < 25:
            suggestions.append("Focus on basic data exploration and quality assessment")
        elif completion < 50:
            suggestions.append("Dive deeper into statistical analysis and patterns")
        elif completion < 75:
            suggestions.append("Create visualizations and explore business insights")
        else:
            suggestions.append("Consider advanced analysis or prepare final reports")

        if len(state.charts_generated) > 3:
            suggestions.append("Consider creating a dashboard with generate_dashboard()")

        if state.custom_code_runs > 0:
            suggestions.append("Document custom analyses for reproducibility")

        return suggestions

    def _log_operation(self, operation: str, dataset_name: str, details: Dict):
        """Log operations for debugging and optimization."""
        self.analysis_history.append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'dataset': dataset_name,
            'details': details
        })

        # Keep only recent history (last 1000 operations)
        if len(self.analysis_history) > 1000:
            self.analysis_history = self.analysis_history[-1000:]

    def get_global_analytics_stats(self) -> Dict:
        """Get system-wide analytics statistics."""
        total_datasets = len(self.datasets)
        total_memory = sum(m.memory_mb for m in self.metrics.values())
        total_analyses = sum(len(s.analyses_performed) for s in self.analytics_state.values())

        return {
            "total_datasets": total_datasets,
            "total_memory_mb": round(total_memory, 1),
            "total_analyses_performed": total_analyses,
            "most_active_dataset": max(self.analytics_state.keys(),
                                       key=lambda x: len(self.analytics_state[x].analyses_performed)) if self.analytics_state else None,
            "recent_operations": self.analysis_history[-10:] if self.analysis_history else []
        }
