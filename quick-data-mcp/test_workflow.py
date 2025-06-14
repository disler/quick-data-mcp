#!/usr/bin/env python3
"""Test script for the data loading and orchestration workflow."""

import asyncio
import sys
import os

# Add src to Python path - adjusted for worktree structure
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from mcp_server.tools.load_dataset_tool import load_dataset
from mcp_server.prompts.adaptive_analytics_workflow_prompt import adaptive_analytics_workflow_prompt


async def main():
    """Run the workflow test."""
    print("🚀 Testing Data Loading and Orchestration Workflow")
    print("=" * 60)
    
    # Check current working directory
    print(f"📍 Current directory: {os.getcwd()}")
    print(f"📍 Python path includes: {src_path}")
    
    # Load the ecommerce dataset - corrected path for worktree
    print("\n📊 Loading ecommerce dataset...")
    dataset_path = "data/ecommerce_orders.json"  # Relative to current worktree
    dataset_name = "ecommerce"
    
    try:
        load_result = await load_dataset(dataset_path, dataset_name)
        print(f"Load result: {load_result}")
        
        if load_result.get("status") == "error":
            print(f"❌ Failed to load dataset: {load_result.get('message', 'Unknown error')}")
            return
            
        print(f"✅ Successfully loaded {load_result.get('rows', 0)} rows")
        
        # Run the adaptive analytics workflow
        print(f"\n🎯 Running adaptive analytics workflow...")
        print("Parameters:")
        print(f"  - Dataset: {dataset_name}")
        print(f"  - Business Context: ecommerce") 
        print(f"  - Analysis Depth: comprehensive")
        
        workflow_guide = await adaptive_analytics_workflow_prompt(
            dataset_name=dataset_name,
            business_context="ecommerce", 
            analysis_depth="comprehensive"
        )
        
        print("\n" + "=" * 60)
        print("📋 WORKFLOW GUIDE")
        print("=" * 60)
        print(workflow_guide)
        
    except Exception as e:
        print(f"❌ Error during workflow test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())