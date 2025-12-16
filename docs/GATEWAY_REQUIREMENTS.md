<!--
  Copyright (c) 2025 Vinicius Tadeu Zein

  See the NOTICE file(s) distributed with this work for additional
  information regarding copyright ownership.

  This program and the accompanying materials are made available under the
  terms of the Apache License Version 2.0 which is available at
  https://www.apache.org/licenses/LICENSE-2.0

  SPDX-License-Identifier: Apache-2.0
-->

# 🚪 SOME/IP Gateway Implementation Requirements

## Overview

For **gateway use cases**, the SOME/IP implementation needs **Extended Compliance** (85-90%) rather than Basic Compliance. Gateways act as protocol bridges between different networks and require advanced SOME/IP features.

## Gateway Use Case Analysis

### Gateway Types & Requirements

```
🌉 Gateway Categories
├── Diagnostic Gateway (OBD-II, UDS bridging)
├── Domain Gateway (Powertrain, Chassis, Body)
├── Central Gateway (Vehicle-wide communication)
└── External Gateway (Vehicle-to-cloud, V2X)
```

### Critical Gateway Features

#### 1. **Multiple Transport Bindings** 🔴 HIGH PRIORITY
```
Required Transport Bindings for Gateways:
├── UDP (✅ Implemented)
├── TCP (❌ Missing - CRITICAL)
├── CAN (❌ Not Applicable - Use Network PDU/I-PDUs + UDS)
└── DoIP (❌ Missing - HIGH)
```

**Why TCP?**
- Diagnostic communication requires reliable transport
- Service-oriented architecture needs connection-oriented communication
- Some ECUs prefer TCP over UDP

**Why CAN?** (Handled by Gateway Protocols)
- Legacy vehicle networks still use CAN
- Gateway bridges using Network PDU/I-PDUs and UDS protocols
- SOME/IP is Ethernet/IP only - CAN integration uses automotive bridging standards

#### 2. **Advanced Service Discovery** 🔴 HIGH PRIORITY
```
SD Features Required for Gateways:
├── Load Balancing Options (❌ Missing)
├── IPv6 Full Support (⚠️ Partial)
├── Configuration Strings (❌ Missing)
├── Event Group Balancing (❌ Missing)
└── Priority-based Routing (❌ Missing)
```

#### 3. **E2E Protection** 🔴 CRITICAL PRIORITY
```
Safety-Critical Data Protection:
├── CRC Calculation (❌ Missing)
├── Counter Mechanisms (❌ Missing)
├── Data ID Handling (❌ Missing)
├── Freshness Values (❌ Missing)
└── Profile C/D/E Support (❌ Missing)
```

**Why E2E for Gateways?**
- Gateways route safety-critical data between domains
- Data integrity must be maintained across network boundaries
- AUTOSAR requires E2E protection for ASIL-B/C systems

## Implementation Roadmap for Gateway Support

### Phase 1: Core Gateway Features (Next Priority)

#### **TCP Transport Binding** 🚀 IMMEDIATE
```cpp
class TcpTransport : public ITransport {
    // Connection management
    // Flow control
    // Reliable data delivery
    // Error recovery
};
```

#### **E2E Protection Layer** 🚀 IMMEDIATE
```cpp
class E2EProtection {
    // CRC calculation variants
    // Counter management
    // Freshness value handling
    // Profile validation
};
```

### Phase 2: Advanced Gateway Features

#### **CAN Integration** ✅ OUT OF SCOPE
```
Note: CAN integration handled by automotive protocols:
- Network PDU/I-PDUs for data transport
- UDS (Unified Diagnostic Services) for communication
- Gateway bridging (separate implementation)
```

#### **Advanced SD Options** 📅 FUTURE
```cpp
class SdAdvancedOptions {
    // Load balancing configuration
    // Priority routing
    // Event group management
};
```

## Gateway-Specific Testing Requirements

### Network Bridging Tests
```python
def test_gateway_service_routing():
    """Test service discovery across transport boundaries"""
    # UDP client discovers TCP service via gateway
    # CAN client accesses Ethernet service via gateway

def test_protocol_translation():
    """Test SOME/IP to CAN protocol conversion"""
    # SOME/IP RPC call translated to CAN message
    # CAN response translated back to SOME/IP
```

### E2E Protection Tests
```python
def test_e2e_data_integrity():
    """Test end-to-end data protection across gateway"""
    # Data sent with E2E protection
    # Passes through gateway
    # Verified at receiver
```

### Load Balancing Tests
```python
def test_sd_load_balancing():
    """Test service load distribution"""
    # Multiple service instances
    # Gateway routes based on load
    # Client gets optimal instance
```

## Performance Requirements for Gateways

### Throughput Targets
- **Basic Gateway**: 10,000 msg/s
- **Central Gateway**: 50,000 msg/s
- **High-Performance Gateway**: 100,000+ msg/s

### Latency Requirements
- **Real-time data**: <100μs
- **Control data**: <1ms
- **Diagnostic data**: <10ms

### Memory Constraints
- **Embedded Gateway**: <32MB RAM
- **Central Gateway**: <128MB RAM

## Certification Requirements

### AUTOSAR Compliance
- **SOME/IP Extended Compliance**: 85-90% coverage required
- **ASIL-B/C Classification**: E2E protection mandatory
- **Network Management**: Advanced SD features required

### Automotive Standards
- **ISO 14229 (UDS)**: Diagnostic communication over SOME/IP
- **AUTOSAR Adaptive**: Service-oriented architecture
- **Vehicle Network Standards**: Bridging requirements

## Implementation Impact Assessment

### Code Size Increase
- **Current**: ~50K lines (estimated)
- **With Gateway Features**: ~150K lines (3x increase)
- **Full Compliance**: ~300K lines (6x increase)

### Complexity Assessment
- **Current Complexity**: Medium
- **With Gateway Features**: High
- **Maintenance Effort**: 2-3x increase

### Testing Effort
- **Current Tests**: ~50 test cases
- **Gateway Tests**: ~200+ test cases required
- **Integration Tests**: Complex multi-transport scenarios

## Recommendation

For **gateway use cases**, implement:

1. **TCP Transport Binding** (Immediate - 2-4 weeks)
2. **E2E Protection Layer** (Immediate - 3-6 weeks)
3. **CAN Integration** (Out of Scope - Use Network PDU/I-PDUs + UDS)
4. **Advanced SD Features** (Phase 2 - 4-8 weeks)

This will achieve **~90% coverage** suitable for most gateway applications while maintaining reasonable development and maintenance costs.

## Success Criteria

### Functional Requirements ✅
- [ ] TCP-based service communication
- [ ] CAN integration via Network PDU/I-PDUs and UDS (separate implementation)
- [ ] E2E-protected data routing
- [ ] Advanced service discovery

### Performance Requirements ✅
- [ ] 10,000+ msg/s throughput
- [ ] <1ms latency for control data
- [ ] <32MB memory usage

### Compliance Requirements ✅
- [ ] AUTOSAR Extended Compliance
- [ ] ASIL-B/C safety features
- [ ] ISO 14229 diagnostic support
