# Complex Types Example

This advanced example demonstrates serialization and deserialization of complex data types in SOME/IP, including structures, arrays, and nested data.

## Overview

The Complex Types example showcases advanced serialization techniques:
- **Vehicle Data Processing**: Complex struct with mixed data types
- **Sensor Array Retrieval**: Variable-length arrays of complex objects
- **Struct Echo**: Round-trip serialization verification

## Data Structures Demonstrated

### VehicleData Structure
```cpp
struct VehicleData {
    uint32_t vehicle_id;           // 32-bit identifier
    std::string model;             // Variable-length string
    float fuel_level;              // 32-bit float (0.0-1.0)
    uint8_t tire_pressure[4];      // Fixed-size array
    bool lights_on;                // Boolean flag
    uint16_t mileage;              // 16-bit integer
};
```

### SensorReading Structure
```cpp
struct SensorReading {
    uint8_t sensor_id;             // 8-bit identifier
    float value;                   // 32-bit measurement value
    std::string unit;              // Variable-length unit string
    uint32_t timestamp;            // 32-bit timestamp
};
```

### SensorArray Structure
```cpp
struct SensorArray {
    uint32_t array_size;           // Array length
    std::vector<SensorReading> sensors; // Variable-length array of structs
};
```

## Files

- `server.cpp` - Server implementing complex type processing methods
- `client.cpp` - Client demonstrating serialization and deserialization
- `README.md` - This documentation

## Running the Example

### Terminal 1 - Start the Server
```bash
cd examples/advanced/complex_types
make server
./server
```

You should see:
```
=== SOME/IP Complex Types Server ===
Complex Types Server initialized for service 0x4000
Available methods:
  - 0x0001: process_vehicle_data(VehicleData) -> string
  - 0x0002: get_sensor_array() -> SensorArray
  - 0x0003: echo_complex_struct(SensorReading) -> SensorReading
Complex Types Server running. Press Ctrl+C to exit.
```

### Terminal 2 - Run the Client
```bash
cd examples/advanced/complex_types
make client
./client
```

You should see output demonstrating:
1. **Vehicle Data Processing**: Complex struct serialization and server-side processing
2. **Sensor Array Retrieval**: Array of complex objects with variable-length strings
3. **Struct Echo**: Round-trip verification of complex data serialization

## What This Example Demonstrates

1. **Complex Structure Serialization**: Converting C++ structs to SOME/IP wire format
2. **Array Handling**: Fixed-size arrays, variable-length arrays, and nested structures
3. **Mixed Data Types**: Combining primitives, strings, and complex types
4. **Big-Endian Encoding**: Proper network byte order for all data types
5. **Length Prefixing**: Variable-length data with explicit length fields
6. **Round-Trip Verification**: Ensuring serialization/deserialization consistency
7. **Error Handling**: Robust error checking in complex data processing

## Serialization Details

### SOME/IP Wire Format
All data follows SOME/IP big-endian encoding:
- **Integers**: Network byte order (big-endian)
- **Floats**: IEEE 754 in big-endian byte order
- **Strings**: Length-prefixed UTF-8 byte arrays
- **Arrays**: Length-prefixed sequences of elements
- **Structs**: Sequential field serialization

### VehicleData Wire Format
```
+------------+--------+--------+-----+-----+-----+-----+-----+-----+--------+
| vehicle_id | model  | fuel_  | tire| tire| tire| tire|     |        |
|   (4)      | length | level  | [0] | [1] | [2] | [3] |     | mileage|
|            |  (4)   |  (4)   | (1) | (1) | (1) | (1) | (1) |  (2)   |
+------------+--------+--------+-----+-----+-----+-----+-----+--------+
|  0x00003039| 0x0000000E | 0x3F59999A | 0x20| 0x21| 0x1F| 0x22| 0x01| 0xB09E|
+------------+--------+--------+-----+-----+-----+-----+-----+--------+
```

### SensorReading Wire Format
```
+------------+--------+--------+-----+--------+--------+
| sensor_id  | value  | unit   | ... |timestamp|
|    (1)     |  (4)   | length |     |  (4)    |
|            |        |  (4)   |     |         |
+------------+--------+--------+-----+--------+--------+
|    0x2A    |0x42C6CCCD| 0x00000002| "°F"| 0x499602D2|
+------------+--------+--------+-----+--------+--------+
```

## Key Concepts

### Length Prefixing
Variable-length data (strings, arrays) include length information:
- **String**: 32-bit length + UTF-8 bytes
- **Array**: 32-bit element count + elements
- **Nested Structs**: Serialized sequentially

### Type Safety
- **Strong Typing**: Each field has explicit type and size
- **Bounds Checking**: Array bounds and buffer limits enforced
- **Validation**: Data integrity checks during deserialization

### Performance Considerations
- **Zero-Copy**: Where possible, avoid unnecessary copies
- **Streaming**: Process data as it's received
- **Memory Efficiency**: Minimal allocations for fixed-size data

## Error Handling

The example demonstrates comprehensive error handling:
- **Deserialization Errors**: Invalid data format detection
- **Buffer Overflows**: Bounds checking on all operations
- **Type Mismatches**: Validation of expected vs actual data types
- **Length Validation**: Ensuring variable-length data integrity

## Advanced Patterns

### Nested Structure Handling
```cpp
// Complex nested structures require careful ordering
struct {
    uint32_t header;
    std::vector<SubStruct> items;
    uint32_t footer;
};
```

### Dynamic Array Processing
```cpp
// Arrays require length prefix for deserialization
uint32_t array_length = deserialize_uint32();
for (uint32_t i = 0; i < array_length; ++i) {
    // Process each array element
}
```

## Comparison with Basic Examples

| Feature | Basic Examples | Complex Types |
|---------|---------------|---------------|
| Data Types | Simple primitives | Complex structures |
| Arrays | Fixed-size only | Variable-length arrays |
| Strings | Basic handling | Full UTF-8 support |
| Nesting | Flat structures | Nested hierarchies |
| Validation | Basic checks | Comprehensive validation |

## Next Steps

After understanding complex types, explore:
- [Large Messages Example](../large_messages/) - TP for messages > MTU
- [Multi-Service Example](../multi_service/) - Multiple services in one application
