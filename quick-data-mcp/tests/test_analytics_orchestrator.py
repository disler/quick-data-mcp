"""Test the analytics orchestrator."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from mcp_server.orchestration.analytics_orchestrator import AnalyticsOrchestrator
from mcp_server.managers.enhanced_dataset_manager import EnhancedDatasetManager


@pytest.fixture
def setup_orchestrator():
    """Setup orchestrator with test data."""
    manager = EnhancedDatasetManager()
    orchestrator = AnalyticsOrchestrator(manager)
    
    # Load test datasets
    manager.load_dataset("data/ecommerce_orders.json", "ecommerce_test")
    manager.load_dataset("data/employee_survey.csv", "hr_test")
    manager.load_dataset("data/product_performance.csv", "product_test")
    
    return orchestrator, manager


@pytest.mark.asyncio
async def test_basic_workflow_generation(setup_orchestrator):
    """Test basic workflow generation."""
    orchestrator, manager = setup_orchestrator
    
    workflow = await orchestrator.adaptive_analytics_workflow("ecommerce_test", "ecommerce", "standard")
    
    assert isinstance(workflow, str)
    assert len(workflow) > 500  # Should be a substantial workflow
    assert "ecommerce_test" in workflow
    assert "Phase" in workflow  # Should have phases
    assert "📊" in workflow or "🎯" in workflow  # Should have visual elements


@pytest.mark.asyncio
async def test_business_context_adaptation(setup_orchestrator):
    """Test workflow adaptation to different business contexts."""
    orchestrator, manager = setup_orchestrator
    
    # Test ecommerce context
    ecommerce_workflow = await orchestrator.adaptive_analytics_workflow(
        "ecommerce_test", "ecommerce", "standard"
    )
    
    # Test HR context
    hr_workflow = await orchestrator.adaptive_analytics_workflow(
        "hr_test", "hr", "standard"
    )
    
    # Test finance context
    finance_workflow = await orchestrator.adaptive_analytics_workflow(
        "product_test", "finance", "standard"
    )
    
    # Workflows should be different based on context
    assert ecommerce_workflow != hr_workflow
    assert hr_workflow != finance_workflow
    assert "ecommerce" in ecommerce_workflow.lower() or "customer" in ecommerce_workflow.lower()
    assert "hr" in hr_workflow.lower() or "employee" in hr_workflow.lower()


@pytest.mark.asyncio
async def test_analysis_depth_levels(setup_orchestrator):
    """Test different analysis depth levels."""
    orchestrator, manager = setup_orchestrator
    
    # Test standard depth
    standard_workflow = await orchestrator.adaptive_analytics_workflow(
        "ecommerce_test", "ecommerce", "standard"
    )
    
    # Test comprehensive depth
    comprehensive_workflow = await orchestrator.adaptive_analytics_workflow(
        "ecommerce_test", "ecommerce", "comprehensive"
    )
    
    # Test advanced depth
    advanced_workflow = await orchestrator.adaptive_analytics_workflow(
        "ecommerce_test", "ecommerce", "advanced"
    )
    
    # More comprehensive workflows should be longer
    assert len(comprehensive_workflow) >= len(standard_workflow)
    assert len(advanced_workflow) >= len(comprehensive_workflow)


@pytest.mark.asyncio
async def test_dataset_not_loaded_error(setup_orchestrator):
    """Test error handling for non-existent datasets."""
    orchestrator, manager = setup_orchestrator
    
    workflow = await orchestrator.adaptive_analytics_workflow(
        "nonexistent_dataset", "general", "standard"
    )
    
    assert "not loaded" in workflow
    assert "Use load_dataset()" in workflow


@pytest.mark.asyncio
async def test_workflow_phases_structure(setup_orchestrator):
    """Test that workflows have proper phase structure."""
    orchestrator, manager = setup_orchestrator
    
    workflow = await orchestrator.adaptive_analytics_workflow(
        "ecommerce_test", "ecommerce", "comprehensive"
    )
    
    # Should contain multiple phases
    assert "Phase 1" in workflow
    assert "Phase 2" in workflow
    assert workflow.count("Phase") >= 2
    
    # Should have recommendations
    assert "recommendation" in workflow.lower() or "suggest" in workflow.lower()
    
    # Should have specific analysis commands
    assert "analyze" in workflow.lower() or "segment" in workflow.lower()


@pytest.mark.asyncio
async def test_column_type_detection_integration(setup_orchestrator):
    """Test that workflows adapt to detected column types."""
    orchestrator, manager = setup_orchestrator
    
    # Generate workflow for dataset with mixed column types
    workflow = await orchestrator.adaptive_analytics_workflow(
        "ecommerce_test", "general", "standard"
    )
    
    # Should reference actual columns from the dataset
    expected_columns = ["order_value", "product_category", "customer_segment", "region"]
    
    # At least some column names should appear in the workflow
    column_found = any(col in workflow for col in expected_columns)
    assert column_found, f"No expected columns found in workflow. Workflow: {workflow[:500]}..."


@pytest.mark.asyncio
async def test_workflow_recommendations_quality(setup_orchestrator):
    """Test quality of workflow recommendations."""
    orchestrator, manager = setup_orchestrator
    
    workflow = await orchestrator.adaptive_analytics_workflow(
        "ecommerce_test", "ecommerce", "comprehensive"
    )
    
    # Should contain actionable recommendations
    action_words = ["analyze", "examine", "explore", "calculate", "segment", "correlate"]
    action_found = any(word in workflow.lower() for word in action_words)
    assert action_found
    
    # Should contain specific analysis methods
    analysis_methods = ["correlation", "segmentation", "distribution", "trend", "pattern"]
    method_found = any(method in workflow.lower() for method in analysis_methods)
    assert method_found


@pytest.mark.asyncio
async def test_multiple_dataset_workflows(setup_orchestrator):
    """Test generating workflows for different datasets."""
    orchestrator, manager = setup_orchestrator
    
    # Generate workflows for all test datasets
    workflows = {}
    
    for dataset_name, context in [
        ("ecommerce_test", "ecommerce"),
        ("hr_test", "hr"),
        ("product_test", "finance")
    ]:
        workflow = await orchestrator.adaptive_analytics_workflow(
            dataset_name, context, "standard"
        )
        workflows[dataset_name] = workflow
    
    # All workflows should be generated successfully
    assert all(len(w) > 100 for w in workflows.values())
    
    # Each should be unique
    workflow_texts = list(workflows.values())
    assert len(set(workflow_texts)) == len(workflow_texts)  # All unique


@pytest.mark.asyncio
async def test_workflow_personalization(setup_orchestrator):
    """Test workflow personalization features."""
    orchestrator, manager = setup_orchestrator
    
    workflow = await orchestrator.adaptive_analytics_workflow(
        "ecommerce_test", "ecommerce", "comprehensive"
    )
    
    # Should be personalized to the specific dataset
    assert "ecommerce_test" in workflow
    
    # Should reference actual data characteristics
    assert "15" in workflow or "records" in workflow  # Reference to row count
    assert "8" in workflow or "columns" in workflow   # Reference to column count
    
    # Should have personalized recommendations
    assert "your" in workflow.lower()  # Personalized language


@pytest.mark.asyncio
async def test_orchestrator_with_shared_manager(setup_orchestrator):
    """Test that orchestrator properly uses shared manager instance."""
    orchestrator, manager = setup_orchestrator
    
    # Verify the orchestrator is using the same manager instance
    assert orchestrator.enhanced_manager is manager
    
    # Track an analysis in the manager
    manager.track_analysis("ecommerce_test", "test_analysis", {"test": True})
    
    # Generate workflow - should be aware of the tracked analysis
    workflow = await orchestrator.adaptive_analytics_workflow(
        "ecommerce_test", "ecommerce", "standard"
    )
    
    # Workflow should still generate properly
    assert isinstance(workflow, str)
    assert len(workflow) > 100