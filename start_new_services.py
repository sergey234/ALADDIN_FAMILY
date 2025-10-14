#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск новых сервисов ALADDIN
Interactive API Docs и Real-time Architecture
"""

import os
import sys
import subprocess
import threading
import time
import signal
import logging
from datetime import datetime
from typing import List, Dict

class ALADDINServicesManager:
    """Менеджер запуска новых сервисов ALADDIN"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.services = {}
        self.running = False
        
    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/new_services.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(self.__class__.__name__)
    
    def start_interactive_api_docs(self):
        """Запуск Interactive API Docs"""
        try:
            self.logger.info("🚀 Запуск Interactive API Docs...")
            
            # Проверка наличия файла
            if not os.path.exists("api_docs/secure_api_docs.py"):
                self.logger.error("❌ Файл api_docs/secure_api_docs.py не найден")
                return False
            
            # Запуск FastAPI сервера
            cmd = [
                sys.executable, "-m", "uvicorn",
                "api_docs.secure_api_docs:InteractiveAPIDocs",
                "--host", "0.0.0.0",
                "--port", "8008",
                "--reload",
                "--log-level", "info"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.services['api_docs'] = {
                'process': process,
                'port': 8008,
                'url': 'http://localhost:8008',
                'name': 'Interactive API Docs'
            }
            
            self.logger.info("✅ Interactive API Docs запущен на порту 8008")
            self.logger.info("🌐 URL: http://localhost:8008")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска Interactive API Docs: {e}")
            return False
    
    def start_real_time_architecture(self):
        """Запуск Real-time Architecture Visualizer"""
        try:
            self.logger.info("🚀 Запуск Real-time Architecture Visualizer...")
            
            # Проверка наличия файла
            if not os.path.exists("architecture/real_time_visualizer.py"):
                self.logger.error("❌ Файл architecture/real_time_visualizer.py не найден")
                return False
            
            # Запуск Flask-SocketIO сервера
            cmd = [
                sys.executable,
                "architecture/real_time_visualizer.py"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.services['architecture'] = {
                'process': process,
                'port': 8007,
                'url': 'http://localhost:8007',
                'name': 'Real-time Architecture'
            }
            
            self.logger.info("✅ Real-time Architecture запущен на порту 8007")
            self.logger.info("🌐 URL: http://localhost:8007")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска Real-time Architecture: {e}")
            return False
    
    def check_dependencies(self):
        """Проверка зависимостей"""
        self.logger.info("🔍 Проверка зависимостей...")
        
        required_packages = [
            'fastapi',
            'uvicorn',
            'flask',
            'flask_socketio',
            'docker',
            'psutil',
            'networkx',
            'matplotlib',
            'numpy',
            'pyyaml',
            'cryptography',
            'pyjwt'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                self.logger.info(f"✅ {package} - установлен")
            except ImportError:
                missing_packages.append(package)
                self.logger.warning(f"❌ {package} - не установлен")
        
        if missing_packages:
            self.logger.error(f"❌ Отсутствующие пакеты: {', '.join(missing_packages)}")
            self.logger.info("💡 Установите их командой: pip install -r requirements_new.txt")
            return False
        
        self.logger.info("✅ Все зависимости установлены")
        return True
    
    def create_directories(self):
        """Создание необходимых директорий"""
        directories = [
            'logs',
            'api_docs/templates',
            'api_docs/static',
            'architecture/templates',
            'architecture/static'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.info(f"📁 Создана директория: {directory}")
    
    def monitor_services(self):
        """Мониторинг сервисов"""
        while self.running:
            try:
                for service_name, service_info in self.services.items():
                    process = service_info['process']
                    
                    if process.poll() is not None:
                        # Процесс завершился
                        self.logger.warning(f"⚠️ Сервис {service_name} завершился")
                        
                        # Попытка перезапуска
                        if service_name == 'api_docs':
                            self.start_interactive_api_docs()
                        elif service_name == 'architecture':
                            self.start_real_time_architecture()
                
                time.sleep(5)  # Проверка каждые 5 секунд
                
            except Exception as e:
                self.logger.error(f"❌ Ошибка мониторинга: {e}")
                time.sleep(5)
    
    def stop_services(self):
        """Остановка всех сервисов"""
        self.logger.info("🛑 Остановка сервисов...")
        
        for service_name, service_info in self.services.items():
            try:
                process = service_info['process']
                if process.poll() is None:  # Процесс еще работает
                    process.terminate()
                    process.wait(timeout=10)
                    self.logger.info(f"✅ Сервис {service_name} остановлен")
                else:
                    self.logger.info(f"ℹ️ Сервис {service_name} уже остановлен")
            except Exception as e:
                self.logger.error(f"❌ Ошибка остановки сервиса {service_name}: {e}")
        
        self.services.clear()
        self.running = False
    
    def start_all_services(self):
        """Запуск всех сервисов"""
        self.logger.info("🚀 Запуск всех новых сервисов ALADDIN...")
        self.logger.info("=" * 60)
        
        # Создание директорий
        self.create_directories()
        
        # Проверка зависимостей
        if not self.check_dependencies():
            self.logger.error("❌ Не все зависимости установлены. Запуск прерван.")
            return False
        
        # Запуск сервисов
        success_count = 0
        
        if self.start_interactive_api_docs():
            success_count += 1
        
        if self.start_real_time_architecture():
            success_count += 1
        
        if success_count == 0:
            self.logger.error("❌ Ни один сервис не удалось запустить")
            return False
        
        self.logger.info("=" * 60)
        self.logger.info(f"✅ Запущено {success_count} из 2 сервисов")
        self.logger.info("🌐 Доступные сервисы:")
        
        for service_name, service_info in self.services.items():
            self.logger.info(f"   📊 {service_info['name']}: {service_info['url']}")
        
        # Запуск мониторинга
        self.running = True
        monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        monitor_thread.start()
        
        return True
    
    def show_status(self):
        """Показ статуса сервисов"""
        self.logger.info("📊 Статус сервисов:")
        self.logger.info("=" * 40)
        
        if not self.services:
            self.logger.info("❌ Сервисы не запущены")
            return
        
        for service_name, service_info in self.services.items():
            process = service_info['process']
            status = "🟢 Работает" if process.poll() is None else "🔴 Остановлен"
            
            self.logger.info(f"📊 {service_info['name']}")
            self.logger.info(f"   Статус: {status}")
            self.logger.info(f"   Порт: {service_info['port']}")
            self.logger.info(f"   URL: {service_info['url']}")
            self.logger.info("")

def signal_handler(signum, frame):
    """Обработчик сигналов"""
    print("\n🛑 Получен сигнал остановки...")
    if 'manager' in globals():
        manager.stop_services()
    sys.exit(0)

def main():
    """Главная функция"""
    global manager
    
    # Обработка сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Создание менеджера
        manager = ALADDINServicesManager()
        
        # Запуск сервисов
        if manager.start_all_services():
            print("\n🎉 Новые сервисы ALADDIN успешно запущены!")
            print("\n📋 Доступные сервисы:")
            print("   🛡️ Interactive API Docs: http://localhost:8008")
            print("   🗺️ Real-time Architecture: http://localhost:8007")
            print("\n💡 Для остановки нажмите Ctrl+C")
            
            # Основной цикл
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Остановка сервисов...")
                manager.stop_services()
        else:
            print("❌ Не удалось запустить сервисы")
            return 1
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())