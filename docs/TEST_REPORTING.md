<!--
  Copyright (c) 2025 Vinicius Tadeu Zein

  See the NOTICE file(s) distributed with this work for additional
  information regarding copyright ownership.

  This program and the accompanying materials are made available under the
  terms of the Apache License Version 2.0 which is available at
  https://www.apache.org/licenses/LICENSE-2.0

  SPDX-License-Identifier: Apache-2.0
-->

# Test Reporting and CI/CD Integration

## Overview

The SOME/IP Stack provides comprehensive test reporting capabilities designed for both development and CI/CD environments. All reports follow industry standards for seamless integration with popular CI/CD platforms.

## Report Types

### 1. JUnit XML Reports

**Location**: `build/junit_results.xml`

**Purpose**: Standard test results format compatible with Jenkins, GitLab CI, Azure DevOps, and other CI/CD systems.

**Format**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="(empty)"
	tests="9"
	failures="3"
	disabled="0"
	skipped="0"
	hostname=""
	time="3"
	timestamp="2025-12-12T15:39:59"
	>
	<testcase name="SerializationTest" classname="SerializationTest" time="0.332449" status="run">
		<!-- Test details -->
	</testcase>
</testsuite>
```

**Generation**: Automatically created by CTest with `--output-junit` flag.

### 2. Code Coverage Reports

**Location**: `build/coverage/index.html`

**Purpose**: Detailed HTML coverage reports showing line-by-line and branch coverage.

**Requirements**:
```bash
pip install gcovr
```

**Generation**:
```bash
./scripts/run_tests.py --rebuild --coverage
```

**Features**:
- Line coverage percentages
- Branch coverage analysis
- File-by-file breakdown
- Interactive HTML interface

### 3. JSON Test Reports

**Location**: `build/test_report.json`

**Purpose**: Machine-readable test results for custom processing and analysis.

**Format**:
```json
{
  "timestamp": "2025-12-12 15:41:08",
  "build_directory": "/path/to/build",
  "results": {
    "unit_tests": {
      "total": 9,
      "passed": 6,
      "failed": 3,
      "junit_xml": "/path/to/junit_results.xml"
    },
    "coverage": {
      "line_rate": 0.85,
      "branch_rate": 0.78,
      "html_report": "/path/to/coverage/index.html"
    }
  }
}
```

### 4. Python Test Reports

**Location**: `tests/python/junit_results.xml`

**Purpose**: JUnit XML reports for Python integration tests.

**Configuration**: pytest.ini includes:
```ini
--junitxml=junit_results.xml
--cov=someip
--cov-report=html:htmlcov
--cov-report=xml
```

## CI/CD Integration Examples

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mkdir build && cd build && cmake .. && make'
            }
        }
        stage('Test') {
            steps {
                sh './scripts/run_tests.py --rebuild --coverage'
            }
            post {
                always {
                    junit 'build/junit_results.xml'
                    publishHTML(target: [
                        reportDir: 'build/coverage',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                    publishHTML(target: [
                        reportDir: 'tests/python/htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Python Coverage'
                    ])
                }
            }
        }
    }
}
```

### GitLab CI

```yaml
test:
  stage: test
  script:
    - ./scripts/run_tests.py --rebuild --coverage
  artifacts:
    reports:
      junit: build/junit_results.xml
      coverage_report:
        coverage_format: cobertura
        path: tests/python/coverage.xml
    paths:
      - build/coverage/
    expire_in: 1 week
```

### GitHub Actions

```yaml
- name: Run tests
  run: ./scripts/run_tests.py --rebuild --coverage

- name: Upload test results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: |
      build/junit_results.xml
      build/coverage/
      tests/python/junit_results.xml

- name: Publish Test Results
  uses: EnricoMi/publish-unit-test-result-action@v2
  with:
    files: |
      build/junit_results.xml
      tests/python/junit_results.xml
```

## Coverage Tools

### gcovr (Recommended)

```bash
# Install
pip install gcovr

# Generate reports
gcovr --root . --exclude tests/ --exclude examples/ --html --html-details --output coverage/index.html

# Text summary
gcovr --root . --exclude tests/ --exclude examples/ --print-summary
```

### Installation on Different Platforms

#### macOS
```bash
# Using Homebrew
brew install llvm cppcheck
pip install gcovr pytest pytest-cov

# Verify installation
which clang-tidy clang-format cppcheck gcovr pytest
```

#### Ubuntu/Debian
```bash
# Install system packages
sudo apt update
sudo apt install clang-tidy clang-format cppcheck lcov

# Install Python packages
pip install gcovr pytest pytest-cov

# Verify installation
which clang-tidy clang-format cppcheck gcovr lcov pytest
```

#### Windows (MSVC)
```bash
# Using vcpkg for clang tools
vcpkg install llvm cppcheck

# Install Python packages
pip install gcovr pytest pytest-cov

# Add to PATH or use full paths
```

