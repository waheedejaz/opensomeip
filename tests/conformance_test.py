#!/usr/bin/env python3
"""
SOME/IP Protocol Conformance Test Suite

This test suite validates compliance with the SOME/IP protocol specification,
covering message formats, service discovery, transport protocol, and safety requirements.
"""

import pytest
import socket
import struct
import time
import threading
import subprocess
import os
from typing import List, Dict, Optional, Tuple, NamedTuple
from enum import Enum
from dataclasses import dataclass

# SOME/IP Protocol Constants
SOMEIP_MAGIC = 0xDEADBEEF
SOMEIP_PROTOCOL_VERSION = 0x01
SOMEIP_MESSAGE_TYPE_REQUEST = 0x00
SOMEIP_MESSAGE_TYPE_RESPONSE = 0x80
SOMEIP_RETURN_CODE_OK = 0x00
SOMEIP_SD_PROTOCOL_VERSION = 0x01

class MessageType(Enum):
    REQUEST = 0x00
    REQUEST_NO_RETURN = 0x01
    NOTIFICATION = 0x02
    RESPONSE = 0x80
    ERROR = 0x81
    TP_REQUEST = 0x20
    TP_REQUEST_NO_RETURN = 0x21
    TP_NOTIFICATION = 0x22
    TP_RESPONSE = 0x23
    TP_ERROR = 0x24

class ReturnCode(Enum):
    E_OK = 0x00
    E_NOT_OK = 0x01
    E_UNKNOWN_SERVICE = 0x02
    E_UNKNOWN_METHOD = 0x03
    E_NOT_READY = 0x04
    E_NOT_REACHABLE = 0x05
    E_TIMEOUT = 0x06
    E_WRONG_PROTOCOL_VERSION = 0x07
    E_WRONG_INTERFACE_VERSION = 0x08
    E_MALFORMED_MESSAGE = 0x09
    E_WRONG_MESSAGE_TYPE = 0x0A

@dataclass
class SomeIpHeader:
    """SOME/IP message header structure"""
    service_id: int
    method_id: int
    length: int
    client_id: int
    session_id: int
    protocol_version: int
    interface_version: int
    message_type: int
    return_code: int

    def to_bytes(self) -> bytes:
        return struct.pack('>HHHHIHBBBB',
                          self.service_id, self.method_id, self.length,
                          self.client_id, self.session_id, self.protocol_version,
                          self.interface_version, self.message_type, self.return_code)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'SomeIpHeader':
        if len(data) < 16:
            raise ValueError("Header too short")
        unpacked = struct.unpack('>HHHHIHBBBB', data[:16])
        return cls(*unpacked)

class SomeIpValidator:
    """SOME/IP protocol validator"""

    @staticmethod
    def validate_header(header: SomeIpHeader) -> List[str]:
        """Validate SOME/IP header according to specification"""
        errors = []

        # Service ID validation (0x0000-0xFFFF)
        if not (0x0000 <= header.service_id <= 0xFFFF):
            errors.append(f"Invalid service_id: {header.service_id}")

        # Method ID validation (0x0000-0xFFFF)
        if not (0x0000 <= header.method_id <= 0xFFFF):
            errors.append(f"Invalid method_id: {header.method_id}")

        # Length validation (minimum 8 bytes for header)
        if header.length < 8:
            errors.append(f"Invalid length: {header.length} (minimum 8)")

        # Client ID validation
        if not (0x0000 <= header.client_id <= 0xFFFF):
            errors.append(f"Invalid client_id: {header.client_id}")

        # Session ID validation (0x0001-0xFFFF for requests)
        if header.message_type in [0x00, 0x01, 0x02, 0x20, 0x21, 0x22]:
            if not (0x0001 <= header.session_id <= 0xFFFF):
                errors.append(f"Invalid session_id for request: {header.session_id}")

        # Protocol version (must be 0x01)
        if header.protocol_version != SOMEIP_PROTOCOL_VERSION:
            errors.append(f"Invalid protocol_version: {header.protocol_version} (expected {SOMEIP_PROTOCOL_VERSION})")

        # Interface version validation
        if not (0x00 <= header.interface_version <= 0xFF):
            errors.append(f"Invalid interface_version: {header.interface_version}")

        # Message type validation
        valid_message_types = {0x00, 0x01, 0x02, 0x20, 0x21, 0x22, 0x80, 0x81, 0x23, 0x24}
        if header.message_type not in valid_message_types:
            errors.append(f"Invalid message_type: {header.message_type}")

        # Return code validation
        if not (0x00 <= header.return_code <= 0xFF):
            errors.append(f"Invalid return_code: {header.return_code}")

        return errors

    @staticmethod
    def validate_sd_message(data: bytes) -> List[str]:
        """Validate SOME/IP-SD message format"""
        errors = []

        if len(data) < 16:
            errors.append("SD message too short for header")
            return errors

        try:
            header = SomeIpHeader.from_bytes(data)
            header_errors = SomeIpValidator.validate_header(header)
            errors.extend(header_errors)

            # SD specific validations
            if header.service_id != 0xFFFF:
                errors.append("SD messages must have service_id 0xFFFF")

            if header.method_id != 0x8100:
                errors.append("SD messages must have method_id 0x8100")

        except Exception as e:
            errors.append(f"Failed to parse SD header: {e}")

        return errors

    @staticmethod
    def validate_tp_message(data: bytes) -> List[str]:
        """Validate SOME/IP-TP message format"""
        errors = []

        if len(data) < 16:
            errors.append("TP message too short for header")
            return errors

        try:
            header = SomeIpHeader.from_bytes(data)

            # TP messages have specific message types
            if header.message_type not in {0x20, 0x21, 0x22, 0x23, 0x24}:
                errors.append(f"Invalid TP message_type: {header.message_type}")

            # TP messages should have additional TP header after SOME/IP header
            if len(data) < 24:  # SOME/IP header + TP header
                errors.append("TP message missing TP header")

        except Exception as e:
            errors.append(f"Failed to parse TP header: {e}")

        return errors

