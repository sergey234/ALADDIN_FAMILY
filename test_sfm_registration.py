#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест регистрации компонентов в SFM
Проверка успешной регистрации всех 8 компонентов

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import json
import os
from typing import Dict, Any, List

def test_sfm_registration():
    """Тест регистрации компонентов в SFM"""
    print("🧪 Тестирование регистрации компонентов в SFM...")
    
    # Путь к реестру SFM
    registry_path = "data/sfm/function_registry.json"
    
    if not os.path.exists(registry_path):
        print("❌ Файл реестра SFM не найден!")
        return False
    
    try:
        # Загрузка реестра
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        print(f"✅ Реестр SFM загружен: {registry_path}")
        
        # Список компонентов для проверки
        expected_components = [
            "external_integrations_system",
            "threat_intelligence_system", 
            "automated_audit_system",
            "enhanced_dashboard_v2",
            "audit_scheduler",
            "compliance_monitor",
            "audit_dashboard_integration",
            "external_integrations_dashboard"
        ]
        
        # Проверка регистрации каждого компонента
        registered_components = []
        missing_components = []
        
        for component_id in expected_components:
            if component_id in registry.get("functions", {}):
                component = registry["functions"][component_id]
                registered_components.append({
                    "id": component_id,
                    "name": component.get("name", "Unknown"),
                    "status": component.get("status", "unknown"),
                    "is_critical": component.get("is_critical", False),
                    "quality_score": component.get("quality_score", "unknown"),
                    "lines_of_code": component.get("lines_of_code", 0)
                })
                print(f"  ✅ {component_id}: {component.get('name', 'Unknown')} - {component.get('status', 'unknown')}")
            else:
                missing_components.append(component_id)
                print(f"  ❌ {component_id}: НЕ НАЙДЕН!")
        
        # Проверка статистики
        stats = registry.get("statistics", {})
        total_functions = stats.get("total_functions", 0)
        external_integrations = stats.get("external_integrations_added", 0)
        
        print(f"\n📊 Статистика SFM:")
        print(f"  Всего функций: {total_functions}")
        print(f"  Внешних интеграций: {external_integrations}")
        print(f"  Зарегистрировано компонентов: {len(registered_components)}")
        print(f"  Отсутствует компонентов: {len(missing_components)}")
        
        # Результаты тестирования
        success = len(missing_components) == 0
        
        if success:
            print(f"\n🎉 ВСЕ {len(registered_components)} КОМПОНЕНТОВ УСПЕШНО ЗАРЕГИСТРИРОВАНЫ!")
            
            # Детальная статистика
            critical_components = [c for c in registered_components if c["is_critical"]]
            auxiliary_components = [c for c in registered_components if not c["is_critical"]]
            
            print(f"\n📋 Детальная статистика:")
            print(f"  🔥 Критических компонентов: {len(critical_components)}")
            print(f"  🔧 Вспомогательных компонентов: {len(auxiliary_components)}")
            
            # Качество компонентов
            a_plus_components = [c for c in registered_components if c["quality_score"] == "A+"]
            print(f"  ⭐ Компонентов с качеством A+: {len(a_plus_components)}")
            
            # Общее количество строк кода
            total_lines = sum(c["lines_of_code"] for c in registered_components)
            print(f"  📝 Общее количество строк кода: {total_lines:,}")
            
            # Статус компонентов
            active_components = [c for c in registered_components if c["status"] == "active"]
            print(f"  🟢 Активных компонентов: {len(active_components)}")
            
        else:
            print(f"\n❌ ОШИБКА: {len(missing_components)} компонентов не найдены!")
            for missing in missing_components:
                print(f"  - {missing}")
        
        return success
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def test_component_details():
    """Тест деталей компонентов"""
    print("\n🔍 Детальный анализ компонентов...")
    
    registry_path = "data/sfm/function_registry.json"
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        components = registry.get("functions", {})
        
        # Анализ по категориям
        categories = {}
        for component_id, component in components.items():
            if component_id.startswith(("external_", "threat_", "automated_", "enhanced_", "audit_", "compliance_")):
                category = component.get("category", "unknown")
                if category not in categories:
                    categories[category] = []
                categories[category].append(component_id)
        
        print(f"\n📁 Компоненты по категориям:")
        for category, component_list in categories.items():
            print(f"  {category}: {len(component_list)} компонентов")
            for comp_id in component_list:
                comp = components[comp_id]
                print(f"    - {comp_id}: {comp.get('name', 'Unknown')} ({comp.get('status', 'unknown')})")
        
        # Анализ зависимостей
        all_dependencies = set()
        for component_id, component in components.items():
            if component_id.startswith(("external_", "threat_", "automated_", "enhanced_", "audit_", "compliance_")):
                deps = component.get("dependencies", [])
                all_dependencies.update(deps)
        
        print(f"\n🔗 Общие зависимости ({len(all_dependencies)}):")
        for dep in sorted(all_dependencies):
            print(f"  - {dep}")
        
        # Анализ функций
        all_features = set()
        for component_id, component in components.items():
            if component_id.startswith(("external_", "threat_", "automated_", "enhanced_", "audit_", "compliance_")):
                features = component.get("features", [])
                all_features.update(features)
        
        print(f"\n⚡ Общие функции ({len(all_features)}):")
        for feature in sorted(all_features):
            print(f"  - {feature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при детальном анализе: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ РЕГИСТРАЦИИ КОМПОНЕНТОВ В SFM")
    print("=" * 60)
    
    # Тест регистрации
    registration_success = test_sfm_registration()
    
    # Тест деталей
    details_success = test_component_details()
    
    print("\n" + "=" * 60)
    
    if registration_success and details_success:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Все 8 компонентов зарегистрированы в SFM")
        print("✅ Детальный анализ выполнен")
        print("🚀 Система готова к использованию!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        if not registration_success:
            print("❌ Ошибка регистрации компонентов")
        if not details_success:
            print("❌ Ошибка детального анализа")
    
    return registration_success and details_success

if __name__ == "__main__":
    main()