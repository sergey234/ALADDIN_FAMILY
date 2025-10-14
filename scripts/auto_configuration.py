#!/usr/bin/env python3
"""
AUTO-CONFIGURATION для системы безопасности ALADDIN
Полная автоматизация всех компонентов системы
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
import platform

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))


class AutoConfiguration:
    """Полная автоматизация конфигурации ALADDIN"""

    def __init__(self):
        self.start_time = time.time()
        self.config_log = []
        self.success_count = 0
        self.error_count = 0
        self.project_root = Path(__file__).parent.parent
        self.system_info = self.detect_system_info()

    def detect_system_info(self):
        """Определение информации о системе"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": sys.version.split()[0],
            "cpu_count": os.cpu_count(),
            "memory_gb": round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024.**3), 2) if hasattr(os, 'sysconf') else "Unknown"
        }

    def log(self, message, status="INFO"):
        """Логирование конфигурации"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {message}"
        self.config_log.append(log_entry)
        print(f"🔧 {log_entry}")

    def auto_detect_optimal_settings(self):
        """Автоматическое определение оптимальных настроек"""
        self.log("Автоматическое определение оптимальных настроек...")
        
        # Определение уровня безопасности на основе системы
        if self.system_info["os"] == "Darwin":  # macOS
            security_level = "high"
            self.log("🍎 macOS обнаружен - высокий уровень безопасности")
        elif self.system_info["os"] == "Linux":
            security_level = "maximum"
            self.log("🐧 Linux обнаружен - максимальный уровень безопасности")
        else:
            security_level = "medium"
            self.log("💻 Другая ОС - средний уровень безопасности")
        
        # Определение производительности на основе ресурсов
        cpu_count = self.system_info["cpu_count"]
        if cpu_count >= 8:
            performance_level = "high"
            self.log(f"⚡ {cpu_count} CPU - высокий уровень производительности")
        elif cpu_count >= 4:
            performance_level = "medium"
            self.log(f"⚡ {cpu_count} CPU - средний уровень производительности")
        else:
            performance_level = "low"
            self.log(f"⚡ {cpu_count} CPU - низкий уровень производительности")
        
        # Определение портов
        base_port = 8000
        ports = {}
        for i, service in enumerate([
            "main_api", "vpn", "antivirus", "mobile", 
            "monitoring", "admin", "backup"
        ]):
            ports[service] = base_port + i
        
        return {
            "security_level": security_level,
            "performance_level": performance_level,
            "ports": ports,
            "auto_update": True,
            "monitoring": True,
            "backup_enabled": True,
            "log_level": "INFO"
        }

    def configure_security_components(self, settings):
        """Автоматическая конфигурация компонентов безопасности"""
        self.log("Конфигурация компонентов безопасности...")
        
        # Конфигурация VPN
        vpn_config = {
            "enabled": True,
            "protocol": "OpenVPN",
            "encryption": "AES-256-GCM",
            "port": settings["ports"]["vpn"],
            "auto_connect": True,
            "kill_switch": True,
            "dns_protection": True
        }
        
        vpn_config_path = self.project_root / "config" / "vpn_config.json"
        vpn_config_path.parent.mkdir(exist_ok=True)
        with open(vpn_config_path, 'w', encoding='utf-8') as f:
            json.dump(vpn_config, f, indent=2, ensure_ascii=False)
        
        self.log("✅ VPN конфигурация создана")
        self.success_count += 1
        
        # Конфигурация Antivirus
        antivirus_config = {
            "enabled": True,
            "engine": "ClamAV",
            "port": settings["ports"]["antivirus"],
            "auto_scan": True,
            "real_time_protection": True,
            "quarantine_enabled": True,
            "scan_schedule": "daily"
        }
        
        antivirus_config_path = self.project_root / "config" / "antivirus_config.json"
        with open(antivirus_config_path, 'w', encoding='utf-8') as f:
            json.dump(antivirus_config, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Antivirus конфигурация создана")
        self.success_count += 1
        
        # Конфигурация Mobile API
        mobile_config = {
            "enabled": True,
            "port": settings["ports"]["mobile"],
            "push_notifications": True,
            "offline_mode": True,
            "touch_optimized": True,
            "auto_sync": True
        }
        
        mobile_config_path = self.project_root / "config" / "mobile_config.json"
        with open(mobile_config_path, 'w', encoding='utf-8') as f:
            json.dump(mobile_config, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Mobile API конфигурация создана")
        self.success_count += 1

    def configure_monitoring_system(self, settings):
        """Автоматическая конфигурация системы мониторинга"""
        self.log("Конфигурация системы мониторинга...")
        
        monitoring_config = {
            "enabled": True,
            "port": settings["ports"]["monitoring"],
            "real_time": True,
            "alerts": True,
            "dashboard": True,
            "metrics_retention_days": 30,
            "log_level": settings["log_level"],
            "performance_monitoring": True,
            "security_monitoring": True
        }
        
        monitoring_config_path = self.project_root / "config" / "monitoring_config.json"
        with open(monitoring_config_path, 'w', encoding='utf-8') as f:
            json.dump(monitoring_config, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Мониторинг конфигурация создана")
        self.success_count += 1

    def configure_database_optimization(self):
        """Автоматическая оптимизация базы данных"""
        self.log("Оптимизация базы данных...")
        
        try:
            import sqlite3
            db_path = self.project_root / "data" / "aladdin.db"
            
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Оптимизация SQLite
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
                
                # Создание индексов для производительности
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_security_events_timestamp 
                    ON security_events(timestamp)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_security_events_type 
                    ON security_events(event_type)
                ''')
                
                conn.commit()
                conn.close()
                
                self.log("✅ База данных оптимизирована")
                self.success_count += 1
            else:
                self.log("⚠️ База данных не найдена", "WARNING")
                
        except Exception as e:
            self.log(f"❌ Ошибка оптимизации БД: {e}", "ERROR")
            self.error_count += 1

    def configure_logging_optimization(self):
        """Автоматическая оптимизация логирования"""
        self.log("Оптимизация системы логирования...")
        
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "level": "DEBUG",
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.project_root / "logs" / "aladdin.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                },
                "error_file": {
                    "level": "ERROR",
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.project_root / "logs" / "errors.log"),
                    "maxBytes": 5242880,  # 5MB
                    "backupCount": 3
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": "DEBUG",
                    "propagate": False
                },
                "errors": {
                    "handlers": ["error_file"],
                    "level": "ERROR",
                    "propagate": False
                }
            }
        }
        
        log_config_path = self.project_root / "config" / "logging_config.json"
        with open(log_config_path, 'w', encoding='utf-8') as f:
            json.dump(log_config, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Логирование оптимизировано")
        self.success_count += 1

    def configure_performance_optimization(self, settings):
        """Автоматическая оптимизация производительности"""
        self.log("Оптимизация производительности...")
        
        perf_config = {
            "caching": {
                "enabled": True,
                "memory_cache_size": "256MB",
                "disk_cache_size": "1GB",
                "cache_ttl": 3600
            },
            "threading": {
                "max_workers": min(self.system_info["cpu_count"] * 2, 16),
                "thread_pool_size": min(self.system_info["cpu_count"], 8)
            },
            "async": {
                "enabled": True,
                "max_concurrent_requests": 100,
                "request_timeout": 30
            },
            "compression": {
                "enabled": True,
                "algorithm": "gzip",
                "min_size": 1024
            }
        }
        
        perf_config_path = self.project_root / "config" / "performance_config.json"
        with open(perf_config_path, 'w', encoding='utf-8') as f:
            json.dump(perf_config, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Производительность оптимизирована")
        self.success_count += 1

    def configure_security_policies(self, settings):
        """Автоматическая конфигурация политик безопасности"""
        self.log("Конфигурация политик безопасности...")
        
        security_policies = {
            "access_control": {
                "max_login_attempts": 5,
                "lockout_duration": 300,  # 5 минут
                "password_policy": {
                    "min_length": 12,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_symbols": True
                }
            },
            "network_security": {
                "rate_limiting": True,
                "max_requests_per_minute": 100,
                "ip_whitelist": [],
                "ip_blacklist": [],
                "geo_blocking": False
            },
            "data_protection": {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "backup_encryption": True,
                "data_retention_days": 365
            },
            "compliance": {
                "gdpr_compliance": True,
                "coppa_compliance": True,
                "russian_data_protection": True,
                "audit_logging": True
            }
        }
        
        policies_path = self.project_root / "config" / "security_policies.json"
        with open(policies_path, 'w', encoding='utf-8') as f:
            json.dump(security_policies, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Политики безопасности настроены")
        self.success_count += 1

    def create_auto_startup_services(self):
        """Создание автоматических сервисов запуска"""
        self.log("Создание автоматических сервисов...")
        
        # Создание systemd сервиса для Linux
        if self.system_info["os"] == "Linux":
            systemd_service = f"""[Unit]
