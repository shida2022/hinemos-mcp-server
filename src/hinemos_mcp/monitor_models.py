"""Hinemos Monitor API data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class MonitorTypeEnum(str, Enum):
    """監視タイプ列挙型."""
    TRUTH = "TRUTH"
    NUMERIC = "NUMERIC" 
    STRING = "STRING"
    TRAP = "TRAP"
    SCENARIO = "SCENARIO"
    BINARY = "BINARY"


class RunIntervalEnum(str, Enum):
    """実行間隔列挙型."""
    NONE = "NONE"
    SEC_30 = "SEC_30"
    MIN_01 = "MIN_01"
    MIN_05 = "MIN_05"
    MIN_10 = "MIN_10"
    MIN_30 = "MIN_30"
    MIN_60 = "MIN_60"
    
    @classmethod
    def _missing_(cls, value):
        """Handle values that don't match enum values."""
        # Handle numeric values for backward compatibility
        if isinstance(value, int):
            value_map = {
                0: cls.NONE,
                30: cls.SEC_30,
                60: cls.MIN_01,
                300: cls.MIN_05,
                600: cls.MIN_10,
                1800: cls.MIN_30,
                3600: cls.MIN_60
            }
            return value_map.get(value)
        return None
    
    def to_index(self) -> int:
        """Convert enum value to index for API requests."""
        index_map = {
            self.NONE: 0,
            self.SEC_30: 1,
            self.MIN_01: 2,
            self.MIN_05: 3,
            self.MIN_10: 4,
            self.MIN_30: 5,
            self.MIN_60: 6
        }
        return index_map.get(self, 3)  # Default to MIN_05
    
    def to_seconds(self) -> int:
        """Convert enum value to seconds for reference."""
        value_map = {
            self.NONE: 0,
            self.SEC_30: 30,
            self.MIN_01: 60,
            self.MIN_05: 300,
            self.MIN_10: 600,
            self.MIN_30: 1800,
            self.MIN_60: 3600
        }
        return value_map.get(self, 300)  # Default to 300 seconds


class PriorityEnum(str, Enum):
    """重要度列挙型."""
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"
    WARNING = "WARNING"
    INFO = "INFO"
    NONE = "NONE"


class ConvertFlagEnum(str, Enum):
    """差分取得フラグ列挙型."""
    NONE = "NONE"
    DELTA = "DELTA"


class MonitorNumericTypeEnum(str, Enum):
    """監視数値タイプ列挙型."""
    BASIC = "BASIC"
    PREDICTION = "PREDICTION"
    CHANGE = "CHANGE"


class PredictionMethodEnum(str, Enum):
    """予測手法列挙型."""
    POLYNOMIAL_1 = "POLYNOMIAL_1"
    POLYNOMIAL_2 = "POLYNOMIAL_2"
    POLYNOMIAL_3 = "POLYNOMIAL_3"


class NotifyTypeEnum(str, Enum):
    """通知タイプ列挙型."""
    STATUS = "STATUS"
    EVENT = "EVENT"
    MAIL = "MAIL"
    JOB = "JOB"
    LOG = "LOG"
    COMMAND = "COMMAND"
    INFRA = "INFRA"
    REST = "REST"


class PriorityChangeJudgmentTypeEnum(str, Enum):
    """重要度変化判定タイプ列挙型."""
    NOT_PRIORITY_CHANGE = "NOT_PRIORITY_CHANGE"
    ACROSS_MONITOR_DETAIL_ID = "ACROSS_MONITOR_DETAIL_ID"


class PriorityChangeFailureTypeEnum(str, Enum):
    """取得失敗による重要度変化タイプ列挙型."""
    NOT_PRIORITY_CHANGE = "NOT_PRIORITY_CHANGE"
    PRIORITY_CHANGE = "PRIORITY_CHANGE"


# 通知関連モデル
class NotifyRelationInfoRequest(BaseModel):
    """通知関連情報リクエスト."""
    notify_id: str = Field(alias="notifyId")

    class Config:
        populate_by_name = True


class NotifyRelationInfoResponse(BaseModel):
    """通知関連情報レスポンス."""
    notify_id: str = Field(alias="notifyId")
    notify_type: Optional[NotifyTypeEnum] = Field(None, alias="notifyType")

    class Config:
        populate_by_name = True


