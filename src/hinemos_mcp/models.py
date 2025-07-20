"""Hinemos API data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class IpAddressVersion(str, Enum):
    """IP address version enum."""
    IPV4 = "IPV4"
    IPV6 = "IPV6"


class FacilityType(str, Enum):
    """Facility type enum."""
    SCOPE = "TYPE_SCOPE"
    NODE = "TYPE_NODE"
    COMPOSITE = "TYPE_COMPOSITE" 
    MANAGER = "TYPE_MANAGER"


class SnmpVersion(str, Enum):
    """SNMP version enum."""
    V1 = "TYPE_V1"
    V2 = "TYPE_V2"
    V3 = "TYPE_V3"


class NodeOsInfo(BaseModel):
    """Node OS information."""
    os_name: Optional[str] = Field(None, alias="osName")
    os_release: Optional[str] = Field(None, alias="osRelease")
    os_version: Optional[str] = Field(None, alias="osVersion")
    character_set: Optional[str] = Field(None, alias="characterSet")
    startup_date_time: Optional[str] = Field(None, alias="startupDateTime")
    reg_date: Optional[str] = Field(None, alias="regDate")
    reg_user: Optional[str] = Field(None, alias="regUser")
    update_date: Optional[str] = Field(None, alias="updateDate")
    update_user: Optional[str] = Field(None, alias="updateUser")
    search_target: Optional[bool] = Field(None, alias="searchTarget")


class NodeVariableInfo(BaseModel):
    """Node variable information."""
    node_variable_name: Optional[str] = Field(None, alias="nodeVariableName")
    node_variable_value: Optional[str] = Field(None, alias="nodeVariableValue")
    reg_date: Optional[str] = Field(None, alias="regDate")
    reg_user: Optional[str] = Field(None, alias="regUser")
    update_date: Optional[str] = Field(None, alias="updateDate")
    update_user: Optional[str] = Field(None, alias="updateUser")
    search_target: Optional[bool] = Field(None, alias="searchTarget")


class FacilityInfo(BaseModel):
    """Facility information."""
    facility_id: str = Field(alias="facilityId")
    facility_name: str = Field(alias="facilityName")
    facility_type: Optional[FacilityType] = Field(None, alias="facilityType")
    description: Optional[str] = None
    display_sort_order: Optional[int] = Field(None, alias="displaySortOrder")
    icon_image: Optional[str] = Field(None, alias="iconImage")
    valid: Optional[bool] = None
    create_user_id: Optional[str] = Field(None, alias="createUserId")
    create_datetime: Optional[str] = Field(None, alias="createDatetime")
    modify_user_id: Optional[str] = Field(None, alias="modifyUserId")
    modify_datetime: Optional[str] = Field(None, alias="modifyDatetime")
    built_in_flg: Optional[bool] = Field(None, alias="builtInFlg")
    not_refer_flg: Optional[bool] = Field(None, alias="notReferFlg")
    owner_role_id: Optional[str] = Field(None, alias="ownerRoleId")


class NodeInfo(BaseModel):
    """Node information."""
    facility_id: str = Field(alias="facilityId")
    facility_name: str = Field(alias="facilityName")
    description: Optional[str] = None
    valid: Optional[bool] = None
    owner_role_id: Optional[str] = Field(None, alias="ownerRoleId")
    
    # Node basic settings
    auto_device_search: Optional[bool] = Field(None, alias="autoDeviceSearch")
    administrator: Optional[str] = None
    contact: Optional[str] = None
    hardware_type: Optional[str] = Field(None, alias="hardwareType")
    node_name: Optional[str] = Field(None, alias="nodeName")
    platform_family: Optional[str] = Field(None, alias="platformFamily")
    sub_platform_family: Optional[str] = Field(None, alias="subPlatformFamily")
    
    # Network settings
    ip_address_v4: Optional[str] = Field(None, alias="ipAddressV4")
    ip_address_v6: Optional[str] = Field(None, alias="ipAddressV6")
    ip_address_version: Optional[IpAddressVersion] = Field(None, alias="ipAddressVersion")
    
    # SNMP settings
    snmp_community: Optional[str] = Field(None, alias="snmpCommunity")
    snmp_port: Optional[int] = Field(None, alias="snmpPort")
    snmp_version: Optional[SnmpVersion] = Field(None, alias="snmpVersion")
    snmp_user: Optional[str] = Field(None, alias="snmpUser")
    snmp_auth_password: Optional[str] = Field(None, alias="snmpAuthPassword")
    snmp_priv_password: Optional[str] = Field(None, alias="snmpPrivPassword")
    snmp_retry_count: Optional[int] = Field(None, alias="snmpRetryCount")
    snmp_timeout: Optional[int] = Field(None, alias="snmpTimeout")
    
    # SSH settings
    ssh_user: Optional[str] = Field(None, alias="sshUser")
    ssh_user_password: Optional[str] = Field(None, alias="sshUserPassword")
    ssh_private_key_filepath: Optional[str] = Field(None, alias="sshPrivateKeyFilepath")
    ssh_private_key_passphrase: Optional[str] = Field(None, alias="sshPrivateKeyPassphrase")
    ssh_port: Optional[int] = Field(None, alias="sshPort")
    ssh_timeout: Optional[int] = Field(None, alias="sshTimeout")
    
    # Cloud settings
    cloud_service: Optional[str] = Field(None, alias="cloudService")
    cloud_scope: Optional[str] = Field(None, alias="cloudScope")
    cloud_resource_type: Optional[str] = Field(None, alias="cloudResourceType")
    cloud_resource_id: Optional[str] = Field(None, alias="cloudResourceId")
    cloud_resource_name: Optional[str] = Field(None, alias="cloudResourceName")
    cloud_location: Optional[str] = Field(None, alias="cloudLocation")
    
    # Job settings
    job_priority: Optional[int] = Field(None, alias="jobPriority")
    job_multiplicity: Optional[int] = Field(None, alias="jobMultiplicity")
    
    # Other settings
    agent_awake_port: Optional[int] = Field(None, alias="agentAwakePort")
    display_sort_order: Optional[int] = Field(None, alias="displaySortOrder")
    icon_image: Optional[str] = Field(None, alias="iconImage")
    
    # Metadata
    create_user_id: Optional[str] = Field(None, alias="createUserId")
    create_datetime: Optional[str] = Field(None, alias="createDatetime")
    modify_user_id: Optional[str] = Field(None, alias="modifyUserId")
    modify_datetime: Optional[str] = Field(None, alias="modifyDatetime")
    built_in_flg: Optional[bool] = Field(None, alias="builtInFlg")
    not_refer_flg: Optional[bool] = Field(None, alias="notReferFlg")
    
    # Configuration info (optional lists)
    node_os_info: Optional[NodeOsInfo] = Field(None, alias="nodeOsInfo")
    node_variable_info: Optional[List[NodeVariableInfo]] = Field(None, alias="nodeVariableInfo")


class ScopeInfo(BaseModel):
    """Scope information."""
    facility_id: str = Field(alias="facilityId")
    facility_name: str = Field(alias="facilityName")
    description: Optional[str] = None
    icon_image: Optional[str] = Field(None, alias="iconImage")
    owner_role_id: str = Field(alias="ownerRoleId")
    
    class Config:
        populate_by_name = True


class GetNodeListRequest(BaseModel):
    """Request for getting node list."""
    parent_facility_id: Optional[str] = Field(None, alias="parentFacilityId")
    node_config_filter_is_and: Optional[bool] = Field(True, alias="nodeConfigFilterIsAnd")
    node_config_target_datetime: Optional[str] = Field(None, alias="nodeConfigTargetDatetime")


class GetNodeListResponse(BaseModel):
    """Response for getting node list."""
    total: int
    node_info_list: List[NodeInfo] = Field(alias="nodeInfoList")


class AddNodeRequest(NodeInfo):
    """Request for adding a node."""
    
    class Config:
        populate_by_name = True


class ModifyNodeRequest(BaseModel):
    """Request for modifying a node."""
    facility_name: Optional[str] = Field(None, alias="facilityName")
    description: Optional[str] = None
    valid: Optional[bool] = None
    
    # Include other fields from NodeInfo except facilityId and ownerRoleId
    auto_device_search: Optional[bool] = Field(None, alias="autoDeviceSearch")
    administrator: Optional[str] = None
    contact: Optional[str] = None
    hardware_type: Optional[str] = Field(None, alias="hardwareType")
    node_name: Optional[str] = Field(None, alias="nodeName")
    platform_family: Optional[str] = Field(None, alias="platformFamily")
    sub_platform_family: Optional[str] = Field(None, alias="subPlatformFamily")
    
    ip_address_v4: Optional[str] = Field(None, alias="ipAddressV4")
    ip_address_v6: Optional[str] = Field(None, alias="ipAddressV6")
    ip_address_version: Optional[IpAddressVersion] = Field(None, alias="ipAddressVersion")
    
    snmp_community: Optional[str] = Field(None, alias="snmpCommunity")
    snmp_port: Optional[int] = Field(None, alias="snmpPort")
    snmp_version: Optional[SnmpVersion] = Field(None, alias="snmpVersion")
    
    class Config:
        populate_by_name = True


class AddScopeRequest(BaseModel):
    """Request for adding a scope."""
    parent_facility_id: Optional[str] = Field(None, alias="parentFacilityId")
    scope_info: ScopeInfo = Field(alias="scopeInfo")
    
    class Config:
        populate_by_name = True


class ModifyScopeRequest(BaseModel):
    """Request for modifying a scope."""
    facility_name: Optional[str] = Field(None, alias="facilityName")
    description: Optional[str] = None
    icon_image: Optional[str] = Field(None, alias="iconImage")
    
    class Config:
        populate_by_name = True


class FacilityTreeResponse(BaseModel):
    """Response for facility tree."""
    data: FacilityInfo


class AgentStatusInfo(BaseModel):
    """Agent status information."""
    facility_id: str = Field(alias="facilityId")
    startup_time: Optional[int] = Field(None, alias="startupTime")
    last_login: Optional[int] = Field(None, alias="lastLogin")
    multiplicity: Optional[int] = None
    awake_port: Optional[int] = Field(None, alias="awakePort")


class AgentStatusResponse(BaseModel):
    """Response for agent status."""
    agent_status_list: List[AgentStatusInfo] = Field(alias="agentStatusList")


# Authentication models
class HinemosToken(BaseModel):
    """Hinemos authentication token."""
    token_id: str = Field(alias="tokenId")
    expiration_date: str = Field(alias="expirationDate")
    valid_term_minutes: Optional[int] = Field(None, alias="validTermMinites")


class ManagerInfo(BaseModel):
    """Manager information."""
    version: Optional[str] = None
    build_date: Optional[str] = Field(None, alias="buildDate")


class LoginRequest(BaseModel):
    """Login request."""
    user_id: str = Field(alias="userId")
    password: str
    
    class Config:
        populate_by_name = True


class LoginResponse(BaseModel):
    """Login response."""
    token: HinemosToken
    manager_info: Optional[ManagerInfo] = Field(None, alias="managerInfo")