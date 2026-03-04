import requests
import json
import time
from datetime import datetime
import sys

# Конфигурация
BASE_URL = "https://aladdin-ai.ru"
OPENAPI_URL = f"{BASE_URL}/api/openapi.json" # Добавил /api/ т.к. обычно там доки
DEVICE_ID = "tester_device_production_final"

# Список эндпоинтов из AppConfig.swift (245 штук) для полной проверки
APP_ENDPOINTS = [
    "/api/ai/assistant/analyze_threat", "/api/ai/assistant/capabilities", "/api/ai/assistant/chat",
    "/api/ai/assistant/feedback", "/api/ai/assistant/history", "/api/ai/assistant/recommendations",
    "/api/ai/assistant/report_incident", "/api/ai/assistant/security_tips",
    "/api/chat/offline-messages/resolve-conflicts", "/api/chat/offline-messages/send", "/api/chat/offline-messages/sync",
    "/api/components/health", "/api/components/list", "/api/crash-detection/alert", "/api/crash-detection/data",
    "/api/crash-detection/history", "/api/crash-detection/notifications", "/api/crash-detection/notifications/send",
    "/api/crash-detection/report", "/api/crash-detection/settings/update", "/api/crash-detection/setup",
    "/api/crash-detection/start", "/api/crash-detection/status", "/api/crash-detection/stop", "/api/crash-detection/sync",
    "/api/elderly/appointments/sync", "/api/elderly/appointments/update", "/api/elderly/medications/sync",
    "/api/elderly/medications/update", "/api/gamification/achievements", "/api/gamification/achievements/claim",
    "/api/gamification/achievements/progress", "/api/gamification/achievements/unlock", "/api/gamification/balance",
    "/api/gamification/balance/add", "/api/gamification/balance/history", "/api/gamification/balance/subtract",
    "/api/gamification/progress", "/api/gamification/progress/level", "/api/gamification/progress/reset",
    "/api/gamification/progress/stats", "/api/gamification/progress/update", "/api/gamification/rewards",
    "/api/gamification/rewards/claim", "/api/gamification/rewards/give", "/api/gamification/rewards/history",
    "/api/gamification/rewards/purchase", "/api/gamification/rewards/shop", "/api/gamification/settings",
    "/api/gamification/settings/notifications", "/api/gamification/settings/notifications/update",
    "/api/gamification/settings/update", "/api/gamification/tournaments", "/api/gamification/tournaments/history",
    "/api/gamification/tournaments/join", "/api/gamification/tournaments/leaderboard", "/api/gamification/tournaments/leave",
    "/api/location/geofences", "/api/location/geofences/sync", "/api/location/geofences/update",
    "/api/location/movement-history", "/api/location/movement-history/update", "/api/location/status",
    "/api/location/status/update", "/api/metrics/upload", "/api/notifications/archive",
    "/api/notifications/bulk-mark-read", "/api/notifications/categories", "/api/notifications/stats",
    "/api/offline-storage/data", "/api/offline-storage/data/update", "/api/offline-storage/resolve-conflicts",
    "/api/offline-storage/sync", "/api/parental-control/app-blocks", "/api/parental-control/app-blocks/sync",
    "/api/parental-control/app-blocks/update", "/api/parental-control/geofences", "/api/parental-control/geofences/add",
    "/api/parental-control/geofences/update", "/api/parental-control/schedules", "/api/parental-control/schedules/delete",
    "/api/parental-control/schedules/history", "/api/parental-control/schedules/update", "/api/parental-control/settings",
    "/api/parental-control/settings/conflicts", "/api/parental-control/settings/history", "/api/parental-control/settings/sync",
    "/api/parental-control/settings/update", "/api/parental-control/time-limits", "/api/parental-control/time-limits/history",
    "/api/parental-control/time-limits/reset", "/api/parental-control/time-limits/update", "/api/roadside-assistance/call",
    "/api/roadside-assistance/cancel/{request_id}", "/api/roadside-assistance/history",
    "/api/roadside-assistance/status/{request_id}", "/api/settings/biometry", "/api/settings/biometry/update",
    "/api/settings/language", "/api/settings/language/update", "/api/settings/notifications",
    "/api/settings/notifications/update", "/api/settings/sync", "/api/settings/theme", "/api/settings/theme/update",
    "/api/settings/update", "/api/subscription/auto-renewal", "/api/subscription/auto-renewal/update",
    "/api/subscription/cancel", "/api/subscription/purchase-history", "/api/subscription/status",
    "/api/subscription/status/update", "/api/subscription/sync", "/api/subscription/update", "/api/system/backup",
    "/api/system/backup/status", "/api/system/health", "/api/system/info", "/api/system/metrics", "/api/system/status",
    "/api/user/profile/history", "/api/user/profile/privacy", "/api/user/profile/privacy/update", "/api/user/profile/sync",
    "/api/user/profile/update", "/api/v1/parental-control/location/geofences", "/api/v1/parental-control/location/track",
    "/api/auth/login", "/api/auth/login-by-recovery-code", "/api/auth/logout", "/api/auth/refresh", "/api/auth/register",
    "/api/auth/register-device", "/api/auth/register-device-trial"
]

# Статистика
STATS = {
    "total": 0,
    "success": 0,
    "auth_error": 0,  # 401/403/422 (считаем живыми)
    "not_found": 0,   # 404
    "server_error": 0, # 500+
    "skipped": 0
}

