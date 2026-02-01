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



