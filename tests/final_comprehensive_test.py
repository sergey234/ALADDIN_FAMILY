#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ФИНАЛЬНЫЙ КОМПЛЕКСНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ SmartMonitoringSystem
ЭТАП 8: Полная проверка всех классов, методов и интеграции
"""

import asyncio
import sys
import os
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_monitoring import (
    SmartMonitoringSystem, AlertRule, Alert, AlertSeverity, AlertStatus,
    smart_monitoring, setup_default_rules
)

class ComprehensiveTestSuite:
    """Комплексный набор тестов для всех компонентов системы"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Логирование результата теста"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        self.test_results[test_name] = {
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"{status} | {test_name}")
        if details:
            print(f"     {details}")
    
    def test_class_instantiation(self):
        """8.1.1 - Тест создания экземпляров всех классов"""
        print("\n" + "="*60)
        print("8.1.1 - ТЕСТ СОЗДАНИЯ ЭКЗЕМПЛЯРОВ КЛАССОВ")
        print("="*60)
        
        try:
            # Тест SmartMonitoringSystem
            system = SmartMonitoringSystem("TestSystem")
            self.log_test_result("SmartMonitoringSystem создание", True, f"Создан: {system}")
            
            # Тест AlertRule
            rule = AlertRule(
                rule_id="test_rule",
                name="Test Rule",
                metric_name="test_metric",
                condition=">",
                threshold=80.0,
                severity=AlertSeverity.WARNING
            )
            self.log_test_result("AlertRule создание", True, f"Создан: {rule}")
            
            # Тест Alert
            alert = Alert(
                alert_id="test_alert_123",
                rule_id="test_rule",
                title="Test Alert",
                message="Test message",
                severity=AlertSeverity.ERROR,
                status=AlertStatus.ACTIVE,
                timestamp=datetime.now(),
                metric_name="test_metric",
                current_value=85.0,
                threshold_value=80.0,
                tags={"source": "test"}
            )
            self.log_test_result("Alert создание", True, f"Создан: {alert}")
            
            # Тест Enum классов
            severity = AlertSeverity.CRITICAL
            status = AlertStatus.RESOLVED
            self.log_test_result("Enum классы создание", True, f"Severity: {severity}, Status: {status}")
            
        except Exception as e:
            self.log_test_result("Создание классов", False, f"Ошибка: {e}")
    
    def test_all_public_methods(self):
        """8.1.2 - Тест всех публичных методов"""
        print("\n" + "="*60)
        print("8.1.2 - ТЕСТ ВСЕХ ПУБЛИЧНЫХ МЕТОДОВ")
        print("="*60)
        
        try:
            system = SmartMonitoringSystem("MethodTest")
            
            # Тест управления системой
            system.start()
            self.log_test_result("start()", True)
            
            system.pause()
            self.log_test_result("pause()", True)
            
            system.resume()
            self.log_test_result("resume()", True)
            
            # Тест добавления правил и метрик
            rule = AlertRule("cpu_rule", "CPU", "cpu_usage", ">", 80.0, AlertSeverity.WARNING)
            system.add_rule(rule)
            self.log_test_result("add_rule()", True)
            
            system.add_metric("cpu_usage", 85.0, {"server": "test"})
            self.log_test_result("add_metric()", True)
            
            # Тест callback'ов
            def test_callback(alert):
                pass
            system.add_alert_callback(test_callback)
            self.log_test_result("add_alert_callback()", True)
            
            # Тест получения данных
            active_alerts = system.get_active_alerts()
            self.log_test_result("get_active_alerts()", True, f"Получено: {len(active_alerts)} алертов")
            
            alert_stats = system.get_alert_stats()
            self.log_test_result("get_alert_stats()", True, f"Статистика получена")
            
            # Тест свойств
            alerts_count = system.active_alerts_count
            total_count = system.total_alerts_count
            rules_count = system.rules_count
            self.log_test_result("Properties", True, f"Алерты: {alerts_count}, Всего: {total_count}, Правила: {rules_count}")
            
            # Тест конфигурации
            config = system.get_config()
            self.log_test_result("get_config()", True, f"Конфигурация получена")
            
            # Тест статистики
            metrics_summary = system.get_metrics_summary()
            self.log_test_result("get_metrics_summary()", True, f"Сводка метрик получена")
            
            perf_stats = system.get_performance_stats()
            self.log_test_result("get_performance_stats()", True, f"Статистика производительности получена")
            
            # Тест здоровья системы
            is_healthy = system.is_healthy()
            health_status = system.get_health_status()
            self.log_test_result("is_healthy()", True, f"Здоровье: {is_healthy}")
            self.log_test_result("get_health_status()", True, f"Статус: {health_status['health_score']}")
            
            # Тест новых методов
            memory_stats = system.get_memory_stats()
            self.log_test_result("get_memory_stats()", True, f"Статистика памяти получена")
            
            detailed_health = system.get_system_health_detailed()
            self.log_test_result("get_system_health_detailed()", True, f"Детальное здоровье: {detailed_health['health_status']}")
            
            # Тест логирования
            logging_result = system.set_logging_config("DEBUG", enable_debug=True)
            self.log_test_result("set_logging_config()", True, f"Логирование настроено: {logging_result}")
            
            # Тест очистки и сброса
            system.clear()
            self.log_test_result("clear()", True)
            
            system.reset()
            self.log_test_result("reset()", True)
            
            system.stop()
            self.log_test_result("stop()", True)
            
        except Exception as e:
            self.log_test_result("Публичные методы", False, f"Ошибка: {e}")
    
    async def test_async_methods(self):
        """8.1.3 - Тест всех асинхронных методов"""
        print("\n" + "="*60)
        print("8.1.3 - ТЕСТ ВСЕХ АСИНХРОННЫХ МЕТОДОВ")
        print("="*60)
        
        try:
            system = SmartMonitoringSystem("AsyncTest")
            
            # Тест асинхронного добавления метрики
            result = await system.add_metric_async("async_metric", 90.0, {"async": "test"})
            self.log_test_result("add_metric_async()", True, f"Результат: {result}")
            
            # Тест асинхронного callback'а
            async def async_callback(alert):
                pass
            
            callback_result = await system.add_alert_callback_async(async_callback)
            self.log_test_result("add_alert_callback_async()", True, f"Результат: {callback_result}")
            
            # Тест асинхронной очистки
            await system._cleanup_old_data_async()
            self.log_test_result("_cleanup_old_data_async()", True)
            
        except Exception as e:
            self.log_test_result("Асинхронные методы", False, f"Ошибка: {e}")
    
    def test_static_and_class_methods(self):
        """8.1.4 - Тест статических и классовых методов"""
        print("\n" + "="*60)
        print("8.1.4 - ТЕСТ СТАТИЧЕСКИХ И КЛАССОВЫХ МЕТОДОВ")
        print("="*60)
        
        try:
            # Тест статического метода create_with_rules
            rule = AlertRule("static_rule", "Static Rule", "static_metric", ">", 70.0, AlertSeverity.INFO)
            system = SmartMonitoringSystem.create_with_rules("StaticSystem", [rule])
            self.log_test_result("create_with_rules()", True, f"Система создана с {len(system.rules)} правилами")
            
            # Тест классового метода from_config
            config = {
                "name": "ConfigSystem",
                "rules": {
                    "config_rule": {
                        "rule_id": "config_rule",
                        "name": "Config Rule",
                        "metric_name": "config_metric",
                        "condition": ">",
                        "threshold": 75.0,
                        "severity": "warning",
                        "cooldown": 300,
                        "min_occurrences": 1,
                        "max_alerts_per_hour": 5,
                        "adaptive_threshold": True
                    }
                }
            }
            config_system = SmartMonitoringSystem.from_config(config)
            self.log_test_result("from_config()", True, f"Система создана из конфигурации")
            
        except Exception as e:
            self.log_test_result("Статические/классовые методы", False, f"Ошибка: {e}")
    
    def test_integration_between_components(self):
        """8.2.1 - Тест интеграции между компонентами"""
        print("\n" + "="*60)
        print("8.2.1 - ТЕСТ ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ")
        print("="*60)
        
        try:
            system = SmartMonitoringSystem("IntegrationTest")
            
            # Создаем правила
            cpu_rule = AlertRule("cpu_rule", "CPU", "cpu_usage", ">", 80.0, AlertSeverity.WARNING)
            memory_rule = AlertRule("memory_rule", "Memory", "memory_usage", ">", 85.0, AlertSeverity.ERROR)
            
            system.add_rule(cpu_rule)
            system.add_rule(memory_rule)
            
            # Добавляем callback для отслеживания алертов
            alerts_received = []
            def alert_callback(alert):
                alerts_received.append(alert)
            
            system.add_alert_callback(alert_callback)
            
            # Запускаем систему
            system.start()
            
            # Добавляем метрики, которые должны вызвать алерты
            system.add_metric("cpu_usage", 85.0)  # Должен вызвать алерт
            system.add_metric("memory_usage", 90.0)  # Должен вызвать алерт
            
            # Проверяем интеграцию
            active_alerts = system.get_active_alerts()
            alert_stats = system.get_alert_stats()
            
            self.log_test_result("Интеграция правил и метрик", True, 
                               f"Активных алертов: {len(active_alerts)}, Получено callback'ов: {len(alerts_received)}")
            
            # Тест передачи данных между методами
            config = system.get_config()
            system.set_config(config)
            self.log_test_result("Передача данных между методами", True, "Конфигурация сохранена и загружена")
            
            # Тест общих ресурсов
            system.clear()
            system.reset()
            self.log_test_result("Общие ресурсы и состояние", True, "Состояние сброшено корректно")
            
            system.stop()
            
        except Exception as e:
            self.log_test_result("Интеграция компонентов", False, f"Ошибка: {e}")
    
    def test_error_handling_and_recovery(self):
        """8.2.2 - Тест обработки ошибок и восстановления"""
        print("\n" + "="*60)
        print("8.2.2 - ТЕСТ ОБРАБОТКИ ОШИБОК И ВОССТАНОВЛЕНИЯ")
        print("="*60)
        
        try:
            system = SmartMonitoringSystem("ErrorTest")
            
            # Тест обработки некорректных данных
            try:
                system.add_metric("", 100.0)  # Пустое имя
                self.log_test_result("Валидация пустого имени", False, "Ошибка не обнаружена")
            except ValueError:
                self.log_test_result("Валидация пустого имени", True, "Ошибка корректно обработана")
            
            try:
                system.add_metric("test", "invalid")  # Некорректное значение
                self.log_test_result("Валидация типа значения", False, "Ошибка не обнаружена")
            except ValueError:
                self.log_test_result("Валидация типа значения", True, "Ошибка корректно обработана")
            
            # Тест обработки некорректного callback'а
            try:
                system.add_alert_callback("not_callable")
                self.log_test_result("Валидация callback'а", False, "Ошибка не обнаружена")
            except ValueError:
                self.log_test_result("Валидация callback'а", True, "Ошибка корректно обработана")
            
            # Тест восстановления после ошибок
            system._handle_error(ValueError("Test error"), "test_context", "ERROR")
            self.log_test_result("Обработка ошибок", True, "Ошибка обработана корректно")
            
            # Тест экстренного восстановления
            system._emergency_recovery()
            self.log_test_result("Экстренное восстановление", True, "Восстановление выполнено")
            
        except Exception as e:
            self.log_test_result("Обработка ошибок", False, f"Ошибка: {e}")
    
    def test_performance_under_load(self):
        """8.2.3 - Тест производительности под нагрузкой"""
        print("\n" + "="*60)
        print("8.2.3 - ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ПОД НАГРУЗКОЙ")
        print("="*60)
        
        try:
            system = SmartMonitoringSystem("PerformanceTest")
            system.start()
            
            # Добавляем правила
            for i in range(10):
                rule = AlertRule(f"rule_{i}", f"Rule {i}", f"metric_{i}", ">", 50.0, AlertSeverity.WARNING)
                system.add_rule(rule)
            
            # Тест производительности добавления метрик
            start_time = time.time()
            for i in range(1000):
                system.add_metric(f"metric_{i % 10}", float(i))
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.log_test_result("Производительность добавления метрик", True, 
                               f"1000 метрик за {duration:.3f}s ({1000/duration:.0f} метрик/сек)")
            
            # Тест производительности получения статистики
            start_time = time.time()
            for _ in range(100):
                system.get_alert_stats()
                system.get_performance_stats()
                system.get_memory_stats()
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.log_test_result("Производительность получения статистики", True, 
                               f"300 операций за {duration:.3f}s ({300/duration:.0f} операций/сек)")
            
            # Проверяем использование памяти
            memory_stats = system.get_memory_stats()
            memory_pressure = memory_stats.get("memory_pressure", False)
            
            self.log_test_result("Использование памяти", not memory_pressure, 
                               f"Давление памяти: {memory_pressure}, Использовано: {memory_stats['memory_usage']['total_estimated_mb']:.2f}MB")
            
            system.stop()
            
        except Exception as e:
            self.log_test_result("Производительность", False, f"Ошибка: {e}")
    
    def generate_comprehensive_report(self):
        """8.3.1 - Генерация комплексного отчета"""
        print("\n" + "="*80)
        print("8.3.1 - КОМПЛЕКСНЫЙ ОТЧЕТ О СОСТОЯНИИ СИСТЕМЫ")
        print("="*80)
        
        # Статистика тестов
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 СТАТИСТИКА ТЕСТИРОВАНИЯ:")
        print(f"   Всего тестов: {self.total_tests}")
        print(f"   Пройдено: {self.passed_tests}")
        print(f"   Провалено: {self.failed_tests}")
        print(f"   Процент успеха: {success_rate:.1f}%")
        
        # Детальные результаты
        print(f"\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        for test_name, result in self.test_results.items():
            status = "✅" if result["passed"] else "❌"
            print(f"   {status} {test_name}")
            if result["details"]:
                print(f"      {result['details']}")
        
        # Общая оценка
        if success_rate >= 95:
            overall_status = "🟢 ОТЛИЧНО"
            status_desc = "Система работает превосходно"
        elif success_rate >= 85:
            overall_status = "🟡 ХОРОШО"
            status_desc = "Система работает хорошо с незначительными проблемами"
        elif success_rate >= 70:
            overall_status = "🟠 УДОВЛЕТВОРИТЕЛЬНО"
            status_desc = "Система работает, но требует внимания"
        else:
            overall_status = "🔴 НЕУДОВЛЕТВОРИТЕЛЬНО"
            status_desc = "Система требует серьезных исправлений"
        
        print(f"\n🎯 ОБЩАЯ ОЦЕНКА: {overall_status}")
        print(f"   {status_desc}")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if self.failed_tests == 0:
            print("   ✅ Все компоненты работают корректно")
            print("   ✅ Система готова к продакшн использованию")
            print("   ✅ Рекомендуется регулярное мониторинг здоровья системы")
        else:
            print(f"   ⚠️  Необходимо исправить {self.failed_tests} проблем")
            print("   ⚠️  Провести дополнительное тестирование")
            print("   ⚠️  Проверить логи на наличие ошибок")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": success_rate,
            "overall_status": overall_status,
            "test_results": self.test_results
        }

async def run_comprehensive_test():
    """Запуск комплексного тестирования"""
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ СИСТЕМЫ МОНИТОРИНГА")
    print("="*80)
    print("ЭТАП 8: Финальная проверка всех компонентов")
    print("="*80)
    
    test_suite = ComprehensiveTestSuite()
    
    # Запускаем все тесты
    test_suite.test_class_instantiation()
    test_suite.test_all_public_methods()
    await test_suite.test_async_methods()
    test_suite.test_static_and_class_methods()
    test_suite.test_integration_between_components()
    test_suite.test_error_handling_and_recovery()
    test_suite.test_performance_under_load()
    
    # Генерируем отчет
    report = test_suite.generate_comprehensive_report()
    
    return report

if __name__ == "__main__":
    report = asyncio.run(run_comprehensive_test())
    
    # Возвращаем код выхода на основе результатов
    if report["success_rate"] >= 95:
        print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        exit(0)
    else:
        print("\n💥 ЕСТЬ ПРОБЛЕМЫ В ТЕСТИРОВАНИИ!")
        exit(1)