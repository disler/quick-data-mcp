"""Enhanced prompt orchestration for multi-stage analytics workflows."""

from typing import Dict, List, Optional, Any
from ..models.schemas import dataset_schemas
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from src.mcp_server.managers.enhanced_dataset_manager import EnhancedDatasetManager

# Global enhanced manager instance
enhanced_manager = EnhancedDatasetManager()


class AnalyticsOrchestrator:
    """Orchestrates complex analytics workflows across multiple prompts and tools."""
    
    def __init__(self, enhanced_manager_instance=None):
        self.workflow_state = {}
        self.recommended_next_steps = {}
        self.enhanced_manager = enhanced_manager_instance or enhanced_manager
    
    async def adaptive_analytics_workflow(
        self, 
        dataset_name: str, 
        business_context: str = "general",
        analysis_depth: str = "standard"
    ) -> str:
        """
        Multi-stage analytics workflow that adapts to data characteristics.
        
        This prompt orchestrates other prompts and tools for comprehensive analysis.
        """
        # Check if dataset exists in multiple possible locations
        if dataset_name not in self.enhanced_manager.schemas and dataset_name not in dataset_schemas:
            return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
        
        # Get schema from enhanced manager first, fallback to dataset_schemas
        schema = self.enhanced_manager.schemas.get(dataset_name) or dataset_schemas.get(dataset_name)
        
        # Stage 1: Data Assessment
        workflow = f"""# 🎯 Adaptive Analytics Workflow: {dataset_name}

## 📊 Intelligent Workflow Planning

Based on your **{dataset_name}** dataset characteristics, I've designed a personalized analytics journey:

**Dataset Profile:**
• **{schema.row_count:,} records** across **{len(schema.columns)} columns**
• **Data types detected:** {self._get_column_type_summary(schema)}
• **Recommended approach:** {self._get_recommended_approach(schema, business_context)}

"""
        
        # Stage 2: Contextual Workflow Design
        workflow_phases = await self._design_workflow_phases(schema, business_context, analysis_depth)
        
        workflow += "## 🚀 Personalized Analysis Phases\n\n"
        
        for i, phase in enumerate(workflow_phases, 1):
            workflow += f"### Phase {i}: {phase['name']}\n"
            workflow += f"**Goal:** {phase['goal']}\n\n"
            
            for step in phase['steps']:
                if step['type'] == 'prompt':
                    workflow += f"🔮 **{step['name']}**\n"
                    workflow += f"   → `/quick-data:{step['command']}`\n"
                elif step['type'] == 'tool':
                    workflow += f"🔧 **{step['name']}**\n"
                    workflow += f"   → `{step['command']}`\n"
                elif step['type'] == 'custom':
                    workflow += f"⚡ **{step['name']}**\n"
                    workflow += f"   → Custom analysis: {step['description']}\n"
                
                workflow += f"   *Why this matters:* {step['rationale']}\n\n"
            
            workflow += f"**🎯 Success Criteria:** {phase['success_criteria']}\n\n"
        
        # Stage 3: Next Steps and Automation
        workflow += f"""## 🎛️ Workflow Automation Options

**Quick Start (Recommended):**
```
# Begin with automated first look
{workflow_phases[0]['steps'][0]['command']}
```

**Full Automation:**
```python
# Execute entire workflow programmatically
workflow_results = await execute_analytics_workflow(
    dataset_name='{dataset_name}',
    phases={len(workflow_phases)},
    business_context='{business_context}'
)
```

**🔄 Adaptive Branching:**
This workflow will adapt based on your findings. After each phase, I'll suggest refined next steps based on what the data reveals.

**💡 Pro Tips:**
• Each phase builds on the previous one
• Skip phases that don't apply to your use case
• Return to earlier phases if new patterns emerge
• Use custom code execution for advanced analysis

Ready to begin your data journey? Start with Phase 1 above!"""
        
        return workflow
    
    def _get_column_type_summary(self, schema) -> str:
        """Generate a summary of column types."""
        type_counts = {}
        for col_info in schema.columns.values():
            role = col_info.suggested_role
            type_counts[role] = type_counts.get(role, 0) + 1
        
        return ", ".join([f"{count} {role}" for role, count in type_counts.items()])
    
    def _get_recommended_approach(self, schema, business_context: str) -> str:
        """Determine the recommended analytical approach."""
        numerical_count = sum(1 for info in schema.columns.values() if info.suggested_role == 'numerical')
        categorical_count = sum(1 for info in schema.columns.values() if info.suggested_role == 'categorical')
        temporal_count = sum(1 for info in schema.columns.values() if info.suggested_role == 'temporal')
        
        if numerical_count >= 3 and categorical_count >= 2:
            return "Comprehensive statistical analysis with segmentation"
        elif temporal_count >= 1 and numerical_count >= 1:
            return "Time series analysis with trend detection"
        elif categorical_count >= 2:
            return "Segmentation-focused analysis"
        elif numerical_count >= 2:
            return "Correlation and distribution analysis"
        else:
            return "Exploratory data analysis"
    
    async def _design_workflow_phases(self, schema, business_context: str, analysis_depth: str) -> List[Dict]:
        """Design workflow phases based on data characteristics."""
        phases = []
        
        # Always start with data exploration
        phases.append({
            "name": "Data Discovery & Quality",
            "goal": "Understand data structure and identify quality issues",
            "steps": [
                {
                    "type": "prompt",
                    "name": "Dataset First Look",
                    "command": f"dataset_first_look_prompt {schema.name}",
                    "rationale": "Get personalized exploration guide based on your specific data structure"
                },
                {
                    "type": "tool",
                    "name": "Data Quality Assessment",
                    "command": f"validate_data_quality('{schema.name}')",
                    "rationale": "Identify missing values, duplicates, and data quality issues early"
                }
            ],
            "success_criteria": "Clear understanding of data structure and quality baseline established"
        })
        
        # Add analysis phases based on data characteristics
        numerical_cols = [name for name, info in schema.columns.items() if info.suggested_role == 'numerical']
        categorical_cols = [name for name, info in schema.columns.items() if info.suggested_role == 'categorical']
        temporal_cols = [name for name, info in schema.columns.items() if info.suggested_role == 'temporal']
        
        if len(numerical_cols) >= 2:
            phases.append({
                "name": "Statistical Relationships",
                "goal": "Discover correlations and numerical patterns",
                "steps": [
                    {
                        "type": "prompt",
                        "name": "Correlation Investigation",
                        "command": f"correlation_investigation_prompt {schema.name}",
                        "rationale": "Guided discovery of relationships between numerical variables"
                    },
                    {
                        "type": "tool",
                        "name": "Distribution Analysis",
                        "command": f"analyze_distributions('{schema.name}', '{numerical_cols[0]}')",
                        "rationale": "Understand the shape and characteristics of your key numerical data"
                    }
                ],
                "success_criteria": "Key correlations identified and distribution patterns understood"
            })
        
        if categorical_cols:
            phases.append({
                "name": "Segmentation Analysis",
                "goal": "Understand how data varies across different groups",
                "steps": [
                    {
                        "type": "prompt",
                        "name": "Segmentation Workshop",
                        "command": f"segmentation_workshop_prompt {schema.name}",
                        "rationale": "Plan systematic approach to grouping and comparing data segments"
                    },
                    {
                        "type": "tool",
                        "name": "Category Analysis",
                        "command": f"segment_by_column('{schema.name}', '{categorical_cols[0]}')",
                        "rationale": "Quantify differences between groups in your most important categorical variable"
                    }
                ],
                "success_criteria": "Key segments identified with quantified performance differences"
            })
        
        # Business insight phase
        phases.append({
            "name": "Business Intelligence",
            "goal": f"Generate actionable insights for {business_context} context",
            "steps": [
                {
                    "type": "prompt",
                    "name": "Insight Generation Workshop",
                    "command": f"insight_generation_workshop_prompt {schema.name} {business_context}",
                    "rationale": "Transform statistical findings into business-relevant insights"
                },
                {
                    "type": "custom",
                    "name": "Custom Analysis",
                    "command": f"execute_custom_analytics_code('{schema.name}', 'custom_python_code')",
                    "description": "Domain-specific calculations and advanced analysis",
                    "rationale": "Go beyond standard analytics with custom logic for your specific use case"
                }
            ],
            "success_criteria": "Actionable business insights documented with supporting evidence"
        })
        
        # Visualization and reporting phase
        if analysis_depth in ["comprehensive", "advanced"]:
            phases.append({
                "name": "Visualization & Reporting",
                "goal": "Create compelling visualizations and comprehensive reports",
                "steps": [
                    {
                        "type": "prompt",
                        "name": "Dashboard Design Consultation",
                        "command": f"dashboard_design_consultation_prompt {schema.name} business_stakeholders",
                        "rationale": "Plan visualizations that effectively communicate your findings"
                    },
                    {
                        "type": "tool",
                        "name": "Export Insights",
                        "command": f"export_insights('{schema.name}', 'html', True)",
                        "rationale": "Create comprehensive report with charts for stakeholder review"
                    }
                ],
                "success_criteria": "Professional report and visualizations ready for stakeholder presentation"
            })
        
        return phases
