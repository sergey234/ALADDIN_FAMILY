#!/usr/bin/env python3
"""
CONFIGURATION TEMPLATES для системы безопасности ALADDIN
Расширенные шаблоны конфигурации для разных сценариев
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
import getpass
import platform

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))


class ConfigurationTemplates:
    """Система расширенных шаблонов конфигурации ALADDIN"""

    def __init__(self):
        self.start_time = time.time()
        self.templates_log = []
        self.success_count = 0
        self.error_count = 0
        self.project_root = Path(__file__).parent.parent

    def log(self, message, status="INFO"):
        """Логирование создания шаблонов"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {message}"
        self.templates_log.append(log_entry)
        print(f"📋 {log_entry}")

    def create_family_templates(self):
        """Создание шаблонов для семейного использования"""
        self.log("Создание шаблонов для семейного использования...")
        
        family_templates = {
            "young_family": {
                "name": "Молодая семья",
                "description": "Для семей с маленькими детьми (0-12 лет)",
                "age_groups": ["0-3", "4-6", "7-9", "10-12"],
                "security_level": "high",
                "features": {
                    "parental_controls": True,
                    "content_filtering": True,
                    "time_restrictions": True,
                    "location_tracking": True,
                    "emergency_contacts": True
                },
                "vpn_settings": {
                    "auto_connect": True,
                    "kill_switch": True,
                    "child_safe_servers": True
                },
                "antivirus_settings": {
                    "real_time_protection": True,
                    "child_safe_scanning": True,
                    "quarantine_automatic": True
                },
                "monitoring_settings": {
                    "alerts_to_parents": True,
                    "daily_reports": True,
                    "suspicious_activity": True
                }
            },
            "teenage_family": {
                "name": "Семья с подростками",
                "description": "Для семей с подростками (13-17 лет)",
                "age_groups": ["13-15", "16-17"],
                "security_level": "medium",
                "features": {
                    "parental_controls": True,
                    "content_filtering": "moderate",
                    "time_restrictions": "flexible",
                    "privacy_protection": True,
                    "social_media_monitoring": True
                },
                "vpn_settings": {
                    "auto_connect": False,
                    "kill_switch": True,
                    "privacy_focused": True
                },
                "antivirus_settings": {
                    "real_time_protection": True,
                    "gaming_mode": True,
                    "performance_optimized": True
                },
                "monitoring_settings": {
                    "weekly_reports": True,
                    "privacy_respecting": True,
                    "educational_alerts": True
                }
            },
            "adult_family": {
                "name": "Взрослая семья",
                "description": "Для семей только со взрослыми (18+ лет)",
                "age_groups": ["18+"],
                "security_level": "balanced",
                "features": {
                    "privacy_protection": True,
                    "work_security": True,
                    "financial_protection": True,
                    "identity_protection": True
                },
                "vpn_settings": {
                    "auto_connect": False,
                    "kill_switch": True,
                    "work_compatible": True
                },
                "antivirus_settings": {
                    "real_time_protection": True,
                    "work_mode": True,
                    "financial_protection": True
                },
                "monitoring_settings": {
                    "security_alerts": True,
                    "performance_monitoring": True,
                    "threat_intelligence": True
                }
            }
        }
        
        templates_path = self.project_root / "config" / "templates" / "family_templates.json"
        templates_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(templates_path, 'w', encoding='utf-8') as f:
            json.dump(family_templates, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Семейные шаблоны созданы")
        self.success_count += 1

    def create_business_templates(self):
        """Создание шаблонов для бизнеса"""
        self.log("Создание шаблонов для бизнеса...")
        
        business_templates = {
            "startup": {
                "name": "Стартап",
                "description": "Для небольших стартапов (1-10 сотрудников)",
                "company_size": "1-10",
                "security_level": "medium",
                "features": {
                    "team_management": True,
                    "device_management": True,
                    "basic_compliance": True,
                    "cost_optimized": True
                },
                "vpn_settings": {
                    "team_vpn": True,
                    "office_remote": True,
                    "cost_optimized": True
                },
                "antivirus_settings": {
                    "centralized_management": True,
                    "team_licenses": True,
                    "basic_protection": True
                },
                "monitoring_settings": {
                    "team_dashboard": True,
                    "basic_alerts": True,
                    "usage_analytics": True
                }
            },
            "small_business": {
                "name": "Малый бизнес",
                "description": "Для малого бизнеса (11-50 сотрудников)",
                "company_size": "11-50",
                "security_level": "high",
                "features": {
                    "advanced_team_management": True,
                    "compliance_tools": True,
                    "incident_response": True,
                    "backup_management": True
                },
                "vpn_settings": {
                    "enterprise_vpn": True,
                    "multi_site": True,
                    "advanced_routing": True
                },
                "antivirus_settings": {
                    "enterprise_protection": True,
                    "advanced_threat_detection": True,
                    "centralized_quarantine": True
                },
                "monitoring_settings": {
                    "enterprise_dashboard": True,
                    "advanced_analytics": True,
                    "compliance_reporting": True
                }
            },
            "enterprise": {
                "name": "Корпорация",
                "description": "Для крупных корпораций (50+ сотрудников)",
                "company_size": "50+",
                "security_level": "maximum",
                "features": {
                    "enterprise_management": True,
                    "full_compliance": True,
                    "advanced_analytics": True,
                    "custom_integrations": True
                },
                "vpn_settings": {
                    "enterprise_grade": True,
                    "global_deployment": True,
                    "custom_protocols": True
                },
                "antivirus_settings": {
                    "enterprise_grade": True,
                    "ai_threat_detection": True,
                    "custom_policies": True
                },
                "monitoring_settings": {
                    "enterprise_grade": True,
                    "real_time_analytics": True,
                    "custom_dashboards": True
                }
            }
        }
        
        templates_path = self.project_root / "config" / "templates" / "business_templates.json"
        with open(templates_path, 'w', encoding='utf-8') as f:
            json.dump(business_templates, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Бизнес шаблоны созданы")
        self.success_count += 1

    def create_security_level_templates(self):
        """Создание шаблонов по уровням безопасности"""
        self.log("Создание шаблонов по уровням безопасности...")
        
        security_templates = {
            "basic": {
                "name": "Базовая защита",
                "description": "Минимальная защита для начинающих",
                "security_level": "basic",
                "features": {
                    "basic_vpn": True,
                    "basic_antivirus": True,
                    "simple_monitoring": True
                },
                "complexity": "low",
                "setup_time": "5 минут",
                "maintenance": "минимальная"
            },
            "standard": {
                "name": "Стандартная защита",
                "description": "Сбалансированная защита для большинства",
                "security_level": "standard",
                "features": {
                    "advanced_vpn": True,
                    "advanced_antivirus": True,
                    "real_time_monitoring": True,
                    "backup_protection": True
                },
                "complexity": "medium",
                "setup_time": "15 минут",
                "maintenance": "умеренная"
            },
            "advanced": {
                "name": "Продвинутая защита",
                "description": "Максимальная защита для экспертов",
                "security_level": "advanced",
                "features": {
                    "enterprise_vpn": True,
                    "enterprise_antivirus": True,
                    "advanced_monitoring": True,
                    "threat_intelligence": True,
                    "custom_policies": True
                },
                "complexity": "high",
                "setup_time": "30 минут",
                "maintenance": "активная"
            },
            "maximum": {
                "name": "Максимальная защита",
                "description": "Военная защита для критически важных систем",
                "security_level": "maximum",
                "features": {
                    "military_grade_vpn": True,
                    "military_grade_antivirus": True,
                    "real_time_threat_intelligence": True,
                    "zero_trust_architecture": True,
                    "custom_integrations": True
                },
                "complexity": "expert",
                "setup_time": "60 минут",
                "maintenance": "постоянная"
            }
        }
        
        templates_path = self.project_root / "config" / "templates" / "security_templates.json"
        with open(templates_path, 'w', encoding='utf-8') as f:
            json.dump(security_templates, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Шаблоны безопасности созданы")
        self.success_count += 1

    def create_device_templates(self):
        """Создание шаблонов для разных устройств"""
        self.log("Создание шаблонов для разных устройств...")
        
        device_templates = {
            "mobile_devices": {
                "name": "Мобильные устройства",
                "description": "Оптимизация для смартфонов и планшетов",
                "devices": ["iPhone", "Android", "iPad", "Android Tablet"],
                "features": {
                    "touch_optimized": True,
                    "battery_efficient": True,
                    "offline_mode": True,
                    "push_notifications": True
                },
                "vpn_settings": {
                    "mobile_optimized": True,
                    "battery_saving": True,
                    "auto_reconnect": True
                },
                "antivirus_settings": {
                    "lightweight_scanning": True,
                    "background_protection": True,
                    "app_scanning": True
                }
            },
            "desktop_computers": {
                "name": "Настольные компьютеры",
                "description": "Полнофункциональная защита для ПК",
                "devices": ["Windows PC", "Mac", "Linux PC"],
                "features": {
                    "full_protection": True,
                    "advanced_monitoring": True,
                    "custom_configuration": True,
                    "enterprise_features": True
                },
                "vpn_settings": {
                    "full_featured": True,
                    "advanced_routing": True,
                    "custom_protocols": True
                },
                "antivirus_settings": {
                    "comprehensive_scanning": True,
                    "real_time_protection": True,
                    "advanced_threat_detection": True
                }
            },
            "smart_home": {
                "name": "Умный дом",
                "description": "Защита для IoT устройств",
                "devices": ["Smart TV", "Smart Speaker", "Security Camera", "Smart Lock"],
                "features": {
                    "iot_protection": True,
                    "network_segmentation": True,
                    "device_management": True,
                    "privacy_protection": True
                },
                "vpn_settings": {
                    "iot_vpn": True,
                    "network_wide": True,
                    "device_specific": True
                },
                "antivirus_settings": {
                    "iot_scanning": True,
                    "firmware_protection": True,
                    "network_monitoring": True
                }
            }
        }
        
        templates_path = self.project_root / "config" / "templates" / "device_templates.json"
        with open(templates_path, 'w', encoding='utf-8') as f:
            json.dump(device_templates, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Шаблоны устройств созданы")
        self.success_count += 1

    def create_industry_templates(self):
        """Создание шаблонов для разных отраслей"""
        self.log("Создание шаблонов для разных отраслей...")
        
        industry_templates = {
            "healthcare": {
                "name": "Здравоохранение",
                "description": "Соответствие HIPAA и защита медицинских данных",
                "compliance": ["HIPAA", "GDPR", "152-ФЗ"],
                "features": {
                    "medical_data_protection": True,
                    "patient_privacy": True,
                    "audit_logging": True,
                    "encryption_at_rest": True
                },
                "security_requirements": {
                    "data_encryption": "AES-256",
                    "access_control": "strict",
                    "audit_trail": "comprehensive",
                    "backup_encryption": True
                }
            },
            "finance": {
                "name": "Финансы",
                "description": "Защита финансовых данных и соответствие PCI DSS",
                "compliance": ["PCI DSS", "SOX", "GDPR"],
                "features": {
                    "financial_data_protection": True,
                    "transaction_monitoring": True,
                    "fraud_detection": True,
                    "regulatory_reporting": True
                },
                "security_requirements": {
                    "data_encryption": "AES-256",
                    "access_control": "multi_factor",
                    "audit_trail": "detailed",
                    "real_time_monitoring": True
                }
            },
            "education": {
                "name": "Образование",
                "description": "Защита образовательных данных и соответствие FERPA",
                "compliance": ["FERPA", "COPPA", "GDPR"],
                "features": {
                    "student_data_protection": True,
                    "parental_controls": True,
                    "content_filtering": True,
                    "educational_monitoring": True
                },
                "security_requirements": {
                    "data_encryption": "AES-256",
                    "access_control": "role_based",
                    "audit_trail": "educational",
                    "child_protection": True
                }
            },
            "government": {
                "name": "Государственный сектор",
                "description": "Защита государственных данных и соответствие требованиям",
                "compliance": ["FISMA", "NIST", "152-ФЗ"],
                "features": {
                    "classified_data_protection": True,
                    "national_security": True,
                    "compliance_monitoring": True,
                    "threat_intelligence": True
                },
                "security_requirements": {
                    "data_encryption": "AES-256",
                    "access_control": "clearance_based",
                    "audit_trail": "comprehensive",
                    "threat_monitoring": True
                }
            }
        }
        
        templates_path = self.project_root / "config" / "templates" / "industry_templates.json"
        with open(templates_path, 'w', encoding='utf-8') as f:
            json.dump(industry_templates, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Отраслевые шаблоны созданы")
        self.success_count += 1

    def create_custom_template_builder(self):
        """Создание конструктора пользовательских шаблонов"""
        self.log("Создание конструктора пользовательских шаблонов...")
        
        template_builder = {
            "template_creator": {
                "name": "Конструктор шаблонов ALADDIN",
                "version": "1.0",
                "description": "Инструмент для создания пользовательских шаблонов"
            },
            "template_structure": {
                "basic_info": {
                    "name": "string",
                    "description": "string",
                    "category": "string",
                    "version": "string"
                },
                "security_settings": {
                    "vpn_config": "object",
                    "antivirus_config": "object",
                    "monitoring_config": "object",
                    "access_control": "object"
                },
                "features": {
                    "enabled_features": "array",
                    "disabled_features": "array",
                    "custom_features": "object"
                },
                "compliance": {
                    "standards": "array",
                    "requirements": "object",
                    "audit_settings": "object"
                }
            },
            "template_validation": {
                "required_fields": ["name", "description", "security_settings"],
                "optional_fields": ["features", "compliance", "custom_settings"],
                "validation_rules": {
                    "name_length": "min 3, max 50",
                    "description_length": "min 10, max 200",
                    "security_level": "basic|standard|advanced|maximum"
                }
            },
            "template_export": {
                "formats": ["JSON", "YAML", "XML"],
                "compression": True,
                "encryption": True,
                "signature": True
            }
        }
        
        builder_path = self.project_root / "config" / "templates" / "template_builder.json"
        with open(builder_path, 'w', encoding='utf-8') as f:
            json.dump(template_builder, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Конструктор шаблонов создан")
        self.success_count += 1

    def create_template_manager(self):
        """Создание менеджера шаблонов"""
        self.log("Создание менеджера шаблонов...")
        
        template_manager = {
            "template_manager": {
                "name": "Менеджер шаблонов ALADDIN",
                "version": "1.0",
                "description": "Управление и применение шаблонов конфигурации"
            },
            "template_operations": {
                "list_templates": {
                    "description": "Показать все доступные шаблоны",
                    "parameters": ["category", "security_level", "device_type"]
                },
                "apply_template": {
                    "description": "Применить шаблон к системе",
                    "parameters": ["template_id", "backup_existing", "validate_before_apply"]
                },
                "create_template": {
                    "description": "Создать новый шаблон",
                    "parameters": ["template_data", "validate", "save"]
                },
                "modify_template": {
                    "description": "Изменить существующий шаблон",
                    "parameters": ["template_id", "modifications", "backup_original"]
                },
                "delete_template": {
                    "description": "Удалить шаблон",
                    "parameters": ["template_id", "confirm_deletion"]
                }
            },
            "template_categories": [
                "family",
                "business",
                "security_level",
                "device_type",
                "industry",
                "custom"
            ],
            "template_validation": {
                "schema_validation": True,
                "security_validation": True,
                "compatibility_check": True,
                "backup_creation": True
            }
        }
        
        manager_path = self.project_root / "config" / "templates" / "template_manager.json"
        with open(manager_path, 'w', encoding='utf-8') as f:
            json.dump(template_manager, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Менеджер шаблонов создан")
        self.success_count += 1

    def generate_templates_report(self):
        """Генерация отчета о шаблонах"""
        self.log("Генерация отчета о шаблонах...")
        
        templates_time = time.time() - self.start_time
        
        report = {
            "templates_info": {
                "creator": "Configuration Templates v1.0",
                "creation_date": datetime.now().isoformat(),
                "creation_time_seconds": round(templates_time, 2)
            },
            "statistics": {
                "successful_templates": self.success_count,
                "failed_templates": self.error_count,
                "total_templates": self.success_count + self.error_count,
                "success_rate": round((self.success_count / (self.success_count + self.error_count)) * 100, 2) if (self.success_count + self.error_count) > 0 else 0
            },
            "created_templates": [
                "Семейные шаблоны (3 типа)",
                "Бизнес шаблоны (3 типа)",
                "Шаблоны безопасности (4 уровня)",
                "Шаблоны устройств (3 типа)",
                "Отраслевые шаблоны (4 отрасли)",
                "Конструктор шаблонов",
                "Менеджер шаблонов"
            ],
            "template_files": [
                "config/templates/family_templates.json",
                "config/templates/business_templates.json",
                "config/templates/security_templates.json",
                "config/templates/device_templates.json",
                "config/templates/industry_templates.json",
                "config/templates/template_builder.json",
                "config/templates/template_manager.json"
            ],
            "template_categories": {
                "family": 3,
                "business": 3,
                "security_level": 4,
                "device_type": 3,
                "industry": 4,
                "total_templates": 17
            },
            "templates_log": self.templates_log
        }
        
        report_path = self.project_root / "TEMPLATES_REPORT.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Отчет о шаблонах создан")
        return report

    def run_templates_creation(self):
        """Запуск создания всех шаблонов"""
        print("📋 CONFIGURATION TEMPLATES - ALADDIN SECURITY SYSTEM")
        print("=" * 60)
        print("Создание расширенных шаблонов конфигурации!")
        print("=" * 60)
        print()
        
        # Создание семейных шаблонов
        self.create_family_templates()
        
        # Создание бизнес шаблонов
        self.create_business_templates()
        
        # Создание шаблонов безопасности
        self.create_security_level_templates()
        
        # Создание шаблонов устройств
        self.create_device_templates()
        
        # Создание отраслевых шаблонов
        self.create_industry_templates()
        
        # Создание конструктора шаблонов
        self.create_custom_template_builder()
        
        # Создание менеджера шаблонов
        self.create_template_manager()
        
        # Генерация отчета
        report = self.generate_templates_report()
        
        # Финальный отчет
        templates_time = time.time() - self.start_time
        print()
        print("🎉 СОЗДАНИЕ ШАБЛОНОВ ЗАВЕРШЕНО!")
        print("=" * 60)
        print(f"⏱️ Время создания: {templates_time:.2f} секунд")
        print(f"✅ Успешных шаблонов: {self.success_count}")
        print(f"❌ Ошибок: {self.error_count}")
        print(f"📊 Успешность: {report['statistics']['success_rate']}%")
        print()
        print("📋 СОЗДАННЫЕ ШАБЛОНЫ:")
        print(f"   Семейные: {report['template_categories']['family']} типов")
        print(f"   Бизнес: {report['template_categories']['business']} типов")
        print(f"   Безопасность: {report['template_categories']['security_level']} уровней")
        print(f"   Устройства: {report['template_categories']['device_type']} типов")
        print(f"   Отрасли: {report['template_categories']['industry']} отраслей")
        print(f"   Всего шаблонов: {report['template_categories']['total_templates']}")
        print()
        print("📋 ОТЧЕТ О ШАБЛОНАХ:")
        print(f"   {self.project_root}/TEMPLATES_REPORT.json")
        print()
        
        return self.error_count == 0


def main():
    """Главная функция"""
    templates = ConfigurationTemplates()
    success = templates.run_templates_creation()
    
    if success:
        print("✅ Создание шаблонов завершено успешно!")
        sys.exit(0)
    else:
        print("❌ Создание шаблонов завершено с ошибками!")
        sys.exit(1)


if __name__ == "__main__":
    main()