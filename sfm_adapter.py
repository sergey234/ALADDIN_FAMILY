#!/usr/bin/env python3
"""
SFM Adapter - Адаптер для интеграции с Safe Function Manager
"""

import sys
import os
import time
import json
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Backend path for SFM imports
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add security module path
security_path = "/opt/aladdin-backend/security"
if security_path not in sys.path:
    sys.path.insert(0, security_path)

class SFMAdapter:
    """
    Optimized Adapter for Safe Function Manager integration
    Asynchronous initialization, fast startup, graceful fallback
    """

    def __init__(self):
        self._sfm = None
        self.available = False
        self._sfm_initialized = False
        self._init_thread = None
        self._init_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="sfm-init")

        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'fallback_calls': 0,
            'avg_response_time': 0,
            'init_time': 0,
            'init_status': 'pending'  # pending -> initializing -> ready/failed
        }

    def _initialize_sfm_async(self):
        """Asynchronous SFM initialization in background thread"""
        def init_worker():
            start_time = time.time()
            try:
                self.metrics['init_status'] = 'initializing'
                print("🔄 Starting SFM initialization in background...")

                # Try to import SFM using optimized singleton
                from security.sfm_singleton import get_sfm
                self._sfm = get_sfm()

                init_duration = time.time() - start_time
                self.metrics['init_time'] = init_duration
                self.available = True
                self._sfm_initialized = True
                self.metrics['init_status'] = 'ready'

                print(f"✅ SFM initialized successfully in {init_duration:.2f} seconds")

            except Exception as e:
                init_duration = time.time() - start_time
                self.metrics['init_time'] = init_duration
                self._sfm = None
                self.available = False
                self._sfm_initialized = True  # Mark as attempted
                self.metrics['init_status'] = 'failed'

                print(f"❌ SFM initialization failed after {init_duration:.2f} seconds: {e}")

        # Start initialization in background thread
        if not self._init_thread or not self._init_thread.is_alive():
            with self._init_lock:
                if not self._init_thread or not self._init_thread.is_alive():
                    self._init_thread = threading.Thread(
                        target=init_worker,
                        name="sfm-initializer",
                        daemon=True
                    )
                    self._init_thread.start()

    def _initialize_sfm(self):
        """Legacy synchronous initialization - redirects to async"""
        if not self._sfm_initialized:
            self._initialize_sfm_async()
        # For immediate calls, wait a bit for initialization
        if self.metrics['init_status'] == 'initializing':
            time.sleep(0.1)  # Brief wait

    def execute_function(self, func_name: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Execute function through SFM with fallback

        Args:
            func_name: Name of the function to execute
            params: Parameters for the function

        Returns:
            Tuple(success: bool, result: Any, error_message: Optional[str])
        """
        # Lazy initialization of SFM
        if not self._sfm_initialized:
            self._initialize_sfm()
            self._sfm_initialized = True

        self.metrics['total_calls'] += 1
        params = params or {}

        start_time = time.time()

        try:
            if self.available and self._sfm:
                # Try to execute through SFM
                result = self._execute_sfm_function(func_name, params)
                response_time = time.time() - start_time

                self.metrics['successful_calls'] += 1
                self.metrics['avg_response_time'] = (
                    (self.metrics['avg_response_time'] * (self.metrics['total_calls'] - 1)) + response_time
                ) / self.metrics['total_calls']

                return True, result, None

            else:
                # Fallback to mock
                result = self._execute_mock_function(func_name, params)
                self.metrics['fallback_calls'] += 1
                return True, result, None

        except Exception as e:
            self.metrics['failed_calls'] += 1
            error_msg = f"SFM execution failed: {str(e)}"
            print(f"❌ {error_msg}")

            # Try fallback
            try:
                result = self._execute_mock_function(func_name, params)
                self.metrics['fallback_calls'] += 1
                return True, result, f"Fallback used: {error_msg}"
            except Exception as fallback_error:
                return False, None, f"Both SFM and fallback failed: {error_msg}, {str(fallback_error)}"

    def _execute_sfm_function(self, func_name: str, params: Dict[str, Any]) -> Any:
        """Execute function through real SFM"""
        if not hasattr(self._sfm, 'execute_function'):
            raise AttributeError("SFM does not have execute_function method")

        return self._sfm.execute_function(func_name, params)

    def _execute_mock_function(self, func_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock function for fallback"""

        # Mock responses based on function name
        mock_responses = {

            # Group 1: Components (10 endpoints)
            "get_component_status": {
                "component_id": params.get("component_id", "unknown"),
                "status": "enabled",
                "last_check": datetime.utcnow().isoformat(),
                "source": "mock"
            },
            "enable_component": {
                "component_id": params.get("component_id", "unknown"),
                "action": "enable",
                "status": "success",
                "source": "mock"
            },
            "disable_component": {
                "component_id": params.get("component_id", "unknown"),
                "action": "disable",
                "status": "success",
                "source": "mock"
            },
            "get_component_config": {
                "component_id": params.get("component_id", "unknown"),
                "config": {"enabled": True, "level": "medium"},
                "source": "mock"
            },
            "update_component_config": {
                "component_id": params.get("component_id", "unknown"),
                "action": "update_config",
                "status": "success",
                "source": "mock"
            },
            "get_components_health": {
                "overall_health": "good",
                "components_count": 10,
                "healthy_components": 9,
                "source": "mock"
            },
            "restart_component": {
                "component_id": params.get("component_id", "unknown"),
                "action": "restart",
                "status": "success",
                "source": "mock"
            },
            "get_component_logs": {
                "component_id": params.get("component_id", "unknown"),
                "logs": ["[INFO] Component started", "[INFO] Health check passed"],
                "source": "mock"
            },
            "backup_component": {
                "component_id": params.get("component_id", "unknown"),
                "action": "backup",
                "backup_id": f"backup_{int(time.time())}",
                "source": "mock"
            },
            "restore_component": {
                "component_id": params.get("component_id", "unknown"),
                "action": "restore",
                "status": "success",
                "source": "mock"
            },

            # Group 2: Security Settings (15 endpoints)
            "get_phishing_sensitivity": {"level": "medium", "source": "mock"},
            "update_phishing_sensitivity": {"action": "update", "level": params.get("level", "medium"), "source": "mock"},
            "get_phishing_block_suspicious": {"enabled": True, "source": "mock"},
            "update_phishing_block_suspicious": {"action": "update", "enabled": params.get("enabled", True), "source": "mock"},
            "get_phishing_exclusions": {"exclusions": [], "source": "mock"},
            "get_malware_scan_scheduled": {"enabled": True, "schedule": "daily", "source": "mock"},
            "update_malware_scan_scheduled": {"action": "update", "status": "success", "source": "mock"},
            "get_malware_quarantine": {"enabled": True, "source": "mock"},
            "update_malware_quarantine": {"action": "update", "status": "success", "source": "mock"},
            "scan_malware_now": {"action": "scan_started", "scan_id": f"scan_{int(time.time())}", "source": "mock"},
            "get_mobile_app_lock": {"enabled": False, "source": "mock"},
            "update_mobile_app_lock": {"action": "update", "status": "success", "source": "mock"},
            "get_mobile_biometric": {"enabled": True, "source": "mock"},
            "get_firewall_rules": {"rules": [], "source": "mock"},
            "update_vpn_config": {"action": "update", "status": "success", "source": "mock"},

            # Group 3: Monitoring (20 endpoints)
            "get_ai_categories_stats": {
                "total_content": 0,
                "blocked_content": 0,
                "allowed_content": 0,
                "source": "mock"
            },
            "get_ai_categories_reports": {"reports": [], "source": "mock"},
            "allow_ai_content": {"action": "allow", "status": "success", "source": "mock"},
            "block_ai_content": {"action": "block", "status": "success", "source": "mock"},
            "get_data_cleanup_stats": {"total_cleaned": 0, "last_cleanup": None, "source": "mock"},
            "get_data_cleanup_records": {"records": [], "source": "mock"},
            "start_data_cleanup": {"action": "cleanup_started", "job_id": f"job_{int(time.time())}", "source": "mock"},
            "get_location_stats": {"total_requests": 0, "allowed_requests": 0, "blocked_requests": 0, "source": "mock"},
            "get_location_requests": {"requests": [], "source": "mock"},
            "allow_location_request": {"action": "allow", "status": "success", "source": "mock"},
            "block_location_request": {"action": "block", "status": "success", "source": "mock"},
            "update_location_accuracy": {"action": "update_accuracy", "status": "success", "source": "mock"},
            "get_darkweb_leaks": {"leaks": [], "total": 0, "source": "mock"},
            "get_darkweb_stats": {"total_scans": 0, "leaks_found": 0, "last_scan": None, "source": "mock"},
            "get_darkweb_scans": {"scans": [], "source": "mock"},
            "resolve_darkweb_leak": {"action": "resolve", "status": "success", "source": "mock"},
            "start_darkweb_scan": {"action": "scan_started", "scan_id": f"scan_{int(time.time())}", "source": "mock"},
            "get_identity_attempts": {"attempts": [], "total": 0, "source": "mock"},
            "get_identity_stats": {"total_attempts": 0, "blocked_attempts": 0, "allowed_attempts": 0, "source": "mock"},
            "allow_identity_attempt": {"action": "allow", "status": "success", "source": "mock"},
            "block_identity_attempt": {"action": "block", "status": "success", "source": "mock"},
            "add_to_identity_whitelist": {"action": "whitelist", "status": "success", "source": "mock"},

            # Group 4: Protection (25 endpoints)
            "get_identity_theft_attempts": {"attempts": [], "source": "mock"},
            "get_identity_theft_stats": {"stats": {}, "source": "mock"},
            "allow_identity_theft_attempt": {"action": "allow", "status": "success", "source": "mock"},
            "block_identity_theft_attempt": {"action": "block", "status": "success", "source": "mock"},
            "add_identity_theft_whitelist": {"action": "whitelist", "source": "mock"},
            "get_identity_theft_history": {"history": [], "source": "mock"},
            "report_identity_theft_attempt": {"action": "report", "status": "success", "source": "mock"},
            "update_identity_theft_settings": {"action": "update_settings", "source": "mock"},
            "get_antitracker_trackers": {"trackers": [], "source": "mock"},
            "block_antitracker_tracker": {"action": "block", "status": "success", "source": "mock"},
            "allow_antitracker_tracker": {"action": "allow", "status": "success", "source": "mock"},
            "get_antitracker_stats": {"stats": {}, "source": "mock"},
            "add_antitracker_whitelist": {"action": "whitelist", "source": "mock"},
            "get_antitracker_categories": {"categories": [], "source": "mock"},
            "update_antitracker_category": {"action": "update_category", "source": "mock"},
            "scan_antitracker": {"action": "scan_started", "scan_id": f"scan_{int(time.time())}", "source": "mock"},
            "get_antitracker_reports": {"reports": [], "source": "mock"},
            "get_parental_stats": {"stats": {}, "source": "mock"},
            "update_parental_settings": {"action": "update_settings", "source": "mock"},
            "restrict_parental_child": {"action": "restrict", "source": "mock"},
            "get_parental_activity": {"activity": [], "source": "mock"},
            "send_parental_alert": {"action": "alert_sent", "source": "mock"},
            "send_roadside_emergency": {"action": "emergency_sent", "emergency_id": f"emergency_{int(time.time())}", "source": "mock"},
            "get_roadside_history": {"history": [], "source": "mock"},
            "update_roadside_settings": {"action": "update_settings", "source": "mock"},

            # Group 5: System (31 endpoints)
            "get_notifications_list": {"notifications": [], "source": "mock"},
            "mark_notification_read": {"action": "mark_read", "source": "mock"},
            "delete_notification": {"action": "delete", "source": "mock"},
            "update_notifications_settings": {"action": "update_settings", "source": "mock"},
            "test_notifications": {"action": "test_sent", "source": "mock"},
            "get_notifications_stats": {"stats": {}, "source": "mock"},
            "bulk_mark_notifications_read": {"action": "bulk_mark_read", "count": 0, "source": "mock"},
            "get_notifications_unread_count": {"unread_count": 0, "source": "mock"},
            "get_analytics_overview": {"overview": {}, "source": "mock"},
            "get_analytics_security_events": {"events": [], "source": "mock"},
            "get_analytics_performance": {"performance": {}, "source": "mock"},
            "export_analytics": {"action": "export_started", "export_id": f"export_{int(time.time())}", "source": "mock"},
            "get_analytics_reports": {"reports": [], "source": "mock"},
            "update_analytics_settings": {"action": "update_settings", "source": "mock"},
            "get_subscription_status": {"status": "active", "plan": "premium", "source": "mock"},
            "get_subscription_plans": {"plans": [], "source": "mock"},
            "upgrade_subscription": {"action": "upgrade", "new_plan": "premium", "source": "mock"},
            "cancel_subscription": {"action": "cancel", "effective_date": "2024-12-31", "source": "mock"},
            "get_subscription_billing_history": {"billing_history": [], "source": "mock"},
            "update_subscription_payment_method": {"action": "update_payment_method", "source": "mock"},
            "register_user": {"action": "register", "user_id": f"user_{int(time.time())}", "source": "mock"},
            "login_user": {"action": "login", "token": f"token_{int(time.time())}", "source": "mock"},
            "logout_user": {"action": "logout", "source": "mock"},
            "refresh_token": {"action": "refresh", "new_token": f"new_token_{int(time.time())}", "source": "mock"},
            "get_user_profile": {"profile": {}, "source": "mock"},
            "update_user_profile": {"action": "update_profile", "source": "mock"},
            "get_system_info": {"system_info": {}, "source": "mock"},
            "get_system_health": {"health": {}, "source": "mock"},
            "create_system_backup": {"action": "backup_created", "backup_id": f"backup_{int(time.time())}", "source": "mock"},
            "get_system_logs": {"logs": [], "source": "mock"},
            "run_system_maintenance": {"action": "maintenance_started", "task_id": f"task_{int(time.time())}", "source": "mock"},
        }

        # Return mock response or default
        return mock_responses.get(func_name, {
            "error": f"Unknown function: {func_name}",
            "params": params,
            "source": "mock"
        })

    def get_metrics(self) -> Dict[str, Any]:
        """Get adapter metrics"""
        return {
            **self.metrics,
            "sfm_available": self.available,
            "timestamp": datetime.utcnow().isoformat()
        }

    def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with detailed SFM status"""
        sfm_status = "available" if self.available else self.metrics['init_status']

        health_data = {
            "status": "ok" if self.available else "initializing",
            "sfm_adapter": sfm_status,  # This is what mobile app checks
            "endpoints": 101,
            "groups": ["components", "security", "monitoring", "protection", "system"],
            "sfm_available": self.available,
            "sfm_init_status": self.metrics['init_status'],
            "sfm_init_time": f"{self.metrics['init_time']:.2f}s" if self.metrics['init_time'] > 0 else "pending",
            "metrics": self.get_metrics()
        }

        return health_data

# Global instance
sfm_adapter = SFMAdapter()

if __name__ == "__main__":
    # Test the adapter
    print("🧪 Testing SFM Adapter...")

    # Test health check
    health = sfm_adapter.health_check()
    print(f"Health: {health}")

    # Test some functions
    test_functions = [
        "get_component_status",
        "get_phishing_sensitivity",
        "get_ai_categories_stats",
        "get_identity_theft_stats",
        "get_notifications_unread_count"
    ]

    for func in test_functions:
        success, result, error = sfm_adapter.execute_function(func, {"test": True})
        status = "✅" if success else "❌"
        print(f"{status} {func}: {result.get('source', 'unknown') if success else error}")

    # Show metrics
    print(f"\n📊 Metrics: {sfm_adapter.get_metrics()}")
    print("✅ SFM Adapter test completed!")


