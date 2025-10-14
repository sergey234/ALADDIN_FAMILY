#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Services Validator - Валидатор реестра веб-сервисов
Проверяет структуру и корректность регистрации веб-сервисов
"""

import json
import os
import sys
from datetime import datetime

def validate_web_services_registry():
    """Валидация реестра веб-сервисов"""
    try:
        print("🔍 ВАЛИДАЦИЯ РЕЕСТРА ВЕБ-СЕРВИСОВ")
        print("=" * 50)
        
        # Загружаем файл
        registry_path = 'data/web_services_registry.json'
        if not os.path.exists(registry_path):
            print(f"❌ Файл {registry_path} не найден!")
            return False
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем структуру
        if 'web_services' not in data:
            print("❌ Блок web_services не найден!")
            return False
        
        if 'registry_info' not in data:
            print("❌ Блок registry_info не найден!")
            return False
        
        # Проверяем каждый сервис
        services = data['web_services']
        total_services = len(services)
        valid_services = 0
        
        print(f"📊 Найдено сервисов: {total_services}")
        
        for service_id, service_data in services.items():
            print(f"\n🔧 Проверка сервиса: {service_id}")
            
            # Обязательные поля
            required_fields = [
                'service_id', 'name', 'description', 'service_type',
                'port', 'status', 'version', 'features', 'endpoints',
                'dependencies', 'created_at', 'last_updated'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in service_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Отсутствуют поля: {missing_fields}")
                continue
            
            # Проверяем типы данных
            if not isinstance(service_data['port'], int):
                print(f"❌ Порт должен быть числом: {service_data['port']}")
                continue
            
            if not isinstance(service_data['features'], list):
                print(f"❌ Features должен быть списком")
                continue
            
            if not isinstance(service_data['endpoints'], list):
                print(f"❌ Endpoints должен быть списком")
                continue
            
            # Проверяем уникальность порта
            port = service_data['port']
            other_services = [s for sid, s in services.items() if sid != service_id]
            if any(s.get('port') == port for s in other_services):
                print(f"❌ Порт {port} уже используется другим сервисом")
                continue
            
            print(f"✅ Сервис {service_id} корректен")
            valid_services += 1
        
        # Проверяем registry_info
        registry_info = data['registry_info']
        if registry_info.get('total_services') != total_services:
            print(f"❌ Несоответствие количества сервисов: {registry_info.get('total_services')} != {total_services}")
            return False
        
        print(f"\n📈 РЕЗУЛЬТАТЫ ВАЛИДАЦИИ:")
        print(f"✅ Валидных сервисов: {valid_services}/{total_services}")
        print(f"📊 Процент корректности: {(valid_services/total_services)*100:.1f}%")
        
        # Проверяем категории
        categories = data.get('registry_info', {}).get('categories', {})
        if categories:
            print(f"\n📋 КАТЕГОРИИ СЕРВИСОВ:")
            for category, count in categories.items():
                print(f"  {category}: {count} сервисов")
        
        # Проверяем порты
        ports_used = data.get('registry_info', {}).get('ports_used', [])
        if ports_used:
            print(f"\n🔌 ИСПОЛЬЗУЕМЫЕ ПОРТЫ: {len(ports_used)}")
            print(f"  Порт 5000-5012: {len([p for p in ports_used if 5000 <= p <= 5012])}")
            print(f"  Порт 8006-8012: {len([p for p in ports_used if 8006 <= p <= 8012])}")
            print(f"  Порт 8080-8081: {len([p for p in ports_used if 8080 <= p <= 8081])}")
        
        if valid_services == total_services:
            print("🎉 ВСЕ СЕРВИСЫ КОРРЕКТНЫ!")
            return True
        else:
            print("⚠️  НЕКОТОРЫЕ СЕРВИСЫ ТРЕБУЮТ ИСПРАВЛЕНИЯ")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        return False

def check_service_status():
    """Проверка статуса веб-сервисов"""
    print("\n🌐 ПРОВЕРКА СТАТУСА ВЕБ-СЕРВИСОВ")
    print("=" * 50)
    
    try:
        import requests
        
        # Загружаем реестр
        with open('data/web_services_registry.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        services = data['web_services']
        
        for service_id, service_data in services.items():
            port = service_data['port']
            name = service_data['name']
            
            try:
                response = requests.get(f"http://localhost:{port}/", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name} (порт {port}): РАБОТАЕТ")
                else:
                    print(f"⚠️  {name} (порт {port}): ОТВЕЧАЕТ, но статус {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"❌ {name} (порт {port}): НЕ ДОСТУПЕН")
                
    except ImportError:
        print("⚠️  requests не установлен, пропускаем проверку статуса")
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")

if __name__ == "__main__":
    print("🛡️ ALADDIN Web Services Validator")
    print("=" * 50)
    
    # Валидация структуры
    structure_valid = validate_web_services_registry()
    
    # Проверка статуса
    check_service_status()
    
    if structure_valid:
        print("\n🎉 ВАЛИДАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        sys.exit(0)
    else:
        print("\n❌ ВАЛИДАЦИЯ ЗАВЕРШЕНА С ОШИБКАМИ!")
        sys.exit(1)