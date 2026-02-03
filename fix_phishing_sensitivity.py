#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ PHISHING SENSITIVITY НА РЕАЛЬНЫЙ SFM ВЫЗОВ
Шаг 1/93 в плане 100% реальной защиты
"""

import re

def fix_phishing_sensitivity():
    """Исправить phishing sensitivity эндпоинт"""

    # Read the file
    with open('/opt/aladdin-backend/api_gateway.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Old hardcoded implementation
    old_phishing = '''@app.get("/api/phishing/sensitivity")
async def get_phishing_sensitivity():
    """
    ✅ WORKING: Real SFM-style response with protection data
    This endpoint now returns REAL PROTECTION DATA in SFM format
    """
    # REAL PROTECTION DATA - SFM STYLE RESPONSE
    return {
        "sensitivity_level": "high",
        "detection_mode": "aggressive",
        "active_rules_count": 15,
        "blocked_phishing_attempts": 15420,
        "suspicious_sites_detected": 8750,
        "false_positive_rate": 0.02,
        "last_model_update": "2026-02-02T12:00:00Z",
        "ml_model_version": "2.1.0",
        "protection_status": "ACTIVE",
        "source": "sfm_real_protection",  # REAL SFM DATA MARKER
        "confidence_score": 0.97,
        "response_time_ms": 45
    }'''

    # New SFM implementation
    new_phishing = '''@app.get("/api/phishing/sensitivity")
async def get_phishing_sensitivity():
    """
    ✅ REAL SFM PROTECTION: Get phishing sensitivity configuration
    Returns real-time phishing protection settings from SFM
    """
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function(
            "get_phishing_protection_config", {}
        )
        if success:
            return result
        else:
            return {"error": message, "status": "sfm_error"}
    else:
        return {"error": "SFM adapter unavailable", "status": "fallback"}'''

    # Replace
    if old_phishing in content:
        content = content.replace(old_phishing, new_phishing)

        # Write back
        with open('/opt/aladdin-backend/api_gateway.py', 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ ШАГ 1/93: Phishing sensitivity исправлен на реальный SFM вызов")
        print("🔄 Теперь endpoint /api/phishing/sensitivity будет возвращать РЕАЛЬНЫЕ данные из SFM")
        return True
    else:
        print("❌ Не найден старый код phishing sensitivity")
        return False

if __name__ == "__main__":
    success = fix_phishing_sensitivity()
    exit(0 if success else 1)