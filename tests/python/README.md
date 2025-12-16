<!--
  Copyright (c) 2025 Vinicius Tadeu Zein

  See the NOTICE file(s) distributed with this work for additional
  information regarding copyright ownership.

  This program and the accompanying materials are made available under the
  terms of the Apache License Version 2.0 which is available at
  https://www.apache.org/licenses/LICENSE-2.0

  SPDX-License-Identifier: Apache-2.0
-->

# SOME/IP Python Testing Framework

This directory contains the Python-based testing framework for comprehensive SOME/IP stack validation, complementing the C++ unit tests with integration and system-level testing.

## Overview

The Python testing framework provides:

- **Integration Tests**: Multi-component interaction testing
- **System Tests**: End-to-end protocol validation
- **Performance Tests**: Load and timing measurements
- **Conformance Tests**: Protocol compliance validation

## Setup

### Install Dependencies

```bash
# Install Python testing dependencies
pip install -r requirements.txt

# Or install individually
pip install pytest pytest-asyncio pytest-cov pytest-xdist
```

### Verify Setup

```bash
# Check pytest installation
python -m pytest --version

# Run a simple test to verify framework works
python -m pytest --collect-only
```

## Test Structure

```
tests/python/
├── someip_test_framework.py    # Core testing utilities
├── conftest.py                 # Pytest fixtures and configuration
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── run_tests.py               # Test runner script
└── README.md                  # This file

tests/integration/              # Integration tests
├── test_echo_integration.py   # Echo protocol tests
└── ...                       # More integration tests

tests/system/                  # System tests
├── test_full_stack_integration.py  # End-to-end tests
└── ...                       # More system tests
```

## Running Tests

### Quick Start

```bash
# Run all Python tests
python run_tests.py

# Or run specific test categories
python -m pytest ../integration/ -v
python -m pytest ../system/ -v
```

### Test Categories

#### Integration Tests

Test multi-component interactions:

```bash
# Run all integration tests
python -m pytest ../integration/ -v

# Run specific integration test
python -m pytest ../integration/test_echo_integration.py::test_echo_message_flow -v
```

#### System Tests

Test complete end-to-end functionality:

```bash
# Run all system tests
python -m pytest ../system/ -v

# Run with detailed output
python -m pytest ../system/ -v -s
```

#### Performance Tests

Measure throughput and latency:

```bash
# Run performance tests only
python -m pytest ../system/ -k performance -v
```

## Test Examples

### Basic Integration Test

```python
import pytest
from someip_test_framework import someip_test_scenario

@pytest.mark.integration
@pytest.mark.asyncio
async def test_basic_communication(echo_scenario):
    """Test basic client-server communication"""
    async with someip_test_scenario(echo_scenario) as scenario:
        client = scenario.clients[0]

        # Send test message
        test_message = b"Hello SOME/IP"
        success = client.send_message(test_message)

        # Receive response
        response = client.receive_message(timeout=1.0)

        assert success
        assert response == test_message
```

### System Test with Multiple Processes

```python
@pytest.mark.system
def test_service_discovery_flow(sd_scenario):
    """Test complete SD discover-connect-communicate flow"""
    with someip_test_scenario(sd_scenario) as scenario:
        # Test automatically starts SD server and client
        # Validates service discovery, connection, and communication

        # Check that all processes completed successfully
        for process in scenario.processes:
            assert process.returncode == 0
```

## Framework Features

### Test Scenarios

Pre-configured test scenarios for common testing patterns:

```python
# Echo server/client scenario
def echo_scenario(echo_server_executable, echo_client_executable, localhost_endpoint)

# RPC calculator scenario
def rpc_scenario(rpc_server_executable, rpc_client_executable, localhost_endpoint)

# Service Discovery scenario
def sd_scenario(sd_server_executable, sd_client_executable, multicast_endpoint, localhost_endpoint)

# Event publish/subscribe scenario
def event_scenario(event_publisher_executable, event_subscriber_executable)
```

### Process Management

Automatic process lifecycle management:

```python
# Processes start automatically
async with someip_test_scenario(scenario) as running_scenario:
    # Test your functionality here
    pass
# Processes stop automatically
```

### Network Testing

Built-in network utilities:

```python
# Create test endpoints
endpoint = SomeIpEndpoint("127.0.0.1", 8888)

# Create test clients
client = SomeIpTestClient(endpoint)
client.connect()
client.send_message(data)
response = client.receive_message()
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = .
python_files = test_*.py *_test.py
addopts = --strict-markers --tb=short -ra
markers =
    integration: Integration tests
    system: System-level tests
    performance: Performance tests
    conformance: Protocol conformance tests
```

### Custom Markers

- `@pytest.mark.integration` - Multi-component tests
- `@pytest.mark.system` - End-to-end tests
- `@pytest.mark.performance` - Performance benchmarks
- `@pytest.mark.conformance` - Protocol compliance tests
- `@pytest.mark.async` - Async tests
- `@pytest.mark.slow` - Tests taking >30 seconds

## Advanced Usage

### Parallel Test Execution

Run tests in parallel for faster execution:

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
python -m pytest -n auto ../integration/
```

### Coverage Analysis

Generate code coverage reports:

```bash
# Install coverage
pip install pytest-cov

# Generate coverage report
python -m pytest --cov=../../src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Custom Test Fixtures

Create custom test scenarios:

```python
@pytest.fixture
def custom_scenario(build_bin_path):
    scenario = TestScenario("custom", "Custom test scenario")

    # Add your processes
    scenario.add_process(build_bin_path / "my_server")
    scenario.add_process(build_bin_path / "my_client")

    # Add clients
    scenario.add_client(SomeIpEndpoint("127.0.0.1", 9999))

    return scenario
```

## Best Practices

### Test Organization

1. **Unit Tests (C++)**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **System Tests**: Test complete workflows
4. **Performance Tests**: Measure and validate performance

### Test Naming

```python
def test_<component>_<functionality>_<condition>():
    """Test description"""
```

Examples:
- `test_echo_message_flow()`
- `test_sd_service_discovery_timeout()`
- `test_rpc_concurrent_requests()`

### Assertions

Use descriptive assertions:

```python
# Good
assert response.return_code == ReturnCode.E_OK, "RPC call should succeed"

# Better
assert response.return_code == ReturnCode.E_OK, \
    f"RPC call failed: expected E_OK, got {response.return_code}"
```

## Troubleshooting

### Common Issues

1. **Executables not found**: Build the project first
   ```bash
   cd build && make -j$(nproc)
   ```

2. **Port conflicts**: Tests use automatic port allocation
3. **Timing issues**: Increase timeouts for slow systems
4. **Process cleanup**: Framework handles automatic cleanup

### Debug Output

Enable debug output:

```bash
# Run with verbose output
python -m pytest -v -s

# Run single test with debugging
python -m pytest test_specific.py::test_function -s --pdb
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run Python Tests
  run: |
    cd tests/python
    pip install -r requirements.txt
    python -m pytest ../integration/ ../system/ -v --junitxml=results.xml

- name: Upload Test Results
  uses: actions/upload-artifact@v2
  with:
    name: test-results
    path: tests/python/results.xml
```

This Python testing framework provides comprehensive validation of your SOME/IP stack, ensuring protocol compliance, performance requirements, and reliability across all components.