# 数値監視判定情報
class MonitorNumericValueInfoRequest(BaseModel):
    """数値監視判定情報リクエスト."""
    monitor_numeric_type: Optional[MonitorNumericTypeEnum] = Field(None, alias="monitorNumericType")
    priority: PriorityEnum
    threshold_lower_limit: Optional[float] = Field(None, alias="thresholdLowerLimit")
    threshold_upper_limit: Optional[float] = Field(None, alias="thresholdUpperLimit")
    message: Optional[str] = None

    def model_dump(self, by_alias: bool = True, exclude_none: bool = True, **kwargs):
        """Override model_dump to handle MonitorNumericTypeEnum.BASIC as empty string."""
        data = super().model_dump(by_alias=by_alias, exclude_none=exclude_none, **kwargs)
        
        # Convert BASIC enum to empty string for API compatibility
        if by_alias and 'monitorNumericType' in data:
            if data['monitorNumericType'] == MonitorNumericTypeEnum.BASIC.value:
                data['monitorNumericType'] = ""
        elif not by_alias and 'monitor_numeric_type' in data:
            if data['monitor_numeric_type'] == MonitorNumericTypeEnum.BASIC.value:
                data['monitor_numeric_type'] = ""
        
        return data

    class Config:
        populate_by_name = True


class MonitorNumericValueInfoResponse(BaseModel):
    """数値監視判定情報レスポンス."""
    priority: PriorityEnum
    threshold_lower_limit: Optional[float] = Field(None, alias="thresholdLowerLimit")
    threshold_upper_limit: Optional[float] = Field(None, alias="thresholdUpperLimit")
    message: Optional[str] = None

    class Config:
        populate_by_name = True


# 文字列監視判定情報
class MonitorStringValueInfoRequest(BaseModel):
    """文字列監視判定情報リクエスト."""
    order_no: int = Field(alias="orderNo")
    priority: PriorityEnum
    pattern: str
    message: Optional[str] = None
    description: Optional[str] = None
    case_sensitivity_flg: bool = Field(True, alias="caseSensitivityFlg")
    process_type: bool = Field(True, alias="processType")
    valid_flg: bool = Field(True, alias="validFlg")

    class Config:
        populate_by_name = True


class MonitorStringValueInfoResponse(BaseModel):
    """文字列監視判定情報レスポンス."""
    order_no: int = Field(alias="orderNo")
    priority: PriorityEnum
    pattern: str
    message: Optional[str] = None
    description: Optional[str] = None
    case_sensitivity_flg: bool = Field(True, alias="caseSensitivityFlg")
    process_type: bool = Field(True, alias="processType")
    valid_flg: bool = Field(True, alias="validFlg")

    class Config:
        populate_by_name = True


# 基底リクエスト・レスポンスクラス
class AbstractMonitorRequest(BaseModel):
    """監視設定リクエスト基底クラス."""
    application: str = "Hinemos"
    description: Optional[str] = None
    monitor_flg: bool = Field(True, alias="monitorFlg")
    run_interval: RunIntervalEnum = Field(RunIntervalEnum.MIN_05, alias="runInterval")
    calendar_id: Optional[str] = Field(None, alias="calendarId")
    facility_id: str = Field(alias="facilityId")
    notify_relation_list: List[NotifyRelationInfoRequest] = Field(
        default_factory=list, alias="notifyRelationList"
    )
    
    def model_dump(self, by_alias: bool = True, exclude_none: bool = True, **kwargs):
        """Override model_dump to keep RunIntervalEnum as string value."""
        data = super().model_dump(by_alias=by_alias, exclude_none=exclude_none, **kwargs)
        
        # Keep runInterval as string value (not index) based on successful server logs
        # The server expects string values like "MIN_05", not numeric indices
        
        return data

    class Config:
        populate_by_name = True


class AbstractAddMonitorRequest(AbstractMonitorRequest):
    """監視設定追加リクエスト基底クラス."""
    monitor_id: str = Field(alias="monitorId")
    owner_role_id: str = Field("ADMINISTRATORS", alias="ownerRoleId")

    class Config:
        populate_by_name = True


class AbstractModifyMonitorRequest(BaseModel):
    """監視設定更新リクエスト基底クラス."""
    application: Optional[str] = None
    description: Optional[str] = None
    monitor_flg: Optional[bool] = Field(None, alias="monitorFlg")
    run_interval: Optional[RunIntervalEnum] = Field(None, alias="runInterval")
    calendar_id: Optional[str] = Field(None, alias="calendarId")
    facility_id: Optional[str] = Field(None, alias="facilityId")
    notify_relation_list: Optional[List[NotifyRelationInfoRequest]] = Field(
        None, alias="notifyRelationList"
    )
    
    class Config:
        populate_by_name = True


