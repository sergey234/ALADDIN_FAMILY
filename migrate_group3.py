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