Description=ALADDIN Security System
After=network.target

[Service]
Type=simple
User={getpass.getuser()}
WorkingDirectory={self.project_root}
ExecStart={sys.executable} {self.project_root}/scripts/start_services.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
            
            service_path = self.project_root / "aladdin-security.service"
            with open(service_path, 'w', encoding='utf-8') as f:
                f.write(systemd_service)
            
            self.log("✅ Systemd сервис создан")
            self.success_count += 1
        
        # Создание launchd сервиса для macOS
        elif self.system_info["os"] == "Darwin":
            launchd_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aladdin.security</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{self.project_root}/scripts/start_services.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{self.project_root}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""
            
            plist_path = self.project_root / "com.aladdin.security.plist"
            with open(plist_path, 'w', encoding='utf-8') as f:
                f.write(launchd_plist)
            
            self.log("✅ Launchd сервис создан")
            self.success_count += 1

    def generate_configuration_report(self):
        """Генерация отчета о конфигурации"""
        self.log("Генерация отчета о конфигурации...")
        
        config_time = time.time() - self.start_time
        
        report = {
            "configuration_info": {
                "configurator": "Auto-Configuration v1.0",
                "config_date": datetime.now().isoformat(),
                "config_time_seconds": round(config_time, 2),
                "system_info": self.system_info
            },
            "statistics": {
                "successful_configurations": self.success_count,
                "failed_configurations": self.error_count,
                "total_configurations": self.success_count + self.error_count,
                "success_rate": round((self.success_count / (self.success_count + self.error_count)) * 100, 2) if (self.success_count + self.error_count) > 0 else 0
            },
            "configured_components": [
                "Компоненты безопасности (VPN, Antivirus, Mobile)",
                "Система мониторинга",
                "Оптимизация базы данных",
                "Оптимизация логирования",
                "Оптимизация производительности",
                "Политики безопасности",
                "Автоматические сервисы"
            ],
            "configuration_files": [
                "config/vpn_config.json",
                "config/antivirus_config.json",
                "config/mobile_config.json",
                "config/monitoring_config.json",
                "config/performance_config.json",
                "config/security_policies.json",
                "config/logging_config.json"
            ],
            "configuration_log": self.config_log
        }
        
        report_path = self.project_root / "CONFIGURATION_REPORT.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Отчет о конфигурации создан")
        return report

    def run_auto_configuration(self):
        """Запуск полной автоматической конфигурации"""
        print("🔧 AUTO-CONFIGURATION - ALADDIN SECURITY SYSTEM")
        print("=" * 60)
        print("Полная автоматизация всех компонентов системы!")
        print("=" * 60)
        print()
        
        # Определение оптимальных настроек
        settings = self.auto_detect_optimal_settings()
        
        # Конфигурация компонентов безопасности
        self.configure_security_components(settings)
        
        # Конфигурация системы мониторинга
        self.configure_monitoring_system(settings)
        
        # Оптимизация базы данных
        self.configure_database_optimization()
        
        # Оптимизация логирования
        self.configure_logging_optimization()
        
        # Оптимизация производительности
        self.configure_performance_optimization(settings)
        
        # Конфигурация политик безопасности
        self.configure_security_policies(settings)
        
        # Создание автоматических сервисов
        self.create_auto_startup_services()
        
        # Генерация отчета
        report = self.generate_configuration_report()
        
        # Финальный отчет
        config_time = time.time() - self.start_time
        print()
        print("🎉 АВТОМАТИЧЕСКАЯ КОНФИГУРАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 60)
        print(f"⏱️ Время конфигурации: {config_time:.2f} секунд")
        print(f"✅ Успешных конфигураций: {self.success_count}")
        print(f"❌ Ошибок: {self.error_count}")
        print(f"📊 Успешность: {report['statistics']['success_rate']}%")
        print()
        print("📋 ОТЧЕТ КОНФИГУРАЦИИ:")
        print(f"   {self.project_root}/CONFIGURATION_REPORT.json")
        print()
        
        return self.error_count == 0


def main():
    """Главная функция"""
    configurator = AutoConfiguration()
    success = configurator.run_auto_configuration()
    
    if success:
        print("✅ Автоматическая конфигурация завершена успешно!")
        sys.exit(0)
    else:
        print("❌ Автоматическая конфигурация завершена с ошибками!")
        sys.exit(1)


if __name__ == "__main__":
    main()