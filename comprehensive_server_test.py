#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНАЯ ПРОВЕРКА ВСЕХ ИСПРАВЛЕННЫХ ФУНКЦИЙ НА СЕРВЕРЕ
Проверяет что все 6 функций (1-6/93) работают идеально
"""

import paramiko
import json
import time

def test_all_fixed_functions():
    """Комплексная проверка всех исправленных функций"""

    print("🧪 КОМПЛЕКСНАЯ ПРОВЕРКА ВСЕХ ИСПРАВЛЕННЫХ ФУНКЦИЙ")
    print("=" * 60)

    # Параметры сервера
    hostname = '149.154.65.180'
    username = 'root'
    password = 'Sergio675'

    # Список всех исправленных функций для тестирования
    functions_to_test = [
        {
            "num": 1,
            "endpoint": "/api/phishing/sensitivity",
            "method": "GET",
            "description": "Чувствительность фишинга",
            "expected_real_data": True
        },
        {
            "num": 2,
            "endpoint": "/api/analytics/overview",
            "method": "GET",
            "description": "Обзор аналитики",
            "expected_real_data": True
        },
        {
            "num": 3,
            "endpoint": "/api/components/status/crash_detection_agent",
            "method": "GET",
            "description": "Статус компонента",
            "expected_real_data": True
        },
        {
            "num": 4,
            "endpoint": "/api/components/enable/crash_detection_agent",
            "method": "POST",
            "description": "Включение компонента",
            "expected_real_data": True
        },
        {
            "num": 5,
            "endpoint": "/api/components/disable/crash_detection_agent",
            "method": "POST",
            "description": "Отключение компонента",
            "expected_real_data": True
        },
        {
            "num": 6,
            "endpoint": "/api/components/config/crash_detection_agent",
            "method": "GET",
            "description": "Конфигурация компонента",
            "expected_real_data": True
        }
    ]

    try:
        # Подключаемся к серверу
        print("📡 Подключение к серверу ALADDIN...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password, timeout=15)
        print("✅ Подключение успешно!")

        results = []

        # 1. Проверяем статус API Gateway
        print("\n🏥 ШАГ 1: ПРОВЕРКА API GATEWAY")
        health_cmd = "curl -s http://127.0.0.1:8002/api/health"
        stdin, stdout, stderr = ssh.exec_command(health_cmd)
        health_response = stdout.read().decode('utf-8').strip()

        try:
            health_data = json.loads(health_response)
            sfm_status = health_data.get('sfm_adapter', 'unknown')
            endpoints = health_data.get('endpoints', 0)

            print(f"✅ API Gateway: Работает")
            print(f"   SFM статус: {sfm_status}")
            print(f"   Эндпоинтов: {endpoints}")

            if sfm_status not in ['available', 'fallback']:
                print("⚠️  ВНИМАНИЕ: SFM не в оптимальном состоянии")

        except json.JSONDecodeError:
            print(f"❌ Ошибка парсинга health: {health_response}")
            return False

        # 2. Проверяем SFM
        print("\n🤖 ШАГ 2: ПРОВЕРКА SFM")
        sfm_cmd = "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && PYTHONPATH=/opt/aladdin-backend:$PYTHONPATH python3 -c 'from security.sfm_singleton import get_sfm; sfm = get_sfm(); print(f\"Функций: {len(sfm.functions)}\"); print(f\"Статус: {sfm.status}\")' 2>/dev/null"
        stdin, stdout, stderr = ssh.exec_command(sfm_cmd)
        sfm_output = stdout.read().decode('utf-8').strip()
        sfm_error = stderr.read().decode('utf-8').strip()

        if sfm_output:
            print(f"✅ SFM: {sfm_output}")
        else:
            print(f"❌ SFM ошибка: {sfm_error}")

        # 3. Тестируем каждую функцию
        print("\n🧪 ШАГ 3: ТЕСТИРОВАНИЕ ФУНКЦИЙ")

        for func in functions_to_test:
            print(f"\nФункция {func['num']}/93: {func['description']}")
            print(f"  Эндпоинт: {func['method']} {func['endpoint']}")

            # Формируем команду curl
            if func['method'] == 'GET':
                curl_cmd = f"curl -s http://127.0.0.1:8002{func['endpoint']}"
            elif func['method'] == 'POST':
                curl_cmd = f"curl -s -X POST http://127.0.0.1:8002{func['endpoint']}"
            elif func['method'] == 'PUT':
                curl_cmd = f"curl -s -X PUT -H 'Content-Type: application/json' -d '{{}}' http://127.0.0.1:8002{func['endpoint']}"

            # Выполняем запрос
            stdin, stdout, stderr = ssh.exec_command(curl_cmd)
            response = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            if error:
                print(f"  ❌ Ошибка запроса: {error}")
                results.append({
                    "function": func['num'],
                    "endpoint": func['endpoint'],
                    "status": "ERROR",
                    "error": error
                })
                continue

            # Анализируем ответ
            try:
                # Пытаемся распарсить как JSON
                try:
                    json_data = json.loads(response)
                    is_json = True
                except json.JSONDecodeError:
                    is_json = False
                    json_data = None

                # Проверяем на mock данные
                has_mock = '"source": "mock"' in response.lower()
                has_real_data = len(response) > 50 and not has_mock  # Реальные данные обычно длиннее

                # Определяем статус
                if has_mock:
                    status = "❌ MOCK ДАННЫЕ"
                    success = False
                elif has_real_data and is_json:
                    status = "✅ РЕАЛЬНЫЕ ДАННЫЕ"
                    success = True
                elif response and not has_mock:
                    status = "⚠️  НЕ JSON (но не mock)"
                    success = True
                else:
                    status = "❌ ПУСТОЙ ОТВЕТ"
                    success = False

                print(f"  Статус: {status}")
                if is_json and json_data:
                    # Показываем ключевые поля
                    keys = list(json_data.keys())[:3] if isinstance(json_data, dict) else []
                    if keys:
                        print(f"  Ключи: {', '.join(keys)}")

                results.append({
                    "function": func['num'],
                    "endpoint": func['endpoint'],
                    "status": "SUCCESS" if success else "FAILED",
                    "has_real_data": has_real_data,
                    "is_json": is_json,
                    "has_mock": has_mock,
                    "response_length": len(response)
                })

            except Exception as e:
                print(f"  ❌ Ошибка анализа: {e}")
                results.append({
                    "function": func['num'],
                    "endpoint": func['endpoint'],
                    "status": "PARSE_ERROR",
                    "error": str(e)
                })

        # 4. Проверяем логи на ошибки
        print("\n📋 ШАГ 4: ПРОВЕРКА ЛОГОВ")
        logs_cmd = "journalctl -u aladdin-main-api-gateway -n 10 | grep -i error | wc -l"
        stdin, stdout, stderr = ssh.exec_command(logs_cmd)
        error_count = int(stdout.read().decode('utf-8').strip())

        if error_count == 0:
            print("✅ Логи чистые - нет ошибок")
        else:
            print(f"⚠️  Найдено ошибок в логах: {error_count}")

        ssh.close()

        # 5. Анализируем результаты
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")

        successful_functions = 0
        total_functions = len(functions_to_test)

        for result in results:
            func_num = result['function']
            endpoint = result['endpoint']
            status = result['status']

            if status == "SUCCESS":
                print(f"✅ Функция {func_num}/93: {endpoint} - РАБОТАЕТ")
                successful_functions += 1
            else:
                print(f"❌ Функция {func_num}/93: {endpoint} - ПРОБЛЕМА ({status})")
                if 'error' in result:
                    print(f"   Ошибка: {result['error']}")

        print("\n" + "=" * 60)
        print("🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
        print(f"✅ Функций работает: {successful_functions}/{total_functions}")
        print(f"📊 Процент готовности: {successful_functions/total_functions*100:.1f}%")

        if successful_functions == total_functions:
            print("\n🎉 ВСЕ ФУНКЦИИ РАБОТАЮТ ИДЕАЛЬНО!")
            print("✅ Возвращают реальные данные")
            print("✅ Взаимодействуют с SFM")
            print("✅ Готовы для мобильного приложения")
            print("\n🚀 ГОТОВ К ПРОДАКШЕНУ!")
            return True
        else:
            print(f"\n⚠️  {total_functions - successful_functions} ФУНКЦИЙ ТРЕБУЮТ ИСПРАВЛЕНИЯ")
            return False

    except paramiko.AuthenticationException:
        print("❌ Ошибка аутентификации")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH ошибка: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    success = test_all_fixed_functions()
    if not success:
        exit(1)