<!--
  Copyright (c) 2025 Vinicius Tadeu Zein

  See the NOTICE file(s) distributed with this work for additional
  information regarding copyright ownership.

  This program and the accompanying materials are made available under the
  terms of the Apache License Version 2.0 which is available at
  https://www.apache.org/licenses/LICENSE-2.0

  SPDX-License-Identifier: Apache-2.0
-->

# Examples and Tutorials

This directory contains examples and tutorials demonstrating how to use the SOME/IP stack implementation in various scenarios.

## Example Categories

### Basic Examples
- **Hello World**: Simple client-server communication
- **Method Calls**: Basic RPC request/response patterns
- **Event Notifications**: Server-to-client event publishing
- **Service Discovery**: Dynamic service location

### Advanced Examples
- **Complex Data Types**: Arrays, structures, and nested types
- **Large Messages**: SOME/IP-TP segmentation usage
- **Multiple Services**: Managing multiple service instances
- **Error Handling**: Robust error handling patterns

### Safety-Oriented Examples (non-certified)
- **Fault Tolerant Design**: Error detection and recovery
- **Resource Management**: Memory and resource constraints
- **Monitoring**: Health monitoring and diagnostics
- **Certification Patterns**: Safety-aligned usage patterns (not ASIL-certified)

## Tutorial Structure

Each example includes:
- **README.md**: Explanation of the example and how to run it
- **Source Code**: Complete, compilable example code
- **CMakeLists.txt**: Build configuration
- **Configuration Files**: Service definitions and network config

## Example Organization

### Directory Structure
```
examples/
├── basic/                    # Fundamental SOME/IP concepts
│   ├── hello_world/         # Basic client-server message exchange
│   ├── method_calls/        # RPC with parameters and return values
│   └── events/              # Publish-subscribe pattern
├── advanced/                # Advanced SOME/IP features
│   ├── complex_types/       # Complex data structures and serialization
│   ├── large_messages/      # TP for messages > MTU
│   └── multi_service/       # Multiple services in one application
├── [future: safety/]        # Safety-critical examples
└── [future: tutorials/]     # Learning-oriented examples
```

### Example Categories

#### Basic Examples - Getting Started
These examples introduce core SOME/IP concepts with simple, focused implementations:

- **[Hello World](../basic/hello_world/)**: Simplest client-server message exchange
- **[Method Calls](../basic/method_calls/)**: RPC patterns with parameters and results
- **[Events](../basic/events/)**: Publish-subscribe event distribution

#### Advanced Examples - Production Features
These examples demonstrate enterprise-level SOME/IP capabilities:

- **[Complex Types](../advanced/complex_types/)**: Advanced serialization of structs and arrays
- **[Large Messages](../advanced/large_messages/)**: TP protocol for oversized data
- **[Multi-Service](../advanced/multi_service/)**: Multiple services in one application

### Learning Path
```
Start Here → Hello World → Method Calls → Events → Complex Types → Large Messages → Multi-Service
    ↓           ↓           ↓         ↓         ↓             ↓              ↓
Concepts   Basic       RPC      Pub/Sub   Structs       TP         Enterprise
           Messages    Calls     Events   Arrays       Protocol     Architecture
```

## Running Examples

### Prerequisites
- Build the SOME/IP libraries
- Network interface configured for SOME/IP multicast
- Appropriate permissions for socket operations

### Build and Run
```bash
# From project root - build all examples
mkdir build && cd build
cmake .. && make

# Quick start - Hello World example
./build/bin/hello_world_server &
./build/bin/hello_world_client
```

### Individual Example Commands
```bash
# Build examples (from build directory)
make hello_world_server hello_world_client
make method_calls_server method_calls_client
make complex_types_server complex_types_client
make large_messages_server large_messages_client
make multi_service_server multi_service_client

# Run examples (from project root)
./build/bin/hello_world_server &
./build/bin/hello_world_client

./build/bin/method_calls_server &
./build/bin/method_calls_client

# ... etc for other examples
```

## Learning Path

### Start with the Basics
```
1. Hello World      → Basic client-server message exchange
2. Method Calls     → RPC with parameters and return values
3. Events          → Publish-subscribe notification patterns
```

### Advanced Features
```
4. Complex Types   → Structs, arrays, and custom serialization
5. Large Messages  → TP protocol for oversized data
6. Multi-Service   → Enterprise service architecture
```

### Recommended Order
- **New to SOME/IP**: Start with Hello World → Method Calls → Events
- **Experienced**: Jump to Complex Types → Large Messages → Multi-Service
- **Production Ready**: Study all examples for comprehensive understanding

## Safety Considerations (non-certified)

Examples demonstrate:
- **Initialization**: Proper setup and cleanup
- **Error Handling**: Comprehensive error checking
- **Resource Management**: Deterministic resource usage
- **Thread Safety**: Safe concurrent operations

## Testing Examples

Each example includes:
- **Unit Tests**: Testing individual components
- **Integration Tests**: End-to-end validation
- **Performance Benchmarks**: Measuring example performance

## Contributing Examples

When adding new examples:
- Follow the established directory structure
- Include comprehensive documentation
- Provide both client and server implementations
- Demonstrate best practices and safety patterns
- Include test cases and performance measurements
