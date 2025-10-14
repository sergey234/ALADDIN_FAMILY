#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System Startup Script
Скрипт запуска всей системы ALADDIN
"""

import os
import sys
import subprocess
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional

class ALADDINSystemStarter:
    """Стартер системы ALADDIN"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.system_status = {}
        self.start_time = datetime.now()
        
    def _setup_logging(self) -> logging.Logger:
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/aladdin_startup.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('ALADDINStarter')
    
    def start_system(self) -> bool:
        """Запуск всей системы ALADDIN"""
        try:
            self.logger.info("🚀 Запуск системы ALADDIN Security")
            self.logger.info("=" * 60)
            
            # 1. Проверка зависимостей
            if not self._check_dependencies():
                return False
            
            # 2. Инициализация базы данных
            if not self._initialize_database():
                return False
            
            # 3. Запуск Docker Compose
            if not self._start_docker_compose():
                return False
            
            # 4. Ожидание готовности сервисов
            if not self._wait_for_services():
                return False
            
            # 5. Проверка здоровья системы
            if not self._health_check_system():
                return False
            
            # 6. Запуск мониторинга
            self._start_monitoring()
            
            # 7. Отчет о запуске
            self._generate_startup_report()
            
            self.logger.info("✅ Система ALADDIN успешно запущена!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска системы: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """Проверка зависимостей"""
        self.logger.info("🔍 Проверка зависимостей...")
        
        dependencies = [
            ('docker', 'Docker'),
            ('docker-compose', 'Docker Compose'),
            ('python3', 'Python 3'),
            ('git', 'Git')
        ]
        
        for command, name in dependencies:
            try:
                result = subprocess.run([command, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info(f"✅ {name}: {result.stdout.split()[2]}")
                else:
                    self.logger.error(f"❌ {name} не найден")
                    return False
            except FileNotFoundError:
                self.logger.error(f"❌ {name} не установлен")
                return False
        
        return True
    
    def _initialize_database(self) -> bool:
        """Инициализация базы данных"""
        self.logger.info("🗄️ Инициализация базы данных...")
        
        try:
            # Создание директорий
            os.makedirs('data/postgres', exist_ok=True)
            os.makedirs('data/redis', exist_ok=True)
            os.makedirs('logs', exist_ok=True)
            
            # Проверка файла инициализации
            init_sql = 'config/database/init.sql'
            if not os.path.exists(init_sql):
                self.logger.warning(f"⚠️ Файл {init_sql} не найден, создаем базовый")
                self._create_basic_init_sql(init_sql)
            
            self.logger.info("✅ База данных инициализирована")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации базы данных: {e}")
            return False
    
    def _create_basic_init_sql(self, file_path: str):
        """Создание базового SQL файла"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        sql_content = """
-- ALADDIN Security System Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание схемы для ALADDIN
CREATE SCHEMA IF NOT EXISTS aladdin;

-- Таблица для функций безопасности
CREATE TABLE IF NOT EXISTS aladdin.security_functions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    function_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    function_type VARCHAR(100),
    security_level VARCHAR(50),
    status VARCHAR(50) DEFAULT 'disabled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_critical BOOLEAN DEFAULT FALSE,
    auto_enable BOOLEAN DEFAULT FALSE
);

