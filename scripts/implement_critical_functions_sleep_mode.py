#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перевода не критичных функций в спящий режим
Оставляет активными только 50 самых критичных функций
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

def load_sfm_registry() -> Dict:
    """Загружает реестр SFM"""
    try:
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки реестра SFM: {e}")
        return None

def load_critical_functions_config() -> Dict:
    """Загружает конфигурацию критичных функций"""
    try:
        with open('CRITICAL_FUNCTIONS_SLEEP_MODE_CONFIG.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return None

def identify_functions_to_sleep(registry: Dict, config: Dict) -> Tuple[List[str], List[str]]:
    """Определяет функции для перевода в спящий режим и активные функции"""
    
    # Получаем список критичных функций из конфигурации
    critical_functions = [func['id'] for func in config['top_50_critical_functions']]
    
    active_functions = []
    sleep_functions = []
    
    for func_id, func_data in registry['functions'].items():
        is_critical = func_data.get('is_critical', False)
        security_level = func_data.get('security_level', 'unknown')
        status = func_data.get('status', 'unknown')
        
        # Функция остается активной если:
        # 1. Она в списке критичных функций ИЛИ
        # 2. Она критическая И имеет высокий уровень безопасности ИЛИ
        # 3. Она уже отключена (не трогаем)
        if (func_id in critical_functions or 
            (is_critical and security_level in ['critical', 'high']) or
            status == 'disabled'):
            active_functions.append(func_id)
        else:
            sleep_functions.append(func_id)
    
    return active_functions, sleep_functions

def update_function_status(registry: Dict, function_ids: List[str], new_status: str) -> Dict:
    """Обновляет статус функций в реестре"""
    updated_count = 0
    
    for func_id in function_ids:
        if func_id in registry['functions']:
            registry['functions'][func_id]['status'] = new_status
            registry['functions'][func_id]['last_updated'] = datetime.now().isoformat()
            if new_status == 'sleeping':
                registry['functions'][func_id]['sleep_start_time'] = datetime.now().isoformat()
                registry['functions'][func_id]['sleep_reason'] = 'Переведена в спящий режим для оптимизации ресурсов'
            updated_count += 1
    
    return updated_count

def save_updated_registry(registry: Dict) -> bool:
    """Сохраняет обновленный реестр"""
    try:
        # Создаем резервную копию
        backup_file = f"data/sfm/function_registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        
        # Сохраняем обновленный реестр
        with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Создана резервная копия: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения реестра: {e}")
        return False

def generate_sleep_mode_report(active_functions: List[str], sleep_functions: List[str], 
                             config: Dict) -> Dict:
    """Генерирует отчет о переводе в спящий режим"""
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'strategy': config['sleep_mode_strategy']['strategy'],
        'total_functions': len(active_functions) + len(sleep_functions),
        'active_functions': {
            'count': len(active_functions),
            'percentage': round(len(active_functions) / (len(active_functions) + len(sleep_functions)) * 100, 2),
            'list': active_functions
        },
        'sleep_functions': {
            'count': len(sleep_functions),
            'percentage': round(len(sleep_functions) / (len(active_functions) + len(sleep_functions)) * 100, 2),
            'list': sleep_functions
        },
        'expected_benefits': config['expected_benefits'],
        'implementation_phases': config['implementation_plan']
    }
    
    return report

