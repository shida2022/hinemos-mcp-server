#!/usr/bin/env python3
"""
Example script demonstrating new monitoring types in Hinemos MCP.

This script shows how to create various types of monitors:
- SQL monitors
- JMX monitors  
- Process monitors
- Port monitors
- Windows Event monitors
- Custom command monitors
"""

import os
import sys
from typing import List

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hinemos_mcp.client import HinemosClient
from hinemos_mcp.monitor import MonitorAPI
from hinemos_mcp.monitor_models import (
    ConvertFlagEnum,
    RunIntervalEnum,
    PriorityEnum
)


def new_monitors_examples():
    """Demonstrate creating new monitoring types."""
    
    # Initialize client - update these values for your Hinemos environment
    base_url = "http://localhost:8080/HinemosWeb/api"
    username = "hinemos"
    password = "hinemos"
    
    with HinemosClient(base_url, username, password) as client:
        monitor_api = MonitorAPI(client)
        
        print("🔍 Hinemos New Monitor Types Example")
        print("=" * 50)
        
        # Test facility - update this to an existing node in your environment
        test_facility_id = "test_node_01"
        
        print("\n📊 Creating SQL Monitor")
        print("-" * 30)
        try:
            sql_monitor = monitor_api.create_sql_monitor(
                monitor_id="SQL_MONITOR_01",
                facility_id=test_facility_id,
                connection_url="jdbc:postgresql://localhost:5432/testdb",
                user="postgres",
                password="password",
                jdbc_driver="org.postgresql.Driver",
                sql="SELECT COUNT(*) FROM users",
                description="Database user count monitor",
                timeout=10000,
                warning_threshold=1000.0,
                critical_threshold=5000.0
            )
            print(f"  ✅ Created SQL monitor: {sql_monitor.monitor_id}")
            print(f"     Connection URL: {sql_monitor.sql_check_info.connection_url}")
            print(f"     SQL Query: {sql_monitor.sql_check_info.sql}")
        except Exception as e:
            print(f"  ❌ Failed to create SQL monitor: {e}")
        
        print("\n☕ Creating JMX Monitor")
        print("-" * 30)
        try:
            jmx_monitor = monitor_api.create_jmx_monitor(
                monitor_id="JMX_MONITOR_01",
                facility_id=test_facility_id,
                port=9999,
                description="JMX memory usage monitor",
                auth_user="jmxuser",
                auth_password="jmxpass",
                url="service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi",
                warning_threshold=80.0,
                critical_threshold=95.0
            )
            print(f"  ✅ Created JMX monitor: {jmx_monitor.monitor_id}")
            print(f"     Port: {jmx_monitor.jmx_check_info.port}")
            print(f"     URL: {jmx_monitor.jmx_check_info.url}")
        except Exception as e:
            print(f"  ❌ Failed to create JMX monitor: {e}")
        
        print("\n⚙️ Creating Process Monitor")
        print("-" * 30)
        try:
            process_monitor = monitor_api.create_process_monitor(
                monitor_id="PROCESS_MONITOR_01",
                facility_id=test_facility_id,
                param="java",
                description="Java process count monitor",
                case_sensitivity_flg=False,
                min_count=1,
                max_count=5
            )
            print(f"  ✅ Created Process monitor: {process_monitor.monitor_id}")
            print(f"     Process param: {process_monitor.process_check_info.param}")
            print(f"     Case sensitive: {process_monitor.process_check_info.case_sensitivity_flg}")
        except Exception as e:
            print(f"  ❌ Failed to create Process monitor: {e}")
        
        print("\n🔌 Creating Port Monitor")
        print("-" * 30)
        try:
            port_monitor = monitor_api.create_port_monitor(
                monitor_id="PORT_MONITOR_01",
                facility_id=test_facility_id,
                port_no=8080,
                description="Web server port monitor",
                service_id="http",
                timeout=3000
            )
            print(f"  ✅ Created Port monitor: {port_monitor.monitor_id}")
            print(f"     Port number: {port_monitor.port_check_info.port_no}")
            print(f"     Service ID: {port_monitor.port_check_info.service_id}")
        except Exception as e:
            print(f"  ❌ Failed to create Port monitor: {e}")
        
        print("\n🪟 Creating Windows Event Monitor")
        print("-" * 30)
        try:
            winevent_monitor = monitor_api.create_winevent_monitor(
                monitor_id="WINEVENT_MONITOR_01",
                facility_id=test_facility_id,
                log_name="System",
                description="Windows System event monitor",
                source="Service Control Manager",
                level=2,  # Error level
                error_patterns=[".*failed.*", ".*error.*"],
                warning_patterns=[".*warning.*", ".*timeout.*"]
            )
            print(f"  ✅ Created Windows Event monitor: {winevent_monitor.monitor_id}")
            print(f"     Log name: {winevent_monitor.winevent_check_info.log_name}")
            print(f"     Source: {winevent_monitor.winevent_check_info.source}")
            print(f"     Level: {winevent_monitor.winevent_check_info.level}")
        except Exception as e:
            print(f"  ❌ Failed to create Windows Event monitor: {e}")
        
        print("\n🛠️ Creating Custom Command Monitor")
        print("-" * 30)
        try:
            custom_monitor = monitor_api.create_custom_monitor(
                monitor_id="CUSTOM_MONITOR_01",
                facility_id=test_facility_id,
                command="df -h / | awk 'NR==2 {print $5}' | sed 's/%//'",
                description="Disk usage percentage monitor",
                timeout=15000,
                warning_threshold=75.0,
                critical_threshold=90.0
            )
            print(f"  ✅ Created Custom monitor: {custom_monitor.monitor_id}")
            print(f"     Command: {custom_monitor.custom_check_info.command}")
            print(f"     Timeout: {custom_monitor.custom_check_info.timeout}ms")
        except Exception as e:
            print(f"  ❌ Failed to create Custom monitor: {e}")
        
        print("\n📋 Listing All Monitor Types")
        print("-" * 30)
        try:
            # List monitors by type
            monitor_counts = {}
            
            sql_monitors = monitor_api.list_sql_monitors()
            monitor_counts["SQL"] = len(sql_monitors)
            
            jmx_monitors = monitor_api.list_jmx_monitors()
            monitor_counts["JMX"] = len(jmx_monitors)
            
            process_monitors = monitor_api.list_process_monitors()
            monitor_counts["Process"] = len(process_monitors)
            
            port_monitors = monitor_api.list_port_monitors()
            monitor_counts["Port"] = len(port_monitors)
            
            winevent_monitors = monitor_api.list_winevent_monitors()
            monitor_counts["Windows Event"] = len(winevent_monitors)
            
            custom_monitors = monitor_api.list_custom_monitors()
            monitor_counts["Custom"] = len(custom_monitors)
            
            # Also show existing types
            ping_monitors = monitor_api.list_ping_monitors()
            monitor_counts["Ping"] = len(ping_monitors)
            
            http_numeric_monitors = monitor_api.list_http_numeric_monitors()
            monitor_counts["HTTP Numeric"] = len(http_numeric_monitors)
            
            http_string_monitors = monitor_api.list_http_string_monitors()
            monitor_counts["HTTP String"] = len(http_string_monitors)
            
            snmp_monitors = monitor_api.list_snmp_monitors()
            monitor_counts["SNMP"] = len(snmp_monitors)
            
            logfile_monitors = monitor_api.list_logfile_monitors()
            monitor_counts["Log File"] = len(logfile_monitors)
            
            print("  📊 Monitor type summary:")
            for monitor_type, count in monitor_counts.items():
                print(f"     {monitor_type}: {count} monitors")
                
        except Exception as e:
            print(f"  ❌ Failed to list monitors: {e}")


