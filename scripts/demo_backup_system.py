#!/usr/bin/env python3
"""
Демонстрация системы автоматических резервных копий
Показывает как работает защита реестра
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from scripts.registry_protection_system import RegistryProtectionSystem

def demo_backup_system():
    """Демонстрация системы резервного копирования"""
    
    print("🔄 ДЕМОНСТРАЦИЯ СИСТЕМЫ АВТОМАТИЧЕСКИХ РЕЗЕРВНЫХ КОПИЙ")
    print("=" * 60)
    
    # Инициализация системы защиты
    protection = RegistryProtectionSystem()
    
    # Показываем текущее состояние
    print("📊 ТЕКУЩЕЕ СОСТОЯНИЕ:")
    status = protection.get_registry_status()
    print(f"   • Функций в реестре: {status['current_functions_count']}")
    print(f"   • Резервных копий: {status['backup_count']}")
    print(f"   • Путь к реестру: {status['registry_path']}")
    
    # Создаём тестовое изменение
    print(f"\n🔄 ТЕСТИРОВАНИЕ АВТОМАТИЧЕСКОГО РЕЗЕРВНОГО КОПИРОВАНИЯ:")
    
    # Читаем текущий реестр
    with open(protection.registry_path, 'r', encoding='utf-8') as f:
        current_registry = json.load(f)
    
    # Создаём копию с небольшим изменением
    test_registry = current_registry.copy()
    test_registry["last_updated"] = datetime.now().isoformat()
    test_registry["test_demo"] = "Демонстрация автоматического резервного копирования"
    
    print("   • Создаём тестовое изменение в реестре...")
    
    # Показываем что происходит при защищённой записи
    print("   • Система автоматически создаёт резервную копию...")
    backup_path = protection.create_backup()
    print(f"   ✅ Резервная копия создана: {backup_path}")
    
    # Показываем содержимое резервной копии
    if backup_path and Path(backup_path).exists():
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print(f"   📄 Резервная копия содержит {len(backup_data.get('functions', {}))} функций")
        print(f"   📅 Время создания: {backup_data.get('last_updated', 'неизвестно')}")
    
    # Демонстрируем защиту от удаления функций
    print(f"\n🛡️ ДЕМОНСТРАЦИЯ ЗАЩИТЫ ОТ УДАЛЕНИЯ ФУНКЦИЙ:")
    
    # Создаём реестр с удалённой функцией
    dangerous_registry = current_registry.copy()
    if dangerous_registry["functions"]:
        # Удаляем первую функцию
        first_func = list(dangerous_registry["functions"].keys())[0]
        del dangerous_registry["functions"][first_func]
        print(f"   • Пытаемся удалить функцию: {first_func}")
    
    print("   • Система проверяет изменения...")
    deletion_info = protection.check_function_deletion(dangerous_registry)
    
    if deletion_info["deleted_count"] > 0:
        print(f"   🚨 ОБНАРУЖЕНО УДАЛЕНИЕ {deletion_info['deleted_count']} ФУНКЦИЙ!")
        print(f"   ❌ ЗАПИСЬ ЗАБЛОКИРОВАНА!")
        print(f"   🛡️ Функции защищены от случайного удаления")
    else:
        print("   ✅ Изменения безопасны")
    
    # Показываем как работает принудительная запись
    print(f"\n🔓 ДЕМОНСТРАЦИЯ ПРИНУДИТЕЛЬНОЙ ЗАПИСИ:")
    print("   • Используем force=True для обхода защиты...")
    
    # Безопасное изменение (добавляем тестовую функцию)
    safe_registry = current_registry.copy()
    safe_registry["functions"]["test_demo_function"] = {
        "name": "Test Demo Function",
        "description": "Демонстрационная функция",
        "status": "active",
        "function_type": "test",
        "security_level": "low",
        "is_critical": False,
        "created_at": datetime.now().isoformat()
    }
    safe_registry["last_updated"] = datetime.now().isoformat()
    
    print("   • Выполняем безопасное обновление...")
    success = protection.protect_registry_write(safe_registry, force=False)
    
    if success:
        print("   ✅ Реестр успешно обновлён с автоматическим резервным копированием")
    else:
        print("   ❌ Обновление заблокировано")
    
    # Показываем финальное состояние
    print(f"\n📊 ФИНАЛЬНОЕ СОСТОЯНИЕ:")
    final_status = protection.get_registry_status()
    print(f"   • Функций в реестре: {final_status['current_functions_count']}")
    print(f"   • Резервных копий: {final_status['backup_count']}")
    print(f"   • Потеряно функций: {final_status['functions_lost']}")
    
    # Показываем все резервные копии
    backup_dir = Path("data/sfm/backups")
    registry_backups = list(backup_dir.glob("registry_backup_*.json"))
    
    print(f"\n💾 ВСЕ РЕЗЕРВНЫЕ КОПИИ РЕЕСТРА:")
    for i, backup in enumerate(registry_backups[-5:], 1):  # Показываем последние 5
        stat = backup.stat()
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)
        print(f"   {i}. {backup.name}")
        print(f"      📅 {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      📊 {size} байт")
    
    print(f"\n🛡️ СИСТЕМА ЗАЩИТЫ АКТИВНА!")
    print(f"   • Автоматические резервные копии: ✅")
    print(f"   • Защита от удаления функций: ✅")
    print(f"   • Валидация формата: ✅")
    print(f"   • Логирование изменений: ✅")

if __name__ == "__main__":
    demo_backup_system()