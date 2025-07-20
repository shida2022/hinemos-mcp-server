#!/usr/bin/env python3
"""Example usage of Hinemos Monitor API client."""

from src.hinemos_mcp import HinemosClient, MonitorAPI, PriorityEnum, RunIntervalEnum, ConvertFlagEnum

# Configuration
CONFIG = {
    "base_url": "http://your-hinemos:8080/HinemosWeb/api",
    "username": "hinemos",
    "password": "hinemos",
    "verify_ssl": False
}

def monitor_examples():
    """Demonstrate Monitor API usage."""
    
    with HinemosClient(**CONFIG) as client:
        monitor_api = MonitorAPI(client)
        
        print("🔍 Hinemos Monitor API Examples")
        print("=" * 50)
        
        # List existing monitors
        print("\n📋 Listing existing monitors...")
        monitors = monitor_api.list_monitors()
        print(f"Found {len(monitors)} monitors")
        
        for monitor in monitors[:3]:  # Show first 3
            print(f"  - {monitor.monitor_id}: {monitor.description} ({monitor.monitor_type})")
        
        # Example 1: Create Ping Monitor
        print("\n🏓 Creating Ping Monitor...")
        
        try:
            ping_monitor = monitor_api.create_ping_monitor(
                monitor_id="PING_EXAMPLE_001",
                facility_id="SERVER01",  # Replace with actual facility ID
                description="Example Ping Monitor for Web Server",
                run_interval=RunIntervalEnum.MIN_05,
                run_count=3,
                timeout=5000,
                thresholds=[
                    {
                        "priority": PriorityEnum.WARNING,
                        "upper_limit": 1000.0,  # 1 second warning
                        "message": "Response time is high"
                    },
                    {
                        "priority": PriorityEnum.CRITICAL,
                        "upper_limit": 3000.0,  # 3 seconds critical
                        "message": "Response time is critical"
                    }
                ]
            )
            print(f"  ✅ Created ping monitor: {ping_monitor.monitor_id}")
            
        except Exception as e:
            print(f"  ❌ Failed to create ping monitor: {e}")
        
        # Example 2: Create HTTP Numeric Monitor
        print("\n🌐 Creating HTTP Numeric Monitor...")
        
        try:
            http_monitor = monitor_api.create_http_numeric_monitor(
                monitor_id="HTTP_EXAMPLE_001",
                facility_id="SERVER01",  # Replace with actual facility ID
                url="http://localhost:8080/health",
                description="Example HTTP Response Time Monitor",
                run_interval=RunIntervalEnum.MIN_05,
                timeout=10000,
                thresholds=[
                    {
                        "priority": PriorityEnum.WARNING,
                        "upper_limit": 2000.0,  # 2 seconds warning
                        "message": "HTTP response time is high"
                    },
                    {
                        "priority": PriorityEnum.CRITICAL,
                        "upper_limit": 5000.0,  # 5 seconds critical
                        "message": "HTTP response time is critical"
                    }
                ]
            )
            print(f"  ✅ Created HTTP numeric monitor: {http_monitor.monitor_id}")
            
        except Exception as e:
            print(f"  ❌ Failed to create HTTP numeric monitor: {e}")
        
        # Example 3: Create HTTP String Monitor
        print("\n📄 Creating HTTP String Monitor...")
        
        try:
            http_string_monitor = monitor_api.create_http_string_monitor(
                monitor_id="HTTP_STRING_001",
                facility_id="SERVER01",  # Replace with actual facility ID
                url="http://localhost:8080/status",
                description="Example HTTP String Pattern Monitor",
                run_interval=RunIntervalEnum.MIN_05,
                timeout=10000,
                patterns=[
                    {
                        "pattern": ".*OK.*",
                        "priority": PriorityEnum.INFO,
                        "message": "Service is OK",
                        "case_sensitive": False
                    },
                    {
                        "pattern": ".*ERROR.*",
                        "priority": PriorityEnum.CRITICAL,
                        "message": "Service error detected",
                        "case_sensitive": False
                    }
                ]
            )
            print(f"  ✅ Created HTTP string monitor: {http_string_monitor.monitor_id}")
            
        except Exception as e:
            print(f"  ❌ Failed to create HTTP string monitor: {e}")
        
        # Example 4: Create SNMP Monitor
        print("\n📊 Creating SNMP Monitor...")
        
        try:
            snmp_monitor = monitor_api.create_snmp_monitor(
                monitor_id="SNMP_EXAMPLE_001",
                facility_id="SERVER01",  # Replace with actual facility ID
                oid="1.3.6.1.2.1.1.3.0",  # System uptime
                description="Example SNMP System Uptime Monitor",
                run_interval=RunIntervalEnum.MIN_10,
                convert_flg=ConvertFlagEnum.NONE,
                thresholds=[
                    {
                        "priority": PriorityEnum.WARNING,
                        "lower_limit": 86400.0,  # Less than 1 day uptime
                        "message": "System uptime is low"
                    }
                ]
            )
            print(f"  ✅ Created SNMP monitor: {snmp_monitor.monitor_id}")
            
        except Exception as e:
            print(f"  ❌ Failed to create SNMP monitor: {e}")
        
        # Example 5: Create Log File Monitor
        print("\n📝 Creating Log File Monitor...")
        
        try:
            logfile_monitor = monitor_api.create_logfile_monitor(
                monitor_id="LOG_EXAMPLE_001",
                facility_id="SERVER01",  # Replace with actual facility ID
                directory="/var/log",
                filename="application.log",
                description="Example Application Log Monitor",
                run_interval=RunIntervalEnum.MIN_01,
                encoding="UTF-8",
                patterns=[
                    {
                        "pattern": ".*ERROR.*",
                        "priority": PriorityEnum.CRITICAL,
                        "message": "Error found in application log",
                        "case_sensitive": False
                    },
                    {
                        "pattern": ".*WARN.*",
                        "priority": PriorityEnum.WARNING,
                        "message": "Warning found in application log",
                        "case_sensitive": False
                    }
                ]
            )
            print(f"  ✅ Created log file monitor: {logfile_monitor.monitor_id}")
            
        except Exception as e:
            print(f"  ❌ Failed to create log file monitor: {e}")
        
        # Example 6: List monitors by type
        print("\n📋 Listing monitors by type...")
        
        try:
            ping_monitors = monitor_api.list_ping_monitors()
            print(f"  📊 Ping monitors: {len(ping_monitors)}")
            
            http_numeric_monitors = monitor_api.list_http_numeric_monitors()
            print(f"  🌐 HTTP numeric monitors: {len(http_numeric_monitors)}")
            
            http_string_monitors = monitor_api.list_http_string_monitors()
            print(f"  📄 HTTP string monitors: {len(http_string_monitors)}")
            
            snmp_monitors = monitor_api.list_snmp_monitors()
            print(f"  📊 SNMP monitors: {len(snmp_monitors)}")
            
            logfile_monitors = monitor_api.list_logfile_monitors()
            print(f"  📝 Log file monitors: {len(logfile_monitors)}")
            
        except Exception as e:
            print(f"  ❌ Failed to list monitors: {e}")
        
        # Example 7: Manage monitor status
        print("\n⚙️ Managing monitor status...")
        
        example_monitor_ids = [
            "PING_EXAMPLE_001",
            "HTTP_EXAMPLE_001",
            "HTTP_STRING_001",
            "SNMP_EXAMPLE_001",
            "LOG_EXAMPLE_001"
        ]
        
        try:
            # Disable example monitors
            monitor_api.disable_monitors(example_monitor_ids)
            print("  ⏸️ Disabled example monitors")
            
            # Enable example monitors
            monitor_api.enable_monitors(example_monitor_ids)
            print("  ▶️ Enabled example monitors")
            
            # Disable collection for example monitors
            monitor_api.disable_collectors(example_monitor_ids)
            print("  📊 Disabled collection for example monitors")
            
            # Enable collection for example monitors
            monitor_api.enable_collectors(example_monitor_ids)
            print("  📈 Enabled collection for example monitors")
            
        except Exception as e:
            print(f"  ❌ Failed to manage monitor status: {e}")
        
        print("\n✅ Monitor API examples completed!")
        print("\n⚠️  Note: Example monitors created above should be cleaned up manually")
        print("   Use monitor_api.delete_monitors(monitor_ids) to remove them")


def cleanup_example_monitors():
    """Clean up example monitors created by the demo."""
    
    with HinemosClient(**CONFIG) as client:
        monitor_api = MonitorAPI(client)
        
        example_monitor_ids = [
            "PING_EXAMPLE_001",
            "HTTP_EXAMPLE_001", 
            "HTTP_STRING_001",
            "SNMP_EXAMPLE_001",
            "LOG_EXAMPLE_001"
        ]
        
        print("🧹 Cleaning up example monitors...")
        
        try:
            monitor_api.delete_monitors(example_monitor_ids)
            print("  ✅ Deleted example monitors")
        except Exception as e:
            print(f"  ❌ Failed to delete monitors: {e}")


if __name__ == "__main__":
    # Run examples
    monitor_examples()
    
    # Uncomment to clean up
    # cleanup_example_monitors()