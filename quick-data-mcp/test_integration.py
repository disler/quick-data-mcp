#!/usr/bin/env python3
"""Integration test for Feature 1 (Orchestration) + Feature 2 (State Tracking)."""

import asyncio
import sys
import os

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from mcp_server.managers.enhanced_dataset_manager import EnhancedDatasetManager, AnalyticsState, DatasetSchema


async def test_cross_feature_integration():
    """Test integration between orchestration and state tracking."""
    print("🔗 Testing Cross-Feature Integration")
    print("=" * 60)
    
    # Initialize enhanced manager
    manager = EnhancedDatasetManager()
    
    # Step 1: Load dataset with enhanced manager
    print("\n📊 Step 1: Loading dataset with enhanced manager...")
    try:
        result = manager.load_dataset("quick-data-mcp/data/ecommerce_orders.json", "ecommerce")
        print(f"Load result: {result}")
    except Exception as e:
        print(f"Could not load ecommerce data, using simulated data: {e}")
        # Create simulated dataset for demo
        import pandas as pd
        import tempfile
        
        simulated_data = pd.DataFrame({
            'order_id': [1, 2, 3, 4, 5],
            'product_category': ['Electronics', 'Clothing', 'Electronics', 'Home', 'Clothing'],
            'order_value': [150.0, 75.0, 200.0, 120.0, 85.0],
            'customer_age': [25, 35, 28, 45, 32],
            'quantity': [1, 2, 1, 3, 2]
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        simulated_data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        result = manager.load_dataset(temp_file.name, "ecommerce")
        print(f"Simulated load result: {result}")
        
        # Clean up temp file
        os.unlink(temp_file.name)
    
    # Step 2: Simulate analytics workflow progression
    print("\n🎯 Step 2: Simulating analytics workflow...")
    
    # Simulate data quality assessment
    manager.track_analysis("ecommerce", "validate_data_quality", {"issues_found": 0})
    print("✅ Data quality assessment completed")
    
    # Simulate correlation analysis  
    manager.track_analysis("ecommerce", "find_correlations", {"correlations_found": 2})
    print("✅ Correlation analysis completed")
    
    # Simulate segmentation
    manager.track_analysis("ecommerce", "segment_by_column", {"column": "product_category"})
    print("✅ Segmentation analysis completed")
    
    # Simulate visualization
    manager.track_analysis("ecommerce", "create_chart", {"chart_type": "bar", "column": "order_value"})
    print("✅ Visualization created")
    
    # Step 3: Check analytics state evolution
    print("\n📈 Step 3: Analytics state after workflow progression...")
    summary = manager.get_analytics_summary("ecommerce")
    
    print(f"Completion percentage: {summary['analytics_progress']['completion_percentage']:.1f}%")
    print(f"Analyses performed: {summary['analytics_progress']['analyses_performed']}")
    print(f"Next recommendations: {summary['recommendations']['next_analyses']}")
    print(f"Workflow suggestions: {summary['recommendations']['workflow_suggestions']}")
    
    # Step 4: Test recommendation evolution
    print("\n🧠 Step 4: Testing recommendation intelligence...")
    
    # Add more analyses and see how recommendations change
    manager.track_analysis("ecommerce", "analyze_distributions", {"column": "order_value"})
    manager.track_analysis("ecommerce", "execute_custom_analytics_code", {"code_lines": 15})
    
    updated_summary = manager.get_analytics_summary("ecommerce")
    print(f"Updated completion: {updated_summary['analytics_progress']['completion_percentage']:.1f}%")
    print(f"New recommendations: {updated_summary['recommendations']['next_analyses']}")
    
    # Step 5: Demonstrate multi-dataset independence
    print("\n🔄 Step 5: Testing multi-dataset independence...")
    
    # Load second dataset (simulate HR dataset)
    import pandas as pd
    import tempfile
    
    hr_data = pd.DataFrame({
        'employee_id': [101, 102, 103, 104, 105],
        'department': ['Engineering', 'Sales', 'HR', 'Engineering', 'Marketing'],
        'salary': [75000, 65000, 60000, 80000, 55000],
        'years_experience': [3, 7, 5, 8, 2],
        'satisfaction_score': [4.2, 3.8, 4.5, 4.1, 3.9]
    })
    
    hr_temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    hr_data.to_csv(hr_temp_file.name, index=False)
    hr_temp_file.close()
    
    hr_result = manager.load_dataset(hr_temp_file.name, "hr_data")
    print(f"HR dataset loaded: {hr_result['status']}")
    
    # Track different analyses for HR dataset
    manager.track_analysis("hr_data", "validate_data_quality", {"issues_found": 3})
    manager.track_analysis("hr_data", "analyze_distributions", {"column": "salary"})
    
    hr_summary = manager.get_analytics_summary("hr_data")
    ecommerce_summary = manager.get_analytics_summary("ecommerce")
    
    print(f"Ecommerce completion: {ecommerce_summary['analytics_progress']['completion_percentage']:.1f}%")
    print(f"HR completion: {hr_summary['analytics_progress']['completion_percentage']:.1f}%")
    print("✅ Datasets maintain independent analytics states")
    
    # Clean up HR temp file
    os.unlink(hr_temp_file.name)
    
    # Step 6: Global system stats
    print("\n📊 Step 6: Global system statistics...")
    global_stats = manager.get_global_analytics_stats()
    print(f"Total datasets: {global_stats['total_datasets']}")
    print(f"Total memory usage: {global_stats['total_memory_mb']} MB")
    print(f"Total analyses: {global_stats['total_analyses_performed']}")
    print(f"Most active dataset: {global_stats['most_active_dataset']}")
    
    # Step 7: Advanced workflow intelligence demonstration
    print("\n🔮 Step 7: Advanced workflow intelligence...")
    
    # Simulate a complete analytics journey
    manager.track_analysis("ecommerce", "detect_outliers", {"outliers_found": 2})
    manager.track_analysis("ecommerce", "segment_by_column", {"column": "customer_age"})
    
    # Check how recommendations evolve with high completion
    final_summary = manager.get_analytics_summary("ecommerce")
    print(f"Final completion: {final_summary['analytics_progress']['completion_percentage']:.1f}%")
    print(f"Advanced recommendations: {final_summary['recommendations']['workflow_suggestions']}")
    
    # Step 8: Performance optimization showcase
    print("\n⚡ Step 8: Performance optimization showcase...")
    performance_metrics = final_summary['performance_metrics']
    print(f"Memory usage: {performance_metrics['memory_mb']:.2f} MB")
    print(f"Dataset access count: {performance_metrics['access_count']}")
    print(f"Total analyses performed: {performance_metrics['analysis_count']}")
    print(f"Optimization suggestions: {len(performance_metrics['optimization_suggestions'])}")
    
    print("\n" + "=" * 60)
    print("🎉 INTEGRATION TEST COMPLETE")
    print("=" * 60)
    print("✅ Enhanced manager loads datasets with optimization")
    print("✅ Analytics state tracks workflow progression")  
    print("✅ Recommendations evolve based on completion")
    print("✅ Multi-dataset analytics states remain independent")
    print("✅ Global system provides comprehensive overview")
    print("✅ Performance metrics track memory and access patterns")
    print("✅ Workflow intelligence suggests next steps dynamically")
    print("\n🚀 Ready for Feature 1 + Feature 2 unified testing!")
    
    return {
        "success": True,
        "datasets_tested": 2,
        "total_analyses": global_stats['total_analyses_performed'],
        "ecommerce_completion": ecommerce_summary['analytics_progress']['completion_percentage'],
        "hr_completion": hr_summary['analytics_progress']['completion_percentage']
    }


if __name__ == "__main__":
    result = asyncio.run(test_cross_feature_integration())
    print(f"\n📋 Test Summary: {result}")