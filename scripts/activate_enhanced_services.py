#!/usr/bin/env python3
"""
🛡️ ALADDIN Enhanced Services Activator
Скрипт для активации Enhanced сервисов из спящего режима
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

def load_web_services_registry():
    """Загружает реестр веб-сервисов"""
    registry_path = Path(__file__).parent.parent / "data" / "web_services_registry.json"
    with open(registry_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_service_status(service_id, status):
    """Обновляет статус сервиса в реестре"""
    registry_path = Path(__file__).parent.parent / "data" / "web_services_registry.json"
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    if service_id in registry['web_services']:
        registry['web_services'][service_id]['status'] = status
        registry['web_services'][service_id]['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%S.000000')
        
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        return True
    return False

def check_port_available(port):
    """Проверяет доступность порта"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def start_enhanced_api_docs():
    """Запускает Enhanced API Docs"""
    print("🚀 Запуск Enhanced API Docs...")
    
    # Проверяем доступность порта
    if not check_port_available(8080):
        print("❌ Порт 8080 занят. Остановите другой сервис или измените порт.")
        return False
    
    # Запускаем сервис в фоне
    try:
        cmd = ["python3", "enhanced_api_docs.py"]
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent.parent
        )
        
        # Обновляем статус в реестре
        update_service_status("enhanced_api_docs", "running")
        
        print("✅ Enhanced API Docs запущен на http://localhost:8080")
        print(f"📋 PID процесса: {process.pid}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка запуска Enhanced API Docs: {e}")
        return False

def start_enhanced_architecture_visualizer():
    """Запускает Enhanced Architecture Visualizer"""
    print("🚀 Запуск Enhanced Architecture Visualizer...")
    
    # Проверяем доступность порта
    if not check_port_available(8081):
        print("❌ Порт 8081 занят. Остановите другой сервис или измените порт.")
        return False
    
    # Запускаем сервис в фоне
    try:
        cmd = ["python3", "enhanced_architecture_visualizer.py"]
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent.parent
        )
        
        # Обновляем статус в реестре
        update_service_status("enhanced_architecture_visualizer", "running")
        
        print("✅ Enhanced Architecture Visualizer запущен на http://localhost:8081")
        print(f"📋 PID процесса: {process.pid}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка запуска Enhanced Architecture Visualizer: {e}")
        return False

def main():
    """Основная функция"""
    print("🛡️ ALADDIN Enhanced Services Activator")
    print("=" * 50)
    
    # Загружаем реестр сервисов
    registry = load_web_services_registry()
    
    print("\n📋 Доступные Enhanced сервисы:")
    for service_id, service in registry['web_services'].items():
        if 'enhanced' in service_id:
            status_emoji = "🟢" if service['status'] == 'running' else "🛌"
            print(f"  {status_emoji} {service['name']} - {service['status']} (порт {service['port']})")
    
    print("\n🎯 Активация Enhanced сервисов...")
    
    # Запускаем сервисы
    api_docs_success = start_enhanced_api_docs()
    time.sleep(2)  # Небольшая пауза между запусками
    
    arch_viz_success = start_enhanced_architecture_visualizer()
    
    print("\n" + "=" * 50)
    if api_docs_success and arch_viz_success:
        print("🎉 Все Enhanced сервисы успешно активированы!")
        print("\n🌐 Доступные URL:")
        print("  📖 Enhanced API Docs: http://localhost:8080")
        print("  🏗️  Architecture Visualizer: http://localhost:8081")
    else:
        print("⚠️  Некоторые сервисы не удалось запустить. Проверьте логи.")
    
    print("\n💡 Для деактивации используйте: python3 scripts/deactivate_enhanced_services.py")

if __name__ == "__main__":
    main()