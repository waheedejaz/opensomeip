# Method Calls Example

This example demonstrates basic RPC (Remote Procedure Call) functionality in SOME/IP, showing how clients can invoke methods on servers with parameters and receive results.

## Overview

The Method Calls example implements a calculator service with three methods:
- **ADD**: Adds two integers and returns the sum
- **MULTIPLY**: Multiplies two integers and returns the product
- **GET_STATS**: Returns the total number of method calls processed by the server

## Files

- `server.cpp` - Calculator server implementing the RPC methods
- `client.cpp` - Calculator client that invokes the methods
- `README.md` - This documentation

## Building the Example

First, build the entire project from the main directory:

```bash
# From the project root directory
mkdir build && cd build
cmake ..
make
```

## Running the Example

### Terminal 1 - Start the Server
```bash
# From the project root directory (after building)
./build/bin/method_calls_server
```

You should see:
```
=== SOME/IP Method Calls Server ===
Calculator Server initialized for service 0x2000
Available methods:
  - 0x0001: add(int32, int32) -> int32
  - 0x0002: multiply(int32, int32) -> int32
  - 0x0003: get_stats() -> struct{calls: uint32}
Calculator Server running. Press Ctrl+C to exit.
```

### Terminal 2 - Run the Client
```bash
# From the project root directory (after building)
./build/bin/method_calls_client
```

You should see output like:
```
=== SOME/IP Method Calls Client ===

Waiting for server to be ready...

=== Running Calculator Operations ===

--- Testing ADD(10, 5) ---
Result: 10 + 5 = 15
✓ ADD operation successful

--- Testing ADD(-3, 7) ---
Result: -3 + 7 = 4
✓ ADD operation successful

... (more operations)

--- Testing GET_STATS() ---
Server statistics: 6 total method calls processed
✓ GET_STATS operation successful

=== All Operations Completed ===

Client finished.
```

And the server will show:
```
ADD: 10 + 5 = 15 (client: 0xabcd, session: 0x1)
MULTIPLY: 6 * 7 = 42 (client: 0xabcd, session: 0x2)
...
GET_STATS: 6 total calls processed (client: 0xabcd, session: 0x7)
```

## What This Example Demonstrates

1. **RPC Server Setup**: Creating and initializing an RPC server with method handlers
2. **Method Registration**: Registering methods with unique IDs and handler functions
3. **Parameter Serialization**: Converting method parameters to/from byte arrays
4. **Synchronous RPC Calls**: Client making blocking method calls and waiting for results
5. **Return Code Handling**: Proper handling of success/failure responses
6. **Session Management**: Automatic session ID management for request correlation
7. **Client ID Assignment**: Using unique client identifiers

## Code Structure

### Server (`server.cpp`)
- Creates `RpcServer` instance for service ID `0x2000`
- Registers three method handlers using lambda functions
- Each handler:
  - Deserializes input parameters from `std::vector<uint8_t>`
  - Performs the requested operation
  - Serializes the result back to `std::vector<uint8_t>`
  - Returns `RpcResult::SUCCESS` or appropriate error code

### Client (`client.cpp`)
- Creates `RpcClient` instance with client ID `0xABCD`
- Makes synchronous calls using `call_method_sync()`
- Serializes parameters and deserializes results
- Handles different RPC result codes

## Method Signatures

### ADD Method (ID: 0x0001)
```
int32_t add(int32_t a, int32_t b)
```

### MULTIPLY Method (ID: 0x0002)
```
int32_t multiply(int32_t a, int32_t b)
```

### GET_STATS Method (ID: 0x0003)
```
struct { uint32_t call_count; } get_stats()
```

## Protocol Details

- **Service ID**: `0x2000` (Calculator Service)
- **Client ID**: `0xABCD` (Calculator Client)
- **Transport**: UDP with automatic endpoint resolution
- **Serialization**: Manual big-endian integer encoding/decoding

## Error Handling

The example demonstrates:
- Parameter validation on the server
- RPC result code checking on the client
- Graceful handling of invalid responses

## Next Steps

After understanding this RPC example, try:
- [Events Example](../events/) - Learn about publish-subscribe patterns
- [Complex Types Example](../../advanced/complex_types/) - Learn about structured data serialization
