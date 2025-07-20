"""Hinemos Monitor API wrapper with simplified interface."""

from typing import List, Optional, Dict, Any

from .client import HinemosClient
from .monitor_models import (
    AbstractMonitorResponse,
    AddPingMonitorRequest,
    AddHttpNumericMonitorRequest,
    AddHttpStringMonitorRequest,
    AddSnmpNumericMonitorRequest,
    AddLogfileMonitorRequest,
    ConvertFlagEnum,
    GetMonitorListRequest,
    HttpCheckInfoRequest,
    HttpNumericMonitorResponse,
    HttpStringMonitorResponse,
    LogfileCheckInfoRequest,
    LogfileMonitorResponse,
    ModifyPingMonitorRequest,
    ModifyHttpNumericMonitorRequest,
    ModifyHttpStringMonitorRequest,
    ModifySnmpNumericMonitorRequest,
    ModifyLogfileMonitorRequest,
    MonitorNumericTypeEnum,
    MonitorNumericValueInfoRequest,
    MonitorNumericValueInfoResponse,
    MonitorStringValueInfoRequest,
    NotifyRelationInfoRequest,
    NotifyRelationInfoResponse,
    PingCheckInfoRequest,
    PingMonitorResponse,
    PredictionMethodEnum,
    PriorityChangeFailureTypeEnum,
    PriorityEnum,
    RunIntervalEnum,
    SnmpCheckInfoRequest,
    SnmpNumericMonitorResponse,
)


