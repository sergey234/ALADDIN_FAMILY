#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование системы экспорта
Проверка экспорта в различные форматы

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export_manager import ExportManager
from elasticsearch_simulator import ElasticsearchSimulator, LogLevel, LogEntry

EXPORT_API_URL = "http://localhost:5002/api/export"


def test_export_manager():
    """Тестирование ExportManager"""
    print("📤 Тестирование Export Manager")
    print("=" * 40)
    
    # Создаем менеджер экспорта
    export_manager = ExportManager()
    
    # Создаем тестовые логи
    test_logs = [
        LogEntry(
            timestamp=datetime.now() - timedelta(minutes=5),
            level=LogLevel.INFO,
            component="TestComponent",
            message="Тестовое сообщение для экспорта",
            metadata={"test": True, "value": 123, "category": "test"},
            log_id="test_001"
        ),
        LogEntry(
            timestamp=datetime.now() - timedelta(minutes=3),
            level=LogLevel.WARNING,
            component="AnotherComponent",
            message="Предупреждение о тестировании",
            metadata={"warning_type": "test", "severity": "medium", "user_id": "user_123"},
            log_id="test_002"
        ),
        LogEntry(
            timestamp=datetime.now() - timedelta(minutes=1),
            level=LogLevel.ERROR,
            component="ErrorComponent",
            message="Ошибка при тестировании экспорта",
            metadata={"error_code": "EXP_001", "retry_count": 3, "timestamp": "2025-09-08"},
            log_id="test_003"
        )
    ]
    
    try:
        print("1. Тестирование экспорта CSV...")
        csv_file = export_manager.export_logs_csv(test_logs)
        print(f"   ✅ CSV файл создан: {os.path.basename(csv_file)}")
        
        print("2. Тестирование экспорта JSON...")
        json_file = export_manager.export_logs_json(test_logs)
        print(f"   ✅ JSON файл создан: {os.path.basename(json_file)}")
        
        print("3. Тестирование экспорта PDF...")
        try:
            pdf_file = export_manager.export_logs_pdf(test_logs)
            print(f"   ✅ PDF файл создан: {os.path.basename(pdf_file)}")
        except ImportError:
            print("   ⚠️ PDF экспорт пропущен (ReportLab не установлен)")
        
        print("4. Тестирование экспорта статистики...")
        stats = {
            "total_logs": len(test_logs),
            "level_distribution": {"INFO": 1, "WARNING": 1, "ERROR": 1},
            "component_distribution": {"TestComponent": 1, "AnotherComponent": 1, "ErrorComponent": 1},
            "export_timestamp": datetime.now().isoformat()
        }
        stats_file = export_manager.export_system_stats(stats)
        print(f"   ✅ Статистика экспортирована: {os.path.basename(stats_file)}")
        
        print("5. Список экспортированных файлов:")
        files = export_manager.get_export_list()
        for file_info in files:
            size_kb = file_info['size'] / 1024
            print(f"   📄 {file_info['filename']} ({size_kb:.1f} KB)")
        
        print("\n✅ Тестирование Export Manager завершено успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Export Manager: {e}")


