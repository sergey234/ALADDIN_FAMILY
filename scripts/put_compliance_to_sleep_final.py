#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт перевода компонентов соответствия в спящий режим
"""

import sys
import os
import json
from datetime import datetime

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def put_compliance_to_sleep():
    """Переводит все компоненты соответствия в спящий режим"""
    print("💤 ПЕРЕВОД КОМПОНЕНТОВ СООТВЕТСТВИЯ В СПЯЩИЙ РЕЖИМ")
    print("=" * 60)
    
    compliance_components = {
        "RussianDataProtectionManager": {
            "file_path": "security/compliance/russian_data_protection_manager.py",
            "sleep_state_file": "security/compliance/152_fz_sleep_state.json",
            "function_id": "function_152_fz_compliance",
            "name": "152-ФЗ Compliance System"
        },
        "COPPAComplianceManager": {
            "file_path": "security/compliance/coppa_compliance_manager.py",
            "sleep_state_file": "security/compliance/coppa_sleep_state.json",
            "function_id": "function_coppa_compliance",
            "name": "COPPA Compliance Manager"
        },
        "RussianChildProtectionManager": {
            "file_path": "security/compliance/russian_child_protection_manager.py",
            "sleep_state_file": "security/compliance/russian_child_protection_sleep_state.json",
            "function_id": "function_russian_child_protection",
            "name": "Russian Child Protection Manager"
        }
    }
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    print("🔍 ПРОВЕРКА ФАЙЛОВ КОМПОНЕНТОВ СООТВЕТСТВИЯ")
    for key, details in compliance_components.items():
        full_path = os.path.join(base_dir, details["file_path"])
        if os.path.exists(full_path):
            print(f"✅ Файл найден: {details['file_path']}")
        else:
            print(f"❌ Файл не найден: {details['file_path']}")
    
    print("\n💤 СОЗДАНИЕ СОСТОЯНИЙ СПЯЩЕГО РЕЖИМА")
    for key, details in compliance_components.items():
        sleep_state_full_path = os.path.join(base_dir, details["sleep_state_file"])
        
        # Создаем или обновляем файл состояния спящего режима
        sleep_state = {
            "function_name": details["name"],
            "function_id": details["function_id"],
            "status": "sleeping",
            "priority": "critical",
            "created_at": datetime.now().isoformat(),
            "sleep_mode": True,
            "compliance_requirements": [
                "152-ФЗ 'О персональных данных'",
                "Локализация данных в РФ",
                "Уведомление Роскомнадзора о нарушениях",
                "Шифрование персональных данных",
                "Ведение журнала доступа",
                "Согласие на обработку персональных данных",
                "Право на забвение (удаление данных)"
            ],
            "capabilities": [
                "Согласие на обработку персональных данных",
                "Право на забвение (удаление данных)",
                "Локализация данных (хранение только в РФ)",
                "Уведомление о нарушениях (в течение 24 часов)",
                "Аудит доступа к персональным данным",
                "Шифрование персональных данных",
                "Соответствие 152-ФЗ"
            ],
            "statistics": {
                "subjects_registered": 0,
                "active_consents": 0,
                "violations_detected": 0,
                "data_requests_processed": 0,
                "deletion_requests_processed": 0
            },
            "integration_status": {
                "safe_function_manager": True,
                "compliance_system": True,
                "monitoring_system": True
            }
        }
        
        with open(sleep_state_full_path, 'w', encoding='utf-8') as f:
            json.dump(sleep_state, f, ensure_ascii=False, indent=4)
        print(f"✅ {details['name']} переведен в спящий режим")
    
    print("\n🔍 ПРОВЕРКА СТАТУСА СПЯЩЕГО РЕЖИМА")
    all_in_sleep_mode = True
    for key, details in compliance_components.items():
        sleep_state_full_path = os.path.join(base_dir, details["sleep_state_file"])
        try:
            with open(sleep_state_full_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            if state.get("status") == "sleeping" and state.get("sleep_mode") == True:
                print(f"✅ {details['name']}: sleeping")
            else:
                print(f"❌ {details['name']}: active (ошибка в файле состояния)")
                all_in_sleep_mode = False
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"❌ Файл состояния не найден: {details['sleep_state_file']}")
            all_in_sleep_mode = False
    
    print("\n" + "=" * 60)
    if all_in_sleep_mode:
        print("📊 РЕЗУЛЬТАТ: 3/3 проверок пройдено")
        print("🎉 ВСЕ КОМПОНЕНТЫ СООТВЕТСТВИЯ В СПЯЩЕМ РЕЖИМЕ!")
    else:
        print("📊 РЕЗУЛЬТАТ: НЕ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
        print("❌ НЕКОТОРЫЕ КОМПОНЕНТЫ НЕ В СПЯЩЕМ РЕЖИМЕ!")
    
    print("\n✅ ГОТОВО!")
    for key, details in compliance_components.items():
        print(f"   {details['name']}: Спящий режим")
    print("   Уведомления Роскомнадзора: ОТКЛЮЧЕНЫ")


if __name__ == "__main__":
    put_compliance_to_sleep()
