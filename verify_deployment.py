#!/usr/bin/env python3
# 🔍 Проверка деплоя auth.py на сервер

import urllib.request
import urllib.error
import ssl
import json

def check_api_with_device_token():
    """Проверка работы /api/family/stats с device token"""
    print("=" * 60)
    print("🔍 ПРОВЕРКА ДЕПЛОЯ auth.py НА СЕРВЕР")
    print("=" * 60)
    print()
    
    # Создаем SSL контекст без проверки сертификата
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # Проверка 1: Health endpoint
    print("📋 ПРОВЕРКА 1: Health endpoint")
    try:
        req = urllib.request.Request('https://aladdin-ai.ru/api/health')
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            health_data = response.read().decode()
            print(f"✅ Health check: {response.status} - {health_data[:100]}")
    except urllib.error.HTTPError as e:
        print(f"⚠️ Health check: {e.code} - {e.reason}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    print()
    
    # Проверка 2: Попытка проверить /api/family/stats
    # Но для этого нужен валидный device token
    print("📋 ПРОВЕРКА 2: /api/family/stats (требует токен)")
    print("   ⚠️ Для полной проверки нужен валидный device token")
    print("   Проверьте вручную:")
    print("   curl -H 'Authorization: Bearer DEVICE_TOKEN' https://aladdin-ai.ru/api/family/stats")
    print()
    
    # Проверка 3: Попытка проверить через SSH (если доступен)
    print("📋 ПРОВЕРКА 3: SSH доступность")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('149.154.65.180', 22))
        if result == 0:
            print("✅ SSH порт 22 открыт")
            sock.close()
        else:
            print("❌ SSH порт 22 недоступен")
    except Exception as e:
        print(f"❌ SSH проверка failed: {e}")
    print()
    
    print("=" * 60)
    print("📊 ВЫВОД:")
    print("=" * 60)
    print()
    print("Для подтверждения деплоя нужно:")
    print("1. ✅ Проверить что сервер отвечает (health check)")
    print("2. ✅ Проверить /api/family/stats с device token (должен вернуть 200 OK)")
    print("3. ✅ Проверить содержимое файла на сервере через SSH")
    print()
    print("Если другая ML система утверждает что деплой выполнен,")
    print("проверьте через тестовый запрос с device token!")

if __name__ == "__main__":
    check_api_with_device_token()