class AbstractMonitorResponse(BaseModel):
    """監視設定レスポンス基底クラス."""
    monitor_id: str = Field(alias="monitorId")
    monitor_type: Optional[MonitorTypeEnum] = Field(None, alias="monitorType")
    monitor_type_id: Optional[str] = Field(None, alias="monitorTypeId")
    application: Optional[str] = None
    description: Optional[str] = None
    monitor_flg: Optional[bool] = Field(None, alias="monitorFlg")
    run_interval: Optional[RunIntervalEnum] = Field(None, alias="runInterval")
    calendar_id: Optional[str] = Field(None, alias="calendarId")
    facility_id: Optional[str] = Field(None, alias="facilityId")
    scope: Optional[str] = None
    notify_relation_list: List[NotifyRelationInfoResponse] = Field(
        default_factory=list, alias="notifyRelationList"
    )
    owner_role_id: Optional[str] = Field(None, alias="ownerRoleId")
    reg_date: Optional[str] = Field(None, alias="regDate")
    reg_user: Optional[str] = Field(None, alias="regUser")
    update_date: Optional[str] = Field(None, alias="updateDate")
    update_user: Optional[str] = Field(None, alias="updateUser")
    sdml_monitor_type_id: Optional[str] = Field(None, alias="sdmlMonitorTypeId")

    class Config:
        populate_by_name = True


# 数値監視基底クラス
class AbstractAddNumericMonitorRequest(AbstractAddMonitorRequest):
    """数値監視追加リクエスト基底クラス."""
    collector_flg: bool = Field(True, alias="collectorFlg")
    item_name: str = Field("取得値", alias="itemName")
    measure: str = "収集値単位"
    prediction_flg: bool = Field(True, alias="predictionFlg")
    prediction_method: PredictionMethodEnum = Field(PredictionMethodEnum.POLYNOMIAL_1, alias="predictionMethod")
    prediction_analysys_range: int = Field(60, alias="predictionAnalysysRange")
    prediction_target: int = Field(60, alias="predictionTarget")
    prediction_application: str = Field("Hinemos", alias="predictionApplication")
    change_flg: bool = Field(False, alias="changeFlg")
    change_analysys_range: int = Field(60, alias="changeAnalysysRange")
    change_application: Optional[str] = Field(None, alias="changeApplication")
    numeric_value_info: List[MonitorNumericValueInfoRequest] = Field(
        default_factory=list, alias="numericValueInfo"
    )
    failure_priority: PriorityEnum = Field(PriorityEnum.UNKNOWN, alias="failurePriority")
    prediction_notify_relation_list: List[NotifyRelationInfoRequest] = Field(
        default_factory=list, alias="predictionNotifyRelationList"
    )
    change_notify_relation_list: List[NotifyRelationInfoRequest] = Field(
        default_factory=list, alias="changeNotifyRelationList"
    )

    class Config:
        populate_by_name = True


class AbstractModifyNumericMonitorRequest(AbstractModifyMonitorRequest):
    """数値監視更新リクエスト基底クラス."""
    collector_flg: Optional[bool] = Field(None, alias="collectorFlg")
    item_name: Optional[str] = Field(None, alias="itemName")
    measure: Optional[str] = None
    prediction_flg: Optional[bool] = Field(None, alias="predictionFlg")
    prediction_method: Optional[PredictionMethodEnum] = Field(None, alias="predictionMethod")
    prediction_analysys_range: Optional[int] = Field(None, alias="predictionAnalysysRange")
    prediction_target: Optional[int] = Field(None, alias="predictionTarget")
    prediction_application: Optional[str] = Field(None, alias="predictionApplication")
    change_flg: Optional[bool] = Field(None, alias="changeFlg")
    change_analysys_range: Optional[int] = Field(None, alias="changeAnalysysRange")
    change_application: Optional[str] = Field(None, alias="changeApplication")
    numeric_value_info: Optional[List[MonitorNumericValueInfoRequest]] = Field(
        None, alias="numericValueInfo"
    )
    prediction_notify_relation_list: Optional[List[NotifyRelationInfoRequest]] = Field(
        None, alias="predictionNotifyRelationList"
    )
    change_notify_relation_list: Optional[List[NotifyRelationInfoRequest]] = Field(
        None, alias="changeNotifyRelationList"
    )

    class Config:
        populate_by_name = True


