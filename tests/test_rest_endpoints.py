#!/usr/bin/env python3
"""
Test script to verify REST API endpoints and HTTP request structures.
This script validates the client's HTTP request generation without making actual API calls.
"""

import json
import sys
import os
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hinemos_mcp.client import HinemosClient
from hinemos_mcp.monitor_models import (
    AddSqlMonitorRequest,
    AddJmxMonitorRequest,
    AddProcessMonitorRequest,
    AddPortMonitorRequest,
    AddWinEventMonitorRequest,
    AddCustomMonitorRequest,
    SqlCheckInfoRequest,
    JmxCheckInfoRequest,
    ProcessCheckInfoRequest,
    PortCheckInfoRequest,
    WinEventCheckInfoRequest,
    CustomCheckInfoRequest,
    MonitorNumericValueInfoRequest,
    MonitorStringValueInfoRequest,
    MonitorNumericTypeEnum,
    PriorityEnum,
    ConvertFlagEnum,
    RunIntervalEnum
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


def test_sql_monitor_endpoints():
    """Test SQL monitor API endpoints."""
    print("🔍 Testing SQL Monitor Endpoints")
    print("-" * 40)
    
    # Create test data
    sql_check_info = SqlCheckInfoRequest(
        connection_url="jdbc:postgresql://localhost:5432/testdb",
        user="postgres",
        password="password",
        jdbc_driver="org.postgresql.Driver",
        sql="SELECT COUNT(*) FROM users",
        timeout=5000
    )
    
    numeric_value_info = [
        MonitorNumericValueInfoRequest(
            monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
            priority=PriorityEnum.INFO,
            threshold_lower_limit=0.0,
            threshold_upper_limit=79.0,
            message="Normal count"
        )
    ]
    
    sql_monitor = AddSqlMonitorRequest(
        monitor_id="SQL_TEST_01",
        facility_id="test_facility",
        description="Test SQL monitor",
        run_interval=RunIntervalEnum.MIN_05,
        owner_role_id="ADMINISTRATORS",
        sql_check_info=sql_check_info,
        numeric_value_info=numeric_value_info
    )
    
    # Mock HTTP client
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock login response
        mock_client.post.return_value = MockResponse({
            "token": {"tokenId": "test_token"}
        })
        
        # Mock monitor creation response
        expected_response = {
            "monitorId": "SQL_TEST_01",
            "description": "Test SQL monitor",
            "sqlCheckInfo": {
                "connectionUrl": "jdbc:postgresql://localhost:5432/testdb",
                "sql": "SELECT COUNT(*) FROM users"
            }
        }
        mock_client.request.return_value = MockResponse(expected_response)
        
        # Test client
        client = HinemosClient("http://test:8080/HinemosWeb/api", "test", "test")
        client.login()
        
        # Test add SQL monitor
        result = client.add_sql_monitor(sql_monitor)
        
        # Verify the request was made correctly
        assert mock_client.request.called
        call_args = mock_client.request.call_args
        
        # Check HTTP method and URL
        assert call_args[1]['method'] == 'POST'
        expected_url = "http://test:8080/HinemosWeb/api/MonitorsettingRestEndpoints/monitorsetting/sql"
        assert call_args[1]['url'] == expected_url
        
        # Check request data structure
        request_json = call_args[1]['json']
        assert 'monitorId' in request_json
        assert 'sqlCheckInfo' in request_json
        assert 'connectionUrl' in request_json['sqlCheckInfo']
        
        print("✅ SQL monitor POST endpoint: /monitorsetting/sql")
        print(f"✅ Request URL: {expected_url}")
        print("✅ Request data structure validated")
        
        # Test modify SQL monitor
        mock_client.request.reset_mock()
        from hinemos_mcp.monitor_models import ModifySqlMonitorRequest
        modify_request = ModifySqlMonitorRequest(description="Modified SQL monitor")
        
        # Mock modify response
        mock_client.request.return_value = MockResponse(expected_response)
        
        result = client.modify_sql_monitor("SQL_TEST_01", modify_request)
        
        # Verify modify request
        call_args = mock_client.request.call_args
        assert call_args[1]['method'] == 'PUT'
        expected_url = "http://test:8080/HinemosWeb/api/MonitorsettingRestEndpoints/monitorsetting/sql/SQL_TEST_01"
        assert call_args[1]['url'] == expected_url
        
        print("✅ SQL monitor PUT endpoint: /monitorsetting/sql/{monitor_id}")
        
        # Test list SQL monitors
        mock_client.request.reset_mock()
        mock_client.request.return_value = MockResponse([expected_response])
        
        result = client.get_sql_monitor_list()
        
        call_args = mock_client.request.call_args
        assert call_args[1]['method'] == 'GET'
        expected_url = "http://test:8080/HinemosWeb/api/MonitorsettingRestEndpoints/monitorsetting/sql"
        assert call_args[1]['url'] == expected_url
        
        print("✅ SQL monitor GET endpoint: /monitorsetting/sql")
        
        return True


def test_jmx_monitor_endpoints():
    """Test JMX monitor API endpoints."""
    print("\n☕ Testing JMX Monitor Endpoints")
    print("-" * 40)
    
    # Create test data
    jmx_check_info = JmxCheckInfoRequest(
        port=9999,
        auth_user="jmxuser",
        auth_password="jmxpass",
        convert_flg=ConvertFlagEnum.NONE
    )
    
    numeric_value_info = [
        MonitorNumericValueInfoRequest(
            monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
            priority=PriorityEnum.CRITICAL,
            threshold_lower_limit=90.0,
            threshold_upper_limit=999999.0,
            message="JMX value too high"
        )
    ]
    
    jmx_monitor = AddJmxMonitorRequest(
        monitor_id="JMX_TEST_01",
        facility_id="test_facility",
        description="Test JMX monitor",
        run_interval=RunIntervalEnum.MIN_05,
        owner_role_id="ADMINISTRATORS",
        jmx_check_info=jmx_check_info,
        numeric_value_info=numeric_value_info
    )
    
    # Mock HTTP client
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock responses
        mock_client.post.return_value = MockResponse({"token": {"tokenId": "test_token"}})
        expected_response = {
            "monitorId": "JMX_TEST_01",
            "description": "Test JMX monitor",
            "jmxCheckInfo": {"port": 9999}
        }
        mock_client.request.return_value = MockResponse(expected_response)
        
        # Test client
        client = HinemosClient("http://test:8080/HinemosWeb/api", "test", "test")
        client.login()
        
        # Test add JMX monitor
        result = client.add_jmx_monitor(jmx_monitor)
        
        # Verify request
        call_args = mock_client.request.call_args
        assert call_args[1]['method'] == 'POST'
        expected_url = "http://test:8080/HinemosWeb/api/MonitorsettingRestEndpoints/monitorsetting/jmx"
        assert call_args[1]['url'] == expected_url
        
        request_json = call_args[1]['json']
        assert 'jmxCheckInfo' in request_json
        assert 'port' in request_json['jmxCheckInfo']
        
        print("✅ JMX monitor POST endpoint: /monitorsetting/jmx")
        print(f"✅ Request URL: {expected_url}")
        print("✅ Request data structure validated")
        
        return True


def test_endpoint_url_construction():
    """Test endpoint URL construction for all new monitor types."""
    print("\n🌐 Testing Endpoint URL Construction")
    print("-" * 40)
    
    base_url = "http://hinemos:8080/HinemosWeb/api"
    
    # Test endpoint mappings
    endpoint_tests = [
        ("sql", "/monitorsetting/sql"),
        ("jmx", "/monitorsetting/jmx"),
        ("process", "/monitorsetting/process"),
        ("port", "/monitorsetting/port"),
        ("winevent", "/monitorsetting/winevent"),
        ("custom", "/monitorsetting/custom")
    ]
    
    # Mock the client's _make_request method to capture URLs
    captured_urls = []
    
    def mock_make_request(method, endpoint, **kwargs):
        # Simulate URL construction logic from client
        endpoint_cleaned = endpoint.lstrip("/")
        if endpoint_cleaned.startswith("monitorsetting/"):
            url = f"{base_url}/MonitorsettingRestEndpoints/{endpoint_cleaned}"
        else:
            url = f"{base_url}/{endpoint_cleaned}"
        captured_urls.append((method, url))
        return {"monitorId": "test"}
    
    # Test each monitor type's endpoints
    for monitor_type, expected_path in endpoint_tests:
        captured_urls.clear()
        
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.post.return_value = MockResponse({"token": {"tokenId": "test_token"}})
            
            client = HinemosClient(base_url, "test", "test")
            client._make_request = mock_make_request
            client._token = "test_token"  # Skip login
            
            # Test POST (create)
            try:
                if monitor_type == "sql":
                    from hinemos_mcp.monitor_models import AddSqlMonitorRequest, SqlCheckInfoRequest
                    monitor_request = AddSqlMonitorRequest(
                        monitor_id="test", facility_id="test",
                        sql_check_info=SqlCheckInfoRequest(
                            connection_url="test", user="test", password="test",
                            jdbc_driver="test", sql="test"
                        ),
                        numeric_value_info=[]
                    )
                    client.add_sql_monitor(monitor_request)
                elif monitor_type == "jmx":
                    from hinemos_mcp.monitor_models import AddJmxMonitorRequest, JmxCheckInfoRequest
                    monitor_request = AddJmxMonitorRequest(
                        monitor_id="test", facility_id="test",
                        jmx_check_info=JmxCheckInfoRequest(port=9999),
                        numeric_value_info=[]
                    )
                    client.add_jmx_monitor(monitor_request)
                elif monitor_type == "process":
                    from hinemos_mcp.monitor_models import AddProcessMonitorRequest, ProcessCheckInfoRequest
                    monitor_request = AddProcessMonitorRequest(
                        monitor_id="test", facility_id="test",
                        process_check_info=ProcessCheckInfoRequest(param="test"),
                        numeric_value_info=[]
                    )
                    client.add_process_monitor(monitor_request)
                elif monitor_type == "port":
                    from hinemos_mcp.monitor_models import AddPortMonitorRequest, PortCheckInfoRequest
                    monitor_request = AddPortMonitorRequest(
                        monitor_id="test", facility_id="test",
                        port_check_info=PortCheckInfoRequest(port_no=80),
                        numeric_value_info=[]
                    )
                    client.add_port_monitor(monitor_request)
                elif monitor_type == "winevent":
                    from hinemos_mcp.monitor_models import AddWinEventMonitorRequest, WinEventCheckInfoRequest
                    monitor_request = AddWinEventMonitorRequest(
                        monitor_id="test", facility_id="test",
                        winevent_check_info=WinEventCheckInfoRequest(log_name="System"),
                        string_value_info=[]
                    )
                    client.add_winevent_monitor(monitor_request)
                elif monitor_type == "custom":
                    from hinemos_mcp.monitor_models import AddCustomMonitorRequest, CustomCheckInfoRequest
                    monitor_request = AddCustomMonitorRequest(
                        monitor_id="test", facility_id="test",
                        custom_check_info=CustomCheckInfoRequest(command="test"),
                        numeric_value_info=[]
                    )
                    client.add_custom_monitor(monitor_request)
                
                # Verify URL construction
                assert len(captured_urls) == 1
                method, url = captured_urls[0]
                assert method == "POST"
                expected_url = f"{base_url}/MonitorsettingRestEndpoints{expected_path}"
                assert url == expected_url
                
                print(f"✅ {monitor_type.upper()} monitor: {expected_path}")
                
            except Exception as e:
                print(f"❌ {monitor_type.upper()} monitor failed: {e}")
                return False
    
    return True


def test_request_headers():
    """Test HTTP request headers."""
    print("\n📋 Testing Request Headers")
    print("-" * 40)
    
    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock login response
        mock_client.post.return_value = MockResponse({
            "token": {"tokenId": "test_token_123"}
        })
        
        # Mock monitor request response
        mock_client.request.return_value = MockResponse({"monitorId": "test"})
        
        # Test client
        client = HinemosClient("http://test:8080/HinemosWeb/api", "testuser", "testpass")
        client.login()
        
        # Make a test request
        test_monitor = AddSqlMonitorRequest(
            monitor_id="test",
            facility_id="test",
            sql_check_info=SqlCheckInfoRequest(
                connection_url="test", user="test", password="test",
                jdbc_driver="test", sql="test"
            ),
            numeric_value_info=[]
        )
        
        client.add_sql_monitor(test_monitor)
        
        # Check request headers
        call_args = mock_client.request.call_args
        headers = call_args[1]['headers']
        
        assert 'Content-Type' in headers
        assert headers['Content-Type'] == 'application/json'
        assert 'Authorization' in headers
        assert headers['Authorization'] == 'Bearer test_token_123'
        
        print("✅ Content-Type: application/json")
        print("✅ Authorization: Bearer {token}")
        
        return True


def main():
    """Run all endpoint tests."""
    print("🌐 REST API Endpoint Validation Tests")
    print("=" * 50)
    
    tests = [
        ("SQL Monitor Endpoints", test_sql_monitor_endpoints),
        ("JMX Monitor Endpoints", test_jmx_monitor_endpoints),
        ("Endpoint URL Construction", test_endpoint_url_construction),
        ("Request Headers", test_request_headers)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Endpoint Test Results Summary")
    print("-" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} {test_name}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All endpoint tests passed! REST client is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the client implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)