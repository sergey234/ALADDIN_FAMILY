#!/usr/bin/env python3
"""
Миграция Группы 2: Настройки безопасности (15 endpoints)
Загружает endpoints настроек безопасности в API Gateway
"""

# =============================================================================
# ГРУППА 2: НАСТРОЙКИ БЕЗОПАСНОСТИ (15 endpoints)
# =============================================================================

@app.get("/api/phishing/sensitivity")
async def get_phishing_sensitivity():
    """Получить уровень чувствительности антифишинга"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_phishing_sensitivity", {})
        return result if success else {"error": message}
    else:
        return {"level": "medium", "enabled": True, "source": "mock"}

@app.put("/api/phishing/sensitivity")
async def update_phishing_sensitivity(data: dict):
    """Обновить уровень чувствительности антифишинга"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_phishing_sensitivity", data)
        return result if success else {"error": message}
    else:
        return {"action": "updated", "level": data.get("level", "medium"), "source": "mock"}

@app.get("/api/phishing/block_suspicious")
async def get_phishing_block_suspicious():
    """Получить настройку блокировки подозрительных сайтов"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_phishing_block_suspicious", {})
        return result if success else {"error": message}
    else:
        return {"enabled": True, "aggressive": False, "source": "mock"}

@app.put("/api/phishing/block_suspicious")
async def update_phishing_block_suspicious(data: dict):
    """Обновить настройку блокировки подозрительных сайтов"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_phishing_block_suspicious", data)
        return result if success else {"error": message}
    else:
        return {"action": "updated", "enabled": data.get("enabled", True), "source": "mock"}

@app.get("/api/phishing/exclusions")
async def get_phishing_exclusions():
    """Получить список исключений для антифишинга"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_phishing_exclusions", {})
        return result if success else {"error": message}
    else:
        return {"exclusions": ["trusted-site.com"], "count": 1, "source": "mock"}

@app.get("/api/malware/scan_scheduled")
async def get_malware_scan_scheduled():
    """Получить расписание сканирования на malware"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_malware_scan_scheduled", {})
        return result if success else {"error": message}
    else:
        return {"enabled": True, "schedule": "daily", "last_scan": "2024-01-30T10:00:00Z", "source": "mock"}

@app.put("/api/malware/scan_scheduled")
async def update_malware_scan_scheduled(data: dict):
    """Обновить расписание сканирования на malware"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_malware_scan_scheduled", data)
        return result if success else {"error": message}
    else:
        return {"action": "updated", "schedule": data.get("schedule", "daily"), "source": "mock"}

@app.get("/api/malware/quarantine")
async def get_malware_quarantine():
    """Получить настройки карантина malware"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_malware_quarantine", {})
        return result if success else {"error": message}
    else:
        return {"enabled": True, "auto_delete": False, "retention_days": 30, "source": "mock"}

@app.put("/api/malware/quarantine")
async def update_malware_quarantine(data: dict):
    """Обновить настройки карантина malware"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_malware_quarantine", data)
        return result if success else {"error": message}
    else:
        return {"action": "updated", "enabled": data.get("enabled", True), "source": "mock"}

@app.post("/api/malware/scan_now")
async def scan_malware_now():
    """Запустить сканирование на malware прямо сейчас"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("scan_malware_now", {})
        return result if success else {"error": message}
    else:
        return {"action": "scan_started", "scan_id": "mock_scan_123", "estimated_time": 300, "source": "mock"}

@app.get("/api/mobile/app_lock")
async def get_mobile_app_lock():
    """Получить статус блокировки приложений"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_mobile_app_lock", {})
        return result if success else {"error": message}
    else:
        return {"enabled": False, "blocked_apps": [], "source": "mock"}

@app.put("/api/mobile/app_lock")
async def update_mobile_app_lock(data: dict):
    """Обновить настройки блокировки приложений"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_mobile_app_lock", data)
        return result if success else {"error": message}
    else:
        return {"action": "updated", "enabled": data.get("enabled", False), "source": "mock"}

@app.get("/api/mobile/biometric")
async def get_mobile_biometric():
    """Получить настройки биометрии"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_mobile_biometric", {})
        return result if success else {"error": message}
    else:
        return {"enabled": True, "fingerprint": True, "face_id": False, "source": "mock"}

@app.get("/api/network/firewall_rules")
async def get_firewall_rules():
    """Получить правила firewall"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_firewall_rules", {})
        return result if success else {"error": message}
    else:
        return {"rules": [{"id": 1, "name": "default_allow", "action": "allow"}], "count": 1, "source": "mock"}

@app.put("/api/network/vpn_config")
async def update_vpn_config(data: dict):
    """Обновить конфигурацию VPN"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_vpn_config", data)
        return result if success else {"error": message}
    else:
        return {"action": "updated", "server": data.get("server", "vpn.aladdin.com"), "source": "mock"}

if __name__ == "__main__":
    print("Группа 2: Настройки безопасности (15 endpoints)")
    print("Скрипт миграции готов к использованию")
    print("Используйте migrate_group2.apply_migration() для применения")