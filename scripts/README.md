<!--
  Copyright (c) 2025 Vinicius Tadeu Zein

  See the NOTICE file(s) distributed with this work for additional
  information regarding copyright ownership.

  This program and the accompanying materials are made available under the
  terms of the Apache License Version 2.0 which is available at
  https://www.apache.org/licenses/LICENSE-2.0

  SPDX-License-Identifier: Apache-2.0
-->

# Utility Scripts

This directory contains utility scripts for development, testing, and maintenance of the SOME/IP stack implementation.

## Available Scripts

### Environment Setup
- **`setup_deps.sh`**: Install basic build dependencies (compiler, cmake, etc.)
- **`install_dev_tools.sh`**: Install advanced development tools (clang-tidy, gcovr, pytest, etc.)

### Build & Maintenance
- **`clean_build.sh`**: Clean build artifacts and cache
- **`verify_build.sh`**: Verify build integrity and run basic checks

### Testing & Quality
- **`run_tests.py`**: Advanced test runner with multiple report formats
- **`add_copyright_headers.sh`**: Apply MIT license headers to source files

### Python Testing
- **`run_tests.py`**: Python test runner (in tests/python/)

## Script Usage

### Basic Setup
```bash
# Install basic build dependencies (required)
./scripts/setup_deps.sh

# Install advanced development tools (recommended)
./scripts/install_dev_tools.sh
```

### Testing
```bash
# Run comprehensive test suite
./scripts/run_tests.py --rebuild --coverage --report-format console

# Run with static analysis (requires clang-tidy/cppcheck)
./scripts/run_tests.py --static-analysis

# Clean rebuild with all checks
./scripts/run_tests.py --clean --rebuild --static-analysis --coverage --format-code
```

### Maintenance
```bash
# Clean build artifacts
./scripts/clean_build.sh

# Add copyright headers to new files
./scripts/add_copyright_headers.sh

# Verify build integrity
./scripts/verify_build.sh
```

## Script Details

### setup_deps.sh
**Purpose**: Install basic build dependencies
- **Linux**: build-essential, cmake, clang
- **macOS**: cmake, llvm (via Homebrew)
- **Windows**: Manual installation guide

### install_dev_tools.sh
**Purpose**: Install advanced development tools for professional workflow
- **Static Analysis**: clang-tidy, clang-format, cppcheck
- **Coverage**: gcovr, lcov
- **Python Testing**: pytest, pytest-cov
- **Auto-detection**: OS-specific package managers

### run_tests.py
**Purpose**: Advanced test runner with comprehensive reporting
- **Multi-format Reports**: JUnit XML, HTML coverage, JSON
- **Selective Testing**: Filter by test name or category
- **Quality Checks**: Static analysis, code formatting
- **CI/CD Ready**: Jenkins/GitLab/Azure DevOps compatible

### clean_build.sh
**Purpose**: Clean build artifacts and cache
- **Safe Cleaning**: Preserves source code
- **Cache Clearing**: Removes CMake cache and FetchContent downloads

### add_copyright_headers.sh
**Purpose**: Apply MIT license headers to source files
- **Batch Processing**: Handles all C++/Python files
- **Smart Detection**: Skips files that already have headers
- **Include Guards**: Adds proper C++ header guards

## Development Workflow

1. **Initial Setup**:
   ```bash
   ./scripts/setup_deps.sh        # Basic dependencies
   ./scripts/install_dev_tools.sh # Advanced tools (optional)
   ```

2. **Daily Development**:
   ```bash
   ./scripts/run_tests.py --rebuild  # Quick test cycle
   ```

3. **Quality Assurance**:
   ```bash
   ./scripts/run_tests.py --clean --rebuild --static-analysis --coverage --format-code
   ```

4. **Maintenance**:
   ```bash
   ./scripts/clean_build.sh       # Clean workspace
   ./scripts/add_copyright_headers.sh  # Update license headers
   ```

## Error Handling

All scripts include:
- **Input validation**
- **Error checking** with clear messages
- **Safe operations** with minimal side effects
- **Help text** and usage examples

## Platform Support

- **Linux**: apt, yum package managers
- **macOS**: Homebrew package manager
- **Windows**: Manual installation with guidance
- **Cross-platform**: Python scripts work everywhere
