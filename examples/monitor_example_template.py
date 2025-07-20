#!/usr/bin/env python3
"""Monitor API usage examples.

This is a template file for monitor operations.
Copy this file and update the configuration with your Hinemos server details.
"""

from hinemos_mcp import HinemosClient, MonitorAPI, RepositoryAPI
from hinemos_mcp.monitor_models import RunIntervalEnum, PriorityEnum, ConvertFlagEnum

# Configuration template - update with your Hinemos server details
CONFIG = {
    "base_url": "http://your-hinemos-server:8080/HinemosWeb/api",
    "username": "your-username", 
    "password": "your-password",
    "verify_ssl": False  # Set to True in production with valid SSL certificates
}

def main():
    """Main example function."""
    print("Monitor API Examples")
    print("=" * 50)
    
    with HinemosClient(**CONFIG) as client:
        monitor_api = MonitorAPI(client)
        repo_api = RepositoryAPI(client)
        
        # Get available nodes for monitoring
        nodes = repo_api.list_nodes()
        if not nodes:
            print("No nodes found in repository. Please add nodes first.")
            return
        
        target_facility = nodes[0].facility_id
        print(f"Using target facility: {target_facility}")
        
        # Example 1: List all monitors
        print("\n1. Listing all monitors:")
        monitors = monitor_api.list_monitors()
        print(f"Found {len(monitors)} monitors:")
        for monitor in monitors[:5]:  # Show first 5
            print(f"  - {monitor.monitor_id}: {getattr(monitor, 'monitor_type_id', 'Unknown type')}")
        
        # Example 2: List monitors by type
        print("\n2. Listing monitors by type:")
        ping_monitors = monitor_api.list_ping_monitors()
        http_monitors = monitor_api.list_http_numeric_monitors()
        print(f"  Ping monitors: {len(ping_monitors)}")
        print(f"  HTTP monitors: {len(http_monitors)}")
        
        # Example 3: Create monitors (commented out for safety)
        print("\n3. Creating monitors (examples - commented out):")
        
        print("\n# Ping monitor creation example:")
        print("# ping_monitor = monitor_api.create_ping_monitor(")
        print(f"#     monitor_id='EXAMPLE_PING_{target_facility}',")
        print(f"#     facility_id='{target_facility}',")
        print("#     description='Example ping monitor',")
        print("#     run_interval=RunIntervalEnum.MIN_05,")
        print("#     run_count=3,")
        print("#     timeout=5000")
        print("# )")
        
        print("\n# HTTP numeric monitor creation example:")
        print("# http_monitor = monitor_api.create_http_numeric_monitor(")
        print(f"#     monitor_id='EXAMPLE_HTTP_{target_facility}',")
        print(f"#     facility_id='{target_facility}',")
        print("#     url='http://example.com/health',")
        print("#     description='Example HTTP response time monitor',")
        print("#     timeout=10000")
        print("# )")
        
        print("\n# HTTP string monitor creation example:")
        print("# string_monitor = monitor_api.create_http_string_monitor(")
        print(f"#     monitor_id='EXAMPLE_STRING_{target_facility}',")
        print(f"#     facility_id='{target_facility}',")
        print("#     url='http://example.com/status',")
        print("#     description='Example HTTP string monitor',")
        print("#     patterns=[")
        print("#         {")
        print("#             'pattern': '.*OK.*',")
        print("#             'priority': PriorityEnum.INFO,")
        print("#             'message': 'Service is OK'")
        print("#         },")
        print("#         {")
        print("#             'pattern': '.*ERROR.*',")
        print("#             'priority': PriorityEnum.CRITICAL,")
        print("#             'message': 'Service error detected'")
        print("#         }")
        print("#     ]")
        print("# )")
        
        print("\n# SNMP monitor creation example:")
        print("# snmp_monitor = monitor_api.create_snmp_monitor(")
        print(f"#     monitor_id='EXAMPLE_SNMP_{target_facility}',")
        print(f"#     facility_id='{target_facility}',")
        print("#     oid='1.3.6.1.2.1.1.3.0',  # System uptime")
        print("#     description='Example SNMP monitor',")
        print("#     convert_flg=ConvertFlagEnum.NONE")
        print("# )")
        
        print("\n# Logfile monitor creation example:")
        print("# logfile_monitor = monitor_api.create_logfile_monitor(")
        print(f"#     monitor_id='EXAMPLE_LOG_{target_facility}',")
        print(f"#     facility_id='{target_facility}',")
        print("#     directory='/var/log',")
        print("#     filename='syslog',")
        print("#     description='Example logfile monitor',")
        print("#     patterns=[")
        print("#         {")
        print("#             'pattern': '.*error.*',")
        print("#             'priority': PriorityEnum.CRITICAL,")
        print("#             'message': 'Error found in log',")
        print("#             'case_sensitive': False")
        print("#         }")
        print("#     ]")
        print("# )")
        
        # Example 4: Get specific monitor details
        print("\n4. Getting monitor details:")
        if monitors:
            first_monitor = monitors[0]
            monitor_detail = monitor_api.get_monitor(first_monitor.monitor_id)
            print(f"Monitor details for {monitor_detail.monitor_id}:")
            print(f"  Description: {monitor_detail.description}")
            print(f"  Monitor type: {getattr(monitor_detail, 'monitor_type_id', 'Unknown')}")
            print(f"  Facility: {getattr(monitor_detail, 'facility_id', 'Unknown')}")

if __name__ == "__main__":
    main()