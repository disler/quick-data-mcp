"""Insight generation workshop prompt implementation."""

from typing import List, Optional
from ..models.schemas import DatasetManager, dataset_schemas


async def insight_generation_workshop(dataset_name: str, business_context: str = "general") -> str:
    """Generate business insights from data analysis."""
    try:
        if dataset_name not in dataset_schemas:
            return f"Dataset '{dataset_name}' not loaded. Use load_dataset() tool first."
        
        schema = dataset_schemas[dataset_name]
        
        prompt = f"""💡 **Business Insights Workshop: {dataset_name}**

Context: **{business_context}** analysis

Let's transform your **{schema.row_count:,} records** into actionable business insights! 

**🎯 Insight generation framework:**

**Phase 1: Data Understanding**
• What does each variable represent in your business?
• Which metrics matter most for decision-making?
• What questions are stakeholders asking?

**Phase 2: Pattern Analysis**
• `suggest_analysis('{dataset_name}')` - Get AI-powered analysis recommendations
• Run suggested analyses to uncover patterns
• Focus on business-relevant relationships

**Phase 3: Insight Synthesis**
• Translate statistical findings into business language
• Identify actionable opportunities
• Quantify potential business impact

**📊 Business insight categories:**

**Performance Insights** - How are we doing?
• Identify top/bottom performers
• Measure efficiency and effectiveness
• Track progress against goals

**Segmentation Insights** - Who are our different groups?
• Customer/product/regional segments
• Behavioral patterns and preferences
• Market opportunities by segment

**Predictive Insights** - What's likely to happen?
• Trend analysis and forecasting
• Risk identification
• Opportunity prediction

**Optimization Insights** - How can we improve?
• Resource allocation opportunities
• Process improvement areas
• Strategy refinement suggestions

**🔍 Context-specific analysis for {business_context}:**
"""
        
        # Add context-specific suggestions
        if business_context.lower() in ['sales', 'revenue', 'ecommerce']:
            prompt += """
• **Sales Performance**: Analyze conversion rates, deal sizes, seasonal patterns
• **Customer Behavior**: Purchase frequency, preferences, lifetime value
• **Channel Effectiveness**: Performance by sales channel or region
• **Product Insights**: Best/worst performers, cross-selling opportunities"""
            
        elif business_context.lower() in ['marketing', 'campaign', 'advertising']:
            prompt += """
• **Campaign Performance**: ROI, engagement rates, conversion metrics
• **Audience Segmentation**: Demographics, behavior, response patterns
• **Channel Analysis**: Most effective marketing channels and timing
• **Content Insights**: What messaging/content drives best results"""
            
        elif business_context.lower() in ['operations', 'process', 'efficiency']:
            prompt += """
• **Process Efficiency**: Bottlenecks, cycle times, resource utilization
• **Quality Metrics**: Error rates, compliance, consistency
• **Resource Optimization**: Capacity planning, cost reduction opportunities
• **Performance Trends**: Improving or declining operational metrics"""
            
        elif business_context.lower() in ['hr', 'employee', 'workforce']:
            prompt += """
• **Workforce Analytics**: Productivity, satisfaction, retention patterns
• **Performance Management**: Top performers, skill gaps, development needs
• **Engagement Insights**: What drives employee satisfaction and retention
• **Organizational Health**: Diversity, growth, cultural indicators"""
            
        else:
            prompt += """
• **Key Performance Indicators**: Identify and track most important metrics
• **Trend Analysis**: Understanding directional changes over time
• **Comparative Analysis**: Benchmarking against targets or competitors
• **Root Cause Analysis**: Understanding drivers of performance"""
        
        prompt += f"""

**🚀 Insight generation workflow:**

1. **Explore the data landscape**
   → `dataset_first_look('{dataset_name}')` - Understand what you have

2. **Run targeted analyses**
   → Focus on business-critical variables and relationships

3. **Create compelling visualizations**
   → `create_chart()` with business-relevant comparisons

4. **Generate actionable recommendations**
   → `export_insights('{dataset_name}', 'html')` - Create business report

**💼 Questions to drive insight generation:**
• What decisions do you need to make based on this data?
• Which patterns would surprise your stakeholders?
• What actions could you take if you knew X about your data?
• How can these insights drive measurable business value?

**🎯 Ready to generate insights?**

Start by telling me:
1. What specific business questions are you trying to answer?
2. Which variables in your dataset are most business-critical?
3. What decisions or actions might result from your analysis?

Let's turn your data into business intelligence that drives results!"""
        
        return prompt
        
    except Exception as e:
        return f"Error generating insight workshop prompt: {str(e)}"