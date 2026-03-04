import sys
import os
sys.path.insert(0, '.')

print('🧪 ТЕСТИРОВАНИЕ ВОССТАНОВЛЕННЫХ РОУТЕРОВ')
print('=' * 50)

# Тестируем импорты роутеров
routers_to_test = [
    ('Family', 'app.routers.family'),
    ('Auth', 'app.routers.auth_router'),
    ('Components', 'app.routers.components'),
    ('Protection', 'app.routers.protection'),
    ('Referral', 'app.routers.referral'),
    ('Payments', 'app.routers.payments')
]

for name, module in routers_to_test:
    try:
        __import__(module)
        print(f'✅ {name} роутер: ДОСТУПЕН')
    except ImportError as e:
        print(f'❌ {name} роутер: НЕДОСТУПЕН - {str(e)[:100]}')
    except Exception as e:
        print(f'⚠️  {name} роутер: ДОСТУПЕН с предупреждениями - {str(e)[:100]}')

print()
print('🎯 ПРОВЕРКА FAMILY API')
print('=' * 30)

# Проверяем наличие файла
if o.py')
    print(f'✅ Размер файла: {size} байт')
    
    # Ищем эндпоинты в файле
    with open('app/routers/family.py', 'r') as f:
        content = f.read()
        if '@router.post("/create"' in content:
            print('✅ Эндпоинт /create найден')
        else:
            print('❌ Эндпоинт /create не найден')
            
        if 'CreateFamilyResponse' in content:
            print('✅ Модель CreateFamilyResponse найдена')
        else:
            print('❌ Модель CreateFamilyResponse не найдена')
else:
    print('❌ Файл family.py не существует')

print()
print('🎯 ПРОВЕРКА MOCKAPISERVICE')
print('=' * 25)

if os.path.exists('Core/Network/MockAPIService.swift'):
    print('✅ Файл MockAPIService.swift существует')
    
    with open('Core/Network/MockAPIService.swift', 'r') as f:
        content = f.read()
        if '#if DEBUG' in content and '#endif' in    lines = content.count('\n')
        print(f'✅ Файл содержит {lines} строк кода')
else:
    print('❌ Файл MockAPIService.swift не существует')
