#!/usr/bin/env python3
"""
SOME/IP Stack Integration Test Framework

This framework provides comprehensive integration testing for the SOME/IP stack,
testing complete workflows and inter-component interactions.
"""

import socket
import struct
import time
import threading
import subprocess
import signal
import os
import sys
from typing import List, Dict, Optional, Tuple
import unittest
import tempfile
import shutil

class SomeIpMessage:
    """SOME/IP message representation for testing"""

    def __init__(self, service_id: int, method_id: int, client_id: int = 0x1234,
                 session_id: int = 0x0001, protocol_version: int = 0x01,
                 interface_version: int = 0x01, message_type: int = 0x00,
                 return_code: int = 0x00, payload: bytes = b""):
        self.service_id = service_id
        self.method_id = method_id
        self.length = 8 + len(payload)  # Header length + payload
        self.client_id = client_id
        self.session_id = session_id
        self.protocol_version = protocol_version
        self.interface_version = interface_version
        self.message_type = message_type
        self.return_code = return_code
        self.payload = payload

    def to_bytes(self) -> bytes:
        """Serialize message to bytes"""
        header = struct.pack('>HHHHIHBBBB',
                           self.service_id,
                           self.method_id,
                           self.length,
                           self.client_id,
                           self.session_id,
                           self.protocol_version,
                           self.interface_version,
                           self.message_type,
                           self.return_code)
        return header + self.payload

    @classmethod
    def from_bytes(cls, data: bytes) -> 'SomeIpMessage':
        """Deserialize message from bytes"""
        if len(data) < 16:
            raise ValueError("Message too short")

        service_id, method_id, length, client_id, session_id, \
        protocol_version, interface_version, message_type, return_code = \
            struct.unpack('>HHHHIHBBBB', data[:16])

        payload = data[16:] if len(data) > 16 else b""

        msg = cls(service_id, method_id, client_id, session_id,
                 protocol_version, interface_version, message_type, return_code, payload)
        msg.length = length
        return msg

class SomeIpClient:
    """SOME/IP client for testing"""

    def __init__(self, local_addr: Tuple[str, int], remote_addr: Tuple[str, int]):
        self.local_addr = local_addr
        self.remote_addr = remote_addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(local_addr)
        self.sock.settimeout(1.0)

    def send_message(self, message: SomeIpMessage) -> None:
        """Send a SOME/IP message"""
        data = message.to_bytes()
        self.sock.sendto(data, self.remote_addr)

    def receive_message(self) -> Optional[SomeIpMessage]:
        """Receive a SOME/IP message"""
        try:
            data, _ = self.sock.recvfrom(4096)
            return SomeIpMessage.from_bytes(data)
        except socket.timeout:
            return None

    def close(self):
        """Close the socket"""
        self.sock.close()

class SomeIpStackTester:
    """Test harness for SOME/IP stack components"""

    def __init__(self, build_dir: str = "../build"):
        self.build_dir = build_dir
        self.processes: List[subprocess.Popen] = []
        self.test_dir = tempfile.mkdtemp(prefix="someip_test_")

    def start_service(self, executable: str, args: List[str] = None) -> subprocess.Popen:
        """Start a SOME/IP service"""
        cmd = [os.path.join(self.build_dir, "bin", executable)]
        if args:
            cmd.extend(args)

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.build_dir
        )
        self.processes.append(proc)
        time.sleep(0.5)  # Allow service to start
        return proc

    def stop_all_services(self):
        """Stop all running services"""
        for proc in self.processes:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
        self.processes.clear()

    def cleanup(self):
        """Clean up test resources"""
        self.stop_all_services()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

