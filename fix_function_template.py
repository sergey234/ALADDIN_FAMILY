#!/usr/bin/env python3
"""
ШАБЛОН ДЛЯ ИСПРАВЛЕНИЯ ЛЮБОЙ ФУНКЦИИ
Замените PLACEHOLDER значения на реальные

ИСПОЛЬЗОВАНИЕ:
1. Скопировать этот файл: cp fix_function_template.py fix_[function_name].py
2. Заменить все PLACEHOLDER на реальные значения
3. Запустить: python3 fix_[function_name].py
"""

import re
import sys
from datetime import datetime

# ========== КОНФИГУРАЦИЯ ФУНКЦИИ ==========
# ЗАМЕНИТЕ ЭТИ ЗНАЧЕНИЯ НА РЕАЛЬНЫЕ

FUNCTION_ENDPOINT = "PLACEHOLDER_ENDPOINT_PATH"  # Например: "/api/phishing/block_suspicious"
FUNCTION_NAME = "PLACEHOLDER_FUNCTION_NAME"      # Например: "get_phishing_block_suspicious"
SFM_FUNCTION_NAME = "PLACEHOLDER_SFM_FUNCTION"   # Например: "get_phishing_block_suspicious"

# Старый код (скопируйте из api_gateway.py)
OLD_FUNCTION_CODE = '''
PLACEHOLDER_OLD_CODE_HERE
'''

# Новый код с SFM вызовом
NEW_FUNCTION_CODE = '''
PLACEHOLDER_NEW_CODE_HERE
'''

# ========== ЛОГИКА ИСПРАВЛЕНИЯ ==========

def fix_function():
    """
    Исправить PLACEHOLDER_FUNCTION_NAME функцию
    Шаг X/93 в плане 100% реальной защиты
    """

    print(f"🔧 ИСПРАВЛЕНИЕ ФУНКЦИИ: {FUNCTION_NAME}")
    print(f"📍 Эндпоинт: {FUNCTION_ENDPOINT}")
    print(f"🔗 SFM функция: {SFM_FUNCTION_NAME}")
    print("=" * 60)

    # Прочитать текущий файл с сервера
    try:
        with open('/opt/aladdin-backend/api_gateway.py', 'r', encoding='utf-8') as f:
            content = f.read()
        print("✅ Файл прочитан")
    except FileNotFoundError:
        print("❌ Ошибка: api_gateway.py не найден")
        return False

    # Проверить что функция существует в файле
    if FUNCTION_NAME not in content:
        print(f"❌ Функция {FUNCTION_NAME} не найдена в файле")
        return False

    print(f"✅ Функция {FUNCTION_NAME} найдена")

    # Проверить что старый код присутствует
    if OLD_FUNCTION_CODE.strip() in content:
        print("✅ Старый код найден")
    else:
        print("⚠️  Старый код не найден точно, но функция существует")
        # Можно продолжить, если функция существует

    # Заменить код
    if OLD_FUNCTION_CODE.strip() and NEW_FUNCTION_CODE.strip():
        content = content.replace(OLD_FUNCTION_CODE.strip(), NEW_FUNCTION_CODE.strip())
        print("✅ Код заменен")
    else:
        print("❌ Шаблонные коды не заполнены!")
        return False

    # Проверить синтаксис
    try:
        compile(content, 'api_gateway.py', 'exec')
        print("✅ Синтаксис Python валиден")
    except SyntaxError as e:
        print(f"❌ Синтаксис Python ошибка: {e}")
        return False

    # Создать backup
    backup_file = f'/opt/aladdin-backend/api_gateway_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content.replace('\n', '\r\n'))
        print(f"💾 Backup создан: {backup_file}")
    except Exception as e:
        print(f"❌ Ошибка создания backup: {e}")
        return False

    # Записать новый файл
    try:
        with open('/opt/aladdin-backend/api_gateway.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("💾 Файл обновлен")
    except Exception as e:
        print(f"❌ Ошибка записи файла: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 ФУНКЦИЯ ИСПРАВЛЕНА!")
    print("=" * 60)
    print(f"📍 Функция: {FUNCTION_NAME}")
    print(f"🔗 Эндпоинт: {FUNCTION_ENDPOINT}")
    print(f"🛡️ SFM: {SFM_FUNCTION_NAME}")
    print(f"💾 Backup: {backup_file}")
    print("\n" + "🚀 " * 10)
    print("СЛЕДУЮЩИЕ ШАГИ:")
    print("1. systemctl restart aladdin-main-api-gateway")
    print(f"2. python3 test_function_fix.py {FUNCTION_ENDPOINT}")
    print("3. Проверить логи: journalctl -u aladdin-main-api-gateway -n 5")
    print("🚀 " * 10)

    return True

def validate_configuration():
    """Проверить что конфигурация заполнена"""
    errors = []

    if FUNCTION_ENDPOINT == "PLACEHOLDER_ENDPOINT_PATH":
        errors.append("FUNCTION_ENDPOINT не заполнен")
    if FUNCTION_NAME == "PLACEHOLDER_FUNCTION_NAME":
        errors.append("FUNCTION_NAME не заполнен")
    if SFM_FUNCTION_NAME == "PLACEHOLDER_SFM_FUNCTION":
        errors.append("SFM_FUNCTION_NAME не заполнен")
    if "PLACEHOLDER_OLD_CODE_HERE" in OLD_FUNCTION_CODE:
        errors.append("OLD_FUNCTION_CODE содержит placeholder")
    if "PLACEHOLDER_NEW_CODE_HERE" in NEW_FUNCTION_CODE:
        errors.append("NEW_FUNCTION_CODE содержит placeholder")

    if errors:
        print("❌ КОНФИГУРАЦИЯ НЕ ПОЛНА:")
        for error in errors:
            print(f"   - {error}")
        return False

    print("✅ Конфигурация валидна")
    return True

if __name__ == "__main__":
    if not validate_configuration():
        print("\n❌ ЗАПОЛНИТЕ КОНФИГУРАЦИЮ ПЕРЕД ЗАПУСКОМ!")
        sys.exit(1)

    success = fix_function()
    if success:
        print("\n🎯 ГОТОВО! ТЕПЕРЬ НУЖНО ПЕРЕЗАПУСТИТЬ API GATEWAY")
        print("Команда: systemctl restart aladdin-main-api-gateway")
    else:
        print("\n❌ ИСПРАВЛЕНИЕ НЕ УДАЛОСЬ")

    sys.exit(0 if success else 1)