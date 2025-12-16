#!/usr/bin/env python3
"""
SOME/IP Stack Coverage Report Generator

Generates comprehensive coverage reports for the SOME/IP implementation
against protocol specification requirements.
"""

import os
import json
import subprocess
from typing import Dict, List, Set, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

class CoverageAnalyzer:
    """Analyze test coverage against SOME/IP specification"""

    def __init__(self):
        self.specification_requirements = {
            # Core Protocol Features
            "message_format": {
                "header_structure": False,
                "big_endian_encoding": False,
                "length_calculation": False,
                "protocol_version": False,
                "message_types": False,
                "return_codes": False,
                "session_handling": False
            },
            "transport_layer": {
                "udp_sockets": False,
                "port_management": False,
                "multicast_support": False,
                "packet_fragmentation": False,
                "error_handling": False
            },
            "service_discovery": {
                "sd_messages": False,
                "multicast_address": False,
                "offer_service": False,
                "find_service": False,
                "subscribe_events": False,
                "ttl_handling": False,
                "reboot_flag": False
            },
            "transport_protocol": {
                "segmentation": False,
                "reassembly": False,
                "sequence_numbers": False,
                "acknowledgments": False,
                "timeout_handling": False
            },
            "event_system": {
                "event_publishers": False,
                "event_subscribers": False,
                "field_notifications": False,
                "subscription_management": False
            },
            "rpc_system": {
                "method_calls": False,
                "parameter_serialization": False,
                "return_values": False,
                "error_handling": False,
                "timeouts": False
            },
            "safety_critical": {
                "memory_bounds": False,
                "resource_limits": False,
                "error_recovery": False,
                "deterministic_behavior": False,
                "timeout_management": False
            },
            "performance": {
                "throughput": False,
                "latency": False,
                "memory_usage": False,
                "concurrent_connections": False
            }
        }

        self.test_mapping = {
            # Map test functions to specification requirements
            "test_valid_message_header": ["message_format.header_structure"],
            "test_header_endianness": ["message_format.big_endian_encoding"],
            "test_length_field_calculation": ["message_format.length_calculation"],
            "test_invalid_protocol_version": ["message_format.protocol_version"],
            "test_invalid_message_type": ["message_format.message_types"],
            "test_return_code_validation": ["message_format.return_codes"],
            "test_session_id_requirements": ["message_format.session_handling"],

            "test_udp_socket_handling": ["transport_layer.udp_sockets"],
            "test_port_assignment": ["transport_layer.port_management"],
            "test_sd_multicast_address": ["transport_layer.multicast_support", "service_discovery.multicast_address"],
            "test_packet_size_limits": ["transport_layer.packet_fragmentation"],

            "test_sd_service_offer_format": ["service_discovery.sd_messages", "service_discovery.offer_service"],
            "test_sd_reboot_flag": ["service_discovery.reboot_flag"],
            "test_sd_ttl_handling": ["service_discovery.ttl_handling"],

            "test_tp_segmentation_reassembly": ["transport_protocol.segmentation", "transport_protocol.reassembly"],
            "test_tp_sequence_numbers": ["transport_protocol.sequence_numbers"],

            "test_event_publisher_subscriber": ["event_system.event_publishers", "event_system.event_subscribers"],
            "test_calculator_add": ["rpc_system.method_calls", "rpc_system.parameter_serialization", "rpc_system.return_values"],

            "test_memory_bounds_checking": ["safety_critical.memory_bounds"],
            "test_concurrent_connections": ["safety_critical.resource_limits", "performance.concurrent_connections"],
            "test_timeout_behavior": ["safety_critical.timeout_management", "rpc_system.timeouts"],

            "test_message_throughput": ["performance.throughput"],
            "test_message_latency": ["performance.latency"]
        }

    def analyze_gtest_coverage(self, build_dir: str) -> Dict[str, bool]:
        """Analyze GTest coverage from test execution"""
        covered_tests = {}

        # Run tests and capture output
        try:
            result = subprocess.run(
                ["ctest", "--output-on-failure", "-O", "/tmp/ctest_output.txt"],
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse test output
            if os.path.exists("/tmp/ctest_output.txt"):
                with open("/tmp/ctest_output.txt", "r") as f:
                    output = f.read()

                # Look for test names
                for line in output.split('\n'):
                    if line.startswith("  START") or "RUN" in line:
                        # Extract test name
                        parts = line.split()
                        if len(parts) >= 3:
                            test_name = parts[-1]
                            covered_tests[test_name] = True

        except subprocess.TimeoutExpired:
            pass

        return covered_tests

    def analyze_pytest_coverage(self, test_dir: str) -> Dict[str, bool]:
        """Analyze pytest coverage"""
        covered_tests = {}

        try:
            # Run pytest with json report
            result = subprocess.run(
                ["python", "-m", "pytest", "--json-report", "--json-report-file=/tmp/pytest_report.json"],
                cwd=test_dir,
                capture_output=True,
                timeout=300
            )

            if os.path.exists("/tmp/pytest_report.json"):
                with open("/tmp/pytest_report.json", "r") as f:
                    data = json.load(f)

                for test in data.get("tests", []):
                    test_name = test["nodeid"].split("::")[-1]
                    covered_tests[test_name] = test["outcome"] == "passed"

        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            pass

        return covered_tests

    def update_coverage_from_tests(self, gtest_results: Dict[str, bool],
                                 pytest_results: Dict[str, bool]) -> None:
        """Update coverage based on test results"""

        all_test_results = {**gtest_results, **pytest_results}

        for test_name, passed in all_test_results.items():
            if test_name in self.test_mapping and passed:
                for req_path in self.test_mapping[test_name]:
                    self._set_requirement_coverage(req_path, True)

    def _set_requirement_coverage(self, req_path: str, covered: bool) -> None:
        """Set coverage for a requirement path like 'message_format.header_structure'"""
        parts = req_path.split('.')
        current = self.specification_requirements

        for part in parts[:-1]:
            if part not in current:
                return
            current = current[part]

        if parts[-1] in current:
            current[parts[-1]] = covered

    def generate_coverage_report(self) -> Dict:
        """Generate comprehensive coverage report"""
        report = {
            "summary": {
                "total_requirements": 0,
                "covered_requirements": 0,
                "coverage_percentage": 0.0
            },
            "categories": {},
            "detailed_coverage": {}
        }

        total_reqs = 0
        covered_reqs = 0

        for category, requirements in self.specification_requirements.items():
            category_total = 0
            category_covered = 0

            for req, covered in requirements.items():
                category_total += 1
                if covered:
                    category_covered += 1

            total_reqs += category_total
            covered_reqs += category_covered

            report["categories"][category] = {
                "total": category_total,
                "covered": category_covered,
                "percentage": (category_covered / category_total * 100) if category_total > 0 else 0
            }

        report["summary"]["total_requirements"] = total_reqs
        report["summary"]["covered_requirements"] = covered_reqs
        report["summary"]["coverage_percentage"] = (covered_reqs / total_reqs * 100) if total_reqs > 0 else 0

        report["detailed_coverage"] = self.specification_requirements

        return report

    def print_report(self, report: Dict) -> None:
        """Print coverage report"""
        print("🎯 SOME/IP Protocol Specification Coverage Report")
        print("=" * 60)

        summary = report["summary"]
        print(".1f"
              f"Requirements: {summary['covered_requirements']}/{summary['total_requirements']}")

        print("\n📊 Category Breakdown:")
        for category, stats in report["categories"].items():
            print("25s"
                  f"{stats['covered']:2d}/{stats['total']:2d} "
                  ".1f")

        print("\n📋 Detailed Coverage:"        for category, requirements in report["detailed_coverage"].items():
            print(f"\n🔍 {category.replace('_', ' ').title()}:")
            for req, covered in requirements.items():
                status = "✅" if covered else "❌"
                print(f"  {status} {req.replace('_', ' ')}")

    def export_report(self, report: Dict, output_file: str) -> None:
        """Export report to JSON file"""
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report exported to: {output_file}")

def main():
    """Main coverage analysis function"""
    analyzer = CoverageAnalyzer()

    # Get project directories
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    build_dir = project_dir / "build"

    if not build_dir.exists():
        print("❌ Build directory not found. Run build first.")
        return 1

    print("🔬 Analyzing test coverage...")

    # Analyze test results
    gtest_results = analyzer.analyze_gtest_coverage(str(build_dir))
    pytest_results = analyzer.analyze_pytest_coverage(str(script_dir))

    # Update coverage
    analyzer.update_coverage_from_tests(gtest_results, pytest_results)

    # Generate and display report
    report = analyzer.generate_coverage_report()
    analyzer.print_report(report)

    # Export report
    output_file = str(project_dir / "test_coverage_report.json")
    analyzer.export_report(report, output_file)

    # Return success if coverage > 80%
    coverage_pct = report["summary"]["coverage_percentage"]
    if coverage_pct >= 80.0:
        print(".1f"        return 0
    else:
        print(".1f"        return 1

if __name__ == "__main__":
    exit(main())
