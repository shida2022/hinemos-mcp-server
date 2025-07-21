"""Hinemos MCP Server implementation."""

import json
from typing import Any, Dict, List, Optional, Sequence
from mcp.server import Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    ReadResourceResult
)
import mcp.server.stdio

from ..client import HinemosClient
from ..repository import RepositoryAPI
from ..monitor import MonitorAPI
from ..monitor_models import RunIntervalEnum, PriorityEnum, ConvertFlagEnum


class HinemosMCPServer:
    """Hinemos MCP Server providing repository and monitor management capabilities."""
    
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = True):
        """Initialize Hinemos MCP Server.
        
        Args:
            base_url: Hinemos REST API base URL
            username: Hinemos username
            password: Hinemos password
            verify_ssl: Whether to verify SSL certificates
        """
        self.config = {
            "base_url": base_url,
            "username": username,
            "password": password,
            "verify_ssl": verify_ssl
        }
        self.server = Server("hinemos-mcp")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available Hinemos resources."""
            return [
                Resource(
                    uri="hinemos://repository/nodes",
                    name="Hinemos Repository Nodes",
                    description="List of all nodes in Hinemos repository",
                    mimeType="application/json"
                ),
                Resource(
                    uri="hinemos://repository/scopes",
                    name="Hinemos Repository Scopes",
                    description="List of all scopes in Hinemos repository",
                    mimeType="application/json"
                ),
                Resource(
                    uri="hinemos://monitor/settings",
                    name="Hinemos Monitor Settings",
                    description="List of all monitor configurations",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            """Read a specific Hinemos resource."""
            try:
                with HinemosClient(**self.config) as client:
                    if uri == "hinemos://repository/nodes":
                        repo_api = RepositoryAPI(client)
                        nodes = repo_api.list_nodes()
                        nodes_data = [
                            {
                                "facility_id": node.facility_id,
                                "facility_name": node.facility_name,
                                "description": node.description,
                                "ip_address": getattr(node, "ip_address", None),
                                "platform_family": getattr(node, "platform_family", None),
                                "sub_platform_family": getattr(node, "sub_platform_family", None)
                            }
                            for node in nodes
                        ]
                        return ReadResourceResult(
                            contents=[
                                TextContent(
                                    type="text",
                                    text=json.dumps(nodes_data, indent=2, ensure_ascii=False)
                                )
                            ]
                        )
                    
                    elif uri == "hinemos://repository/scopes":
                        repo_api = RepositoryAPI(client)
                        scopes = repo_api.list_scopes()
                        scopes_data = [
                            {
                                "facility_id": scope.facility_id,
                                "facility_name": scope.facility_name,
                                "description": scope.description,
                                "facility_type": getattr(scope, "facility_type", None)
                            }
                            for scope in scopes
                        ]
                        return ReadResourceResult(
                            contents=[
                                TextContent(
                                    type="text",
                                    text=json.dumps(scopes_data, indent=2, ensure_ascii=False)
                                )
                            ]
                        )
                    
                    elif uri == "hinemos://monitor/settings":
                        monitor_api = MonitorAPI(client)
                        monitors = monitor_api.list_monitors()
                        monitors_data = [
                            {
                                "monitor_id": monitor.monitor_id,
                                "monitor_type": getattr(monitor, "monitor_type", None),
                                "monitor_type_id": getattr(monitor, "monitor_type_id", None),
                                "description": monitor.description,
                                "facility_id": getattr(monitor, "facility_id", None),
                                "monitor_flg": getattr(monitor, "monitor_flg", None),
                                "collector_flg": getattr(monitor, "collector_flg", None)
                            }
                            for monitor in monitors
                        ]
                        return ReadResourceResult(
                            contents=[
                                TextContent(
                                    type="text",
                                    text=json.dumps(monitors_data, indent=2, ensure_ascii=False)
                                )
                            ]
                        )
                    
                    else:
                        raise ValueError(f"Unknown resource URI: {uri}")
                        
            except Exception as e:
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=f"Error reading resource {uri}: {str(e)}"
                        )
                    ]
                )
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available Hinemos tools."""
            return [
                    # Repository management tools
                    Tool(
                        name="hinemos_get_repository_node",
                        description="Get a specific node from Hinemos repository",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "facility_id": {
                                    "type": "string",
                                    "description": "Facility ID of the node to retrieve"
                                }
                            },
                            "required": ["facility_id"]
                        }
                    ),
                    Tool(
                        name="hinemos_create_repository_node",
                        description="Create a new node in Hinemos repository",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "facility_id": {
                                    "type": "string",
                                    "description": "Unique facility ID for the new node"
                                },
                                "facility_name": {
                                    "type": "string",
                                    "description": "Display name for the node"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Description of the node"
                                },
                                "ip_address": {
                                    "type": "string",
                                    "description": "IP address of the node"
                                },
                                "platform_family": {
                                    "type": "string",
                                    "description": "Platform family (e.g., LINUX, WINDOWS)"
                                },
                                "sub_platform_family": {
                                    "type": "string",
                                    "description": "Sub platform family (e.g., RHEL, Ubuntu)"
                                }
                            },
                            "required": ["facility_id", "facility_name", "ip_address"]
                        }
                    ),
                    Tool(
                        name="hinemos_update_repository_node",
                        description="Update an existing node in Hinemos repository",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "facility_id": {
                                    "type": "string",
                                    "description": "Facility ID of the node to update"
                                },
                                "facility_name": {
                                    "type": "string",
                                    "description": "New display name for the node"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "New description of the node"
                                },
                                "ip_address": {
                                    "type": "string",
                                    "description": "New IP address of the node"
                                }
                            },
                            "required": ["facility_id"]
                        }
                    ),
                    # Monitor management tools
                    Tool(
                        name="hinemos_get_monitor",
                        description="Get a specific monitor configuration",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "monitor_id": {
                                    "type": "string",
                                    "description": "Monitor ID to retrieve"
                                }
                            },
                            "required": ["monitor_id"]
                        }
                    ),
                    Tool(
                        name="hinemos_create_monitor",
                        description="Create a new monitor configuration",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "monitor_type": {
                                    "type": "string",
                                    "enum": ["ping", "http_numeric", "http_string", "snmp", "logfile", "sql", "jmx", "process", "port", "winevent", "custom"],
                                    "description": "Type of monitor to create"
                                },
                                "monitor_id": {
                                    "type": "string",
                                    "description": "Unique monitor ID"
                                },
                                "facility_id": {
                                    "type": "string",
                                    "description": "Target facility ID"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Monitor description"
                                },
                                "run_interval": {
                                    "type": "string",
                                    "enum": ["MIN_01", "MIN_05", "MIN_10", "MIN_30", "MIN_60"],
                                    "description": "Monitoring interval",
                                    "default": "MIN_05"
                                },
                                # Ping specific parameters
                                "run_count": {
                                    "type": "integer",
                                    "description": "Number of ping attempts (ping monitors)",
                                    "default": 3
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in milliseconds",
                                    "default": 5000
                                },
                                # HTTP specific parameters
                                "url": {
                                    "type": "string",
                                    "description": "URL to monitor (HTTP monitors)"
                                },
                                "patterns": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "pattern": {"type": "string"},
                                            "priority": {"type": "string", "enum": ["CRITICAL", "WARNING", "INFO", "UNKNOWN"]},
                                            "message": {"type": "string"}
                                        }
                                    },
                                    "description": "String patterns for HTTP string/logfile monitors"
                                },
                                # SNMP specific parameters
                                "oid": {
                                    "type": "string",
                                    "description": "SNMP OID (SNMP monitors)"
                                },
                                "convert_flg": {
                                    "type": "string",
                                    "enum": ["NONE", "DELTA"],
                                    "description": "Convert flag for SNMP monitors",
                                    "default": "NONE"
                                },
                                # Logfile specific parameters
                                "directory": {
                                    "type": "string",
                                    "description": "Log file directory (logfile monitors)"
                                },
                                "filename": {
                                    "type": "string",
                                    "description": "Log file name pattern (logfile monitors)"
                                },
                                "encoding": {
                                    "type": "string",
                                    "description": "File encoding (logfile monitors)",
                                    "default": "UTF-8"
                                },
                                # SQL specific parameters
                                "connection_url": {
                                    "type": "string",
                                    "description": "Database connection URL (sql monitors)"
                                },
                                "user": {
                                    "type": "string",
                                    "description": "Database user (sql monitors)"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "Database password (sql monitors)"
                                },
                                "jdbc_driver": {
                                    "type": "string",
                                    "description": "JDBC driver class name (sql monitors)"
                                },
                                "sql": {
                                    "type": "string",
                                    "description": "SQL query to execute (sql monitors)"
                                },
                                # JMX specific parameters
                                "port": {
                                    "type": "integer",
                                    "description": "JMX port number (jmx monitors)"
                                },
                                "auth_user": {
                                    "type": "string",
                                    "description": "JMX authentication user (jmx monitors)"
                                },
                                "auth_password": {
                                    "type": "string",
                                    "description": "JMX authentication password (jmx monitors)"
                                },
                                # Process specific parameters
                                "param": {
                                    "type": "string",
                                    "description": "Process parameter to monitor (process monitors)"
                                },
                                "case_sensitivity_flg": {
                                    "type": "boolean",
                                    "description": "Case sensitivity flag (process monitors)",
                                    "default": True
                                },
                                "min_count": {
                                    "type": "integer",
                                    "description": "Minimum expected process count (process monitors)",
                                    "default": 1
                                },
                                "max_count": {
                                    "type": "integer",
                                    "description": "Maximum expected process count (process monitors)",
                                    "default": 10
                                },
                                # Port specific parameters
                                "port_no": {
                                    "type": "integer",
                                    "description": "Port number to monitor (port monitors)"
                                },
                                "service_id": {
                                    "type": "string",
                                    "description": "Service ID (port monitors)"
                                },
                                # Windows Event specific parameters
                                "log_name": {
                                    "type": "string",
                                    "description": "Windows Event log name (winevent monitors)"
                                },
                                "source": {
                                    "type": "string",
                                    "description": "Event source filter (winevent monitors)"
                                },
                                "level": {
                                    "type": "integer",
                                    "description": "Event level filter (winevent monitors)"
                                },
                                "keywords": {
                                    "type": "string",
                                    "description": "Event keywords filter (winevent monitors)"
                                },
                                "error_patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of error patterns (winevent monitors)"
                                },
                                "warning_patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of warning patterns (winevent monitors)"
                                },
                                # Custom monitor specific parameters
                                "command": {
                                    "type": "string",
                                    "description": "Command to execute (custom monitors)"
                                },
                                "spec_flg": {
                                    "type": "boolean",
                                    "description": "Specification flag (custom monitors)",
                                    "default": False
                                },
                                # Common numeric threshold parameters
                                "warning_threshold": {
                                    "type": "number",
                                    "description": "Warning threshold value (numeric monitors)",
                                    "default": 80.0
                                },
                                "critical_threshold": {
                                    "type": "number",
                                    "description": "Critical threshold value (numeric monitors)",
                                    "default": 90.0
                                }
                            },
                            "required": ["monitor_type", "monitor_id", "facility_id"]
                        }
                    ),
                    # Scope management tools
                    Tool(
                        name="hinemos_create_scope",
                        description="Create a new scope in Hinemos repository",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "facility_id": {
                                    "type": "string",
                                    "description": "Unique facility ID for the new scope"
                                },
                                "facility_name": {
                                    "type": "string",
                                    "description": "Display name for the scope"
                                },
                                "parent_facility_id": {
                                    "type": "string",
                                    "description": "Parent facility ID (scope will be created under this parent)"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Description of the scope"
                                },
                                "owner_role_id": {
                                    "type": "string",
                                    "description": "Owner role ID",
                                    "default": "ALL_USERS"
                                },
                                "icon_image": {
                                    "type": "string",
                                    "description": "Icon image for the scope"
                                }
                            },
                            "required": ["facility_id", "facility_name"]
                        }
                    ),
                    Tool(
                        name="hinemos_assign_nodes_to_scope",
                        description="Assign nodes to a scope",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "scope_id": {
                                    "type": "string",
                                    "description": "Facility ID of the scope"
                                },
                                "node_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of node facility IDs to assign to the scope"
                                }
                            },
                            "required": ["scope_id", "node_ids"]
                        }
                    ),
                    Tool(
                        name="hinemos_remove_nodes_from_scope",
                        description="Remove nodes from a scope",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "scope_id": {
                                    "type": "string",
                                    "description": "Facility ID of the scope"
                                },
                                "node_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of node facility IDs to remove from the scope"
                                }
                            },
                            "required": ["scope_id", "node_ids"]
                        }
                    )
                ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]):
            """Handle tool calls."""
            try:
                with HinemosClient(**self.config) as client:
                    if name == "hinemos_get_repository_node":
                        repo_api = RepositoryAPI(client)
                        facility_id = arguments["facility_id"]
                        node = repo_api.get_node(facility_id)
                        
                        result = {
                            "facility_id": node.facility_id,
                            "facility_name": node.facility_name,
                            "description": node.description,
                            "ip_address": getattr(node, "ip_address", None),
                            "platform_family": getattr(node, "platform_family", None),
                            "sub_platform_family": getattr(node, "sub_platform_family", None)
                        }
                        
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps(result, indent=2, ensure_ascii=False)
                            )
                        ]
                    
                    elif name == "hinemos_create_repository_node":
                        repo_api = RepositoryAPI(client)
                        
                        node = repo_api.create_node(
                            facility_id=arguments["facility_id"],
                            facility_name=arguments["facility_name"],
                            description=arguments.get("description", ""),
                            ip_address=arguments["ip_address"],
                            platform_family=arguments.get("platform_family"),
                            sub_platform_family=arguments.get("sub_platform_family")
                        )
                        
                        result = {
                            "status": "created",
                            "facility_id": node.facility_id,
                            "facility_name": node.facility_name
                        }
                        
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps(result, indent=2, ensure_ascii=False)
                            )
                        ]
                    
                    elif name == "hinemos_update_repository_node":
                        repo_api = RepositoryAPI(client)
                        
                        update_data = {k: v for k, v in arguments.items() if k != "facility_id" and v is not None}
                        
                        node = repo_api.update_node(
                            facility_id=arguments["facility_id"],
                            **update_data
                        )
                        
                        result = {
                            "status": "updated",
                            "facility_id": node.facility_id,
                            "facility_name": node.facility_name
                        }
                        
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps(result, indent=2, ensure_ascii=False)
                            )
                        ]
                    
                    elif name == "hinemos_get_monitor":
                        monitor_api = MonitorAPI(client)
                        monitor_id = arguments["monitor_id"]
                        monitor = monitor_api.get_monitor(monitor_id)
                        
                        result = {
                            "monitor_id": monitor.monitor_id,
                            "monitor_type": getattr(monitor, "monitor_type", None),
                            "monitor_type_id": getattr(monitor, "monitor_type_id", None),
                            "description": monitor.description,
                            "facility_id": getattr(monitor, "facility_id", None),
                            "monitor_flg": getattr(monitor, "monitor_flg", None),
                            "collector_flg": getattr(monitor, "collector_flg", None),
                            "run_interval": getattr(monitor, "run_interval", None)
                        }
                        
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps(result, indent=2, ensure_ascii=False)
                            )
                        ]
                    
                    elif name == "hinemos_create_monitor":
                        monitor_api = MonitorAPI(client)
                        monitor_type = arguments["monitor_type"]
                        
                        # Common parameters
                        common_params = {
                            "monitor_id": arguments["monitor_id"],
                            "facility_id": arguments["facility_id"],
                            "description": arguments.get("description", ""),
                            "run_interval": RunIntervalEnum(arguments.get("run_interval", "MIN_05")),
                            "prediction_flg": False,  # Disable prediction by default
                            "change_flg": False       # Disable change monitoring by default
                        }
                        
                        if monitor_type == "ping":
                            monitor = monitor_api.create_ping_monitor(
                                run_count=arguments.get("run_count", 3),
                                timeout=arguments.get("timeout", 5000),
                                **common_params
                            )
                        
                        elif monitor_type == "http_numeric":
                            monitor = monitor_api.create_http_numeric_monitor(
                                url=arguments["url"],
                                timeout=arguments.get("timeout", 10000),
                                **common_params
                            )
                        
                        elif monitor_type == "http_string":
                            patterns = arguments.get("patterns", [])
                            if not patterns:
                                patterns = [
                                    {
                                        "pattern": ".*error.*",
                                        "priority": PriorityEnum.CRITICAL,
                                        "message": "Error pattern found"
                                    }
                                ]
                            
                            monitor = monitor_api.create_http_string_monitor(
                                url=arguments["url"],
                                patterns=patterns,
                                timeout=arguments.get("timeout", 10000),
                                **common_params
                            )
                        
                        elif monitor_type == "snmp":
                            monitor = monitor_api.create_snmp_monitor(
                                oid=arguments["oid"],
                                convert_flg=ConvertFlagEnum(arguments.get("convert_flg", "NONE")),
                                **common_params
                            )
                        
                        elif monitor_type == "logfile":
                            patterns = arguments.get("patterns", [])
                            if not patterns:
                                patterns = [
                                    {
                                        "pattern": ".*error.*",
                                        "priority": PriorityEnum.CRITICAL,
                                        "message": "Error pattern found"
                                    }
                                ]
                            
                            monitor = monitor_api.create_logfile_monitor(
                                directory=arguments["directory"],
                                filename=arguments["filename"],
                                patterns=patterns,
                                encoding=arguments.get("encoding", "UTF-8"),
                                **common_params
                            )
                        
                        elif monitor_type == "sql":
                            monitor = monitor_api.create_sql_monitor(
                                connection_url=arguments["connection_url"],
                                user=arguments["user"],
                                password=arguments["password"],
                                jdbc_driver=arguments["jdbc_driver"],
                                sql=arguments["sql"],
                                timeout=arguments.get("timeout", 5000),
                                warning_threshold=arguments.get("warning_threshold", 80.0),
                                critical_threshold=arguments.get("critical_threshold", 90.0),
                                **common_params
                            )
                        
                        elif monitor_type == "jmx":
                            monitor = monitor_api.create_jmx_monitor(
                                port=arguments["port"],
                                auth_user=arguments.get("auth_user"),
                                auth_password=arguments.get("auth_password"),
                                url=arguments.get("url"),
                                convert_flg=ConvertFlagEnum(arguments.get("convert_flg", "NONE")),
                                warning_threshold=arguments.get("warning_threshold", 80.0),
                                critical_threshold=arguments.get("critical_threshold", 90.0),
                                **common_params
                            )
                        
                        elif monitor_type == "process":
                            monitor = monitor_api.create_process_monitor(
                                param=arguments["param"],
                                case_sensitivity_flg=arguments.get("case_sensitivity_flg", True),
                                min_count=arguments.get("min_count", 1),
                                max_count=arguments.get("max_count", 10),
                                **common_params
                            )
                        
                        elif monitor_type == "port":
                            monitor = monitor_api.create_port_monitor(
                                port_no=arguments["port_no"],
                                service_id=arguments.get("service_id"),
                                timeout=arguments.get("timeout", 5000),
                                **common_params
                            )
                        
                        elif monitor_type == "winevent":
                            monitor = monitor_api.create_winevent_monitor(
                                log_name=arguments["log_name"],
                                source=arguments.get("source"),
                                level=arguments.get("level"),
                                keywords=arguments.get("keywords"),
                                error_patterns=arguments.get("error_patterns"),
                                warning_patterns=arguments.get("warning_patterns"),
                                **common_params
                            )
                        
                        elif monitor_type == "custom":
                            monitor = monitor_api.create_custom_monitor(
                                command=arguments["command"],
                                timeout=arguments.get("timeout", 30000),
                                spec_flg=arguments.get("spec_flg", False),
                                convert_flg=ConvertFlagEnum(arguments.get("convert_flg", "NONE")),
                                warning_threshold=arguments.get("warning_threshold", 80.0),
                                critical_threshold=arguments.get("critical_threshold", 90.0),
                                **common_params
                            )
                        
                        else:
                            raise ValueError(f"Unsupported monitor type: {monitor_type}")
                        
                        result = {
                            "status": "created",
                            "monitor_id": monitor.monitor_id,
                            "monitor_type": monitor_type,
                            "description": monitor.description
                        }
                        
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps(result, indent=2, ensure_ascii=False)
                            )
                        ]
                    
                    elif name == "hinemos_create_scope":
                        repo_api = RepositoryAPI(client)
                        
                        scope = repo_api.create_scope(
                            facility_id=arguments["facility_id"],
                            facility_name=arguments["facility_name"],
                            parent_facility_id=arguments.get("parent_facility_id") or "",
                            description=arguments.get("description", ""),
                            owner_role_id=arguments.get("owner_role_id", "ALL_USERS"),
                            icon_image=arguments.get("icon_image")
                        )
                        
                        result = {
                            "status": "created",
                            "facility_id": scope.facility_id,
                            "facility_name": scope.facility_name,
                            "description": scope.description,
                            "parent_facility_id": arguments.get("parent_facility_id")
                        }
                        
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps(result, indent=2, ensure_ascii=False)
                            )
                        ]
                    
                    elif name == "hinemos_assign_nodes_to_scope":
                        repo_api = RepositoryAPI(client)
                        scope_id = arguments["scope_id"]
                        node_ids = arguments["node_ids"]
                        
                        repo_api.assign_nodes_to_scope(scope_id, node_ids)
                        
                        result = {
                            "status": "success",
                            "scope_id": scope_id,
                            "assigned_nodes": node_ids,
                            "message": f"Successfully assigned {len(node_ids)} nodes to scope {scope_id}"
                        }
                        
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps(result, indent=2, ensure_ascii=False)
                            )
                        ]
                    
                    elif name == "hinemos_remove_nodes_from_scope":
                        repo_api = RepositoryAPI(client)
                        scope_id = arguments["scope_id"]
                        node_ids = arguments["node_ids"]
                        
                        repo_api.remove_nodes_from_scope(scope_id, node_ids)
                        
                        result = {
                            "status": "success",
                            "scope_id": scope_id,
                            "removed_nodes": node_ids,
                            "message": f"Successfully removed {len(node_ids)} nodes from scope {scope_id}"
                        }
                        
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps(result, indent=2, ensure_ascii=False)
                            )
                        ]
                    
                    else:
                        raise ValueError(f"Unknown tool: {name}")
            
            except Exception as e:
                return [
                    TextContent(
                        type="text",
                        text=f"Error executing {name}: {str(e)}"
                    )
                ]
    
    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )