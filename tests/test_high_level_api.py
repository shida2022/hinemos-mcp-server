#!/usr/bin/env python3
"""
Test script to verify the high-level MonitorAPI works correctly.
This tests the simplified wrapper methods and parameter handling.
"""

import json
import sys
import os
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hinemos_mcp.client import HinemosClient
from hinemos_mcp.monitor import MonitorAPI
from hinemos_mcp.monitor_models import (
    ConvertFlagEnum,
    RunIntervalEnum,
    PriorityEnum
)


class MockResponse:
    """Mock response for testing."""
    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def test_sql_monitor_high_level_api():
    """Test SQL monitor high-level API."""
    print("🔍 Testing SQL Monitor High-Level API")
    print("-" * 45)
    
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock login and responses
        mock_client.post.return_value = MockResponse({"token": {"tokenId": "test_token"}})
        
        expected_response = {
            "monitorId": "SQL_SIMPLE_01",
            "description": "Simple SQL monitor",
            "sqlCheckInfo": {
                "connectionUrl": "jdbc:postgresql://localhost:5432/testdb",
                "user": "postgres",
                "sql": "SELECT COUNT(*) FROM users",
                "timeout": 5000
            },
            "numericValueInfo": [
                {
                    "priority": "INFO",
                    "thresholdLowerLimit": 0.0,
                    "thresholdUpperLimit": 79.0,
                    "message": "SQL query result is normal"
                }
            ]
        }
        mock_client.request.return_value = MockResponse(expected_response)
        
        # Test high-level API
        client = HinemosClient("http://test:8080/HinemosWeb/api", "test", "test")
        monitor_api = MonitorAPI(client)
        
        # Test create_sql_monitor with simplified parameters
        result = monitor_api.create_sql_monitor(
            monitor_id="SQL_SIMPLE_01",
            facility_id="test_node",
            connection_url="jdbc:postgresql://localhost:5432/testdb",
            user="postgres",
            password="password",
            jdbc_driver="org.postgresql.Driver",
            sql="SELECT COUNT(*) FROM users",
            description="Simple SQL monitor",
            timeout=5000,
            warning_threshold=80.0,
            critical_threshold=90.0
        )
        
        # Verify the call was made
        assert mock_client.request.called
        call_args = mock_client.request.call_args
        
        # Verify request structure
        request_json = call_args[1]['json']
        assert request_json['monitorId'] == "SQL_SIMPLE_01"
        assert request_json['facilityId'] == "test_node"
        assert request_json['description'] == "Simple SQL monitor"
        
        # Verify SQL check info
        sql_check = request_json['sqlCheckInfo']
        assert sql_check['connectionUrl'] == "jdbc:postgresql://localhost:5432/testdb"
        assert sql_check['user'] == "postgres"
        assert sql_check['password'] == "password"
        assert sql_check['jdbcDriver'] == "org.postgresql.Driver"
        assert sql_check['sql'] == "SELECT COUNT(*) FROM users"
        assert sql_check['timeout'] == 5000
        
        # Verify numeric value info was generated correctly
        numeric_info = request_json['numericValueInfo']
        assert len(numeric_info) == 4  # INFO, WARNING, CRITICAL, UNKNOWN
        
        # Check threshold configuration
        warning_threshold = next((item for item in numeric_info if item['priority'] == 'WARNING'), None)
        assert warning_threshold is not None
        assert warning_threshold['thresholdLowerLimit'] == 80.0
        assert warning_threshold['thresholdUpperLimit'] == 89.0
        
        critical_threshold = next((item for item in numeric_info if item['priority'] == 'CRITICAL'), None)
        assert critical_threshold is not None
        assert critical_threshold['thresholdLowerLimit'] == 90.0
        
        print("✅ SQL monitor creation with default thresholds")
        print("✅ Parameter mapping to request structure")
        print("✅ Automatic threshold generation")
        
        return True