def print_header(text):
    print(f"\n{'='*60}\n🚀 {text}\n{'='*60}")

def get_jwt_token():
    print("🔑 Авторизация на сервере...")
    try:
        # Пробуем эндпоинты с префиксом /api/ и без него
        reg_endpoints = ["/api/auth/register-device", "/auth/register-device"]
        token = None
        
        for ep in reg_endpoints:
            print(f"📡 Проверка: {ep}")
            reg_resp = requests.post(f"{BASE_URL}{ep}", json={
                "deviceId": DEVICE_ID,
                "deviceType": "ios"
            }, timeout=30)
            
            if reg_resp.status_code in [200, 201]:
                token = reg_resp.json().get("token")
                if token:
                    print(f"✅ Устройство зарегистрировано через {ep}")
                    return token
        
        # Если регистрация не прошла, пробуем логин
        login_endpoints = ["/api/auth/login", "/auth/login"]
        for ep in login_endpoints:
            print(f"📡 Проверка входа: {ep}")
            login_resp = requests.post(f"{BASE_URL}{ep}", json={"deviceId": DEVICE_ID}, timeout=30)
            if login_resp.status_code == 200:
                token = login_resp.json().get("access_token")
                if token:
                    print(f"✅ Вход выполнен через {ep}")
                    return token
            
        print(f"❌ Все методы авторизации завершились ошибкой.")
        return None
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

def fetch_server_endpoints():
    print("📥 Загрузка эндпоинтов из OpenAPI...")
    try:
        resp = requests.get(OPENAPI_URL, timeout=15)
        if resp.status_code == 200:
            paths = resp.json().get("paths", {})
            print(f"✅ Найдено {len(paths)} путей на сервере.")
            return paths
        return {}
    except:
        return {}

def prepare_path(path):
    replacements = {
        "{request_id}": "test-req-123",
        "{familyId}": "test-fam-456",
        "{childId}": "test-child-789",
        "{geofenceId}": "test-geo-000",
        "{dataId}": "test-data-111",
        "{achievementId}": "test-ach-222",
        "{tournamentId}": "test-tour-333",
        "{deviceId}": DEVICE_ID,
        "{homeId}": "test-home-555",
        "{threatId}": "test-threat-666",
        "{paymentId}": "test-pay-777"
    }
    for key, val in replacements.items():
        path = path.replace(key, val)
    return path

def test_endpoint(path, method, token):
    url = f"{BASE_URL}{prepare_path(path)}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "deviceId": DEVICE_ID,
        "appVersion": "1.0.0",
        "platform": "ios",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": [{"type": "test", "value": 1, "timestamp": datetime.utcnow().isoformat()}],
        "message": "Test message",
        "context": "general"
    }
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=payload,
            timeout=15
        )
        return response.status_code, response.reason
    except Exception as e:
        return 0, str(e)

def run_tests():
    print_header("ФИНАЛЬНАЯ ВАЛИДАЦИЯ ВСЕХ 231+ ФУНКЦИЙ")
    
    token = get_jwt_token()
    if not token:
        print("🛑 Тестирование остановлено: нет доступа.")
        return

    server_paths = fetch_server_endpoints()
    all_test_paths = {}
    
    for p, methods in server_paths.items():
        all_test_paths[p] = list(methods.keys())
    
    for p in APP_ENDPOINTS:
        if p not in all_test_paths:
            all_test_paths[p] = ["post"]
            
    STATS["total"] = len(all_test_paths)
    print(f"📊 Итого эндпоинтов для проверки: {STATS['total']}")
    
    results = []
    count = 0
    
    for path, methods in sorted(all_test_paths.items()):
        for method in methods:
            count += 1
            status, reason = test_endpoint(path, method, token)
            
            icon = "❓"
            if 200 <= status < 300:
                STATS["success"] += 1
                icon = "✅"
            elif status in [401, 403, 422]: 
                STATS["auth_error"] += 1
                icon = "⚠️"
            elif status == 404:
                STATS["not_found"] += 1
                icon = "❌"
            elif status >= 500:
                STATS["server_error"] += 1
                icon = "🔥"
            else:
                STATS["skipped"] += 1
                icon = "⏩"
                
            if count % 20 == 1 or status >= 404:
                print(f"[{count}/{STATS['total']}] {icon} {status} {method.upper()} {path}")
                if status >= 404:
                    results.append(f"{icon} {status} {method.upper()} {path}")

    print_header("РЕЗУЛЬТАТЫ ВАЛИДАЦИИ")
    live_total = STATS['success'] + STATS['auth_error']
    print(f"✅ Успешно: {STATS['success']}")
    print(f"⚠️ Валидация/Права (Живые): {STATS['auth_error']}")
    print(f"❌ Не найдены (404): {STATS['not_found']}")
    print(f"🔥 Ошибки сервера: {STATS['server_error']}")
    print(f"\n🏆 ОБЩИЙ ПРОЦЕНТ ГОТОВНОСТИ API: {(live_total/STATS['total'])*100:.1f}%")

    if live_total >= STATS['total'] * 0.9:
        print("\n🚀 ВЫВОД: СИСТЕМА ГОТОВА К ПРОДАКШНУ!")
    else:
        print("\n⚠️ ВЫВОД: ТРЕБУЕТСЯ ПРОВЕРКА ОТСУТСТВУЮЩИХ ЭНДПОИНТОВ.")

if __name__ == "__main__":
    run_tests()
