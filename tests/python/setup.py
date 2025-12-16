#!/usr/bin/env python3
"""
Setup script for SOME/IP Python testing framework.

Installs required dependencies and verifies the testing environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"STDERR: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False

    print(f"✅ Python {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")

    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False

    # Try to install dependencies
    if run_command(f"pip install -r {requirements_file}"):
        print("✅ Dependencies installed")
        return True
    else:
        print("⚠️  Failed to install some dependencies")
        print("   You may need to install them manually:")
        print(f"   pip install -r {requirements_file}")
        return False


def verify_installation():
    """Verify that key packages are installed"""
    required_packages = [
        'pytest',
        'pytest_asyncio',
        'pytest_cov'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('_', ''))
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        return False

    print("✅ All required packages available")
    return True


def check_build_artifacts():
    """Check if the C++ project is built"""
    project_root = Path(__file__).parent.parent.parent
    build_dir = project_root / "build" / "bin"

    if not build_dir.exists():
        print("❌ Build directory not found")
        print("   Please build the C++ project first:")
        print("   mkdir build && cd build && cmake .. && make")
        return False

    required_executables = [
        "echo_server", "echo_client",
        "rpc_calculator_server", "rpc_calculator_client"
    ]

    missing = []
    for exe in required_executables:
        if not (build_dir / exe).exists():
            missing.append(exe)

    if missing:
        print(f"❌ Missing executables: {', '.join(missing)}")
        print("   Please build the complete project")
        return False

    print("✅ Build artifacts found")
    return True


def run_basic_test():
    """Run a basic test to verify everything works"""
    print("🧪 Running basic test...")

    # Try to import our framework
    try:
        import someip_test_framework
        print("✅ Framework import successful")
    except ImportError as e:
        print(f"❌ Framework import failed: {e}")
        return False

    # Try to run pytest discovery
    if run_command("python -m pytest --collect-only -q"):
        print("✅ Pytest discovery successful")
        return True
    else:
        print("❌ Pytest discovery failed")
        return False


def main():
    """Main setup function"""
    print("🚗 SOME/IP Python Testing Framework Setup")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Package Verification", verify_installation),
        ("Build Artifacts", check_build_artifacts),
        ("Basic Test", run_basic_test)
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        if not check_func():
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Setup completed successfully!")
        print("\n🚀 You can now run tests with:")
        print("   python run_tests.py")
        print("   # or")
        print("   python -m pytest ../integration/ -v")
    else:
        print("⚠️  Setup completed with issues")
        print("   Please resolve the errors above before running tests")
        sys.exit(1)


if __name__ == "__main__":
    main()
