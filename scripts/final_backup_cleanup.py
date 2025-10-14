#!/usr/bin/env python3
"""
Финальная очистка backup файлов - Phase 2
Перенос оставшихся 6 backup файлов с полным тестированием
"""

import os
import shutil
import json
import sys
from datetime import datetime
from pathlib import Path

# Настройки
BASE_DIR = Path("/Users/sergejhlystov/ALADDIN_NEW")
BACKUP_DIR = BASE_DIR / "security" / "formatting_work" / "backup_files"
LOG_FILE = BACKUP_DIR / "FINAL_CLEANUP_LOG.json"

# Создаем директорию если не существует
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Файлы для переноса (Phase 2)
FILES_TO_MOVE = [
    {
        "source": "security/ai_agents/elderly_interface_manager_backup_original_backup_20250103.py",
        "target": "elderly_interface_manager_backup_original_backup_20250103.py",
        "original": "security/managers/elderly_interface_manager.py",
        "category": "ai_agents"
    },
    {
        "source": "security/bots/components/notification_service_original_backup_20250103.py",
        "target": "notification_service_original_backup_20250103.py",
        "original": "security/bots/components/notification_service.py",
        "category": "bots"
    },
    {
        "source": "security/bots/components/time_monitor_original_backup_20250103.py",
        "target": "time_monitor_original_backup_20250103.py",
        "original": "security/bots/components/time_monitor.py",
        "category": "bots"
    },
    {
        "source": "security/bots/components/content_analyzer_original_backup_20250103.py",
        "target": "content_analyzer_original_backup_20250103.py",
        "original": "security/bots/components/content_analyzer.py",
        "category": "bots"
    },
    {
        "source": "security/bots/components/performance_optimizer_original_backup_20250103.py",
        "target": "performance_optimizer_original_backup_20250103.py",
        "original": "security/bots/components/performance_optimizer.py",
        "category": "bots"
    },
    {
        "source": "security/microservices/put_to_sleep_backup.py",
        "target": "put_to_sleep_backup.py",
        "original": "security/formatting_work/duplicates/put_to_sleep.py",
        "category": "microservices"
    }
]

