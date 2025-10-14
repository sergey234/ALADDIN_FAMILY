#!/usr/bin/env python3
"""
ИСПРАВЛЕННЫЙ СКРИПТ АНАЛИЗА КАЧЕСТВА КОДА
Анализирует качество кода менеджеров с правильной обработкой AST
"""

import ast
import os
import re
from typing import Dict, List, Any, Tuple, Union

def analyze_file_quality(file_path: str) -> Dict[str, Any]:
    """
    Анализ качества файла с исправленной обработкой AST
    
    Args:
        file_path: Путь к файлу для анализа
        
    Returns:
        Словарь с метриками качества
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Подсчет метрик
        lines = content.split('\n')
        total_lines = len([line for line in lines if line.strip()])
        
        # Комментарии и документация
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        docstring_lines = 0
        type_hint_lines = 0
        complex_algorithm_lines = 0
        
        # Анализ AST с исправленной обработкой
        classes = []
        functions = []
        methods = []
        imports = []
        
        def safe_walk(node):
            """Безопасный обход AST с обработкой ошибок"""
            try:
                for child in ast.walk(node):
                    yield child
            except Exception as e:
                print(f"⚠️ Ошибка обхода AST: {e}")
                return
        
        for node in safe_walk(tree):
            try:
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    # Подсчет docstring в классе
                    if (node.body and isinstance(node.body[0], ast.Expr) 
                        and isinstance(node.body[0].value, ast.Constant)):
                        docstring_lines += len(str(node.body[0].value.value).split('\n'))
                elif isinstance(node, ast.FunctionDef):
                    # Проверяем, является ли функция методом класса
                    is_method = False
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef) and node in parent.body:
                            is_method = True
                            break
                    
                    if is_method:
                        methods.append(node.name)
                    else:
                        functions.append(node.name)
                    
                    # Подсчет docstring в функции
                    if (node.body and isinstance(node.body[0], ast.Expr) 
                        and isinstance(node.body[0].value, ast.Constant)):
                        docstring_lines += len(str(node.body[0].value.value).split('\n'))
                    
                    # Подсчет type hints
                    if node.returns:
                        type_hint_lines += 1
                    for arg in node.args.args:
                        if arg.annotation:
                            type_hint_lines += 1
                elif isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    imports.extend([alias.name for alias in node.names])
            except Exception as e:
                print(f"⚠️ Ошибка обработки узла AST: {e}")
                continue
        
        # Поиск сложных алгоритмов по ключевым словам
        algorithm_keywords = [
            'sklearn', 'numpy', 'scipy', 'pandas', 'matplotlib', 'seaborn',
            'RandomForest', 'KMeans', 'PCA', 'IsolationForest', 'DBSCAN',
            'StandardScaler', 'TfidfVectorizer', 'MinMaxScaler',
            'LinearRegression', 'LogisticRegression', 'SVM', 'SVC',
            'networkx', 'stats', 'statistical', 'correlation',
            'MLPClassifier', 'GradientBoosting', 'AdaBoost',
            'cross_val_score', 'GridSearchCV', 'train_test_split',
            'confusion_matrix', 'classification_report', 'roc_auc_score',
            'mean_squared_error', 'r2_score', 'accuracy_score',
            'silhouette_score', 'calinski_harabasz_score',
            'davies_bouldin_score', 'adjusted_rand_score',
            'mutual_info_score', 'normalized_mutual_info_score',
            'homogeneity_score', 'completeness_score', 'v_measure_score',
            'f1_score', 'precision_score', 'recall_score',
            'jaccard_score', 'hamming_loss', 'zero_one_loss',
            'log_loss', 'hinge_loss', 'huber_loss',
            'mean_absolute_error', 'median_absolute_error',
            'explained_variance_score', 'max_error',
            'mean_poisson_deviance', 'mean_gamma_deviance',
            'mean_tweedie_deviance', 'd2_tweedie_score',
            'd2_pinball_score', 'd2_absolute_error_score'
        ]
        
        for line in lines:
            if any(keyword in line for keyword in algorithm_keywords):
                complex_algorithm_lines += 1
        
        # Расчет процентов
        doc_percentage = (docstring_lines / max(total_lines, 1)) * 100
        type_hint_percentage = (type_hint_lines / max(total_lines, 1)) * 100
        algorithm_percentage = (complex_algorithm_lines / max(total_lines, 1)) * 100
        
        # Расчет общего балла (взвешенный)
        size_score = min(100, (total_lines / 500) * 100)  # Нормализация по размеру
        doc_score = min(100, doc_percentage * 2)  # Документация важна
        type_score = min(100, type_hint_percentage * 2)  # Type hints важны
        algorithm_score = min(100, algorithm_percentage * 3)  # Алгоритмы очень важны
        structure_score = min(100, (len(classes) + len(functions) + len(methods)) * 5)
        
        # Взвешенный итоговый балл
        final_score = (
            size_score * 0.2 +
            doc_score * 0.25 +
            type_score * 0.2 +
            algorithm_score * 0.25 +
            structure_score * 0.1
        )
        
        return {
            'file_name': os.path.basename(file_path),
            'total_lines': total_lines,
            'comment_lines': comment_lines,
            'docstring_lines': docstring_lines,
            'type_hint_lines': type_hint_lines,
            'complex_algorithm_lines': complex_algorithm_lines,
            'classes': len(classes),
            'functions': len(functions),
            'methods': len(methods),
            'imports': len(imports),
            'doc_percentage': doc_percentage,
            'type_hint_percentage': type_hint_percentage,
            'algorithm_percentage': algorithm_percentage,
            'final_score': final_score,
            'quality_grade': 'A+' if final_score >= 80 else 'A' if final_score >= 70 else 'B' if final_score >= 60 else 'C'
        }
    except Exception as e:
        return {
            'error': str(e), 
            'file_name': os.path.basename(file_path),
            'total_lines': 0,
            'final_score': 0,
            'quality_grade': 'ERROR'
        }

def main():
    """Основная функция анализа качества"""
    print('🔍 ИСПРАВЛЕННАЯ ПРОВЕРКА КАЧЕСТВА ВСЕХ 5 МЕНЕДЖЕРОВ')
    print('=' * 70)
    
    # Переходим в директорию с менеджерами
    os.chdir('security/ai_agents')
    
    managers = [
        'monitor_manager.py',
        'alert_manager.py', 
        'report_manager.py',
        'analytics_manager.py',
        'dashboard_manager.py'
    ]
    
    results = []
    total_score = 0
    valid_results = 0
    
    for manager_file in managers:
        if os.path.exists(manager_file):
            result = analyze_file_quality(manager_file)
            results.append(result)
            
            if 'error' not in result:
                valid_results += 1
                total_score += result['final_score']
            
            print(f'\n📋 {result["file_name"]}:')
            print('-' * 50)
            
            if 'error' in result:
                print(f'  ❌ Ошибка: {result["error"]}')
                print(f'  🏆 КАЧЕСТВО: ERROR')
            else:
                print(f'  📊 Строки кода: {result["total_lines"]}')
                print(f'  📝 Комментарии: {result["comment_lines"]}')
                print(f'  📖 Документация: {result["docstring_lines"]} ({result["doc_percentage"]:.1f}%)')
                print(f'  🏷️  Type hints: {result["type_hint_lines"]} ({result["type_hint_percentage"]:.1f}%)')
                print(f'  🧠 Сложные алгоритмы: {result["complex_algorithm_lines"]} ({result["algorithm_percentage"]:.1f}%)')
                print(f'  🏗️  Классы: {result["classes"]}')
                print(f'  ⚙️  Функции: {result["functions"]}')
                print(f'  🔧 Методы: {result["methods"]}')
                print(f'  📦 Импорты: {result["imports"]}')
                print(f'  🎯 ИТОГОВЫЙ БАЛЛ: {result["final_score"]:.1f}%')
                print(f'  🏆 КАЧЕСТВО: {result["quality_grade"]}')
        else:
            print(f'❌ Файл не найден: {manager_file}')
    
    if valid_results > 0:
        avg_score = total_score / valid_results
        print(f'\n📊 ИТОГОВАЯ СТАТИСТИКА:')
        print('=' * 50)
        print(f'🎯 Средний балл: {avg_score:.1f}%')
        print(f'📈 Общий балл: {total_score:.1f}%')
        print(f'🔢 Менеджеров: {valid_results}/{len(managers)}')
        
        a_plus_count = len([r for r in results if r.get('quality_grade') == 'A+'])
        a_count = len([r for r in results if r.get('quality_grade') == 'A'])
        b_count = len([r for r in results if r.get('quality_grade') == 'B'])
        c_count = len([r for r in results if r.get('quality_grade') == 'C'])
        
        print(f'\n🏆 РАСПРЕДЕЛЕНИЕ ПО КАЧЕСТВУ:')
        if a_plus_count > 0:
            print(f'  🏆 A+ качество: {a_plus_count} менеджеров')
        if a_count > 0:
            print(f'  🥇 A качество: {a_count} менеджеров')
        if b_count > 0:
            print(f'  🥉 B качество: {b_count} менеджеров')
        if c_count > 0:
            print(f'  ⚠️  C качество: {c_count} менеджеров')
        
        if avg_score >= 80:
            print(f'\n🏆 ОБЩЕЕ КАЧЕСТВО: A+')
            print(f'💬 ОТЛИЧНОЕ КАЧЕСТВО!')
        elif avg_score >= 70:
            print(f'\n🥇 ОБЩЕЕ КАЧЕСТВО: A')
            print(f'💬 ХОРОШЕЕ КАЧЕСТВО!')
        elif avg_score >= 60:
            print(f'\n🥉 ОБЩЕЕ КАЧЕСТВО: B')
            print(f'💬 УДОВЛЕТВОРИТЕЛЬНОЕ КАЧЕСТВО!')
        else:
            print(f'\n⚠️  ОБЩЕЕ КАЧЕСТВО: C')
            print(f'💬 ТРЕБУЕТ УЛУЧШЕНИЯ!')
        
        print(f'\n🎉 ПРОВЕРКА ЗАВЕРШЕНА!')
        print(f'📊 Результат: {avg_score:.1f}%')
    
    return valid_results > 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
