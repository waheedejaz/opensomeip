# Multi-Service Example

This advanced example demonstrates a server offering multiple SOME/IP services simultaneously, showing enterprise-level service architecture patterns.

## Overview

The Multi-Service example showcases a comprehensive server that provides four distinct services:

- **Calculator Service**: Mathematical operations with history tracking
- **Filesystem Service**: File operations simulation with in-memory storage
- **Sensor Service**: Environmental sensor data with event publishing
- **System Service**: System information and management functions

This demonstrates how to architect complex SOME/IP applications with multiple service interfaces.

## Architecture

### Service Organization
```
Multi-Service Server
├── Calculator Service (0x6001)
│   ├── add(a, b) → sum
│   ├── subtract(a, b) → difference
│   ├── multiply(a, b) → product
│   ├── divide(a, b) → quotient
│   └── get_history() → calculation log
│
├── Filesystem Service (0x6002)
│   ├── list_dir() → file listing
│   ├── read_file(path) → file content
│   ├── write_file(path, data) → success status
│   ├── delete_file(path) → success status
│   └── get_file_info(path) → file metadata
│
├── Sensor Service (0x6003)
│   ├── get_readings() → sensor data
│   ├── set_config(config) → status
│   ├── calibrate() → status
│   └── Events: Temperature, Humidity, Pressure
│
└── System Service (0x6004)
    ├── get_info() → system information
    ├── get_load() → system metrics
    ├── shutdown() → status
    └── restart() → status
```

## Files

- `server.cpp` - Multi-service server implementation
- `client.cpp` - Multi-service client demonstrating all services
- `README.md` - This documentation

## Running the Example

## Building the Example

First, build the entire project from the main directory:

```bash
# From the project root directory
mkdir build && cd build
cmake ..
make
```

## Running the Example

### Terminal 1 - Start the Multi-Service Server
```bash
# From the project root directory (after building)
./build/bin/multi_service_server
```

You should see:
```
=== SOME/IP Multi-Service Server ===
Multi-Service Server initialized successfully!
Available services:
  - Calculator Service (0x6001)
  - Filesystem Service (0x6002)
  - Sensor Service (0x6003)
  - System Service (0x6004)
Multi-Service Server running. Press Ctrl+C to exit.
All services are active and accepting requests...
[CALCULATOR] ADD: 15 + 27 = 42
[FILESYSTEM] Wrote file: /data/user_data.txt (45 bytes)
[SENSOR] Readings - Temp: 24.7°C, Humidity: 58.3%, Pressure: 1012.8 hPa
```

### Terminal 2 - Run the Multi-Service Client
```bash
# From the project root directory (after building)
./build/bin/multi_service_client
```

The client will demonstrate interactions with all four services:
- Calculator operations and history retrieval
- Filesystem operations (list, read, write, info)
- Sensor configuration and readings
- System information and load metrics
- Sensor event subscription and reception

## What This Example Demonstrates

1. **Multi-Service Architecture**: Managing multiple service interfaces in one application
2. **Service Isolation**: Each service operates independently with separate state
3. **Event Integration**: Combining RPC services with event publishing
4. **Resource Management**: Proper initialization and cleanup of multiple services
5. **Concurrent Operations**: Handling simultaneous requests to different services
6. **State Management**: Maintaining service-specific state and configuration

## Service Details

### Calculator Service (0x6001)

**Methods:**
- `add(int32, int32) → int32`: Integer addition
- `subtract(int32, int32) → int32`: Integer subtraction
- `multiply(int32, int32) → int32`: Integer multiplication
- `divide(int32, int32) → int32`: Integer division (with zero check)
- `get_history() → string`: Returns last 10 calculations

**Features:**
- Input validation and error handling
- Calculation history tracking
- Thread-safe operations

### Filesystem Service (0x6002)

**Methods:**
- `list_dir() → string`: Lists all files in the virtual filesystem
- `read_file(string) → buffer`: Reads file content
- `write_file(string, buffer) → status`: Writes file content
- `delete_file(string) → status`: Deletes a file
- `get_file_info(string) → string`: Returns file metadata

**Features:**
- In-memory file storage simulation
- Null-terminated string handling for filenames
- File existence checking
- Thread-safe file operations