class AbstractNumericMonitorResponse(AbstractMonitorResponse):
    """数値監視レスポンス基底クラス."""
    collector_flg: Optional[bool] = Field(None, alias="collectorFlg")
    item_name: Optional[str] = Field(None, alias="itemName")
    measure: Optional[str] = None
    prediction_flg: Optional[bool] = Field(None, alias="predictionFlg")
    prediction_method: Optional[PredictionMethodEnum] = Field(None, alias="predictionMethod")
    prediction_analysys_range: Optional[int] = Field(None, alias="predictionAnalysysRange")
    prediction_target: Optional[int] = Field(None, alias="predictionTarget")
    prediction_application: Optional[str] = Field(None, alias="predictionApplication")
    change_flg: Optional[bool] = Field(None, alias="changeFlg")
    change_analysys_range: Optional[int] = Field(None, alias="changeAnalysysRange")
    change_application: Optional[str] = Field(None, alias="changeApplication")
    numeric_value_info: List[MonitorNumericValueInfoResponse] = Field(
        default_factory=list, alias="numericValueInfo"
    )
    prediction_notify_relation_list: List[NotifyRelationInfoResponse] = Field(
        default_factory=list, alias="predictionNotifyRelationList"
    )
    change_notify_relation_list: List[NotifyRelationInfoResponse] = Field(
        default_factory=list, alias="changeNotifyRelationList"
    )

    class Config:
        populate_by_name = True


# 文字列監視基底クラス
class AbstractAddStringMonitorRequest(AbstractAddMonitorRequest):
    """文字列監視追加リクエスト基底クラス."""
    collector_flg: bool = Field(False, alias="collectorFlg")
    log_format_id: Optional[str] = Field(None, alias="logFormatId")
    string_value_info: List[MonitorStringValueInfoRequest] = Field(
        default_factory=list, alias="stringValueInfo"
    )
    priority_change_judgment_type: PriorityChangeJudgmentTypeEnum = Field(
        PriorityChangeJudgmentTypeEnum.NOT_PRIORITY_CHANGE, alias="priorityChangeJudgmentType"
    )

    class Config:
        populate_by_name = True


class AbstractModifyStringMonitorRequest(AbstractModifyMonitorRequest):
    """文字列監視更新リクエスト基底クラス."""
    collector_flg: Optional[bool] = Field(None, alias="collectorFlg")
    log_format_id: Optional[str] = Field(None, alias="logFormatId")
    string_value_info: Optional[List[MonitorStringValueInfoRequest]] = Field(
        None, alias="stringValueInfo"
    )
    priority_change_judgment_type: Optional[PriorityChangeJudgmentTypeEnum] = Field(
        None, alias="priorityChangeJudgmentType"
    )

    class Config:
        populate_by_name = True


class AbstractStringMonitorResponse(AbstractMonitorResponse):
    """文字列監視レスポンス基底クラス."""
    collector_flg: Optional[bool] = Field(None, alias="collectorFlg")
    log_format_id: Optional[str] = Field(None, alias="logFormatId")
    string_value_info: List[MonitorStringValueInfoResponse] = Field(
        default_factory=list, alias="stringValueInfo"
    )
    priority_change_judgment_type: Optional[PriorityChangeJudgmentTypeEnum] = Field(
        None, alias="priorityChangeJudgmentType"
    )

    class Config:
        populate_by_name = True


# 監視項目固有の設定クラス
class PingCheckInfoRequest(BaseModel):
    """Ping監視設定リクエスト."""
    run_count: int = Field(1, alias="runCount")
    run_interval: int = Field(1000, alias="runInterval")
    timeout: int = Field(5000, alias="timeout")

    class Config:
        populate_by_name = True


class PingCheckInfoResponse(BaseModel):
    """Ping監視設定レスポンス."""
    run_count: Optional[int] = Field(None, alias="runCount")
    run_interval: Optional[int] = Field(None, alias="runInterval")
    timeout: Optional[int] = Field(None, alias="timeout")

    class Config:
        populate_by_name = True


class HttpCheckInfoRequest(BaseModel):
    """HTTP監視設定リクエスト."""
    request_url: str = Field(alias="requestUrl")
    timeout: int = Field(10000, alias="timeout")
    user_agent: Optional[str] = Field(None, alias="userAgent")
    connect_timeout: Optional[int] = Field(None, alias="connectTimeout")
    request_method: Optional[str] = Field("GET", alias="requestMethod")
    post_data: Optional[str] = Field(None, alias="postData")
    auth_type: Optional[str] = Field(None, alias="authType")
    auth_user: Optional[str] = Field(None, alias="authUser")
    auth_password: Optional[str] = Field(None, alias="authPassword")
    proxy_flg: bool = Field(False, alias="proxyFlg")
    proxy_url: Optional[str] = Field(None, alias="proxyUrl")
    proxy_port: Optional[int] = Field(None, alias="proxyPort")
    proxy_user: Optional[str] = Field(None, alias="proxyUser")
    proxy_password: Optional[str] = Field(None, alias="proxyPassword")

    class Config:
        populate_by_name = True


