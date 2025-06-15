#!/usr/bin/env python3
"""Comprehensive test runner for the analytics platform."""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Run comprehensive test suite."""
    print("🧪 COMPREHENSIVE ANALYTICS PLATFORM TEST SUITE")
    print("=" * 70)
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    tests_passed = 0
    total_tests = 0
    
    # 1. Run unit tests
    total_tests += 1
    if run_command("python -m pytest tests/test_*.py -v", "Unit Tests (30 tests)"):
        tests_passed += 1
    
    # 2. Run integration tests
    total_tests += 1
    if run_command("python tests/integration/test_complete_platform.py", "Integration Test - Complete Platform"):
        tests_passed += 1
    
    # 3. Run final validation
    total_tests += 1  
    if run_command("python tests/integration/test_final_validation.py", "Final Validation - End-to-End Test"):
        tests_passed += 1
    
    # 4. Run all tests together
    total_tests += 1
    if run_command("python -m pytest tests/ -v", "All Tests (Unit + Integration)"):
        tests_passed += 1
    
    # Summary
    print(f"\n🏆 TEST SUITE SUMMARY")
    print("=" * 70)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {tests_passed/total_tests*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - PLATFORM READY FOR PRODUCTION!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - CHECK OUTPUT ABOVE")
        return 1


if __name__ == "__main__":
    sys.exit(main())