<!--
  Copyright (c) 2025 Vinicius Tadeu Zein

  See the NOTICE file(s) distributed with this work for additional
  information regarding copyright ownership.

  This program and the accompanying materials are made available under the
  terms of the Apache License Version 2.0 which is available at
  https://www.apache.org/licenses/LICENSE-2.0

  SPDX-License-Identifier: Apache-2.0
-->

# Source Code Implementation

This directory contains the implementation source code for the SOME/IP stack. Code is organized by functional modules with clear separation of concerns.

## Subdirectories

### `core/`
Core protocol implementation:
- Message header processing
- RPC request/response handling
- Event notification system
- Session management

### `transport/`
Transport layer implementations:
- UDP socket management
- TCP connection handling
- Multicast support
- Socket pooling and lifecycle

### `sd/`
Service Discovery implementation:
- SD message processing
- Service advertisement
- Service discovery queries
- Subscription management
- TTL-based cleanup

### `tp/`
Transport Protocol implementation:
- Message segmentation
- Reassembly algorithms
- Segment ordering and validation

### `serialization/`
Data serialization implementations:
- Type-specific serializers
- Deserialization logic
- Array and structure handling
- Endianness conversion

### `common/`
Common utilities and infrastructure:
- Error handling implementation
- Logging framework
- Memory management
- Threading utilities

### `safety/`
Safety-critical components:
- Fault detection and containment
- Error recovery mechanisms
- Safety monitors
- Diagnostic interfaces

### `config/`
Configuration management:
- Service configuration parsing
- Network configuration
- Runtime reconfiguration
- Configuration validation

## Implementation Principles

### Safety-Critical Design
- **Defensive Programming**: All inputs validated, defensive coding practices
- **Error Containment**: Faults isolated to prevent system-wide failures
- **Resource Management**: Deterministic memory and resource usage
- **Thread Safety**: All shared state properly synchronized

### Code Quality
- **Modular Design**: Clear interfaces and separation of concerns
- **Testability**: Code designed for comprehensive testing
- **Maintainability**: Clear documentation and consistent patterns
- **Performance**: Optimized for embedded systems

### Error Handling
- **Return Codes**: All functions return status codes
- **Exception Safety**: RAII patterns for resource management
- **Logging**: Comprehensive error logging with context
- **Recovery**: Graceful degradation and recovery mechanisms

## Build Organization

Source files are compiled into static libraries:
- `libsomeip-core.a` - Core protocol
- `libsomeip-transport.a` - Transport layer
- `libsomeip-sd.a` - Service discovery
- `libsomeip-tp.a` - Transport protocol
- `libsomeip-serialization.a` - Serialization
- `libsomeip-common.a` - Common utilities

## Safety Alignment (non-certified)

Code in this directory is designed to support:
- **MISRA C++** compliance guidelines
- **CERT C++** secure coding standards
- **AUTOSAR** C++ compliance
- Additional measures would be required for any safety certification
