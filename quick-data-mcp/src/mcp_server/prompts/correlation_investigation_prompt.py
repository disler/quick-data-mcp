"""Correlation investigation prompt implementation."""

from typing import List, Optional
from ..models.schemas import DatasetManager, dataset_schemas


async def correlation_investigation(dataset_name: str) -> str:
    """Guide correlation analysis workflow."""
    try:
        if dataset_name not in dataset_schemas:
            return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
        
        schema = dataset_schemas[dataset_name]
        
        # Find numerical columns
        numerical_cols = [name for name, info in schema.columns.items() 
                         if info.suggested_role == 'numerical']
        
        if len(numerical_cols) < 2:
            return f"""**Correlation Analysis: Insufficient Numerical Data**

Your **{dataset_name}** dataset has {len(numerical_cols)} numerical column(s): {', '.join(numerical_cols) if numerical_cols else 'none'}

**To perform correlation analysis, you need:**
• At least 2 numerical columns
• Sufficient data variation (not all identical values)

**Suggestions:**
1. Check if any categorical columns contain numerical data stored as text
2. Convert date columns to numerical formats (days since epoch, etc.)
3. Create numerical features from categorical data (count encodings, etc.)
4. Load additional datasets with more numerical variables

**Alternative analyses you can perform:**
• Data quality assessment: `validate_data_quality('{dataset_name}')`
• Distribution analysis: `analyze_distributions('{dataset_name}', 'column_name')`
• Segmentation: `segment_by_column('{dataset_name}', 'categorical_column')`
"""
        
        prompt = f"""Let's explore **correlations** in your **{dataset_name}** dataset!

**📊 Available numerical columns** ({len(numerical_cols)}):
"""
        
        for col in numerical_cols:
            col_info = schema.columns[col]
            prompt += f"• **{col}**: {col_info.unique_values} unique values, {col_info.null_percentage:.1f}% missing\n"
            prompt += f"  Sample values: {', '.join(map(str, col_info.sample_values))}\n"
        
        prompt += f"""
**🎯 Correlation analysis strategy:**

1. **Start broad**: Find all significant correlations
   → `find_correlations('{dataset_name}')`

2. **Focus on strong relationships**: Investigate correlations > 0.7
   → Look for business logic behind statistical relationships

3. **Create visualizations**: Plot the strongest correlations
   → `create_chart('{dataset_name}', 'scatter', 'column1', 'column2')`

4. **Segment analysis**: Check if correlations hold across different groups
   → Combine with categorical segmentation

**🔍 What to look for:**
• **Strong positive correlations** (0.7+): Variables that increase together
• **Strong negative correlations** (-0.7+): Variables that move oppositely  
• **Moderate correlations** (0.3-0.7): Interesting but not overwhelming relationships
• **No correlation** (~0): Independent variables

**⚠️ Correlation insights:**
• Correlation ≠ Causation (remember this!)
• High correlation might indicate redundant features
• Unexpected correlations often reveal interesting patterns

**Quick commands to start:**
• `find_correlations('{dataset_name}')` - Find all correlations
• `find_correlations('{dataset_name}', ['{numerical_cols[0]}', '{numerical_cols[1]}'])` - Focus on specific columns"""
        
        if len(numerical_cols) >= 2:
            prompt += f"""
• `create_chart('{dataset_name}', 'scatter', '{numerical_cols[0]}', '{numerical_cols[1]}')` - Visualize relationship"""
        
        prompt += f"""

**💡 Advanced correlation techniques:**
• Partial correlations (controlling for other variables)
• Correlation matrices with hierarchical clustering
• Rolling correlations for time series data

Ready to discover hidden relationships in your data? What correlation analysis would you like to start with?"""
        
        return prompt
        
    except Exception as e:
        return f"Error generating correlation investigation prompt: {str(e)}"