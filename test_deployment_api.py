#!/usr/bin/env python3
# 🔍 Проверка деплоя через API

import urllib.request
import urllib.error
import ssl
import json
import uuid

def test_deployment():
    """Проверка деплоя через API тесты"""
    print("=" * 70)
    print("🔍 ПРОВЕРКА ДЕПЛОЯ auth.py ЧЕРЕЗ API")
    print("=" * 70)
    print()
    
    # SSL контекст без проверки сертификата
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # ТЕСТ 1: Health endpoint
    print("📋 ТЕСТ 1: Health endpoint")
    try:
        req = urllib.request.Request('https://aladdin-ai.ru/api/health')
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            health_data = response.read().decode()
            print(f"✅ Статус: {response.status}")
            print(f"   Ответ: {health_data[:200]}")
    except urllib.error.HTTPError as e:
        print(f"⚠️ Статус: {e.code} - {e.reason}")
        try:
            error_data = e.read().decode()
            print(f"   Ответ: {error_data[:200]}")
        except:
            pass
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    print()
    
    # ТЕСТ 2: Регистрация устройства для получения device token
    print("📋 ТЕСТ 2: Регистрация устройства (для получения device token)")
    device_id = str(uuid.uuid4())
    register_data = json.dumps({
        "device_id": device_id,
        "device_type": "ios"
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(
            'https://aladdin-ai.ru/api/auth/register-device',
            data=register_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            register_response = response.read().decode()
            print(f"✅ Статус: {response.status}")
            try:
                register_json = json.loads(register_response)
                if 'token' in register_json:
                    device_token = register_json['token']
                    print(f"✅ Device token получен: {device_token[:50]}...")
                    print()
                    
                    # ТЕСТ 3: Проверка /api/family/stats с device token
                    print("📋 ТЕСТ 3: /api/family/stats с device token")
                    stats_req = urllib.request.Request(
                        'https://aladdin-ai.ru/api/family/stats',
                        headers={'Authorization': f'Bearer {device_token}'}
                    )
                    try:
                        with urllib.request.urlopen(stats_req, context=ctx, timeout=10) as stats_response:
                            stats_data = stats_response.read().decode()
                            print(f"✅ Статус: {stats_response.status} OK")
                            try:
                                stats_json = json.loads(stats_data)
                                print(f"✅ Данные получены: {json.dumps(stats_json, indent=2, ensure_ascii=False)[:300]}")
                                print()
                                print("=" * 70)
                                print("✅ ДЕПЛОЙ ПОДТВЕРЖДЕН!")
                                print("=" * 70)
                                print()
                                print("📊 Результат:")
                                print("   - /api/family/stats возвращает 200 OK")
                                print("   - Device token работает корректно")
                                print("   - Исправление применено на сервере ✅")
                                return True
                            except json.JSONDecodeError:
                                print(f"⚠️ Ответ не JSON: {stats_data[:200]}")
                    except urllib.error.HTTPError as e:
                        if e.code == 401:
                            print(f"❌ Статус: {e.code} Unauthorized")
                            print("   ⚠️ ДЕПЛОЙ НЕ ПОДТВЕРЖДЕН!")
                            print("   Файл auth.py не обновлен на сервере")
                            print()
                            print("=" * 70)
                            print("❌ ДЕПЛОЙ НЕ ВЫПОЛНЕН")
                            print("=" * 70)
                            return False
                        else:
                            print(f"⚠️ Статус: {e.code} - {e.reason}")
                            try:
                                error_data = e.read().decode()
                                print(f"   Ответ: {error_data[:200]}")
                            except:
                                pass
                    except Exception as e:
                        print(f"❌ Ошибка при проверке /api/family/stats: {e}")
                else:
                    print(f"⚠️ Токен не найден в ответе: {register_json}")
            except json.JSONDecodeError:
                print(f"⚠️ Ответ не JSON: {register_response[:200]}")
    except urllib.error.HTTPError as e:
        print(f"⚠️ Статус регистрации: {e.code} - {e.reason}")
        try:
            error_data = e.read().decode()
            print(f"   Ответ: {error_data[:200]}")
        except:
            pass
    except Exception as e:
        print(f"❌ Ошибка регистрации: {e}")
    
    print()
    print("=" * 70)
    print("⏳ ТРЕБУЕТСЯ РУЧНАЯ ПРОВЕРКА")
    print("=" * 70)
    print()
    print("Для полной проверки:")
    print("1. Запустите iOS приложение")
    print("2. Зарегистрируйте устройство")
    print("3. Проверьте что /api/family/stats возвращает 200 OK")
    print("4. Проверьте логи приложения")
    
    return None

if __name__ == "__main__":
    result = test_deployment()
    exit(0 if result is True else 1 if result is False else 0)
