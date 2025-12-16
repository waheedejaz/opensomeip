# Events Example

This example demonstrates the publish-subscribe pattern in SOME/IP, showing how publishers can send event notifications to subscribers.

## Overview

The Events example simulates a vehicle sensor system:
- **Publisher**: Generates temperature and speed sensor data
- **Subscriber**: Receives and displays sensor event notifications

Events are sent periodically to simulate real sensor data streams.

## Files

- `publisher.cpp` - Sensor data publisher that generates temperature and speed events
- `subscriber.cpp` - Sensor data subscriber that receives and displays events
- `README.md` - This documentation

## Running the Example

### Terminal 1 - Start the Publisher
```bash
cd examples/basic/events
make publisher
./publisher
```

You should see:
```
=== SOME/IP Events Publisher ===
Sensor Publisher initialized for service 0x3000
Publishing events:
  - Temperature (ID: 0x8001) every 2 seconds
  - Speed (ID: 0x8002) every 1.5 seconds

Sensor Publisher running. Press Ctrl+C to exit.
Publishing sensor data...
📊 Published Temperature: 22.5°C
🚗 Published Speed: 65.3 km/h
📊 Published Temperature: 19.8°C
🚗 Published Speed: 78.1 km/h
...
```

### Terminal 2 - Start the Subscriber
```bash
cd examples/basic/events
make subscriber
./subscriber
```

You should see:
```
=== SOME/IP Events Subscriber ===
Sensor Subscriber initialized for service 0x3000
Subscribed to events:
  - Temperature (ID: 0x8001)
  - Speed (ID: 0x8002)

Sensor Subscriber running. Press Ctrl+C to exit.
Waiting for sensor events...
🌡️  Temperature Event: 22.5°C (at 1234567890ms)
🚗 Speed Event: 65.3 km/h (at 1234567891ms)
🌡️  Temperature Event: 19.8°C (at 1234567892ms)
🚗 Speed Event: 78.1 km/h (at 1234567893ms)
...
```

## What This Example Demonstrates

1. **Event Publishing**: How to offer and publish events using `EventPublisher`
2. **Event Subscription**: How to subscribe to events using `EventSubscriber`
3. **Event Handlers**: Setting up callback functions for different event types
4. **Periodic Events**: Publishing events at regular intervals
5. **Event Data Serialization**: Converting sensor data to/from byte arrays
6. **Event Groups**: Organizing related events into groups
7. **Timestamp Handling**: Working with event timestamps

## Code Structure

### Publisher (`publisher.cpp`)
- Creates `EventPublisher` for service ID `0x3000`
- Offers two events: Temperature (ID `0x8001`) and Speed (ID `0x8002`)
- Generates realistic sensor data using random number generation
- Publishes events at different intervals (2s for temp, 1.5s for speed)
- Serializes float data to big-endian byte arrays

### Subscriber (`subscriber.cpp`)
- Creates `EventSubscriber` for service ID `0x3000`
- Subscribes to both temperature and speed events
- Sets up event handlers using lambda functions
- Deserializes received event data from big-endian byte arrays
- Displays events with timestamps

## Event Configuration

### Temperature Event
- **Event ID**: `0x8001`
- **Event Group**: `0x0001`
- **Reliability**: Unreliable
- **Type**: Periodic (every 2 seconds)
- **Data**: Single float (temperature in °C)

### Speed Event
- **Event ID**: `0x8002`
- **Event Group**: `0x0001`
- **Reliability**: Unreliable
- **Type**: Periodic (every 1.5 seconds)
- **Data**: Single float (speed in km/h)

## Protocol Details

- **Service ID**: `0x3000` (Sensor Service)
- **Event Group ID**: `0x0001` (Sensor Events)
- **Transport**: UDP multicast for event distribution
- **Serialization**: Manual big-endian float encoding/decoding
- **Timing**: Event-driven with periodic publishing

## Key Concepts Demonstrated

### Publish-Subscribe Pattern
- **Publisher**: Offers events and publishes data
- **Subscriber**: Subscribes to events and receives notifications
- **Decoupling**: Publisher and subscriber operate independently

### Event Types
- **Periodic Events**: Regular data updates (sensors)
- **Aperiodic Events**: Event-driven notifications (could be added)

### Data Flow
```
Publisher → SOME/IP Event → Transport → Subscriber
    ↓              ↓              ↓          ↓
Generate → Serialize → Send → Receive → Deserialize → Display
```

## Error Handling

The example demonstrates:
- Failed event offering/subscription handling
- Invalid event data size checking
- Transport initialization error handling

## Next Steps

After understanding this events example, try:
- [Complex Types Example](../../advanced/complex_types/) - Learn about structured event data
- [Large Messages Example](../../advanced/large_messages/) - Learn about TP for big events
