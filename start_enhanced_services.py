#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт запуска Enhanced API Docs и Architecture Visualizer
ALADDIN Security System

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-01-06
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Проверка зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'psutil',
        'httpx',
        'sqlite3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("Установите их командой: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ Все зависимости установлены")
    return True

def check_aladdin_integration():
    """Проверка интеграции с ALADDIN"""
    print("\n🔗 Проверка интеграции с ALADDIN...")
    
    # Проверяем наличие основных модулей
    aladdin_modules = [
        'security/safe_function_manager.py',
        'security/microservices/api_gateway.py',
        'security/microservices/load_balancer.py'
    ]
    
    available_modules = 0
    
    for module in aladdin_modules:
        if Path(module).exists():
            print(f"✅ {module}")
            available_modules += 1
        else:
            print(f"❌ {module}")
    
    if available_modules > 0:
        print(f"✅ Найдено {available_modules}/{len(aladdin_modules)} модулей ALADDIN")
        return True
    else:
        print("⚠️  Модули ALADDIN не найдены, будет использован mock режим")
        return False

def start_enhanced_api_docs():
    """Запуск Enhanced API Docs"""
    print("\n🚀 Запуск Enhanced API Docs на порту 8080...")
    
    try:
        process = subprocess.Popen([
            sys.executable, 'enhanced_api_docs.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Ждем немного для проверки запуска
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Enhanced API Docs запущен успешно")
            print("🌐 Доступен по адресу: http://localhost:8080")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Ошибка запуска Enhanced API Docs:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запуска Enhanced API Docs: {e}")
        return None

def start_enhanced_architecture_visualizer():
    """Запуск Enhanced Architecture Visualizer"""
    print("\n🏗️ Запуск Enhanced Architecture Visualizer на порту 8081...")
    
    try:
        process = subprocess.Popen([
            sys.executable, 'enhanced_architecture_visualizer.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Ждем немного для проверки запуска
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Enhanced Architecture Visualizer запущен успешно")
            print("🌐 Доступен по адресу: http://localhost:8081")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Ошибка запуска Enhanced Architecture Visualizer:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запуска Enhanced Architecture Visualizer: {e}")
        return None

def monitor_processes(processes):
    """Мониторинг процессов"""
    print("\n📊 Мониторинг процессов...")
    
    while True:
        try:
            for name, process in processes.items():
                if process and process.poll() is not None:
                    print(f"⚠️  Процесс {name} завершился неожиданно")
                    processes[name] = None
            
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал остановки...")
            break

def cleanup_processes(processes):
    """Очистка процессов"""
    print("\n🧹 Остановка процессов...")
    
    for name, process in processes.items():
        if process and process.poll() is None:
            print(f"🛑 Остановка {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} остановлен")
            except subprocess.TimeoutExpired:
                print(f"⚠️  Принудительная остановка {name}...")
                process.kill()
                process.wait()
                print(f"✅ {name} принудительно остановлен")
            except Exception as e:
                print(f"❌ Ошибка остановки {name}: {e}")

def main():
    """Главная функция"""
    print("🛡️ ALADDIN Enhanced Services Launcher")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\n❌ Не все зависимости установлены. Завершение работы.")
        return
    
    # Проверяем интеграцию с ALADDIN
    aladdin_available = check_aladdin_integration()
    
    # Запускаем сервисы
    processes = {}
    
    # Запуск Enhanced API Docs
    api_docs_process = start_enhanced_api_docs()
    processes['Enhanced API Docs'] = api_docs_process
    
    # Запуск Enhanced Architecture Visualizer
    arch_process = start_enhanced_architecture_visualizer()
    processes['Enhanced Architecture Visualizer'] = arch_process
    
    # Проверяем, что хотя бы один сервис запустился
    running_services = [name for name, process in processes.items() if process is not None]
    
    if not running_services:
        print("\n❌ Не удалось запустить ни одного сервиса. Завершение работы.")
        return
    
    print(f"\n✅ Успешно запущены сервисы: {', '.join(running_services)}")
    print("\n🌐 Доступные сервисы:")
    print("   📡 Enhanced API Docs: http://localhost:8080")
    print("   🏗️ Enhanced Architecture Visualizer: http://localhost:8081")
    print("\n📋 Возможности:")
    print("   • Реальная интеграция с ALADDIN системой")
    print("   • Мониторинг без Docker через psutil")
    print("   • WebSocket real-time обновления")
    print("   • Интерактивное тестирование API")
    print("   • JWT аутентификация")
    print("   • Экспорт данных в JSON/CSV")
    print("   • 3D визуализация архитектуры")
    
    if aladdin_available:
        print("\n🔗 Интеграция с ALADDIN: АКТИВНА")
        print("   • Сканирование реальных API endpoints")
        print("   • Мониторинг SafeFunctionManager")
        print("   • Отслеживание портов 8006-8012")
    else:
        print("\n⚠️  Интеграция с ALADDIN: MOCK РЕЖИМ")
        print("   • Используются демонстрационные данные")
        print("   • Для полной интеграции настройте ALADDIN")
    
    print("\n⌨️  Нажмите Ctrl+C для остановки всех сервисов")
    
    try:
        # Мониторим процессы
        monitor_processes(processes)
    except KeyboardInterrupt:
        pass
    finally:
        # Очищаем процессы
        cleanup_processes(processes)
        print("\n👋 Все сервисы остановлены. До свидания!")

if __name__ == "__main__":
    main()