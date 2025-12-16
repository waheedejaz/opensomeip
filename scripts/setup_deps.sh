#!/bin/bash
################################################################################
# Copyright (c) 2025 Vinicius Tadeu Zein
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
################################################################################

# SOME/IP Stack - Dependency Setup Script
# Installs required dependencies for building the SOME/IP stack

set -e

echo "SOME/IP Stack - Dependency Setup"
echo "================================"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux"

    # Check if we're on Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        echo "Installing dependencies with apt-get..."
        sudo apt-get update
        sudo apt-get install -y build-essential cmake clang

echo "Dependencies installed successfully!"
echo ""
echo "Next steps:"
echo "1. mkdir build && cd build"
echo "2. cmake ..  # This will automatically download Google Test"
echo "3. make -j$(nproc 2>/dev/null || echo 4)"
echo "4. make test  # Run the test suite"

    elif command -v yum &> /dev/null; then
        echo "Installing dependencies with yum..."
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y cmake clang

        echo "Dependencies installed successfully!"
    else
        echo "Unsupported Linux distribution. Please install:"
        echo "  - build-essential or Development Tools"
        echo "  - cmake"
        echo "  - clang"
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"

    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    echo "Installing dependencies with Homebrew..."
    brew update
    brew install cmake llvm

    echo "Dependencies installed successfully!"
    echo "Note: CMake will automatically download and build Google Test during build."

elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "Detected Windows"

    echo "Please install the following manually:"
    echo "1. Visual Studio 2019+ with C++ support"
    echo "2. CMake: https://cmake.org/download/"
    echo "3. Git: https://git-scm.com/downloads"
    echo ""
    echo "Or use Chocolatey:"
    echo "  choco install cmake visualstudio2019-workload-vctools git"

else
    echo "Unsupported operating system: $OSTYPE"
    echo "Please install manually:"
    echo "  - C++17 compiler (GCC 9+, Clang 10+, MSVC 2019+)"
    echo "  - CMake 3.20+"
    exit 1
fi

echo ""
echo "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. mkdir build && cd build"
echo "2. cmake .."
echo "3. make -j$(nproc 2>/dev/null || echo 4)"
echo "4. make test"
