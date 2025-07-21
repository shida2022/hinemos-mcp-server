#!/usr/bin/env python3
"""
Test script to verify the new monitor models work correctly with REST API.
"""

import json
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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


def test_sql_monitor_serialization():
    """Test SQL monitor model serialization."""
    print("🔍 Testing SQL Monitor Model")
    print("-" * 40)
    
    # Create SQL check info
    sql_check_info = SqlCheckInfoRequest(
        connection_url="jdbc:postgresql://localhost:5432/testdb",
        user="postgres", 
        password="password",
        jdbc_driver="org.postgresql.Driver",
        sql="SELECT COUNT(*) FROM users",
        timeout=5000
    )
    
    # Create numeric value info
    numeric_value_info = [
        MonitorNumericValueInfoRequest(
            monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
            priority=PriorityEnum.INFO,
            threshold_lower_limit=0.0,
            threshold_upper_limit=79.0,
            message="Normal user count"
        ),
        MonitorNumericValueInfoRequest(
            monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
            priority=PriorityEnum.WARNING,
            threshold_lower_limit=80.0,
            threshold_upper_limit=99.0,
            message="High user count"
        )
    ]
    
    # Create SQL monitor request
    sql_monitor = AddSqlMonitorRequest(
        monitor_id="SQL_TEST_01",
        facility_id="test_facility",
        description="Test SQL monitor",
        run_interval=RunIntervalEnum.MIN_05,
        owner_role_id="ADMINISTRATORS",
        sql_check_info=sql_check_info,
        numeric_value_info=numeric_value_info
    )
    
    # Test serialization
    try:
        serialized = sql_monitor.model_dump(by_alias=True, exclude_none=True)
        json_str = json.dumps(serialized, indent=2)
        print("✅ SQL Monitor serialization successful")
        print("JSON structure:")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
        
        # Verify required fields
        assert "monitorId" in serialized
        assert "facilityId" in serialized
        assert "sqlCheckInfo" in serialized
        assert "connectionUrl" in serialized["sqlCheckInfo"]
        assert "numericValueInfo" in serialized
        print("✅ Required fields present")
        
        return True
    except Exception as e:
        print(f"❌ SQL Monitor serialization failed: {e}")
        return False


def test_jmx_monitor_serialization():
    """Test JMX monitor model serialization."""
    print("\n☕ Testing JMX Monitor Model")
    print("-" * 40)
    
    # Create JMX check info
    jmx_check_info = JmxCheckInfoRequest(
        port=9999,
        auth_user="jmxuser",
        auth_password="jmxpass",
        url="service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi",
        convert_flg=ConvertFlagEnum.NONE
    )
    
    # Create numeric value info
    numeric_value_info = [
        MonitorNumericValueInfoRequest(
            monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
            priority=PriorityEnum.CRITICAL,
            threshold_lower_limit=90.0,
            threshold_upper_limit=999999.0,
            message="JMX value too high"
        )
    ]
    
    # Create JMX monitor request
    jmx_monitor = AddJmxMonitorRequest(
        monitor_id="JMX_TEST_01",
        facility_id="test_facility",
        description="Test JMX monitor",
        run_interval=RunIntervalEnum.MIN_05,
        owner_role_id="ADMINISTRATORS",
        jmx_check_info=jmx_check_info,
        numeric_value_info=numeric_value_info
    )
    
    # Test serialization
    try:
        serialized = jmx_monitor.model_dump(by_alias=True, exclude_none=True)
        json_str = json.dumps(serialized, indent=2)
        print("✅ JMX Monitor serialization successful")
        print("JSON structure:")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
        
        # Verify required fields
        assert "monitorId" in serialized
        assert "facilityId" in serialized
        assert "jmxCheckInfo" in serialized
        assert "port" in serialized["jmxCheckInfo"]
        print("✅ Required fields present")
        
        return True
    except Exception as e:
        print(f"❌ JMX Monitor serialization failed: {e}")
        return False