class MonitorAPI:
    """High-level wrapper for Hinemos Monitor API."""
    
    def __init__(self, client: HinemosClient):
        """Initialize Monitor API wrapper.
        
        Args:
            client: Hinemos client instance
        """
        self.client = client
    
    @staticmethod
    def _convert_numeric_value_response_to_request(
        response_list: List[MonitorNumericValueInfoResponse]
    ) -> List[MonitorNumericValueInfoRequest]:
        """Convert MonitorNumericValueInfoResponse objects to MonitorNumericValueInfoRequest objects."""
        if not response_list:
            return []
            
        request_list = []
        for response in response_list:
            # Convert response data to request format
            request_data = {
                "priority": response.priority,
                "threshold_lower_limit": response.threshold_lower_limit,
                "threshold_upper_limit": response.threshold_upper_limit,
                "message": response.message
            }
            
            # Determine monitor_numeric_type based on threshold characteristics
            # From the successful ping monitor log pattern:
            # CHANGE type: Usually has negative lower limits or both limits same (like 0.0, 0.0)
            # BASIC type: Usually has large positive lower limits that may be > upper limits
            
            lower = response.threshold_lower_limit
            upper = response.threshold_upper_limit
            
            if (lower is not None and upper is not None):
                if (lower < 0) or (lower == 0.0 and upper == 0.0):
                    # Negative lower limit or both zero suggests CHANGE type
                    request_data["monitor_numeric_type"] = MonitorNumericTypeEnum.CHANGE
                elif (lower > upper and lower >= 1000.0):
                    # Large positive lower > upper suggests BASIC type (like 1000.0 > 1.0, 3000.0 > 51.0)
                    request_data["monitor_numeric_type"] = MonitorNumericTypeEnum.BASIC
                else:
                    # Default case - use BASIC
                    request_data["monitor_numeric_type"] = MonitorNumericTypeEnum.BASIC
            else:
                # Default when limits are None
                request_data["monitor_numeric_type"] = MonitorNumericTypeEnum.BASIC
            
            request_list.append(MonitorNumericValueInfoRequest(**request_data))
        
        return request_list
    
    @staticmethod
    def _convert_notify_relation_response_to_request(
        response_list: List[NotifyRelationInfoResponse]
    ) -> List[NotifyRelationInfoRequest]:
        """Convert NotifyRelationInfoResponse objects to NotifyRelationInfoRequest objects."""
        if not response_list:
            return []
            
        return [
            NotifyRelationInfoRequest(notify_id=response.notify_id)
            for response in response_list
        ]
    
    @staticmethod
    def _convert_string_value_response_to_request(
        response_list
    ) -> List[MonitorStringValueInfoRequest]:
        """Convert MonitorStringValueInfoResponse objects to MonitorStringValueInfoRequest objects."""
        if not response_list:
            return []
            
        return [
            MonitorStringValueInfoRequest(
                order_no=response.order_no,
                priority=response.priority,
                pattern=response.pattern,
                message=response.message,
                description=response.description,
                case_sensitivity_flg=response.case_sensitivity_flg,
                process_type=response.process_type,
                valid_flg=response.valid_flg
            )
            for response in response_list
        ]
    
    # General monitor operations
    
    def list_monitors(self, **filters) -> List[AbstractMonitorResponse]:
        """List monitors with optional filtering.
        
        Args:
            **filters: Filter parameters (monitor_id, monitor_type_id, facility_id, etc.)
            
        Returns:
            List of monitor information
        """
        if filters:
            request = GetMonitorListRequest(**filters)
            return self.client.get_monitor_list(request)
        else:
            return self.client.get_monitor_list()
    
    def get_monitor(self, monitor_id: str) -> AbstractMonitorResponse:
        """Get monitor information by ID.
        
        Args:
            monitor_id: Monitor ID
            
        Returns:
            Monitor information
        """
        return self.client.get_monitor(monitor_id)
    
    def delete_monitors(self, monitor_ids: List[str]) -> None:
        """Delete monitors.
        
        Args:
            monitor_ids: List of monitor IDs to delete
        """
        self.client.delete_monitors(monitor_ids)
    
    def enable_monitors(self, monitor_ids: List[str]) -> None:
        """Enable monitoring for specified monitors.
        
        Args:
            monitor_ids: List of monitor IDs to enable
        """
        if not monitor_ids:
            return  # Skip if no monitors to enable
        self.client.set_monitor_valid(monitor_ids, True)
    
    def disable_monitors(self, monitor_ids: List[str]) -> None:
        """Disable monitoring for specified monitors.
        
        Args:
            monitor_ids: List of monitor IDs to disable
        """
        if not monitor_ids:
            return  # Skip if no monitors to disable
        self.client.set_monitor_valid(monitor_ids, False)
    
    def enable_collectors(self, monitor_ids: List[str]) -> None:
        """Enable collection for specified monitors.
        
        Args:
            monitor_ids: List of monitor IDs to enable collection
        """
        if not monitor_ids:
            return  # Skip if no monitors to enable collection
        self.client.set_collector_valid(monitor_ids, True)
    
    def disable_collectors(self, monitor_ids: List[str]) -> None:
        """Disable collection for specified monitors.
        
        Note: Monitors with prediction enabled cannot have collection disabled.
        Such monitors will be skipped automatically.
        
        Args:
            monitor_ids: List of monitor IDs to disable collection
        """
        if not monitor_ids:
            return  # Skip if no monitors to disable collection
        
        # Filter out monitors that have prediction enabled to avoid server errors
        valid_monitor_ids = []
        for monitor_id in monitor_ids:
            try:
                monitor = self.get_monitor(monitor_id)
                # Check if monitor has prediction enabled
                if hasattr(monitor, 'prediction_flg') and monitor.prediction_flg:
                    # Skip monitors with prediction enabled
                    continue
                valid_monitor_ids.append(monitor_id)
            except Exception:
                # If we can't check the monitor, include it anyway
                valid_monitor_ids.append(monitor_id)
        
        if valid_monitor_ids:
            self.client.set_collector_valid(valid_monitor_ids, False)
    
    # Ping monitoring
    
    def create_ping_monitor(
        self,
        monitor_id: str,
        facility_id: str,
        description: str = "",
        run_interval: RunIntervalEnum = RunIntervalEnum.MIN_05,
        run_count: int = 1,
        timeout: int = 5000,
        thresholds: Optional[List[Dict[str, Any]]] = None,
        notify_ids: Optional[List[str]] = None,
        owner_role_id: str = "ADMINISTRATORS",
        **kwargs
    ) -> PingMonitorResponse:
        """Create a new ping monitor with simplified parameters.
        
        Args:
            monitor_id: Unique monitor ID
            facility_id: Target facility ID
            description: Monitor description
            run_interval: Monitoring interval
            run_count: Number of ping attempts
            timeout: Ping timeout in milliseconds
            thresholds: List of threshold configurations
            notify_ids: List of notification IDs
            owner_role_id: Owner role ID
            **kwargs: Additional monitor parameters
            
        Returns:
            Created ping monitor information
        """
        # Create ping check info
        ping_check_info = PingCheckInfoRequest(
            run_count=run_count,
            run_interval=1000,  # Internal ping interval
            timeout=timeout
        )
        
        # Create numeric value info for thresholds with default 8 entries like existing monitors
        numeric_value_info = []
        if thresholds:
            for threshold in thresholds:
                numeric_value_info.append(MonitorNumericValueInfoRequest(
                    monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
                    priority=PriorityEnum(threshold.get("priority", PriorityEnum.WARNING)),
                    threshold_lower_limit=threshold.get("lower_limit"),
                    threshold_upper_limit=threshold.get("upper_limit"),
                    message=threshold.get("message", "")
                ))
        else:
            # Create default 8 threshold entries based on successful server logs
            default_thresholds = [
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.INFO, threshold_lower_limit=-1.0, threshold_upper_limit=1.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.WARNING, threshold_lower_limit=-2.0, threshold_upper_limit=2.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.CRITICAL, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.UNKNOWN, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.INFO, threshold_lower_limit=1000.0, threshold_upper_limit=1.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.WARNING, threshold_lower_limit=3000.0, threshold_upper_limit=51.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.CRITICAL, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.UNKNOWN, threshold_lower_limit=0.0, threshold_upper_limit=0.0)
            ]
            numeric_value_info = default_thresholds
        
        # Create notification relations
        notify_relation_list = []
        if notify_ids:
            notify_relation_list = [
                NotifyRelationInfoRequest(notify_id=notify_id)
                for notify_id in notify_ids
            ]
        
        # Create monitor request
        monitor_request = AddPingMonitorRequest(
            monitor_id=monitor_id,
            facility_id=facility_id,
            description=description,
            run_interval=run_interval,
            owner_role_id=owner_role_id,
            notify_relation_list=notify_relation_list,
            numeric_value_info=numeric_value_info,
            ping_check_info=ping_check_info,
            item_name="Response Time",
            measure="msec",
            application=kwargs.get("application", "Hinemos"),
            prediction_flg=kwargs.get("prediction_flg", False),
            prediction_method=kwargs.get("prediction_method", PredictionMethodEnum.POLYNOMIAL_1),
            prediction_analysys_range=kwargs.get("prediction_analysys_range", 60),
            prediction_target=kwargs.get("prediction_target", 60),
            prediction_application=kwargs.get("prediction_application", "TEST"),
            change_flg=kwargs.get("change_flg", False),
            change_analysys_range=kwargs.get("change_analysys_range", 60),
            change_application=kwargs.get("change_application", "TEST"),
            **{k: v for k, v in kwargs.items() if k not in ["application", "prediction_flg", "prediction_method", "prediction_analysys_range", "prediction_target", "prediction_application", "change_flg", "change_analysys_range", "change_application"]}
        )
        
        return self.client.add_ping_monitor(monitor_request)
    
    def update_ping_monitor(
        self,
        monitor_id: str,
        description: Optional[str] = None,
        run_interval: Optional[RunIntervalEnum] = None,
        run_count: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> PingMonitorResponse:
        """Update an existing ping monitor.
        
        Args:
            monitor_id: Monitor ID to update
            description: New description
            run_interval: New monitoring interval
            run_count: New ping attempt count
            timeout: New ping timeout
            **kwargs: Additional monitor parameters
            
        Returns:
            Updated ping monitor information
        """
        # Get current monitor to preserve existing values and get facilityId
        current = self.client.get_ping_monitor_list()
        current_monitor = next((m for m in current if m.monitor_id == monitor_id), None)
        
        if not current_monitor:
            raise ValueError(f"Monitor with ID {monitor_id} not found")
        
        # Include all required fields from current monitor
        update_data = {
            "facility_id": current_monitor.facility_id,
            "collector_flg": current_monitor.collector_flg,
            "application": current_monitor.application,
            "item_name": current_monitor.item_name,
            "measure": current_monitor.measure,
            "prediction_flg": current_monitor.prediction_flg,
            "prediction_method": current_monitor.prediction_method,
            "prediction_target": current_monitor.prediction_target,
            "prediction_analysys_range": current_monitor.prediction_analysys_range,
            "prediction_application": current_monitor.prediction_application,
            "change_flg": current_monitor.change_flg,
            "change_analysys_range": current_monitor.change_analysys_range,
            "change_application": current_monitor.change_application,
            "numeric_value_info": self._convert_numeric_value_response_to_request(current_monitor.numeric_value_info),
            "prediction_notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.prediction_notify_relation_list),
            "change_notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.change_notify_relation_list),
            "notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.notify_relation_list)
        }
        
        if description is not None:
            update_data["description"] = description
        if run_interval is not None:
            update_data["run_interval"] = run_interval
        
        ping_check_info = None
        if run_count is not None or timeout is not None:
            ping_check_info = PingCheckInfoRequest(
                run_count=run_count if run_count is not None else (
                    current_monitor.ping_check_info.run_count if current_monitor.ping_check_info else 1
                ),
                run_interval=1000,
                timeout=timeout if timeout is not None else (
                    current_monitor.ping_check_info.timeout if current_monitor.ping_check_info else 5000
                )
            )
        
        if ping_check_info:
            update_data["ping_check_info"] = ping_check_info
        
        update_data.update(kwargs)
        
        modify_request = ModifyPingMonitorRequest(**update_data)
        return self.client.modify_ping_monitor(monitor_id, modify_request)
    
    def list_ping_monitors(self) -> List[PingMonitorResponse]:
        """List all ping monitors.
        
        Returns:
            List of ping monitor information
        """
        return self.client.get_ping_monitor_list()
    
    # HTTP monitoring
    
    def create_http_numeric_monitor(
        self,
        monitor_id: str,
        facility_id: str,
        url: str,
        description: str = "",
        run_interval: RunIntervalEnum = RunIntervalEnum.MIN_05,
        timeout: int = 10000,
        thresholds: Optional[List[Dict[str, Any]]] = None,
        notify_ids: Optional[List[str]] = None,
        owner_role_id: str = "ADMINISTRATORS",
        **kwargs
    ) -> HttpNumericMonitorResponse:
        """Create a new HTTP numeric monitor.
        
        Args:
            monitor_id: Unique monitor ID
            facility_id: Target facility ID
            url: URL to monitor
            description: Monitor description
            run_interval: Monitoring interval
            timeout: HTTP timeout in milliseconds
            thresholds: List of threshold configurations
            notify_ids: List of notification IDs
            owner_role_id: Owner role ID
            **kwargs: Additional monitor parameters
            
        Returns:
            Created HTTP numeric monitor information
        """
        # Create HTTP check info
        http_check_info = HttpCheckInfoRequest(
            request_url=url,
            timeout=timeout
        )
        
        # Create numeric value info for thresholds
        numeric_value_info = []
        if thresholds:
            for threshold in thresholds:
                numeric_value_info.append(MonitorNumericValueInfoRequest(
                    monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
                    priority=PriorityEnum(threshold.get("priority", PriorityEnum.WARNING)),
                    threshold_lower_limit=threshold.get("lower_limit"),
                    threshold_upper_limit=threshold.get("upper_limit"),
                    message=threshold.get("message", "")
                ))
        else:
            # Create default 8 threshold entries based on existing HTTP numeric monitor
            # Avoid duplicate (monitor_numeric_type, priority) combinations
            default_thresholds = [
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.WARNING, threshold_lower_limit=0.0, threshold_upper_limit=5000.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.INFO, threshold_lower_limit=-1.0, threshold_upper_limit=1.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.WARNING, threshold_lower_limit=-2.0, threshold_upper_limit=2.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.UNKNOWN, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.CRITICAL, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.CRITICAL, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.UNKNOWN, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.INFO, threshold_lower_limit=0.0, threshold_upper_limit=1000.0)
            ]
            numeric_value_info = default_thresholds
        
        # Create notification relations
        notify_relation_list = []
        if notify_ids:
            notify_relation_list = [
                NotifyRelationInfoRequest(notify_id=notify_id)
                for notify_id in notify_ids
            ]
        
        # Create monitor request
        monitor_request = AddHttpNumericMonitorRequest(
            monitor_id=monitor_id,
            facility_id=facility_id,
            description=description,
            run_interval=run_interval,
            owner_role_id=owner_role_id,
            notify_relation_list=notify_relation_list,
            numeric_value_info=numeric_value_info,
            http_check_info=http_check_info,
            item_name="Response Time",
            measure="msec",
            application=kwargs.get("application", "Hinemos"),
            prediction_flg=kwargs.get("prediction_flg", False),
            prediction_method=kwargs.get("prediction_method", PredictionMethodEnum.POLYNOMIAL_1),
            prediction_analysys_range=kwargs.get("prediction_analysys_range", 60),
            prediction_target=kwargs.get("prediction_target", 60),
            prediction_application=kwargs.get("prediction_application", "TEST"),
            change_flg=kwargs.get("change_flg", False),
            change_analysys_range=kwargs.get("change_analysys_range", 60),
            change_application=kwargs.get("change_application", "TEST"),
            **{k: v for k, v in kwargs.items() if k not in ["application", "prediction_flg", "prediction_method", "prediction_analysys_range", "prediction_target", "prediction_application", "change_flg", "change_analysys_range", "change_application"]}
        )
        
        return self.client.add_http_numeric_monitor(monitor_request)
    
    def update_http_numeric_monitor(
        self,
        monitor_id: str,
        description: Optional[str] = None,
        run_interval: Optional[RunIntervalEnum] = None,
        url: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> HttpNumericMonitorResponse:
        """Update an existing HTTP numeric monitor.
        
        Args:
            monitor_id: Monitor ID to update
            description: New description
            run_interval: New monitoring interval
            url: New URL to monitor
            timeout: New HTTP timeout
            **kwargs: Additional monitor parameters
            
        Returns:
            Updated HTTP numeric monitor information
        """
        # Get current monitor to preserve existing values
        current = self.client.get_http_numeric_monitor_list()
        current_monitor = next((m for m in current if m.monitor_id == monitor_id), None)
        
        if not current_monitor:
            raise ValueError(f"HTTP numeric monitor with ID {monitor_id} not found")
        
        # Include all required fields from current monitor
        update_data = {
            "facility_id": current_monitor.facility_id,
            "collector_flg": current_monitor.collector_flg,
            "application": current_monitor.application,
            "item_name": current_monitor.item_name,
            "measure": current_monitor.measure,
            "prediction_flg": current_monitor.prediction_flg,
            "prediction_method": current_monitor.prediction_method,
            "prediction_target": current_monitor.prediction_target,
            "prediction_analysys_range": current_monitor.prediction_analysys_range,
            "prediction_application": current_monitor.prediction_application,
            "change_flg": current_monitor.change_flg,
            "change_analysys_range": current_monitor.change_analysys_range,
            "change_application": current_monitor.change_application,
            "numeric_value_info": self._convert_numeric_value_response_to_request(current_monitor.numeric_value_info),
            "prediction_notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.prediction_notify_relation_list),
            "change_notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.change_notify_relation_list),
            "notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.notify_relation_list)
        }
        
        if description is not None:
            update_data["description"] = description
        if run_interval is not None:
            update_data["run_interval"] = run_interval
        
        http_check_info = None
        if url is not None or timeout is not None:
            http_check_info = HttpCheckInfoRequest(
                request_url=url if url is not None else (
                    current_monitor.http_check_info.request_url if current_monitor.http_check_info else "http://example.com"
                ),
                timeout=timeout if timeout is not None else (
                    current_monitor.http_check_info.timeout if current_monitor.http_check_info else 10000
                )
            )
        
        if http_check_info:
            update_data["http_check_info"] = http_check_info
        
        update_data.update(kwargs)
        
        modify_request = ModifyHttpNumericMonitorRequest(**update_data)
        return self.client.modify_http_numeric_monitor(monitor_id, modify_request)
    
    def create_http_string_monitor(
        self,
        monitor_id: str,
        facility_id: str,
        url: str,
        patterns: List[Dict[str, Any]],
        description: str = "",
        run_interval: RunIntervalEnum = RunIntervalEnum.MIN_05,
        timeout: int = 10000,
        notify_ids: Optional[List[str]] = None,
        owner_role_id: str = "ADMINISTRATORS",
        **kwargs
    ) -> HttpStringMonitorResponse:
        """Create a new HTTP string monitor.
        
        Args:
            monitor_id: Unique monitor ID
            facility_id: Target facility ID
            url: URL to monitor
            patterns: List of pattern configurations
            description: Monitor description
            run_interval: Monitoring interval
            timeout: HTTP timeout in milliseconds
            notify_ids: List of notification IDs
            owner_role_id: Owner role ID
            **kwargs: Additional monitor parameters
            
        Returns:
            Created HTTP string monitor information
        """
        # Create HTTP check info
        http_check_info = HttpCheckInfoRequest(
            request_url=url,
            timeout=timeout
        )
        
        # Create string value info for patterns
        string_value_info = []
        for i, pattern in enumerate(patterns):
            string_value_info.append(MonitorStringValueInfoRequest(
                order_no=i + 1,
                priority=PriorityEnum(pattern.get("priority", PriorityEnum.WARNING)),
                pattern=pattern["pattern"],
                message=pattern.get("message", ""),
                description=pattern.get("description", ""),
                case_sensitivity_flg=pattern.get("case_sensitive", True),
                process_type=pattern.get("process_type", True),
                valid_flg=pattern.get("valid", True)
            ))
        
        # Create notification relations
        notify_relation_list = []
        if notify_ids:
            notify_relation_list = [
                NotifyRelationInfoRequest(notify_id=notify_id)
                for notify_id in notify_ids
            ]
        
        # Create monitor request
        monitor_request = AddHttpStringMonitorRequest(
            monitor_id=monitor_id,
            facility_id=facility_id,
            description=description,
            run_interval=run_interval,
            owner_role_id=owner_role_id,
            notify_relation_list=notify_relation_list,
            string_value_info=string_value_info,
            http_check_info=http_check_info,
            application=kwargs.get("application", "Hinemos"),
            **{k: v for k, v in kwargs.items() if k not in ["application"]}
        )
        
        return self.client.add_http_string_monitor(monitor_request)
    
    def update_http_string_monitor(
        self,
        monitor_id: str,
        description: Optional[str] = None,
        run_interval: Optional[RunIntervalEnum] = None,
        url: Optional[str] = None,
        timeout: Optional[int] = None,
        patterns: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> HttpStringMonitorResponse:
        """Update an existing HTTP string monitor.
        
        Args:
            monitor_id: Monitor ID to update
            description: New description
            run_interval: New monitoring interval
            url: New URL to monitor
            timeout: New HTTP timeout
            patterns: New pattern configurations
            **kwargs: Additional monitor parameters
            
        Returns:
            Updated HTTP string monitor information
        """
        # Get current monitor to preserve existing values
        current = self.client.get_http_string_monitor_list()
        current_monitor = next((m for m in current if m.monitor_id == monitor_id), None)
        
        if not current_monitor:
            raise ValueError(f"HTTP string monitor with ID {monitor_id} not found")
        
        # Include all required fields from current monitor
        update_data = {
            "facility_id": current_monitor.facility_id,
            "collector_flg": current_monitor.collector_flg,
            "application": current_monitor.application,
            "log_format_id": current_monitor.log_format_id,
            "priority_change_judgment_type": current_monitor.priority_change_judgment_type,
            "priority_change_failure_type": getattr(current_monitor, 'priority_change_failure_type', PriorityChangeFailureTypeEnum.NOT_PRIORITY_CHANGE),
            "string_value_info": self._convert_string_value_response_to_request(current_monitor.string_value_info),
            "notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.notify_relation_list)
        }
        
        if description is not None:
            update_data["description"] = description
        if run_interval is not None:
            update_data["run_interval"] = run_interval
        
        # Handle patterns update
        if patterns is not None:
            string_value_info = []
            for i, pattern in enumerate(patterns):
                string_value_info.append(MonitorStringValueInfoRequest(
                    order_no=i + 1,
                    priority=PriorityEnum(pattern.get("priority", PriorityEnum.WARNING)),
                    pattern=pattern["pattern"],
                    message=pattern.get("message", ""),
                    description=pattern.get("description", ""),
                    case_sensitivity_flg=pattern.get("case_sensitive", True),
                    process_type=pattern.get("process_type", True),
                    valid_flg=pattern.get("valid", True)
                ))
            update_data["string_value_info"] = string_value_info
        
        http_check_info = None
        if url is not None or timeout is not None:
            http_check_info = HttpCheckInfoRequest(
                request_url=url if url is not None else (
                    current_monitor.http_check_info.request_url if current_monitor.http_check_info else "http://example.com"
                ),
                timeout=timeout if timeout is not None else (
                    current_monitor.http_check_info.timeout if current_monitor.http_check_info else 10000
                )
            )
        
        if http_check_info:
            update_data["http_check_info"] = http_check_info
        
        update_data.update(kwargs)
        
        modify_request = ModifyHttpStringMonitorRequest(**update_data)
        return self.client.modify_http_string_monitor(monitor_id, modify_request)
    
    def list_http_numeric_monitors(self) -> List[HttpNumericMonitorResponse]:
        """List all HTTP numeric monitors.
        
        Returns:
            List of HTTP numeric monitor information
        """
        return self.client.get_http_numeric_monitor_list()
    
    def list_http_string_monitors(self) -> List[HttpStringMonitorResponse]:
        """List all HTTP string monitors.
        
        Returns:
            List of HTTP string monitor information
        """
        return self.client.get_http_string_monitor_list()
    
    # SNMP monitoring
    
    def create_snmp_monitor(
        self,
        monitor_id: str,
        facility_id: str,
        oid: str,
        description: str = "",
        run_interval: RunIntervalEnum = RunIntervalEnum.MIN_05,
        convert_flg: ConvertFlagEnum = ConvertFlagEnum.NONE,
        thresholds: Optional[List[Dict[str, Any]]] = None,
        notify_ids: Optional[List[str]] = None,
        owner_role_id: str = "ADMINISTRATORS",
        **kwargs
    ) -> SnmpNumericMonitorResponse:
        """Create a new SNMP numeric monitor.
        
        Args:
            monitor_id: Unique monitor ID
            facility_id: Target facility ID
            oid: SNMP OID to monitor
            description: Monitor description
            run_interval: Monitoring interval
            convert_flg: Convert flag (NONE/DELTA)
            thresholds: List of threshold configurations
            notify_ids: List of notification IDs
            owner_role_id: Owner role ID
            **kwargs: Additional monitor parameters
            
        Returns:
            Created SNMP numeric monitor information
        """
        # Create SNMP check info
        snmp_check_info = SnmpCheckInfoRequest(
            snmp_oid=oid,
            convert_flg=convert_flg
        )
        
        # Create numeric value info for thresholds
        numeric_value_info = []
        if thresholds:
            for threshold in thresholds:
                numeric_value_info.append(MonitorNumericValueInfoRequest(
                    monitor_numeric_type=MonitorNumericTypeEnum.BASIC,
                    priority=PriorityEnum(threshold.get("priority", PriorityEnum.WARNING)),
                    threshold_lower_limit=threshold.get("lower_limit"),
                    threshold_upper_limit=threshold.get("upper_limit"),
                    message=threshold.get("message", "")
                ))
        else:
            # Create default 8 threshold entries based on existing SNMP monitor
            # Avoid duplicate (monitor_numeric_type, priority) combinations
            default_thresholds = [
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.WARNING, threshold_lower_limit=0.0, threshold_upper_limit=80.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.CRITICAL, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.CRITICAL, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.UNKNOWN, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.WARNING, threshold_lower_limit=-2.0, threshold_upper_limit=2.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.INFO, threshold_lower_limit=-1.0, threshold_upper_limit=1.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.CHANGE, priority=PriorityEnum.UNKNOWN, threshold_lower_limit=0.0, threshold_upper_limit=0.0),
                MonitorNumericValueInfoRequest(monitor_numeric_type=MonitorNumericTypeEnum.BASIC, priority=PriorityEnum.INFO, threshold_lower_limit=0.0, threshold_upper_limit=50.0)
            ]
            numeric_value_info = default_thresholds
        
        # Create notification relations
        notify_relation_list = []
        if notify_ids:
            notify_relation_list = [
                NotifyRelationInfoRequest(notify_id=notify_id)
                for notify_id in notify_ids
            ]
        
        # Create monitor request
        monitor_request = AddSnmpNumericMonitorRequest(
            monitor_id=monitor_id,
            facility_id=facility_id,
            description=description,
            run_interval=run_interval,
            owner_role_id=owner_role_id,
            notify_relation_list=notify_relation_list,
            numeric_value_info=numeric_value_info,
            snmp_check_info=snmp_check_info,
            item_name="SNMP Value",
            measure=kwargs.get("measure", "count"),
            application=kwargs.get("application", "Hinemos"),
            prediction_flg=kwargs.get("prediction_flg", False),
            prediction_method=kwargs.get("prediction_method", PredictionMethodEnum.POLYNOMIAL_1),
            prediction_analysys_range=kwargs.get("prediction_analysys_range", 60),
            prediction_target=kwargs.get("prediction_target", 60),
            prediction_application=kwargs.get("prediction_application", "TEST"),
            change_flg=kwargs.get("change_flg", False),
            change_analysys_range=kwargs.get("change_analysys_range", 60),
            change_application=kwargs.get("change_application", "TEST"),
            **{k: v for k, v in kwargs.items() if k not in ["application", "prediction_flg", "prediction_method", "prediction_analysys_range", "prediction_target", "prediction_application", "change_flg", "change_analysys_range", "change_application"]}
        )
        
        return self.client.add_snmp_numeric_monitor(monitor_request)
    
    def update_snmp_monitor(
        self,
        monitor_id: str,
        description: Optional[str] = None,
        run_interval: Optional[RunIntervalEnum] = None,
        oid: Optional[str] = None,
        convert_flg: Optional[ConvertFlagEnum] = None,
        **kwargs
    ) -> SnmpNumericMonitorResponse:
        """Update an existing SNMP numeric monitor.
        
        Args:
            monitor_id: Monitor ID to update
            description: New description
            run_interval: New monitoring interval
            oid: New SNMP OID to monitor
            convert_flg: New convert flag
            **kwargs: Additional monitor parameters
            
        Returns:
            Updated SNMP numeric monitor information
        """
        # Get current monitor to preserve existing values
        current = self.client.get_snmp_numeric_monitor_list()
        current_monitor = next((m for m in current if m.monitor_id == monitor_id), None)
        
        if not current_monitor:
            raise ValueError(f"SNMP numeric monitor with ID {monitor_id} not found")
        
        # Include all required fields from current monitor
        update_data = {
            "facility_id": current_monitor.facility_id,
            "collector_flg": current_monitor.collector_flg,
            "application": current_monitor.application,
            "item_name": current_monitor.item_name,
            "measure": current_monitor.measure,
            "prediction_flg": current_monitor.prediction_flg,
            "prediction_method": current_monitor.prediction_method,
            "prediction_target": current_monitor.prediction_target,
            "prediction_analysys_range": current_monitor.prediction_analysys_range,
            "prediction_application": current_monitor.prediction_application,
            "change_flg": current_monitor.change_flg,
            "change_analysys_range": current_monitor.change_analysys_range,
            "change_application": current_monitor.change_application,
            "numeric_value_info": self._convert_numeric_value_response_to_request(current_monitor.numeric_value_info),
            "prediction_notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.prediction_notify_relation_list),
            "change_notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.change_notify_relation_list),
            "notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.notify_relation_list)
        }
        
        if description is not None:
            update_data["description"] = description
        if run_interval is not None:
            update_data["run_interval"] = run_interval
        
        snmp_check_info = None
        if oid is not None or convert_flg is not None:
            snmp_check_info = SnmpCheckInfoRequest(
                snmp_oid=oid if oid is not None else (
                    current_monitor.snmp_check_info.snmp_oid if current_monitor.snmp_check_info else "1.3.6.1.2.1.1.3.0"
                ),
                convert_flg=convert_flg if convert_flg is not None else (
                    current_monitor.snmp_check_info.convert_flg if current_monitor.snmp_check_info else ConvertFlagEnum.NONE
                )
            )
        
        if snmp_check_info:
            update_data["snmp_check_info"] = snmp_check_info
        
        update_data.update(kwargs)
        
        modify_request = ModifySnmpNumericMonitorRequest(**update_data)
        return self.client.modify_snmp_numeric_monitor(monitor_id, modify_request)
    
    def list_snmp_monitors(self) -> List[SnmpNumericMonitorResponse]:
        """List all SNMP numeric monitors.
        
        Returns:
            List of SNMP numeric monitor information
        """
        return self.client.get_snmp_numeric_monitor_list()
    
    # Log file monitoring
    
    def create_logfile_monitor(
        self,
        monitor_id: str,
        facility_id: str,
        directory: str,
        filename: str,
        patterns: List[Dict[str, Any]],
        description: str = "",
        run_interval: RunIntervalEnum = RunIntervalEnum.MIN_05,
        encoding: str = "UTF-8",
        notify_ids: Optional[List[str]] = None,
        owner_role_id: str = "ADMINISTRATORS",
        **kwargs
    ) -> LogfileMonitorResponse:
        """Create a new log file monitor.
        
        Args:
            monitor_id: Unique monitor ID
            facility_id: Target facility ID
            directory: Log file directory path
            filename: Log file name pattern
            patterns: List of pattern configurations
            description: Monitor description
            run_interval: Monitoring interval
            encoding: File encoding
            notify_ids: List of notification IDs
            owner_role_id: Owner role ID
            **kwargs: Additional monitor parameters
            
        Returns:
            Created log file monitor information
        """
        # Create logfile check info
        logfile_check_info = LogfileCheckInfoRequest(
            directory=directory,
            file_name=filename,
            file_encoding=encoding
        )
        
        # Create string value info for patterns
        string_value_info = []
        for i, pattern in enumerate(patterns):
            string_value_info.append(MonitorStringValueInfoRequest(
                order_no=i + 1,
                priority=PriorityEnum(pattern.get("priority", PriorityEnum.WARNING)),
                pattern=pattern["pattern"],
                message=pattern.get("message", ""),
                description=pattern.get("description", ""),
                case_sensitivity_flg=pattern.get("case_sensitive", True),
                process_type=pattern.get("process_type", True),
                valid_flg=pattern.get("valid", True)
            ))
        
        # Create notification relations
        notify_relation_list = []
        if notify_ids:
            notify_relation_list = [
                NotifyRelationInfoRequest(notify_id=notify_id)
                for notify_id in notify_ids
            ]
        
        # Create monitor request
        monitor_request = AddLogfileMonitorRequest(
            monitor_id=monitor_id,
            facility_id=facility_id,
            description=description,
            run_interval=run_interval,
            owner_role_id=owner_role_id,
            notify_relation_list=notify_relation_list,
            string_value_info=string_value_info,
            logfile_check_info=logfile_check_info,
            application=kwargs.get("application", "Hinemos"),
            **{k: v for k, v in kwargs.items() if k not in ["application"]}
        )
        
        return self.client.add_logfile_monitor(monitor_request)
    
    def update_logfile_monitor(
        self,
        monitor_id: str,
        description: Optional[str] = None,
        run_interval: Optional[RunIntervalEnum] = None,
        directory: Optional[str] = None,
        filename: Optional[str] = None,
        encoding: Optional[str] = None,
        patterns: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LogfileMonitorResponse:
        """Update an existing logfile monitor.
        
        Args:
            monitor_id: Monitor ID to update
            description: New description
            run_interval: New monitoring interval
            directory: New log file directory
            filename: New log filename pattern
            encoding: New file encoding
            patterns: New pattern configurations
            **kwargs: Additional monitor parameters
            
        Returns:
            Updated logfile monitor information
        """
        # Get current monitor to preserve existing values
        current = self.client.get_logfile_monitor_list()
        current_monitor = next((m for m in current if m.monitor_id == monitor_id), None)
        
        if not current_monitor:
            raise ValueError(f"Logfile monitor with ID {monitor_id} not found")
        
        # Include all required fields from current monitor
        update_data = {
            "facility_id": current_monitor.facility_id,
            "collector_flg": current_monitor.collector_flg,
            "application": current_monitor.application,
            "log_format_id": current_monitor.log_format_id,
            "priority_change_judgment_type": current_monitor.priority_change_judgment_type,
            "string_value_info": self._convert_string_value_response_to_request(current_monitor.string_value_info),
            "notify_relation_list": self._convert_notify_relation_response_to_request(current_monitor.notify_relation_list)
        }
        
        if description is not None:
            update_data["description"] = description
        if run_interval is not None:
            update_data["run_interval"] = run_interval
        
        # Handle patterns update
        if patterns is not None:
            string_value_info = []
            for i, pattern in enumerate(patterns):
                string_value_info.append(MonitorStringValueInfoRequest(
                    order_no=i + 1,
                    priority=PriorityEnum(pattern.get("priority", PriorityEnum.WARNING)),
                    pattern=pattern["pattern"],
                    message=pattern.get("message", ""),
                    description=pattern.get("description", ""),
                    case_sensitivity_flg=pattern.get("case_sensitive", True),
                    process_type=pattern.get("process_type", True),
                    valid_flg=pattern.get("valid", True)
                ))
            update_data["string_value_info"] = string_value_info
        
        logfile_check_info = None
        if directory is not None or filename is not None or encoding is not None:
            logfile_check_info = LogfileCheckInfoRequest(
                directory=directory if directory is not None else (
                    current_monitor.logfile_check_info.directory if current_monitor.logfile_check_info else "/var/log"
                ),
                file_name=filename if filename is not None else (
                    current_monitor.logfile_check_info.file_name if current_monitor.logfile_check_info else "syslog"
                ),
                file_encoding=encoding if encoding is not None else (
                    current_monitor.logfile_check_info.file_encoding if current_monitor.logfile_check_info else "UTF-8"
                )
            )
        
        if logfile_check_info:
            update_data["logfile_check_info"] = logfile_check_info
        
        update_data.update(kwargs)
        
        modify_request = ModifyLogfileMonitorRequest(**update_data)
        return self.client.modify_logfile_monitor(monitor_id, modify_request)
    
    def list_logfile_monitors(self) -> List[LogfileMonitorResponse]:
        """List all log file monitors.
        
        Returns:
            List of log file monitor information
        """
        return self.client.get_logfile_monitor_list()