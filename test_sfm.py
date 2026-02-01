#!/usr/bin/env python3
import sys
sys.path.append('/opt/aladdin-backend/security')

try:
    from safe_function_manager import SafeFunctionManager
    sfm = SafeFunctionManager()
    print('✅ SFM инициализирован успешно')

    # Тестовая функция
    result = sfm.execute_function('get_component_status', {'component_id': 'test'})
    print(f'✅ SFM функция выполнена: {result}')

except Exception as e:
    print(f'❌ Ошибка SFM: {e}')
    import traceback
    traceback.print_exc()


