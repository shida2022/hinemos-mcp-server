"""Hinemos MCP Server implementation using FastMCP."""

import json
import os
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from ..client import HinemosClient
from ..repository import RepositoryAPI
from ..monitor import MonitorAPI
from ..monitor_models import RunIntervalEnum, PriorityEnum, ConvertFlagEnum


class HinemosFastMCPServer:
    """Hinemos MCP Server using FastMCP framework."""
    
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = True):
        """Initialize Hinemos FastMCP Server.
        
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
        self.mcp = FastMCP("hinemos-mcp")
        self._setup_tools()
        self._setup_resources()
    
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
        def hinemos_create_ping_monitor(
            monitor_id: str,
            facility_id: str,
            description: str = "",
            run_interval: str = "MIN_05",
            run_count: int = 3,
            timeout: int = 5000
        ) -> str:
            """Create a new ping monitor configuration.
            
            Args:
                monitor_id: Unique monitor ID
                facility_id: Target facility ID
                description: Monitor description
                run_interval: Monitoring interval (MIN_01, MIN_05, MIN_10, MIN_30, MIN_60)
                run_count: Number of ping attempts
                timeout: Timeout in milliseconds
                
            Returns:
                JSON string containing creation result
            """
            try:
                with HinemosClient(**self.config) as client:
                    monitor_api = MonitorAPI(client)
                    
                    monitor = monitor_api.create_ping_monitor(
                        monitor_id=monitor_id,
                        facility_id=facility_id,
                        description=description,
                        run_interval=RunIntervalEnum(run_interval),
                        run_count=run_count,
                        timeout=timeout,
                        prediction_flg=False,
                        change_flg=False
                    )
                    
                    result = {
                        "status": "created",
                        "monitor_id": monitor.monitor_id,
                        "monitor_type": "ping",
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
    
    def run(self):
        """Run the FastMCP server."""
        self.mcp.run()


def main():
    """Main entry point for Hinemos FastMCP Server."""
    # Get configuration from environment variables
    base_url = os.environ.get("HINEMOS_BASE_URL", "http://localhost:8080/HinemosWeb/api")
    username = os.environ.get("HINEMOS_USERNAME", "hinemos")
    password = os.environ.get("HINEMOS_PASSWORD", "hinemos")
    verify_ssl = os.environ.get("HINEMOS_VERIFY_SSL", "true").lower() == "true"
    
    # Validate required configuration
    if not all([base_url, username, password]):
        print("Error: Missing required environment variables:", file=sys.stderr)
        print("Required: HINEMOS_BASE_URL, HINEMOS_USERNAME, HINEMOS_PASSWORD", file=sys.stderr)
        print("Optional: HINEMOS_VERIFY_SSL (default: true)", file=sys.stderr)
        sys.exit(1)
    
    # Create and run server
    server = HinemosFastMCPServer(
        base_url=base_url,
        username=username,
        password=password,
        verify_ssl=verify_ssl
    )
    
    print(f"Starting Hinemos FastMCP Server...", file=sys.stderr)
    print(f"Hinemos URL: {base_url}", file=sys.stderr)
    print(f"Username: {username}", file=sys.stderr)
    print(f"SSL Verification: {verify_ssl}", file=sys.stderr)
    
    import asyncio
    import sys
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()