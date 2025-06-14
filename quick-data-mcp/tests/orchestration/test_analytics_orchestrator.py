"""Tests for analytics orchestration functionality."""
import pytest
from src.mcp_server.orchestration.analytics_orchestrator import AnalyticsOrchestrator
from src.mcp_server.models.schemas import DatasetSchema, ColumnInfo


@pytest.fixture
def sample_schema():
    """Create a sample dataset schema for testing."""
    columns = {
        "order_id": ColumnInfo(
            name="order_id", 
            dtype="object", 
            unique_values=1000,
            null_percentage=0.0,
            sample_values=["ORD001", "ORD002", "ORD003"],
            suggested_role="identifier"
        ),
        "customer_id": ColumnInfo(
            name="customer_id", 
            dtype="object", 
            unique_values=200,
            null_percentage=0.0,
            sample_values=["CUST001", "CUST002", "CUST003"],
            suggested_role="categorical"
        ),
        "order_date": ColumnInfo(
            name="order_date", 
            dtype="datetime64[ns]", 
            unique_values=365,
            null_percentage=0.0,
            sample_values=["2024-01-01", "2024-01-02", "2024-01-03"],
            suggested_role="temporal"
        ),
        "order_value": ColumnInfo(
            name="order_value", 
            dtype="float64", 
            unique_values=500,
            null_percentage=0.0,
            sample_values=[99.99, 150.00, 75.50],
            suggested_role="numerical"
        ),
        "quantity": ColumnInfo(
            name="quantity", 
            dtype="int64", 
            unique_values=10,
            null_percentage=0.0,
            sample_values=[1, 2, 3],
            suggested_role="numerical"
        ),
        "product_category": ColumnInfo(
            name="product_category", 
            dtype="object", 
            unique_values=5,
            null_percentage=0.0,
            sample_values=["Electronics", "Clothing", "Books"],
            suggested_role="categorical"
        )
    }
    
    return DatasetSchema(
        name="test_ecommerce",
        columns=columns,
        row_count=1000,
        suggested_analyses=["correlation_analysis", "segmentation_analysis"]
    )


@pytest.fixture
def orchestrator():
    """Create an analytics orchestrator instance."""
    return AnalyticsOrchestrator()


def test_column_type_summary(orchestrator, sample_schema):
    """Test column type summary generation."""
    summary = orchestrator._get_column_type_summary(sample_schema)
    
    assert "2 numerical" in summary
    assert "2 categorical" in summary
    assert "1 temporal" in summary
    assert "1 identifier" in summary


def test_recommended_approach(orchestrator, sample_schema):
    """Test recommended approach determination."""
    approach = orchestrator._get_recommended_approach(sample_schema, "ecommerce")
    
    # With 2 numerical, 2 categorical, 1 temporal - temporal takes precedence
    assert "Time series analysis with trend detection" in approach


@pytest.mark.asyncio
async def test_workflow_phases_generation(orchestrator, sample_schema):
    """Test workflow phases generation."""
    phases = await orchestrator._design_workflow_phases(sample_schema, "ecommerce", "standard")
    
    # Should have at least 3 phases for this data profile
    assert len(phases) >= 3
    
    # Check first phase
    assert phases[0]["name"] == "Data Discovery & Quality"
    assert "steps" in phases[0]
    assert len(phases[0]["steps"]) >= 2
    
    # Check for statistical relationships phase (should exist with 2+ numerical cols)
    phase_names = [phase["name"] for phase in phases]
    assert "Statistical Relationships" in phase_names
    
    # Check for segmentation phase (should exist with categorical cols)
    assert "Segmentation Analysis" in phase_names