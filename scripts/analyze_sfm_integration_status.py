#!/usr/bin/env python3
"""
🔍 ALADDIN - SFM Integration Status Analysis
Анализ статуса интеграции всех созданных файлов в SFM

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import os
from pathlib import Path

def load_sfm_registry():
    """Загружает реестр функций SFM"""
    registry_path = "/Users/sergejhlystov/ALADDIN_NEW/security/family/data/sfm/function_registry.json"
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('functions', {})
    except Exception as e:
        print(f"Ошибка загрузки SFM реестра: {e}")
        return {}

def analyze_integration_status():
    """Анализирует статус интеграции всех файлов"""
    
    # Загружаем SFM реестр
    sfm_functions = load_sfm_registry()
    print(f"📊 Загружено функций из SFM реестра: {len(sfm_functions)}")
    
    # Список всех созданных файлов
    all_files = {
        # Интеграционные модули (14 файлов)
        "Интеграционные модули": [
            "antifrod_integration.py",
            "audio_deepfake_detection.py", 
            "children_cyber_protection.py",
            "crypto_fraud_protection.py",
            "ddos_protection.py",
            "fakeradar_integration.py",
            "max_messenger_protection.py",
            "national_security_system.py",
            "russian_ai_models.py",
            "russian_banking_integration.py",
            "russian_threat_intelligence.py",
            "sim_card_monitoring.py",
            "telegram_fake_chat_detection.py",
            "vk_messenger_protection.py"
        ],
        
        # Расширения модулей (7 файлов)
        "Расширения модулей": [
            "security_monitoring_fakeradar_expansion.py",
            "security_analytics_antifrod_expansion.py",
            "security_analytics_russian_banking_expansion.py",
            "threat_intelligence_russian_context_expansion.py",
            "family_communication_hub_children_protection_expansion.py",
            "family_communication_hub_max_messenger_expansion.py",
            "incognito_protection_bot_telegram_expansion.py"
        ],
        
        # Скрипты создания (15 файлов)
        "Скрипты создания": [
            "create_sim_card_monitoring.py",
            "create_max_messenger_integration.py",
            "create_banking_integration.py",
            "create_gosuslugi_integration.py",
            "create_digital_sovereignty.py",
            "create_telegram_enhancement.py",
            "create_audio_deepfake_detection.py",
            "create_vk_messenger_integration.py",
            "create_crypto_fraud_protection.py",
            "create_ddos_protection.py",
            "integrate_fakeradar.py",
            "integrate_antifrod_system.py",
            "test_call_protection_system.py",
            "run_all_integrations.py",
            "create_children_cyber_threats_protection.py"
        ]
    }
    
    # Анализируем статус интеграции
    integrated_files = []
    not_integrated_files = []
    
    print("\n🔍 АНАЛИЗ СТАТУСА ИНТЕГРАЦИИ В SFM:")
    print("=" * 80)
    
    for group_name, file_list in all_files.items():
        print(f"\n📂 {group_name}:")
        print("-" * 60)
        
        for file_name in file_list:
            # Проверяем, есть ли функция в SFM реестре
            is_integrated = False
            
            # Ищем по различным вариантам названий
            base_name = file_name.replace('.py', '').replace('_integration', '').replace('_protection', '').replace('_expansion', '')
            
            for func_id in sfm_functions.keys():
                if (base_name in func_id or 
                    func_id in base_name or
                    any(keyword in func_id for keyword in ['antifrod', 'fakeradar', 'children', 'crypto', 'ddos', 'max', 'national', 'russian', 'sim', 'telegram', 'vk', 'audio'])):
                    is_integrated = True
                    break
            
            if is_integrated:
                integrated_files.append((group_name, file_name))
                print(f"✅ {file_name} - ИНТЕГРИРОВАН В SFM")
            else:
                not_integrated_files.append((group_name, file_name))
                print(f"❌ {file_name} - НЕ ИНТЕГРИРОВАН В SFM")
    
    # Итоговая статистика
    print("\n" + "=" * 80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 80)
    print(f"✅ Интегрировано в SFM: {len(integrated_files)} файлов")
    print(f"❌ НЕ интегрировано в SFM: {len(not_integrated_files)} файлов")
    print(f"📁 Всего файлов: {len(integrated_files) + len(not_integrated_files)}")
    
    return integrated_files, not_integrated_files

def generate_integration_report(integrated_files, not_integrated_files):
    """Генерирует отчет по интеграции"""
    
    report = f"""
