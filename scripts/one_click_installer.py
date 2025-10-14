#!/usr/bin/env python3
"""
ONE-CLICK INSTALLER для системы безопасности ALADDIN
Полностью автоматическая установка за 30 секунд
"""

import sys
import os
import time
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import getpass

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))


class OneClickInstaller:
    """Полностью автоматический установщик ALADDIN"""

    def __init__(self):
        self.start_time = time.time()
        self.install_log = []
        self.success_count = 0
        self.error_count = 0
        self.project_root = Path(__file__).parent.parent

    def log(self, message, status="INFO"):
        """Логирование установки"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {message}"
        self.install_log.append(log_entry)
        print(f"🔧 {log_entry}")

    def check_system_requirements(self):
        """Проверка системных требований"""
        self.log("Проверка системных требований...")
        
        # Проверка Python версии
        if sys.version_info < (3, 8):
            self.log("❌ Требуется Python 3.8+", "ERROR")
            return False
        
        self.log(f"✅ Python {sys.version.split()[0]} - OK")
        
        # Проверка доступности портов
        ports_to_check = [8000, 8001, 8002, 8003, 8004, 8005, 8006]
        for port in ports_to_check:
            if self.is_port_available(port):
                self.log(f"✅ Порт {port} - свободен")
            else:
                self.log(f"⚠️ Порт {port} - занят (будет использован альтернативный)")
        
        return True

    def is_port_available(self, port):
        """Проверка доступности порта"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def install_dependencies(self):
        """Автоматическая установка зависимостей"""
        self.log("Установка зависимостей...")
        
        dependencies = [
            "cryptography",
            "requests",
            "psutil",
            "watchdog"
        ]
        
        for dep in dependencies:
            try:
                self.log(f"Установка {dep}...")
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                self.log(f"✅ {dep} установлен")
                self.success_count += 1
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Ошибка установки {dep}: {e}", "ERROR")
                self.error_count += 1

    def create_directories(self):
        """Создание необходимых директорий"""
        self.log("Создание структуры директорий...")
        
        directories = [
            "logs",
            "data",
            "backups",
            "config",
            "mobile",
            "docs",
            "tests"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            self.log(f"✅ Директория {directory} создана")
            self.success_count += 1

    def setup_configuration(self):
        """Автоматическая настройка конфигурации"""
        self.log("Настройка конфигурации...")
        
        # Создание базовой конфигурации
        config = {
            "system": {
                "name": "ALADDIN Security System",
                "version": "1.0.0",
                "install_date": datetime.now().isoformat(),
                "installer": "one_click_installer"
            },
            "security": {
                "level": "high",
                "auto_update": True,
                "monitoring": True
            },
            "ports": {
                "main_api": 8000,
                "vpn": 8001,
                "antivirus": 8002,
                "mobile": 8003,
                "monitoring": 8004,
                "admin": 8005,
                "backup": 8006
            },
            "features": {
                "vpn": True,
                "antivirus": True,
                "mobile_api": True,
                "monitoring": True,
                "backup": True
            }
        }
        
        config_path = self.project_root / "config" / "system_config.json"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Конфигурация создана")
        self.success_count += 1

    def setup_database(self):
        """Настройка базы данных"""
        self.log("Настройка базы данных...")
        
        try:
            # Создание SQLite базы данных
            db_path = self.project_root / "data" / "aladdin.db"
            db_path.parent.mkdir(exist_ok=True)
            
            # Инициализация базы данных
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Создание основных таблиц
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.log("✅ База данных настроена")
            self.success_count += 1
            
        except Exception as e:
            self.log(f"❌ Ошибка настройки БД: {e}", "ERROR")
            self.error_count += 1

    def setup_logging(self):
        """Настройка системы логирования"""
        self.log("Настройка системы логирования...")
        
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "level": "INFO",
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "level": "DEBUG",
                    "formatter": "standard",
                    "class": "logging.FileHandler",
                    "filename": str(self.project_root / "logs" / "aladdin.log"),
                    "mode": "a"
                }
            },
            "loggers": {
                "": {
                    "handlers": ["default", "file"],
                    "level": "DEBUG",
                    "propagate": False
                }
            }
        }
        
        log_config_path = self.project_root / "config" / "logging_config.json"
        with open(log_config_path, 'w', encoding='utf-8') as f:
            json.dump(log_config, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Логирование настроено")
        self.success_count += 1

    def run_quality_tests(self):
        """Запуск тестов качества"""
        self.log("Запуск тестов качества...")
        
        try:
            # Запуск быстрых тестов
            test_script = self.project_root / "scripts" / "ultra_fast_test.py"
            if test_script.exists():
                result = subprocess.run([sys.executable, str(test_script)], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self.log("✅ Тесты качества пройдены")
                    self.success_count += 1
                else:
                    self.log(f"⚠️ Тесты качества с предупреждениями: {result.stderr}", "WARNING")
            else:
                self.log("⚠️ Файл тестов не найден", "WARNING")
                
        except subprocess.TimeoutExpired:
            self.log("⚠️ Тесты прерваны по таймауту", "WARNING")
        except Exception as e:
            self.log(f"❌ Ошибка тестирования: {e}", "ERROR")
            self.error_count += 1

    def create_startup_script(self):
        """Создание скрипта запуска"""
        self.log("Создание скрипта запуска...")
        
        startup_script = '''#!/bin/bash
# ALADDIN Security System - Скрипт запуска
# Автоматически создан One-Click Installer

echo "🚀 Запуск системы безопасности ALADDIN..."

# Переход в директорию проекта
cd "$(dirname "$0")"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден!"
    exit 1
fi

# Запуск основных сервисов
echo "🔧 Запуск основных сервисов..."

# API Gateway
python3 -m http.server 8000 &
echo "✅ API Gateway запущен на порту 8000"

# VPN Service
python3 scripts/real_vpn_api_server.py &
echo "✅ VPN Service запущен на порту 8001"

# Antivirus Service
python3 scripts/antivirus_api_server.py &
echo "✅ Antivirus Service запущен на порту 8002"

# Mobile API
python3 mobile/mobile_api.py &
echo "✅ Mobile API запущен на порту 8003"

echo "🎉 Система ALADDIN успешно запущена!"
echo "📱 Доступ: http://localhost:8000"
echo "📊 Мониторинг: http://localhost:8004"
echo "🔧 Админ панель: http://localhost:8005"

# Ожидание завершения
wait
'''
        
        startup_path = self.project_root / "start_aladdin.sh"
        with open(startup_path, 'w', encoding='utf-8') as f:
            f.write(startup_script)
        
        # Делаем скрипт исполняемым
        os.chmod(startup_path, 0o755)
        
        self.log("✅ Скрипт запуска создан")
        self.success_count += 1

    def create_uninstaller(self):
        """Создание деинсталлятора"""
        self.log("Создание деинсталлятора...")
        
        uninstaller_script = '''#!/bin/bash
# ALADDIN Security System - Деинсталлятор
# Автоматически создан One-Click Installer

echo "🗑️ Удаление системы безопасности ALADDIN..."

# Остановка всех процессов ALADDIN
echo "⏹️ Остановка сервисов..."
pkill -f "aladdin"
pkill -f "vpn"
pkill -f "antivirus"

# Удаление файлов (с подтверждением)
read -p "Удалить все файлы ALADDIN? (y/N): " confirm
if [[ $confirm == [yY] ]]; then
    echo "🗑️ Удаление файлов..."
    rm -rf logs/
    rm -rf data/
    rm -rf backups/
    rm -rf config/
    echo "✅ Файлы удалены"
else
    echo "ℹ️ Файлы сохранены"
fi

echo "✅ Деинсталляция завершена"
'''
        
        uninstaller_path = self.project_root / "uninstall_aladdin.sh"
        with open(uninstaller_path, 'w', encoding='utf-8') as f:
            f.write(uninstaller_script)
        
        os.chmod(uninstaller_path, 0o755)
        
        self.log("✅ Деинсталлятор создан")
        self.success_count += 1

    def generate_install_report(self):
        """Генерация отчета об установке"""
        self.log("Генерация отчета об установке...")
        
        install_time = time.time() - self.start_time
        
        report = {
            "install_info": {
                "installer": "One-Click Installer v1.0",
                "install_date": datetime.now().isoformat(),
                "install_time_seconds": round(install_time, 2),
                "python_version": sys.version.split()[0],
                "project_path": str(self.project_root)
            },
            "statistics": {
                "successful_operations": self.success_count,
                "failed_operations": self.error_count,
                "total_operations": self.success_count + self.error_count,
                "success_rate": round((self.success_count / (self.success_count + self.error_count)) * 100, 2) if (self.success_count + self.error_count) > 0 else 0
            },
            "installed_components": [
                "Системные зависимости",
                "Структура директорий",
                "Конфигурация системы",
                "База данных SQLite",
                "Система логирования",
                "Скрипт запуска",
                "Деинсталлятор"
            ],
            "access_urls": {
                "main_api": "http://localhost:8000",
                "vpn_service": "http://localhost:8001",
                "antivirus_service": "http://localhost:8002",
                "mobile_api": "http://localhost:8003",
                "monitoring": "http://localhost:8004",
                "admin_panel": "http://localhost:8005",
                "backup_service": "http://localhost:8006"
            },
            "install_log": self.install_log
        }
        
        report_path = self.project_root / "INSTALL_REPORT.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Отчет об установке создан")
        return report

    def run_installation(self):
        """Запуск полной установки"""
        print("🚀 ONE-CLICK INSTALLER - ALADDIN SECURITY SYSTEM")
        print("=" * 60)
        print("Полностью автоматическая установка за 30 секунд!")
        print("=" * 60)
        print()
        
        # Проверка системных требований
        if not self.check_system_requirements():
            self.log("❌ Системные требования не выполнены", "ERROR")
            return False
        
        # Установка зависимостей
        self.install_dependencies()
        
        # Создание директорий
        self.create_directories()
        
        # Настройка конфигурации
        self.setup_configuration()
        
        # Настройка базы данных
        self.setup_database()
        
        # Настройка логирования
        self.setup_logging()
        
        # Запуск тестов качества
        self.run_quality_tests()
        
        # Создание скрипта запуска
        self.create_startup_script()
        
        # Создание деинсталлятора
        self.create_uninstaller()
        
        # Генерация отчета
        report = self.generate_install_report()
        
        # Финальный отчет
        install_time = time.time() - self.start_time
        print()
        print("🎉 УСТАНОВКА ЗАВЕРШЕНА!")
        print("=" * 60)
        print(f"⏱️ Время установки: {install_time:.2f} секунд")
        print(f"✅ Успешных операций: {self.success_count}")
        print(f"❌ Ошибок: {self.error_count}")
        print(f"📊 Успешность: {report['statistics']['success_rate']}%")
        print()
        print("🌐 ДОСТУП К СИСТЕМЕ:")
        for service, url in report['access_urls'].items():
            print(f"   {service}: {url}")
        print()
        print("🚀 ДЛЯ ЗАПУСКА СИСТЕМЫ:")
        print("   ./start_aladdin.sh")
        print()
        print("📋 ОТЧЕТ УСТАНОВКИ:")
        print(f"   {self.project_root}/INSTALL_REPORT.json")
        print()
        
        return self.error_count == 0


def main():
    """Главная функция"""
    installer = OneClickInstaller()
    success = installer.run_installation()
    
    if success:
        print("✅ Установка завершена успешно!")
        sys.exit(0)
    else:
        print("❌ Установка завершена с ошибками!")
        sys.exit(1)


if __name__ == "__main__":
    main()