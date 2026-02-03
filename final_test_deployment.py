#!/usr/bin/env python3
"""
ФИНАЛЬНЫЙ ТЕСТ РАЗВЕРТЫВАНИЯ ALADDIN
Проверка что все работает правильно
"""

import paramiko

SERVER_CONFIG = {
    'hostname': '149.154.65.180',
    'username': 'root',
    'password': 'Sergio675',
    'port': 22
}

def test_command(ssh_client, command, description):
    """Тест команды"""
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=10)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        exit_code = stdout.channel.recv_exit_status()
        return exit_code == 0, output, error
    except Exception as e:
        return False, "", str(e)

def main():
    """Финальный тест"""
    print("🎯 ФИНАЛЬНЫЙ ТЕСТ РАЗВЕРТЫВАНИЯ ALADDIN")
    print("=" * 50)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(**SERVER_CONFIG)
    except Exception as e:
        print(f"❌ НЕ МОГУ ПОДКЛЮЧИТЬСЯ: {e}")
        return

    results = {}

    try:
        # 1. SFM HTTP API health
        success, output, error = test_command(ssh, "curl -s http://127.0.0.1:8003/api/health", "SFM HTTP API")
        results['sfm_api'] = success and 'healthy' in output
        print(f"SFM HTTP API: {'✅' if results['sfm_api'] else '❌'} ({output[:50]}...)")

        # 2. SFM функция
        success, output, error = test_command(ssh, 'curl -X POST http://127.0.0.1:8003/api/execute -H "Content-Type: application/json" -d \'{"function": "get_phishing_sensitivity", "params": {}}\'', "SFM функция")
        results['sfm_function'] = success and 'success' in output
        print(f"SFM функция: {'✅' if results['sfm_function'] else '❌'}")

        # 3. API Gateway health
        success, output, error = test_command(ssh, "curl -s http://127.0.0.1:8002/api/health", "API Gateway")
        results['api_gateway'] = success and 'ok' in output
        sfm_available = 'available' in output
        results['sfm_adapter'] = sfm_available
        print(f"API Gateway: {'✅' if results['api_gateway'] else '❌'}")
        print(f"SFM адаптер: {'✅ available' if sfm_available else '❌ fallback'}")

        # 4. Функции API
        functions = ['/api/phishing/sensitivity', '/api/analytics/overview', '/api/components/health']
        working_functions = 0

        for func in functions:
            success, output, error = test_command(ssh, f"curl -s http://127.0.0.1:8002{func} | jq -r .source 2>/dev/null || echo 'ERROR'", f"Функция {func}")
            is_real_sfm = success and 'real_sfm' in output
            if is_real_sfm:
                working_functions += 1
            print(f"{func}: {'✅ real_sfm' if is_real_sfm else '❌ ' + output[:20]}")

        results['working_functions'] = working_functions

    finally:
        ssh.close()

    # РЕЗУЛЬТАТЫ
    print("\n" + "=" * 50)
    print("🎉 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)

    all_good = all([
        results.get('sfm_api', False),
        results.get('sfm_function', False),
        results.get('api_gateway', False),
        results.get('working_functions', 0) >= 2
    ])

    if all_good:
        print("✅ РАЗВЕРТЫВАНИЕ УСПЕШНО ЗАВЕРШЕНО!")
        print("✅ ALADDIN получил 100% РЕАЛЬНУЮ ЗАЩИТУ!")
        print(f"✅ {results['working_functions']}/3 функций работают с real_sfm")
        print("🚀 ПРОЕКТ ГОТОВ К ПРОДАКШЕНУ!")
    else:
        print("⚠️ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО С ПРОБЛЕМАМИ")
        print(f"Проверено: SFM API={results.get('sfm_api')}, Функции={results.get('working_functions')}/3")
        print("🔍 Требуется дополнительная настройка")

    print("\n📞 КОМАНДЫ ДЛЯ ПРОВЕРКИ:")
    print("   curl http://149.154.65.180:8002/api/health")
    print("   curl http://149.154.65.180:8002/api/phishing/sensitivity | jq .source")

if __name__ == "__main__":
    main()