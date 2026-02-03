#!/usr/bin/env python3
"""
ПРОВЕРКА ПОСЛЕ ИЗМЕНЕНИЯ НА SafeFunctionManager
"""

import paramiko

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🔍 ПРОВЕРКА ПОСЛЕ ИЗМЕНЕНИЯ НА SafeFunctionManager')

    # Проверим статус API Gateway
    status = run_command(ssh, 'systemctl status aladdin-main-api-gateway --no-pager | head -3')
    print('Статус API Gateway:')
    print(status)

    # Тестируем SFM адаптер
    print('\\n🧪 ТЕСТ SFM АДАПТЕРА:')
    test_cmd = 'cd /opt/aladdin-backend && python3 -c "from sfm_adapter import sfm_adapter; print(\'Импорт успешен\'); sfm_adapter._initialize_sfm_sync(); print(f\'Инициализация: {sfm_adapter.available}\'); print(f\'Тип: {type(sfm_adapter._sfm)}\')"'
    test_result = run_command(ssh, test_cmd)
    print(test_result)

    # Проверим что происходит при импорте SafeFunctionManager
    print('\\n🔍 ТЕСТ SafeFunctionManager:')
    sfm_test = 'cd /opt/aladdin-backend && python3 -c "from security.safe_function_manager import SafeFunctionManager; sfm = SafeFunctionManager(); print(f\'SFM создан: {len(sfm.functions)} функций\')"'
    sfm_result = run_command(ssh, sfm_test)
    print(sfm_result)

    ssh.close()

if __name__ == '__main__':
    main()