class HttpCheckInfoResponse(BaseModel):
    """HTTP監視設定レスポンス."""
    request_url: Optional[str] = Field(None, alias="requestUrl")
    timeout: Optional[int] = Field(None, alias="timeout")
    user_agent: Optional[str] = Field(None, alias="userAgent")
    connect_timeout: Optional[int] = Field(None, alias="connectTimeout")
    request_method: Optional[str] = Field(None, alias="requestMethod")
    post_data: Optional[str] = Field(None, alias="postData")
    auth_type: Optional[str] = Field(None, alias="authType")
    auth_user: Optional[str] = Field(None, alias="authUser")
    auth_password: Optional[str] = Field(None, alias="authPassword")
    proxy_flg: Optional[bool] = Field(None, alias="proxyFlg")
    proxy_url: Optional[str] = Field(None, alias="proxyUrl")
    proxy_port: Optional[int] = Field(None, alias="proxyPort")
    proxy_user: Optional[str] = Field(None, alias="proxyUser")
    proxy_password: Optional[str] = Field(None, alias="proxyPassword")

    class Config:
        populate_by_name = True


class SnmpCheckInfoRequest(BaseModel):
    """SNMP監視設定リクエスト."""
    snmp_oid: str = Field(alias="snmpOid")
    convert_flg: ConvertFlagEnum = Field(ConvertFlagEnum.NONE, alias="convertFlg")

    class Config:
        populate_by_name = True


class SnmpCheckInfoResponse(BaseModel):
    """SNMP監視設定レスポンス."""
    snmp_oid: Optional[str] = Field(None, alias="snmpOid")
    convert_flg: Optional[ConvertFlagEnum] = Field(None, alias="convertFlg")

    class Config:
        populate_by_name = True


class LogfileCheckInfoRequest(BaseModel):
    """ログファイル監視設定リクエスト."""
    directory: str
    file_name: str = Field(alias="fileName")
    file_encoding: str = Field("UTF-8", alias="fileEncoding")
    file_return_code: str = Field("LF", alias="fileReturnCode")
    pattern_head: Optional[str] = Field(None, alias="patternHead")
    pattern_tail: Optional[str] = Field(None, alias="patternTail")
    max_bytes: int = Field(131072, alias="maxBytes")

    class Config:
        populate_by_name = True


class LogfileCheckInfoResponse(BaseModel):
    """ログファイル監視設定レスポンス."""
    directory: Optional[str] = None
    file_name: Optional[str] = Field(None, alias="fileName")
    file_encoding: Optional[str] = Field(None, alias="fileEncoding")
    file_return_code: Optional[str] = Field(None, alias="fileReturnCode")
    pattern_head: Optional[str] = Field(None, alias="patternHead")
    pattern_tail: Optional[str] = Field(None, alias="patternTail")
    max_bytes: Optional[int] = Field(None, alias="maxBytes")

    class Config:
        populate_by_name = True


class SqlCheckInfoRequest(BaseModel):
    """SQL監視設定リクエスト."""
    connection_url: str = Field(alias="connectionUrl")
    user: str
    password: str
    jdbc_driver: str = Field(alias="jdbcDriver")
    query: str
    timeout: int = Field(5000, alias="timeout")

    class Config:
        populate_by_name = True


class SqlCheckInfoResponse(BaseModel):
    """SQL監視設定レスポンス."""
    connection_url: Optional[str] = Field(None, alias="connectionUrl")
    user: Optional[str] = None
    password: Optional[str] = None
    jdbc_driver: Optional[str] = Field(None, alias="jdbcDriver")
    sql: Optional[str] = None
    timeout: Optional[int] = Field(None, alias="timeout")

    class Config:
        populate_by_name = True


class JmxCheckInfoRequest(BaseModel):
    """JMX監視設定リクエスト."""
    port: int
    auth_user: Optional[str] = Field(None, alias="authUser")
    auth_password: Optional[str] = Field(None, alias="authPassword")
    url: Optional[str] = None
    convert_flg: ConvertFlagEnum = Field(ConvertFlagEnum.NONE, alias="convertFlg")
    master_id: str = Field("JMX_MEMORY_HEAP_COMMITTED", alias="masterId")
    url_format_name: str = Field("Default", alias="urlFormatName")

    class Config:
        populate_by_name = True


