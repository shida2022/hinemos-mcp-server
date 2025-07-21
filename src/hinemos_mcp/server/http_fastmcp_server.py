"""Hinemos MCP Server implementation using FastMCP with HTTP Transport."""

import json
import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from ..client import HinemosClient
from ..repository import RepositoryAPI
from ..monitor import MonitorAPI
from ..monitor_models import RunIntervalEnum, PriorityEnum, ConvertFlagEnum


class HinemosHTTPFastMCPServer:
    """Hinemos MCP Server using FastMCP framework with HTTP transport."""
    
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = True):
        """Initialize Hinemos HTTP FastMCP Server.
        
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
        self.app = FastAPI(
            title="Hinemos MCP Server",
            description="HTTP-based MCP server for Hinemos integration",
            version="1.0.0"
        )
        self.mcp = FastMCP("hinemos-mcp-http")
        self._setup_tools()
        self._setup_resources()
        self._setup_routes()
    
    def _setup_tools(self):
        """Setup MCP tools using FastMCP decorators."""
        
        @self.mcp.tool()
        def hinemos_get_facility_tree(root_facility_id: str = None, owner_role_id: str = "ALL_USERS") -> str:
            """Get complete facility tree showing hierarchy and relationships.
            
            This provides the complete structure of the Hinemos repository including:
            - Which nodes belong to which scopes
            - The hierarchical organization of facilities
            - Parent-child relationships between facilities
                
            Args:
                root_facility_id: Root facility ID to start from (None for complete tree)
                owner_role_id: Owner role ID for access control (default: ALL_USERS)
                
            Returns:
                JSON string containing the complete facility tree structure
            """
            try:
                with HinemosClient(**self.config) as client:
                    repo_api = RepositoryAPI(client)
                    tree_data = repo_api.get_facility_tree(root_facility_id, owner_role_id)
                    return json.dumps(tree_data, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error: {str(e)}"

        @self.mcp.tool()
        def hinemos_get_repository_node(facility_id: str) -> str:
            """Get a specific node from Hinemos repository.
            
            Args:
                facility_id: Facility ID of the node to retrieve
                
            Returns:
                JSON string containing node information
            """
            try:
                with HinemosClient(**self.config) as client:
                    repo_api = RepositoryAPI(client)
                    node = repo_api.get_node(facility_id)
                    
                    result = {
                        "facility_id": node.facility_id,
                        "facility_name": node.facility_name,
                        "description": node.description,
                        "ip_address": getattr(node, "ip_address", None),
                        "platform_family": getattr(node, "platform_family", None),
                        "sub_platform_family": getattr(node, "sub_platform_family", None)
                    }
                    
                    return json.dumps(result, indent=2, ensure_ascii=False)
            except Exception as e:
                # If node not found, provide helpful suggestions
                if "404" in str(e) or "not found" in str(e).lower():
                    try:
                        with HinemosClient(**self.config) as client:
                            repo_api = RepositoryAPI(client)
                            nodes = repo_api.list_nodes()
                            available_ids = [node.facility_id for node in nodes[:5]]
                            return f"Error: Node '{facility_id}' not found. Available node IDs include: {', '.join(available_ids)}. Use hinemos_get_facility_tree to see all available nodes and their hierarchy."
                    except:
                        pass
                return f"Error: {str(e)}"
        
        @self.mcp.tool()
        def hinemos_create_repository_node(
            facility_id: str,
            facility_name: str,
            ip_address: str,
            description: str = "",
            platform_family: Optional[str] = None,
            sub_platform_family: Optional[str] = None
        ) -> str:
            """Create a new node in Hinemos repository.
            
            Args:
                facility_id: Unique facility ID for the new node
                facility_name: Display name for the node
                ip_address: IP address of the node
                description: Description of the node
                platform_family: Platform family (e.g., LINUX, WINDOWS)
                sub_platform_family: Sub platform family (e.g., RHEL, Ubuntu)
                
            Returns:
                JSON string containing creation result
            """
            try:
                with HinemosClient(**self.config) as client:
                    repo_api = RepositoryAPI(client)
                    
                    node = repo_api.create_node(
                        facility_id=facility_id,
                        facility_name=facility_name,
                        description=description,
                        ip_address=ip_address,
                        platform_family=platform_family,
                        sub_platform_family=sub_platform_family
                    )
                    
                    result = {
                        "status": "created",
                        "facility_id": node.facility_id,
                        "facility_name": node.facility_name
                    }
                    
                    return json.dumps(result, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error: {str(e)}"
        
        @self.mcp.tool()
        def hinemos_update_repository_node(
            facility_id: str,
            facility_name: Optional[str] = None,
            description: Optional[str] = None,
            ip_address: Optional[str] = None
        ) -> str:
            """Update an existing node in Hinemos repository.
            
            Args:
                facility_id: Facility ID of the node to update
                facility_name: New display name for the node
                description: New description of the node
                ip_address: New IP address of the node
                
            Returns:
                JSON string containing update result
            """
            try:
                with HinemosClient(**self.config) as client:
                    repo_api = RepositoryAPI(client)
                    
                    update_data = {}
                    if facility_name is not None:
                        update_data["facility_name"] = facility_name
                    if description is not None:
                        update_data["description"] = description
                    if ip_address is not None:
                        update_data["ip_address"] = ip_address
                    
                    node = repo_api.update_node(facility_id=facility_id, **update_data)
                    
                    result = {
                        "status": "updated",
                        "facility_id": node.facility_id,
                        "facility_name": node.facility_name
                    }
                    
                    return json.dumps(result, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error: {str(e)}"
        
        @self.mcp.tool()
        def hinemos_get_monitor(monitor_id: str) -> str:
            """Get a specific monitor configuration.
            
            Args:
                monitor_id: Monitor ID to retrieve
                
            Returns:
                JSON string containing monitor information
            """
            try:
                with HinemosClient(**self.config) as client:
                    monitor_api = MonitorAPI(client)
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
                    
                    return json.dumps(result, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error: {str(e)}"
        
        @self.mcp.tool()
        def hinemos_create_monitor(
            monitor_type: str,
            monitor_id: str,
            facility_id: str,
            description: str = "",
            run_interval: str = "MIN_05",
            # Ping specific parameters
            run_count: Optional[int] = None,
            timeout: Optional[int] = None,
            # HTTP specific parameters
            url: Optional[str] = None,
            patterns: Optional[List[Dict[str, str]]] = None,
            # SNMP specific parameters
            oid: Optional[str] = None,
            convert_flg: Optional[str] = None,
            # Logfile specific parameters
            directory: Optional[str] = None,
            filename: Optional[str] = None,
            encoding: Optional[str] = None,
            # SQL specific parameters
            connection_url: Optional[str] = None,
            user: Optional[str] = None,
            password: Optional[str] = None,
            jdbc_driver: Optional[str] = None,
            sql: Optional[str] = None,
            # JMX specific parameters
            port: Optional[int] = None,
            auth_user: Optional[str] = None,
            auth_password: Optional[str] = None,
            # Process specific parameters
            param: Optional[str] = None,
            case_sensitivity_flg: Optional[bool] = None,
            min_count: Optional[int] = None,
            max_count: Optional[int] = None,
            # Port specific parameters
            port_no: Optional[int] = None,
            service_id: Optional[str] = None,
            # Windows Event specific parameters
            log_name: Optional[str] = None,
            source: Optional[str] = None,
            level: Optional[int] = None,
            keywords: Optional[str] = None,
            error_patterns: Optional[List[str]] = None,
            warning_patterns: Optional[List[str]] = None,
            # Custom monitor specific parameters
            command: Optional[str] = None,
            spec_flg: Optional[bool] = None,
            # Common threshold parameters
            warning_threshold: Optional[float] = None,
            critical_threshold: Optional[float] = None
        ) -> str:
            """Create a new monitor configuration.
            
            Examples:
                Port monitoring (TCP port 8080):
                {
                  "monitor_type": "port",
                  "monitor_id": "PORT_8080_AP1", 
                  "facility_id": "AP1",
                  "description": "AP1ノードのポート8080監視",
                  "port_no": 8080,
                  "service_id": "TCP",
                  "timeout": 5000,
                  "run_interval": "MIN_05"
                }
                
                HTTP monitoring:
                {
                  "monitor_type": "http_numeric",
                  "monitor_id": "HTTP_HEALTH_CHECK",
                  "facility_id": "WEB_SERVER",
                  "url": "http://example.com/health",
                  "timeout": 10000
                }
            
            Args:
                monitor_type: Type of monitor (ping, http_numeric, http_string, snmp, logfile, sql, jmx, process, port, winevent, custom)
                monitor_id: Unique monitor ID
                facility_id: Target facility ID
                description: Monitor description
                run_interval: Monitoring interval (MIN_01, MIN_05, MIN_10, MIN_30, MIN_60)
                
                # Ping monitor parameters:
                run_count: Number of ping attempts (default: 3)
                timeout: Timeout in milliseconds (default: 5000)
                
                # HTTP monitor parameters:
                url: URL to monitor
                timeout: Timeout in milliseconds (default: 10000)
                patterns: String patterns for HTTP string monitoring
                
                # SNMP monitor parameters:
                oid: SNMP OID
                convert_flg: Convert flag (NONE, DELTA)
                
                # Logfile monitor parameters:
                directory: Log file directory
                filename: Log file name pattern
                encoding: File encoding (default: UTF-8)
                patterns: String patterns to match
                
                # SQL monitor parameters:
                connection_url: Database connection URL
                user: Database user
                password: Database password
                jdbc_driver: JDBC driver class name
                sql: SQL query to execute
                timeout: Query timeout (default: 5000)
                warning_threshold: Warning threshold value
                critical_threshold: Critical threshold value
                
                # JMX monitor parameters:
                port: JMX port number
                auth_user: JMX authentication user
                auth_password: JMX authentication password
                url: JMX URL pattern
                convert_flg: Convert flag (NONE, DELTA)
                warning_threshold: Warning threshold value
                critical_threshold: Critical threshold value
                
                # Process monitor parameters:
                param: Process parameter to monitor
                case_sensitivity_flg: Case sensitivity flag (default: True)
                min_count: Minimum expected process count (default: 1)
                max_count: Maximum expected process count (default: 10)
                
                # Port monitor parameters:
                port_no: Port number to monitor (required)
                service_id: Service protocol type (optional)
                  Valid values: TCP, FTP, SMTP, DNS, NTP, POP3, IMAP, SMTPS, POP3S, IMAPS
                  Default: TCP if not specified
                timeout: Connection timeout in milliseconds (default: 5000)
                  Example: 5000 for 5 seconds timeout
                
                # Windows Event monitor parameters:
                log_name: Windows Event log name
                source: Event source filter
                level: Event level filter
                keywords: Event keywords filter
                error_patterns: List of error patterns
                warning_patterns: List of warning patterns
                
                # Custom monitor parameters:
                command: Command to execute
                timeout: Command timeout (default: 30000)
                spec_flg: Specification flag (default: False)
                convert_flg: Convert flag (NONE, DELTA)
                warning_threshold: Warning threshold value
                critical_threshold: Critical threshold value
                
            Returns:
                JSON string containing creation result
            """
            try:
                # Validate monitor type
                valid_types = ["ping", "http_numeric", "http_string", "snmp", "logfile", "sql", "jmx", "process", "port", "winevent", "custom"]
                if monitor_type not in valid_types:
                    return f"Error: Invalid monitor_type '{monitor_type}'. Valid types: {', '.join(valid_types)}"
                
                with HinemosClient(**self.config) as client:
                    monitor_api = MonitorAPI(client)
                    
                    # Common parameters
                    common_params = {
                        "monitor_id": monitor_id,
                        "facility_id": facility_id,
                        "description": description,
                        "run_interval": RunIntervalEnum(run_interval),
                        "prediction_flg": False,  # Disable prediction by default
                        "change_flg": False       # Disable change monitoring by default
                    }
                    
                    if monitor_type == "ping":
                        monitor = monitor_api.create_ping_monitor(
                            run_count=run_count or 3,
                            timeout=timeout or 5000,
                            **common_params
                        )
                    
                    elif monitor_type == "http_numeric":
                        if not url:
                            return "Error: 'url' parameter is required for HTTP numeric monitors"
                        monitor = monitor_api.create_http_numeric_monitor(
                            url=url,
                            timeout=timeout or 10000,
                            **common_params
                        )
                    
                    elif monitor_type == "http_string":
                        if not url:
                            return "Error: 'url' parameter is required for HTTP string monitors"
                        if not patterns:
                            patterns = [
                                {
                                    "pattern": ".*error.*",
                                    "priority": "CRITICAL",
                                    "message": "Error pattern found"
                                }
                            ]
                        monitor = monitor_api.create_http_string_monitor(
                            url=url,
                            patterns=patterns,
                            timeout=timeout or 10000,
                            **common_params
                        )
                    
                    elif monitor_type == "snmp":
                        if not oid:
                            return "Error: 'oid' parameter is required for SNMP monitors"
                        monitor = monitor_api.create_snmp_monitor(
                            oid=oid,
                            convert_flg=ConvertFlagEnum(convert_flg or "NONE"),
                            **common_params
                        )
                    
                    elif monitor_type == "logfile":
                        if not directory or not filename:
                            return "Error: 'directory' and 'filename' parameters are required for logfile monitors"
                        if not patterns:
                            patterns = [
                                {
                                    "pattern": ".*error.*",
                                    "priority": "CRITICAL",
                                    "message": "Error pattern found"
                                }
                            ]
                        monitor = monitor_api.create_logfile_monitor(
                            directory=directory,
                            filename=filename,
                            patterns=patterns,
                            encoding=encoding or "UTF-8",
                            **common_params
                        )
                    
                    elif monitor_type == "sql":
                        required_sql_params = [connection_url, user, password, jdbc_driver, sql]
                        if not all(required_sql_params):
                            return "Error: 'connection_url', 'user', 'password', 'jdbc_driver', and 'sql' parameters are required for SQL monitors"
                        monitor = monitor_api.create_sql_monitor(
                            connection_url=connection_url,
                            user=user,
                            password=password,
                            jdbc_driver=jdbc_driver,
                            sql=sql,
                            timeout=timeout or 5000,
                            warning_threshold=warning_threshold or 80.0,
                            critical_threshold=critical_threshold or 90.0,
                            **common_params
                        )
                    
                    elif monitor_type == "jmx":
                        if not port:
                            return "Error: 'port' parameter is required for JMX monitors"
                        monitor = monitor_api.create_jmx_monitor(
                            port=port,
                            auth_user=auth_user,
                            auth_password=auth_password,
                            url=url,
                            convert_flg=ConvertFlagEnum(convert_flg or "NONE"),
                            warning_threshold=warning_threshold or 80.0,
                            critical_threshold=critical_threshold or 90.0,
                            **common_params
                        )
                    
                    elif monitor_type == "process":
                        if not param:
                            return "Error: 'param' parameter is required for process monitors"
                        monitor = monitor_api.create_process_monitor(
                            param=param,
                            case_sensitivity_flg=case_sensitivity_flg if case_sensitivity_flg is not None else True,
                            min_count=min_count or 1,
                            max_count=max_count or 10,
                            **common_params
                        )
                    
                    elif monitor_type == "port":
                        if not port_no:
                            return "Error: 'port_no' parameter is required for port monitors"
                        monitor = monitor_api.create_port_monitor(
                            port_no=port_no,
                            service_id=service_id,
                            timeout=timeout or 5000,
                            **common_params
                        )
                    
                    elif monitor_type == "winevent":
                        if not log_name:
                            return "Error: 'log_name' parameter is required for Windows Event monitors"
                        monitor = monitor_api.create_winevent_monitor(
                            log_name=log_name,
                            source=source,
                            level=level,
                            keywords=keywords,
                            error_patterns=error_patterns,
                            warning_patterns=warning_patterns,
                            **common_params
                        )
                    
                    elif monitor_type == "custom":
                        if not command:
                            return "Error: 'command' parameter is required for custom monitors"
                        monitor = monitor_api.create_custom_monitor(
                            command=command,
                            timeout=timeout or 30000,
                            spec_flg=spec_flg if spec_flg is not None else False,
                            convert_flg=ConvertFlagEnum(convert_flg or "NONE"),
                            warning_threshold=warning_threshold or 80.0,
                            critical_threshold=critical_threshold or 90.0,
                            **common_params
                        )
                    
                    result = {
                        "status": "created",
                        "monitor_id": monitor.monitor_id,
                        "monitor_type": monitor_type,
                        "description": monitor.description
                    }
                    
                    return json.dumps(result, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error: {str(e)}"
        
        # Scope management tools
        @self.mcp.tool()
        def hinemos_create_scope(
            facility_id: str,
            facility_name: str,
            parent_facility_id: Optional[str] = None,
            description: str = "",
            owner_role_id: str = "ALL_USERS",
            icon_image: Optional[str] = None
        ) -> str:
            """Create a new scope in Hinemos repository.
            
            Args:
                facility_id: Unique facility ID for the new scope
                facility_name: Display name for the scope
                parent_facility_id: Parent facility ID (scope will be created under this parent)
                description: Description of the scope
                owner_role_id: Owner role ID (default: ADMINISTRATORS)
                icon_image: Icon image for the scope
                
            Returns:
                JSON string containing creation result
            """
            try:
                with HinemosClient(**self.config) as client:
                    repo_api = RepositoryAPI(client)
                    
                    scope = repo_api.create_scope(
                        facility_id=facility_id,
                        facility_name=facility_name,
                        parent_facility_id=parent_facility_id or "",
                        description=description,
                        owner_role_id=owner_role_id,
                        icon_image=icon_image
                    )
                    
                    result = {
                        "status": "created",
                        "facility_id": scope.facility_id,
                        "facility_name": scope.facility_name,
                        "description": scope.description,
                        "parent_facility_id": parent_facility_id
                    }
                    
                    return json.dumps(result, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error: {str(e)}"
        
        @self.mcp.tool()
        def hinemos_assign_nodes_to_scope(
            scope_id: str,
            node_ids: List[str]
        ) -> str:
            """Assign nodes to a scope.
            
            Args:
                scope_id: Facility ID of the scope
                node_ids: List of node facility IDs to assign to the scope
                
            Returns:
                JSON string containing assignment result
            """
            try:
                with HinemosClient(**self.config) as client:
                    repo_api = RepositoryAPI(client)
                    
                    repo_api.assign_nodes_to_scope(scope_id, node_ids)
                    
                    result = {
                        "status": "success",
                        "scope_id": scope_id,
                        "assigned_nodes": node_ids,
                        "message": f"Successfully assigned {len(node_ids)} nodes to scope {scope_id}"
                    }
                    
                    return json.dumps(result, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error: {str(e)}"
        
        @self.mcp.tool()
        def hinemos_remove_nodes_from_scope(
            scope_id: str,
            node_ids: List[str]
        ) -> str:
            """Remove nodes from a scope.
            
            Args:
                scope_id: Facility ID of the scope
                node_ids: List of node facility IDs to remove from the scope
                
            Returns:
                JSON string containing removal result
            """
            try:
                with HinemosClient(**self.config) as client:
                    repo_api = RepositoryAPI(client)
                    
                    repo_api.remove_nodes_from_scope(scope_id, node_ids)
                    
                    result = {
                        "status": "success",
                        "scope_id": scope_id,
                        "removed_nodes": node_ids,
                        "message": f"Successfully removed {len(node_ids)} nodes from scope {scope_id}"
                    }
                    
                    return json.dumps(result, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error: {str(e)}"
    
    def _setup_resources(self):
        """Setup MCP resources using FastMCP decorators."""
        
        @self.mcp.resource("hinemos://repository/facility_tree")
        def get_complete_facility_tree() -> str:
            """Complete facility tree showing all nodes, scopes, and their relationships."""
            try:
                with HinemosClient(**self.config) as client:
                    repo_api = RepositoryAPI(client)
                    tree_data = repo_api.get_facility_tree()
                    return json.dumps(tree_data, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error reading facility tree: {str(e)}"

        @self.mcp.resource("hinemos://monitor/settings")
        def get_monitor_settings() -> str:
            """List of all monitor configurations."""
            try:
                with HinemosClient(**self.config) as client:
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
                    return json.dumps(monitors_data, indent=2, ensure_ascii=False)
            except Exception as e:
                return f"Error reading monitor settings: {str(e)}"
    
    def _call_get_facility_tree(self, parameters: Dict[str, Any]) -> str:
        """Call hinemos_get_facility_tree tool."""
        try:
            with HinemosClient(**self.config) as client:
                repo_api = RepositoryAPI(client)
                tree_data = repo_api.get_facility_tree(
                    parameters.get("root_facility_id"),
                    parameters.get("owner_role_id", "ALL_USERS")
                )
                return json.dumps(tree_data, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_get_repository_node(self, parameters: Dict[str, Any]) -> str:
        """Call hinemos_get_repository_node tool."""
        try:
            facility_id = parameters["facility_id"]
            with HinemosClient(**self.config) as client:
                repo_api = RepositoryAPI(client)
                node = repo_api.get_node(facility_id)
                
                result = {
                    "facility_id": node.facility_id,
                    "facility_name": node.facility_name,
                    "description": node.description,
                    "ip_address": getattr(node, "ip_address", None),
                    "platform_family": getattr(node, "platform_family", None),
                    "sub_platform_family": getattr(node, "sub_platform_family", None)
                }
                
                return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_create_repository_node(self, parameters: Dict[str, Any]) -> str:
        """Call hinemos_create_repository_node tool."""
        try:
            with HinemosClient(**self.config) as client:
                repo_api = RepositoryAPI(client)
                
                node = repo_api.create_node(
                    facility_id=parameters["facility_id"],
                    facility_name=parameters["facility_name"],
                    description=parameters.get("description", ""),
                    ip_address=parameters["ip_address"],
                    platform_family=parameters.get("platform_family"),
                    sub_platform_family=parameters.get("sub_platform_family")
                )
                
                result = {
                    "status": "created",
                    "facility_id": node.facility_id,
                    "facility_name": node.facility_name
                }
                
                return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_update_repository_node(self, parameters: Dict[str, Any]) -> str:
        """Call hinemos_update_repository_node tool."""
        try:
            with HinemosClient(**self.config) as client:
                repo_api = RepositoryAPI(client)
                
                update_data = {}
                if "facility_name" in parameters:
                    update_data["facility_name"] = parameters["facility_name"]
                if "description" in parameters:
                    update_data["description"] = parameters["description"]
                if "ip_address" in parameters:
                    update_data["ip_address"] = parameters["ip_address"]
                
                node = repo_api.update_node(facility_id=parameters["facility_id"], **update_data)
                
                result = {
                    "status": "updated",
                    "facility_id": node.facility_id,
                    "facility_name": node.facility_name
                }
                
                return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_get_monitor(self, parameters: Dict[str, Any]) -> str:
        """Call hinemos_get_monitor tool."""
        try:
            with HinemosClient(**self.config) as client:
                monitor_api = MonitorAPI(client)
                monitor = monitor_api.get_monitor(parameters["monitor_id"])
                
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
                
                return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_create_monitor(self, parameters: Dict[str, Any]) -> str:
        """Call hinemos_create_monitor tool."""
        try:
            monitor_type = parameters["monitor_type"]
            
            # Validate monitor type
            valid_types = ["ping", "http_numeric", "http_string", "snmp", "logfile", "sql", "jmx", "process", "port", "winevent", "custom"]
            if monitor_type not in valid_types:
                return f"Error: Invalid monitor_type '{monitor_type}'. Valid types: {', '.join(valid_types)}"
            
            with HinemosClient(**self.config) as client:
                monitor_api = MonitorAPI(client)
                
                # Common parameters
                common_params = {
                    "monitor_id": parameters["monitor_id"],
                    "facility_id": parameters["facility_id"],
                    "description": parameters.get("description", ""),
                    "run_interval": RunIntervalEnum(parameters.get("run_interval", "MIN_05")),
                    "prediction_flg": False,
                    "change_flg": False
                }
                
                if monitor_type == "ping":
                    monitor = monitor_api.create_ping_monitor(
                        run_count=parameters.get("run_count", 3),
                        timeout=parameters.get("timeout", 5000),
                        **common_params
                    )
                elif monitor_type == "port":
                    if "port_no" not in parameters:
                        return "Error: 'port_no' parameter is required for port monitors"
                    monitor = monitor_api.create_port_monitor(
                        port_no=parameters["port_no"],
                        service_id=parameters.get("service_id"),
                        timeout=parameters.get("timeout", 5000),
                        **common_params
                    )
                else:
                    return f"Error: Monitor type '{monitor_type}' not yet implemented in HTTP transport"
                
                result = {
                    "status": "created",
                    "monitor_id": monitor.monitor_id,
                    "monitor_type": monitor_type,
                    "description": monitor.description
                }
                
                return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_create_scope(self, parameters: Dict[str, Any]) -> str:
        """Call hinemos_create_scope tool."""
        try:
            with HinemosClient(**self.config) as client:
                repo_api = RepositoryAPI(client)
                
                scope = repo_api.create_scope(
                    facility_id=parameters["facility_id"],
                    facility_name=parameters["facility_name"],
                    parent_facility_id=parameters.get("parent_facility_id", ""),
                    description=parameters.get("description", ""),
                    owner_role_id=parameters.get("owner_role_id", "ALL_USERS"),
                    icon_image=parameters.get("icon_image")
                )
                
                result = {
                    "status": "created",
                    "facility_id": scope.facility_id,
                    "facility_name": scope.facility_name,
                    "description": scope.description,
                    "parent_facility_id": parameters.get("parent_facility_id")
                }
                
                return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_assign_nodes_to_scope(self, parameters: Dict[str, Any]) -> str:
        """Call hinemos_assign_nodes_to_scope tool."""
        try:
            with HinemosClient(**self.config) as client:
                repo_api = RepositoryAPI(client)
                scope_id = parameters["scope_id"]
                node_ids = parameters["node_ids"]
                
                repo_api.assign_nodes_to_scope(scope_id, node_ids)
                
                result = {
                    "status": "success",
                    "scope_id": scope_id,
                    "assigned_nodes": node_ids,
                    "message": f"Successfully assigned {len(node_ids)} nodes to scope {scope_id}"
                }
                
                return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_remove_nodes_from_scope(self, parameters: Dict[str, Any]) -> str:
        """Call hinemos_remove_nodes_from_scope tool."""
        try:
            with HinemosClient(**self.config) as client:
                repo_api = RepositoryAPI(client)
                scope_id = parameters["scope_id"]
                node_ids = parameters["node_ids"]
                
                repo_api.remove_nodes_from_scope(scope_id, node_ids)
                
                result = {
                    "status": "success",
                    "scope_id": scope_id,
                    "removed_nodes": node_ids,
                    "message": f"Successfully removed {len(node_ids)} nodes from scope {scope_id}"
                }
                
                return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _setup_routes(self):
        """Setup HTTP routes for the FastAPI server."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with server information."""
            return {
                "name": "Hinemos MCP Server",
                "version": "1.0.0",
                "transport": "HTTP",
                "hinemos_url": self.config["base_url"],
                "available_endpoints": [
                    "/health",
                    "/tools",
                    "/tools/{tool_name}",
                    "/resources",
                    "/resources/{resource_name}"
                ]
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            try:
                with HinemosClient(**self.config) as client:
                    # Simple connection test
                    repo_api = RepositoryAPI(client)
                    repo_api.list_nodes()
                    return {
                        "status": "healthy",
                        "hinemos_connection": "ok",
                        "timestamp": json.dumps(None, default=str)
                    }
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Hinemos connection failed: {str(e)}")
        
        @self.app.get("/tools")
        async def list_tools():
            """List all available MCP tools."""
            tools = [
                {
                    "name": "hinemos_get_facility_tree",
                    "description": "Get complete facility tree showing hierarchy and relationships",
                    "endpoint": "/tools/hinemos_get_facility_tree"
                },
                {
                    "name": "hinemos_get_repository_node", 
                    "description": "Get a specific node from Hinemos repository",
                    "endpoint": "/tools/hinemos_get_repository_node"
                },
                {
                    "name": "hinemos_create_repository_node",
                    "description": "Create a new node in Hinemos repository", 
                    "endpoint": "/tools/hinemos_create_repository_node"
                },
                {
                    "name": "hinemos_update_repository_node",
                    "description": "Update an existing node in Hinemos repository",
                    "endpoint": "/tools/hinemos_update_repository_node" 
                },
                {
                    "name": "hinemos_get_monitor",
                    "description": "Get a specific monitor configuration",
                    "endpoint": "/tools/hinemos_get_monitor"
                },
                {
                    "name": "hinemos_create_monitor",
                    "description": "Create a new monitor configuration (11 types supported)",
                    "endpoint": "/tools/hinemos_create_monitor"
                },
                {
                    "name": "hinemos_create_scope",
                    "description": "Create a new scope in Hinemos repository",
                    "endpoint": "/tools/hinemos_create_scope"
                },
                {
                    "name": "hinemos_assign_nodes_to_scope",
                    "description": "Assign nodes to a scope",
                    "endpoint": "/tools/hinemos_assign_nodes_to_scope"
                },
                {
                    "name": "hinemos_remove_nodes_from_scope", 
                    "description": "Remove nodes from a scope",
                    "endpoint": "/tools/hinemos_remove_nodes_from_scope"
                }
            ]
            return {"tools": tools}
        
        @self.app.post("/tools/{tool_name}")
        async def call_tool(tool_name: str, parameters: Dict[str, Any]):
            """Call a specific MCP tool."""
            try:
                # Define tool function mapping
                tool_functions = {
                    "hinemos_get_facility_tree": self._call_get_facility_tree,
                    "hinemos_get_repository_node": self._call_get_repository_node,
                    "hinemos_create_repository_node": self._call_create_repository_node,
                    "hinemos_update_repository_node": self._call_update_repository_node,
                    "hinemos_get_monitor": self._call_get_monitor,
                    "hinemos_create_monitor": self._call_create_monitor,
                    "hinemos_create_scope": self._call_create_scope,
                    "hinemos_assign_nodes_to_scope": self._call_assign_nodes_to_scope,
                    "hinemos_remove_nodes_from_scope": self._call_remove_nodes_from_scope
                }
                
                if tool_name not in tool_functions:
                    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
                
                # Call the tool function with parameters
                result = tool_functions[tool_name](parameters)
                
                return {
                    "tool": tool_name,
                    "status": "success",
                    "result": result
                }
            except TypeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")
        
        @self.app.get("/resources")
        async def list_resources():
            """List all available MCP resources."""
            resources = [
                {
                    "name": "facility_tree",
                    "uri": "hinemos://repository/facility_tree",
                    "endpoint": "/resources/facility_tree"
                },
                {
                    "name": "monitor_settings",
                    "uri": "hinemos://monitor/settings", 
                    "endpoint": "/resources/monitor_settings"
                }
            ]
            return {"resources": resources}
        
        @self.app.get("/resources/{resource_name}")
        async def get_resource(resource_name: str):
            """Get a specific MCP resource."""
            try:
                if resource_name == "facility_tree":
                    result = self._get_facility_tree_resource()
                elif resource_name == "monitor_settings":
                    result = self._get_monitor_settings_resource()
                else:
                    raise HTTPException(status_code=404, detail=f"Resource '{resource_name}' not found")
                
                return {
                    "resource": resource_name,
                    "status": "success",
                    "content": result
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Resource access failed: {str(e)}")
    
    def _get_facility_tree_resource(self) -> str:
        """Get facility tree resource."""
        try:
            with HinemosClient(**self.config) as client:
                repo_api = RepositoryAPI(client)
                tree_data = repo_api.get_facility_tree()
                return json.dumps(tree_data, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error reading facility tree: {str(e)}"
    
    def _get_monitor_settings_resource(self) -> str:
        """Get monitor settings resource."""
        try:
            with HinemosClient(**self.config) as client:
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
                return json.dumps(monitors_data, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error reading monitor settings: {str(e)}"
    
    def run(self, host: str = "127.0.0.1", port: int = 8000, **kwargs):
        """Run the HTTP FastMCP server."""
        print(f"Starting Hinemos HTTP FastMCP Server on {host}:{port}...")
        print(f"Hinemos URL: {self.config['base_url']}")
        print(f"Username: {self.config['username']}")
        print(f"Server URL: http://{host}:{port}")
        print(f"Health Check: http://{host}:{port}/health")
        print(f"Tools List: http://{host}:{port}/tools")
        
        uvicorn.run(self.app, host=host, port=port, **kwargs)


def main():
    """Main entry point for Hinemos HTTP FastMCP Server."""
    # Get configuration from environment variables
    base_url = os.environ.get("HINEMOS_BASE_URL", "http://localhost:8080/HinemosWeb/api")
    username = os.environ.get("HINEMOS_USERNAME", "hinemos")
    password = os.environ.get("HINEMOS_PASSWORD", "hinemos")
    verify_ssl = os.environ.get("HINEMOS_VERIFY_SSL", "true").lower() == "true"
    
    # HTTP server configuration
    host = os.environ.get("MCP_HTTP_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_HTTP_PORT", "8000"))
    
    # Validate required configuration
    if not all([base_url, username, password]):
        print("Error: Missing required environment variables:", file=sys.stderr)
        print("Required: HINEMOS_BASE_URL, HINEMOS_USERNAME, HINEMOS_PASSWORD", file=sys.stderr)
        print("Optional: HINEMOS_VERIFY_SSL (default: true)", file=sys.stderr)
        print("Optional: MCP_HTTP_HOST (default: 127.0.0.1), MCP_HTTP_PORT (default: 8000)", file=sys.stderr)
        sys.exit(1)
    
    # Create and run server
    server = HinemosHTTPFastMCPServer(
        base_url=base_url,
        username=username,
        password=password,
        verify_ssl=verify_ssl
    )
    
    try:
        server.run(host=host, port=port)
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()