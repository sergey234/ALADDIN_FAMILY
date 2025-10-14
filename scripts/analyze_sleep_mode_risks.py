#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ рисков перевода функций в спящий режим
Выявляет критические зависимости и потенциальные проблемы
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict

def load_sfm_registry() -> Dict:
    """Загружает реестр SFM"""
    try:
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки реестра SFM: {e}")
        return None

def analyze_dependencies(registry: Dict) -> Dict:
    """Анализирует зависимости между функциями"""
    print("🔍 Анализ зависимостей между функциями...")
    
    # Создаем граф зависимостей
    dependency_graph = defaultdict(list)
    reverse_dependency_graph = defaultdict(list)
    
    for func_id, func_data in registry['functions'].items():
        dependencies = func_data.get('dependencies', [])
        for dep in dependencies:
            dependency_graph[func_id].append(dep)
            reverse_dependency_graph[dep].append(func_id)
    
    # Анализируем критические пути
    critical_paths = []
    high_dependency_functions = []
    
    for func_id, deps in dependency_graph.items():
        if len(deps) > 3:  # Функции с высоким количеством зависимостей
            func_data = registry['functions'].get(func_id, {})
            high_dependency_functions.append({
                'id': func_id,
                'name': func_data.get('name', func_id),
                'dependencies': deps,
                'dependency_count': len(deps),
                'is_critical': func_data.get('is_critical', False),
                'security_level': func_data.get('security_level', 'unknown')
            })
    
    # Функции, от которых зависят другие
    high_dependents_functions = []
    for func_id, dependents in reverse_dependency_graph.items():
        if len(dependents) > 2:  # Функции, от которых зависят более 2 других
            func_data = registry['functions'].get(func_id, {})
            high_dependents_functions.append({
                'id': func_id,
                'name': func_data.get('name', func_id),
                'dependents': dependents,
                'dependent_count': len(dependents),
                'is_critical': func_data.get('is_critical', False),
                'security_level': func_data.get('security_level', 'unknown')
            })
    
    return {
        'dependency_graph': dict(dependency_graph),
        'reverse_dependency_graph': dict(reverse_dependency_graph),
        'high_dependency_functions': high_dependency_functions,
        'high_dependents_functions': high_dependents_functions
    }

def identify_critical_risks(registry: Dict, dependencies: Dict) -> List[Dict]:
    """Выявляет критические риски"""
    print("🚨 Выявление критических рисков...")
    
    risks = []
    
    # Риск 1: Критические функции с зависимостями
    for func in dependencies['high_dependency_functions']:
        if func['is_critical'] and func['dependency_count'] > 5:
            risks.append({
                'type': 'critical_function_with_dependencies',
                'severity': 'CRITICAL',
                'function_id': func['id'],
                'function_name': func['name'],
                'description': f"Критическая функция {func['name']} имеет {func['dependency_count']} зависимостей",
                'impact': 'Может нарушить работу системы при переводе в спящий режим',
                'recommendation': 'НЕ ПЕРЕВОДИТЬ в спящий режим'
            })
    
    # Риск 2: Функции, от которых зависят критические
    for func in dependencies['high_dependents_functions']:
        critical_dependents = [dep for dep in func['dependents'] 
                             if registry['functions'].get(dep, {}).get('is_critical', False)]
        if critical_dependents:
            risks.append({
                'type': 'function_supports_critical',
                'severity': 'HIGH',
                'function_id': func['id'],
                'function_name': func['name'],
                'description': f"Функция {func['name']} поддерживает {len(critical_dependents)} критических функций",
                'impact': 'Отключение может нарушить работу критических функций',
                'recommendation': 'Требует особого внимания при переводе в спящий режим'
            })
    
    # Риск 3: Функции с высоким уровнем безопасности
    for func_id, func_data in registry['functions'].items():
        security_level = func_data.get('security_level', 'unknown')
        is_critical = func_data.get('is_critical', False)
        if security_level in ['critical', 'high'] and not is_critical:
            risks.append({
                'type': 'high_security_non_critical',
                'severity': 'MEDIUM',
                'function_id': func_id,
                'function_name': func_data.get('name', func_id),
                'description': f"Функция {func_data.get('name', func_id)} имеет высокий уровень безопасности, но не помечена как критическая",
                'impact': 'Может быть неправильно классифицирована',
                'recommendation': 'Пересмотреть классификацию критичности'
            })
    
    return risks

def analyze_sleep_mode_impact(registry: Dict, critical_functions: List[str]) -> Dict:
    """Анализирует влияние перевода в спящий режим"""
    print("📊 Анализ влияния перевода в спящий режим...")
    
    # Функции для перевода в спящий режим
    sleep_functions = []
    for func_id, func_data in registry['functions'].items():
        if func_id not in critical_functions and func_data.get('status') == 'enabled':
            sleep_functions.append(func_id)
    
    # Анализ по типам функций
    type_analysis = defaultdict(int)
    security_level_analysis = defaultdict(int)
    
    for func_id in sleep_functions:
        func_data = registry['functions'].get(func_id, {})
        func_type = func_data.get('function_type', 'unknown')
        security_level = func_data.get('security_level', 'unknown')
        
        type_analysis[func_type] += 1
        security_level_analysis[security_level] += 1
    
    # Анализ потенциальных проблем
    potential_issues = []
    
    # Проверка на функции с высоким уровнем безопасности
    high_security_sleep = [f for f in sleep_functions 
                          if registry['functions'].get(f, {}).get('security_level') in ['critical', 'high']]
    if high_security_sleep:
        potential_issues.append({
            'type': 'high_security_functions_sleep',
            'count': len(high_security_sleep),
            'description': f"{len(high_security_sleep)} функций с высоким уровнем безопасности планируется перевести в спящий режим"
        })
    
    return {
        'sleep_functions_count': len(sleep_functions),
        'sleep_functions': sleep_functions,
        'type_analysis': dict(type_analysis),
        'security_level_analysis': dict(security_level_analysis),
        'potential_issues': potential_issues
    }