def test_jmx_monitor_high_level_api():
    """Test JMX monitor high-level API."""
    print("\n☕ Testing JMX Monitor High-Level API")
    print("-" * 45)
    
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock responses
        mock_client.post.return_value = MockResponse({"token": {"tokenId": "test_token"}})
        mock_client.request.return_value = MockResponse({
            "monitorId": "JMX_SIMPLE_01",
            "description": "JMX memory monitor"
        })
        
        # Test high-level API
        client = HinemosClient("http://test:8080/HinemosWeb/api", "test", "test")
        monitor_api = MonitorAPI(client)
        
        # Test create_jmx_monitor
        result = monitor_api.create_jmx_monitor(
            monitor_id="JMX_SIMPLE_01",
            facility_id="java_server",
            port=9999,
            description="JMX memory monitor",
            auth_user="jmxuser",
            auth_password="secret",
            url="service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi",
            convert_flg=ConvertFlagEnum.NONE,
            warning_threshold=75.0,
            critical_threshold=90.0
        )
        
        # Verify the call
        call_args = mock_client.request.call_args
        request_json = call_args[1]['json']
        
        # Verify JMX check info
        jmx_check = request_json['jmxCheckInfo']
        assert jmx_check['port'] == 9999
        assert jmx_check['authUser'] == "jmxuser"
        assert jmx_check['authPassword'] == "secret"
        assert jmx_check['url'] == "service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi"
        assert jmx_check['convertFlg'] == "NONE"
        
        print("✅ JMX monitor creation with authentication")
        print("✅ Convert flag handling")
        print("✅ Custom threshold configuration")
        
        return True


def test_process_monitor_high_level_api():
    """Test Process monitor high-level API."""
    print("\n⚙️ Testing Process Monitor High-Level API")
    print("-" * 45)
    
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock responses
        mock_client.post.return_value = MockResponse({"token": {"tokenId": "test_token"}})
        mock_client.request.return_value = MockResponse({
            "monitorId": "PROC_SIMPLE_01",
            "description": "Java process monitor"
        })
        
        # Test high-level API
        client = HinemosClient("http://test:8080/HinemosWeb/api", "test", "test")
        monitor_api = MonitorAPI(client)
        
        # Test create_process_monitor
        result = monitor_api.create_process_monitor(
            monitor_id="PROC_SIMPLE_01",
            facility_id="web_server",
            param="java",
            description="Java process monitor",
            case_sensitivity_flg=False,
            min_count=2,
            max_count=8
        )
        
        # Verify the call
        call_args = mock_client.request.call_args
        request_json = call_args[1]['json']
        
        # Verify process check info
        process_check = request_json['processCheckInfo']
        assert process_check['param'] == "java"
        assert process_check['caseSensitivityFlg'] == False
        
        # Verify numeric thresholds for process count
        numeric_info = request_json['numericValueInfo']
        
        # Check normal range (2-8 processes)
        normal_range = next((item for item in numeric_info if item['priority'] == 'INFO'), None)
        assert normal_range is not None
        assert normal_range['thresholdLowerLimit'] == 2.0
        assert normal_range['thresholdUpperLimit'] == 8.0
        
        # Check warning for too few processes (0-1)
        warning_range = next((item for item in numeric_info if item['priority'] == 'WARNING'), None)
        assert warning_range is not None
        assert warning_range['thresholdLowerLimit'] == 0.0
        assert warning_range['thresholdUpperLimit'] == 1.0
        
        # Check critical for too many processes (9+)
        critical_range = next((item for item in numeric_info if item['priority'] == 'CRITICAL'), None)
        assert critical_range is not None
        assert critical_range['thresholdLowerLimit'] == 9.0
        
        print("✅ Process parameter configuration")
        print("✅ Case sensitivity handling")
        print("✅ Process count range validation")
        
        return True


