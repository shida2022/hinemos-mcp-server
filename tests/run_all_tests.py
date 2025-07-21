#!/usr/bin/env python3
"""
Comprehensive test runner for all Hinemos MCP REST client tests.
This script runs all validation tests to ensure the REST client works correctly.
"""

import sys
import os
import subprocess
import time
from typing import List, Tuple, Dict

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_test_script(script_path: str, test_name: str) -> Tuple[bool, str, float]:
    """Run a test script and return results."""
    print(f"\n🧪 Running {test_name}")
    print("=" * (len(test_name) + 12))
    
    start_time = time.time()
    
    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ {test_name} completed successfully in {duration:.2f}s")
        else:
            print(f"❌ {test_name} failed with return code {result.returncode}")
        
        return success, result.stdout + result.stderr, duration
    
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name} timed out after 60 seconds")
        return False, "Test timed out", 60.0
    
    except Exception as e:
        print(f"💥 {test_name} crashed with exception: {e}")
        return False, str(e), 0.0


def check_test_files() -> List[Tuple[str, str]]:
    """Check which test files exist and return list of (path, name) tuples."""
    test_dir = os.path.dirname(__file__)
    
    test_files = [
        ("test_new_monitor_models.py", "Monitor Model Validation"),
        ("test_rest_endpoints.py", "REST API Endpoints"),
        ("test_high_level_api.py", "High-Level API Integration")
    ]
    
    available_tests = []
    missing_tests = []
    
    for filename, test_name in test_files:
        filepath = os.path.join(test_dir, filename)
        if os.path.exists(filepath):
            available_tests.append((filepath, test_name))
        else:
            missing_tests.append((filename, test_name))
    
    if missing_tests:
        print("⚠️ Missing test files:")
        for filename, test_name in missing_tests:
            print(f"   - {filename} ({test_name})")
    
    return available_tests


def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking Dependencies")
    print("-" * 30)
    
    required_modules = [
        "pydantic",
        "httpx"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - not found")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ Missing required modules: {', '.join(missing_modules)}")
        print("Install them with: pip install " + " ".join(missing_modules))
        return False
    
    return True


def check_source_files():
    """Check if source files exist."""
    print("\n📁 Checking Source Files")
    print("-" * 30)
    
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'hinemos_mcp')
    
    required_files = [
        "client.py",
        "monitor.py", 
        "monitor_models.py",
        "server/server.py"
    ]
    
    missing_files = []
    
    for filename in required_files:
        filepath = os.path.join(src_dir, filename)
        if os.path.exists(filepath):
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} - not found")
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n⚠️ Missing source files: {', '.join(missing_files)}")
        return False
    
    return True


def main():
    """Main test runner."""
    print("🚀 Hinemos MCP REST Client Test Suite")
    print("=" * 50)
    print("Testing new monitoring types implementation")
    print("- SQL monitoring")
    print("- JMX monitoring") 
    print("- Process monitoring")
    print("- Port monitoring")
    print("- Windows Event monitoring")
    print("- Custom command monitoring")
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing modules.")
        return False
    
    # Check source files
    if not check_source_files():
        print("\n❌ Source file check failed. Please ensure all files are present.")
        return False
    
    # Check test files
    available_tests = check_test_files()
    
    if not available_tests:
        print("\n❌ No test files found!")
        return False
    
    print(f"\n🎯 Found {len(available_tests)} test suites to run")
    
    # Run all tests
    results: Dict[str, Tuple[bool, float]] = {}
    total_time = 0.0
    
    for test_path, test_name in available_tests:
        success, output, duration = run_test_script(test_path, test_name)
        results[test_name] = (success, duration)
        total_time += duration
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, (success, duration) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name:<35} ({duration:.2f}s)")
        if success:
            passed += 1
    
    print("-" * 60)
    print(f"🎯 Overall Results: {passed}/{total} test suites passed")
    print(f"⏱️ Total time: {total_time:.2f} seconds")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✅ REST client models are correctly implemented")
        print("✅ API endpoints are properly configured")
        print("✅ High-level API wrapper functions work correctly")
        print("✅ New monitoring types are ready for use:")
        print("   • SQL monitoring")
        print("   • JMX monitoring")
        print("   • Process monitoring") 
        print("   • Port monitoring")
        print("   • Windows Event monitoring")
        print("   • Custom command monitoring")
        print("\n🚀 The Hinemos MCP REST client is ready for production use!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test suite(s) failed")
        print("Please review the failed tests and fix any issues before using the client.")
        return False


def run_individual_test():
    """Run a specific test interactively."""
    available_tests = check_test_files()
    
    if not available_tests:
        print("❌ No test files found!")
        return
    
    print("\nAvailable test suites:")
    for i, (test_path, test_name) in enumerate(available_tests, 1):
        print(f"{i}. {test_name}")
    
    try:
        choice = input(f"\nSelect test to run (1-{len(available_tests)}): ")
        index = int(choice) - 1
        
        if 0 <= index < len(available_tests):
            test_path, test_name = available_tests[index]
            success, output, duration = run_test_script(test_path, test_name)
            
            if success:
                print(f"\n✅ {test_name} completed successfully!")
            else:
                print(f"\n❌ {test_name} failed!")
        else:
            print("Invalid choice!")
    
    except (ValueError, KeyboardInterrupt):
        print("\nTest cancelled.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hinemos MCP REST Client Test Suite")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run tests interactively")
    parser.add_argument("--check-only", "-c", action="store_true",
                       help="Only check dependencies and files, don't run tests")
    
    args = parser.parse_args()
    
    if args.check_only:
        success = check_dependencies() and check_source_files()
        sys.exit(0 if success else 1)
    elif args.interactive:
        run_individual_test()
    else:
        success = main()
        sys.exit(0 if success else 1)