### Current System Status

Based on the test run, the following tools are **missing** on your system:

- ❌ **clang-tidy**: Static analysis and code quality
- ❌ **clang-format**: Code formatting
- ❌ **cppcheck**: Additional static analysis
- ❌ **gcovr**: Professional coverage reports
- ❌ **pytest**: Python testing framework

**Available tools:**
- ✅ **gcov**: Basic coverage data collection (GCC built-in)
- ✅ **CTest**: Test execution framework
- ✅ **JUnit XML**: Test result reporting

### Tool Integration

The test script automatically detects and uses the best available tools:

1. **Static Analysis**: clang-tidy → cppcheck → (none)
2. **Coverage**: gcovr → lcov → basic gcov → (none)
3. **Python Tests**: pytest → (none)

### Recommended Setup

For a complete development environment, install:

```bash
# Core development tools
pip install gcovr pytest pytest-cov

# System tools (choose based on your OS)
# macOS: brew install llvm cppcheck
# Ubuntu: sudo apt install clang-tidy clang-format cppcheck lcov
```

### lcov (Alternative)

```bash
# Install (Ubuntu/Debian)
sudo apt-get install lcov

# Generate coverage
lcov --capture --directory build --output-file coverage.info
lcov --remove coverage.info '/usr/*' '*/tests/*' '*/examples/*' --output-file coverage.info

# Generate HTML
genhtml coverage.info --output-directory coverage-html/
```

### Coverage Configuration

**CMake Coverage Flags**:
```cmake
if(COVERAGE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fprofile-arcs -ftest-coverage -O0")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fprofile-arcs -ftest-coverage")
endif()
```

## Test Execution Options

### Selective Test Execution

```bash
# Run specific test suites
./scripts/run_tests.py --filter "*Message*" --unit-only

# Run integration tests only
./scripts/run_tests.py --integration-only

# Run with static analysis
./scripts/run_tests.py --static-analysis

# Clean rebuild with all checks
./scripts/run_tests.py --clean --rebuild --static-analysis --coverage --format-code
```

### Report Formats

```bash
# Console output (default)
./scripts/run_tests.py --report-format console

# JSON output
./scripts/run_tests.py --report-format json

# Both (console shows paths to files)
./scripts/run_tests.py --report-format json
```

## Quality Gates

### Recommended CI Checks

1. **Test Success Rate**: >95% tests passing
2. **Coverage Thresholds**:
   - Line coverage: >85%
   - Branch coverage: >80%
3. **Static Analysis**: Zero errors from clang-tidy
4. **Code Formatting**: Compliant with clang-format

### Quality Metrics

```bash
# Generate comprehensive quality report
./scripts/run_tests.py --clean --rebuild --static-analysis --coverage --format-code --report-format json

# Check coverage thresholds
python3 -c "
import json
with open('build/test_report.json') as f:
    data = json.load(f)
    cov = data['results'].get('coverage', {})
    if cov.get('line_rate', 0) < 0.85:
        exit(1)
    print(f'Coverage: {cov.get(\"line_rate\", 0):.1%}')
"
```

## Troubleshooting

### Common Issues

**JUnit XML not generated**:
- Ensure CTest is run with `--output-junit`
- Check build directory permissions

**Coverage reports empty**:
- Build with `-DCOVERAGE=ON`
- Ensure gcovr is installed
- Check that tests actually run

**Python tests not found**:
- Install pytest: `pip install pytest pytest-cov`
- Check test file locations match pytest.ini patterns

### Report Locations

```
build/
├── junit_results.xml          # C++ test results
├── coverage/
│   └── index.html            # C++ coverage report
└── test_report.json          # Combined test report

tests/python/
├── junit_results.xml         # Python test results
├── htmlcov/
│   └── index.html           # Python coverage report
└── coverage.xml             # Python coverage (Cobertura format)
```

## Integration with Test Frameworks

### Google Test (C++)

- **Output**: JUnit XML via CTest
- **Coverage**: gcov/lcov integration
- **Filtering**: `--filter` option support

### pytest (Python)

- **Output**: JUnit XML via `--junitxml`
- **Coverage**: pytest-cov plugin
- **Markers**: Custom test categorization

### Custom Test Frameworks

The test runner script can be extended to support additional test frameworks by:

1. Adding new `_run_<framework>_tests()` methods
2. Implementing `_parse_<framework>_output()` methods
3. Updating the report generation to include framework-specific results

## Best Practices

1. **Always run tests before commits**
2. **Use CI/CD for automated quality checks**
3. **Monitor coverage trends over time**
4. **Archive test reports for historical analysis**
5. **Set up quality gates for pull requests**

---

*This reporting system ensures comprehensive test visibility and CI/CD integration for professional software development workflows.*
