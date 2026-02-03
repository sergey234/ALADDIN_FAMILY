#!/usr/bin/env python3
"""
АНАЛИЗ SFM АДАПТЕРА - ПОНИМАНИЕ ЛОГИКИ ПЕРЕКЛЮЧЕНИЯ РЕЖИМОВ
"""

import paramiko

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🔍 АНАЛИЗ SFM АДАПТЕРА - ЛОГИКА РЕЖИМОВ')
    print('=' * 60)

    # 1. Найдем логику fallback/real
    print('1️⃣ ПОИСК ЛОГИКИ FALLBACK/REAL:')
    fallback_search = run_command(ssh, 'cd /opt/aladdin-backend && grep -n -A 5 -B 5 "fallback\|real\|mode" sfm_adapter.py')
    print(fallback_search)

    # 2. Найдем определение SFM_ADAPTER_AVAILABLE
    print('\n2️⃣ SFM_ADAPTER_AVAILABLE:')
    available_search = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 10 -B 5 "SFM_ADAPTER_AVAILABLE" sfm_adapter.py')
    print(available_search)

    # 3. Найдем функцию execute_function
    print('\n3️⃣ ФУНКЦИЯ EXECUTE_FUNCTION:')
    execute_search = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 20 "def execute_function" sfm_adapter.py')
    print(execute_search)

    # 4. Найдем как создается sfm_adapter
    print('\n4️⃣ СОЗДАНИЕ SFM_ADAPTER:')
    adapter_creation = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 15 -B 5 "sfm_adapter.*=" sfm_adapter.py')
    print(adapter_creation)

    # 5. Найдем импорты SFM
    print('\n5️⃣ ИМПОРТЫ SFM:')
    imports = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 5 -B 5 "from.*sfm\|import.*sfm\|SFMManager\|SafeFunctionManager" sfm_adapter.py')
    print(imports)

    # 6. Проверим что происходит при импорте
    print('\n6️⃣ ТЕСТ ИМПОРТА SFM АДАПТЕРА:')
    import_cmd = '''cd /opt/aladdin-backend && python3 -c "
try:
    from sfm_adapter import SFM_ADAPTER_AVAILABLE, sfm_adapter
    print(f'SFM_ADAPTER_AVAILABLE = {SFM_ADAPTER_AVAILABLE}')
    print(f'sfm_adapter = {sfm_adapter}')
    if sfm_adapter:
        print(f'type(sfm_adapter) = {type(sfm_adapter)}')
        print(f'hasattr functions = {hasattr(sfm_adapter, \"functions\")}')
        if hasattr(sfm_adapter, 'functions'):
            print(f'len(functions) = {len(sfm_adapter.functions)}')
except Exception as e:
    print(f'Import error: {e}')
"'''
    import_test = run_command(ssh, import_cmd)
    print(import_test)

    ssh.close()

    print('\n' + '=' * 60)
    print('🎯 АНАЛИЗ ПРОБЛЕМЫ:')
    print('1. SFM адаптер должен определять когда SafeFunctionManager доступен')
    print('2. Сейчас он всегда в fallback режиме')
    print('3. Нужно исправить логику определения доступности SFM')
    print('')
    print('💡 РЕШЕНИЕ:')
    print('Найти в коде где проверяется доступность SFM и исправить эту логику')

if __name__ == '__main__':
    main()