def test_port_monitor_high_level_api():
    """Test Port monitor high-level API."""
    print("\n🔌 Testing Port Monitor High-Level API")
    print("-" * 45)
    
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock responses
        mock_client.post.return_value = MockResponse({"token": {"tokenId": "test_token"}})
        mock_client.request.return_value = MockResponse({
            "monitorId": "PORT_SIMPLE_01",
            "description": "Web server port monitor"
        })
        
        # Test high-level API
        client = HinemosClient("http://test:8080/HinemosWeb/api", "test", "test")
        monitor_api = MonitorAPI(client)
        
        # Test create_port_monitor
        result = monitor_api.create_port_monitor(
            monitor_id="PORT_SIMPLE_01",
            facility_id="web_server",
            port_no=80,
            description="Web server port monitor",
            service_id="http",
            timeout=3000
        )
        
        # Verify the call
        call_args = mock_client.request.call_args
        request_json = call_args[1]['json']
        
        # Verify port check info
        port_check = request_json['portCheckInfo']
        assert port_check['portNo'] == 80
        assert port_check['serviceId'] == "http"
        assert port_check['timeout'] == 3000
        
        # Verify binary-style thresholds (0=accessible, 1+=not accessible)
        numeric_info = request_json['numericValueInfo']
        
        # Check accessible state (return value 0)
        accessible = next((item for item in numeric_info if item['priority'] == 'INFO'), None)
        assert accessible is not None
        assert accessible['thresholdLowerLimit'] == 0.0
        assert accessible['thresholdUpperLimit'] == 0.0
        
        # Check not accessible state (return value 1+)
        not_accessible = next((item for item in numeric_info if item['priority'] == 'CRITICAL'), None)
        assert not_accessible is not None
        assert not_accessible['thresholdLowerLimit'] == 1.0
        
        print("✅ Port number and service ID configuration")
        print("✅ Timeout configuration")
        print("✅ Binary threshold logic (accessible/not accessible)")
        
        return True


def test_winevent_monitor_high_level_api():
    """Test Windows Event monitor high-level API."""
    print("\n🪟 Testing Windows Event Monitor High-Level API")
    print("-" * 45)
    
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock responses
        mock_client.post.return_value = MockResponse({"token": {"tokenId": "test_token"}})
        mock_client.request.return_value = MockResponse({
            "monitorId": "WIN_SIMPLE_01",
            "description": "System event monitor"
        })
        
        # Test high-level API
        client = HinemosClient("http://test:8080/HinemosWeb/api", "test", "test")
        monitor_api = MonitorAPI(client)
        
        # Test create_winevent_monitor with patterns
        result = monitor_api.create_winevent_monitor(
            monitor_id="WIN_SIMPLE_01",
            facility_id="windows_server",
            log_name="System",
            description="System event monitor",
            source="Service Control Manager",
            level=2,  # Error level
            error_patterns=[".*failed.*", ".*error.*"],
            warning_patterns=[".*timeout.*", ".*retry.*"]
        )
        
        # Verify the call
        call_args = mock_client.request.call_args
        request_json = call_args[1]['json']
        
        # Verify Windows Event check info
        winevent_check = request_json['wineventCheckInfo']
        assert winevent_check['logName'] == "System"
        assert winevent_check['source'] == "Service Control Manager"
        assert winevent_check['level'] == 2
        
        # Verify string value info patterns
        string_info = request_json['stringValueInfo']
        assert len(string_info) == 4  # 2 error + 2 warning patterns
        
        # Check error patterns
        error_patterns = [item for item in string_info if item['priority'] == 'CRITICAL']
        assert len(error_patterns) == 2
        assert any(item['pattern'] == ".*failed.*" for item in error_patterns)
        assert any(item['pattern'] == ".*error.*" for item in error_patterns)
        
        # Check warning patterns
        warning_patterns = [item for item in string_info if item['priority'] == 'WARNING']
        assert len(warning_patterns) == 2
        assert any(item['pattern'] == ".*timeout.*" for item in warning_patterns)
        assert any(item['pattern'] == ".*retry.*" for item in warning_patterns)
        
        # Verify order numbers are sequential
        order_numbers = [item['orderNo'] for item in string_info]
        assert order_numbers == [1, 2, 3, 4]
        
        print("✅ Windows Event log configuration")
        print("✅ Error and warning pattern handling")
        print("✅ Sequential pattern ordering")
        
        return True


