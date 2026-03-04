#!/usr/bin/env python3
"""
ALADDIN API Gateway - ПОЛНАЯ ВЕРСИЯ со ВСЕМИ 101 ENDPOINT
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# SFM Adapter import
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
    print("SFM Adapter loaded successfully")
except ImportError as e:
    print(f"SFM Adapter not available: {e}")
    SFM_ADAPTER_AVAILABLE = False

app = FastAPI(title="ALADDIN API Gateway", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"service": "ALADDIN API Gateway", "version": "1.0.0", "status": "running"}

@app.get("/api/health")
async def health():
    sfm_status = "available" if SFM_ADAPTER_AVAILABLE and sfm_adapter and sfm_adapter.available else "fallback"
    return {
        "status": "ok",
        "sfm_adapter": sfm_status,
        "endpoints": 101,
        "groups": ["components", "security", "monitoring", "protection", "system"]
    }

# =============================================================================
# ГРУППА 1: КОМПОНЕНТЫ (10 endpoints)
# =============================================================================

@app.get("/api/components/status/{component_id}")
async def get_component_status(component_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_component_status", {"component_id": component_id})
        return result if success else {"error": message, "component_id": component_id}
    else:
        return {"component_id": component_id, "status": "enabled", "source": "mock"}

@app.post("/api/components/enable/{component_id}")
async def enable_component(component_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("enable_component", {"component_id": component_id})
        return result if success else {"error": message, "component_id": component_id}
    else:
        return {"component_id": component_id, "action": "enable", "source": "mock"}

@app.post("/api/components/disable/{component_id}")
async def disable_component(component_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("disable_component", {"component_id": component_id})
        return result if success else {"error": message, "component_id": component_id}
    else:
        return {"component_id": component_id, "action": "disable", "source": "mock"}

@app.get("/api/components/config/{component_id}")
async def get_component_config(component_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_component_config", {"component_id": component_id})
        return result if success else {"error": message, "component_id": component_id}
    else:
        return {"component_id": component_id, "config": {}, "source": "mock"}

@app.put("/api/components/config/{component_id}")
async def update_component_config(component_id: str, config: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_component_config", {"component_id": component_id, "config": config})
        return result if success else {"error": message, "component_id": component_id}
    else:
        return {"component_id": component_id, "action": "update_config", "source": "mock"}

@app.get("/api/components/health")
async def get_components_health():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_components_health", {})
        return result if success else {"error": message}
    else:
        return {"overall_health": "unknown", "components_count": 0, "source": "mock"}

@app.post("/api/components/restart/{component_id}")
async def restart_component(component_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("restart_component", {"component_id": component_id})
        return result if success else {"error": message, "component_id": component_id}
    else:
        return {"component_id": component_id, "action": "restart", "source": "mock"}

@app.get("/api/components/logs/{component_id}")
async def get_component_logs(component_id: str, limit: int = 100):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_component_logs", {"component_id": component_id, "limit": limit})
        return result if success else {"error": message, "component_id": component_id}
    else:
        return {"component_id": component_id, "logs": [], "source": "mock"}

@app.post("/api/components/backup/{component_id}")
async def backup_component(component_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("backup_component", {"component_id": component_id})
        return result if success else {"error": message, "component_id": component_id}
    else:
        return {"component_id": component_id, "action": "backup", "source": "mock"}

@app.post("/api/components/restore/{component_id}")
async def restore_component(component_id: str, backup_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("restore_component", {"component_id": component_id, "backup_id": backup_id})
        return result if success else {"error": message, "component_id": component_id}
    else:
        return {"component_id": component_id, "action": "restore", "source": "mock"}

# =============================================================================
# ГРУППА 2: НАСТРОЙКИ БЕЗОПАСНОСТИ (15 endpoints)
# =============================================================================

# Phishing Protection (5 endpoints)
@app.get("/api/phishing/sensitivity")
async def get_phishing_sensitivity():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_phishing_sensitivity", {})
        return result if success else {"error": message}
    else:
        return {"sensitivity": "medium", "source": "mock"}

@app.put("/api/phishing/sensitivity")
async def update_phishing_sensitivity(sensitivity: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_phishing_sensitivity", {"sensitivity": sensitivity})
        return result if success else {"error": message}
    else:
        return {"action": "update_sensitivity", "source": "mock"}

@app.get("/api/phishing/block_suspicious")
async def get_phishing_block_suspicious():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_phishing_block_suspicious", {})
        return result if success else {"error": message}
    else:
        return {"block_suspicious": True, "source": "mock"}

@app.put("/api/phishing/block_suspicious")
async def update_phishing_block_suspicious(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_phishing_block_suspicious", {"settings": settings})
        return result if success else {"error": message}
    else:
        return {"action": "update_block_suspicious", "source": "mock"}

@app.get("/api/phishing/exclusions")
async def get_phishing_exclusions():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_phishing_exclusions", {})
        return result if success else {"error": message}
    else:
        return {"exclusions": [], "source": "mock"}

# Malware Detection (5 endpoints)
@app.get("/api/malware/scan_scheduled")
async def get_malware_scan_scheduled():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_malware_scan_scheduled", {})
        return result if success else {"error": message}
    else:
        return {"scheduled": True, "schedule": "daily", "source": "mock"}

@app.put("/api/malware/scan_scheduled")
async def update_malware_scan_scheduled(schedule: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_malware_scan_scheduled", {"schedule": schedule})
        return result if success else {"error": message}
    else:
        return {"action": "update_scan_schedule", "source": "mock"}

@app.get("/api/malware/quarantine")
async def get_malware_quarantine():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_malware_quarantine", {})
        return result if success else {"error": message}
    else:
        return {"enabled": True, "retention_days": 30, "source": "mock"}

@app.put("/api/malware/quarantine")
async def update_malware_quarantine(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_malware_quarantine", {"settings": settings})
        return result if success else {"error": message}
    else:
        return {"action": "update_quarantine", "source": "mock"}

@app.post("/api/malware/scan_now")
async def scan_malware_now():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("scan_malware_now", {})
        return result if success else {"error": message}
    else:
        return {"action": "scan_started", "scan_id": "mock_scan_123", "source": "mock"}

# Mobile Security (3 endpoints)
@app.get("/api/mobile/app_lock")
async def get_mobile_app_lock():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_mobile_app_lock", {})
        return result if success else {"error": message}
    else:
        return {"enabled": True, "timeout_minutes": 5, "source": "mock"}

@app.put("/api/mobile/app_lock")
async def update_mobile_app_lock(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_mobile_app_lock", {"settings": settings})
        return result if success else {"error": message}
    else:
        return {"action": "update_app_lock", "source": "mock"}

@app.get("/api/mobile/biometric")
async def get_mobile_biometric():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_mobile_biometric", {})
        return result if success else {"error": message}
    else:
        return {"enabled": True, "fingerprint": True, "face_id": False, "source": "mock"}

# Network Security (2 endpoints)
@app.get("/api/network/firewall_rules")
async def get_network_firewall_rules():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_network_firewall_rules", {})
        return result if success else {"error": message}
    else:
        return {"rules": [], "default_policy": "allow", "source": "mock"}

@app.put("/api/network/vpn_config")
async def update_network_vpn_config(config: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_network_vpn_config", {"config": config})
        return result if success else {"error": message}
    else:
        return {"action": "update_vpn_config", "source": "mock"}

# =============================================================================
# ГРУППА 3: МОНИТОРИНГ (20 endpoints)
# =============================================================================

# AI Categories (4 endpoints)
@app.get("/api/ai/categories/stats")
async def get_ai_categories_stats(child_id: str = None):
    params = {"child_id": child_id} if child_id else {}
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_ai_categories_stats", params)
        return result if success else {"error": message}
    else:
        return {"total_content": 0, "blocked_content": 0, "allowed_content": 0, "source": "mock"}

@app.get("/api/ai/categories/reports")
async def get_ai_categories_reports(child_id: str = None):
    params = {"child_id": child_id} if child_id else {}
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_ai_categories_reports", params)
        return result if success else {"error": message}
    else:
        return {"reports": [], "source": "mock"}

@app.post("/api/ai/categories/allow")
async def allow_ai_content(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_ai_content", data)
        return result if success else {"error": message}
    else:
        return {"action": "allow", "status": "mock_success", "source": "mock"}

@app.post("/api/ai/categories/block")
async def block_ai_content(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_ai_content", data)
        return result if success else {"error": message}
    else:
        return {"action": "block", "status": "mock_success", "source": "mock"}

# Data Cleanup (3 endpoints)
@app.get("/api/data/cleanup/stats")
async def get_data_cleanup_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_data_cleanup_stats", {})
        return result if success else {"error": message}
    else:
        return {"total_cleaned": 0, "last_cleanup": None, "source": "mock"}

@app.get("/api/data/cleanup/records")
async def get_data_cleanup_records(limit: int = 20):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_data_cleanup_records", {"limit": limit})
        return result if success else {"error": message}
    else:
        return {"records": [], "limit": limit, "source": "mock"}

@app.post("/api/data/cleanup/start")
async def start_data_cleanup(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("start_data_cleanup", data)
        return result if success else {"error": message}
    else:
        return {"action": "cleanup_started", "job_id": "mock_job_123", "source": "mock"}

# Location Tracking (4 endpoints)
@app.get("/api/location/stats")
async def get_location_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_location_stats", {})
        return result if success else {"error": message}
    else:
        return {"total_requests": 0, "allowed_requests": 0, "blocked_requests": 0, "source": "mock"}

@app.get("/api/location/requests")
async def get_location_requests(limit: int = 50):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_location_requests", {"limit": limit})
        return result if success else {"error": message}
    else:
        return {"requests": [], "limit": limit, "source": "mock"}

@app.post("/api/location/allow")
async def allow_location_request(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_location_request", data)
        return result if success else {"error": message}
    else:
        return {"action": "allow", "status": "mock_success", "source": "mock"}

@app.post("/api/location/block")
async def block_location_request(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_location_request", data)
        return result if success else {"error": message}
    else:
        return {"action": "block", "status": "mock_success", "source": "mock"}

@app.put("/api/location/accuracy")
async def update_location_accuracy(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_location_accuracy", data)
        return result if success else {"error": message}
    else:
        return {"action": "update_accuracy", "status": "mock_success", "source": "mock"}

# Dark Web Monitoring (5 endpoints)
@app.get("/api/darkweb/leaks")
async def get_darkweb_leaks(status: str = None, severity: str = None):
    params = {}
    if status: params["status"] = status
    if severity: params["severity"] = severity
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_darkweb_leaks", params)
        return result if success else {"error": message}
    else:
        return {"leaks": [], "total": 0, "source": "mock"}

@app.get("/api/darkweb/stats")
async def get_darkweb_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_darkweb_stats", {})
        return result if success else {"error": message}
    else:
        return {"total_scans": 0, "leaks_found": 0, "last_scan": None, "source": "mock"}

@app.get("/api/darkweb/scans")
async def get_darkweb_scans(limit: int = 20):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_darkweb_scans", {"limit": limit})
        return result if success else {"error": message}
    else:
        return {"scans": [], "limit": limit, "source": "mock"}

@app.post("/api/darkweb/resolve")
async def resolve_darkweb_leak(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("resolve_darkweb_leak", data)
        return result if success else {"error": message}
    else:
        return {"action": "resolve", "status": "mock_success", "source": "mock"}

@app.post("/api/darkweb/scan_start")
async def start_darkweb_scan():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("start_darkweb_scan", {})
        return result if success else {"error": message}
    else:
        return {"action": "scan_started", "scan_id": "mock_scan_123", "source": "mock"}

# Identity Theft (4 endpoints)
@app.get("/api/identity/attempts")
async def get_identity_attempts(action: str = None, severity: str = None):
    params = {}
    if action: params["action"] = action
    if severity: params["severity"] = severity
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_attempts", params)
        return result if success else {"error": message}
    else:
        return {"attempts": [], "total": 0, "source": "mock"}

@app.get("/api/identity/stats")
async def get_identity_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_stats", {})
        return result if success else {"error": message}
    else:
        return {"total_attempts": 0, "blocked_attempts": 0, "allowed_attempts": 0, "source": "mock"}

@app.post("/api/identity/allow")
async def allow_identity_attempt(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_identity_attempt", data)
        return result if success else {"error": message}
    else:
        return {"action": "allow", "status": "mock_success", "source": "mock"}

@app.post("/api/identity/block")
async def block_identity_attempt(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_identity_attempt", data)
        return result if success else {"error": message}
    else:
        return {"action": "block", "status": "mock_success", "source": "mock"}

@app.post("/api/identity/whitelist")
async def add_to_identity_whitelist(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("add_to_identity_whitelist", data)
        return result if success else {"error": message}
    else:
        return {"action": "whitelist", "status": "mock_success", "source": "mock"}

# =============================================================================
# ГРУППА 4: ЗАЩИТА (25 endpoints)
# =============================================================================

# Identity Theft (8 endpoints)
@app.get("/api/identity/theft/attempts")
async def get_identity_theft_attempts(action: str = None, severity: str = None):
    params = {}
    if action: params["action"] = action
    if severity: params["severity"] = severity
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_theft_attempts", params)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"attempts": [], "source": "mock"}

@app.get("/api/identity/theft/stats")
async def get_identity_theft_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_theft_stats", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"stats": {}, "source": "mock"}

@app.post("/api/identity/theft/allow/{attempt_id}")
async def allow_identity_theft_attempt(attempt_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_identity_theft_attempt", {"attempt_id": attempt_id})
        return result if success else {"error": message, "attempt_id": attempt_id, "source": "mock"}
    else:
        return {"action": "allow", "attempt_id": attempt_id, "source": "mock"}

@app.post("/api/identity/theft/block/{attempt_id}")
async def block_identity_theft_attempt(attempt_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_identity_theft_attempt", {"attempt_id": attempt_id})
        return result if success else {"error": message, "attempt_id": attempt_id, "source": "mock"}
    else:
        return {"action": "block", "attempt_id": attempt_id, "source": "mock"}

@app.post("/api/identity/theft/whitelist")
async def add_identity_theft_whitelist(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("add_identity_theft_whitelist", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "whitelist", "source": "mock"}

@app.get("/api/identity/theft/history")
async def get_identity_theft_history(limit: int = 50):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_theft_history", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"history": [], "limit": limit, "source": "mock"}

@app.post("/api/identity/theft/report/{attempt_id}")
async def report_identity_theft_attempt(attempt_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("report_identity_theft_attempt", {"attempt_id": attempt_id})
        return result if success else {"error": message, "attempt_id": attempt_id, "source": "mock"}
    else:
        return {"action": "report", "attempt_id": attempt_id, "source": "mock"}

@app.put("/api/identity/theft/settings")
async def update_identity_theft_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_identity_theft_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

# Anti Tracker (9 endpoints)
@app.get("/api/antitracker/trackers")
async def get_antitracker_trackers():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_antitracker_trackers", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"trackers": [], "source": "mock"}

@app.post("/api/antitracker/block/{tracker_id}")
async def block_antitracker_tracker(tracker_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_antitracker_tracker", {"tracker_id": tracker_id})
        return result if success else {"error": message, "tracker_id": tracker_id, "source": "mock"}
    else:
        return {"action": "block", "tracker_id": tracker_id, "source": "mock"}

@app.post("/api/antitracker/allow/{tracker_id}")
async def allow_antitracker_tracker(tracker_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_antitracker_tracker", {"tracker_id": tracker_id})
        return result if success else {"error": message, "tracker_id": tracker_id, "source": "mock"}
    else:
        return {"action": "allow", "tracker_id": tracker_id, "source": "mock"}

@app.get("/api/antitracker/stats")
async def get_antitracker_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_antitracker_stats", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"stats": {}, "source": "mock"}

@app.post("/api/antitracker/whitelist")
async def add_antitracker_whitelist(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("add_antitracker_whitelist", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "whitelist", "source": "mock"}

@app.get("/api/antitracker/categories")
async def get_antitracker_categories():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_antitracker_categories", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"categories": [], "source": "mock"}

@app.put("/api/antitracker/category/{category_id}")
async def update_antitracker_category(category_id: str, settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        params = {"category_id": category_id, **settings}
        success, result, message = sfm_adapter.execute_function("update_antitracker_category", params)
        return result if success else {"error": message, "category_id": category_id, "source": "mock"}
    else:
        return {"action": "update_category", "category_id": category_id, "source": "mock"}

@app.post("/api/antitracker/scan")
async def scan_antitracker():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("scan_antitracker", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "scan_started", "scan_id": "mock_scan_123", "source": "mock"}

@app.get("/api/antitracker/reports")
async def get_antitracker_reports(limit: int = 20):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_antitracker_reports", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"reports": [], "limit": limit, "source": "mock"}

# Parental Control (5 endpoints)
@app.get("/api/parental/stats")
async def get_parental_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_parental_stats", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"stats": {}, "source": "mock"}

@app.put("/api/parental/settings")
async def update_parental_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_parental_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

@app.post("/api/parental/restrict/{child_id}")
async def restrict_parental_child(child_id: str, restrictions: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        params = {"child_id": child_id, **restrictions}
        success, result, message = sfm_adapter.execute_function("restrict_parental_child", params)
        return result if success else {"error": message, "child_id": child_id, "source": "mock"}
    else:
        return {"action": "restrict", "child_id": child_id, "source": "mock"}

@app.get("/api/parental/activity/{child_id}")
async def get_parental_activity(child_id: str, limit: int = 50):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_parental_activity", {"child_id": child_id, "limit": limit})
        return result if success else {"error": message, "child_id": child_id, "source": "mock"}
    else:
        return {"activity": [], "child_id": child_id, "limit": limit, "source": "mock"}

@app.post("/api/parental/alert")
async def send_parental_alert(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("send_parental_alert", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "alert_sent", "source": "mock"}

# Roadside Assistance (3 endpoints)
@app.post("/api/roadside/emergency")
async def send_roadside_emergency(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("send_roadside_emergency", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "emergency_sent", "emergency_id": "mock_emergency_123", "source": "mock"}

@app.get("/api/roadside/history")
async def get_roadside_history(limit: int = 20):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_roadside_history", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"history": [], "limit": limit, "source": "mock"}

@app.put("/api/roadside/settings")
async def update_roadside_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_roadside_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

# =============================================================================
# ГРУППА 5: СИСТЕМА (31 endpoint)
# =============================================================================

# Notifications (8 endpoints)
@app.get("/api/notifications/list")
async def get_notifications_list(limit: int = 50):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_notifications_list", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"notifications": [], "limit": limit, "source": "mock"}

@app.post("/api/notifications/mark_read/{notification_id}")
async def mark_notification_read(notification_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("mark_notification_read", {"notification_id": notification_id})
        return result if success else {"error": message, "notification_id": notification_id, "source": "mock"}
    else:
        return {"action": "mark_read", "notification_id": notification_id, "source": "mock"}

@app.post("/api/notifications/delete/{notification_id}")
async def delete_notification(notification_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("delete_notification", {"notification_id": notification_id})
        return result if success else {"error": message, "notification_id": notification_id, "source": "mock"}
    else:
        return {"action": "delete", "notification_id": notification_id, "source": "mock"}

@app.put("/api/notifications/settings")
async def update_notifications_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_notifications_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

@app.post("/api/notifications/test")
async def test_notifications():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("test_notifications", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "test_sent", "source": "mock"}

@app.get("/api/notifications/stats")
async def get_notifications_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_notifications_stats", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"stats": {}, "source": "mock"}

@app.post("/api/notifications/bulk_mark_read")
async def bulk_mark_notifications_read(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("bulk_mark_notifications_read", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "bulk_mark_read", "count": 0, "source": "mock"}

@app.get("/api/notifications/unread_count")
async def get_notifications_unread_count():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_notifications_unread_count", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"unread_count": 0, "source": "mock"}

# Analytics (6 endpoints)
@app.get("/api/analytics/overview")
async def get_analytics_overview(period: str = "month"):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_analytics_overview", {"period": period})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"overview": {}, "period": period, "source": "mock"}

@app.get("/api/analytics/security_events")
async def get_analytics_security_events(limit: int = 100):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_analytics_security_events", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"events": [], "limit": limit, "source": "mock"}

@app.get("/api/analytics/performance")
async def get_analytics_performance():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_analytics_performance", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"performance": {}, "source": "mock"}

@app.post("/api/analytics/export")
async def export_analytics(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("export_analytics", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "export_started", "export_id": "mock_export_123", "source": "mock"}

@app.get("/api/analytics/reports")
async def get_analytics_reports(type: str = "security"):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_analytics_reports", {"type": type})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"reports": [], "type": type, "source": "mock"}

@app.put("/api/analytics/settings")
async def update_analytics_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_analytics_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

# Subscription (6 endpoints)
@app.get("/api/subscription/status")
async def get_subscription_status():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_subscription_status", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"status": "active", "plan": "premium", "source": "mock"}

@app.get("/api/subscription/plans")
async def get_subscription_plans():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_subscription_plans", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"plans": [], "source": "mock"}

@app.post("/api/subscription/upgrade")
async def upgrade_subscription(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("upgrade_subscription", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "upgrade", "new_plan": "premium", "source": "mock"}

@app.post("/api/subscription/cancel")
async def cancel_subscription():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("cancel_subscription", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "cancel", "effective_date": "2024-12-31", "source": "mock"}

@app.get("/api/subscription/billing_history")
async def get_subscription_billing_history(limit: int = 12):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_subscription_billing_history", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"billing_history": [], "limit": limit, "source": "mock"}

@app.put("/api/subscription/payment_method")
async def update_subscription_payment_method(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_subscription_payment_method", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_payment_method", "source": "mock"}

# Register/Login (6 endpoints)
@app.post("/api/auth/register")
async def register_user(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("register_user", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "register", "user_id": "mock_user_123", "source": "mock"}

@app.post("/api/auth/login")
async def login_user(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("login_user", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "login", "token": "mock_token_123", "source": "mock"}

@app.post("/api/auth/logout")
async def logout_user():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("logout_user", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "logout", "source": "mock"}

@app.post("/api/auth/refresh")
async def refresh_token(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("refresh_token", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "refresh", "new_token": "mock_new_token_123", "source": "mock"}

@app.get("/api/auth/profile")
async def get_user_profile():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_user_profile", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"profile": {}, "source": "mock"}

@app.put("/api/auth/profile")
async def update_user_profile(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_user_profile", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_profile", "source": "mock"}

# System (5 endpoints)
@app.get("/api/system/info")
async def get_system_info():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_system_info", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"system_info": {}, "source": "mock"}

@app.get("/api/system/health")
async def get_system_health():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_system_health", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"health": {}, "source": "mock"}

@app.post("/api/system/backup")
async def create_system_backup():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("create_system_backup", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "backup_created", "backup_id": "mock_backup_123", "source": "mock"}

@app.get("/api/system/logs")
async def get_system_logs(limit: int = 100):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_system_logs", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"logs": [], "limit": limit, "source": "mock"}

@app.post("/api/system/maintenance")
async def run_system_maintenance():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("run_system_maintenance", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "maintenance_started", "task_id": "mock_task_123", "source": "mock"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
# Группа 3: Мониторинг
#!/usr/bin/env python3
"""
Скрипт миграции Группы 3: Мониторинг (20 endpoints)
Загружает endpoints мониторинга в API Gateway
"""

import sys
import os

# Добавляем путь к backend
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def add_group3_endpoints():
    """Добавляет endpoints Группы 3 в api_gateway.py"""

    # Код Группы 3 для вставки
    group3_code = '''
# =============================================================================
# ГРУППА 3: МОНИТОРИНГ (20 endpoints)
# =============================================================================

# AI Categories (4 endpoints)
@app.get("/api/ai/categories/stats")
async def get_ai_categories_stats(child_id: str = None):
    params = {"child_id": child_id} if child_id else {}
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_ai_categories_stats", params)
        return result if success else {"error": message}
    else:
        return {"total_content": 0, "blocked_content": 0, "allowed_content": 0, "source": "mock"}

@app.get("/api/ai/categories/reports")
async def get_ai_categories_reports(child_id: str = None):
    params = {"child_id": child_id} if child_id else {}
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_ai_categories_reports", params)
        return result if success else {"error": message}
    else:
        return {"reports": [], "source": "mock"}

@app.post("/api/ai/categories/allow")
async def allow_ai_content(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_ai_content", data)
        return result if success else {"error": message}
    else:
        return {"action": "allow", "status": "mock_success", "source": "mock"}

@app.post("/api/ai/categories/block")
async def block_ai_content(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_ai_content", data)
        return result if success else {"error": message}
    else:
        return {"action": "block", "status": "mock_success", "source": "mock"}

# Data Cleanup (3 endpoints)
@app.get("/api/data/cleanup/stats")
async def get_data_cleanup_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_data_cleanup_stats", {})
        return result if success else {"error": message}
    else:
        return {"total_cleaned": 0, "last_cleanup": None, "source": "mock"}

@app.get("/api/data/cleanup/records")
async def get_data_cleanup_records(limit: int = 20):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_data_cleanup_records", {"limit": limit})
        return result if success else {"error": message}
    else:
        return {"records": [], "limit": limit, "source": "mock"}

@app.post("/api/data/cleanup/start")
async def start_data_cleanup(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("start_data_cleanup", data)
        return result if success else {"error": message}
    else:
        return {"action": "cleanup_started", "job_id": "mock_job_123", "source": "mock"}

# Location Tracking (4 endpoints)
@app.get("/api/location/stats")
async def get_location_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_location_stats", {})
        return result if success else {"error": message}
    else:
        return {"total_requests": 0, "allowed_requests": 0, "blocked_requests": 0, "source": "mock"}

@app.get("/api/location/requests")
async def get_location_requests(limit: int = 50):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_location_requests", {"limit": limit})
        return result if success else {"error": message}
    else:
        return {"requests": [], "limit": limit, "source": "mock"}

@app.post("/api/location/allow")
async def allow_location_request(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_location_request", data)
        return result if success else {"error": message}
    else:
        return {"action": "allow", "status": "mock_success", "source": "mock"}

@app.post("/api/location/block")
async def block_location_request(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_location_request", data)
        return result if success else {"error": message}
    else:
        return {"action": "block", "status": "mock_success", "source": "mock"}

@app.put("/api/location/accuracy")
async def update_location_accuracy(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_location_accuracy", data)
        return result if success else {"error": message}
    else:
        return {"action": "update_accuracy", "status": "mock_success", "source": "mock"}

# Dark Web Monitoring (5 endpoints)
@app.get("/api/darkweb/leaks")
async def get_darkweb_leaks(status: str = None, severity: str = None):
    params = {}
    if status: params["status"] = status
    if severity: params["severity"] = severity
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_darkweb_leaks", params)
        return result if success else {"error": message}
    else:
        return {"leaks": [], "total": 0, "source": "mock"}

@app.get("/api/darkweb/stats")
async def get_darkweb_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_darkweb_stats", {})
        return result if success else {"error": message}
    else:
        return {"total_scans": 0, "leaks_found": 0, "last_scan": None, "source": "mock"}

@app.get("/api/darkweb/scans")
async def get_darkweb_scans(limit: int = 20):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_darkweb_scans", {"limit": limit})
        return result if success else {"error": message}
    else:
        return {"scans": [], "limit": limit, "source": "mock"}

@app.post("/api/darkweb/resolve")
async def resolve_darkweb_leak(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("resolve_darkweb_leak", data)
        return result if success else {"error": message}
    else:
        return {"action": "resolve", "status": "mock_success", "source": "mock"}

@app.post("/api/darkweb/scan_start")
async def start_darkweb_scan():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("start_darkweb_scan", {})
        return result if success else {"error": message}
    else:
        return {"action": "scan_started", "scan_id": "mock_scan_123", "source": "mock"}

# Identity Theft (4 endpoints)
@app.get("/api/identity/attempts")
async def get_identity_attempts(action: str = None, severity: str = None):
    params = {}
    if action: params["action"] = action
    if severity: params["severity"] = severity
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_attempts", params)
        return result if success else {"error": message}
    else:
        return {"attempts": [], "total": 0, "source": "mock"}

@app.get("/api/identity/stats")
async def get_identity_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_stats", {})
        return result if success else {"error": message}
    else:
        return {"total_attempts": 0, "blocked_attempts": 0, "allowed_attempts": 0, "source": "mock"}

@app.post("/api/identity/allow")
async def allow_identity_attempt(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_identity_attempt", data)
        return result if success else {"error": message}
    else:
        return {"action": "allow", "status": "mock_success", "source": "mock"}

@app.post("/api/identity/block")
async def block_identity_attempt(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_identity_attempt", data)
        return result if success else {"error": message}
    else:
        return {"action": "block", "status": "mock_success", "source": "mock"}

@app.post("/api/identity/whitelist")
async def add_to_identity_whitelist(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("add_to_identity_whitelist", data)
        return result if success else {"error": message}
    else:
        return {"action": "whitelist", "status": "mock_success", "source": "mock"}

# =============================================================================
# КОНЕЦ ГРУППЫ 3
# =============================================================================
'''

    print("✅ Код Группы 3 подготовлен")
    print("📋 Группа 3 включает 20 endpoints:")
    print("   • AI Categories: 4 endpoints")
    print("   • Data Cleanup: 3 endpoints")
    print("   • Location Tracking: 4 endpoints")
    print("   • Dark Web Monitoring: 5 endpoints")
    print("   • Identity Theft: 4 endpoints")

    return group3_code

def test_group3_endpoints():
    """Тестирует endpoints Группы 3"""
    import requests

    base_url = "http://localhost:8002"
    test_token = "test_token"  # Заменить на реальный токен

    headers = {"Authorization": f"Bearer {test_token}"}

    endpoints_to_test = [
        "/api/ai/categories/stats",
        "/api/data/cleanup/stats",
        "/api/location/stats",
        "/api/darkweb/stats",
        "/api/identity/stats"
    ]

    print("\\n🧪 Тестирование endpoints Группы 3:")

    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Ошибка - {e}")

if __name__ == "__main__":
    print("🚀 МИГРАЦИЯ ГРУППЫ 3: МОНИТОРИНГ")
    print("=" * 50)

    # Получаем код Группы 3
    group3_code = add_group3_endpoints()

    print("\\n📝 Следующие шаги:")
    print("1. Скопировать код Группы 3 в api_gateway.py")
    print("2. Перезапустить API Gateway сервис")
    print("3. Протестировать endpoints")

    print("\\n💡 Для автоматической миграции запустите:")
    print("   python3 migrate_group3.py --apply")

    # Если передан флаг --apply, применить миграцию
    if "--apply" in sys.argv:
        print("\\n🔧 Применение миграции...")

        # Читаем текущий api_gateway.py
        api_gateway_path = "/opt/aladdin-backend/api_gateway.py"
        try:
            with open(api_gateway_path, 'r') as f:
                content = f.read()

            # Находим место для вставки (после Группы 2)
            insert_marker = "# =============================================================================\\n# ГРУППА 4: ЗАЩИТА (25 endpoints) - ЗАГЛУШКИ\\n# ============================================================================="

            if insert_marker in content:
                # Вставляем код Группы 3 перед Группой 4
                new_content = content.replace(insert_marker, group3_code + "\\n" + insert_marker)

                # Записываем обратно
                with open(api_gateway_path, 'w') as f:
                    f.write(new_content)

                print("✅ Код Группы 3 добавлен в api_gateway.py")

                # Перезапускаем сервис
                print("🔄 Перезапуск API Gateway...")
                os.system("systemctl restart aladdin-api-gateway")

                # Тестируем
                test_group3_endpoints()

                print("\\n🎉 МИГРАЦИЯ ГРУППЫ 3 ЗАВЕРШЕНА!")

            else:
                print("❌ Не найден маркер вставки в api_gateway.py")

        except Exception as e:
            print(f"❌ Ошибка миграции: {e}")

    print("\\n" + "=" * 50)


# Группа 4: Защита
#!/usr/bin/env python3
"""
Скрипт миграции Группы 4: Защита (25 endpoints)
Заменяет заглушки на SFM интеграцию
"""

import sys
import os
import re

# Добавляем путь к backend
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def get_group4_code():
    """Возвращает код Группы 4 с SFM интеграцией"""
    
    group4_code = '''# =============================================================================
# ГРУППА 4: ЗАЩИТА (25 endpoints)
# =============================================================================

# Identity Theft (8 endpoints)
@app.get("/api/identity/theft/attempts")
async def get_identity_theft_attempts(action: str = None, severity: str = None):
    params = {}
    if action: params["action"] = action
    if severity: params["severity"] = severity
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_theft_attempts", params)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"attempts": [], "source": "mock"}

@app.get("/api/identity/theft/stats")
async def get_identity_theft_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_theft_stats", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"stats": {}, "source": "mock"}

@app.post("/api/identity/theft/allow/{attempt_id}")
async def allow_identity_theft_attempt(attempt_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_identity_theft_attempt", {"attempt_id": attempt_id})
        return result if success else {"error": message, "attempt_id": attempt_id, "source": "mock"}
    else:
        return {"action": "allow", "attempt_id": attempt_id, "source": "mock"}

@app.post("/api/identity/theft/block/{attempt_id}")
async def block_identity_theft_attempt(attempt_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_identity_theft_attempt", {"attempt_id": attempt_id})
        return result if success else {"error": message, "attempt_id": attempt_id, "source": "mock"}
    else:
        return {"action": "block", "attempt_id": attempt_id, "source": "mock"}

@app.post("/api/identity/theft/whitelist")
async def add_identity_theft_whitelist(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("add_identity_theft_whitelist", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "whitelist", "source": "mock"}

@app.get("/api/identity/theft/history")
async def get_identity_theft_history(limit: int = 50):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_identity_theft_history", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"history": [], "limit": limit, "source": "mock"}

@app.post("/api/identity/theft/report/{attempt_id}")
async def report_identity_theft_attempt(attempt_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("report_identity_theft_attempt", {"attempt_id": attempt_id})
        return result if success else {"error": message, "attempt_id": attempt_id, "source": "mock"}
    else:
        return {"action": "report", "attempt_id": attempt_id, "source": "mock"}

@app.put("/api/identity/theft/settings")
async def update_identity_theft_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_identity_theft_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

# Anti Tracker (9 endpoints)
@app.get("/api/antitracker/trackers")
async def get_antitracker_trackers():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_antitracker_trackers", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"trackers": [], "source": "mock"}

@app.post("/api/antitracker/block/{tracker_id}")
async def block_antitracker_tracker(tracker_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("block_antitracker_tracker", {"tracker_id": tracker_id})
        return result if success else {"error": message, "tracker_id": tracker_id, "source": "mock"}
    else:
        return {"action": "block", "tracker_id": tracker_id, "source": "mock"}

@app.post("/api/antitracker/allow/{tracker_id}")
async def allow_antitracker_tracker(tracker_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("allow_antitracker_tracker", {"tracker_id": tracker_id})
        return result if success else {"error": message, "tracker_id": tracker_id, "source": "mock"}
    else:
        return {"action": "allow", "tracker_id": tracker_id, "source": "mock"}

@app.get("/api/antitracker/stats")
async def get_antitracker_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_antitracker_stats", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"stats": {}, "source": "mock"}

@app.post("/api/antitracker/whitelist")
async def add_antitracker_whitelist(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("add_antitracker_whitelist", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "whitelist", "source": "mock"}

@app.get("/api/antitracker/categories")
async def get_antitracker_categories():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_antitracker_categories", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"categories": [], "source": "mock"}

@app.put("/api/antitracker/category/{category_id}")
async def update_antitracker_category(category_id: str, settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        params = {"category_id": category_id, **settings}
        success, result, message = sfm_adapter.execute_function("update_antitracker_category", params)
        return result if success else {"error": message, "category_id": category_id, "source": "mock"}
    else:
        return {"action": "update_category", "category_id": category_id, "source": "mock"}

@app.post("/api/antitracker/scan")
async def scan_antitracker():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("scan_antitracker", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "scan_started", "scan_id": "mock_scan_123", "source": "mock"}

@app.get("/api/antitracker/reports")
async def get_antitracker_reports(limit: int = 20):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_antitracker_reports", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"reports": [], "limit": limit, "source": "mock"}

# Parental Control (5 endpoints)
@app.get("/api/parental/stats")
async def get_parental_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_parental_stats", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"stats": {}, "source": "mock"}

@app.put("/api/parental/settings")
async def update_parental_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_parental_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

@app.post("/api/parental/restrict/{child_id}")
async def restrict_parental_child(child_id: str, restrictions: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        params = {"child_id": child_id, **restrictions}
        success, result, message = sfm_adapter.execute_function("restrict_parental_child", params)
        return result if success else {"error": message, "child_id": child_id, "source": "mock"}
    else:
        return {"action": "restrict", "child_id": child_id, "source": "mock"}

@app.get("/api/parental/activity/{child_id}")
async def get_parental_activity(child_id: str, limit: int = 50):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_parental_activity", {"child_id": child_id, "limit": limit})
        return result if success else {"error": message, "child_id": child_id, "source": "mock"}
    else:
        return {"activity": [], "child_id": child_id, "limit": limit, "source": "mock"}

@app.post("/api/parental/alert")
async def send_parental_alert(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("send_parental_alert", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "alert_sent", "source": "mock"}

# Roadside Assistance (3 endpoints)
@app.post("/api/roadside/emergency")
async def send_roadside_emergency(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("send_roadside_emergency", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "emergency_sent", "emergency_id": "mock_emergency_123", "source": "mock"}

@app.get("/api/roadside/history")
async def get_roadside_history(limit: int = 20):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_roadside_history", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"history": [], "limit": limit, "source": "mock"}

@app.put("/api/roadside/settings")
async def update_roadside_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_roadside_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

# =============================================================================
# КОНЕЦ ГРУППЫ 4
# =============================================================================
'''
    
    return group4_code

def apply_migration(file_path):
    """Применяет миграцию Группы 4 к файлу"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Находим начало Группы 4 (заглушки)
        group4_start_pattern = r'# =============================================================================\n# ГРУППА 4: ЗАЩИТА \(25 endpoints\) - ЗАГЛУШКИ\n# ============================================================================='
        
        # Находим конец Группы 4 (начало Группы 5)
        group4_end_pattern = r'# =============================================================================\n# ГРУППА 5: СИСТЕМА'
        
        # Проверяем наличие маркеров
        if not re.search(group4_start_pattern, content):
            print("❌ Не найден маркер начала Группы 4")
            return False
        
        if not re.search(group4_end_pattern, content):
            print("❌ Не найден маркер конца Группы 4")
            return False
        
        # Находим позиции
        start_match = re.search(group4_start_pattern, content)
        end_match = re.search(group4_end_pattern, content)
        
        if not start_match or not end_match:
            print("❌ Не удалось найти границы Группы 4")
            return False
        
        # Заменяем весь блок Группы 4
        start_pos = start_match.start()
        end_pos = end_match.start()
        
        new_content = (
            content[:start_pos] + 
            get_group4_code() + "\n" + 
            content[end_pos:]
        )
        
        # Записываем обратно
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Группа 4 мигрирована в {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        return False

def test_group4_endpoints():
    """Тестирует endpoints Группы 4"""
    import requests
    
    base_url = "http://localhost:8002"
    
    endpoints_to_test = [
        ("GET", "/api/identity/theft/stats"),
        ("GET", "/api/antitracker/stats"),
        ("GET", "/api/parental/stats"),
        ("GET", "/api/antitracker/trackers"),
        ("GET", "/api/antitracker/categories"),
    ]
    
    print("\n🧪 Тестирование endpoints Группы 4:")
    
    for method, endpoint in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{base_url}{endpoint}", json={}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                source = data.get("source", "unknown")
                print(f"✅ {method} {endpoint}: OK (source: {source})")
            else:
                print(f"❌ {method} {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint}: Ошибка - {e}")

if __name__ == "__main__":
    print("🚀 МИГРАЦИЯ ГРУППЫ 4: ЗАЩИТА")
    print("=" * 50)
    
    print("\n📋 Группа 4 включает 25 endpoints:")
    print("   • Identity Theft: 8 endpoints")
    print("   • Anti Tracker: 9 endpoints")
    print("   • Parental Control: 5 endpoints")
    print("   • Roadside Assistance: 3 endpoints")
    
    # Определяем путь к файлу
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        # На сервере
        api_gateway_path = "/opt/aladdin-backend/api_gateway.py"
    else:
        # Локально
        api_gateway_path = "api_gateway_complete.py"
    
    if "--apply" in sys.argv:
        print(f"\n🔧 Применение миграции к {api_gateway_path}...")
        
        if apply_migration(api_gateway_path):
            print("\n🔄 Перезапуск API Gateway...")
            os.system("systemctl restart aladdin-api-gateway 2>/dev/null || echo '⚠️  Не удалось перезапустить (возможно, локальный запуск)'")
            
            import time
            time.sleep(2)
            
            test_group4_endpoints()
            
            print("\n🎉 МИГРАЦИЯ ГРУППЫ 4 ЗАВЕРШЕНА!")
        else:
            print("\n❌ МИГРАЦИЯ НЕ УДАЛАСЬ")
    else:
        print("\n💡 Для применения миграции запустите:")
        print(f"   python3 migrate_group4.py --apply")
        print("\n📝 Код Группы 4 готов к применению")



# Группа 5: Система
#!/usr/bin/env python3
"""
Скрипт миграции Группы 5: Система (31 endpoint)
Заменяет заглушки на SFM интеграцию
"""

import sys
import os
import re

# Добавляем путь к backend
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def get_group5_code():
    """Возвращает код Группы 5 с SFM интеграцией"""
    
    group5_code = '''# =============================================================================
# ГРУППА 5: СИСТЕМА (31 endpoint)
# =============================================================================

# Notifications (8 endpoints)
@app.get("/api/notifications/list")
async def get_notifications_list(limit: int = 50):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_notifications_list", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"notifications": [], "limit": limit, "source": "mock"}

@app.post("/api/notifications/mark_read/{notification_id}")
async def mark_notification_read(notification_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("mark_notification_read", {"notification_id": notification_id})
        return result if success else {"error": message, "notification_id": notification_id, "source": "mock"}
    else:
        return {"action": "mark_read", "notification_id": notification_id, "source": "mock"}

@app.post("/api/notifications/delete/{notification_id}")
async def delete_notification(notification_id: str):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("delete_notification", {"notification_id": notification_id})
        return result if success else {"error": message, "notification_id": notification_id, "source": "mock"}
    else:
        return {"action": "delete", "notification_id": notification_id, "source": "mock"}

@app.put("/api/notifications/settings")
async def update_notifications_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_notifications_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

@app.post("/api/notifications/test")
async def test_notifications():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("test_notifications", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "test_sent", "source": "mock"}

@app.get("/api/notifications/stats")
async def get_notifications_stats():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_notifications_stats", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"stats": {}, "source": "mock"}

@app.post("/api/notifications/bulk_mark_read")
async def bulk_mark_notifications_read(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("bulk_mark_notifications_read", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "bulk_mark_read", "count": 0, "source": "mock"}

@app.get("/api/notifications/unread_count")
async def get_notifications_unread_count():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_notifications_unread_count", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"unread_count": 0, "source": "mock"}

# Analytics (6 endpoints)
@app.get("/api/analytics/overview")
async def get_analytics_overview(period: str = "month"):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_analytics_overview", {"period": period})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"overview": {}, "period": period, "source": "mock"}

@app.get("/api/analytics/security_events")
async def get_analytics_security_events(limit: int = 100):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_analytics_security_events", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"events": [], "limit": limit, "source": "mock"}

@app.get("/api/analytics/performance")
async def get_analytics_performance():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_analytics_performance", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"performance": {}, "source": "mock"}

@app.post("/api/analytics/export")
async def export_analytics(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("export_analytics", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "export_started", "export_id": "mock_export_123", "source": "mock"}

@app.get("/api/analytics/reports")
async def get_analytics_reports(type: str = "security"):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_analytics_reports", {"type": type})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"reports": [], "type": type, "source": "mock"}

@app.put("/api/analytics/settings")
async def update_analytics_settings(settings: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_analytics_settings", settings)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_settings", "source": "mock"}

# Subscription (6 endpoints)
@app.get("/api/subscription/status")
async def get_subscription_status():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_subscription_status", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"status": "active", "plan": "premium", "source": "mock"}

@app.get("/api/subscription/plans")
async def get_subscription_plans():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_subscription_plans", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"plans": [], "source": "mock"}

@app.post("/api/subscription/upgrade")
async def upgrade_subscription(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("upgrade_subscription", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "upgrade", "new_plan": "premium", "source": "mock"}

@app.post("/api/subscription/cancel")
async def cancel_subscription():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("cancel_subscription", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "cancel", "effective_date": "2024-12-31", "source": "mock"}

@app.get("/api/subscription/billing_history")
async def get_subscription_billing_history(limit: int = 12):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_subscription_billing_history", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"billing_history": [], "limit": limit, "source": "mock"}

@app.put("/api/subscription/payment_method")
async def update_subscription_payment_method(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_subscription_payment_method", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_payment_method", "source": "mock"}

# Register/Login (6 endpoints)
@app.post("/api/auth/register")
async def register_user(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("register_user", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "register", "user_id": "mock_user_123", "source": "mock"}

@app.post("/api/auth/login")
async def login_user(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("login_user", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "login", "token": "mock_token_123", "source": "mock"}

@app.post("/api/auth/logout")
async def logout_user():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("logout_user", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "logout", "source": "mock"}

@app.post("/api/auth/refresh")
async def refresh_token(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("refresh_token", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "refresh", "new_token": "mock_new_token_123", "source": "mock"}

@app.get("/api/auth/profile")
async def get_user_profile():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_user_profile", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"profile": {}, "source": "mock"}

@app.put("/api/auth/profile")
async def update_user_profile(data: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_user_profile", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "update_profile", "source": "mock"}

# System (5 endpoints)
@app.get("/api/system/info")
async def get_system_info():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_system_info", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"system_info": {}, "source": "mock"}

@app.get("/api/system/health")
async def get_system_health():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_system_health", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"health": {}, "source": "mock"}

@app.post("/api/system/backup")
async def create_system_backup():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("create_system_backup", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "backup_created", "backup_id": "mock_backup_123", "source": "mock"}

@app.get("/api/system/logs")
async def get_system_logs(limit: int = 100):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_system_logs", {"limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"logs": [], "limit": limit, "source": "mock"}

@app.post("/api/system/maintenance")
async def run_system_maintenance():
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("run_system_maintenance", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {"action": "maintenance_started", "task_id": "mock_task_123", "source": "mock"}

# =============================================================================
# КОНЕЦ ГРУППЫ 5
# =============================================================================
'''
    
    return group5_code

def apply_migration(file_path):
    """Применяет миграцию Группы 5 к файлу"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Находим начало Группы 5 (заглушки)
        group5_start_pattern = r'# =============================================================================\n# ГРУППА 5: СИСТЕМА \(31 endpoints\) - ЗАГЛУШКИ\n# ============================================================================='
        
        # Находим конец Группы 5 (if __name__ == "__main__")
        group5_end_pattern = r'if __name__ == "__main__":'
        
        # Проверяем наличие маркеров
        if not re.search(group5_start_pattern, content):
            print("❌ Не найден маркер начала Группы 5")
            return False
        
        if not re.search(group5_end_pattern, content):
            print("❌ Не найден маркер конца Группы 5")
            return False
        
        # Находим позиции
        start_match = re.search(group5_start_pattern, content)
        end_match = re.search(group5_end_pattern, content)
        
        if not start_match or not end_match:
            print("❌ Не удалось найти границы Группы 5")
            return False
        
        # Заменяем весь блок Группы 5
        start_pos = start_match.start()
        end_pos = end_match.start()
        
        new_content = (
            content[:start_pos] + 
            get_group5_code() + "\n" + 
            content[end_pos:]
        )
        
        # Записываем обратно
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Группа 5 мигрирована в {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_group5_endpoints():
    """Тестирует endpoints Группы 5"""
    import requests
    
    base_url = "http://localhost:8002"
    
    endpoints_to_test = [
        ("GET", "/api/notifications/unread_count"),
        ("GET", "/api/analytics/overview"),
        ("GET", "/api/subscription/status"),
        ("GET", "/api/system/info"),
        ("GET", "/api/system/health"),
    ]
    
    print("\n🧪 Тестирование endpoints Группы 5:")
    
    for method, endpoint in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{base_url}{endpoint}", json={}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                source = data.get("source", "unknown")
                print(f"✅ {method} {endpoint}: OK (source: {source})")
            else:
                print(f"❌ {method} {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint}: Ошибка - {e}")

if __name__ == "__main__":
    print("🚀 МИГРАЦИЯ ГРУППЫ 5: СИСТЕМА")
    print("=" * 50)
    
    print("\n📋 Группа 5 включает 31 endpoint:")
    print("   • Notifications: 8 endpoints")
    print("   • Analytics: 6 endpoints")
    print("   • Subscription: 6 endpoints")
    print("   • Register/Login: 6 endpoints")
    print("   • System: 5 endpoints")
    
    # Определяем путь к файлу
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        # На сервере
        api_gateway_path = "/opt/aladdin-backend/api_gateway.py"
    else:
        # Локально
        api_gateway_path = "api_gateway_complete.py"
    
    if "--apply" in sys.argv:
        print(f"\n🔧 Применение миграции к {api_gateway_path}...")
        
        if apply_migration(api_gateway_path):
            print("\n🔄 Перезапуск API Gateway...")
            os.system("systemctl restart aladdin-api-gateway 2>/dev/null || echo '⚠️  Не удалось перезапустить (возможно, локальный запуск)'")
            
            import time
            time.sleep(2)
            
            test_group5_endpoints()
            
            print("\n🎉 МИГРАЦИЯ ГРУППЫ 5 ЗАВЕРШЕНА!")
        else:
            print("\n❌ МИГРАЦИЯ НЕ УДАЛАСЬ")
    else:
        print("\n💡 Для применения миграции запустите:")
        print(f"   python3 migrate_group5.py --apply")
        print("\n📝 Код Группы 5 готов к применению")



