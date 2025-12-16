#!/usr/bin/env python3
"""
SOME/IP Stack Integration Tests using pytest

This provides comprehensive integration testing with better reporting,
parallel execution, and advanced testing features.
"""

import pytest
import socket
import struct
import time
import threading
import subprocess
import signal
import os
import tempfile
import shutil
from typing import List, Dict, Optional, Tuple, Generator
import asyncio
from contextlib import contextmanager

class SomeIpMessage:
    """SOME/IP message for testing"""

    def __init__(self, service_id: int, method_id: int, client_id: int = 0x1234,
                 session_id: int = 0x0001, protocol_version: int = 0x01,
                 interface_version: int = 0x01, message_type: int = 0x00,
                 return_code: int = 0x00, payload: bytes = b""):
        self.service_id = service_id
        self.method_id = method_id
        self.length = 8 + len(payload)
        self.client_id = client_id
        self.session_id = session_id
        self.protocol_version = protocol_version
        self.interface_version = interface_version
        self.message_type = message_type
        self.return_code = return_code
        self.payload = payload

    def to_bytes(self) -> bytes:
        header = struct.pack('>HHHHIHBBBB',
                           self.service_id, self.method_id, self.length,
                           self.client_id, self.session_id, self.protocol_version,
                           self.interface_version, self.message_type, self.return_code)
        return header + self.payload

    @classmethod
    def from_bytes(cls, data: bytes) -> 'SomeIpMessage':
        if len(data) < 16:
            raise ValueError("Message too short")
        unpacked = struct.unpack('>HHHHIHBBBB', data[:16])
        payload = data[16:]
        return cls(*unpacked[:2], *unpacked[3:], payload)

class SomeIpClient:
    """SOME/IP test client"""

    def __init__(self, remote_addr: Tuple[str, int] = ("127.0.0.1", 3000)):
        self.remote_addr = remote_addr
        self.local_addr = ("127.0.0.1", 0)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.local_addr)
        self.sock.settimeout(2.0)

    def send_message(self, message: SomeIpMessage) -> None:
        data = message.to_bytes()
        self.sock.sendto(data, self.remote_addr)

    def receive_message(self) -> Optional[SomeIpMessage]:
        try:
            data, _ = self.sock.recvfrom(4096)
            return SomeIpMessage.from_bytes(data)
        except socket.timeout:
            return None

    def close(self):
        self.sock.close()

@pytest.fixture(scope="session")
def build_dir():
    """Get the build directory path"""
    return os.path.abspath("../build")

@pytest.fixture(scope="session")
def someip_services(build_dir):
    """Fixture to manage SOME/IP services during testing"""
    services = []

    def start_service(executable: str, args: List[str] = None) -> subprocess.Popen:
        cmd = [os.path.join(build_dir, "bin", executable)]
        if args:
            cmd.extend(args)

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=build_dir
        )
        services.append(proc)
        time.sleep(0.5)  # Allow service to start
        return proc

    yield start_service

    # Cleanup
    for proc in services:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

class TestBasicCommunication:
    """Basic communication tests"""

    def test_echo_request_response(self, someip_services):
        """Test basic echo functionality"""
        # Start echo server
        server = someip_services("echo_server")

        client = SomeIpClient()
        test_payload = b"Hello SOME/IP!"

        # Send request
        request = SomeIpMessage(
            service_id=0x1234,
            method_id=0x0001,
            message_type=0x00,  # REQUEST
            payload=test_payload
        )

        client.send_message(request)

        # Receive response
        response = client.receive_message()
        assert response is not None, "No response received"

        assert response.service_id == request.service_id
        assert response.method_id == request.method_id
        assert response.message_type == 0x80  # RESPONSE
        assert response.payload == test_payload

        client.close()

    def test_multiple_messages(self, someip_services):
        """Test sending multiple messages"""
        server = someip_services("echo_server")
        client = SomeIpClient()

        for i in range(5):
            payload = f"Message {i}".encode()
            request = SomeIpMessage(0x1234, 0x0001, payload=payload)
            client.send_message(request)

            response = client.receive_message()
            assert response is not None
            assert response.payload == payload

        client.close()

