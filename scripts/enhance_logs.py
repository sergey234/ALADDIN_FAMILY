#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшение системы логов
Добавление больше примеров логов для демонстрации

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import sys
import os
import time
import requests
from datetime import datetime, timedelta
from typing import List

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch_simulator import LogLevel, LogEntry


def create_enhanced_logs() -> List[LogEntry]:
    """Создание расширенного набора логов"""
    
    logs = []
    base_time = datetime.now()
    
    # Системные логи
    system_logs = [
        ("SystemManager", "INFO", "Система ALADDIN запущена успешно"),
        ("SystemManager", "INFO", "Инициализация всех компонентов завершена"),
        ("SystemManager", "INFO", "Проверка целостности системы пройдена"),
        ("SystemManager", "WARNING", "Высокая нагрузка на систему"),
        ("SystemManager", "INFO", "Автоматическое обновление завершено"),
        ("SystemManager", "ERROR", "Ошибка подключения к внешнему API"),
        ("SystemManager", "INFO", "Система переведена в режим обслуживания"),
        ("SystemManager", "INFO", "Восстановление после сбоя завершено"),
    ]
    
    # Логи безопасности
    security_logs = [
        ("SecurityManager", "INFO", "Система безопасности активирована"),
        ("SecurityManager", "WARNING", "Обнаружена подозрительная активность"),
        ("SecurityManager", "CRITICAL", "Попытка несанкционированного доступа"),
        ("SecurityManager", "INFO", "Пользователь успешно авторизован"),
        ("SecurityManager", "WARNING", "Множественные неудачные попытки входа"),
        ("SecurityManager", "INFO", "Сессия пользователя завершена"),
        ("SecurityManager", "CRITICAL", "Обнаружена атака типа DDoS"),
        ("SecurityManager", "INFO", "Угроза успешно заблокирована"),
        ("ThreatDetectionAgent", "INFO", "Сканирование на вирусы завершено"),
        ("ThreatDetectionAgent", "WARNING", "Обнаружен подозрительный файл"),
        ("ThreatDetectionAgent", "CRITICAL", "Обнаружен троянский конь"),
        ("ThreatDetectionAgent", "INFO", "Файл помещен в карантин"),
    ]
    
    # Логи производительности
    performance_logs = [
        ("PerformanceMonitor", "INFO", "CPU загрузка: 45%"),
        ("PerformanceMonitor", "WARNING", "CPU загрузка: 85%"),
        ("PerformanceMonitor", "INFO", "Память использована: 2.1 GB"),
        ("PerformanceMonitor", "WARNING", "Память использована: 7.8 GB"),
        ("PerformanceMonitor", "INFO", "Диск заполнен на 60%"),
        ("PerformanceMonitor", "WARNING", "Диск заполнен на 90%"),
        ("PerformanceMonitor", "INFO", "Сетевая активность: 1.2 MB/s"),
        ("PerformanceMonitor", "WARNING", "Высокая сетевая активность: 15.3 MB/s"),
    ]
    
    # Семейные логи
    family_logs = [
        ("FamilyManager", "INFO", "Создан профиль ребенка: Анна, 8 лет"),
        ("FamilyManager", "INFO", "Установлены ограничения времени для ребенка"),
        ("FamilyManager", "WARNING", "Ребенок пытается зайти на запрещенный сайт"),
        ("FamilyManager", "INFO", "Родительский контроль активирован"),
        ("FamilyManager", "INFO", "Отправлено уведомление родителям"),
        ("FamilyManager", "INFO", "Создан профиль пожилого: Иван, 72 года"),
        ("FamilyManager", "INFO", "Активирована защита от мошенничества"),
        ("FamilyManager", "WARNING", "Подозрительный звонок заблокирован"),
    ]
    
    # Логи базы данных
    database_logs = [
        ("DatabaseManager", "INFO", "Подключение к базе данных установлено"),
        ("DatabaseManager", "INFO", "Резервное копирование запущено"),
        ("DatabaseManager", "INFO", "Резервное копирование завершено успешно"),
        ("DatabaseManager", "ERROR", "Ошибка записи в базу данных"),
        ("DatabaseManager", "WARNING", "Медленный запрос к базе данных"),
        ("DatabaseManager", "INFO", "Индексы базы данных обновлены"),
        ("DatabaseManager", "INFO", "Очистка старых записей завершена"),
    ]
    
    # Логи API
    api_logs = [
        ("APIGateway", "INFO", "Получен запрос к API безопасности"),
        ("APIGateway", "INFO", "Запрос обработан за 45ms"),
        ("APIGateway", "WARNING", "Превышен лимит запросов от IP"),
        ("APIGateway", "ERROR", "Ошибка валидации запроса"),
        ("APIGateway", "INFO", "API ответ отправлен клиенту"),
        ("APIGateway", "WARNING", "Медленный ответ API: 2.3s"),
    ]
    
    # Объединяем все логи
    all_logs = system_logs + security_logs + performance_logs + family_logs + database_logs + api_logs
    
    # Создаем объекты LogEntry
    for i, (component, level, message) in enumerate(all_logs):
        log_time = base_time - timedelta(minutes=i*2, seconds=i*30)
        
        # Создаем метаданные в зависимости от типа лога
        metadata = {
            "log_id": f"enhanced_log_{i+1:03d}",
            "source": "enhancement_script",
            "timestamp": log_time.isoformat()
        }
        
        # Добавляем специфичные метаданные
        if "CPU" in message:
            metadata["cpu_usage"] = 45 + (i % 50)
        elif "Память" in message:
            metadata["memory_usage"] = 2.1 + (i % 5)
        elif "Диск" in message:
            metadata["disk_usage"] = 60 + (i % 30)
        elif "сеть" in message.lower():
            metadata["network_speed"] = 1.2 + (i % 10)
        elif "пользователь" in message.lower():
            metadata["user_id"] = f"user_{i % 100:03d}"
        elif "ребенок" in message.lower():
            metadata["child_id"] = f"child_{i % 10:02d}"
            metadata["age"] = 8 + (i % 10)
        
        log_entry = LogEntry(
            timestamp=log_time,
            level=LogLevel(level),
            component=component,
            message=message,
            metadata=metadata,
            log_id=metadata["log_id"]
        )
        
        logs.append(log_entry)
    
    return logs