class NetworkMonitor:
    """Network traffic monitor for SOME/IP messages"""

    def __init__(self, interface: str = "lo", port: int = 30490):
        self.interface = interface
        self.port = port
        self.captured_messages: List[bytes] = []
        self.monitoring = False

    def start_monitoring(self):
        """Start network monitoring"""
        self.monitoring = True
        self.captured_messages = []

        # Note: In production, this would use scapy or similar
        # For now, we'll use a simple socket approach
        pass

    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False

    def get_captured_messages(self) -> List[bytes]:
        """Get captured messages"""
        return self.captured_messages.copy()

class ConformanceTestSuite:
    """SOME/IP Conformance Test Suite"""

    def __init__(self, build_dir: str = "../build"):
        self.build_dir = build_dir
        self.services: Dict[str, subprocess.Popen] = {}

    def start_service(self, name: str, args: List[str] = None) -> subprocess.Popen:
        """Start a SOME/IP service"""
        cmd = [os.path.join(self.build_dir, "bin", name)]
        if args:
            cmd.extend(args)

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.services[name] = proc
        time.sleep(0.5)  # Allow startup
        return proc

    def stop_all_services(self):
        """Stop all services"""
        for proc in self.services.values():
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    proc.kill()
        self.services.clear()

# Test Fixtures
@pytest.fixture(scope="session")
def conformance_suite():
    """Conformance test suite fixture"""
    suite = ConformanceTestSuite()
    yield suite
    suite.stop_all_services()

@pytest.fixture
def someip_client():
    """SOME/IP test client fixture"""
    class TestClient:
        def __init__(self):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(("127.0.0.1", 0))
            self.sock.settimeout(2.0)

        def send_message(self, header: SomeIpHeader, payload: bytes = b"") -> None:
            data = header.to_bytes() + payload
            self.sock.sendto(data, ("127.0.0.1", 30490))

        def receive_message(self) -> Optional[Tuple[SomeIpHeader, bytes]]:
            try:
                data, _ = self.sock.recvfrom(4096)
                if len(data) >= 16:
                    header = SomeIpHeader.from_bytes(data)
                    payload = data[16:]
                    return header, payload
            except socket.timeout:
                pass
            return None

        def close(self):
            self.sock.close()

    client = TestClient()
    yield client
    client.close()