def test_process_monitor_serialization():
    """Test Process monitor model serialization."""
    print("\n⚙️ Testing Process Monitor Model")
    print("-" * 40)
    
    # Create Process check info
    process_check_info = ProcessCheckInfoRequest(
        param="java",
        case_sensitivity_flg=True
    )
    
    # Create numeric value info
    numeric_value_info = [
        MonitorNumericValueInfoRequest(
            monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
            priority=PriorityEnum.INFO,
            threshold_lower_limit=1.0,
            threshold_upper_limit=5.0,
            message="Process count normal"
        )
    ]
    
    # Create Process monitor request
    process_monitor = AddProcessMonitorRequest(
        monitor_id="PROCESS_TEST_01",
        facility_id="test_facility",
        description="Test Process monitor",
        run_interval=RunIntervalEnum.MIN_05,
        owner_role_id="ADMINISTRATORS",
        process_check_info=process_check_info,
        numeric_value_info=numeric_value_info
    )
    
    # Test serialization
    try:
        serialized = process_monitor.model_dump(by_alias=True, exclude_none=True)
        json_str = json.dumps(serialized, indent=2)
        print("✅ Process Monitor serialization successful")
        print("JSON structure:")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
        
        # Verify required fields
        assert "monitorId" in serialized
        assert "facilityId" in serialized
        assert "processCheckInfo" in serialized
        assert "param" in serialized["processCheckInfo"]
        print("✅ Required fields present")
        
        return True
    except Exception as e:
        print(f"❌ Process Monitor serialization failed: {e}")
        return False


def test_port_monitor_serialization():
    """Test Port monitor model serialization."""
    print("\n🔌 Testing Port Monitor Model")
    print("-" * 40)
    
    # Create Port check info
    port_check_info = PortCheckInfoRequest(
        port_no=8080,
        service_id="http",
        timeout=5000
    )
    
    # Create numeric value info
    numeric_value_info = [
        MonitorNumericValueInfoRequest(
            monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
            priority=PriorityEnum.INFO,
            threshold_lower_limit=0.0,
            threshold_upper_limit=0.0,
            message="Port accessible"
        )
    ]
    
    # Create Port monitor request
    port_monitor = AddPortMonitorRequest(
        monitor_id="PORT_TEST_01",
        facility_id="test_facility",
        description="Test Port monitor",
        run_interval=RunIntervalEnum.MIN_05,
        owner_role_id="ADMINISTRATORS",
        port_check_info=port_check_info,
        numeric_value_info=numeric_value_info
    )
    
    # Test serialization
    try:
        serialized = port_monitor.model_dump(by_alias=True, exclude_none=True)
        json_str = json.dumps(serialized, indent=2)
        print("✅ Port Monitor serialization successful")
        print("JSON structure:")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
        
        # Verify required fields
        assert "monitorId" in serialized
        assert "facilityId" in serialized
        assert "portCheckInfo" in serialized
        assert "portNo" in serialized["portCheckInfo"]
        print("✅ Required fields present")
        
        return True
    except Exception as e:
        print(f"❌ Port Monitor serialization failed: {e}")
        return False


def test_winevent_monitor_serialization():
    """Test Windows Event monitor model serialization."""
    print("\n🪟 Testing Windows Event Monitor Model")
    print("-" * 40)
    
    # Create Windows Event check info
    winevent_check_info = WinEventCheckInfoRequest(
        log_name="System",
        source="Service Control Manager",
        level=2,
        keywords="error"
    )
    
    # Create string value info
    string_value_info = [
        MonitorStringValueInfoRequest(
            order_no=1,
            priority=PriorityEnum.CRITICAL,
            pattern=".*error.*",
            message="Error event detected",
            description="Error pattern",
            case_sensitivity_flg=False,
            process_type=True,
            valid_flg=True
        )
    ]
    
    # Create Windows Event monitor request
    winevent_monitor = AddWinEventMonitorRequest(
        monitor_id="WINEVENT_TEST_01",
        facility_id="test_facility",
        description="Test Windows Event monitor",
        run_interval=RunIntervalEnum.MIN_05,
        owner_role_id="ADMINISTRATORS",
        winevent_check_info=winevent_check_info,
        string_value_info=string_value_info
    )
    
    # Test serialization
    try:
        serialized = winevent_monitor.model_dump(by_alias=True, exclude_none=True)
        json_str = json.dumps(serialized, indent=2)
        print("✅ Windows Event Monitor serialization successful")
        print("JSON structure:")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
        
        # Verify required fields
        assert "monitorId" in serialized
        assert "facilityId" in serialized
        assert "wineventCheckInfo" in serialized
        assert "logName" in serialized["wineventCheckInfo"]
        assert "stringValueInfo" in serialized
        print("✅ Required fields present")
        
        return True
    except Exception as e:
        print(f"❌ Windows Event Monitor serialization failed: {e}")
        return False