def add_logs_to_elasticsearch(logs: List[LogEntry]):
    """Добавление логов в Elasticsearch через API"""
    
    base_url = "http://localhost:5001/api/elasticsearch"
    
    print(f"📝 Добавление {len(logs)} логов в Elasticsearch...")
    
    success_count = 0
    error_count = 0
    
    for i, log in enumerate(logs):
        try:
            # Преобразуем в формат API
            log_data = {
                "timestamp": log.timestamp.isoformat(),
                "level": log.level.value,
                "component": log.component,
                "message": log.message,
                "metadata": log.metadata,
                "log_id": log.log_id
            }
            
            # Отправляем через API
            response = requests.post(f"{base_url}/index", json=log_data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    success_count += 1
                    if (i + 1) % 10 == 0:
                        print(f"   ✅ Добавлено {i + 1}/{len(logs)} логов")
                else:
                    error_count += 1
                    print(f"   ❌ Ошибка добавления лога {i + 1}: {result.get('error')}")
            else:
                error_count += 1
                print(f"   ❌ HTTP ошибка {response.status_code} для лога {i + 1}")
            
            # Небольшая задержка между запросами
            time.sleep(0.1)
            
        except Exception as e:
            error_count += 1
            print(f"   ❌ Исключение для лога {i + 1}: {e}")
    
    print(f"\n📊 Результат добавления логов:")
    print(f"   ✅ Успешно: {success_count}")
    print(f"   ❌ Ошибок: {error_count}")
    print(f"   📝 Всего: {len(logs)}")
    
    return success_count, error_count


def test_enhanced_search():
    """Тестирование улучшенного поиска"""
    
    base_url = "http://localhost:5001/api/elasticsearch"
    
    print("\n🔍 Тестирование улучшенного поиска...")
    
    # Тестовые запросы
    test_queries = [
        ("security", "Поиск по безопасности"),
        ("error", "Поиск ошибок"),
        ("warning", "Поиск предупреждений"),
        ("child", "Поиск по детям"),
        ("performance", "Поиск по производительности"),
        ("database", "Поиск по базе данных"),
        ("api", "Поиск по API"),
        ("", "Все логи")
    ]
    
    for query, description in test_queries:
        try:
            response = requests.get(f"{base_url}/search?q={query}&limit=5", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   {description}: {data['hits']} результатов")
            else:
                print(f"   ❌ Ошибка поиска '{query}': {response.status_code}")
        except Exception as e:
            print(f"   ❌ Исключение поиска '{query}': {e}")


def get_elasticsearch_stats():
    """Получение статистики Elasticsearch"""
    
    base_url = "http://localhost:5001/api/elasticsearch"
    
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Статистика Elasticsearch:")
            print(f"   📝 Всего логов: {stats['total_logs']}")
            print(f"   📁 Индексов: {len(stats['indices'])}")
            print(f"   🔍 Поисковых запросов: {stats['search_queries']}")
            print(f"   📈 Распределение по уровням:")
            for level, count in stats['level_distribution'].items():
                print(f"      - {level}: {count}")
        else:
            print(f"❌ Ошибка получения статистики: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")


if __name__ == "__main__":
    print("🚀 Улучшение системы логов ALADDIN")
    print("=" * 50)
    
    # 1. Создание расширенных логов
    print("1. Создание расширенного набора логов...")
    enhanced_logs = create_enhanced_logs()
    print(f"   ✅ Создано {len(enhanced_logs)} логов")
    
    # 2. Добавление в Elasticsearch
    print("\n2. Добавление логов в Elasticsearch...")
    success, errors = add_logs_to_elasticsearch(enhanced_logs)
    
    # 3. Тестирование поиска
    test_enhanced_search()
    
    # 4. Статистика
    get_elasticsearch_stats()
    
    print("\n" + "=" * 50)
    if success > 0:
        print("🎉 УЛУЧШЕНИЕ ЛОГОВ ЗАВЕРШЕНО УСПЕШНО!")
        print(f"📝 Добавлено {success} новых логов")
        print("\n💡 Теперь в системе больше данных для демонстрации:")
        print("   - Различные типы логов (система, безопасность, семья)")
        print("   - Разные уровни серьезности (INFO, WARNING, ERROR, CRITICAL)")
        print("   - Богатые метаданные для поиска")
        print("   - Временные метки для анализа трендов")
        print("\n🌐 Проверьте улучшения в дашборде: http://localhost:5000")
    else:
        print("❌ УЛУЧШЕНИЕ ЛОГОВ НЕ УДАЛОСЬ!")
        print("   Проверьте, что Elasticsearch API запущен на порту 5001")