def cleanup_example_monitors():
    """Clean up monitors created by this example."""
    
    base_url = "http://localhost:8080/HinemosWeb/api"
    username = "hinemos"
    password = "hinemos"
    
    monitor_ids_to_delete = [
        "SQL_MONITOR_01",
        "JMX_MONITOR_01", 
        "PROCESS_MONITOR_01",
        "PORT_MONITOR_01",
        "WINEVENT_MONITOR_01",
        "CUSTOM_MONITOR_01"
    ]
    
    with HinemosClient(base_url, username, password) as client:
        monitor_api = MonitorAPI(client)
        
        print("\n🧹 Cleaning up example monitors")
        print("-" * 30)
        
        for monitor_id in monitor_ids_to_delete:
            try:
                monitor_api.delete_monitors([monitor_id])
                print(f"  ✅ Deleted monitor: {monitor_id}")
            except Exception as e:
                print(f"  ⚠️ Could not delete {monitor_id}: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hinemos New Monitor Types Example")
    parser.add_argument("--cleanup", action="store_true", 
                       help="Clean up monitors created by this example")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_example_monitors()
    else:
        new_monitors_examples()
        
        print("\n" + "=" * 50)
        print("✅ Example completed!")
        print("💡 To clean up the created monitors, run:")
        print("   python new_monitors_example.py --cleanup")