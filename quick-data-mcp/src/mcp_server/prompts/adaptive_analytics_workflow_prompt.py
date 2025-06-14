"""Master orchestration prompt for adaptive analytics workflows."""
from ..orchestration.analytics_orchestrator import AnalyticsOrchestrator


async def adaptive_analytics_workflow_prompt(
    dataset_name: str, 
    business_context: str = "general",
    analysis_depth: str = "standard"
) -> str:
    """
    Master orchestration prompt that designs personalized analytics workflows.
    
    This prompt adapts to your data characteristics and creates a multi-stage
    analytics journey with intelligent phase recommendations.
    
    Args:
        dataset_name: Name of the loaded dataset
        business_context: Business domain context (e.g., "ecommerce", "hr", "finance")
        analysis_depth: Level of analysis ("standard", "comprehensive", "advanced")
    
    Returns:
        Comprehensive workflow guide with personalized phases and recommendations
    """
    orchestrator = AnalyticsOrchestrator()
    return await orchestrator.adaptive_analytics_workflow(dataset_name, business_context, analysis_depth)