def main():
    """Основная функция"""
    print("🌙 ПЕРЕВОД НЕ КРИТИЧНЫХ ФУНКЦИЙ В СПЯЩИЙ РЕЖИМ")
    print("=" * 60)
    
    # Загружаем данные
    print("📥 Загрузка данных...")
    registry = load_sfm_registry()
    if not registry:
        return False
    
    config = load_critical_functions_config()
    if not config:
        return False
    
    print("✅ Данные загружены успешно")
    
    # Определяем функции для перевода
    print("\n🔍 Анализ функций...")
    active_functions, sleep_functions = identify_functions_to_sleep(registry, config)
    
    print(f"📊 Найдено функций:")
    print(f"   • Активных: {len(active_functions)}")
    print(f"   • Для перевода в спящий режим: {len(sleep_functions)}")
    
    # Показываем топ-10 активных функций
    print(f"\n🏆 ТОП-10 АКТИВНЫХ ФУНКЦИЙ:")
    print("-" * 40)
    for i, func_id in enumerate(active_functions[:10], 1):
        func_data = registry['functions'].get(func_id, {})
        name = func_data.get('name', func_id)
        security_level = func_data.get('security_level', 'unknown')
        print(f"{i:2d}. {func_id} - {name} ({security_level})")
    
    if len(active_functions) > 10:
        print(f"    ... и еще {len(active_functions) - 10} функций")
    
    # Показываем первые 10 функций для перевода в спящий режим
    print(f"\n😴 ПЕРВЫЕ 10 ФУНКЦИЙ ДЛЯ ПЕРЕВОДА В СПЯЩИЙ РЕЖИМ:")
    print("-" * 50)
    for i, func_id in enumerate(sleep_functions[:10], 1):
        func_data = registry['functions'].get(func_id, {})
        name = func_data.get('name', func_id)
        security_level = func_data.get('security_level', 'unknown')
        print(f"{i:2d}. {func_id} - {name} ({security_level})")
    
    if len(sleep_functions) > 10:
        print(f"    ... и еще {len(sleep_functions) - 10} функций")
    
    # Запрашиваем подтверждение
    print(f"\n⚠️  ВНИМАНИЕ!")
    print(f"Будет переведено в спящий режим: {len(sleep_functions)} функций")
    print(f"Останется активными: {len(active_functions)} функций")
    
    confirm = input("\n❓ Продолжить? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Операция отменена")
        return False
    
    # Обновляем статусы функций
    print(f"\n🔄 Обновление статусов функций...")
    
    # Переводим функции в спящий режим
    sleep_updated = update_function_status(registry, sleep_functions, 'sleeping')
    print(f"✅ Переведено в спящий режим: {sleep_updated} функций")
    
    # Обновляем общую статистику
    registry['last_updated'] = datetime.now().isoformat()
    registry['total_functions'] = len(registry['functions'])
    registry['active_functions'] = len(active_functions)
    registry['sleeping_functions'] = len(sleep_functions)
    registry['disabled_functions'] = sum(1 for f in registry['functions'].values() if f.get('status') == 'disabled')
    
    # Сохраняем обновленный реестр
    if save_updated_registry(registry):
        print("✅ Реестр SFM обновлен успешно")
    else:
        print("❌ Ошибка сохранения реестра")
        return False
    
    # Генерируем отчет
    print(f"\n📊 Генерация отчета...")
    report = generate_sleep_mode_report(active_functions, sleep_functions, config)
    
    report_file = f"CRITICAL_FUNCTIONS_SLEEP_MODE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Отчет сохранен: {report_file}")
    
    # Итоговая статистика
    print(f"\n🎉 ПЕРЕВОД В СПЯЩИЙ РЕЖИМ ЗАВЕРШЕН!")
    print("=" * 60)
    print(f"📊 Итоговая статистика:")
    print(f"   • Всего функций: {report['total_functions']}")
    print(f"   • Активных: {report['active_functions']['count']} ({report['active_functions']['percentage']}%)")
    print(f"   • В спящем режиме: {report['sleep_functions']['count']} ({report['sleep_functions']['percentage']}%)")
    print(f"   • Отключенных: {registry['disabled_functions']}")
    
    print(f"\n💡 Ожидаемые преимущества:")
    for benefit, description in report['expected_benefits'].items():
        print(f"   • {benefit}: {description}")
    
    print(f"\n📁 Созданные файлы:")
    print(f"   • {report_file} - Отчет о переводе в спящий режим")
    print(f"   • data/sfm/function_registry_backup_*.json - Резервная копия")
    print(f"   • data/sfm/function_registry.json - Обновленный реестр")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)