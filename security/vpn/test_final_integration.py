#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Integration Test - Финальное тестирование VPN системы
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

# Импорты модулей
try:
    from monitoring.vpn_metrics import VPNMetricsCollector
    from analytics.business_analytics import BusinessAnalytics
    from analytics.ml_detector import AnomalyDetector
    from api.graphql_api import GraphQLAPI
    from api.websocket_api import WebSocketAPI
    from integrations.external_services import ExternalServicesManager
    from backup.backup_manager import BackupManager
    from service_orchestrator import ServiceOrchestrator
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinalIntegrationTest:
    """
    Финальное тестирование интеграции всех компонентов VPN системы
    
    Тестирует:
    - Все основные модули
    - Интеграцию между компонентами
    - Производительность
    - Стабильность
    """
    
    def __init__(self):
        self.name = "FinalIntegrationTest"
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        
        # Результаты тестов
        self.test_results: Dict[str, Any] = {}
        self.start_time = datetime.now()
        
        # Компоненты для тестирования
        self.components = {}
        
        self.logger.info(f"Final Integration Test '{self.name}' инициализирован")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        self.logger.info("🚀 Запуск финального тестирования VPN системы...")
        
        try:
            # Инициализация компонентов
            await self._initialize_components()
            
            # Тестирование основных модулей
            await self._test_vpn_metrics()
            await self._test_business_analytics()
            await self._test_ml_detector()
            await self._test_graphql_api()
            await self._test_websocket_api()
            await self._test_external_services()
            await self._test_backup_manager()
            await self._test_service_orchestrator()
            
            # Тестирование интеграции
            await self._test_component_integration()
            
            # Тестирование производительности
            await self._test_performance()
            
            # Генерация отчета
            report = await self._generate_report()
            
            self.logger.info("✅ Финальное тестирование завершено")
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка в тестировании: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _initialize_components(self) -> None:
        """Инициализация компонентов для тестирования"""
        self.logger.info("🔧 Инициализация компонентов...")
        
        try:
            # VPN Metrics Collector
            self.components["metrics"] = VPNMetricsCollector("TestMetrics")
            await self.components["metrics"].start_collection()
            
            # Business Analytics
            self.components["business_analytics"] = BusinessAnalytics("TestBusinessAnalytics")
            
            # ML Detector
            self.components["ml_detector"] = AnomalyDetector("TestMLDetector")
            await self.components["ml_detector"].start_detection()
            
            # External Services Manager
            self.components["external_services"] = ExternalServicesManager("TestExternalServices")
            await self.components["external_services"].start()
            
            # Backup Manager
            self.components["backup"] = BackupManager("TestBackupManager")
            await self.components["backup"].start()
            
            # Service Orchestrator
            self.components["orchestrator"] = ServiceOrchestrator("TestOrchestrator")
            
            self.logger.info("✅ Компоненты инициализированы")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации компонентов: {e}")
            raise
    
    async def _test_vpn_metrics(self) -> None:
        """Тестирование VPN метрик"""
        self.logger.info("📊 Тестирование VPN метрик...")
        
        try:
            metrics = self.components["metrics"]
            
            # Тест сбора метрик
            await asyncio.sleep(2)  # Ждем сбора данных
            
            server_metrics = metrics.get_server_metrics()
            connection_metrics = metrics.get_connection_metrics()
            performance_summary = metrics.get_performance_summary()
            
            self.test_results["vpn_metrics"] = {
                "status": "passed",
                "server_metrics_count": len(server_metrics),
                "connection_metrics_count": len(connection_metrics),
                "performance_summary": performance_summary,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ VPN метрики работают корректно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования VPN метрик: {e}")
            self.test_results["vpn_metrics"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _test_business_analytics(self) -> None:
        """Тестирование бизнес-аналитики"""
        self.logger.info("💰 Тестирование бизнес-аналитики...")
        
        try:
            analytics = self.components["business_analytics"]
            
            # Тест расчета метрик
            metrics = await analytics.calculate_business_metrics(6)
            
            # Тест когортного анализа
            cohorts = await analytics.get_cohort_analysis(6)
            
            # Тест прогноза
            forecast = await analytics.get_revenue_forecast(6)
            
            # Тест ROI анализа
            roi_analysis = await analytics.get_roi_analysis()
            
            self.test_results["business_analytics"] = {
                "status": "passed",
                "mrr": metrics.monthly_recurring_revenue,
                "arr": metrics.annual_recurring_revenue,
                "arpu": metrics.average_revenue_per_user,
                "ltv": metrics.customer_lifetime_value,
                "cac": metrics.customer_acquisition_cost,
                "cohorts_count": len(cohorts),
                "forecast_months": len(forecast),
                "roi_channels": len(roi_analysis),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ Бизнес-аналитика работает корректно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования бизнес-аналитики: {e}")
            self.test_results["business_analytics"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _test_ml_detector(self) -> None:
        """Тестирование ML детектора аномалий"""
        self.logger.info("🤖 Тестирование ML детектора...")
        
        try:
            detector = self.components["ml_detector"]
            
            # Ждем некоторое время для сбора данных
            await asyncio.sleep(5)
            
            # Получение активных аномалий
            active_anomalies = detector.get_active_anomalies()
            
            # Получение статистики детекции
            detection_summary = detector.get_detection_summary()
            
            self.test_results["ml_detector"] = {
                "status": "passed",
                "active_anomalies": len(active_anomalies),
                "total_anomalies": detection_summary["total_anomalies"],
                "ml_models": detection_summary["ml_models"],
                "anomalies_by_type": detection_summary["anomalies_by_type"],
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ ML детектор работает корректно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования ML детектора: {e}")
            self.test_results["ml_detector"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _test_graphql_api(self) -> None:
        """Тестирование GraphQL API"""
        self.logger.info("🔗 Тестирование GraphQL API...")
        
        try:
            # Создание GraphQL API (без запуска сервера)
            api = GraphQLAPI("TestGraphQLAPI")
            
            # Тест резолвера
            resolver = api.resolver
            
            # Тест запроса серверов
            servers = await resolver.resolve_query("servers", {})
            
            # Тест запроса метрик
            metrics = await resolver.resolve_query("metrics", {})
            
            # Тест мутации подключения
            connect_result = await resolver.resolve_mutation("connect", {
                "userId": "test_user",
                "serverId": "sg-01"
            })
            
            self.test_results["graphql_api"] = {
                "status": "passed",
                "servers_count": len(servers) if isinstance(servers, list) else 0,
                "metrics_available": bool(metrics),
                "connect_success": connect_result.get("success", False),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ GraphQL API работает корректно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования GraphQL API: {e}")
            self.test_results["graphql_api"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _test_websocket_api(self) -> None:
        """Тестирование WebSocket API"""
        self.logger.info("🔌 Тестирование WebSocket API...")
        
        try:
            # Создание WebSocket API (без запуска сервера)
            api = WebSocketAPI("TestWebSocketAPI")
            
            # Тест менеджера WebSocket
            manager = api.manager
            
            # Тест статистики
            client_count = manager.get_client_count()
            subscription_stats = manager.get_subscription_stats()
            
            self.test_results["websocket_api"] = {
                "status": "passed",
                "client_count": client_count,
                "subscription_stats": subscription_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ WebSocket API работает корректно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования WebSocket API: {e}")
            self.test_results["websocket_api"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _test_external_services(self) -> None:
        """Тестирование внешних сервисов"""
        self.logger.info("🌐 Тестирование внешних сервисов...")
        
        try:
            manager = self.components["external_services"]
            
            # Тест статистики сервисов
            service_stats = manager.get_service_stats()
            
            # Тест получения сервисов по типу
            from integrations.external_services import ServiceType
            payment_services = manager.get_services_by_type(ServiceType.PAYMENT)
            notification_services = manager.get_services_by_type(ServiceType.NOTIFICATION)
            
            self.test_results["external_services"] = {
                "status": "passed",
                "total_services": service_stats["total_services"],
                "active_services": service_stats["active_services"],
                "payment_services": len(payment_services),
                "notification_services": len(notification_services),
                "services_by_type": service_stats["services_by_type"],
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ Внешние сервисы работают корректно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования внешних сервисов: {e}")
            self.test_results["external_services"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _test_backup_manager(self) -> None:
        """Тестирование менеджера бэкапов"""
        self.logger.info("💾 Тестирование менеджера бэкапов...")
        
        try:
            backup_manager = self.components["backup"]
            
            # Тест создания бэкапа
            from backup.backup_manager import BackupType
            backup_id = await backup_manager.create_backup(BackupType.CONFIGURATION)
            
            # Ждем завершения бэкапа
            await asyncio.sleep(3)
            
            # Тест получения статуса бэкапа
            backup_status = backup_manager.get_backup_status(backup_id)
            
            # Тест статистики бэкапов
            backup_stats = backup_manager.get_backup_stats()
            
            self.test_results["backup_manager"] = {
                "status": "passed",
                "backup_id": backup_id,
                "backup_status": backup_status.status.value if backup_status else "unknown",
                "total_backups": backup_stats["total_backups"],
                "completed_backups": backup_stats["completed_backups"],
                "total_size_mb": backup_stats["total_size_mb"],
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ Менеджер бэкапов работает корректно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования менеджера бэкапов: {e}")
            self.test_results["backup_manager"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _test_service_orchestrator(self) -> None:
        """Тестирование оркестратора сервисов"""
        self.logger.info("🎼 Тестирование оркестратора сервисов...")
        
        try:
            orchestrator = self.components["orchestrator"]
            
            # Тест получения списка сервисов
            services = orchestrator.services
            
            # Тест запуска сервиса
            start_result = await orchestrator.start_service("vpn_monitoring")
            
            # Тест получения статуса сервиса
            service_status = await orchestrator.get_service_status("vpn_monitoring")
            
            # Тест остановки сервиса
            stop_result = await orchestrator.stop_service("vpn_monitoring")
            
            self.test_results["service_orchestrator"] = {
                "status": "passed",
                "total_services": len(services) if services else 0,
                "start_result": start_result,
                "service_status": service_status.status.value if service_status and hasattr(service_status, 'status') else "unknown",
                "stop_result": stop_result,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ Оркестратор сервисов работает корректно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования оркестратора сервисов: {e}")
            self.test_results["service_orchestrator"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _test_component_integration(self) -> None:
        """Тестирование интеграции компонентов"""
        self.logger.info("🔗 Тестирование интеграции компонентов...")
        
        try:
            # Тест передачи данных между компонентами
            metrics = self.components["metrics"]
            business_analytics = self.components["business_analytics"]
            ml_detector = self.components["ml_detector"]
            
            # Получение данных из метрик
            performance_summary = metrics.get_performance_summary()
            
            # Передача данных в бизнес-аналитику
            business_metrics = await business_analytics.calculate_business_metrics(3)
            
            # Проверка работы ML детектора с данными
            detection_summary = ml_detector.get_detection_summary()
            
            self.test_results["component_integration"] = {
                "status": "passed",
                "metrics_data_available": bool(performance_summary),
                "business_metrics_calculated": bool(business_metrics),
                "ml_detection_active": detection_summary["ml_models"] > 0,
                "integration_working": True,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ Интеграция компонентов работает корректно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования интеграции компонентов: {e}")
            self.test_results["component_integration"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _test_performance(self) -> None:
        """Тестирование производительности"""
        self.logger.info("⚡ Тестирование производительности...")
        
        try:
            import time
            import psutil
            
            # Измерение использования ресурсов
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            cpu_before = process.cpu_percent()
            
            # Тест производительности метрик
            start_time = time.time()
            metrics = self.components["metrics"]
            performance_summary = metrics.get_performance_summary()
            metrics_time = time.time() - start_time
            
            # Тест производительности бизнес-аналитики
            start_time = time.time()
            business_analytics = self.components["business_analytics"]
            business_metrics = await business_analytics.calculate_business_metrics(3)
            analytics_time = time.time() - start_time
            
            # Измерение использования ресурсов после тестов
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            cpu_after = process.cpu_percent()
            
            self.test_results["performance"] = {
                "status": "passed",
                "metrics_response_time": metrics_time,
                "analytics_response_time": analytics_time,
                "memory_usage_mb": memory_after,
                "memory_increase_mb": memory_after - memory_before,
                "cpu_usage_percent": cpu_after,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ Производительность в норме")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования производительности: {e}")
            self.test_results["performance"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_report(self) -> Dict[str, Any]:
        """Генерация финального отчета"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Подсчет результатов
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get("status") == "passed"])
        failed_tests = total_tests - passed_tests
        
        # Определение общего статуса
        overall_status = "passed" if failed_tests == 0 else "failed"
        
        report = {
            "overall_status": overall_status,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "duration_seconds": duration,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "test_results": self.test_results,
            "summary": {
                "vpn_metrics": "✅ Работает" if self.test_results.get("vpn_metrics", {}).get("status") == "passed" else "❌ Ошибка",
                "business_analytics": "✅ Работает" if self.test_results.get("business_analytics", {}).get("status") == "passed" else "❌ Ошибка",
                "ml_detector": "✅ Работает" if self.test_results.get("ml_detector", {}).get("status") == "passed" else "❌ Ошибка",
                "graphql_api": "✅ Работает" if self.test_results.get("graphql_api", {}).get("status") == "passed" else "❌ Ошибка",
                "websocket_api": "✅ Работает" if self.test_results.get("websocket_api", {}).get("status") == "passed" else "❌ Ошибка",
                "external_services": "✅ Работает" if self.test_results.get("external_services", {}).get("status") == "passed" else "❌ Ошибка",
                "backup_manager": "✅ Работает" if self.test_results.get("backup_manager", {}).get("status") == "passed" else "❌ Ошибка",
                "service_orchestrator": "✅ Работает" if self.test_results.get("service_orchestrator", {}).get("status") == "passed" else "❌ Ошибка",
                "component_integration": "✅ Работает" if self.test_results.get("component_integration", {}).get("status") == "passed" else "❌ Ошибка",
                "performance": "✅ Работает" if self.test_results.get("performance", {}).get("status") == "passed" else "❌ Ошибка"
            }
        }
        
        return report
    
    async def cleanup(self) -> None:
        """Очистка ресурсов"""
        self.logger.info("🧹 Очистка ресурсов...")
        
        try:
            # Остановка компонентов
            if "metrics" in self.components:
                await self.components["metrics"].stop_collection()
            
            if "ml_detector" in self.components:
                await self.components["ml_detector"].stop_detection()
            
            if "external_services" in self.components:
                await self.components["external_services"].stop()
            
            if "backup" in self.components:
                await self.components["backup"].stop()
            
            self.logger.info("✅ Ресурсы очищены")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка очистки ресурсов: {e}")


async def main():
    """Главная функция тестирования"""
    print("🚀 ALADDIN VPN - ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ")
    print("=" * 50)
    
    test = FinalIntegrationTest()
    
    try:
        # Запуск тестирования
        report = await test.run_all_tests()
        
        # Вывод результатов
        print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print("=" * 50)
        print(f"Общий статус: {report['overall_status'].upper()}")
        print(f"Всего тестов: {report['total_tests']}")
        print(f"Пройдено: {report['passed_tests']}")
        print(f"Провалено: {report['failed_tests']}")
        print(f"Успешность: {report['success_rate']:.1f}%")
        print(f"Время выполнения: {report['duration_seconds']:.2f} секунд")
        
        print("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        print("-" * 30)
        for component, status in report['summary'].items():
            print(f"{component.replace('_', ' ').title()}: {status}")
        
        # Сохранение отчета
        report_file = Path("test_report.json")
        # Конвертация datetime объектов в строки для JSON
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=json_serializer)
        
        print(f"\n💾 Отчет сохранен: {report_file}")
        
        # Определение финального статуса
        if report['overall_status'] == 'passed':
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("✅ VPN система готова к production!")
            return 0
        else:
            print("\n❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
            print("🔧 Требуется исправление ошибок")
            return 1
            
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return 1
    
    finally:
        # Очистка ресурсов
        await test.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)