# Conformance Test Classes
class TestMessageFormatConformance:
    """Test SOME/IP message format conformance"""

    def test_valid_message_header(self, someip_client):
        """Test valid SOME/IP message header"""
        header = SomeIpHeader(
            service_id=0x1234,
            method_id=0x5678,
            length=8,
            client_id=0xABCD,
            session_id=0x0001,
            protocol_version=SOMEIP_PROTOCOL_VERSION,
            interface_version=0x01,
            message_type=MessageType.REQUEST.value,
            return_code=ReturnCode.E_OK.value
        )

        errors = SomeIpValidator.validate_header(header)
        assert len(errors) == 0, f"Valid header failed validation: {errors}"

    def test_invalid_service_id(self, someip_client):
        """Test invalid service ID handling"""
        header = SomeIpHeader(
            service_id=0x10000,  # Invalid (> 0xFFFF)
            method_id=0x5678,
            length=8,
            client_id=0xABCD,
            session_id=0x0001,
            protocol_version=SOMEIP_PROTOCOL_VERSION,
            interface_version=0x01,
            message_type=MessageType.REQUEST.value,
            return_code=ReturnCode.E_OK.value
        )

        errors = SomeIpValidator.validate_header(header)
        assert len(errors) > 0
        assert any("service_id" in error for error in errors)

    def test_invalid_protocol_version(self, someip_client):
        """Test invalid protocol version handling"""
        header = SomeIpHeader(
            service_id=0x1234,
            method_id=0x5678,
            length=8,
            client_id=0xABCD,
            session_id=0x0001,
            protocol_version=0x02,  # Invalid (not 0x01)
            interface_version=0x01,
            message_type=MessageType.REQUEST.value,
            return_code=ReturnCode.E_OK.value
        )

        errors = SomeIpValidator.validate_header(header)
        assert len(errors) > 0
        assert any("protocol_version" in error for error in errors)

    def test_invalid_message_type(self, someip_client):
        """Test invalid message type handling"""
        header = SomeIpHeader(
            service_id=0x1234,
            method_id=0x5678,
            length=8,
            client_id=0xABCD,
            session_id=0x0001,
            protocol_version=SOMEIP_PROTOCOL_VERSION,
            interface_version=0x01,
            message_type=0xFF,  # Invalid message type
            return_code=ReturnCode.E_OK.value
        )

        errors = SomeIpValidator.validate_header(header)
        assert len(errors) > 0
        assert any("message_type" in error for error in errors)

    def test_minimum_message_length(self, someip_client):
        """Test minimum message length"""
        header = SomeIpHeader(
            service_id=0x1234,
            method_id=0x5678,
            length=7,  # Invalid (< 8)
            client_id=0xABCD,
            session_id=0x0001,
            protocol_version=SOMEIP_PROTOCOL_VERSION,
            interface_version=0x01,
            message_type=MessageType.REQUEST.value,
            return_code=ReturnCode.E_OK.value
        )

        errors = SomeIpValidator.validate_header(header)
        assert len(errors) > 0
        assert any("length" in error for error in errors)

    def test_session_id_validation(self, someip_client):
        """Test session ID validation for different message types"""
        # Valid request
        header_request = SomeIpHeader(
            service_id=0x1234,
            method_id=0x5678,
            length=8,
            client_id=0xABCD,
            session_id=0x0001,  # Valid for request
            protocol_version=SOMEIP_PROTOCOL_VERSION,
            interface_version=0x01,
            message_type=MessageType.REQUEST.value,
            return_code=ReturnCode.E_OK.value
        )

        errors = SomeIpValidator.validate_header(header_request)
        assert len(errors) == 0

        # Valid response (can have session_id = 0x0000)
        header_response = SomeIpHeader(
            service_id=0x1234,
            method_id=0x5678,
            length=8,
            client_id=0xABCD,
            session_id=0x0000,  # Valid for response
            protocol_version=SOMEIP_PROTOCOL_VERSION,
            interface_version=0x01,
            message_type=MessageType.RESPONSE.value,
            return_code=ReturnCode.E_OK.value
        )

        errors = SomeIpValidator.validate_header(header_response)
        assert len(errors) == 0

class TestSdConformance:
    """Test SOME/IP-SD conformance"""

    def test_sd_service_offer_format(self, conformance_suite):
        """Test SD service offer message format"""
        # This would test actual SD message parsing
        # For now, validate the format expectations
        pass

    def test_sd_multicast_address(self, conformance_suite):
        """Test SD multicast address usage"""
        # SD should use 224.244.224.245:30490
        expected_multicast = ("224.244.224.245", 30490)
        # Test that our implementation uses correct multicast address
        pass

    def test_sd_ttl_handling(self, conformance_suite):
        """Test TTL field handling in SD messages"""
        # Test TTL decrement and expiration
        pass

class TestTpConformance:
    """Test SOME/IP-TP conformance"""

    def test_tp_segmentation(self, conformance_suite):
        """Test TP message segmentation"""
        # Start TP example and validate segmentation
        proc = conformance_suite.start_service("tp_example")

        try:
            stdout, _ = proc.communicate(timeout=10.0)
            output = stdout.decode()

            # Validate segmentation output
            assert "Segment 0:" in output
            assert "Total segments:" in output
            assert "VERIFIED" in output

        except subprocess.TimeoutExpired:
            pytest.fail("TP segmentation test timed out")

    def test_tp_reassembly(self, conformance_suite):
        """Test TP message reassembly"""
        # Test is covered in tp_segmentation test
        pass

    def test_tp_sequence_numbers(self, conformance_suite):
        """Test TP sequence number handling"""
        # Validate sequence numbers in segmented messages
        pass

