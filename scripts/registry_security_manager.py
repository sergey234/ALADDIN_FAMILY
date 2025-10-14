#!/usr/bin/env python3
"""
Главный менеджер безопасности реестра функций ALADDIN
Объединяет все системы защиты, валидации, мониторинга и отчётов
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Импорт наших модулей
from registry_protection_system import RegistryProtectionSystem
from registry_format_validator import RegistryFormatValidator
from registry_monitor import RegistryMonitor
from registry_problem_reporter import RegistryProblemReporter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/registry_security_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RegistrySecurityManager:
    """Главный менеджер безопасности реестра функций"""
    
    def __init__(self, registry_path: str = "data/sfm/function_registry.json"):
        self.registry_path = registry_path
        
        # Инициализация всех систем
        self.protection = RegistryProtectionSystem(registry_path)
        self.validator = RegistryFormatValidator(registry_path)
        self.monitor = RegistryMonitor(registry_path)
        self.reporter = RegistryProblemReporter()
        
        logger.info("🛡️ Менеджер безопасности реестра инициализирован")
        logger.info(f"📁 Защищаемый реестр: {registry_path}")
    
    def start_full_protection(self) -> bool:
        """Запуск полной защиты реестра"""
        try:
            logger.info("🚀 Запуск полной защиты реестра")
            
            # 1. Валидация текущего реестра
            logger.info("🔍 Валидация формата реестра...")
            success, registry, errors = self.validator.validate_file()
            
            if not success:
                logger.error(f"❌ Реестр не прошёл валидацию: {len(errors)} ошибок")
                for error in errors:
                    logger.error(f"   {error}")
                return False
            
            if errors:
                logger.warning(f"⚠️ Обнаружено {len(errors)} предупреждений валидации")
                for error in errors:
                    logger.warning(f"   {error}")
            
            # 2. Запуск мониторинга
            logger.info("📊 Запуск мониторинга реестра...")
            if not self.monitor.start_monitoring():
                logger.error("❌ Не удалось запустить мониторинг")
                return False
            
            # 3. Проверка статуса защиты
            protection_status = self.protection.get_registry_status()
            logger.info(f"🛡️ Статус защиты: {protection_status['current_functions_count']} функций под защитой")
            
            logger.info("✅ Полная защита реестра активирована")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска защиты: {e}")
            return False
    
    def stop_protection(self) -> bool:
        """Остановка защиты реестра"""
        try:
            logger.info("⏹️ Остановка защиты реестра")
            
            # Остановка мониторинга
            if not self.monitor.stop_monitoring():
                logger.warning("⚠️ Не удалось корректно остановить мониторинг")
            
            logger.info("✅ Защита реестра остановлена")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки защиты: {e}")
            return False
    
    def safe_registry_update(self, new_registry: Dict[str, Any], force: bool = False) -> bool:
        """Безопасное обновление реестра с проверками"""
        try:
            logger.info("🔄 Безопасное обновление реестра")
            
            # 1. Валидация нового реестра
            logger.info("🔍 Валидация нового реестра...")
            is_valid, errors, fixed_registry = self.validator.validate_registry(new_registry)
            
            if not is_valid:
                logger.error(f"❌ Новый реестр не прошёл валидацию: {len(errors)} ошибок")
                for error in errors:
                    logger.error(f"   {error}")
                return False
            
            if errors:
                logger.warning(f"⚠️ Исправлено {len(errors)} ошибок в новом реестре")
                for error in errors:
                    logger.warning(f"   {error}")
            
            # 2. Защищённая запись
            logger.info("🛡️ Защищённая запись реестра...")
            if not self.protection.protect_registry_write(fixed_registry, force):
                logger.error("❌ Не удалось записать реестр (защита заблокировала)")
                return False
            
            logger.info("✅ Реестр успешно обновлён")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления реестра: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение полного статуса системы"""
        try:
            protection_status = self.protection.get_registry_status()
            monitor_status = self.monitor.get_monitoring_status()
            validation_report = self.validator.get_validation_report()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "registry_path": self.registry_path,
                "protection": protection_status,
                "monitoring": monitor_status,
                "validation": validation_report,
                "system_health": self._calculate_system_health(protection_status, monitor_status, validation_report)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса: {e}")
            return {"error": str(e)}
    
    def _calculate_system_health(self, protection: Dict, monitoring: Dict, validation: Dict) -> Dict[str, Any]:
        """Расчёт здоровья системы"""
        health_score = 100
        
        # Проверка защиты
        if protection.get("functions_lost", 0) > 0:
            health_score -= protection["functions_lost"] * 10
        
        # Проверка мониторинга
        if not monitoring.get("is_monitoring", False):
            health_score -= 20
        
        # Проверка валидации
        if not validation.get("validation_success", True):
            health_score -= 15
        
        # Определение статуса
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 70:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        elif health_score >= 30:
            status = "poor"
        else:
            status = "critical"
        
        return {
            "score": max(0, min(100, health_score)),
            "status": status,
            "recommendations": self._get_health_recommendations(health_score, protection, monitoring, validation)
        }
    
    def _get_health_recommendations(self, score: int, protection: Dict, monitoring: Dict, validation: Dict) -> List[str]:
        """Получение рекомендаций по здоровью системы"""
        recommendations = []
        
        if score < 50:
            recommendations.append("🚨 Критично: Система требует немедленного внимания")
        
        if protection.get("functions_lost", 0) > 0:
            recommendations.append("⚠️ Внимание: Потеряны функции из реестра")
        
        if not monitoring.get("is_monitoring", False):
            recommendations.append("📊 Рекомендация: Запустите мониторинг реестра")
        
        if not validation.get("validation_success", True):
            recommendations.append("🔍 Рекомендация: Исправьте ошибки валидации")
        
        if not recommendations:
            recommendations.append("✅ Система работает стабильно")
        
        return recommendations
    
    def generate_problem_report(self) -> str:
        """Генерация отчёта о проблемах"""
        try:
            logger.info("📋 Генерация отчёта о проблемах")
            report_path = self.reporter.generate_and_save_report()
            
            if report_path:
                logger.info(f"✅ Отчёт сгенерирован: {report_path}")
                return report_path
            else:
                logger.error("❌ Не удалось сгенерировать отчёт")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации отчёта: {e}")
            return ""
    
    def emergency_protection_check(self) -> Dict[str, Any]:
        """Экстренная проверка защиты реестра"""
        try:
            logger.critical("🚨 ЭКСТРЕННАЯ ПРОВЕРКА ЗАЩИТЫ РЕЕСТРА")
            
            # Быстрая проверка всех систем
            protection_status = self.protection.get_registry_status()
            monitor_status = self.monitor.get_monitoring_status()
            validation_report = self.validator.get_validation_report()
            
            # Анализ критических проблем
            critical_issues = []
            
            if protection_status.get("functions_lost", 0) > 0:
                critical_issues.append(f"🚨 КРИТИЧНО: Потеряно {protection_status['functions_lost']} функций")
            
            if not monitor_status.get("is_monitoring", False):
                critical_issues.append("⚠️ ВНИМАНИЕ: Мониторинг не активен")
            
            if not validation_report.get("validation_success", True):
                critical_issues.append("🔍 ПРОБЛЕМА: Ошибки валидации реестра")
            
            if not Path(self.registry_path).exists():
                critical_issues.append("💥 КАТАСТРОФА: Файл реестра не существует")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "critical_issues": critical_issues,
                "protection_status": protection_status,
                "monitoring_status": monitor_status,
                "validation_status": validation_report,
                "emergency_level": "critical" if critical_issues else "normal"
            }
            
        except Exception as e:
            logger.critical(f"💥 КРИТИЧЕСКАЯ ОШИБКА ПРОВЕРКИ: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "critical_issues": [f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}"],
                "emergency_level": "critical"
            }