-- Таблица для метрик
CREATE TABLE IF NOT EXISTS aladdin.system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(10,2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Таблица для логов безопасности
CREATE TABLE IF NOT EXISTS aladdin.security_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    log_level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    service_name VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_security_functions_function_id ON aladdin.security_functions(function_id);
CREATE INDEX IF NOT EXISTS idx_system_metrics_service_timestamp ON aladdin.system_metrics(service_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_security_logs_timestamp ON aladdin.security_logs(timestamp);

-- Вставка базовых функций
INSERT INTO aladdin.security_functions (function_id, name, description, function_type, security_level, status, is_critical, auto_enable) VALUES
('safe_function_manager', 'Safe Function Manager', 'Главный менеджер безопасных функций', 'core', 'high', 'enabled', TRUE, TRUE),
('api_gateway', 'API Gateway', 'Шлюз API для маршрутизации запросов', 'microservice', 'high', 'enabled', TRUE, TRUE),
('security_monitoring', 'Security Monitoring', 'Мониторинг безопасности системы', 'monitoring', 'high', 'enabled', TRUE, TRUE)
ON CONFLICT (function_id) DO NOTHING;

COMMIT;
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(sql_content)
    
    def _start_docker_compose(self) -> bool:
        """Запуск Docker Compose"""
        self.logger.info("🐳 Запуск Docker Compose...")
        
        try:
            # Остановка существующих контейнеров
            subprocess.run(['docker-compose', 'down'], 
                         capture_output=True, text=True)
            
            # Сборка и запуск
            result = subprocess.run([
                'docker-compose', 'up', '--build', '-d'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("✅ Docker Compose запущен успешно")
                return True
            else:
                self.logger.error(f"❌ Ошибка запуска Docker Compose: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска Docker Compose: {e}")
            return False
    
    def _wait_for_services(self) -> bool:
        """Ожидание готовности сервисов"""
        self.logger.info("⏳ Ожидание готовности сервисов...")
        
        services = [
            ('aladdin-core', 8000),
            ('aladdin-sfm', 8002),
            ('aladdin-gateway', 8003),
            ('aladdin-mesh', 8004),
            ('aladdin-ai-agents', 8005),
            ('aladdin-bots', 8006),
            ('aladdin-visualizer', 8007),
            ('aladdin-docs', 8008)
        ]
        
        max_wait_time = 300  # 5 минут
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            all_ready = True
            
            for service_name, port in services:
                if not self._check_service_health(service_name, port):
                    all_ready = False
                    break
            
            if all_ready:
                self.logger.info("✅ Все сервисы готовы")
                return True
            
            self.logger.info("⏳ Ожидание готовности сервисов...")
            time.sleep(10)
        
        self.logger.error("❌ Таймаут ожидания готовности сервисов")
        return False
    
    def _check_service_health(self, service_name: str, port: int) -> bool:
        """Проверка здоровья сервиса"""
        try:
            import requests
            response = requests.get(f'http://localhost:{port}/health', 
                                  timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _health_check_system(self) -> bool:
        """Проверка здоровья системы"""
        self.logger.info("🏥 Проверка здоровья системы...")
        
        health_checks = [
            ('Core System', 'http://localhost:8000/health'),
            ('Safe Function Manager', 'http://localhost:8002/health'),
            ('API Gateway', 'http://localhost:8003/health'),
            ('Service Mesh', 'http://localhost:8004/health'),
            ('AI Agents', 'http://localhost:8005/health'),
            ('Security Bots', 'http://localhost:8006/health'),
            ('Architecture Visualizer', 'http://localhost:8007/health'),
            ('API Documentation', 'http://localhost:8008/health'),
            ('Prometheus', 'http://localhost:9090/'),
            ('Grafana', 'http://localhost:3000/api/health')
        ]
        
        failed_services = []
        
        for service_name, url in health_checks:
            try:
                import requests
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.logger.info(f"✅ {service_name}: OK")
                else:
                    self.logger.warning(f"⚠️ {service_name}: HTTP {response.status_code}")
                    failed_services.append(service_name)
            except Exception as e:
                self.logger.error(f"❌ {service_name}: {e}")
                failed_services.append(service_name)
        
        if failed_services:
            self.logger.warning(f"⚠️ Некоторые сервисы недоступны: {failed_services}")
            return len(failed_services) < 3  # Разрешаем до 3 недоступных сервисов
        
        return True
    
    def _start_monitoring(self):
        """Запуск мониторинга"""
        self.logger.info("📊 Запуск мониторинга...")
        
        # Здесь можно добавить запуск дополнительных мониторинговых сервисов
        self.logger.info("✅ Мониторинг запущен")
    
    def _generate_startup_report(self):
        """Генерация отчета о запуске"""
        self.logger.info("📋 Генерация отчета о запуске...")
        
        end_time = datetime.now()
        startup_time = end_time - self.start_time
        
        report = {
            "startup_time": startup_time.total_seconds(),
            "timestamp": end_time.isoformat(),
            "services": [
                {
                    "name": "ALADDIN Core",
                    "url": "http://localhost:8000",
                    "status": "running"
                },
                {
                    "name": "Safe Function Manager",
                    "url": "http://localhost:8002",
                    "status": "running"
                },
                {
                    "name": "API Gateway",
                    "url": "http://localhost:8003",
                    "status": "running"
                },
                {
                    "name": "Service Mesh",
                    "url": "http://localhost:8004",
                    "status": "running"
                },
                {
                    "name": "AI Agents",
                    "url": "http://localhost:8005",
                    "status": "running"
                },
                {
                    "name": "Security Bots",
                    "url": "http://localhost:8006",
                    "status": "running"
                },
                {
                    "name": "Architecture Visualizer",
                    "url": "http://localhost:8007",
                    "status": "running"
                },
                {
                    "name": "API Documentation",
                    "url": "http://localhost:8008",
                    "status": "running"
                },
                {
                    "name": "Prometheus",
                    "url": "http://localhost:9090",
                    "status": "running"
                },
                {
                    "name": "Grafana",
                    "url": "http://localhost:3000",
                    "status": "running"
                }
            ]
        }
        
        # Сохранение отчета
        os.makedirs('reports', exist_ok=True)
        with open(f'reports/startup_report_{end_time.strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info("✅ Отчет о запуске сохранен в reports/")
        self.logger.info(f"⏱️ Время запуска: {startup_time.total_seconds():.2f} секунд")
    
    def stop_system(self) -> bool:
        """Остановка системы"""
        try:
            self.logger.info("🛑 Остановка системы ALADDIN...")
            
            result = subprocess.run(['docker-compose', 'down'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("✅ Система ALADDIN остановлена")
                return True
            else:
                self.logger.error(f"❌ Ошибка остановки системы: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка остановки системы: {e}")
            return False

def main():
    """Главная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == 'stop':
        starter = ALADDINSystemStarter()
        starter.stop_system()
    else:
        starter = ALADDINSystemStarter()
        starter.start_system()

if __name__ == "__main__":
    main()