class TestRpcFunctionality:
    """RPC functionality tests"""

    def test_calculator_add(self, someip_services):
        """Test calculator ADD operation"""
        server = someip_services("rpc_calculator_server")
        client = SomeIpClient()

        # ADD: 42 + 58 = 100
        payload = struct.pack(">ii", 42, 58)
        request = SomeIpMessage(
            service_id=0x1234,
            method_id=0x0001,  # ADD method
            payload=payload
        )

        client.send_message(request)
        response = client.receive_message()

        assert response is not None
        result = struct.unpack(">i", response.payload)[0]
        assert result == 100

        client.close()

    def test_calculator_subtract(self, someip_services):
        """Test calculator SUBTRACT operation"""
        server = someip_services("rpc_calculator_server")
        client = SomeIpClient()

        # SUBTRACT: 100 - 25 = 75
        payload = struct.pack(">ii", 100, 25)
        request = SomeIpMessage(
            service_id=0x1234,
            method_id=0x0002,  # SUBTRACT method
            payload=payload
        )

        client.send_message(request)
        response = client.receive_message()

        assert response is not None
        result = struct.unpack(">i", response.payload)[0]
        assert result == 75

        client.close()

    def test_calculator_multiply(self, someip_services):
        """Test calculator MULTIPLY operation"""
        server = someip_services("rpc_calculator_server")
        client = SomeIpClient()

        # MULTIPLY: 7 * 8 = 56
        payload = struct.pack(">ii", 7, 8)
        request = SomeIpMessage(
            service_id=0x1234,
            method_id=0x0003,  # MULTIPLY method
            payload=payload
        )

        client.send_message(request)
        response = client.receive_message()

        assert response is not None
        result = struct.unpack(">i", response.payload)[0]
        assert result == 56

        client.close()

    def test_calculator_divide(self, someip_services):
        """Test calculator DIVIDE operation"""
        server = someip_services("rpc_calculator_server")
        client = SomeIpClient()

        # DIVIDE: 144 / 12 = 12
        payload = struct.pack(">ii", 144, 12)
        request = SomeIpMessage(
            service_id=0x1234,
            method_id=0x0004,  # DIVIDE method
            payload=payload
        )

        client.send_message(request)
        response = client.receive_message()

        assert response is not None
        result = struct.unpack(">i", response.payload)[0]
        assert result == 12

        client.close()

class TestServiceDiscovery:
    """Service Discovery tests"""

    @pytest.mark.timeout(10)
    def test_sd_client_server_interaction(self, someip_services):
        """Test SD client and server interaction"""
        # Start SD server
        server = someip_services("sd_service_server")
        time.sleep(1.0)  # Allow server to initialize

        # Start SD client
        client = someip_services("sd_service_client")
        time.sleep(3.0)  # Allow discovery process

        # Check if client process completed successfully
        assert client.poll() == 0, "SD client failed"

        # Check output for discovery success
        stdout, stderr = client.communicate()
        output = stdout.decode() + stderr.decode()
        assert "Service discovered" in output or "Found service" in output, \
               f"Service discovery failed. Output: {output}"

class TestEventSystem:
    """Event system tests"""

    @pytest.mark.timeout(15)
    def test_event_publisher_subscriber(self, someip_services):
        """Test event publishing and subscription"""
        # Start event publisher
        publisher = someip_services("event_publisher")
        time.sleep(1.0)

        # Start event subscriber
        subscriber = someip_services("event_subscriber")
        time.sleep(5.0)  # Allow event exchange

        # Check if subscriber process completed
        assert subscriber.poll() == 0, "Event subscriber failed"

        # Check output for event reception
        stdout, stderr = subscriber.communicate()
        output = stdout.decode() + stderr.decode()
        assert "Event received" in output or "Notification received" in output, \
               f"Event reception failed. Output: {output}"

class TestTransportProtocol:
    """TP (Transport Protocol) tests"""

    @pytest.mark.timeout(15)
    def test_tp_segmentation_reassembly(self, someip_services):
        """Test TP large message handling"""
        # Run TP example
        tp_proc = someip_services("tp_example")

        # Wait for completion
        stdout, stderr = tp_proc.communicate()
        output = stdout.decode() + stderr.decode()

        assert tp_proc.poll() == 0, f"TP example failed. Output: {output}"
        assert "VERIFIED" in output, f"TP integrity check failed. Output: {output}"

class TestPerformance:
    """Performance tests"""

    def test_message_throughput(self, someip_services):
        """Test message throughput under load"""
        server = someip_services("echo_server")
        client = SomeIpClient()

        num_messages = 50
        start_time = time.time()

        for i in range(num_messages):
            payload = f"Perf test message {i}".encode()
            request = SomeIpMessage(0x1234, 0x0001, payload=payload)
            client.send_message(request)

            response = client.receive_message()
            assert response is not None
            assert response.payload == payload

        end_time = time.time()
        duration = end_time - start_time
        messages_per_second = num_messages / duration

        print(".2f")

        # Reasonable performance expectation
        assert messages_per_second > 20.0, f"Low throughput: {messages_per_second} msg/s"

        client.close()

class TestErrorHandling:
    """Error handling and edge case tests"""

    def test_invalid_message_handling(self, someip_services):
        """Test handling of invalid messages"""
        server = someip_services("echo_server")
        client = SomeIpClient()

        # Send invalid message (too short)
        client.sock.sendto(b"invalid", ("127.0.0.1", 3000))

        # Server should not crash, might send error response or ignore
        time.sleep(0.5)

        # Send valid message to ensure server still works
        request = SomeIpMessage(0x1234, 0x0001, payload=b"Test after invalid")
        client.send_message(request)

        response = client.receive_message()
        assert response is not None, "Server crashed after invalid message"

        client.close()

    def test_connection_timeout(self, someip_services):
        """Test timeout behavior when no server is running"""
        client = SomeIpClient()

        # Try to send message when no server is running
        request = SomeIpMessage(0x1234, 0x0001, payload=b"Test timeout")
        client.send_message(request)

        # Should timeout
        response = client.receive_message()
        assert response is None, "Unexpected response when no server running"

        client.close()

if __name__ == "__main__":
    # Can be run directly or with pytest
    pytest.main([__file__, "-v"])
