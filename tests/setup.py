#!/usr/bin/env python3
"""
Setup script for SOME/IP testing environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, **kwargs):
    """Run command and return success"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, **kwargs)
    return result.returncode == 0

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")

    try:
        # Try to install requirements
        if run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
            print("✅ Python dependencies installed")
            return True
        else:
            print("❌ Failed to install Python dependencies")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_build():
    """Check if project is built"""
    build_dir = Path("../build")
    if not build_dir.exists():
        print("❌ Build directory not found")
        print("   Run: mkdir build && cd build && cmake .. && make")
        return False

    # Check for executables
    required_bins = [
        "echo_server", "echo_client",
        "rpc_calculator_server", "rpc_calculator_client",
        "sd_service_server", "sd_service_client",
        "event_publisher", "event_subscriber",
        "tp_example"
    ]

    missing = []
    for bin_name in required_bins:
        bin_path = build_dir / "bin" / bin_name
        if not bin_path.exists():
            missing.append(bin_name)

    if missing:
        print(f"❌ Missing executables: {', '.join(missing)}")
        print("   Run: cd build && make")
        return False

    print("✅ Build artifacts found")
    return True

def test_basic_setup():
    """Test basic setup by running a simple command"""
    print("🧪 Testing basic setup...")

    try:
        # Test Python imports
        import socket
        import struct
        print("✅ Basic Python modules available")

        # Test SOME/IP message creation
        sys.path.insert(0, str(Path(__file__).parent))
        from test_integration import SomeIpMessage

        msg = SomeIpMessage(0x1234, 0x0001, payload=b"test")
        data = msg.to_bytes()

        # Parse it back
        msg2 = SomeIpMessage.from_bytes(data)

        if msg2.payload == b"test":
            print("✅ SOME/IP message serialization works")
            return True
        else:
            print("❌ SOME/IP message serialization failed")
            return False

    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up SOME/IP Testing Environment")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return 1

    # Check build
    if not check_build():
        return 1

    # Install dependencies
    if not install_dependencies():
        return 1

    # Test setup
    if not test_basic_setup():
        return 1

    print()
    print("🎉 Setup complete! You can now run tests:")
    print()
    print("  # Run all tests")
    print("  python tests/run_tests.py --all")
    print()
    print("  # Run specific test categories")
    print("  python tests/run_tests.py --unit-only")
    print("  python tests/run_tests.py --integration-only")
    print("  python tests/run_tests.py --performance-only")
    print()
    print("  # Run with verbose output")
    print("  python tests/run_tests.py --all --verbose")
    print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
