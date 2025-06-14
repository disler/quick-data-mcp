#!/usr/bin/env python3
"""Debug the code generation to find the f-string issue."""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'quick-data-mcp', 'src')
sys.path.insert(0, src_path)

from mcp_server.advanced.advanced_code_executor import AdvancedCodeExecutor
from mcp_server.models.schemas import DatasetManager

async def debug_code_generation():
    """Debug what code is being generated."""
    
    # Load dataset
    DatasetManager.load_dataset("quick-data-mcp/data/ecommerce_orders.json", "test_debug")
    
    # Create executor
    executor = AdvancedCodeExecutor()
    
    # Create context
    context = await executor._create_execution_context("test_debug", "print('test')")
    
    # Generate enhanced code
    enhanced_code = await executor._prepare_enhanced_code(
        "print('test')", context, include_ai_context=True, execution_mode="safe"
    )
    
    print("GENERATED CODE:")
    print("=" * 80)
    
    # Split into lines and number them to find the issue
    lines = enhanced_code.split('\n')
    for i, line in enumerate(lines, 1):
        print(f"{i:3d}: {line}")
    
    print("=" * 80)
    
    # Try to identify problematic lines
    print("\nLooking for problematic f-strings...")
    for i, line in enumerate(lines, 1):
        if 'print(f"' in line and not line.rstrip().endswith('")') and not line.rstrip().endswith("')"):
            print(f"SUSPICIOUS LINE {i}: {line}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_code_generation())