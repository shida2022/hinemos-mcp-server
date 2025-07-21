"""Hinemos REST API client."""

import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import ValidationError

from .models import (
    AddNodeRequest,
    AddScopeRequest,
    AgentStatusInfo,
    FacilityInfo,
    FacilityTreeResponse,
    GetNodeListRequest,
    GetNodeListResponse,
    LoginRequest,
    LoginResponse,
    ModifyNodeRequest,
    ModifyScopeRequest,
    NodeInfo,
    ScopeInfo,
)
from .monitor_models import (
    AbstractMonitorResponse,
    AddPingMonitorRequest,
    AddHttpNumericMonitorRequest,
    AddHttpStringMonitorRequest,
    AddSnmpNumericMonitorRequest,
    AddLogfileMonitorRequest,
    AddSqlMonitorRequest,
    AddJmxMonitorRequest,
    AddProcessMonitorRequest,
    AddPortMonitorRequest,
    AddWinEventMonitorRequest,
    AddCustomMonitorRequest,
    CollectorValidRequest,
    GetMonitorListRequest,
    HttpNumericMonitorResponse,
    HttpStringMonitorResponse,
    LogfileMonitorResponse,
    SqlMonitorResponse,
    JmxMonitorResponse,
    ProcessMonitorResponse,
    PortMonitorResponse,
    WinEventMonitorResponse,
    CustomMonitorResponse,
    ModifyPingMonitorRequest,
    ModifyHttpNumericMonitorRequest,
    ModifyHttpStringMonitorRequest,
    ModifySnmpNumericMonitorRequest,
    ModifyLogfileMonitorRequest,
    ModifySqlMonitorRequest,
    ModifyJmxMonitorRequest,
    ModifyProcessMonitorRequest,
    ModifyPortMonitorRequest,
    ModifyWinEventMonitorRequest,
    ModifyCustomMonitorRequest,
    MonitorValidRequest,
    PingMonitorResponse,
    SnmpNumericMonitorResponse,
)