class IntegrationTests(unittest.TestCase):
    """Integration tests for the complete SOME/IP stack"""

    def setUp(self):
        """Set up test environment"""
        self.tester = SomeIpStackTester()
        self.client = SomeIpClient(("127.0.0.1", 0), ("127.0.0.1", 3000))

    def tearDown(self):
        """Clean up test environment"""
        self.client.close()
        self.tester.cleanup()

    def test_echo_communication(self):
        """Test basic request-response communication"""
        # Start echo server
        self.tester.start_service("echo_server")

        # Create test message
        test_payload = b"Hello, SOME/IP!"
        request = SomeIpMessage(
            service_id=0x1234,
            method_id=0x0001,
            message_type=0x00,  # REQUEST
            payload=test_payload
        )

        # Send request
        self.client.send_message(request)

        # Receive response
        response = self.client.receive_message()
        self.assertIsNotNone(response, "No response received")

        # Verify response
        self.assertEqual(response.service_id, request.service_id)
        self.assertEqual(response.method_id, request.method_id)
        self.assertEqual(response.message_type, 0x80)  # RESPONSE
        self.assertEqual(response.payload, test_payload)

    def test_rpc_calculator(self):
        """Test RPC calculator service"""
        # Start calculator server
        self.tester.start_service("rpc_calculator_server")

        # Test ADD operation
        add_request = SomeIpMessage(
            service_id=0x1234,
            method_id=0x0001,  # ADD method
            message_type=0x00,
            payload=struct.pack(">ii", 42, 58)  # 42 + 58
        )

        self.client.send_message(add_request)
        response = self.client.receive_message()
        self.assertIsNotNone(response)

        result = struct.unpack(">i", response.payload)[0]
        self.assertEqual(result, 100)  # 42 + 58 = 100

    def test_service_discovery(self):
        """Test service discovery functionality"""
        # Start SD server
        sd_server = self.tester.start_service("sd_service_server")
        time.sleep(1.0)  # Allow server to start

        # Start SD client
        sd_client = self.tester.start_service("sd_service_client")
        time.sleep(2.0)  # Allow discovery process

        # Check if client found server (by checking process output)
        try:
            stdout, stderr = sd_client.communicate(timeout=5.0)
            output = stdout.decode() + stderr.decode()
            self.assertIn("Service discovered", output,
                         "Service discovery failed")
        except subprocess.TimeoutExpired:
            self.fail("Service discovery timed out")

    def test_event_system(self):
        """Test event publishing and subscription"""
        # Start event publisher
        publisher = self.tester.start_service("event_publisher")
        time.sleep(1.0)

        # Start event subscriber
        subscriber = self.tester.start_service("event_subscriber")
        time.sleep(3.0)  # Allow event exchange

        # Check if events were received
        try:
            stdout, stderr = subscriber.communicate(timeout=5.0)
            output = stdout.decode() + stderr.decode()
            self.assertIn("Event received", output,
                         "Event reception failed")
        except subprocess.TimeoutExpired:
            self.fail("Event system test timed out")

    def test_tp_large_messages(self):
        """Test TP segmentation and reassembly"""
        # Start TP example
        tp_proc = self.tester.start_service("tp_example")

        # Wait for completion
        try:
            stdout, stderr = tp_proc.communicate(timeout=10.0)
            output = stdout.decode() + stderr.decode()
            self.assertIn("VERIFIED", output,
                         "TP message integrity check failed")
        except subprocess.TimeoutExpired:
            self.fail("TP test timed out")

class PerformanceTests(unittest.TestCase):
    """Performance tests for the SOME/IP stack"""

    def setUp(self):
        self.tester = SomeIpStackTester()

    def tearDown(self):
        self.tester.cleanup()

    def test_message_throughput(self):
        """Test message throughput"""
        self.tester.start_service("echo_server")

        client = SomeIpClient(("127.0.0.1", 0), ("127.0.0.1", 3000))

        # Send 100 messages and measure time
        start_time = time.time()
        for i in range(100):
            msg = SomeIpMessage(0x1234, 0x0001, payload=f"Message {i}".encode())
            client.send_message(msg)
            response = client.receive_message()
            self.assertIsNotNone(response)

        end_time = time.time()
        duration = end_time - start_time

        messages_per_second = 100 / duration
        print(".2f")

        # Should handle at least 100 msgs/sec
        self.assertGreater(messages_per_second, 50.0)

        client.close()

if __name__ == '__main__':
    # Add command line options
    import argparse
    parser = argparse.ArgumentParser(description='SOME/IP Stack Integration Tests')
    parser.add_argument('--integration-only', action='store_true',
                       help='Run only integration tests')
    parser.add_argument('--performance-only', action='store_true',
                       help='Run only performance tests')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args, unknown = parser.parse_known_args()

    # Configure test runner
    if args.verbose:
        unittest.TestLoader.verbosity = 2

    # Select test suites
    loader = unittest.TestLoader()

    if args.integration_only:
        suite = loader.loadTestsFromTestCase(IntegrationTests)
    elif args.performance_only:
        suite = loader.loadTestsFromTestCase(PerformanceTests)
    else:
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromTestCase(IntegrationTests))
        suite.addTests(loader.loadTestsFromTestCase(PerformanceTests))

    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