### Sensor Service (0x6003)

**Methods:**
- `get_readings() → struct{temp, humidity, pressure}`: Current sensor values
- `set_config(struct{enables, interval}) → status`: Configure sensor behavior
- `calibrate() → status`: Perform sensor calibration

**Events:**
- `Temperature (0x8001)`: Periodic temperature readings
- `Humidity (0x8002)`: Periodic humidity readings
- `Pressure (0x8003)`: Periodic pressure readings

**Features:**
- Configurable sensor enable/disable
- Adjustable update intervals
- Event publishing integration
- Simulated sensor data generation

### System Service (0x6004)

**Methods:**
- `get_info() → string`: System identification and status
- `get_load() → struct{cpu, memory, connections}`: System performance metrics
- `shutdown() → status`: System shutdown request
- `restart() → status`: System restart request

**Features:**
- System information reporting
- Load simulation and monitoring
- Administrative operation simulation

## Client Architecture

The client demonstrates comprehensive service integration:

### Service Discovery
- Connects to all four services simultaneously
- Subscribes to sensor events
- Maintains separate connections for each service

### Operation Sequencing
- Calculator operations with result verification
- Filesystem operations (create, read, modify, delete)
- Sensor configuration and monitoring
- System status checking

### Event Handling
- Subscribes to all sensor events
- Processes events asynchronously
- Displays real-time sensor data

## Protocol Details

### Service IDs and Methods
```
Calculator: 0x6001
├── 0x0001: add
├── 0x0002: subtract
├── 0x0003: multiply
├── 0x0004: divide
└── 0x0005: get_history

Filesystem: 0x6002
├── 0x0001: list_dir
├── 0x0002: read_file
├── 0x0003: write_file
├── 0x0004: delete_file
└── 0x0005: get_file_info

Sensor: 0x6003
├── 0x0001: get_readings
├── 0x0002: set_config
├── 0x0003: calibrate
├── 0x8001: temperature_event
├── 0x8002: humidity_event
└── 0x8003: pressure_event

System: 0x6004
├── 0x0001: get_info
├── 0x0002: get_load
├── 0x0003: shutdown
└── 0x0004: restart
```

### Data Serialization
- **Primitives**: Big-endian integers and floats
- **Strings**: Length-prefixed UTF-8 byte arrays
- **Arrays**: Size-prefixed element sequences
- **Structs**: Sequential field serialization

## Design Patterns

### Service Isolation
Each service maintains separate:
- State and configuration
- Method handlers
- Resource management
- Error handling

### Thread Safety
- Mutex-protected shared resources
- Atomic operations for counters
- Safe concurrent access to services

### Event-Driven Architecture
- Sensor events published asynchronously
- Client processes events in real-time
- Decoupled producer-consumer pattern

## Enterprise Applications

This pattern is commonly used in:

### Automotive Systems
- **ECU Integration**: Multiple ECUs offering different services
- **Vehicle Networks**: Sensors, actuators, and control units
- **Diagnostic Services**: Multiple diagnostic interfaces

### Industrial Automation
- **PLC Systems**: Multiple programmable logic controllers
- **Sensor Networks**: Distributed sensor data collection
- **SCADA Systems**: Supervisory control and data acquisition

### IoT Gateways
- **Device Management**: Multiple device service interfaces
- **Protocol Translation**: Converting between different protocols
- **Data Aggregation**: Collecting data from multiple sources

## Performance Considerations

### Resource Management
- **Memory**: Each service maintains separate state
- **CPU**: Concurrent request processing
- **Network**: Multiple service endpoints

### Scalability
- **Service Count**: Easily add new services
- **Client Load**: Handle multiple simultaneous clients
- **Event Frequency**: Configurable event publishing rates

## Testing and Validation

### Unit Testing
- Individual service method testing
- Event publishing verification
- Serialization/deserialization validation

### Integration Testing
- Multi-service interaction testing
- Event subscription and reception
- Concurrent client handling

### Load Testing
- Multiple client connections
- High-frequency event publishing
- Large data transfer handling

## Next Steps

After understanding multi-service architecture, explore:
- [Hello World Example](../../basic/hello_world/) - Basic SOME/IP concepts
- [Large Messages Example](../large_messages/) - TP for oversized data
