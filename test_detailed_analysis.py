#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест детального анализа универсальной системы качества
"""

import sys
import json
from security.ai_agents.universal_quality_system import analyze_file_universally

def test_detailed_analysis(file_path: str):
    """Детальный анализ файла с полным выводом"""
    print(f"🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ФАЙЛА: {file_path}")
    print("=" * 80)
    
    # Выполняем полный анализ
    result = analyze_file_universally(file_path)
    
    if "error" in result:
        print(f"❌ Ошибка: {result['error']}")
        return
    
    # Выводим общую информацию
    print(f"📁 Файл: {result['file_path']}")
    print(f"📊 Общий балл: {result['overall_score']:.1f}/100")
    print(f"📏 Строк кода: {result['line_count']}")
    print(f"📊 Размер файла: {result['file_size']} байт")
    print()
    
    # Детальный анализ каждого компонента
    analysis_results = result.get('analysis_results', {})
    
    print("🔍 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ АНАЛИЗА:")
    print("-" * 50)
    
    # 1. Синтаксический анализ
    if 'syntax_analysis' in analysis_results:
        syntax = analysis_results['syntax_analysis']
        print(f"1. СИНТАКСИС: {'✅ Успешно' if syntax.get('status') == 'success' else '❌ Ошибка'}")
        if 'ast_analysis' in syntax:
            ast_info = syntax['ast_analysis']
            print(f"   - AST валиден: {'✅' if ast_info.get('valid_ast') else '❌'}")
            print(f"   - Узлов AST: {ast_info.get('nodes_count', 0)}")
            print(f"   - Глубина AST: {ast_info.get('depth', 0)}")
        print()
    
    # 2. Анализ импортов
    if 'import_analysis' in analysis_results:
        imports = analysis_results['import_analysis']
        print(f"2. ИМПОРТЫ: {'✅ Успешно' if imports.get('status') == 'success' else '❌ Ошибка'}")
        if 'import_analysis' in imports:
            imp_info = imports['import_analysis']
            print(f"   - Всего импортов: {imp_info.get('total_imports', 0)}")
            print(f"   - Неиспользуемых: {len(imp_info.get('unused_imports', []))}")
        print()
    
    # 3. Анализ flake8
    if 'flake8_analysis' in analysis_results:
        flake8 = analysis_results['flake8_analysis']
        print(f"3. FLAKE8: {flake8.get('total_errors', 0)} ошибок")
        print(f"   - Балл качества: {flake8.get('quality_score', 0):.1f}/100")
        if 'error_groups' in flake8:
            groups = flake8['error_groups']
            print(f"   - Безопасных: {len(groups.get('safe', []))}")
            print(f"   - Ручных: {len(groups.get('manual', []))}")
            print(f"   - Опасных: {len(groups.get('dangerous', []))}")
            print(f"   - Критических: {len(groups.get('critical', []))}")
        print()
    
    # 4. Анализ безопасности
    if 'security_analysis' in analysis_results:
        security = analysis_results['security_analysis']
        print(f"4. БЕЗОПАСНОСТЬ: {security.get('total_vulnerabilities', 0)} уязвимостей")
        print(f"   - Балл безопасности: {security.get('security_score', 0):.1f}/100")
        print(f"   - Критических: {security.get('critical_vulnerabilities', 0)}")
        print(f"   - Высокого уровня: {security.get('high_vulnerabilities', 0)}")
        print()
    
    # 5. Анализ производительности
    if 'performance_analysis' in analysis_results:
        perf = analysis_results['performance_analysis']
        print(f"5. ПРОИЗВОДИТЕЛЬНОСТЬ: {perf.get('total_issues', 0)} проблем")
        print(f"   - Балл производительности: {perf.get('performance_score', 0):.1f}/100")
        print()
    
    # 6. Анализ структуры
    if 'structure_analysis' in analysis_results:
        structure = analysis_results['structure_analysis']
        print(f"6. СТРУКТУРА: {structure.get('total_classes', 0)} классов, {structure.get('total_functions', 0)} функций")
        print(f"   - Балл структуры: {structure.get('structure_score', 0):.1f}/100")
        print(f"   - Общая сложность: {structure.get('total_complexity', 0)}")
        print(f"   - Средняя сложность: {structure.get('average_complexity', 0):.1f}")
        print()
    
    # 7. Анализ документации
    if 'documentation_analysis' in analysis_results:
        doc = analysis_results['documentation_analysis']
        print(f"7. ДОКУМЕНТАЦИЯ: {doc.get('comment_percentage', 0):.1f}% комментариев")
        print(f"   - Балл документации: {doc.get('documentation_score', 0):.1f}/100")
        print(f"   - Строк документации: {doc.get('docstring_lines', 0)}")
        print()
    
    # 8. Анализ метрик
    if 'metrics_analysis' in analysis_results:
        metrics = analysis_results['metrics_analysis']
        print(f"8. МЕТРИКИ:")
        print(f"   - Строк кода: {metrics.get('code_lines', 0)}")
        print(f"   - Комментариев: {metrics.get('comment_lines', 0)}")
        print(f"   - Пустых строк: {metrics.get('blank_lines', 0)}")
        print(f"   - Соотношение кода: {metrics.get('code_ratio', 0):.1%}")
        print()
    
    # 9. Сканирование уязвимостей
    if 'vulnerability_scan' in analysis_results:
        vuln = analysis_results['vulnerability_scan']
        print(f"9. УЯЗВИМОСТИ: {vuln.get('total_vulnerabilities', 0)} найдено")
        print(f"   - Балл уязвимостей: {vuln.get('vulnerability_score', 0):.1f}/100")
        print()
    
    # 10. Запахи кода
    if 'code_smells' in analysis_results:
        smells = analysis_results['code_smells']
        print(f"10. ЗАПАХИ КОДА: {smells.get('total_smells', 0)} найдено")
        print(f"    - Балл запахов: {smells.get('smell_score', 0):.1f}/100")
        print()
    
    # Сводка качества
    if 'quality_summary' in result:
        summary = result['quality_summary']
        print("📊 СВОДКА КАЧЕСТВА:")
        print(f"   - Общее качество: {summary.get('overall_quality', 'N/A')}")
        print(f"   - Всего проблем: {summary.get('total_issues', 0)}")
        print(f"   - Критических: {summary.get('critical_issues', 0)}")
        print()
    
    # Рекомендации
    if 'recommendations' in result:
        recommendations = result['recommendations']
        if recommendations:
            print("💡 РЕКОМЕНДАЦИИ:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
            print()
    
    # План исправлений
    if 'fix_plan' in result:
        plan = result['fix_plan']
        print("📋 ПЛАН ИСПРАВЛЕНИЙ:")
        print(f"   - Всего проблем: {plan.get('total_issues', 0)}")
        print(f"   - Безопасных: {plan.get('safe_fixes', 0)}")
        print(f"   - Ручных: {plan.get('manual_fixes', 0)}")
        print(f"   - Опасных: {plan.get('dangerous_fixes', 0)}")
        print(f"   - Критических: {plan.get('critical_fixes', 0)}")
        
        if 'steps' in plan and plan['steps']:
            print("   Шаги исправлений:")
            for step in plan['steps']:
                print(f"   - Шаг {step['step']}: {step['action']} ({step['count']} проблем)")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_detailed_analysis(sys.argv[1])
    else:
        print("Использование: python3 test_detailed_analysis.py <путь_к_файлу>")