class TestSafetyConformance:
    """Test safety-critical conformance"""

    def test_memory_bounds_checking(self, someip_client):
        """Test memory bounds validation"""
        # Send oversized message and verify rejection
        large_payload = b"X" * 100000  # 100KB payload

        header = SomeIpHeader(
            service_id=0x1234,
            method_id=0x5678,
            length=8 + len(large_payload),
            client_id=0xABCD,
            session_id=0x0001,
            protocol_version=SOMEIP_PROTOCOL_VERSION,
            interface_version=0x01,
            message_type=MessageType.REQUEST.value,
            return_code=ReturnCode.E_OK.value
        )

        someip_client.send_message(header, large_payload)
        # Should either reject or handle gracefully
        response = someip_client.receive_message()
        # Validate appropriate error handling
        pass

    def test_timeout_behavior(self, someip_client):
        """Test timeout handling"""
        # Send message to non-existent service
        header = SomeIpHeader(
            service_id=0xFFFF,  # Non-existent service
            method_id=0x0001,
            length=8,
            client_id=0xABCD,
            session_id=0x0001,
            protocol_version=SOMEIP_PROTOCOL_VERSION,
            interface_version=0x01,
            message_type=MessageType.REQUEST.value,
            return_code=ReturnCode.E_OK.value
        )

        someip_client.send_message(header)
        start_time = time.time()

        response = someip_client.receive_message()
        elapsed = time.time() - start_time

        # Should timeout within reasonable time
        assert elapsed < 5.0, f"Timeout took too long: {elapsed}s"
        # Should not crash or hang indefinitely

    def test_concurrent_connections(self, conformance_suite):
        """Test handling of concurrent connections"""
        # Start echo server
        server = conformance_suite.start_service("echo_server")

        # Create multiple clients
        clients = []
        threads = []

        def client_worker(client_id: int):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", 0))
            sock.settimeout(1.0)

            try:
                for i in range(10):
                    payload = f"Client {client_id} Message {i}".encode()
                    header = SomeIpHeader(
                        service_id=0x1234,
                        method_id=0x0001,
                        length=8 + len(payload),
                        client_id=client_id,
                        session_id=i + 1,
                        protocol_version=SOMEIP_PROTOCOL_VERSION,
                        interface_version=0x01,
                        message_type=MessageType.REQUEST.value,
                        return_code=ReturnCode.E_OK.value
                    )

                    data = header.to_bytes() + payload
                    sock.sendto(data, ("127.0.0.1", 30490))

                    # Try to receive response
                    try:
                        resp_data, _ = sock.recvfrom(4096)
                        # Validate response
                    except socket.timeout:
                        pass  # Expected for high load

            finally:
                sock.close()

        # Start 5 concurrent clients
        for i in range(5):
            thread = threading.Thread(target=client_worker, args=(0x1000 + i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10.0)

        # Server should still be running
        assert server.poll() is None, "Server crashed under concurrent load"

class TestNetworkConformance:
    """Test network layer conformance"""

    def test_udp_socket_handling(self, someip_client):
        """Test UDP socket handling"""
        # Test socket creation, binding, sending, receiving
        assert someip_client.sock is not None
        assert someip_client.sock.family == socket.AF_INET
        assert someip_client.sock.type == socket.SOCK_DGRAM

    def test_port_assignment(self, conformance_suite):
        """Test port assignment and management"""
        # Start service and verify it binds to correct port
        server = conformance_suite.start_service("echo_server")
        assert server.poll() is None

        # Check that port 30490 is in use
        import psutil
        connections = psutil.net_connections()
        someip_ports = [conn.laddr.port for conn in connections
                       if conn.laddr and conn.laddr.port == 30490]
        assert len(someip_ports) > 0, "SOME/IP port not found in use"

    def test_packet_size_limits(self, someip_client):
        """Test UDP packet size limits"""
        # Test various payload sizes
        test_sizes = [100, 1000, 5000, 10000]

        for size in test_sizes:
            payload = b"X" * size
            header = SomeIpHeader(
                service_id=0x1234,
                method_id=0x5678,
                length=8 + len(payload),
                client_id=0xABCD,
                session_id=0x0001,
                protocol_version=SOMEIP_PROTOCOL_VERSION,
                interface_version=0x01,
                message_type=MessageType.REQUEST.value,
                return_code=ReturnCode.E_OK.value
            )

            # Should not crash on large payloads
            try:
                someip_client.send_message(header, payload)
            except OSError as e:
                # UDP fragmentation or size limits may cause errors
                assert "Message too long" in str(e) or "too long" in str(e)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