def test_custom_monitor_serialization():
    """Test Custom monitor model serialization."""
    print("\n🛠️ Testing Custom Monitor Model")
    print("-" * 40)
    
    # Create Custom check info
    custom_check_info = CustomCheckInfoRequest(
        command="df -h / | awk 'NR==2 {print $5}' | sed 's/%//'",
        timeout=30000,
        spec_flg=False,
        convert_flg=ConvertFlagEnum.NONE
    )
    
    # Create numeric value info
    numeric_value_info = [
        MonitorNumericValueInfoRequest(
            monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
            priority=PriorityEnum.WARNING,
            threshold_lower_limit=75.0,
            threshold_upper_limit=89.0,
            message="Disk usage high"
        )
    ]
    
    # Create Custom monitor request
    custom_monitor = AddCustomMonitorRequest(
        monitor_id="CUSTOM_TEST_01",
        facility_id="test_facility",
        description="Test Custom monitor",
        run_interval=RunIntervalEnum.MIN_05,
        owner_role_id="ADMINISTRATORS",
        custom_check_info=custom_check_info,
        numeric_value_info=numeric_value_info
    )
    
    # Test serialization
    try:
        serialized = custom_monitor.model_dump(by_alias=True, exclude_none=True)
        json_str = json.dumps(serialized, indent=2)
        print("✅ Custom Monitor serialization successful")
        print("JSON structure:")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
        
        # Verify required fields
        assert "monitorId" in serialized
        assert "facilityId" in serialized
        assert "customCheckInfo" in serialized
        assert "command" in serialized["customCheckInfo"]
        print("✅ Required fields present")
        
        return True
    except Exception as e:
        print(f"❌ Custom Monitor serialization failed: {e}")
        return False


def test_field_aliases():
    """Test that field aliases are working correctly."""
    print("\n🏷️ Testing Field Aliases")
    print("-" * 40)
    
    # Test SQL check info aliases
    sql_check = SqlCheckInfoRequest(
        connection_url="jdbc:test",
        user="test",
        password="test", 
        jdbc_driver="test.Driver",
        sql="SELECT 1",
        timeout=5000
    )
    
    serialized = sql_check.model_dump(by_alias=True)
    
    # Check aliases are applied
    expected_aliases = {
        "connectionUrl": "connection_url",
        "jdbcDriver": "jdbc_driver"
    }
    
    for alias, field in expected_aliases.items():
        if alias in serialized:
            print(f"✅ Alias '{alias}' correctly mapped from '{field}'")
        else:
            print(f"❌ Alias '{alias}' missing for field '{field}'")
            return False
    
    return True


def test_enum_serialization():
    """Test enum serialization."""
    print("\n🎯 Testing Enum Serialization")
    print("-" * 40)
    
    # Test RunIntervalEnum
    intervals = [RunIntervalEnum.MIN_01, RunIntervalEnum.MIN_05, RunIntervalEnum.MIN_30]
    for interval in intervals:
        print(f"✅ RunIntervalEnum.{interval.name} = '{interval.value}'")
    
    # Test PriorityEnum
    priorities = [PriorityEnum.INFO, PriorityEnum.WARNING, PriorityEnum.CRITICAL]
    for priority in priorities:
        print(f"✅ PriorityEnum.{priority.name} = '{priority.value}'")
    
    # Test ConvertFlagEnum
    convert_flags = [ConvertFlagEnum.NONE, ConvertFlagEnum.DELTA]
    for convert_flag in convert_flags:
        print(f"✅ ConvertFlagEnum.{convert_flag.name} = '{convert_flag.value}'")
    
    return True


def main():
    """Run all tests."""
    print("🧪 REST Client Model Validation Tests")
    print("=" * 50)
    
    tests = [
        ("SQL Monitor", test_sql_monitor_serialization),
        ("JMX Monitor", test_jmx_monitor_serialization), 
        ("Process Monitor", test_process_monitor_serialization),
        ("Port Monitor", test_port_monitor_serialization),
        ("Windows Event Monitor", test_winevent_monitor_serialization),
        ("Custom Monitor", test_custom_monitor_serialization),
        ("Field Aliases", test_field_aliases),
        ("Enum Serialization", test_enum_serialization)
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
    print("📊 Test Results Summary")
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
        print("🎉 All tests passed! REST client models are ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the models.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)