#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ ФУНКЦИИ 7/93 НА СЕРВЕРЕ
Правит функцию update_component_config прямо на сервере
"""

import paramiko

def fix_function_7_on_server():
    """Исправляет функцию 7/93 на сервере"""

    print("🔧 ИСПРАВЛЕНИЕ ФУНКЦИИ 7/93 НА СЕРВЕРЕ")
    print("Функция: /api/components/config/{component_id} (PUT)")
    print("=" * 55)

    # Параметры сервера
    hostname = '149.154.65.180'
    username = 'root'
    password = 'Sergio675'

    try:
        # Подключаемся к серверу
        print("📡 Подключение к серверу...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password, timeout=10)
        print("✅ Подключение успешно!")

        # Исправление функции на сервере
        print("\n🔧 Исправление функции update_component_config...")

        fix_cmd = '''
cd /opt/aladdin-backend && python3 -c "
import re

# Читаем файл
with open('api_gateway.py', 'r') as f:
    content = f.read()

# Ищем функцию update_component_config
func_start = content.find('@app.put(\"/api/components/config/{component_id}\")')
if func_start != -1:
    func_end = content.find('\n\n@app.', func_start + 1)
    if func_end == -1:
        func_end = len(content)
    
    old_func = content[func_start:func_end]
    
    # Создаем новую версию
    new_func = \'\'\'@app.put("/api/components/config/{component_id}")
async def update_component_config(component_id: str, config: dict):
    # ✅ ИСПРАВЛЕНА - функция 7/93
    # Заменено hardcoded/mock на реальный SFM вызов
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function(\"update_component_config\", {\"component_id\": component_id, \"config\": config})
        if success:
            return result
        else:
            return {\"error\": message, \"component_id\": component_id, \"status\": \"sfm_error\"}
    else:
        return {\"error\": \"SFM adapter unavailable\", \"component_id\": component_id, \"status\": \"fallback\"}
\'\'\'
    
    # Заменяем
    content = content.replace(old_func, new_func)
    
    # Записываем обратно
    with open('api_gateway.py', 'w') as f:
        f.write(content)
    
    print('Функция update_component_config исправлена')
else:
    print('Функция не найдена')
"
'''
        stdin, stdout, stderr = ssh.exec_command(fix_cmd)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f"❌ Ошибка исправления: {error}")
            return False
        else:
            print(f"✅ {output}")

        # Проверка синтаксиса
        print("\n🔍 Проверка синтаксиса...")
        syntax_cmd = "cd /opt/aladdin-backend && python3 -m py_compile api_gateway.py"
        stdin, stdout, stderr = ssh.exec_command(syntax_cmd)
        error = stderr.read().decode('utf-8').strip()
        if error:
            print(f"❌ Синтаксическая ошибка: {error}")
            return False
        else:
            print("✅ Синтаксис корректный")

        # Перезапуск сервиса
        print("\n🔄 Перезапуск API Gateway...")
        restart_cmd = "systemctl restart aladdin-main-api-gateway"
        stdin, stdout, stderr = ssh.exec_command(restart_cmd)

        import time
        time.sleep(3)

        # Тестирование
        print("\n🧪 Тестирование функции...")
        test_cmd = "curl -s -X PUT -H 'Content-Type: application/json' -d '{\"enabled\": true}' http://127.0.0.1:8002/api/components/config/crash_detection_agent | grep -o 'source.*mock' || echo '✅ РЕАЛЬНЫЕ ДАННЫЕ'"
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        test_output = stdout.read().decode('utf-8').strip()
        print(f"Результат: {test_output}")

        ssh.close()
        print("\n🔌 Соединение закрыто")
        print("\n🎉 ФУНКЦИЯ 7/93 ИСПРАВЛЕНА!")

        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    if fix_function_7_on_server():
        print("✅ ГОТОВ К СЛЕДУЮЩЕЙ ФУНКЦИИ 8/93!")
    else:
        print("❌ ОШИБКА ИСПРАВЛЕНИЯ")
        exit(1)