class JmxCheckInfoResponse(BaseModel):
    """JMX監視設定レスポンス."""
    port: Optional[int] = None
    auth_user: Optional[str] = Field(None, alias="authUser")
    auth_password: Optional[str] = Field(None, alias="authPassword")
    url: Optional[str] = None
    convert_flg: Optional[ConvertFlagEnum] = Field(None, alias="convertFlg")

    class Config:
        populate_by_name = True


class ProcessCheckInfoRequest(BaseModel):
    """プロセス監視設定リクエスト."""
    param: str
    case_sensitivity_flg: bool = Field(True, alias="caseSensitivityFlg")
    command: str = "ps"

    class Config:
        populate_by_name = True


class ProcessCheckInfoResponse(BaseModel):
    """プロセス監視設定レスポンス."""
    param: Optional[str] = None
    case_sensitivity_flg: Optional[bool] = Field(None, alias="caseSensitivityFlg")

    class Config:
        populate_by_name = True


class PortCheckInfoRequest(BaseModel):
    """ポート監視設定リクエスト."""
    port_no: int = Field(alias="portNo")
    service_id: Optional[str] = Field(None, alias="serviceId")
    timeout: int = Field(5000, alias="timeout")
    run_count: int = Field(1, alias="runCount")
    run_interval: int = Field(1000, alias="runInterval")

    class Config:
        populate_by_name = True


class PortCheckInfoResponse(BaseModel):
    """ポート監視設定レスポンス."""
    port_no: Optional[int] = Field(None, alias="portNo")
    service_id: Optional[str] = Field(None, alias="serviceId")
    timeout: Optional[int] = Field(None, alias="timeout")

    class Config:
        populate_by_name = True


class WinEventCheckInfoRequest(BaseModel):
    """Windowsイベント監視設定リクエスト."""
    log_name: str = Field(alias="logName")
    source: Optional[str] = None
    level: Optional[int] = None
    keywords: Optional[str] = None

    class Config:
        populate_by_name = True


class WinEventCheckInfoResponse(BaseModel):
    """Windowsイベント監視設定レスポンス."""
    log_name: Optional[str] = Field(None, alias="logName")
    source: Optional[str] = None
    level: Optional[int] = None
    keywords: Optional[str] = None

    class Config:
        populate_by_name = True


class CustomCheckInfoRequest(BaseModel):
    """カスタム監視設定リクエスト."""
    command: str
    timeout: int = Field(30000, alias="timeout")
    spec_flg: bool = Field(False, alias="specFlg")
    convert_flg: ConvertFlagEnum = Field(ConvertFlagEnum.NONE, alias="convertFlg")

    class Config:
        populate_by_name = True


class CustomCheckInfoResponse(BaseModel):
    """カスタム監視設定レスポンス."""
    command: Optional[str] = None
    timeout: Optional[int] = Field(None, alias="timeout")
    spec_flg: Optional[bool] = Field(None, alias="specFlg")
    convert_flg: Optional[ConvertFlagEnum] = Field(None, alias="convertFlg")

    class Config:
        populate_by_name = True


# 具象監視設定クラス
class AddPingMonitorRequest(AbstractAddNumericMonitorRequest):
    """Ping監視追加リクエスト."""
    ping_check_info: PingCheckInfoRequest = Field(alias="pingCheckInfo")

    class Config:
        populate_by_name = True


class ModifyPingMonitorRequest(AbstractModifyNumericMonitorRequest):
    """Ping監視更新リクエスト."""
    ping_check_info: Optional[PingCheckInfoRequest] = Field(None, alias="pingCheckInfo")

    class Config:
        populate_by_name = True


class PingMonitorResponse(AbstractNumericMonitorResponse):
    """Ping監視レスポンス."""
    ping_check_info: Optional[PingCheckInfoResponse] = Field(None, alias="pingCheckInfo")

    class Config:
        populate_by_name = True


class AddHttpNumericMonitorRequest(AbstractAddNumericMonitorRequest):
    """HTTP数値監視追加リクエスト."""
    http_check_info: HttpCheckInfoRequest = Field(alias="httpCheckInfo")

    class Config:
        populate_by_name = True


class ModifyHttpNumericMonitorRequest(AbstractModifyNumericMonitorRequest):
    """HTTP数値監視更新リクエスト."""
    http_check_info: Optional[HttpCheckInfoRequest] = Field(None, alias="httpCheckInfo")

    class Config:
        populate_by_name = True


class HttpNumericMonitorResponse(AbstractNumericMonitorResponse):
    """HTTP数値監視レスポンス."""
    http_check_info: Optional[HttpCheckInfoResponse] = Field(None, alias="httpCheckInfo")

    class Config:
        populate_by_name = True


