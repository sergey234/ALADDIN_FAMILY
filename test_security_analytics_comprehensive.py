# -*- coding: utf-8 -*-
"""
Комплексное тестирование модуля security_analytics.py
Согласно алгоритму КОМПОНЕНТОВ (НОВЫЙ) пункт 8

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Добавляем путь к модулям
sys.path.append('ALADDIN_NEW')

from security.security_analytics import (
    SecurityMetric,
    SecurityAnalyticsManager,
    AsyncSecurityAnalyticsManager,
    EnhancedSecurityAnalyticsManager,
    MetricType,
    AnalyticsType,
    ValidationError,
    SecurityAnalyticsError,
    MetricNotFoundError,
    InvalidMetricValueError,
    ConfigurationError,
    validate_metric_id,
    validate_metric_value,
    validate_threshold_value,
    validate_config_dict,
    enhanced_error_handler
)


class SecurityAnalyticsTester:
    """Класс для комплексного тестирования модуля security_analytics"""
    
    def __init__(self):
        self.test_results = {
            "classes_tested": [],
            "methods_tested": [],
            "integration_tests": [],
            "errors_found": [],
            "performance_metrics": {},
            "recommendations": []
        }
        self.start_time = datetime.now()
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Логирование результатов теста"""
        timestamp = datetime.now().isoformat()
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": timestamp,
            "details": details
        }
        
        if status == "PASS":
            print(f"✅ {test_name}: {status}")
        elif status == "FAIL":
            print(f"❌ {test_name}: {status} - {details}")
            self.test_results["errors_found"].append(result)
        else:
            print(f"⚠️  {test_name}: {status} - {details}")
            
        self.test_results["methods_tested"].append(result)
        
    def test_validation_functions(self):
        """8.1.1 - Тестирование функций валидации"""
        print("\n🔍 8.1.1 - ТЕСТИРОВАНИЕ ФУНКЦИЙ ВАЛИДАЦИИ")
        
        # Тест validate_metric_id
        try:
            validate_metric_id("test_metric_123")
            self.log_test("validate_metric_id_valid", "PASS")
        except Exception as e:
            self.log_test("validate_metric_id_valid", "FAIL", str(e))
            
        try:
            validate_metric_id("")
            self.log_test("validate_metric_id_empty", "FAIL", "Должна была вызвать исключение")
        except ValidationError:
            self.log_test("validate_metric_id_empty", "PASS")
        except Exception as e:
            self.log_test("validate_metric_id_empty", "FAIL", f"Неправильное исключение: {e}")
            
        # Тест validate_metric_value
        try:
            validate_metric_value(100.0, MetricType.COUNTER)
            self.log_test("validate_metric_value_valid", "PASS")
        except Exception as e:
            self.log_test("validate_metric_value_valid", "FAIL", str(e))
            
        try:
            validate_metric_value(-10.0, MetricType.COUNTER)
            self.log_test("validate_metric_value_negative", "FAIL", "Должна была вызвать исключение")
        except ValidationError:
            self.log_test("validate_metric_value_negative", "PASS")
        except Exception as e:
            self.log_test("validate_metric_value_negative", "FAIL", f"Неправильное исключение: {e}")
            
        # Тест validate_threshold_value
        try:
            validate_threshold_value(0.5)
            self.log_test("validate_threshold_value_valid", "PASS")
        except Exception as e:
            self.log_test("validate_threshold_value_valid", "FAIL", str(e))
            
        # Тест validate_config_dict
        try:
            valid_config = {
                "data_retention_days": 90,
                "analysis_interval": 300,
                "enable_real_time": True
            }
            validate_config_dict(valid_config)
            self.log_test("validate_config_dict_valid", "PASS")
        except Exception as e:
            self.log_test("validate_config_dict_valid", "FAIL", str(e))
            
    def test_security_metric_class(self):
        """8.1.1 - Тестирование класса SecurityMetric"""
        print("\n🔍 8.1.1 - ТЕСТИРОВАНИЕ КЛАССА SecurityMetric")
        
        try:
            # Создание экземпляра
            metric = SecurityMetric(
                metric_id="test_metric",
                name="Test Metric",
                metric_type=MetricType.COUNTER,
                value=100.0,
                unit="count",
                tags={"category": "test"}
            )
            self.log_test("SecurityMetric_creation", "PASS")
            self.test_results["classes_tested"].append("SecurityMetric")
            
            # Тест методов
            methods_to_test = [
                ("update_value", lambda: metric.update_value(150.0)),
                ("set_threshold", lambda: metric.set_threshold("max", 200.0)),
                ("check_thresholds", lambda: metric.check_thresholds()),
                ("to_dict", lambda: metric.to_dict()),
                ("validate", lambda: metric.validate()),
                ("reset", lambda: metric.reset()),
                ("get_statistics", lambda: metric.get_statistics()),
                ("export_data", lambda: metric.export_data()),
                ("add_threshold", lambda: metric.add_threshold("warning", 150.0)),
                ("get_history", lambda: metric.get_history(10)),
                ("clear_history", lambda: metric.clear_history())
            ]
            
            for method_name, method_call in methods_to_test:
                try:
                    result = method_call()
                    self.log_test(f"SecurityMetric_{method_name}", "PASS")
                except Exception as e:
                    self.log_test(f"SecurityMetric_{method_name}", "FAIL", str(e))
                    
            # Тест магических методов
            magic_methods = [
                ("__str__", lambda: str(metric)),
                ("__repr__", lambda: repr(metric)),
                ("__eq__", lambda: metric == metric),
                ("__hash__", lambda: hash(metric)),
                ("__len__", lambda: len(metric)),
                ("__contains__", lambda: 100.0 in metric)
            ]
            
            for method_name, method_call in magic_methods:
                try:
                    result = method_call()
                    self.log_test(f"SecurityMetric_{method_name}", "PASS")
                except Exception as e:
                    self.log_test(f"SecurityMetric_{method_name}", "FAIL", str(e))
                    
        except Exception as e:
            self.log_test("SecurityMetric_creation", "FAIL", str(e))
            
    def test_security_analytics_manager_class(self):
        """8.1.1 - Тестирование класса SecurityAnalyticsManager"""
        print("\n🔍 8.1.1 - ТЕСТИРОВАНИЕ КЛАССА SecurityAnalyticsManager")
        
        try:
            # Создание экземпляра
            config = {
                "data_retention_days": 30,
                "analysis_interval": 60,
                "enable_real_time": True,
                "alert_threshold": 0.8
            }
            manager = SecurityAnalyticsManager("TestManager", config)
            self.log_test("SecurityAnalyticsManager_creation", "PASS")
            self.test_results["classes_tested"].append("SecurityAnalyticsManager")
            
            # Тест инициализации
            try:
                init_result = manager.initialize()
                self.log_test("SecurityAnalyticsManager_initialize", "PASS" if init_result else "FAIL")
            except Exception as e:
                self.log_test("SecurityAnalyticsManager_initialize", "FAIL", str(e))
                
            # Тест основных методов
            methods_to_test = [
                ("add_metric", lambda: manager.add_metric(SecurityMetric("test", "Test", MetricType.COUNTER))),
                ("update_metric", lambda: manager.update_metric("test", 50.0)),
                ("get_metric", lambda: manager.get_metric("test")),
                ("get_metrics_by_category", lambda: manager.get_metrics_by_category("test")),
                ("conduct_threat_analysis", lambda: manager.conduct_threat_analysis()),
                ("conduct_risk_assessment", lambda: manager.conduct_risk_assessment()),
                ("analyze_performance_metrics", lambda: manager.analyze_performance_metrics()),
                ("detect_anomalies", lambda: manager.detect_anomalies()),
                ("generate_insights", lambda: manager.generate_insights()),
                ("get_analytics_dashboard_data", lambda: manager.get_analytics_dashboard_data()),
                ("get_analytics_stats", lambda: manager.get_analytics_stats()),
                ("start", lambda: manager.start()),
                ("stop", lambda: manager.stop()),
                ("get_health_status", lambda: manager.get_health_status()),
                ("backup_data", lambda: manager.backup_data()),
                ("cleanup_old_data", lambda: manager.cleanup_old_data(1)),
                ("get_performance_metrics", lambda: manager.get_performance_metrics()),
                ("validate_integrity", lambda: manager.validate_integrity()),
                ("remove_metric", lambda: manager.remove_metric("test")),
                ("analyze_security_metrics", lambda: manager.analyze_security_metrics()),
                ("get_analytics_summary", lambda: manager.get_analytics_summary()),
                ("export_analytics", lambda: manager.export_analytics()),
                ("import_analytics", lambda: manager.import_analytics({}))
            ]
            
            for method_name, method_call in methods_to_test:
                try:
                    result = method_call()
                    self.log_test(f"SecurityAnalyticsManager_{method_name}", "PASS")
                except Exception as e:
                    self.log_test(f"SecurityAnalyticsManager_{method_name}", "FAIL", str(e))
                    
            # Тест магических методов
            magic_methods = [
                ("__str__", lambda: str(manager)),
                ("__repr__", lambda: repr(manager)),
                ("__eq__", lambda: manager == manager),
                ("__hash__", lambda: hash(manager)),
                ("__len__", lambda: len(manager)),
                ("__contains__", lambda: "test" in manager)
            ]
            
            for method_name, method_call in magic_methods:
                try:
                    result = method_call()
                    self.log_test(f"SecurityAnalyticsManager_{method_name}", "PASS")
                except Exception as e:
                    self.log_test(f"SecurityAnalyticsManager_{method_name}", "FAIL", str(e))
                    
        except Exception as e:
            self.log_test("SecurityAnalyticsManager_creation", "FAIL", str(e))
            
    def test_async_security_analytics_manager_class(self):
        """8.1.1 - Тестирование класса AsyncSecurityAnalyticsManager"""
        print("\n🔍 8.1.1 - ТЕСТИРОВАНИЕ КЛАССА AsyncSecurityAnalyticsManager")
        
        try:
            # Создание экземпляра
            config = {
                "data_retention_days": 30,
                "analysis_interval": 60,
                "enable_real_time": True
            }
            async_manager = AsyncSecurityAnalyticsManager("TestAsyncManager", config)
            self.log_test("AsyncSecurityAnalyticsManager_creation", "PASS")
            self.test_results["classes_tested"].append("AsyncSecurityAnalyticsManager")
            
            # Тест инициализации
            try:
                init_result = async_manager.initialize()
                self.log_test("AsyncSecurityAnalyticsManager_initialize", "PASS" if init_result else "FAIL")
            except Exception as e:
                self.log_test("AsyncSecurityAnalyticsManager_initialize", "FAIL", str(e))
                
            # Тест асинхронных методов
            async def test_async_methods():
                methods_to_test = [
                    ("async_analyze_security_metrics", lambda: async_manager.async_analyze_security_metrics()),
                    ("async_detect_anomalies", lambda: async_manager.async_detect_anomalies()),
                    ("async_generate_insights", lambda: async_manager.async_generate_insights())
                ]
                
                for method_name, method_call in methods_to_test:
                    try:
                        result = await method_call()
                        self.log_test(f"AsyncSecurityAnalyticsManager_{method_name}", "PASS")
                    except Exception as e:
                        self.log_test(f"AsyncSecurityAnalyticsManager_{method_name}", "FAIL", str(e))
                        
            # Запуск асинхронных тестов
            asyncio.run(test_async_methods())
            
            # Тест синхронных методов
            try:
                result = async_manager.get_async_performance_metrics()
                self.log_test("AsyncSecurityAnalyticsManager_get_async_performance_metrics", "PASS")
            except Exception as e:
                self.log_test("AsyncSecurityAnalyticsManager_get_async_performance_metrics", "FAIL", str(e))
            
        except Exception as e:
            self.log_test("AsyncSecurityAnalyticsManager_creation", "FAIL", str(e))
            
    def test_enhanced_security_analytics_manager_class(self):
        """8.1.1 - Тестирование класса EnhancedSecurityAnalyticsManager"""
        print("\n🔍 8.1.1 - ТЕСТИРОВАНИЕ КЛАССА EnhancedSecurityAnalyticsManager")
        
        try:
            # Создание экземпляра
            config = {
                "data_retention_days": 30,
                "analysis_interval": 60,
                "enable_real_time": True,
                "max_cache_size": 100,
                "memory_threshold": 500000,
                "metrics_threshold": 500,
                "error_threshold": 5
            }
            enhanced_manager = EnhancedSecurityAnalyticsManager("TestEnhancedManager", config)
            self.log_test("EnhancedSecurityAnalyticsManager_creation", "PASS")
            self.test_results["classes_tested"].append("EnhancedSecurityAnalyticsManager")
            
            # Тест инициализации
            try:
                init_result = enhanced_manager.initialize()
                self.log_test("EnhancedSecurityAnalyticsManager_initialize", "PASS" if init_result else "FAIL")
            except Exception as e:
                self.log_test("EnhancedSecurityAnalyticsManager_initialize", "FAIL", str(e))
                
            # Тест расширенных методов
            methods_to_test = [
                ("get_cached_statistics", lambda: enhanced_manager.get_cached_statistics("test")),
                ("get_enhanced_performance_metrics", lambda: enhanced_manager.get_enhanced_performance_metrics()),
                ("export_enhanced_analytics", lambda: enhanced_manager.export_enhanced_analytics())
            ]
            
            for method_name, method_call in methods_to_test:
                try:
                    result = method_call()
                    self.log_test(f"EnhancedSecurityAnalyticsManager_{method_name}", "PASS")
                except Exception as e:
                    self.log_test(f"EnhancedSecurityAnalyticsManager_{method_name}", "FAIL", str(e))
                    
        except Exception as e:
            self.log_test("EnhancedSecurityAnalyticsManager_creation", "FAIL", str(e))
            
    def test_integration_between_components(self):
        """8.2 - ПРОВЕРКА ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ"""
        print("\n🔍 8.2 - ПРОВЕРКА ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ")
        
        try:
            # Создание менеджера
            manager = SecurityAnalyticsManager("IntegrationTestManager")
            manager.initialize()
            
            # Создание метрик
            metrics = [
                SecurityMetric("metric1", "Metric 1", MetricType.COUNTER, 100.0, "count", {"category": "test"}),
                SecurityMetric("metric2", "Metric 2", MetricType.GAUGE, 50.0, "percent", {"category": "test"}),
                SecurityMetric("metric3", "Metric 3", MetricType.TIMER, 200.0, "ms", {"category": "performance"})
            ]
            
            # Добавление метрик в менеджер
            for metric in metrics:
                success = manager.add_metric(metric)
                if success:
                    self.log_test(f"Integration_add_metric_{metric.metric_id}", "PASS")
                else:
                    self.log_test(f"Integration_add_metric_{metric.metric_id}", "FAIL", "Не удалось добавить метрику")
                    
            # Тест взаимодействия между компонентами
            integration_tests = [
                ("update_metric_interaction", lambda: manager.update_metric("metric1", 150.0)),
                ("get_metric_interaction", lambda: manager.get_metric("metric1")),
                ("category_filtering", lambda: manager.get_metrics_by_category("test")),
                ("threat_analysis_with_metrics", lambda: manager.conduct_threat_analysis()),
                ("anomaly_detection_with_metrics", lambda: manager.detect_anomalies()),
                ("insight_generation_with_metrics", lambda: manager.generate_insights())
            ]
            
            for test_name, test_func in integration_tests:
                try:
                    result = test_func()
                    self.log_test(f"Integration_{test_name}", "PASS")
                    self.test_results["integration_tests"].append({
                        "test_name": test_name,
                        "status": "PASS",
                        "result_type": type(result).__name__
                    })
                except Exception as e:
                    self.log_test(f"Integration_{test_name}", "FAIL", str(e))
                    self.test_results["integration_tests"].append({
                        "test_name": test_name,
                        "status": "FAIL",
                        "error": str(e)
                    })
                    
            # Тест передачи данных между методами
            try:
                # Обновляем метрику
                manager.update_metric("metric1", 200.0)
                
                # Получаем статистику
                metric_data = manager.get_metric("metric1")
                if metric_data and metric_data["value"] == 200.0:
                    self.log_test("Integration_data_flow", "PASS")
                else:
                    self.log_test("Integration_data_flow", "FAIL", "Данные не передались корректно")
                    
            except Exception as e:
                self.log_test("Integration_data_flow", "FAIL", str(e))
                
            # Тест общих ресурсов и состояния
            try:
                # Проверяем, что метрики сохраняются в менеджере
                if len(manager.metrics) == 3:
                    self.log_test("Integration_shared_state", "PASS")
                else:
                    self.log_test("Integration_shared_state", "FAIL", f"Ожидалось 3 метрики, получено {len(manager.metrics)}")
                    
            except Exception as e:
                self.log_test("Integration_shared_state", "FAIL", str(e))
                
        except Exception as e:
            self.log_test("Integration_setup", "FAIL", str(e))
            
    def test_error_handling(self):
        """8.1.4 - Тестирование обработки ошибок"""
        print("\n🔍 8.1.4 - ТЕСТИРОВАНИЕ ОБРАБОТКИ ОШИБОК")
        
        # Тест ValidationError
        try:
            validate_metric_id("")
            self.log_test("ErrorHandling_ValidationError", "FAIL", "Должна была вызвать ValidationError")
        except ValidationError:
            self.log_test("ErrorHandling_ValidationError", "PASS")
        except Exception as e:
            self.log_test("ErrorHandling_ValidationError", "FAIL", f"Неправильное исключение: {e}")
            
        # Тест SecurityAnalyticsError
        try:
            manager = SecurityAnalyticsManager("ErrorTestManager")
            # Попытка получить несуществующую метрику
            result = manager.get_metric("nonexistent_metric")
            if result is None:
                self.log_test("ErrorHandling_NonexistentMetric", "PASS")
            else:
                self.log_test("ErrorHandling_NonexistentMetric", "FAIL", "Должен был вернуть None")
        except Exception as e:
            self.log_test("ErrorHandling_NonexistentMetric", "FAIL", str(e))
            
        # Тест обработки некорректных параметров
        try:
            metric = SecurityMetric("test", "Test", MetricType.COUNTER, -10.0)  # Отрицательное значение для COUNTER
            self.log_test("ErrorHandling_InvalidValue", "FAIL", "Должна была вызвать ValidationError")
        except ValidationError:
            self.log_test("ErrorHandling_InvalidValue", "PASS")
        except Exception as e:
            self.log_test("ErrorHandling_InvalidValue", "FAIL", f"Неправильное исключение: {e}")
            
    def test_performance_metrics(self):
        """8.1.3 - Тестирование производительности"""
        print("\n🔍 8.1.3 - ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
        
        try:
            manager = SecurityAnalyticsManager("PerformanceTestManager")
            manager.initialize()
            
            # Тест создания множества метрик
            start_time = time.time()
            for i in range(100):
                metric = SecurityMetric(f"perf_metric_{i}", f"Performance Metric {i}", MetricType.COUNTER, i * 10.0)
                manager.add_metric(metric)
            creation_time = time.time() - start_time
            
            self.test_results["performance_metrics"]["metric_creation_time"] = creation_time
            self.log_test("Performance_metric_creation", "PASS", f"100 метрик созданы за {creation_time:.3f}с")
            
            # Тест обновления метрик
            start_time = time.time()
            for i in range(100):
                manager.update_metric(f"perf_metric_{i}", i * 20.0)
            update_time = time.time() - start_time
            
            self.test_results["performance_metrics"]["metric_update_time"] = update_time
            self.log_test("Performance_metric_update", "PASS", f"100 метрик обновлены за {update_time:.3f}с")
            
            # Тест анализа
            start_time = time.time()
            analysis_result = manager.conduct_threat_analysis()
            analysis_time = time.time() - start_time
            
            self.test_results["performance_metrics"]["analysis_time"] = analysis_time
            self.log_test("Performance_analysis", "PASS", f"Анализ выполнен за {analysis_time:.3f}с")
            
        except Exception as e:
            self.log_test("Performance_testing", "FAIL", str(e))
            
    def generate_comprehensive_report(self):
        """8.3 - ГЕНЕРАЦИЯ ОТЧЕТА О СОСТОЯНИИ"""
        print("\n📊 8.3 - ГЕНЕРАЦИЯ ОТЧЕТА О СОСТОЯНИИ")
        
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        # 8.3.1 - Список всех классов и их методов
        classes_info = {
            "SecurityMetric": {
                "methods": [
                    "update_value", "set_threshold", "check_thresholds", "to_dict",
                    "validate", "reset", "get_statistics", "export_data", "import_data",
                    "add_threshold", "get_history", "clear_history"
                ],
                "magic_methods": ["__str__", "__repr__", "__eq__", "__hash__", "__len__", "__contains__"]
            },
            "SecurityAnalyticsManager": {
                "methods": [
                    "initialize", "add_metric", "update_metric", "get_metric",
                    "get_metrics_by_category", "conduct_threat_analysis", "conduct_risk_assessment",
                    "analyze_performance_metrics", "detect_anomalies", "generate_insights",
                    "get_analytics_dashboard_data", "get_analytics_stats", "start", "stop",
                    "get_health_status", "backup_data", "restore_data", "cleanup_old_data",
                    "get_performance_metrics", "validate_integrity", "remove_metric",
                    "analyze_security_metrics", "get_analytics_summary", "export_analytics", "import_analytics"
                ],
                "magic_methods": ["__str__", "__repr__", "__eq__", "__hash__", "__len__", "__contains__"]
            },
            "AsyncSecurityAnalyticsManager": {
                "methods": [
                    "async_analyze_security_metrics", "async_detect_anomalies", "async_generate_insights",
                    "get_async_performance_metrics"
                ]
            },
            "EnhancedSecurityAnalyticsManager": {
                "methods": [
                    "get_cached_statistics", "get_enhanced_performance_metrics", "export_enhanced_analytics"
                ]
            }
        }
        
        # 8.3.2 - Статус каждого метода
        method_status = {}
        for test_result in self.test_results["methods_tested"]:
            test_name = test_result["test_name"]
            status = test_result["status"]
            method_status[test_name] = status
            
        # 8.3.3 - Статистика по исправлениям
        total_tests = len(self.test_results["methods_tested"])
        passed_tests = len([t for t in self.test_results["methods_tested"] if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results["methods_tested"] if t["status"] == "FAIL"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 8.3.4 - Рекомендации по улучшению
        recommendations = []
        
        if success_rate < 90:
            recommendations.append("Улучшить обработку ошибок и валидацию параметров")
            
        if failed_tests > 0:
            recommendations.append("Исправить ошибки в методах с статусом FAIL")
            
        if "async" not in str(self.test_results["classes_tested"]):
            recommendations.append("Добавить больше асинхронных методов для улучшения производительности")
            
        recommendations.extend([
            "Добавить больше unit-тестов для покрытия edge cases",
            "Улучшить документацию методов",
            "Добавить метрики производительности в реальном времени",
            "Реализовать автоматическое масштабирование на основе нагрузки"
        ])
        
        # Генерация отчета
        report = {
            "test_summary": {
                "total_time_seconds": total_time,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate_percent": success_rate,
                "classes_tested": self.test_results["classes_tested"],
                "integration_tests_passed": len([t for t in self.test_results["integration_tests"] if t["status"] == "PASS"])
            },
            "classes_analysis": classes_info,
            "method_status": method_status,
            "performance_metrics": self.test_results["performance_metrics"],
            "errors_found": self.test_results["errors_found"],
            "recommendations": recommendations,
            "test_timestamp": end_time.isoformat()
        }
        
        # Сохранение отчета
        with open("security_analytics_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print(f"\n📈 СТАТИСТИКА ТЕСТИРОВАНИЯ:")
        print(f"   Общее время: {total_time:.2f} секунд")
        print(f"   Всего тестов: {total_tests}")
        print(f"   Успешных: {passed_tests}")
        print(f"   Неудачных: {failed_tests}")
        print(f"   Процент успеха: {success_rate:.1f}%")
        print(f"   Классов протестировано: {len(self.test_results['classes_tested'])}")
        
        print(f"\n🔧 РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
            
        return report
        
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ SECURITY_ANALYTICS.PY")
        print("=" * 80)
        
        # 8.1 - ПОЛНЫЙ ТЕСТ ВСЕХ КЛАССОВ И МЕТОДОВ
        self.test_validation_functions()
        self.test_security_metric_class()
        self.test_security_analytics_manager_class()
        self.test_async_security_analytics_manager_class()
        self.test_enhanced_security_analytics_manager_class()
        
        # 8.2 - ПРОВЕРКА ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ
        self.test_integration_between_components()
        
        # 8.1.4 - ТЕСТИРОВАНИЕ ОБРАБОТКИ ОШИБОК
        self.test_error_handling()
        
        # 8.1.3 - ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ
        self.test_performance_metrics()
        
        # 8.3 - ГЕНЕРАЦИЯ ОТЧЕТА
        report = self.generate_comprehensive_report()
        
        print("\n" + "=" * 80)
        print("✅ КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print(f"📄 Отчет сохранен в: security_analytics_test_report.json")
        
        return report


def main():
    """Главная функция для запуска тестирования"""
    tester = SecurityAnalyticsTester()
    report = tester.run_all_tests()
    return report


if __name__ == "__main__":
    main()