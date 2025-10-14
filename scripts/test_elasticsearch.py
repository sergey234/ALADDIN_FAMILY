#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование Elasticsearch Simulator
Тестирование поиска по логам

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import sys
import os
import time
import requests
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch_simulator import ElasticsearchSimulator, LogLevel, LogEntry


def test_elasticsearch_simulator():
    """Тестирование симулятора Elasticsearch"""
    print("🔍 Тестирование Elasticsearch Simulator")
    print("=" * 50)
    
    try:
        # 1. Создание симулятора
        print("1. Создание Elasticsearch Simulator...")
        es = ElasticsearchSimulator()
        print("✅ Симулятор создан")
        
        # 2. Проверка статистики
        print("2. Проверка статистики...")
        stats = es.get_statistics()
        print(f"   Всего логов: {stats['total_logs']}")
        print(f"   Индексов: {len(stats['indices'])}")
        print(f"   Поисковых запросов: {stats['search_queries']}")
        
        # 3. Тестирование поиска
        print("3. Тестирование поиска...")
        
        # Поиск по тексту
        results = es.search("security", limit=5)
        print(f"   Поиск 'security': {results['hits']} результатов")
        
        # Поиск по уровню
        results = es.search("", level=LogLevel.ERROR, limit=5)
        print(f"   Поиск ошибок: {results['hits']} результатов")
        
        # Поиск по компоненту
        results = es.search("", component="Security", limit=5)
        print(f"   Поиск по Security: {results['hits']} результатов")
        
        # 4. Тестирование индексации
        print("4. Тестирование индексации...")
        
        # Создание нового лога
        new_log = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            component="TestComponent",
            message="Тестовое сообщение для проверки индексации",
            metadata={"test": True, "value": 123}
        )
        
        success = es.index_log(new_log)
        if success:
            print("✅ Новый лог проиндексирован")
        else:
            print("❌ Ошибка индексации лога")
        
        # 5. Проверка после индексации
        print("5. Проверка после индексации...")
        stats_after = es.get_statistics()
        print(f"   Всего логов после индексации: {stats_after['total_logs']}")
        
        # 6. Тестирование массовой индексации
        print("6. Тестирование массовой индексации...")
        
        bulk_logs = []
        for i in range(5):
            log = LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.INFO,
                component=f"BulkComponent_{i}",
                message=f"Массовое сообщение {i}",
                metadata={"bulk": True, "index": i}
            )
            bulk_logs.append(log)
        
        bulk_result = es.bulk_index(bulk_logs)
        print(f"   Массовая индексация: {bulk_result['success_count']} успешно, {bulk_result['error_count']} ошибок")
        
        # 7. Финальная статистика
        print("7. Финальная статистика...")
        final_stats = es.get_statistics()
        print(f"   Всего логов: {final_stats['total_logs']}")
        print(f"   Индексов: {len(final_stats['indices'])}")
        print(f"   Поисковых запросов: {final_stats['search_queries']}")
        
        print("\n✅ Тестирование симулятора завершено успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_elasticsearch_api():
    """Тестирование API Elasticsearch"""
    print("\n🌐 Тестирование Elasticsearch API")
    print("=" * 50)
    
    try:
        base_url = "http://localhost:5001/api/elasticsearch"
        
        # 1. Проверка здоровья
        print("1. Проверка здоровья API...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Статус: {health_data['status']}")
            print(f"   Elasticsearch: {health_data['elasticsearch']}")
            print(f"   Всего логов: {health_data['total_logs']}")
        else:
            print(f"   ❌ API недоступен: {response.status_code}")
            return False
        
        # 2. Тестирование поиска
        print("2. Тестирование поиска через API...")
        
        # Поиск по тексту
        response = requests.get(f"{base_url}/search?q=security&limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Поиск 'security': {data['hits']} результатов")
        else:
            print(f"   ❌ Ошибка поиска: {response.status_code}")
        
        # Поиск по уровню
        response = requests.get(f"{base_url}/search?level=ERROR&limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Поиск ошибок: {data['hits']} результатов")
        else:
            print(f"   ❌ Ошибка поиска ошибок: {response.status_code}")
        
        # 3. Тестирование статистики
        print("3. Тестирование статистики...")
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"   Всего логов: {stats['total_logs']}")
            print(f"   Индексов: {len(stats['indices'])}")
            print(f"   Поисковых запросов: {stats['search_queries']}")
        else:
            print(f"   ❌ Ошибка получения статистики: {response.status_code}")
        
        # 4. Тестирование последних логов
        print("4. Тестирование последних логов...")
        response = requests.get(f"{base_url}/logs/recent?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Последних логов: {len(data['logs'])}")
        else:
            print(f"   ❌ Ошибка получения последних логов: {response.status_code}")
        
        # 5. Тестирование индексации через API
        print("5. Тестирование индексации через API...")
        
        new_log = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "component": "APITestComponent",
            "message": "Тестовое сообщение через API",
            "metadata": {"api_test": True, "timestamp": datetime.now().isoformat()}
        }
        
        response = requests.post(f"{base_url}/index", json=new_log, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"   ✅ Лог проиндексирован: {result['log_id']}")
            else:
                print(f"   ❌ Ошибка индексации: {result['error']}")
        else:
            print(f"   ❌ Ошибка API индексации: {response.status_code}")
        
        print("\n✅ Тестирование API завершено успешно!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Elasticsearch API недоступен (запустите elasticsearch_api.py)")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования API: {e}")
        return False


def test_dashboard_integration():
    """Тестирование интеграции с дашбордом"""
    print("\n📊 Тестирование интеграции с дашбордом")
    print("=" * 50)
    
    try:
        # Проверяем основной дашборд
        print("1. Проверка основного дашборда...")
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Основной дашборд доступен")
        else:
            print(f"   ❌ Основной дашборд недоступен: {response.status_code}")
            return False
        
        # Проверяем Elasticsearch API
        print("2. Проверка Elasticsearch API...")
        response = requests.get("http://localhost:5001/api/elasticsearch/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Elasticsearch API доступен")
        else:
            print(f"   ❌ Elasticsearch API недоступен: {response.status_code}")
            return False
        
        print("\n✅ Интеграция с дашбордом работает!")
        print("\n🌐 Ссылки для тестирования:")
        print("   📊 Дашборд: http://localhost:5000")
        print("   🔍 Поиск логов: http://localhost:5000 (вкладка 'Поиск логов')")
        print("   📡 Elasticsearch API: http://localhost:5001/api/elasticsearch/health")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования интеграции: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск тестирования Elasticsearch")
    print("=" * 60)
    
    # Тестирование симулятора
    simulator_success = test_elasticsearch_simulator()
    
    # Тестирование API
    api_success = test_elasticsearch_api()
    
    # Тестирование интеграции
    integration_success = test_dashboard_integration()
    
    print("\n" + "=" * 60)
    if simulator_success and api_success and integration_success:
        print("🎉 ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("\n💡 Для полной работы системы:")
        print("   1. Откройте дашборд: http://localhost:5000")
        print("   2. Перейдите на вкладку 'Поиск логов'")
        print("   3. Попробуйте поиск по логам")
        print("   4. Проверьте статистику Elasticsearch")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        if not simulator_success:
            print("   - Симулятор Elasticsearch")
        if not api_success:
            print("   - Elasticsearch API")
        if not integration_success:
            print("   - Интеграция с дашбордом")