class HinemosAPIError(Exception):
    """Hinemos API error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class HinemosClient:
    """Hinemos REST API client."""
    
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        """Initialize Hinemos client.
        
        Args:
            base_url: Hinemos Manager base URL (e.g., "http://hinemos-manager:8080/HinemosWeb/api")
            username: Username for authentication
            password: Password for authentication
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._token = None
        
        self._client = httpx.Client(
            timeout=timeout,
            verify=verify_ssl,
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def login(self) -> None:
        """Login and obtain authentication token."""
        if self._token:
            return  # Already logged in
            
        # Use the correct endpoint path
        login_url = f"{self.base_url}/AccessRestEndpoints/access/login"
        login_data = {"userId": self.username, "password": self.password}
        
        try:
            response = self._client.post(
                login_url,
                json=login_data,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            
            login_response = response.json()
            token_info = login_response.get('token', {})
            self._token = token_info.get('tokenId')
            
        except httpx.HTTPStatusError as e:
            error_detail = "Login failed"
            try:
                error_response = e.response.json()
                error_detail = error_response.get("message", str(error_response))
            except (ValueError, json.JSONDecodeError):
                error_detail = e.response.text or str(e)
            
            raise HinemosAPIError(
                f"Login failed - HTTP {e.response.status_code}: {error_detail}",
                status_code=e.response.status_code,
                response=error_response if 'error_response' in locals() else None,
            ) from e
        
        except httpx.RequestError as e:
            raise HinemosAPIError(f"Login request failed: {e}") from e
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Hinemos API."""
        # Ensure we are logged in
        if not self._token:
            self.login()
            
        # Repository endpoints need the RepositoryRestEndpoints prefix
        # Monitor endpoints need the MonitorsettingRestEndpoints prefix
        endpoint_cleaned = endpoint.lstrip("/")
        if endpoint_cleaned.startswith("repository/"):
            url = f"{self.base_url}/RepositoryRestEndpoints/{endpoint_cleaned}"
        elif endpoint_cleaned.startswith("monitorsetting/"):
            url = f"{self.base_url}/MonitorsettingRestEndpoints/{endpoint_cleaned}"
        elif endpoint_cleaned.startswith("monitorresult/"):
            url = f"{self.base_url}/MonitorResultRestEndpoints/{endpoint_cleaned}"
        else:
            url = urljoin(self.base_url + "/", endpoint_cleaned)
        
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        
        try:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
            )
            response.raise_for_status()
            
            if response.status_code == 204:  # No Content
                return {}
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_response = e.response.json()
                error_detail = error_response.get("message", str(error_response))
            except (ValueError, json.JSONDecodeError):
                error_detail = e.response.text or str(e)
            
            raise HinemosAPIError(
                f"HTTP {e.response.status_code}: {error_detail}",
                status_code=e.response.status_code,
                response=error_response if 'error_response' in locals() else None,
            ) from e
        
        except httpx.RequestError as e:
            raise HinemosAPIError(f"Request failed: {e}") from e
    
    # Repository API methods
    
    def get_facility_tree(self, target_facility_id: Optional[str] = None, owner_role_id: str = "ALL_USERS") -> dict:
        """Get facility tree.
        
        Args:
            target_facility_id: Target facility ID to get tree from (None for full tree)
            owner_role_id: Owner role ID for access control
            
        Returns:
            Facility tree structure as dict
        """
        if target_facility_id:
            endpoint = f"/repository/facility_tree/{target_facility_id}"
            params = {"ownerRoleId": owner_role_id}
        else:
            endpoint = "/repository/facility_tree"
            params = {"ownerRoleId": owner_role_id}
        
        response_data = self._make_request("GET", endpoint, params=params)
        return response_data
    
    def get_node_tree(self, owner_role_id: str = "ALL_USERS") -> dict:
        """Get node tree (nodes only).
        
        Args:
            owner_role_id: Owner role ID for access control
            
        Returns:
            Node tree structure as dict
        """
        endpoint = "/repository/facility_nodeTree"
        params = {"ownerRoleId": owner_role_id}
        response_data = self._make_request("GET", endpoint, params=params)
        return response_data
    
    def get_node(self, facility_id: str, full: bool = False) -> NodeInfo:
        """Get node information.
        
        Args:
            facility_id: Facility ID of the node
            full: Whether to get full node info including configuration details
            
        Returns:
            Node information
        """
        if full:
            endpoint = f"/repository/node/{facility_id}"
        else:
            endpoint = f"/repository/node_withoutNodeConfigInfo/{facility_id}"
        
        response_data = self._make_request("GET", endpoint)
        return NodeInfo(**response_data)
    
    def get_scope(self, facility_id: str) -> ScopeInfo:
        """Get scope information.
        
        Args:
            facility_id: Facility ID of the scope
            
        Returns:
            Scope information
        """
        response_data = self._make_request("GET", f"/repository/scope/{facility_id}")
        return ScopeInfo(**response_data)
    
    def get_node_list(self, request: Optional[GetNodeListRequest] = None) -> List[NodeInfo]:
        """Get node list.
        
        Args:
            request: Request parameters for filtering nodes
            
        Returns:
            List of node information
        """
        json_data = request.model_dump(by_alias=True, exclude_none=True) if request else {}
        response_data = self._make_request("POST", "/repository/node_withoutNodeConfigInfo_search", json_data=json_data)
        # Response is directly a list of nodes
        return [NodeInfo(**node) for node in response_data]
    
    def add_node(self, node: AddNodeRequest) -> NodeInfo:
        """Add a new node.
        
        Args:
            node: Node information to add
            
        Returns:
            Created node information
        """
        json_data = node.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/repository/node", json_data=json_data)
        return NodeInfo(**response_data)
    
    def modify_node(self, facility_id: str, node: ModifyNodeRequest) -> NodeInfo:
        """Modify an existing node.
        
        Args:
            facility_id: Facility ID of the node to modify
            node: Node information to update
            
        Returns:
            Updated node information
        """
        json_data = node.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/repository/node/{facility_id}", json_data=json_data)
        return NodeInfo(**response_data)
    
    def delete_nodes(self, facility_ids: List[str]) -> None:
        """Delete nodes.
        
        Args:
            facility_ids: List of facility IDs to delete
        """
        # Use query parameter instead of JSON body
        params = {"facilityIds": ",".join(facility_ids)}
        self._make_request("DELETE", "/repository/node", params=params)
    
    def add_scope(self, scope: AddScopeRequest) -> ScopeInfo:
        """Add a new scope.
        
        Args:
            scope: Scope information to add
            
        Returns:
            Created scope information
        """
        json_data = scope.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/repository/scope", json_data=json_data)
        return ScopeInfo(**response_data)
    
    def modify_scope(self, facility_id: str, scope: ModifyScopeRequest) -> ScopeInfo:
        """Modify an existing scope.
        
        Args:
            facility_id: Facility ID of the scope to modify
            scope: Scope information to update
            
        Returns:
            Updated scope information
        """
        json_data = scope.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/repository/scope/{facility_id}", json_data=json_data)
        return ScopeInfo(**response_data)
    
    def delete_scopes(self, facility_ids: List[str]) -> None:
        """Delete scopes.
        
        Args:
            facility_ids: List of facility IDs to delete
        """
        # Use query parameter instead of JSON body
        params = {"facilityIds": ",".join(facility_ids)}
        self._make_request("DELETE", "/repository/scope", params=params)
    
    def assign_node_to_scope(self, parent_facility_id: str, facility_ids: List[str]) -> None:
        """Assign nodes to a scope.
        
        Args:
            parent_facility_id: Parent scope facility ID
            facility_ids: List of node facility IDs to assign
        """
        json_data = {"facilityIdList": facility_ids}
        self._make_request("PUT", f"/repository/facilityRelation/{parent_facility_id}", json_data=json_data)
    
    def release_node_from_scope(self, parent_facility_id: str, facility_ids: List[str]) -> None:
        """Release nodes from a scope.
        
        Args:
            parent_facility_id: Parent scope facility ID
            facility_ids: List of node facility IDs to release
        """
        json_data = {"facilityIdList": facility_ids}
        self._make_request("PUT", f"/repository/facilityRelation_release/{parent_facility_id}", json_data=json_data)
    
    def set_node_valid(self, facility_id: str, valid: bool) -> None:
        """Set node valid/invalid status.
        
        Args:
            facility_id: Facility ID of the node
            valid: True to enable, False to disable
        """
        json_data = {"flg": valid}
        self._make_request("PUT", f"/repository/node_valid/{facility_id}", json_data=json_data)
    
    def get_agent_status(self) -> List[AgentStatusInfo]:
        """Get agent status information.
        
        Returns:
            List of agent status information
        """
        response_data = self._make_request("GET", "/repository/agentStatus")
        return [AgentStatusInfo(**agent) for agent in response_data]
    
    def ping_node(self, facility_id: str, reachability_num: int = 3) -> Dict[str, Any]:
        """Ping a node.
        
        Args:
            facility_id: Facility ID of the node to ping
            reachability_num: Number of ping attempts
            
        Returns:
            Ping result
        """
        json_data = {"reachabilityNum": reachability_num}
        return self._make_request("POST", f"/repository/facility_ping/{facility_id}", json_data=json_data)
    
    def get_facility_info(self) -> List[FacilityInfo]:
        """Get all facility information.
        
        Returns:
            List of facility information
        """
        response_data = self._make_request("GET", "/repository/facility")
        return [FacilityInfo(**item) for item in response_data]
    
    # Monitor API methods
    
    def get_monitor_list(self, request: Optional[GetMonitorListRequest] = None) -> List[AbstractMonitorResponse]:
        """Get monitor list.
        
        Args:
            request: Search criteria for monitors
            
        Returns:
            List of monitor information
        """
        if request:
            json_data = request.model_dump(by_alias=True, exclude_none=True)
            response_data = self._make_request("POST", "/monitorsetting/monitor_search", json_data=json_data)
        else:
            response_data = self._make_request("GET", "/monitorsetting/monitor")
        
        return [AbstractMonitorResponse(**monitor) for monitor in response_data]
    
    def get_monitor(self, monitor_id: str) -> AbstractMonitorResponse:
        """Get monitor information by ID.
        
        Args:
            monitor_id: Monitor ID
            
        Returns:
            Monitor information
        """
        response_data = self._make_request("GET", f"/monitorsetting/monitor/{monitor_id}")
        return AbstractMonitorResponse(**response_data)
    
    def delete_monitors(self, monitor_ids: List[str]) -> None:
        """Delete monitors.
        
        Args:
            monitor_ids: List of monitor IDs to delete
        """
        json_data = {"monitorIdList": monitor_ids}
        self._make_request("DELETE", "/monitorsetting/monitor", json_data=json_data)
    
    def set_monitor_valid(self, monitor_ids: List[str], valid: bool) -> None:
        """Set monitor valid/invalid status.
        
        Args:
            monitor_ids: List of monitor IDs
            valid: True to enable, False to disable
        """
        request = MonitorValidRequest(monitor_ids=monitor_ids, valid_flg=valid)
        json_data = request.model_dump(by_alias=True)
        self._make_request("PUT", "/monitorsetting/monitor_monitorValid", json_data=json_data)
    
    def set_collector_valid(self, monitor_ids: List[str], valid: bool) -> None:
        """Set collector valid/invalid status.
        
        Args:
            monitor_ids: List of monitor IDs
            valid: True to enable, False to disable
        """
        request = CollectorValidRequest(monitor_ids=monitor_ids, valid_flg=valid)
        json_data = request.model_dump(by_alias=True)
        self._make_request("PUT", "/monitorsetting/monitor_collectorValid", json_data=json_data)
    
    # Ping monitoring
    def add_ping_monitor(self, monitor: AddPingMonitorRequest) -> PingMonitorResponse:
        """Add a new ping monitor.
        
        Args:
            monitor: Ping monitor configuration
            
        Returns:
            Created ping monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/ping", json_data=json_data)
        return PingMonitorResponse(**response_data)
    
    def modify_ping_monitor(self, monitor_id: str, monitor: ModifyPingMonitorRequest) -> PingMonitorResponse:
        """Modify an existing ping monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: Ping monitor configuration
            
        Returns:
            Updated ping monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/ping/{monitor_id}", json_data=json_data)
        return PingMonitorResponse(**response_data)
    
    def get_ping_monitor_list(self) -> List[PingMonitorResponse]:
        """Get ping monitor list.
        
        Returns:
            List of ping monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/ping")
        return [PingMonitorResponse(**monitor) for monitor in response_data]
    
    # HTTP monitoring
    def add_http_numeric_monitor(self, monitor: AddHttpNumericMonitorRequest) -> HttpNumericMonitorResponse:
        """Add a new HTTP numeric monitor.
        
        Args:
            monitor: HTTP numeric monitor configuration
            
        Returns:
            Created HTTP numeric monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/httpNumeric", json_data=json_data)
        return HttpNumericMonitorResponse(**response_data)
    
    def modify_http_numeric_monitor(self, monitor_id: str, monitor: ModifyHttpNumericMonitorRequest) -> HttpNumericMonitorResponse:
        """Modify an existing HTTP numeric monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: HTTP numeric monitor configuration
            
        Returns:
            Updated HTTP numeric monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/httpNumeric/{monitor_id}", json_data=json_data)
        return HttpNumericMonitorResponse(**response_data)
    
    def get_http_numeric_monitor_list(self) -> List[HttpNumericMonitorResponse]:
        """Get HTTP numeric monitor list.
        
        Returns:
            List of HTTP numeric monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/httpNumeric")
        return [HttpNumericMonitorResponse(**monitor) for monitor in response_data]
    
    def add_http_string_monitor(self, monitor: AddHttpStringMonitorRequest) -> HttpStringMonitorResponse:
        """Add a new HTTP string monitor.
        
        Args:
            monitor: HTTP string monitor configuration
            
        Returns:
            Created HTTP string monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/httpString", json_data=json_data)
        return HttpStringMonitorResponse(**response_data)
    
    def modify_http_string_monitor(self, monitor_id: str, monitor: ModifyHttpStringMonitorRequest) -> HttpStringMonitorResponse:
        """Modify an existing HTTP string monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: HTTP string monitor configuration
            
        Returns:
            Updated HTTP string monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/httpString/{monitor_id}", json_data=json_data)
        return HttpStringMonitorResponse(**response_data)
    
    def get_http_string_monitor_list(self) -> List[HttpStringMonitorResponse]:
        """Get HTTP string monitor list.
        
        Returns:
            List of HTTP string monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/httpString")
        return [HttpStringMonitorResponse(**monitor) for monitor in response_data]
    
    # SNMP monitoring
    def add_snmp_numeric_monitor(self, monitor: AddSnmpNumericMonitorRequest) -> SnmpNumericMonitorResponse:
        """Add a new SNMP numeric monitor.
        
        Args:
            monitor: SNMP numeric monitor configuration
            
        Returns:
            Created SNMP numeric monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/snmpNumeric", json_data=json_data)
        return SnmpNumericMonitorResponse(**response_data)
    
    def modify_snmp_numeric_monitor(self, monitor_id: str, monitor: ModifySnmpNumericMonitorRequest) -> SnmpNumericMonitorResponse:
        """Modify an existing SNMP numeric monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: SNMP numeric monitor configuration
            
        Returns:
            Updated SNMP numeric monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/snmpNumeric/{monitor_id}", json_data=json_data)
        return SnmpNumericMonitorResponse(**response_data)
    
    def get_snmp_numeric_monitor_list(self) -> List[SnmpNumericMonitorResponse]:
        """Get SNMP numeric monitor list.
        
        Returns:
            List of SNMP numeric monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/snmpNumeric")
        return [SnmpNumericMonitorResponse(**monitor) for monitor in response_data]
    
    # Log file monitoring
    def add_logfile_monitor(self, monitor: AddLogfileMonitorRequest) -> LogfileMonitorResponse:
        """Add a new logfile monitor.
        
        Args:
            monitor: Logfile monitor configuration
            
        Returns:
            Created logfile monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/logfile", json_data=json_data)
        return LogfileMonitorResponse(**response_data)
    
    def modify_logfile_monitor(self, monitor_id: str, monitor: ModifyLogfileMonitorRequest) -> LogfileMonitorResponse:
        """Modify an existing logfile monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: Logfile monitor configuration
            
        Returns:
            Updated logfile monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/logfile/{monitor_id}", json_data=json_data)
        return LogfileMonitorResponse(**response_data)
    
    def get_logfile_monitor_list(self) -> List[LogfileMonitorResponse]:
        """Get logfile monitor list.
        
        Returns:
            List of logfile monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/logfile")
        return [LogfileMonitorResponse(**monitor) for monitor in response_data]
    
    # SQL monitoring
    def add_sql_monitor(self, monitor: AddSqlMonitorRequest) -> SqlMonitorResponse:
        """Add a new SQL monitor.
        
        Args:
            monitor: SQL monitor configuration
            
        Returns:
            Created SQL monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/sqlNumeric", json_data=json_data)
        return SqlMonitorResponse(**response_data)
    
    def modify_sql_monitor(self, monitor_id: str, monitor: ModifySqlMonitorRequest) -> SqlMonitorResponse:
        """Modify an existing SQL monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: SQL monitor configuration
            
        Returns:
            Updated SQL monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/sqlNumeric/{monitor_id}", json_data=json_data)
        return SqlMonitorResponse(**response_data)
    
    def get_sql_monitor_list(self) -> List[SqlMonitorResponse]:
        """Get SQL monitor list.
        
        Returns:
            List of SQL monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/sqlNumeric")
        return [SqlMonitorResponse(**monitor) for monitor in response_data]
    
    # JMX monitoring
    def add_jmx_monitor(self, monitor: AddJmxMonitorRequest) -> JmxMonitorResponse:
        """Add a new JMX monitor.
        
        Args:
            monitor: JMX monitor configuration
            
        Returns:
            Created JMX monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/jmx", json_data=json_data)
        return JmxMonitorResponse(**response_data)
    
    def modify_jmx_monitor(self, monitor_id: str, monitor: ModifyJmxMonitorRequest) -> JmxMonitorResponse:
        """Modify an existing JMX monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: JMX monitor configuration
            
        Returns:
            Updated JMX monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/jmx/{monitor_id}", json_data=json_data)
        return JmxMonitorResponse(**response_data)
    
    def get_jmx_monitor_list(self) -> List[JmxMonitorResponse]:
        """Get JMX monitor list.
        
        Returns:
            List of JMX monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/jmx")
        return [JmxMonitorResponse(**monitor) for monitor in response_data]
    
    # Process monitoring
    def add_process_monitor(self, monitor: AddProcessMonitorRequest) -> ProcessMonitorResponse:
        """Add a new process monitor.
        
        Args:
            monitor: Process monitor configuration
            
        Returns:
            Created process monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/process", json_data=json_data)
        return ProcessMonitorResponse(**response_data)
    
    def modify_process_monitor(self, monitor_id: str, monitor: ModifyProcessMonitorRequest) -> ProcessMonitorResponse:
        """Modify an existing process monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: Process monitor configuration
            
        Returns:
            Updated process monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/process/{monitor_id}", json_data=json_data)
        return ProcessMonitorResponse(**response_data)
    
    def get_process_monitor_list(self) -> List[ProcessMonitorResponse]:
        """Get process monitor list.
        
        Returns:
            List of process monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/process")
        return [ProcessMonitorResponse(**monitor) for monitor in response_data]
    
    # Port monitoring
    def add_port_monitor(self, monitor: AddPortMonitorRequest) -> PortMonitorResponse:
        """Add a new port monitor.
        
        Args:
            monitor: Port monitor configuration
            
        Returns:
            Created port monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/serviceport", json_data=json_data)
        return PortMonitorResponse(**response_data)
    
    def modify_port_monitor(self, monitor_id: str, monitor: ModifyPortMonitorRequest) -> PortMonitorResponse:
        """Modify an existing port monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: Port monitor configuration
            
        Returns:
            Updated port monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/serviceport/{monitor_id}", json_data=json_data)
        return PortMonitorResponse(**response_data)
    
    def get_port_monitor_list(self) -> List[PortMonitorResponse]:
        """Get port monitor list.
        
        Returns:
            List of port monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/serviceport")
        return [PortMonitorResponse(**monitor) for monitor in response_data]
    
    # Windows Event monitoring
    def add_winevent_monitor(self, monitor: AddWinEventMonitorRequest) -> WinEventMonitorResponse:
        """Add a new Windows Event monitor.
        
        Args:
            monitor: Windows Event monitor configuration
            
        Returns:
            Created Windows Event monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/winevent", json_data=json_data)
        return WinEventMonitorResponse(**response_data)
    
    def modify_winevent_monitor(self, monitor_id: str, monitor: ModifyWinEventMonitorRequest) -> WinEventMonitorResponse:
        """Modify an existing Windows Event monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: Windows Event monitor configuration
            
        Returns:
            Updated Windows Event monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/winevent/{monitor_id}", json_data=json_data)
        return WinEventMonitorResponse(**response_data)
    
    def get_winevent_monitor_list(self) -> List[WinEventMonitorResponse]:
        """Get Windows Event monitor list.
        
        Returns:
            List of Windows Event monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/winevent")
        return [WinEventMonitorResponse(**monitor) for monitor in response_data]
    
    # Custom monitoring
    def add_custom_monitor(self, monitor: AddCustomMonitorRequest) -> CustomMonitorResponse:
        """Add a new custom monitor.
        
        Args:
            monitor: Custom monitor configuration
            
        Returns:
            Created custom monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("POST", "/monitorsetting/customNumeric", json_data=json_data)
        return CustomMonitorResponse(**response_data)
    
    def modify_custom_monitor(self, monitor_id: str, monitor: ModifyCustomMonitorRequest) -> CustomMonitorResponse:
        """Modify an existing custom monitor.
        
        Args:
            monitor_id: Monitor ID to modify
            monitor: Custom monitor configuration
            
        Returns:
            Updated custom monitor information
        """
        json_data = monitor.model_dump(by_alias=True, exclude_none=True)
        response_data = self._make_request("PUT", f"/monitorsetting/customNumeric/{monitor_id}", json_data=json_data)
        return CustomMonitorResponse(**response_data)
    
    def get_custom_monitor_list(self) -> List[CustomMonitorResponse]:
        """Get custom monitor list.
        
        Returns:
            List of custom monitor information
        """
        response_data = self._make_request("GET", "/monitorsetting/customNumeric")
        return [CustomMonitorResponse(**monitor) for monitor in response_data]