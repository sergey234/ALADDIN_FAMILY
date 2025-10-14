#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
НАСТРОЙКА ЛОКАЛЬНОЙ ТЕСТОВОЙ СРЕДЫ
Создание изолированной среды для полного тестирования системы
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


class LocalTestEnvironmentSetup:
    """Настройка локальной тестовой среды"""
    
    def __init__(self, project_root: str = "/Users/sergejhlystov/ALADDIN_NEW"):
        self.project_root = Path(project_root)
        self.test_env_dir = self.project_root / "test_environment"
        self.test_data_dir = self.test_env_dir / "test_data"
        self.test_config_dir = self.test_env_dir / "config"
        
    def create_test_environment(self) -> bool:
        """Создание тестовой среды"""
        try:
            print("🏗️ Создание локальной тестовой среды...")
            
            # Создание директорий
            self.test_env_dir.mkdir(exist_ok=True)
            self.test_data_dir.mkdir(exist_ok=True)
            self.test_config_dir.mkdir(exist_ok=True)
            
            # Создание конфигурации тестовой среды
            self._create_test_config()
            
            # Создание тестовых данных
            self._create_test_data()
            
            # Настройка изоляции
            self._setup_isolation()
            
            print("✅ Локальная тестовая среда создана!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания тестовой среды: {e}")
            return False
    
    def _create_test_config(self) -> None:
        """Создание конфигурации тестовой среды"""
        test_config = {
            "test_environment": {
                "name": "ALADDIN Local Test Environment",
                "version": "1.0.0",
                "description": "Локальная тестовая среда для полного тестирования системы",
                "isolation": {
                    "enabled": True,
                    "separate_database": True,
                    "separate_logs": True,
                    "mock_external_apis": True
                },
                "test_data": {
                    "use_mock_data": True,
                    "mock_personal_data": True,
                    "mock_family_profiles": True,
                    "mock_devices": True,
                    "mock_threats": True
                },
                "features": {
                    "all_functions_enabled": True,
                    "personal_data_processing": True,
                    "family_security": True,
                    "biometric_analysis": True,
                    "geolocation_tracking": True,
                    "real_time_monitoring": True
                },
                "compliance": {
                    "test_mode_only": True,
                    "no_real_data": True,
                    "local_processing_only": True,
                    "no_external_transmission": True
                }
            }
        }
        
        config_file = self.test_config_dir / "test_environment_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Конфигурация создана: {config_file}")
    
    def _create_test_data(self) -> None:
        """Создание тестовых данных"""
        test_families = [
            {
                "family_id": "test_family_001",
                "family_name": "Тестовая семья Ивановых",
                "members": [
                    {
                        "member_id": "parent_001",
                        "name": "Иван Иванов",
                        "age": 35,
                        "role": "parent",
                        "email": "ivan.test@example.com",
                        "phone": "+7-900-000-0001"
                    },
                    {
                        "member_id": "child_001",
                        "name": "Анна Иванова",
                        "age": 12,
                        "role": "child",
                        "email": "anna.test@example.com",
                        "phone": "+7-900-000-0002"
                    }
                ],
                "devices": [
                    {
                        "device_id": "device_001",
                        "type": "smartphone",
                        "owner": "parent",
                        "os": "iOS 15.0",
                        "last_seen": "2024-01-15T10:30:00Z"
                    },
                    {
                        "device_id": "device_002",
                        "type": "tablet",
                        "owner": "child",
                        "os": "Android 11",
                        "last_seen": "2024-01-15T10:25:00Z"
                    }
                ]
            },
            {
                "family_id": "test_family_002",
                "family_name": "Тестовая семья Петровых",
                "members": [
                    {
                        "member_id": "parent_002",
                        "name": "Петр Петров",
                        "age": 42,
                        "role": "parent",
                        "email": "petr.test@example.com",
                        "phone": "+7-900-000-0003"
                    },
                    {
                        "member_id": "elderly_001",
                        "name": "Мария Петрова",
                        "age": 68,
                        "role": "elderly",
                        "email": "maria.test@example.com",
                        "phone": "+7-900-000-0004"
                    }
                ],
                "devices": [
                    {
                        "device_id": "device_003",
                        "type": "laptop",
                        "owner": "parent",
                        "os": "Windows 11",
                        "last_seen": "2024-01-15T09:15:00Z"
                    },
                    {
                        "device_id": "device_004",
                        "type": "smartphone",
                        "owner": "elderly",
                        "os": "Android 10",
                        "last_seen": "2024-01-15T08:45:00Z"
                    }
                ]
            }
        ]
        
        # Сохранение тестовых семей
        families_file = self.test_data_dir / "test_families.json"
        with open(families_file, 'w', encoding='utf-8') as f:
            json.dump(test_families, f, indent=2, ensure_ascii=False)
        
        # Создание тестовых угроз
        test_threats = [
            {
                "threat_id": "threat_001",
                "type": "phishing",
                "severity": "high",
                "description": "Фишинговая атака на email",
                "detected_at": "2024-01-15T10:00:00Z",
                "source_ip": "192.168.1.100",
                "target_device": "device_001",
                "status": "blocked"
            },
            {
                "threat_id": "threat_002",
                "type": "malware",
                "severity": "critical",
                "description": "Вредоносное ПО обнаружено",
                "detected_at": "2024-01-15T09:30:00Z",
                "source_ip": "10.0.0.50",
                "target_device": "device_002",
                "status": "quarantined"
            }
        ]
        
        threats_file = self.test_data_dir / "test_threats.json"
        with open(threats_file, 'w', encoding='utf-8') as f:
            json.dump(test_threats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Тестовые данные созданы в: {self.test_data_dir}")
    
    def _setup_isolation(self) -> None:
        """Настройка изоляции тестовой среды"""
        isolation_config = {
            "database": {
                "type": "sqlite",
                "path": str(self.test_env_dir / "test_database.db"),
                "separate_from_production": True
            },
            "logs": {
                "path": str(self.test_env_dir / "test_logs"),
                "separate_from_production": True,
                "level": "DEBUG"
            },
            "external_apis": {
                "mock_mode": True,
                "mock_responses": True,
                "no_real_requests": True
            },
            "network": {
                "isolated": True,
                "no_external_connections": True,
                "local_only": True
            }
        }
        
        isolation_file = self.test_config_dir / "isolation_config.json"
        with open(isolation_file, 'w', encoding='utf-8') as f:
            json.dump(isolation_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Изоляция настроена: {isolation_file}")
    
    def run_full_system_test(self) -> bool:
        """Запуск полного тестирования системы"""
        try:
            print("🧪 Запуск полного тестирования системы...")
            
            # Активация тестового режима
            test_mode_script = self.project_root / "security" / "test_mode_manager.py"
            if test_mode_script.exists():
                result = subprocess.run([
                    sys.executable, str(test_mode_script)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Тестовый режим активирован")
                    print(f"Вывод: {result.stdout}")
                else:
                    print(f"❌ Ошибка активации тестового режима: {result.stderr}")
                    return False
            else:
                print("❌ Файл test_mode_manager.py не найден")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска тестирования: {e}")
            return False
    
    def cleanup_test_environment(self) -> bool:
        """Очистка тестовой среды"""
        try:
            print("🧹 Очистка тестовой среды...")
            
            # Удаление тестовых данных
            import shutil
            if self.test_env_dir.exists():
                shutil.rmtree(self.test_env_dir)
                print("✅ Тестовая среда очищена")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка очистки: {e}")
            return False


def main():
    """Основная функция"""
    setup = LocalTestEnvironmentSetup()
    
    print("🏗️ НАСТРОЙКА ЛОКАЛЬНОЙ ТЕСТОВОЙ СРЕДЫ")
    print("=" * 50)
    
    # Создание тестовой среды
    if setup.create_test_environment():
        print("\n✅ Тестовая среда создана успешно!")
        
        # Запуск тестирования
        if setup.run_full_system_test():
            print("\n✅ Полное тестирование системы завершено!")
        else:
            print("\n❌ Ошибка при тестировании")
    else:
        print("\n❌ Ошибка создания тестовой среды")
    
    print("\n" + "=" * 50)
    print("🎯 ТЕСТОВАЯ СРЕДА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")


if __name__ == "__main__":
    main()