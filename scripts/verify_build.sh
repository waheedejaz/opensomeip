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

# SOME/IP Stack - Build Verification Script
# Verifies that CMake configuration works without errors

set -e

echo "SOME/IP Stack - Build Verification"
echo "==================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Clean previous build
echo "Cleaning previous build..."
rm -rf "${PROJECT_ROOT}/build/"

# Create build directory
echo "Creating build directory..."
mkdir -p "${PROJECT_ROOT}/build/"
cd "${PROJECT_ROOT}/build/"

# Test CMake configuration (without building)
echo "Testing CMake configuration..."
if cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF > cmake_config.log 2>&1; then
    echo "✅ CMake configuration successful!"
else
    echo "❌ CMake configuration failed!"
    echo "Check cmake_config.log for details:"
    cat cmake_config.log
    exit 1
fi

# Test CMake configuration with tests enabled (but don't download)
echo "Testing CMake configuration with tests..."
if cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON > /dev/null 2>&1; then
    echo "✅ CMake configuration with tests successful!"
    echo "Note: Google Test will be downloaded during actual build"
else
    echo "❌ CMake configuration with tests failed!"
    exit 1
fi

echo ""
echo "Build verification complete! ✅"
echo ""
echo "Your CMake configuration is working correctly."
echo "To build the project:"
echo "  cd build"
echo "  make -j$(nproc 2>/dev/null || echo 4)"
echo ""
echo "To run tests after building:"
echo "  cd build"
echo "  ctest --output-on-failure"
