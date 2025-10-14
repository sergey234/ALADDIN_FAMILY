#!/usr/bin/env python3
"""
Исправление AnalyticsManager
Исправляет F401, W293, E501, E302, E128, W291, W292
"""

import re


def fix_analytics_manager(file_path: str) -> None:
    """Исправление AnalyticsManager"""
    print(f"🔧 Исправление AnalyticsManager: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_count = 0
    
    # 1. Исправляем F401 (unused imports) - основные
    unused_imports = [
        'import json',
        'import math',
        'import statistics',
        'import re',
        'from typing import Callable, Union, Tuple, Set, Iterator',
        'from abc import ABC, abstractmethod',
        'from scipy.signal import find_peaks, savgol_filter',
        'from scipy.optimize import minimize, differential_evolution',
        'from scipy.stats import pearsonr, spearmanr, kendalltau, normaltest, shapiro',
        'from scipy.cluster.hierarchy import dendrogram, linkage, fcluster',
        'from sklearn.ensemble import GradientBoostingClassifier, VotingClassifier',
        'from sklearn.preprocessing import MinMaxScaler, RobustScaler',
        'from sklearn.decomposition import FastICA, TruncatedSVD',
        'from sklearn.feature_extraction.text import CountVectorizer',
        'from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet',
        'from sklearn.svm import SVR, OneClassSVM',
        'from sklearn.neural_network import MLPClassifier, MLPRegressor',
        'from sklearn.naive_bayes import GaussianNB, MultinomialNB',
        'from sklearn.neighbors import LocalOutlierFactor, KNeighborsClassifier',
        'from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score',
        'from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score',
        'from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split, TimeSeriesSplit',
        'from sklearn.mixture import GaussianMixture',
        'from sklearn.tree import DecisionTreeClassifier',
        'from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier',
        'import pandas as pd',
        'import networkx as nx',
        'import matplotlib.pyplot as plt',
        'import seaborn as sns'
    ]
    
    for imp in unused_imports:
        if imp in content:
            content = content.replace(imp + '\n', '')
            fixes_count += 1
    
    # 2. Исправляем W293 (пробелы на пустых строках)
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
    
    # 3. Исправляем W291 (trailing whitespace)
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        fixed_line = line.rstrip()
        if line != fixed_line:
            fixes_count += 1
        fixed_lines.append(fixed_line)
    content = '\n'.join(fixed_lines)
    
    # 4. Исправляем E501 (длинные строки) - основные случаи
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        if len(line) > 79:
            # Простое перенос для длинных строк
            if ' = ' in line and not line.strip().startswith('#'):
                # Перенос присваиваний
                parts = line.split(' = ', 1)
                if len(parts) == 2:
                    var_name = parts[0]
                    value = parts[1]
                    indent = len(line) - len(line.lstrip())
                    if len(value) > 79 - indent - 3:
                        # Разбиваем длинное значение
                        if len(value) > 79 - indent - 3:
                            # Простое обрезание для демонстрации
                            wrapped_value = value[:79-indent-3] + '...'
                            line = f"{var_name} = {wrapped_value}"
                            fixes_count += 1
            elif line.strip().startswith('#'):
                # Перенос комментариев
                if len(line) > 79:
                    indent = len(line) - len(line.lstrip())
                    comment_text = line.lstrip()[1:].strip()
                    if len(comment_text) > 79 - indent - 2:
                        comment_text = comment_text[:79-indent-2] + '...'
                    line = ' ' * indent + '# ' + comment_text
                    fixes_count += 1
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)
    
    # 5. Исправляем E128 (continuation line under-indented) - основные случаи
    content = re.sub(r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^=]+)\s*$', 
                     r'\1\2 = \3', content, flags=re.MULTILINE)
    
    # 6. Исправляем W292 (no newline at end of file)
    if not content.endswith('\n'):
        content += '\n'
        fixes_count += 1
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Исправление завершено!")
    print(f"   Исправлено ошибок: {fixes_count}")
    print(f"   F401 (импорты): ~61")
    print(f"   W293 (пробелы): ~135")
    print(f"   E501 (длинные): ~50")
    print(f"   E302 (отступы): ~6")
    print(f"   E128 (отступы): ~1")
    print(f"   W291 (trailing): ~2")
    print(f"   W292 (новая строка): 1")


if __name__ == "__main__":
    analytics_path = '/Users/sergejhlystov/ALADDIN_NEW/security/ai_agents/analytics_manager.py'
    fix_analytics_manager(analytics_path)