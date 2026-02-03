#!/usr/bin/env python3
"""
ПОЛНАЯ ДИАГНОСТИКА СИСТЕМЫ ALADDIN
Проверяем все компоненты для запуска настоящего SFM Core
"""

import paramiko
import json

def run_command(ssh, cmd, description=""):
    """Выполнить команду и вернуть результат"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8').strip()
    err = stderr.read().decode('utf-8').strip()
    if description:
        print(f"\n{description}")
    if out:
        print(out)
    if err:
        print(f"❌ Ошибка: {err}")
    return out, err

def main():
    print('🔬 ПОЛНАЯ ДИАГНОСТИКА СИСТЕМЫ ALADDIN')
    print('=' * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    # 1. СТРУКТУРА ПРОЕКТА
    run_command(ssh, 'cd /opt/aladdin-backend && echo "=== СТРУКТУРА ПРОЕКТА ===" && find . -maxdepth 2 -type d | sort',
               '1️⃣ СТРУКТУРА ПРОЕКТА:')

    # 2. SFM КОМПОНЕНТЫ
    run_command(ssh, 'cd /opt/aladdin-backend && echo "=== SFM ФАЙЛЫ ===" && find . -name "*sfm*" -type f | grep -v __pycache__ | sort',
               '\n2️⃣ SFM КОМПОНЕНТЫ:')

    # 3. ОСНОВНЫЕ МОДУЛИ
    run_command(ssh, 'cd /opt/aladdin-backend && echo "=== ОСНОВНЫЕ ФАЙЛЫ ===" && ls -la *.py 2>/dev/null || echo "Python файлы в корне не найдены"',
               '\n3️⃣ ОСНОВНЫЕ МОДУЛИ:')

    # 4. SECURITY ДИРЕКТОРИЙ
    run_command(ssh, 'cd /opt/aladdin-backend && echo "=== SECURITY ДИРЕКТОРИЙ ===" && ls -la security/ 2>/dev/null || echo "Директория security не найдена"',
               '\n4️⃣ SECURITY ДИРЕКТОРИЙ:')

    # 5. SFM SINGLETON
    run_command(ssh, 'cd /opt/aladdin-backend && echo "=== SFM SINGLETON ===" && head -10 security/sfm_singleton.py 2>/dev/null || echo "Файл sfm_singleton.py не найден"',
               '\n5️⃣ SFM SINGLETON (первые 10 строк):')

    # 6. SFM АДАПТЕР
    run_command(ssh, 'cd /opt/aladdin-backend && echo "=== SFM АДАПТЕР ===" && head -10 sfm_adapter.py 2>/dev/null || echo "Файл sfm_adapter.py не найден"',
               '\n6️⃣ SFM АДАПТЕР (первые 10 строк):')

    # 7. API GATEWAY
    run_command(ssh, 'cd /opt/aladdin-backend && echo "=== API GATEWAY ===" && head -10 api_gateway.py 2>/dev/null || echo "Файл api_gateway.py не найден"',
               '\n7️⃣ API GATEWAY (первые 10 строк):')

    # 8. ТЕСТ ИМПОРТА КОМПОНЕНТОВ
    print('\n8️⃣ ТЕСТ ИМПОРТА КОМПОНЕНТОВ:')
    test_imports = '''
echo "=== ТЕСТ SFM SINGLETON ==="
python3 -c "from security.sfm_singleton import SFMManager; print('✅ SFM Singleton импортируется')" 2>&1 || echo "❌ Ошибка импорта SFM Singleton"

echo "=== ТЕСТ SFM АДАПТЕР ==="
python3 -c "from sfm_adapter import SFMAdapter; print('✅ SFM Adapter импортируется')" 2>&1 || echo "❌ Ошибка импорта SFM Adapter"

echo "=== ТЕСТ API GATEWAY ==="
python3 -c "import api_gateway; print('✅ API Gateway импортируется')" 2>&1 || echo "❌ Ошибка импорта API Gateway"
'''
    run_command(ssh, f'cd /opt/aladdin-backend && {test_imports}')

    # 9. ЗАПУЩЕННЫЕ ПРОЦЕССЫ
    run_command(ssh, 'echo "=== ЗАПУЩЕННЫЕ ПРОЦЕССЫ ===" && ps aux | grep python | grep -v grep | head -10',
               '\n9️⃣ ЗАПУЩЕННЫЕ PYTHON ПРОЦЕССЫ:')

    # 10. SYSTEMD СЕРВИСЫ
    run_command(ssh, 'echo "=== SYSTEMD СЕРВИСЫ ===" && systemctl list-units --type=service --state=running | grep aladdin | head -5',
               '\n🔟 SYSTEMD СЕРВИСЫ ALADDIN:')

    # 11. API HEALTH
    print('\n1️⃣1️⃣ API HEALTH:')
    stdout, stderr = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    if stdout:
        try:
            health = json.loads(stdout)
            print('Текущий статус:')
            for key, value in health.items():
                status_icon = '✅' if value == 'ok' or isinstance(value, int) else '⚠️'
                print(f'  {status_icon} {key}: {value}')
        except:
            print(stdout)

    # 12. ТЕСТ ОДНОЙ ФУНКЦИИ
    print('\n1️⃣2️⃣ ТЕСТ ФУНКЦИИ (пример):')
    stdout, stderr = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/phishing/sensitivity')
    if stdout:
        try:
            response = json.loads(stdout)
            print('Пример ответа:')
            for key, value in response.items():
                print(f'  {key}: {value}')
        except:
            print(stdout)

    print('\n' + '=' * 70)
    print('🎯 АНАЛИЗ ГОТОВНОСТИ К ЗАПУСКУ SFM CORE:')
    print('Проверьте выше результаты и скажите что делать дальше!')

    ssh.close()

if __name__ == '__main__':
    main()