def main():
    """Тестирование менеджера безопасности реестра"""
    print("🛡️ ТЕСТИРОВАНИЕ МЕНЕДЖЕРА БЕЗОПАСНОСТИ РЕЕСТРА")
    print("=" * 60)
    
    # Инициализация менеджера
    manager = RegistrySecurityManager()
    
    # Запуск полной защиты
    print("🚀 Запуск полной защиты...")
    if manager.start_full_protection():
        print("✅ Защита активирована")
    else:
        print("❌ Ошибка активации защиты")
        return
    
    # Показ статуса системы
    print("\n📊 Статус системы:")
    status = manager.get_system_status()
    
    print(f"   • Путь к реестру: {status['registry_path']}")
    print(f"   • Функций под защитой: {status['protection']['current_functions_count']}")
    print(f"   • Мониторинг активен: {'✅' if status['monitoring']['is_monitoring'] else '❌'}")
    print(f"   • Валидация успешна: {'✅' if status['validation']['validation_success'] else '❌'}")
    
    health = status['system_health']
    print(f"   • Оценка здоровья: {health['score']}/100 ({health['status']})")
    
    # Рекомендации
    if health['recommendations']:
        print(f"\n💡 Рекомендации:")
        for rec in health['recommendations']:
            print(f"   {rec}")
    
    # Экстренная проверка
    print(f"\n🚨 Экстренная проверка:")
    emergency = manager.emergency_protection_check()
    print(f"   • Уровень экстренности: {emergency['emergency_level']}")
    print(f"   • Критических проблем: {len(emergency['critical_issues'])}")
    
    if emergency['critical_issues']:
        for issue in emergency['critical_issues']:
            print(f"   {issue}")
    
    # Генерация отчёта
    print(f"\n📋 Генерация отчёта о проблемах...")
    report_path = manager.generate_problem_report()
    if report_path:
        print(f"✅ Отчёт: {report_path}")
    
    print(f"\n🛡️ Система защиты реестра активна!")
    print(f"📁 Логи: logs/registry_security_manager.log")

if __name__ == "__main__":
    main()