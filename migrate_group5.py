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



