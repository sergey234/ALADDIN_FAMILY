import requests
import json
import time
from datetime import datetime
import sys

# Конфигурация
BASE_URL = "http://149.154.65.180:8002"
OPENAPI_URL = f"{BASE_URL}/openapi.json"
AUTH_URL = f"{BASE_URL}/api/auth/login"
DEVICE_ID = "tester_device_v1"

# Статистика
STATS = {
    "total": 0,
    "success": 0,
    "auth_error": 0,  # 401/403 (считаем живыми)
    "not_found": 0,   # 404
    "server_error": 0, # 500+
    "skipped": 0
}

def print_header(text):
    print(f"\n{'='*60}\n🚀 {text}\n{'='*60}")

def get_jwt_token():
    print("🔑 Авторизация...")
    try:
        # Сначала регистрируемся (на случай если устройства нет)
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "device_id": DEVICE_ID,
            "device_type": "script"
        })
        
        # Логинимся
        resp = requests.post(AUTH_URL, json={"device_id": DEVICE_ID})
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            print(f"✅ Токен получен: {token[:15]}...")
            return token
        else:
            print(f"❌ Ошибка авторизации: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

def fetch_endpoints():
    print("📥 Загрузка списка эндпоинтов с сервера...")
    try:
        resp = requests.get(OPENAPI_URL)
        if resp.status_code != 200:
            print(f"❌ Не удалось получить OpenAPI: {resp.status_code}")
            return {}
        
        data = resp.json()
        paths = data.get("paths", {})
        print(f"✅ Найдено {len(paths)} путей")
        return paths
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return {}

def test_endpoint(path, method, token):
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        # Подготовка данных для POST/PUT
        json_data = {}
        if method.lower() in ["post", "put"]:
            if "auth" in path: 
                json_data = {"device_id": DEVICE_ID, "device_type": "script"}
            elif "scan" in path: 
                json_data = {"files": [], "scan_type": "quick"}
            elif "check" in path:
                json_data = {"url": "https://example.com"}
            elif "monitor" in path:
                json_data = {"target": "test@example.com"}
            elif "detect" in path:
                json_data = {"data": "test_data"}
            elif "report" in path:
                json_data = {"type": "weekly"}
            else:
                json_data = {"dummy": "data"} # Send something to avoid 422 empty body if required
            
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            timeout=10 # Increased timeout
        )
        return response.status_code, response.reason
    except Exception as e:
        return 0, str(e)

def run_tests():
    print_header("ЗАПУСК УМНОГО ТЕСТИРОВАНИЯ API")
    
    token = get_jwt_token()
    if not token:
        print("🛑 Тестирование невозможно без токена")
        return

    paths = fetch_endpoints()
    STATS["total"] = len(paths)
    
    print("\n🔍 НАЧИНАЕМ ПРОВЕРКУ (по 5 в блоке)...")
    
    results = []
    
    count = 0
    for path, methods in paths.items():
        for method in methods:
            count += 1
            status, reason = test_endpoint(path, method, token)
            
            # Анализ результата
            icon = "❓"
            if 200 <= status < 300:
                STATS["success"] += 1
                icon = "✅"
            elif status in [401, 403, 422]: # 422 - ошибка валидации, значит эндпоинт ЕСТЬ
                STATS["auth_error"] += 1
                icon = "⚠️" # Живой, но требует данных
            elif status == 404:
                STATS["not_found"] += 1
                icon = "❌"
            elif status >= 500:
                STATS["server_error"] += 1
                icon = "🔥"
            elif status == 405: # Method Not Allowed
                STATS["skipped"] += 1
                icon = "⏩"
            
            print(f"{count}. {icon} [{status}] {method.upper()} {path}")
            
            results.append({
                "path": path,
                "method": method,
                "status": status,
                "icon": icon
            })
            
            # Пауза каждые 10 запросов
            if count % 10 == 0:
                time.sleep(0.5)

    # Генерация отчета
    print_header("ИТОГОВЫЙ ОТЧЕТ")
    print(f"📊 Всего эндпоинтов: {STATS['total']}")
    print(f"✅ Успешно (200-299): {STATS['success']}")
    print(f"⚠️ Живые (401/403/422): {STATS['auth_error']}")
    print(f"❌ Не найдены (404): {STATS['not_found']}")
    print(f"🔥 Ошибки сервера (500+): {STATS['server_error']}")
    
    live_total = STATS['success'] + STATS['auth_error']
    print(f"\n🏆 РЕАЛЬНО ЖИВЫХ ЭНДПОИНТОВ: {live_total} / {STATS['total']}")
    
    # Сохранение в файл
    with open("api_test_results.md", "w") as f:
        f.write(f"# 📊 API TEST REPORT - {datetime.now()}\n\n")
        f.write(f"**Total:** {STATS['total']} | **Live:** {live_total} | **Dead:** {STATS['not_found']}\n\n")
        f.write("| Status | Method | Path |\n")
        f.write("|--------|--------|------|\n")
        for r in results:
            f.write(f"| {r['icon']} {r['status']} | {r['method'].upper()} | `{r['path']}` |\n")
            
    print("\n📄 Полный отчет сохранен в api_test_results.md")

if __name__ == "__main__":
    run_tests()