def generate_risk_report(registry: Dict, dependencies: Dict, risks: List[Dict], 
                        impact_analysis: Dict) -> Dict:
    """Генерирует отчет о рисках"""
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_functions': len(registry['functions']),
        'critical_functions_count': sum(1 for f in registry['functions'].values() if f.get('is_critical', False)),
        'functions_with_dependencies': len(dependencies['high_dependency_functions']),
        'functions_supporting_others': len(dependencies['high_dependents_functions']),
        'risks': {
            'total': len(risks),
            'critical': len([r for r in risks if r['severity'] == 'CRITICAL']),
            'high': len([r for r in risks if r['severity'] == 'HIGH']),
            'medium': len([r for r in risks if r['severity'] == 'MEDIUM']),
            'low': len([r for r in risks if r['severity'] == 'LOW'])
        },
        'impact_analysis': impact_analysis,
        'recommendations': generate_recommendations(risks, impact_analysis)
    }
    
    return report

def generate_recommendations(risks: List[Dict], impact_analysis: Dict) -> List[str]:
    """Генерирует рекомендации на основе анализа рисков"""
    
    recommendations = []
    
    # Критические рекомендации
    critical_risks = [r for r in risks if r['severity'] == 'CRITICAL']
    if critical_risks:
        recommendations.append("🚨 КРИТИЧЕСКИЕ РИСКИ ОБНАРУЖЕНЫ!")
        recommendations.append("   • НЕ ПЕРЕВОДИТЬ критические функции с зависимостями")
        recommendations.append("   • Провести дополнительный анализ зависимостей")
        recommendations.append("   • Создать план отката")
    
    # Рекомендации по безопасности
    high_security_issues = [i for i in impact_analysis['potential_issues'] 
                           if 'high_security' in i['type']]
    if high_security_issues:
        recommendations.append("⚠️ ВНИМАНИЕ: Функции с высоким уровнем безопасности")
        recommendations.append("   • Пересмотреть классификацию критичности")
        recommendations.append("   • Провести дополнительное тестирование")
    
    # Общие рекомендации
    recommendations.extend([
        "📋 ОБЩИЕ РЕКОМЕНДАЦИИ:",
        "   • Начать с пилотного проекта (10-20 функций)",
        "   • Создать полную карту зависимостей",
        "   • Настроить мониторинг и алерты",
        "   • Подготовить план отката",
        "   • Провести тестирование на копии системы"
    ])
    
    return recommendations

def main():
    """Основная функция"""
    print("🚨 АНАЛИЗ РИСКОВ ПЕРЕВОДА В СПЯЩИЙ РЕЖИМ")
    print("=" * 60)
    
    # Загружаем данные
    print("📥 Загрузка данных...")
    registry = load_sfm_registry()
    if not registry:
        return False
    
    print("✅ Данные загружены успешно")
    
    # Анализируем зависимости
    dependencies = analyze_dependencies(registry)
    print(f"✅ Найдено функций с зависимостями: {len(dependencies['high_dependency_functions'])}")
    print(f"✅ Найдено функций, поддерживающих другие: {len(dependencies['high_dependents_functions'])}")
    
    # Выявляем критические риски
    risks = identify_critical_risks(registry, dependencies)
    print(f"✅ Выявлено рисков: {len(risks)}")
    
    # Загружаем список критических функций
    try:
        with open('TOP_50_CRITICAL_FUNCTIONS.json', 'r', encoding='utf-8') as f:
            critical_functions_data = json.load(f)
        critical_functions = [f['id'] for f in critical_functions_data]
    except:
        print("⚠️ Не удалось загрузить список критических функций")
        critical_functions = []
    
    # Анализируем влияние
    impact_analysis = analyze_sleep_mode_impact(registry, critical_functions)
    print(f"✅ Функций для перевода в спящий режим: {impact_analysis['sleep_functions_count']}")
    
    # Генерируем отчет
    report = generate_risk_report(registry, dependencies, risks, impact_analysis)
    
    # Сохраняем отчет
    report_file = f"SLEEP_MODE_RISKS_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Выводим результаты
    print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА РИСКОВ:")
    print("=" * 60)
    print(f"📈 Всего функций: {report['total_functions']}")
    print(f"🔒 Критических функций: {report['critical_functions_count']}")
    print(f"🔗 Функций с зависимостями: {report['functions_with_dependencies']}")
    print(f"🎯 Функций, поддерживающих другие: {report['functions_supporting_others']}")
    
    print(f"\n🚨 ВЫЯВЛЕННЫЕ РИСКИ:")
    print("-" * 40)
    print(f"🔴 Критические: {report['risks']['critical']}")
    print(f"🟠 Высокие: {report['risks']['high']}")
    print(f"🟡 Средние: {report['risks']['medium']}")
    print(f"🟢 Низкие: {report['risks']['low']}")
    
    if risks:
        print(f"\n⚠️ КРИТИЧЕСКИЕ РИСКИ:")
        print("-" * 40)
        for i, risk in enumerate(risks[:5], 1):
            print(f"{i}. {risk['function_name']} - {risk['description']}")
            print(f"   Рекомендация: {risk['recommendation']}")
            print()
    
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    print("-" * 40)
    for rec in report['recommendations']:
        print(rec)
    
    print(f"\n📁 Отчет сохранен: {report_file}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)