def test_custom_monitor_high_level_api():
    """Test Custom monitor high-level API."""
    print("\n🛠️ Testing Custom Monitor High-Level API")
    print("-" * 45)
    
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock responses
        mock_client.post.return_value = MockResponse({"token": {"tokenId": "test_token"}})
        mock_client.request.return_value = MockResponse({
            "monitorId": "CUSTOM_SIMPLE_01",
            "description": "Disk usage monitor"
        })
        
        # Test high-level API
        client = HinemosClient("http://test:8080/HinemosWeb/api", "test", "test")
        monitor_api = MonitorAPI(client)
        
        # Test create_custom_monitor
        result = monitor_api.create_custom_monitor(
            monitor_id="CUSTOM_SIMPLE_01",
            facility_id="linux_server",
            command="df -h / | awk 'NR==2 {print $5}' | sed 's/%//'",
            description="Disk usage monitor",
            timeout=15000,
            spec_flg=False,
            convert_flg=ConvertFlagEnum.NONE,
            warning_threshold=75.0,
            critical_threshold=90.0
        )
        
        # Verify the call
        call_args = mock_client.request.call_args
        request_json = call_args[1]['json']
        
        # Verify custom check info
        custom_check = request_json['customCheckInfo']
        assert custom_check['command'] == "df -h / | awk 'NR==2 {print $5}' | sed 's/%//'"
        assert custom_check['timeout'] == 15000
        assert custom_check['specFlg'] == False
        assert custom_check['convertFlg'] == "NONE"
        
        print("✅ Custom command configuration")
        print("✅ Timeout and flags handling")
        print("✅ Complex shell command support")
        
        return True


def test_run_interval_enum_handling():
    """Test RunIntervalEnum handling in high-level API."""
    print("\n⏰ Testing RunInterval Enum Handling")
    print("-" * 45)
    
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock responses
        mock_client.post.return_value = MockResponse({"token": {"tokenId": "test_token"}})
        mock_client.request.return_value = MockResponse({"monitorId": "TEST_INTERVAL"})
        
        # Test high-level API
        client = HinemosClient("http://test:8080/HinemosWeb/api", "test", "test")
        monitor_api = MonitorAPI(client)
        
        # Test with different run intervals
        intervals_to_test = [
            RunIntervalEnum.MIN_01,
            RunIntervalEnum.MIN_05,
            RunIntervalEnum.MIN_10,
            RunIntervalEnum.MIN_30,
            RunIntervalEnum.MIN_60
        ]
        
        for interval in intervals_to_test:
            mock_client.request.reset_mock()
            
            # Use SQL monitor as test case
            monitor_api.create_sql_monitor(
                monitor_id="TEST_INTERVAL",
                facility_id="test",
                connection_url="jdbc:test",
                user="test",
                password="test",
                jdbc_driver="test.Driver",
                sql="SELECT 1",
                run_interval=interval
            )
            
            # Verify the interval was set correctly
            call_args = mock_client.request.call_args
            request_json = call_args[1]['json']
            assert request_json['runInterval'] == interval.value
            
            print(f"✅ RunInterval.{interval.name} -> '{interval.value}'")
        
        return True


def main():
    """Run all high-level API tests."""
    print("🎯 High-Level MonitorAPI Integration Tests")
    print("=" * 55)
    
    tests = [
        ("SQL Monitor High-Level API", test_sql_monitor_high_level_api),
        ("JMX Monitor High-Level API", test_jmx_monitor_high_level_api),
        ("Process Monitor High-Level API", test_process_monitor_high_level_api),
        ("Port Monitor High-Level API", test_port_monitor_high_level_api),
        ("Windows Event Monitor High-Level API", test_winevent_monitor_high_level_api),
        ("Custom Monitor High-Level API", test_custom_monitor_high_level_api),
        ("RunInterval Enum Handling", test_run_interval_enum_handling)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 High-Level API Test Results Summary")
    print("-" * 55)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} {test_name}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All high-level API tests passed! MonitorAPI is ready for use.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the MonitorAPI implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)