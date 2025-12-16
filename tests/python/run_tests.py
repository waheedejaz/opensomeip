#!/usr/bin/env python3
"""
SOME/IP Stack Testing Runner

Runs the complete test suite including unit tests (C++), integration tests (Python),
and system tests (Python) for comprehensive validation.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, cwd=None, env=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_build():
    """Check if the project is built and executables exist"""
    build_dir = Path(__file__).parent.parent.parent / "build" / "bin"

    required_executables = [
        "echo_server", "echo_client",
        "rpc_calculator_server", "rpc_calculator_client",
        "sd_service_server", "sd_service_client",
        "event_publisher", "event_subscriber",
        "tp_example"
    ]

    missing = []
    for exe in required_executables:
        exe_path = build_dir / exe
        if not exe_path.exists():
            missing.append(exe)

    if missing:
        print(f"❌ Missing executables: {', '.join(missing)}")
        print("Please build the project first:")
        print("  cd build && make -j$(nproc)")
        return False

    print("✅ All executables found")
    return True


def run_cpp_unit_tests():
    """Run C++ unit tests using CTest"""
    print("\n" + "="*60)
    print("🧪 RUNNING C++ UNIT TESTS")
    print("="*60)

    success, stdout, stderr = run_command("cd build && ctest --output-on-failure")

    if success:
        print("✅ C++ unit tests PASSED")
    else:
        print("❌ C++ unit tests FAILED")
        if stderr:
            print("STDERR:", stderr[-500:])  # Last 500 chars

    return success


def run_python_integration_tests():
    """Run Python integration tests"""
    print("\n" + "="*60)
    print("🔗 RUNNING PYTHON INTEGRATION TESTS")
    print("="*60)

    success, stdout, stderr = run_command(
        "cd tests/python && python -m pytest ../integration/ -v --tb=short"
    )

    if success:
        print("✅ Python integration tests PASSED")
    else:
        print("❌ Python integration tests FAILED")
        if stderr:
            print("STDERR:", stderr[-1000:])  # Last 1000 chars

    return success


def run_python_system_tests():
    """Run Python system tests"""
    print("\n" + "="*60)
    print("🏗️  RUNNING PYTHON SYSTEM TESTS")
    print("="*60)

    success, stdout, stderr = run_command(
        "cd tests/python && python -m pytest ../system/ -v --tb=short -k 'not performance'"
    )

    if success:
        print("✅ Python system tests PASSED")
    else:
        print("❌ Python system tests FAILED")
        if stderr:
            print("STDERR:", stderr[-1000:])  # Last 1000 chars

    return success


def run_performance_tests():
    """Run performance tests (optional, slower)"""
    print("\n" + "="*60)
    print("⚡ RUNNING PERFORMANCE TESTS")
    print("="*60)

    response = input("Run performance tests? They take longer (y/N): ").strip().lower()
    if response != 'y':
        print("⏭️  Skipping performance tests")
        return True

    success, stdout, stderr = run_command(
        "cd tests/python && python -m pytest ../system/ -v --tb=short -k performance"
    )

    if success:
        print("✅ Performance tests PASSED")
    else:
        print("❌ Performance tests FAILED")

    return success


def generate_coverage_report():
    """Generate test coverage report"""
    print("\n" + "="*60)
    print("📊 GENERATING COVERAGE REPORT")
    print("="*60)

    try:
        success, stdout, stderr = run_command(
            "cd tests/python && python -m pytest ../integration/ ../system/ --cov=../../src --cov-report=html --cov-report=term"
        )

        if success:
            print("✅ Coverage report generated in tests/python/htmlcov/")
        else:
            print("⚠️  Coverage report generation failed")

        return success
    except:
        print("⚠️  pytest-cov not available, skipping coverage")
        return True


def main():
    """Main test runner"""
    print("🚗 SOME/IP Stack Complete Test Suite")
    print("="*60)

    # Check if we're in the right directory
    if not Path("CMakeLists.txt").exists():
        print("❌ Please run from project root directory")
        sys.exit(1)

    # Check build
    if not check_build():
        sys.exit(1)

    # Run test suites
    results = []

    # C++ Unit Tests
    results.append(("C++ Unit Tests", run_cpp_unit_tests()))

    # Python Integration Tests
    results.append(("Python Integration", run_python_integration_tests()))

    # Python System Tests
    results.append(("Python System", run_python_system_tests()))

    # Performance Tests (optional)
    results.append(("Performance", run_performance_tests()))

    # Coverage (optional)
    results.append(("Coverage", generate_coverage_report()))

    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print("15")
        if not passed:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! SOME/IP Stack is fully functional.")
    else:
        print("⚠️  SOME TESTS FAILED. Check output above for details.")
        sys.exit(1)

    print("\n📖 Test Categories:")
    print("  🧪 Unit Tests: Component-level validation (GTest)")
    print("  🔗 Integration Tests: Multi-component interaction (pytest)")
    print("  🏗️  System Tests: End-to-end functionality (pytest)")
    print("  ⚡ Performance Tests: Load and timing validation")
    print("  📊 Coverage: Code coverage analysis")


if __name__ == "__main__":
    main()
