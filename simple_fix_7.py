#!/usr/bin/env python3
"""
🔧 ПРОСТОЕ ИСПРАВЛЕНИЕ ФУНКЦИИ 7/93
Заменяет только mock ответ на правильный SFM вызов
"""

import paramiko

def simple_fix_7():
    """Простое исправление функции 7/93"""

    hostname = '149.154.65.180'
    username = 'root'
    password = 'Sergio675'

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password, timeout=10)

        print("🔧 Исправление функции 7/93...")

        # Простая замена с sed
        fix_cmd = "cd /opt/aladdin-backend && sed -i 's/return {\"component_id\": component_id, \"action\": \"update_config\", \"source\": \"mock\"}/        if success:\\n            return result\\n        else:\\n            return {\"error\": message, \"component_id\": component_id, \"status\": \"sfm_error\"}\\n    else:\\n        return {\"error\": \"SFM adapter unavailable\", \"component_id\": component_id, \"status\": \"fallback\"}/g' api_gateway.py"

        stdin, stdout, stderr = ssh.exec_command(fix_cmd)
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f"❌ Ошибка: {error}")
            ssh.close()
            return False

        # Добавление комментария
        comment_cmd = "cd /opt/aladdin-backend && sed -i '/async def update_component_config/a\\    # ✅ ИСПРАВЛЕНА - функция 7/93\\n    # Заменено hardcoded/mock на реальный SFM вызов' api_gateway.py"

        stdin, stdout, stderr = ssh.exec_command(comment_cmd)
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f"⚠️ Предупреждение с комментарием: {error}")

        # Проверка синтаксиса
        syntax_cmd = "cd /opt/aladdin-backend && python3 -m py_compile api_gateway.py"
        stdin, stdout, stderr = ssh.exec_command(syntax_cmd)
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f"❌ Синтаксис: {error}")
            ssh.close()
            return False

        print("✅ Функция исправлена")

        # Перезапуск
        restart_cmd = "systemctl restart aladdin-main-api-gateway"
        stdin, stdout, stderr = ssh.exec_command(restart_cmd)

        import time
        time.sleep(3)

        ssh.close()
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    if simple_fix_7():
        print("🎉 ФУНКЦИЯ 7/93 ИСПРАВЛЕНА!")
    else:
        print("❌ ОШИБКА")
        exit(1)