# 🔍 ALADDIN - ОТЧЕТ ПО СТАТУСУ ИНТЕГРАЦИИ В SFM
## Разделение файлов на интегрированные и требующие интеграции

---

## 📊 **ОБЩАЯ СТАТИСТИКА**

```
✅ Интегрировано в SFM: {len(integrated_files)} файлов
❌ НЕ интегрировано в SFM: {len(not_integrated_files)} файлов
📁 Всего файлов: {len(integrated_files) + len(not_integrated_files)}
```

---

## ✅ **ГРУППА 1: УЖЕ ИНТЕГРИРОВАНЫ В SFM**

### **📊 Статистика по группам:**
"""
    
    # Группируем интегрированные файлы
    integrated_by_group = {}
    for group, file_name in integrated_files:
        if group not in integrated_by_group:
            integrated_by_group[group] = []
        integrated_by_group[group].append(file_name)
    
    for group_name, file_list in integrated_by_group.items():
        report += f"\n**📂 {group_name} ({len(file_list)} файлов):**\n"
        for file_name in file_list:
            report += f"- ✅ `{file_name}`\n"
    
    report += f"""
---

## ❌ **ГРУППА 2: ТРЕБУЮТ ИНТЕГРАЦИИ В SFM**

### **📊 Статистика по группам:**
"""
    
    # Группируем неинтегрированные файлы
    not_integrated_by_group = {}
    for group, file_name in not_integrated_files:
        if group not in not_integrated_by_group:
            not_integrated_by_group[group] = []
        not_integrated_by_group[group].append(file_name)
    
    for group_name, file_list in not_integrated_by_group.items():
        report += f"\n**📂 {group_name} ({len(file_list)} файлов):**\n"
        for file_name in file_list:
            report += f"- ❌ `{file_name}`\n"
    
    report += f"""
---

## 🎯 **ДЕТАЛЬНЫЙ СПИСОК ДЛЯ ИНТЕГРАЦИИ**

### **🔧 Интеграционные модули (требуют интеграции):**
"""
    
    integration_modules = [f for g, f in not_integrated_files if g == "Интеграционные модули"]
    for i, file_name in enumerate(integration_modules, 1):
        report += f"{i}. `{file_name}`\n"
    
    report += f"""
### **🔧 Расширения модулей (требуют интеграции):**
"""
    
    expansion_modules = [f for g, f in not_integrated_files if g == "Расширения модулей"]
    for i, file_name in enumerate(expansion_modules, 1):
        report += f"{i}. `{file_name}`\n"
    
    report += f"""
### **📜 Скрипты создания (требуют интеграции):**
"""
    
    script_modules = [f for g, f in not_integrated_files if g == "Скрипты создания"]
    for i, file_name in enumerate(script_modules, 1):
        report += f"{i}. `{file_name}`\n"
    
    report += f"""
---

## 🚀 **РЕКОМЕНДАЦИИ ПО ИНТЕГРАЦИИ**

### **📋 Приоритеты интеграции:**
1. **Высокий приоритет:** Интеграционные модули (основная функциональность)
2. **Средний приоритет:** Расширения модулей (улучшения существующих)
3. **Низкий приоритет:** Скрипты создания (вспомогательные)

### **⚙️ Шаги интеграции:**
1. Создать функцию в SFM для каждого модуля
2. Зарегистрировать в JSON реестре
3. Настроить зависимости и конфигурацию
4. Протестировать интеграцию
5. Активировать в системе

---

*Отчет создан: 2025-01-27*  
*Версия: 1.0*  
*Статус: Анализ завершен*
"""
    
    return report

if __name__ == "__main__":
    print("🚀 Запуск анализа статуса интеграции в SFM...")
    
    integrated_files, not_integrated_files = analyze_integration_status()
    
    # Генерируем отчет
    report = generate_integration_report(integrated_files, not_integrated_files)
    
    # Сохраняем отчет
    report_path = "/Users/sergejhlystov/Desktop/ALADDIN_SFM_INTEGRATION_STATUS_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Отчет сохранен: {report_path}")
    print("\n🎯 АНАЛИЗ ЗАВЕРШЕН!")