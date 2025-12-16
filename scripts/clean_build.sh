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

# SOME/IP Stack - Clean Build Script
# Cleans build artifacts and cached dependencies

set -e

echo "SOME/IP Stack - Clean Build"
echo "==========================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Cleaning build directory..."
rm -rf "${PROJECT_ROOT}/build/"

echo "Cleaning CMake cache files..."
find "${PROJECT_ROOT}" -name "CMakeCache.txt" -delete
find "${PROJECT_ROOT}" -name "CMakeFiles" -type d -exec rm -rf {} + 2>/dev/null || true
find "${PROJECT_ROOT}" -name "cmake_install.cmake" -delete
find "${PROJECT_ROOT}" -name "*.cmake" -path "*/CMakeFiles/*" -delete

echo "Cleaning FetchContent cache..."
rm -rf "${PROJECT_ROOT}/_deps/"

echo ""
echo "Clean complete! 🧹"
echo ""
echo "You can now rebuild fresh:"
echo "  mkdir build && cd build"
echo "  cmake .."
echo "  make"
echo ""
echo "If you had Google Test download issues, try:"
echo "  cmake .. -DBUILD_TESTS=OFF  # Skip tests"
echo "  # or"
echo "  ./scripts/clean_build.sh && cmake ..  # Fresh start"