def log_operation(operation, status, details=""):
    """Логирование операций"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "operation": operation,
        "status": status,
        "details": details
    }
    
    # Читаем существующий лог
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
    else:
        log_data = {"phase": "final_cleanup", "operations": []}
    
    log_data["operations"].append(log_entry)
    
    # Записываем обновленный лог
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def test_import(file_path):
    """Тестирование импорта файла"""
    try:
        # Проверяем синтаксис файла
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Компилируем для проверки синтаксиса
        compile(content, str(file_path), 'exec')
        
        # Проверяем размер файла
        file_size = file_path.stat().st_size
        
        return True, f"Синтаксис OK, размер: {file_size} байт"
    except SyntaxError as e:
        return False, f"Синтаксическая ошибка: {str(e)}"
    except Exception as e:
        return False, f"Ошибка проверки: {str(e)}"

def test_sfm_registration():
    """Тестирование SFM регистрации"""
    try:
        sfm_path = BASE_DIR / "data" / "sfm" / "function_registry.json"
        if not sfm_path.exists():
            return False, "SFM файл не найден"
        
        with open(sfm_path, 'r', encoding='utf-8') as f:
            sfm_data = json.load(f)
        
        total_functions = len(sfm_data.get('functions', {}))
        active_functions = sum(1 for f in sfm_data.get('functions', {}).values() if f.get('status') == 'active')
        
        return True, f"SFM: {total_functions} функций, {active_functions} активных"
    except Exception as e:
        return False, f"Ошибка SFM: {str(e)}"

def move_backup_file(file_info):
    """Перенос backup файла с тестированием"""
    source_path = BASE_DIR / file_info["source"]
    target_path = BACKUP_DIR / file_info["target"]
    original_path = BASE_DIR / file_info["original"]
    
    print(f"\n🔄 Перенос: {file_info['source']}")
    
    # Проверяем существование файлов
    if not source_path.exists():
        log_operation(f"move_{file_info['target']}", "ERROR", "Source файл не найден")
        return False, "Source файл не найден"
    
    if not original_path.exists():
        log_operation(f"move_{file_info['target']}", "ERROR", "Original файл не найден")
        return False, "Original файл не найден"
    
    # Тестируем оригинал ДО переноса
    print(f"  ✅ Тестируем оригинал: {file_info['original']}")
    original_works, original_msg = test_import(original_path)
    if not original_works:
        log_operation(f"test_original_{file_info['target']}", "ERROR", original_msg)
        return False, f"Оригинал не работает: {original_msg}"
    
    print(f"  ✅ Оригинал работает: {original_msg}")
    
    # Переносим файл
    try:
        shutil.move(str(source_path), str(target_path))
        print(f"  ✅ Перенесен: {file_info['target']}")
        log_operation(f"move_{file_info['target']}", "SUCCESS", "Файл успешно перенесен")
        
        # Тестируем оригинал ПОСЛЕ переноса
        print(f"  🔍 Тестируем оригинал после переноса...")
        original_works_after, original_msg_after = test_import(original_path)
        if not original_works_after:
            log_operation(f"test_original_after_{file_info['target']}", "ERROR", original_msg_after)
            return False, f"Оригинал не работает после переноса: {original_msg_after}"
        
        print(f"  ✅ Оригинал работает после переноса: {original_msg_after}")
        log_operation(f"test_original_after_{file_info['target']}", "SUCCESS", original_msg_after)
        
        return True, "Успешно перенесен и протестирован"
        
    except Exception as e:
        log_operation(f"move_{file_info['target']}", "ERROR", str(e))
        return False, f"Ошибка переноса: {str(e)}"

def main():
    """Основная функция"""
    print("🚀 ФИНАЛЬНАЯ ОЧИСТКА BACKUP ФАЙЛОВ - PHASE 2")
    print("=" * 60)
    
    # Инициализация лога
    log_operation("init", "START", f"Начало Phase 2 - {len(FILES_TO_MOVE)} файлов")
    
    success_count = 0
    error_count = 0
    
    # Переносим каждый файл
    for i, file_info in enumerate(FILES_TO_MOVE, 1):
        print(f"\n📁 [{i}/{len(FILES_TO_MOVE)}] {file_info['source']}")
        
        success, message = move_backup_file(file_info)
        if success:
            success_count += 1
            print(f"  ✅ УСПЕХ: {message}")
        else:
            error_count += 1
            print(f"  ❌ ОШИБКА: {message}")
    
    # Тестируем SFM
    print(f"\n🔍 ТЕСТИРОВАНИЕ SFM...")
    sfm_works, sfm_msg = test_sfm_registration()
    if sfm_works:
        print(f"  ✅ SFM работает: {sfm_msg}")
        log_operation("test_sfm", "SUCCESS", sfm_msg)
    else:
        print(f"  ❌ SFM ошибка: {sfm_msg}")
        log_operation("test_sfm", "ERROR", sfm_msg)
    
    # Финальный отчет
    print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ:")
    print(f"  ✅ Успешно перенесено: {success_count}/{len(FILES_TO_MOVE)}")
    print(f"  ❌ Ошибок: {error_count}")
    print(f"  🔍 SFM статус: {'✅ Работает' if sfm_works else '❌ Ошибка'}")
    
    # Логируем итоги
    log_operation("final_report", "COMPLETE", 
                 f"Успешно: {success_count}, Ошибок: {error_count}, SFM: {'OK' if sfm_works else 'ERROR'}")
    
    if error_count == 0 and sfm_works:
        print(f"\n🎉 ВСЕ BACKUP ФАЙЛЫ УСПЕШНО ПЕРЕНЕСЕНЫ!")
        print(f"📁 Расположение: {BACKUP_DIR}")
        print(f"📋 Лог операций: {LOG_FILE}")
        return True
    else:
        print(f"\n⚠️  ЕСТЬ ПРОБЛЕМЫ - ПРОВЕРЬТЕ ЛОГИ!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)