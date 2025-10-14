#!/usr/bin/env python3
"""
🛡️ ALADDIN Enhanced Services Deactivator
Скрипт для перевода Enhanced сервисов в спящий режим
"""

import os
import sys
import json
import subprocess
import time
import signal
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

def find_enhanced_processes():
    """Находит запущенные процессы Enhanced сервисов"""
    try:
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        
        processes = []
        for line in result.stdout.split('\n'):
            if 'enhanced_api_docs.py' in line or 'enhanced_architecture_visualizer.py' in line:
                if 'grep' not in line:  # Исключаем строку с grep
                    parts = line.split()
                    if len(parts) > 1:
                        pid = int(parts[1])
                        service_name = "Enhanced API Docs" if 'enhanced_api_docs.py' in line else "Enhanced Architecture Visualizer"
                        processes.append((pid, service_name))
        
        return processes
    except Exception as e:
        print(f"❌ Ошибка поиска процессов: {e}")
        return []

def stop_enhanced_service(pid, service_name):
    """Останавливает Enhanced сервис"""
    try:
        print(f"🛑 Остановка {service_name} (PID: {pid})...")
        
        # Отправляем SIGTERM
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        
        # Проверяем, остановился ли процесс
        try:
            os.kill(pid, 0)  # Проверяем существование процесса
            print(f"⚠️  Процесс {service_name} не остановился, отправляем SIGKILL...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(1)
        except ProcessLookupError:
            print(f"✅ {service_name} успешно остановлен")
            return True
        
        return True
        
    except ProcessLookupError:
        print(f"✅ {service_name} уже остановлен")
        return True
    except Exception as e:
        print(f"❌ Ошибка остановки {service_name}: {e}")
        return False

def deactivate_enhanced_services():
    """Деактивирует все Enhanced сервисы"""
    print("🛌 Переход Enhanced сервисов в спящий режим...")
    
    # Находим запущенные процессы
    processes = find_enhanced_processes()
    
    if not processes:
        print("ℹ️  Enhanced сервисы не запущены")
        return True
    
    print(f"📋 Найдено {len(processes)} запущенных Enhanced сервисов:")
    for pid, service_name in processes:
        print(f"  - {service_name} (PID: {pid})")
    
    # Останавливаем каждый сервис
    success_count = 0
    for pid, service_name in processes:
        if stop_enhanced_service(pid, service_name):
            success_count += 1
    
    # Обновляем статус в реестре
    update_service_status("enhanced_api_docs", "dormant")
    update_service_status("enhanced_architecture_visualizer", "dormant")
    
    return success_count == len(processes)

def main():
    """Основная функция"""
    print("🛡️ ALADDIN Enhanced Services Deactivator")
    print("=" * 50)
    
    # Загружаем реестр сервисов
    registry = load_web_services_registry()
    
    print("\n📋 Статус Enhanced сервисов:")
    for service_id, service in registry['web_services'].items():
        if 'enhanced' in service_id:
            status_emoji = "🟢" if service['status'] == 'running' else "🛌"
            print(f"  {status_emoji} {service['name']} - {service['status']}")
    
    print("\n🎯 Деактивация Enhanced сервисов...")
    
    # Деактивируем сервисы
    success = deactivate_enhanced_services()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Все Enhanced сервисы переведены в спящий режим!")
        print("\n💡 Для активации используйте: python3 scripts/activate_enhanced_services.py")
    else:
        print("⚠️  Некоторые сервисы не удалось остановить. Проверьте процессы вручную.")

if __name__ == "__main__":
    main()