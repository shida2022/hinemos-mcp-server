"""Hinemos Repository API wrapper with simplified interface."""

from typing import List, Optional

from .client import HinemosClient
from .models import (
    AddNodeRequest,
    AddScopeRequest,
    FacilityInfo,
    GetNodeListRequest,
    IpAddressVersion,
    ModifyNodeRequest,
    ModifyScopeRequest,
    NodeInfo,
    ScopeInfo,
    SnmpVersion,
)


class RepositoryAPI:
    """High-level wrapper for Hinemos Repository API."""
    
    def __init__(self, client: HinemosClient):
        """Initialize Repository API wrapper.
        
        Args:
            client: Hinemos client instance
        """
        self.client = client
    
    # Node management
    
    def create_node(
        self,
        facility_id: str,
        facility_name: str,
        ip_address: str,
        owner_role_id: str = "ADMINISTRATORS",
        description: Optional[str] = None,
        platform_family: Optional[str] = None,
        snmp_community: str = "public",
        snmp_port: int = 161,
        snmp_version: SnmpVersion = SnmpVersion.V2,
        **kwargs,
    ) -> NodeInfo:
        """Create a new node with common parameters.
        
        Args:
            facility_id: Unique facility ID for the node
            facility_name: Display name for the node
            ip_address: IP address of the node
            owner_role_id: Owner role ID (default: ADMINISTRATORS)
            description: Optional description
            platform_family: Platform family (Linux, Windows, etc.)
            snmp_community: SNMP community string
            snmp_port: SNMP port number
            snmp_version: SNMP version
            **kwargs: Additional node parameters
            
        Returns:
            Created node information
        """
        # Determine IP version
        ip_version = IpAddressVersion.IPV6 if ":" in ip_address else IpAddressVersion.IPV4
        
        node_request = AddNodeRequest(
            facility_id=facility_id,
            facility_name=facility_name,
            node_name=facility_name,  # ノード名はファシリティ名と同じに設定
            description=description,
            owner_role_id=owner_role_id,
            platform_family=platform_family,
            ip_address_v4=ip_address if ip_version == IpAddressVersion.IPV4 else None,
            ip_address_v6=ip_address if ip_version == IpAddressVersion.IPV6 else None,
            ip_address_version=ip_version,
            snmp_community=snmp_community,
            snmp_port=snmp_port,
            snmp_version=snmp_version,
            valid=True,
            **kwargs,
        )
        
        return self.client.add_node(node_request)
    
    def update_node(
        self,
        facility_id: str,
        facility_name: Optional[str] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        platform_family: Optional[str] = None,
        snmp_community: Optional[str] = None,
        **kwargs,
    ) -> NodeInfo:
        """Update an existing node.
        
        Args:
            facility_id: Facility ID of the node to update
            facility_name: New display name
            description: New description
            ip_address: New IP address
            platform_family: New platform family
            snmp_community: New SNMP community
            **kwargs: Additional node parameters
            
        Returns:
            Updated node information
        """
        # Get current node to use as defaults
        current_node = self.get_node(facility_id)
        
        update_data = {
            "facility_name": facility_name or current_node.facility_name,
            "node_name": current_node.node_name,  # ノード名が必須
            "platform_family": platform_family or current_node.platform_family,  # プラットフォームが必須
            "ip_address_version": current_node.ip_address_version,  # IPアドレスバージョンが必須
            "ip_address_v4": current_node.ip_address_v4,  # 既存のIPアドレスを維持
            "ip_address_v6": current_node.ip_address_v6
        }
        
        if description is not None:
            update_data["description"] = description
        # platform_family is already set above
        if snmp_community is not None:
            update_data["snmp_community"] = snmp_community
            
        if ip_address is not None:
            ip_version = IpAddressVersion.IPV6 if ":" in ip_address else IpAddressVersion.IPV4
            update_data["ip_address_version"] = ip_version
            if ip_version == IpAddressVersion.IPV4:
                update_data["ip_address_v4"] = ip_address
                update_data["ip_address_v6"] = None
            else:
                update_data["ip_address_v6"] = ip_address
                update_data["ip_address_v4"] = None
        
        update_data.update(kwargs)
        
        modify_request = ModifyNodeRequest(**update_data)
        return self.client.modify_node(facility_id, modify_request)
    
    def get_node(self, facility_id: str, include_config: bool = False) -> NodeInfo:
        """Get node information.
        
        Args:
            facility_id: Facility ID of the node
            include_config: Whether to include configuration details
            
        Returns:
            Node information
        """
        return self.client.get_node(facility_id, full=include_config)
    
    def list_nodes(
        self,
        parent_scope_id: Optional[str] = None,
        target_datetime: Optional[str] = None,
    ) -> List[NodeInfo]:
        """List nodes with optional filtering.
        
        Args:
            parent_scope_id: Parent scope to filter by
            target_datetime: Target datetime for historical data
            
        Returns:
            List of node information
        """
        request = GetNodeListRequest(
            parent_facility_id=parent_scope_id,
            node_config_target_datetime=target_datetime,
        )
        return self.client.get_node_list(request)
    
    def delete_node(self, facility_id: str) -> None:
        """Delete a node.
        
        Args:
            facility_id: Facility ID of the node to delete
        """
        self.client.delete_nodes([facility_id])
    
    def enable_node(self, facility_id: str) -> None:
        """Enable a node.
        
        Args:
            facility_id: Facility ID of the node
        """
        self.client.set_node_valid(facility_id, True)
    
    def disable_node(self, facility_id: str) -> None:
        """Disable a node.
        
        Args:
            facility_id: Facility ID of the node
        """
        self.client.set_node_valid(facility_id, False)
    
    def ping_node(self, facility_id: str, count: int = 3) -> dict:
        """Ping a node to test connectivity.
        
        Args:
            facility_id: Facility ID of the node
            count: Number of ping attempts
            
        Returns:
            Ping result
        """
        return self.client.ping_node(facility_id, count)
    
    # Scope management
    
    def create_scope(
        self,
        facility_id: str,
        facility_name: str,
        owner_role_id: str = "ADMINISTRATORS",
        description: Optional[str] = None,
        icon_image: Optional[str] = None,
    ) -> ScopeInfo:
        """Create a new scope.
        
        Args:
            facility_id: Unique facility ID for the scope
            facility_name: Display name for the scope
            owner_role_id: Owner role ID (default: ADMINISTRATORS)
            description: Optional description
            icon_image: Optional icon image
            
        Returns:
            Created scope information
        """
        scope_info = ScopeInfo(
            facility_id=facility_id,
            facility_name=facility_name,
            description=description,
            icon_image=icon_image,
            owner_role_id=owner_role_id,
        )
        
        scope_request = AddScopeRequest(
            scope_info=scope_info
        )
        
        return self.client.add_scope(scope_request)
    
    def update_scope(
        self,
        facility_id: str,
        facility_name: Optional[str] = None,
        description: Optional[str] = None,
        icon_image: Optional[str] = None,
    ) -> ScopeInfo:
        """Update an existing scope.
        
        Args:
            facility_id: Facility ID of the scope to update
            facility_name: New display name
            description: New description
            icon_image: New icon image
            
        Returns:
            Updated scope information
        """
        # Get current scope to use as defaults
        current_scope = self.get_scope(facility_id)
        
        update_data = {
            "facility_name": facility_name or current_scope.facility_name
        }
        if description is not None:
            update_data["description"] = description
        if icon_image is not None:
            update_data["icon_image"] = icon_image
        
        modify_request = ModifyScopeRequest(**update_data)
        return self.client.modify_scope(facility_id, modify_request)
    
    def get_scope(self, facility_id: str) -> ScopeInfo:
        """Get scope information.
        
        Args:
            facility_id: Facility ID of the scope
            
        Returns:
            Scope information
        """
        return self.client.get_scope(facility_id)
    
    def delete_scope(self, facility_id: str) -> None:
        """Delete a scope.
        
        Args:
            facility_id: Facility ID of the scope to delete
        """
        self.client.delete_scopes([facility_id])
    
    def assign_nodes_to_scope(self, scope_id: str, node_ids: List[str]) -> None:
        """Assign nodes to a scope.
        
        Args:
            scope_id: Facility ID of the scope
            node_ids: List of node facility IDs to assign
        """
        self.client.assign_node_to_scope(scope_id, node_ids)
    
    def remove_nodes_from_scope(self, scope_id: str, node_ids: List[str]) -> None:
        """Remove nodes from a scope.
        
        Args:
            scope_id: Facility ID of the scope
            node_ids: List of node facility IDs to remove
        """
        self.client.release_node_from_scope(scope_id, node_ids)
    
    # Facility tree operations
    
    def get_facility_tree(self, root_facility_id: Optional[str] = None, owner_role_id: str = "ALL_USERS") -> dict:
        """Get facility tree structure.
        
        Args:
            root_facility_id: Root facility ID to start from (None for full tree)
            owner_role_id: Owner role ID for access control
            
        Returns:
            Complete facility tree structure as dict
        """
        return self.client.get_facility_tree(root_facility_id, owner_role_id)
    
    def get_node_tree(self, owner_role_id: str = "ALL_USERS") -> dict:
        """Get node tree (nodes only).
        
        Args:
            owner_role_id: Owner role ID for access control
            
        Returns:
            Node tree structure as dict
        """
        return self.client.get_node_tree(owner_role_id)
    
    def get_all_facilities(self) -> List[FacilityInfo]:
        """Get all facility information.
        
        Returns:
            List of all facility information
        """
        return self.client.get_facility_info()
    
    def list_scopes(self) -> List[FacilityInfo]:
        """List all scopes in the repository.
        
        Returns:
            List of scope information
        """
        all_facilities = self.get_all_facilities()
        # Filter only scopes (facilities that are not nodes)
        return [facility for facility in all_facilities if not hasattr(facility, 'node_name')]
    
    # Agent operations
    
    def get_agent_status(self) -> dict:
        """Get agent status for all nodes.
        
        Returns:
            Agent status information
        """
        agents = self.client.get_agent_status()
        return {
            "agents": [
                {
                    "facility_id": agent.facility_id,
                    "startup_time": agent.startup_time,
                    "last_login": agent.last_login,
                    "multiplicity": agent.multiplicity,
                    "awake_port": agent.awake_port,
                }
                for agent in agents
            ]
        }