class AddHttpStringMonitorRequest(AbstractAddStringMonitorRequest):
    """HTTP文字列監視追加リクエスト."""
    http_check_info: HttpCheckInfoRequest = Field(alias="httpCheckInfo")
    priority_change_failure_type: PriorityChangeFailureTypeEnum = Field(
        PriorityChangeFailureTypeEnum.NOT_PRIORITY_CHANGE, alias="priorityChangeFailureType"
    )

    class Config:
        populate_by_name = True


class ModifyHttpStringMonitorRequest(AbstractModifyStringMonitorRequest):
    """HTTP文字列監視更新リクエスト."""
    http_check_info: Optional[HttpCheckInfoRequest] = Field(None, alias="httpCheckInfo")
    priority_change_failure_type: Optional[PriorityChangeFailureTypeEnum] = Field(
        None, alias="priorityChangeFailureType"
    )

    class Config:
        populate_by_name = True


class HttpStringMonitorResponse(AbstractStringMonitorResponse):
    """HTTP文字列監視レスポンス."""
    http_check_info: Optional[HttpCheckInfoResponse] = Field(None, alias="httpCheckInfo")
    priority_change_failure_type: Optional[PriorityChangeFailureTypeEnum] = Field(
        None, alias="priorityChangeFailureType"
    )

    class Config:
        populate_by_name = True


class AddSnmpNumericMonitorRequest(AbstractAddNumericMonitorRequest):
    """SNMP数値監視追加リクエスト."""
    snmp_check_info: SnmpCheckInfoRequest = Field(alias="snmpCheckInfo")

    class Config:
        populate_by_name = True


class ModifySnmpNumericMonitorRequest(AbstractModifyNumericMonitorRequest):
    """SNMP数値監視更新リクエスト."""
    snmp_check_info: Optional[SnmpCheckInfoRequest] = Field(None, alias="snmpCheckInfo")

    class Config:
        populate_by_name = True


class SnmpNumericMonitorResponse(AbstractNumericMonitorResponse):
    """SNMP数値監視レスポンス."""
    snmp_check_info: Optional[SnmpCheckInfoResponse] = Field(None, alias="snmpCheckInfo")

    class Config:
        populate_by_name = True


class AddLogfileMonitorRequest(AbstractAddStringMonitorRequest):
    """ログファイル監視追加リクエスト."""
    logfile_check_info: LogfileCheckInfoRequest = Field(alias="logfileCheckInfo")

    class Config:
        populate_by_name = True


class ModifyLogfileMonitorRequest(AbstractModifyStringMonitorRequest):
    """ログファイル監視更新リクエスト."""
    logfile_check_info: Optional[LogfileCheckInfoRequest] = Field(None, alias="logfileCheckInfo")

    class Config:
        populate_by_name = True


class LogfileMonitorResponse(AbstractStringMonitorResponse):
    """ログファイル監視レスポンス."""
    logfile_check_info: Optional[LogfileCheckInfoResponse] = Field(None, alias="logfileCheckInfo")

    class Config:
        populate_by_name = True


class AddSqlMonitorRequest(AbstractAddNumericMonitorRequest):
    """SQL監視追加リクエスト."""
    sql_check_info: SqlCheckInfoRequest = Field(alias="sqlCheckInfo")

    class Config:
        populate_by_name = True


class ModifySqlMonitorRequest(AbstractModifyNumericMonitorRequest):
    """SQL監視更新リクエスト."""
    sql_check_info: Optional[SqlCheckInfoRequest] = Field(None, alias="sqlCheckInfo")

    class Config:
        populate_by_name = True


class SqlMonitorResponse(AbstractNumericMonitorResponse):
    """SQL監視レスポンス."""
    sql_check_info: Optional[SqlCheckInfoResponse] = Field(None, alias="sqlCheckInfo")

    class Config:
        populate_by_name = True


class AddJmxMonitorRequest(AbstractAddNumericMonitorRequest):
    """JMX監視追加リクエスト."""
    jmx_check_info: JmxCheckInfoRequest = Field(alias="jmxCheckInfo")

    class Config:
        populate_by_name = True


class ModifyJmxMonitorRequest(AbstractModifyNumericMonitorRequest):
    """JMX監視更新リクエスト."""
    jmx_check_info: Optional[JmxCheckInfoRequest] = Field(None, alias="jmxCheckInfo")

    class Config:
        populate_by_name = True


class JmxMonitorResponse(AbstractNumericMonitorResponse):
    """JMX監視レスポンス."""
    jmx_check_info: Optional[JmxCheckInfoResponse] = Field(None, alias="jmxCheckInfo")

    class Config:
        populate_by_name = True


