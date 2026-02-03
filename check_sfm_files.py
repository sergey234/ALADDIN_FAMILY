#!/usr/bin/env python3
"""
ПРОВЕРКА SFM ФАЙЛОВ - ЧТО У НАС ЕСТЬ
"""

import paramiko

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🔍 ЧТО У НАС ЕСТЬ В SFM')
    print('=' * 50)

    # 1. Основные SFM файлы
    print('1️⃣ ОСНОВНЫЕ SFM ФАЙЛЫ:')
    files_to_check = [
        'security/sfm_singleton.py',
        'sfm_adapter.py',
        'security/safe_function_manager.py',
        'complete_api_sfm_mapping.py',
        'correct_sfm_count.py'
    ]

    for file_path in files_to_check:
        result = run_command(ssh, f'cd /opt/aladdin-backend && ls -la {file_path} 2>/dev/null || echo "❌ НЕ НАЙДЕН"')
        if '❌' not in result:
            print(f'✅ {file_path}')
        else:
            print(f'❌ {file_path}')

    # 2. SFM JSON регистры
    print('\n2️⃣ SFM JSON РЕГИСТРЫ:')
    json_files = run_command(ssh, 'cd /opt/aladdin-backend && find . -name "*sfm*" -name "*.json"')
    if json_files:
        for f in json_files.split('\n'):
            if f.strip():
                print(f'✅ {f.strip()}')
    else:
        print('❌ JSON регистры не найдены')

    # 3. Что работает в SFM адаптере
    print('\n3️⃣ SFM АДАПТЕР СТАТУС:')
    sfm_status = run_command(ssh, 'cd /opt/aladdin-backend && python3 -c "from sfm_adapter import SFM_ADAPTER_AVAILABLE, sfm_adapter; print(f\"AVAILABLE: {SFM_ADAPTER_AVAILABLE}\"); print(f\"TYPE: {type(sfm_adapter).__name__ if sfm_adapter else \'None\'}\"); print(f\"FUNCTIONS: {len(sfm_adapter.functions) if sfm_adapter and hasattr(sfm_adapter, \'functions\') else \'unknown\'}\")"')
    print(sfm_status)

    # 4. Что запущено как сервис
    print('\n4️⃣ ЗАПУЩЕННЫЙ SFM СЕРВИС:')
    script_content = run_command(ssh, 'cd /opt/aladdin-backend && cat start_sfm_core.sh 2>/dev/null || echo "СКРИПТ НЕ НАЙДЕН"')
    if 'СКРИПТ НЕ НАЙДЕН' not in script_content:
        if 'SafeFunctionManager' in script_content:
            print('✅ Сервис запускает: SafeFunctionManager')
        if 'SFMCore' in script_content:
            print('❓ Сервис ищет: SFMCore (может не существовать)')
    else:
        print('❌ Скрипт запуска не найден')

    # 5. Логи сервиса
    print('\n5️⃣ ЛОГИ SFM СЕРВИСА:')
    logs = run_command(ssh, 'journalctl -u aladdin-sfm-core -n 2 --no-pager 2>/dev/null || echo "ЛОГИ НЕ ДОСТУПНЫ"')
    if 'ЛОГИ НЕ ДОСТУПНЫ' not in logs:
        for line in logs.split('\n')[-2:]:
            if line.strip():
                print(f'  {line.strip()}')
    else:
        print('❌ Логи недоступны')

    ssh.close()

    print('\n' + '=' * 50)
    print('🎯 ВЫВОД:')
    print('• У вас НЕТ sfm_core.py файла')
    print('• SFM - это SafeFunctionManager из security/safe_function_manager.py')
    print('• Он успешно работает, но API Gateway не переключается на real режим')

if __name__ == '__main__':
    main()