def test_export_api():
    """Тестирование Export API"""
    print("\n🌐 Тестирование Export API")
    print("=" * 40)
    
    # Проверка здоровья API
    try:
        response = requests.get(f"{EXPORT_API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"1. ✅ API здоров: {data['status']}")
            print(f"   📊 Поддерживаемые форматы: {', '.join(data['formats'])}")
        else:
            print(f"1. ❌ API недоступен: {response.status_code}")
            return
    except Exception as e:
        print(f"1. ❌ Ошибка подключения к API: {e}")
        return
    
    # Тестирование экспорта CSV
    print("\n2. Тестирование экспорта CSV...")
    try:
        params = {
            'q': 'test',
            'limit': '10'
        }
        response = requests.get(f"{EXPORT_API_URL}/logs/csv", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ CSV экспорт успешен: {data['filename']}")
                print(f"   📊 Логов экспортировано: {data['total_logs']}")
                print(f"   🔗 URL скачивания: {data['download_url']}")
            else:
                print(f"   ❌ Ошибка экспорта: {data.get('error')}")
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка экспорта CSV: {e}")
    
    # Тестирование экспорта JSON
    print("\n3. Тестирование экспорта JSON...")
    try:
        params = {
            'q': 'error',
            'level': 'ERROR',
            'limit': '5'
        }
        response = requests.get(f"{EXPORT_API_URL}/logs/json", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ JSON экспорт успешен: {data['filename']}")
                print(f"   📊 Логов экспортировано: {data['total_logs']}")
            else:
                print(f"   ❌ Ошибка экспорта: {data.get('error')}")
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка экспорта JSON: {e}")
    
    # Тестирование экспорта PDF
    print("\n4. Тестирование экспорта PDF...")
    try:
        params = {
            'q': 'security',
            'limit': '5'
        }
        response = requests.get(f"{EXPORT_API_URL}/logs/pdf", params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ PDF экспорт успешен: {data['filename']}")
                print(f"   📊 Логов экспортировано: {data['total_logs']}")
            else:
                print(f"   ❌ Ошибка экспорта: {data.get('error')}")
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка экспорта PDF: {e}")
    
    # Тестирование экспорта статистики
    print("\n5. Тестирование экспорта статистики...")
    try:
        response = requests.get(f"{EXPORT_API_URL}/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Статистика экспортирована: {data['filename']}")
            else:
                print(f"   ❌ Ошибка экспорта: {data.get('error')}")
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка экспорта статистики: {e}")
    
    # Тестирование списка файлов
    print("\n6. Тестирование списка файлов...")
    try:
        response = requests.get(f"{EXPORT_API_URL}/files", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                files = data.get('files', [])
                print(f"   ✅ Найдено файлов: {len(files)}")
                for file_info in files[:3]:  # Показываем первые 3
                    size_kb = file_info['size'] / 1024
                    print(f"      📄 {file_info['filename']} ({size_kb:.1f} KB)")
                if len(files) > 3:
                    print(f"      ... и еще {len(files) - 3} файлов")
            else:
                print(f"   ❌ Ошибка получения списка: {data.get('error')}")
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка получения списка файлов: {e}")


def test_export_performance():
    """Тестирование производительности экспорта"""
    print("\n⚡ Тестирование производительности экспорта")
    print("=" * 50)
    
    # Тестируем разные размеры данных
    test_sizes = [10, 50, 100, 500]
    
    for size in test_sizes:
        print(f"\nТестирование экспорта {size} логов:")
        
        # CSV экспорт
        start_time = time.time()
        try:
            params = {'limit': str(size)}
            response = requests.get(f"{EXPORT_API_URL}/logs/csv", params=params, timeout=30)
            csv_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   📊 CSV: {csv_time:.2f}s ({data['total_logs']} логов)")
                else:
                    print(f"   ❌ CSV: Ошибка - {data.get('error')}")
            else:
                print(f"   ❌ CSV: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ CSV: Исключение - {e}")
        
        # JSON экспорт
        start_time = time.time()
        try:
            params = {'limit': str(size)}
            response = requests.get(f"{EXPORT_API_URL}/logs/json", params=params, timeout=30)
            json_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   📄 JSON: {json_time:.2f}s ({data['total_logs']} логов)")
                else:
                    print(f"   ❌ JSON: Ошибка - {data.get('error')}")
            else:
                print(f"   ❌ JSON: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ JSON: Исключение - {e}")


if __name__ == "__main__":
    print("🚀 Запуск тестирования системы экспорта")
    print("=" * 60)
    
    # 1. Тестирование ExportManager
    test_export_manager()
    
    # 2. Тестирование Export API
    test_export_api()
    
    # 3. Тестирование производительности
    test_export_performance()
    
    print("\n" + "=" * 60)
    print("🎉 ТЕСТИРОВАНИЕ СИСТЕМЫ ЭКСПОРТА ЗАВЕРШЕНО!")
    print("\n💡 Новые возможности экспорта:")
    print("   ✅ Экспорт в CSV формат (для Excel)")
    print("   ✅ Экспорт в JSON формат (структурированный)")
    print("   ✅ Экспорт в PDF формат (для печати)")
    print("   ✅ Экспорт статистики системы")
    print("   ✅ Фильтрация данных перед экспортом")
    print("   ✅ Управление экспортированными файлами")
    print("   ✅ API для интеграции с другими системами")
    print("\n🌐 Проверьте интерфейс экспорта: http://localhost:5002")
    print("📊 Или используйте API: http://localhost:5002/api/export/health")