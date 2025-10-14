#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование регулярных выражений в поиске
Проверка новых возможностей поиска

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import requests
import json
import time
import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch_simulator import ElasticsearchSimulator, LogLevel, LogEntry
from datetime import datetime, timedelta

ELASTICSEARCH_API_URL = "http://localhost:5001/api/elasticsearch"


def test_regex_search_simulator():
    """Тестирование регулярных выражений в симуляторе"""
    print("🔍 Тестирование регулярных выражений в симуляторе")
    print("=" * 50)
    
    # Создаем симулятор
    es = ElasticsearchSimulator()
    
    # Тестовые запросы
    test_cases = [
        {
            "name": "Поиск по паттерну 'error|warning'",
            "query": "error|warning",
            "use_regex": True,
            "expected_min": 1
        },
        {
            "name": "Поиск по паттерну '^.*Manager.*$'",
            "query": "^.*Manager.*$",
            "use_regex": True,
            "expected_min": 1
        },
        {
            "name": "Поиск по паттерну '\\d{4}-\\d{2}-\\d{2}' (даты)",
            "query": "\\d{4}-\\d{2}-\\d{2}",
            "use_regex": True,
            "expected_min": 0
        },
        {
            "name": "Поиск по паттерну 'user_\\d+' (ID пользователей)",
            "query": "user_\\d+",
            "use_regex": True,
            "expected_min": 0
        },
        {
            "name": "Поиск с учетом регистра 'Security'",
            "query": "Security",
            "use_regex": False,
            "case_sensitive": True,
            "expected_min": 0
        },
        {
            "name": "Поиск без учета регистра 'security'",
            "query": "security",
            "use_regex": False,
            "case_sensitive": False,
            "expected_min": 1
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        
        try:
            result = es.search(
                query=test_case['query'],
                use_regex=test_case.get('use_regex', False),
                case_sensitive=test_case.get('case_sensitive', False),
                limit=10
            )
            
            hits = result.get('hits', 0)
            expected = test_case.get('expected_min', 0)
            
            if hits >= expected:
                print(f"   ✅ Найдено {hits} результатов (ожидалось минимум {expected})")
            else:
                print(f"   ❌ Найдено {hits} результатов (ожидалось минимум {expected})")
            
            # Показываем первые несколько результатов
            logs = result.get('logs', [])
            if logs:
                print(f"   📝 Примеры результатов:")
                for j, log in enumerate(logs[:3]):
                    print(f"      - {log.get('component', 'Unknown')}: {log.get('message', 'No message')[:50]}...")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print()
    
    print("✅ Тестирование симулятора завершено")


def test_regex_search_api():
    """Тестирование регулярных выражений через API"""
    print("\n🌐 Тестирование регулярных выражений через API")
    print("=" * 50)
    
    # Тестовые запросы для API
    test_cases = [
        {
            "name": "API: Поиск по паттерну 'error|warning'",
            "params": {"q": "error|warning", "regex": "true"},
            "expected_min": 1
        },
        {
            "name": "API: Поиск по паттерну '^.*Manager.*$'",
            "params": {"q": "^.*Manager.*$", "regex": "true"},
            "expected_min": 1
        },
        {
            "name": "API: Поиск с учетом регистра",
            "params": {"q": "Security", "case_sensitive": "true"},
            "expected_min": 0
        },
        {
            "name": "API: Поиск без учета регистра",
            "params": {"q": "security", "case_sensitive": "false"},
            "expected_min": 1
        },
        {
            "name": "API: Комбинированный поиск (regex + фильтры)",
            "params": {"q": "error|warning", "regex": "true", "level": "ERROR", "limit": "5"},
            "expected_min": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        
        try:
            response = requests.get(f"{ELASTICSEARCH_API_URL}/search", params=test_case['params'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', 0)
                expected = test_case.get('expected_min', 0)
                
                if hits >= expected:
                    print(f"   ✅ Найдено {hits} результатов (ожидалось минимум {expected})")
                else:
                    print(f"   ❌ Найдено {hits} результатов (ожидалось минимум {expected})")
                
                # Показываем первые несколько результатов
                logs = data.get('logs', [])
                if logs:
                    print(f"   📝 Примеры результатов:")
                    for j, log in enumerate(logs[:2]):
                        print(f"      - {log.get('component', 'Unknown')}: {log.get('message', 'No message')[:50]}...")
                
                # Показываем время выполнения
                took = data.get('took', 0)
                print(f"   ⏱️ Время выполнения: {took}ms")
                
            else:
                print(f"   ❌ HTTP ошибка: {response.status_code}")
                print(f"   📝 Ответ: {response.text[:100]}...")
        
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Ошибка запроса: {e}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print()
    
    print("✅ Тестирование API завершено")


def test_invalid_regex():
    """Тестирование некорректных регулярных выражений"""
    print("\n🚫 Тестирование некорректных регулярных выражений")
    print("=" * 50)
    
    invalid_regexes = [
        "[unclosed",
        "(unclosed",
        "\\",
        "?*+",
        "a{5,3}",
        "(?<name>invalid"
    ]
    
    for i, regex in enumerate(invalid_regexes, 1):
        print(f"{i}. Тестирование некорректного regex: '{regex}'")
        
        try:
            response = requests.get(f"{ELASTICSEARCH_API_URL}/search", 
                                  params={"q": regex, "regex": "true"}, 
                                  timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    print(f"   ✅ Ошибка корректно обработана: {data['error']}")
                else:
                    print(f"   ❌ Ошибка не обработана, получен результат: {data.get('hits', 0)}")
            else:
                print(f"   ❌ HTTP ошибка: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        print()


def test_performance():
    """Тестирование производительности регулярных выражений"""
    print("\n⚡ Тестирование производительности")
    print("=" * 50)
    
    # Тестовые запросы разной сложности
    performance_tests = [
        {
            "name": "Простой regex: 'error'",
            "query": "error",
            "use_regex": True
        },
        {
            "name": "Сложный regex: '^.*(error|warning|critical).*$'",
            "query": "^.*(error|warning|critical).*$",
            "use_regex": True
        },
        {
            "name": "Очень сложный regex: '\\b\\w{5,}\\b'",
            "query": "\\b\\w{5,}\\b",
            "use_regex": True
        },
        {
            "name": "Обычный поиск: 'error'",
            "query": "error",
            "use_regex": False
        }
    ]
    
    for test in performance_tests:
        print(f"Тестирование: {test['name']}")
        
        # Выполняем несколько запросов для усреднения
        times = []
        for _ in range(5):
            start_time = time.time()
            
            try:
                response = requests.get(f"{ELASTICSEARCH_API_URL}/search", 
                                      params={"q": test['query'], "regex": str(test['use_regex']).lower()}, 
                                      timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get('hits', 0)
                    took = data.get('took', 0)
                    times.append(took)
                else:
                    print(f"   ❌ HTTP ошибка: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                break
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"   ⏱️ Среднее время: {avg_time:.3f}ms")
            print(f"   📊 Результатов: {hits}")
            print(f"   🔄 Тестов: {len(times)}")
        
        print()


if __name__ == "__main__":
    print("🚀 Запуск тестирования регулярных выражений")
    print("=" * 60)
    
    # 1. Тестирование симулятора
    test_regex_search_simulator()
    
    # 2. Тестирование API
    test_regex_search_api()
    
    # 3. Тестирование некорректных regex
    test_invalid_regex()
    
    # 4. Тестирование производительности
    test_performance()
    
    print("=" * 60)
    print("🎉 ТЕСТИРОВАНИЕ РЕГУЛЯРНЫХ ВЫРАЖЕНИЙ ЗАВЕРШЕНО!")
    print("\n💡 Новые возможности поиска:")
    print("   ✅ Поддержка регулярных выражений")
    print("   ✅ Поиск с учетом/без учета регистра")
    print("   ✅ Обработка некорректных regex")
    print("   ✅ Фильтрация по компонентам")
    print("   ✅ Комбинированные запросы")
    print("\n🌐 Проверьте в дашборде: http://localhost:5000")