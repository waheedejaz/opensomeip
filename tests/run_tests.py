#!/usr/bin/env python3
"""
SOME/IP Stack Test Runner

Unified test runner for unit tests, integration tests, and performance tests.
"""

import subprocess
import sys
import os
import argparse
import time
from pathlib import Path

def run_command(cmd: list, cwd: str = None, timeout: int = None) -> tuple:
    """Run a command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout} seconds: {' '.join(cmd)}")
        return -1, "", "Timeout"

def run_ctest(build_dir: str, test_filter: str = None, verbose: bool = False):
    """Run CTest unit tests"""
    print("🔬 Running C++ Unit Tests (CTest)...")

    cmd = ["ctest", "--output-on-failure"]
    if test_filter:
        cmd.extend(["-R", test_filter])
    if verbose:
        cmd.append("-V")

    returncode, stdout, stderr = run_command(cmd, cwd=build_dir)

    if returncode == 0:
        print("✅ C++ Unit Tests: PASSED")
    else:
        print("❌ C++ Unit Tests: FAILED")
        print(stdout)
        print(stderr)

    return returncode == 0

def run_pytest(build_dir: str, test_type: str = "all", verbose: bool = False, coverage: bool = False):
    """Run Python integration tests with pytest"""
    print("🔬 Running Python Integration Tests (pytest)...")

    # Ensure we're in the tests directory
    test_dir = os.path.dirname(__file__)

    cmd = ["python", "-m", "pytest"]

    # Select test files based on type
    if test_type == "integration":
        cmd.extend(["test_integration.py", "conformance_test.py"])
    elif test_type == "specification":
        cmd.append("specification_test.py")
    elif test_type == "performance":
        cmd.append("-k", "Performance or Throughput or Latency")
    elif test_type == "conformance":
        cmd.append("conformance_test.py")
    elif test_type == "basic":
        cmd.append("-k", "BasicCommunication or RpcFunctionality")
    else:
        # Run all Python tests
        cmd.extend(["test_integration.py", "conformance_test.py", "specification_test.py"])

    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    if coverage:
        cmd.extend(["--cov=../src", "--cov-report=html"])

    # Set PYTHONPATH to include the build directory
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{build_dir}/bin:{env.get('PYTHONPATH', '')}"

    returncode, stdout, stderr = run_command(cmd, cwd=test_dir, timeout=120)

    if returncode == 0:
        print("✅ Python Integration Tests: PASSED")
    else:
        print("❌ Python Integration Tests: FAILED")
        if not verbose:
            print(stdout)
            print(stderr)

    return returncode == 0

def run_unittest(build_dir: str, test_type: str = "all", verbose: bool = False):
    """Run Python tests with unittest"""
    print("🔬 Running Python Tests (unittest)...")

    test_dir = os.path.dirname(__file__)

    cmd = ["python", "integration_test.py"]
    if test_type == "integration":
        cmd.append("--integration-only")
    elif test_type == "performance":
        cmd.append("--performance-only")

    if verbose:
        cmd.append("--verbose")

    returncode, stdout, stderr = run_command(cmd, cwd=test_dir, timeout=120)

    if returncode == 0:
        print("✅ Python Unittest Tests: PASSED")
    else:
        print("❌ Python Unittest Tests: FAILED")
        print(stdout)
        print(stderr)

    return returncode == 0

def build_project(build_dir: str, clean: bool = False):
    """Build the project"""
    print("🔨 Building project...")

    if clean:
        print("   Cleaning build directory...")
        returncode, stdout, stderr = run_command(["make", "clean"], cwd=build_dir)
        if returncode != 0:
            print("Warning: Clean failed")

    returncode, stdout, stderr = run_command(["make", "-j4"], cwd=build_dir, timeout=300)

    if returncode == 0:
        print("✅ Build: SUCCESS")
        return True
    else:
        print("❌ Build: FAILED")
        print(stdout)
        print(stderr)
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")

    missing = []

    # Check Python packages
    try:
        import pytest
        print("   ✅ pytest available")
    except ImportError:
        missing.append("pytest (pip install pytest)")

    try:
        import scapy
        print("   ✅ scapy available")
    except ImportError:
        print("   ⚠️  scapy not available (optional for advanced network testing)")

    # Check build tools
    returncode, _, _ = run_command(["cmake", "--version"])
    if returncode == 0:
        print("   ✅ cmake available")
    else:
        missing.append("cmake")

    returncode, _, _ = run_command(["make", "--version"])
    if returncode == 0:
        print("   ✅ make available")
    else:
        missing.append("make")

    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        return False

    print("✅ All required dependencies available")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="SOME/IP Stack Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                    # Run all tests
  %(prog)s --unit-only              # Run only C++ unit tests
  %(prog)s --integration-only       # Run only Python integration tests
  %(prog)s --performance-only       # Run only performance tests
  %(prog)s --test-framework pytest  # Use pytest instead of unittest
  %(prog)s --build                  # Build before testing
  %(prog)s --clean                  # Clean build before building
        """
    )

    parser.add_argument("--all", action="store_true",
                       help="Run all tests (default)")
    parser.add_argument("--unit-only", action="store_true",
                       help="Run only C++ unit tests")
    parser.add_argument("--integration-only", action="store_true",
                       help="Run only integration tests")
    parser.add_argument("--specification-only", action="store_true",
                       help="Run only specification compliance tests")
    parser.add_argument("--conformance-only", action="store_true",
                       help="Run only protocol conformance tests")
    parser.add_argument("--performance-only", action="store_true",
                       help="Run only performance tests")

    parser.add_argument("--test-framework", choices=["unittest", "pytest"],
                       default="pytest", help="Test framework to use (default: pytest)")

    parser.add_argument("--build", action="store_true",
                       help="Build project before testing")
    parser.add_argument("--clean", action="store_true",
                       help="Clean build directory before building")

    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report (pytest only)")
    parser.add_argument("--generate-coverage-report", action="store_true",
                       help="Generate specification coverage report")

    parser.add_argument("--check-deps", action="store_true",
                       help="Check dependencies and exit")

    args = parser.parse_args()

    # Get project directories
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    build_dir = project_dir / "build"

    # Check dependencies if requested
    if args.check_deps:
        return 0 if check_dependencies() else 1

    # Ensure build directory exists
    if not build_dir.exists():
        print(f"❌ Build directory not found: {build_dir}")
        print("   Run 'mkdir build && cd build && cmake .. && make' first")
        return 1

    # Build project if requested
    if args.build or args.clean:
        if not build_project(str(build_dir), args.clean):
            return 1

    # Check dependencies
    if not check_dependencies():
        return 1

    # Determine test scope
    if args.unit_only:
        test_scope = "unit"
    elif args.integration_only:
        test_scope = "integration"
    elif args.specification_only:
        test_scope = "specification"
    elif args.conformance_only:
        test_scope = "conformance"
    elif args.performance_only:
        test_scope = "performance"
    else:
        test_scope = "all"

    print("🚀 Starting SOME/IP Stack Tests")
    print(f"   Test Scope: {test_scope}")
    print(f"   Test Framework: {args.test_framework}")
    print(f"   Build Dir: {build_dir}")
    print()

    results = []
    start_time = time.time()

    # Run unit tests (always run these)
    if test_scope in ["all", "unit"]:
        results.append(run_ctest(str(build_dir), verbose=args.verbose))

    # Run integration/performance tests
    if test_scope in ["all", "integration", "performance"]:
        if args.test_framework == "pytest":
            results.append(run_pytest(str(build_dir), test_scope, args.verbose, args.coverage))
        else:
            results.append(run_unittest(str(build_dir), test_scope, args.verbose))

    # Generate coverage report if requested
    if args.generate_coverage_report:
        print("\n📊 Generating Specification Coverage Report...")
        coverage_cmd = ["python", "coverage_report.py"]
        returncode, stdout, stderr = run_command(coverage_cmd, cwd=str(script_dir))
        if returncode == 0:
            print("✅ Coverage report generated")
        else:
            print("❌ Coverage report generation failed")
            if args.verbose:
                print(stdout)
                print(stderr)

    # Summary
    duration = time.time() - start_time
    passed = sum(results)
    total = len(results)

    print()
    print("📊 Test Summary:")
    print(".2f")
    print(f"   Tests Passed: {passed}/{total}")

    if all(results):
        print("🎉 All tests PASSED!")
        return 0
    else:
        print("💥 Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