class AddProcessMonitorRequest(AbstractAddNumericMonitorRequest):
    """プロセス監視追加リクエスト."""
    process_check_info: ProcessCheckInfoRequest = Field(alias="processCheckInfo")

    class Config:
        populate_by_name = True


class ModifyProcessMonitorRequest(AbstractModifyNumericMonitorRequest):
    """プロセス監視更新リクエスト."""
    process_check_info: Optional[ProcessCheckInfoRequest] = Field(None, alias="processCheckInfo")

    class Config:
        populate_by_name = True


class ProcessMonitorResponse(AbstractNumericMonitorResponse):
    """プロセス監視レスポンス."""
    process_check_info: Optional[ProcessCheckInfoResponse] = Field(None, alias="processCheckInfo")

    class Config:
        populate_by_name = True


class AddPortMonitorRequest(AbstractAddNumericMonitorRequest):
    """ポート監視追加リクエスト."""
    port_check_info: PortCheckInfoRequest = Field(alias="portCheckInfo")

    class Config:
        populate_by_name = True


class ModifyPortMonitorRequest(AbstractModifyNumericMonitorRequest):
    """ポート監視更新リクエスト."""
    port_check_info: Optional[PortCheckInfoRequest] = Field(None, alias="portCheckInfo")

    class Config:
        populate_by_name = True


class PortMonitorResponse(AbstractNumericMonitorResponse):
    """ポート監視レスポンス."""
    port_check_info: Optional[PortCheckInfoResponse] = Field(None, alias="portCheckInfo")

    class Config:
        populate_by_name = True


class AddWinEventMonitorRequest(AbstractAddStringMonitorRequest):
    """Windowsイベント監視追加リクエスト."""
    winevent_check_info: WinEventCheckInfoRequest = Field(alias="wineventCheckInfo")

    class Config:
        populate_by_name = True


class ModifyWinEventMonitorRequest(AbstractModifyStringMonitorRequest):
    """Windowsイベント監視更新リクエスト."""
    winevent_check_info: Optional[WinEventCheckInfoRequest] = Field(None, alias="wineventCheckInfo")

    class Config:
        populate_by_name = True


class WinEventMonitorResponse(AbstractStringMonitorResponse):
    """Windowsイベント監視レスポンス."""
    winevent_check_info: Optional[WinEventCheckInfoResponse] = Field(None, alias="wineventCheckInfo")

    class Config:
        populate_by_name = True


class AddCustomMonitorRequest(AbstractAddNumericMonitorRequest):
    """カスタム監視追加リクエスト."""
    custom_check_info: CustomCheckInfoRequest = Field(alias="customCheckInfo")

    class Config:
        populate_by_name = True


class ModifyCustomMonitorRequest(AbstractModifyNumericMonitorRequest):
    """カスタム監視更新リクエスト."""
    custom_check_info: Optional[CustomCheckInfoRequest] = Field(None, alias="customCheckInfo")

    class Config:
        populate_by_name = True


class CustomMonitorResponse(AbstractNumericMonitorResponse):
    """カスタム監視レスポンス."""
    custom_check_info: Optional[CustomCheckInfoResponse] = Field(None, alias="customCheckInfo")

    class Config:
        populate_by_name = True


# 監視設定検索用
class GetMonitorListRequest(BaseModel):
    """監視設定検索リクエスト."""
    monitor_id: Optional[str] = Field(None, alias="monitorId")
    monitor_type_id: Optional[str] = Field(None, alias="monitorTypeId")
    description: Optional[str] = None
    calendar_id: Optional[str] = Field(None, alias="calendarId")
    facility_id: Optional[str] = Field(None, alias="facilityId")
    monitor_flg: Optional[bool] = Field(None, alias="monitorFlg")
    collector_flg: Optional[bool] = Field(None, alias="collectorFlg")
    owner_role_id: Optional[str] = Field(None, alias="ownerRoleId")

    class Config:
        populate_by_name = True


# 有効/無効設定用
class MonitorValidRequest(BaseModel):
    """監視有効/無効設定リクエスト."""
    monitor_ids: List[str] = Field(alias="monitorIds")
    valid_flg: bool = Field(alias="validFlg")

    class Config:
        populate_by_name = True


class CollectorValidRequest(BaseModel):
    """収集有効/無効設定リクエスト."""
    monitor_ids: List[str] = Field(alias="monitorIds")
    valid_flg: bool = Field(alias="validFlg")

    class Config:
        populate_by_name = True