#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест экспорта данных
"""

import csv
import json
import os
from datetime import datetime
from elasticsearch_simulator import ElasticsearchSimulator

def test_export():
    print("🚀 Тестирование экспорта данных...")
    
    # Инициализация
    es_simulator = ElasticsearchSimulator()
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)
    
    # Получаем данные
    results = es_simulator.search(query="security", limit=10)
    print(f"📊 Найдено логов: {len(results.get('logs', []))}")
    
    # Тест CSV экспорта
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_logs_{timestamp}.csv"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Level', 'Component', 'Message', 'Metadata'])
            
            for log in results.get('logs', []):
                writer.writerow([
                    log.get('timestamp', ''),
                    log.get('level', ''),
                    log.get('component', ''),
                    log.get('message', ''),
                    json.dumps(log.get('metadata', {}), ensure_ascii=False)
                ])
        
        print(f"✅ CSV файл создан: {filename}")
        print(f"📁 Путь: {filepath}")
        print(f"📏 Размер: {os.path.getsize(filepath)} байт")
        
    except Exception as e:
        print(f"❌ Ошибка CSV экспорта: {e}")
    
    # Тест JSON экспорта
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_logs_{timestamp}.json"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON файл создан: {filename}")
        print(f"📁 Путь: {filepath}")
        print(f"📏 Размер: {os.path.getsize(filepath)} байт")
        
    except Exception as e:
        print(f"❌ Ошибка JSON экспорта: {e}")
    
    # Список файлов
    print("\n📁 Список экспортированных файлов:")
    if os.path.exists(export_dir):
        for filename in os.listdir(export_dir):
            filepath = os.path.join(export_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                size = stat.st_size
                created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                print(f"  📄 {filename} ({size} байт, {created})")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == '__main__':
    test_export()