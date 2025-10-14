# -*- coding: utf-8 -*-
"""
Тесты для KubernetesOrchestrator
"""

import unittest
import time
import threading
from datetime import datetime
from unittest.mock import patch, MagicMock

from security.orchestration.kubernetes_orchestrator import (
    KubernetesOrchestrator, PodStatus, ServiceStatus, ScalingStrategy,
    PodInfo, ServiceInfo, NodeInfo, OrchestrationMetrics
)


class TestKubernetesOrchestrator(unittest.TestCase):
    """Тесты для KubernetesOrchestrator"""

    def setUp(self):
        """Настройка тестов"""
        self.orchestrator = KubernetesOrchestrator("TestK8sOrchestrator")

    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'orchestrator'):
            self.orchestrator.stop()

    def test_initialization(self):
        """Тест инициализации"""
        result = self.orchestrator.initialize()
        self.assertTrue(result)
        self.assertEqual(self.orchestrator.status.value, "running")

    def test_stop(self):
        """Тест остановки"""
        self.orchestrator.initialize()
        result = self.orchestrator.stop()
        self.assertTrue(result)
        self.assertEqual(self.orchestrator.status.value, "stopped")

    def test_deploy_service(self):
        """Тест развертывания сервиса"""
        self.orchestrator.initialize()

        service_config = {
            "name": "test-service",
            "replicas": 2,
            "cpu_limit": 0.5,
            "memory_limit": 1.0,
            "scaling_strategy": "auto",
            "labels": {"app": "test"}
        }

        result = self.orchestrator.deploy_service(service_config)
        self.assertTrue(result)

        # Проверяем что сервис создан
        services = self.orchestrator.get_services()
        self.assertGreater(len(services), 0)

        # Проверяем что поды созданы
        pods = self.orchestrator.get_pods()
        self.assertGreater(len(pods), 0)

    def test_scale_service(self):
        """Тест масштабирования сервиса"""
        self.orchestrator.initialize()

        # Сначала развертываем сервис
        service_config = {
            "name": "test-service",
            "replicas": 1,
            "cpu_limit": 0.5,
            "memory_limit": 1.0
        }
        self.orchestrator.deploy_service(service_config)

        # Получаем ID сервиса
        services = self.orchestrator.get_services()
        self.assertGreater(len(services), 0)
        service_id = services[0].service_id

        # Масштабируем до 3 реплик
        result = self.orchestrator.scale_service(service_id, 3)
        self.assertTrue(result)

        # Проверяем что количество подов увеличилось
        pods = self.orchestrator.get_pods(service_id)
        self.assertEqual(len(pods), 3)

    def test_scale_service_down(self):
        """Тест уменьшения масштаба сервиса"""
        self.orchestrator.initialize()

        # Развертываем сервис с 3 репликами
        service_config = {
            "name": "test-service",
            "replicas": 3,
            "cpu_limit": 0.5,
            "memory_limit": 1.0
        }
        self.orchestrator.deploy_service(service_config)

        # Получаем ID сервиса
        services = self.orchestrator.get_services()
        service_id = services[0].service_id

        # Масштабируем до 1 реплики
        result = self.orchestrator.scale_service(service_id, 1)
        self.assertTrue(result)

        # Проверяем что количество подов уменьшилось
        pods = self.orchestrator.get_pods(service_id)
        self.assertEqual(len(pods), 1)

    def test_get_pods(self):
        """Тест получения подов"""
        self.orchestrator.initialize()

        # Развертываем сервис
        service_config = {
            "name": "test-service",
            "replicas": 2
        }
        self.orchestrator.deploy_service(service_config)

        # Получаем все поды
        all_pods = self.orchestrator.get_pods()
        self.assertGreater(len(all_pods), 0)

        # Получаем поды конкретного сервиса
        services = self.orchestrator.get_services()
        service_id = services[0].service_id
        service_pods = self.orchestrator.get_pods(service_id)
        self.assertGreater(len(service_pods), 0)

    def test_get_services(self):
        """Тест получения сервисов"""
        self.orchestrator.initialize()

        # Развертываем несколько сервисов
        service_configs = [
            {"name": "service-1", "replicas": 1},
            {"name": "service-2", "replicas": 2}
        ]

        for config in service_configs:
            self.orchestrator.deploy_service(config)

        services = self.orchestrator.get_services()
        self.assertEqual(len(services), 2)

    def test_get_nodes(self):
        """Тест получения нод"""
        self.orchestrator.initialize()

        nodes = self.orchestrator.get_nodes()
        self.assertGreater(len(nodes), 0)

        # Проверяем структуру ноды
        node = nodes[0]
        self.assertIsInstance(node, NodeInfo)
        self.assertIsNotNone(node.node_id)
        self.assertIsNotNone(node.name)

    def test_get_orchestrator_status(self):
        """Тест получения статуса оркестратора"""
        self.orchestrator.initialize()

        status = self.orchestrator.get_orchestrator_status()
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("total_pods", status)
        self.assertIn("total_services", status)
        self.assertIn("total_nodes", status)
        self.assertIn("metrics", status)
        self.assertIn("statistics", status)
        self.assertIn("config", status)

    def test_pod_info_creation(self):
        """Тест создания информации о поде"""
        pod = PodInfo(
            pod_id="test-pod",
            name="test-pod-name",
            namespace="default",
            status=PodStatus.RUNNING,
            cpu_usage=0.5,
            memory_usage=0.3
        )

        self.assertEqual(pod.pod_id, "test-pod")
        self.assertEqual(pod.name, "test-pod-name")
        self.assertEqual(pod.status, PodStatus.RUNNING)
        self.assertEqual(pod.cpu_usage, 0.5)
        self.assertEqual(pod.memory_usage, 0.3)

    def test_pod_info_to_dict(self):
        """Тест преобразования информации о поде в словарь"""
        pod = PodInfo(
            pod_id="test-pod",
            name="test-pod-name",
            namespace="default",
            status=PodStatus.RUNNING,
            cpu_usage=0.5,
            memory_usage=0.3
        )

        data = pod.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["pod_id"], "test-pod")
        self.assertEqual(data["status"], "running")

    def test_service_info_creation(self):
        """Тест создания информации о сервисе"""
        service = ServiceInfo(
            service_id="test-service",
            name="test-service-name",
            namespace="default",
            status=ServiceStatus.ACTIVE,
            replicas=3,
            desired_replicas=3,
            cpu_limit=1.0,
            memory_limit=2.0,
            scaling_strategy=ScalingStrategy.AUTO
        )

        self.assertEqual(service.service_id, "test-service")
        self.assertEqual(service.name, "test-service-name")
        self.assertEqual(service.status, ServiceStatus.ACTIVE)
        self.assertEqual(service.replicas, 3)
        self.assertEqual(service.scaling_strategy, ScalingStrategy.AUTO)

    def test_service_info_to_dict(self):
        """Тест преобразования информации о сервисе в словарь"""
        service = ServiceInfo(
            service_id="test-service",
            name="test-service-name",
            namespace="default",
            status=ServiceStatus.ACTIVE,
            replicas=3,
            desired_replicas=3,
            cpu_limit=1.0,
            memory_limit=2.0,
            scaling_strategy=ScalingStrategy.AUTO
        )

        data = service.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["service_id"], "test-service")
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["scaling_strategy"], "auto")

    def test_node_info_creation(self):
        """Тест создания информации о ноде"""
        node = NodeInfo(
            node_id="test-node",
            name="test-node-name",
            status="Ready",
            cpu_capacity=4.0,
            memory_capacity=8.0,
            cpu_allocatable=3.5,
            memory_allocatable=7.0,
            cpu_usage=0.5,
            memory_usage=0.3,
            pod_count=5
        )

        self.assertEqual(node.node_id, "test-node")
        self.assertEqual(node.name, "test-node-name")
        self.assertEqual(node.status, "Ready")
        self.assertEqual(node.cpu_capacity, 4.0)
        self.assertEqual(node.memory_capacity, 8.0)

    def test_node_info_to_dict(self):
        """Тест преобразования информации о ноде в словарь"""
        node = NodeInfo(
            node_id="test-node",
            name="test-node-name",
            status="Ready",
            cpu_capacity=4.0,
            memory_capacity=8.0,
            cpu_allocatable=3.5,
            memory_allocatable=7.0,
            cpu_usage=0.5,
            memory_usage=0.3,
            pod_count=5
        )

        data = node.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["node_id"], "test-node")
        self.assertEqual(data["status"], "Ready")

    def test_orchestration_metrics_creation(self):
        """Тест создания метрик оркестрации"""
        metrics = OrchestrationMetrics()
        
        self.assertEqual(metrics.total_pods, 0)
        self.assertEqual(metrics.running_pods, 0)
        self.assertEqual(metrics.failed_pods, 0)
        self.assertEqual(metrics.total_services, 0)
        self.assertEqual(metrics.total_nodes, 0)

    def test_orchestration_metrics_update(self):
        """Тест обновления метрик оркестрации"""
        metrics = OrchestrationMetrics()
        
        # Создаем тестовые данные
        pods = [
            PodInfo("pod1", "pod1", "default", PodStatus.RUNNING, 0.5, 0.3),
            PodInfo("pod2", "pod2", "default", PodStatus.FAILED, 0.0, 0.0)
        ]
        
        services = [
            ServiceInfo("svc1", "svc1", "default", ServiceStatus.ACTIVE, 1, 1, 0.5, 1.0, ScalingStrategy.AUTO)
        ]
        
        nodes = [
            NodeInfo("node1", "node1", "Ready", 4.0, 8.0, 3.5, 7.0, 0.5, 0.3, 2)
        ]

        # Обновляем метрики
        metrics.update_metrics(pods, services, nodes)

        self.assertEqual(metrics.total_pods, 2)
        self.assertEqual(metrics.running_pods, 1)
        self.assertEqual(metrics.failed_pods, 1)
        self.assertEqual(metrics.total_services, 1)
        self.assertEqual(metrics.total_nodes, 1)

    def test_orchestration_metrics_to_dict(self):
        """Тест преобразования метрик в словарь"""
        metrics = OrchestrationMetrics()
        data = metrics.to_dict()

        self.assertIsInstance(data, dict)
        self.assertIn("total_pods", data)
        self.assertIn("running_pods", data)
        self.assertIn("total_services", data)
        self.assertIn("total_nodes", data)

    def test_concurrent_deployment(self):
        """Тест параллельного развертывания"""
        self.orchestrator.initialize()

        def deploy_worker(worker_id):
            service_config = {
                "name": f"service-{worker_id}",
                "replicas": 1,
                "cpu_limit": 0.5,
                "memory_limit": 1.0
            }
            result = self.orchestrator.deploy_service(service_config)
            return result

        # Запуск нескольких потоков
        threads = []
        results = []
        
        for i in range(3):
            thread = threading.Thread(target=lambda i=i: results.append(deploy_worker(i)))
            threads.append(thread)
            thread.start()

        # Ожидание завершения всех потоков
        for thread in threads:
            thread.join()

        # Проверка результатов
        self.assertEqual(len(results), 3)
        self.assertTrue(all(results))  # Все должны быть успешными

        # Проверяем что все сервисы созданы
        services = self.orchestrator.get_services()
        self.assertEqual(len(services), 3)

    def test_scale_nonexistent_service(self):
        """Тест масштабирования несуществующего сервиса"""
        self.orchestrator.initialize()

        result = self.orchestrator.scale_service("nonexistent-service", 5)
        self.assertFalse(result)

    def test_scale_beyond_limits(self):
        """Тест масштабирования за пределами лимитов"""
        self.orchestrator.initialize()

        # Развертываем сервис
        service_config = {"name": "test-service", "replicas": 1}
        self.orchestrator.deploy_service(service_config)

        services = self.orchestrator.get_services()
        service_id = services[0].service_id

        # Пытаемся масштабировать за максимальный лимит
        result = self.orchestrator.scale_service(service_id, 20)
        self.assertTrue(result)  # Должно ограничиться максимальным значением

        # Проверяем что количество реплик не превышает лимит
        pods = self.orchestrator.get_pods(service_id)
        self.assertLessEqual(len(pods), self.orchestrator.max_replicas)

    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с неинициализированным оркестратором
        result = self.orchestrator.deploy_service({"name": "test"})
        self.assertFalse(result)

    def test_statistics_tracking(self):
        """Тест отслеживания статистики"""
        self.orchestrator.initialize()

        initial_deployments = self.orchestrator.statistics["total_deployments"]
        initial_scaling = self.orchestrator.statistics["total_scaling_operations"]

        # Выполняем развертывание
        service_config = {"name": "test-service", "replicas": 1}
        self.orchestrator.deploy_service(service_config)

        # Проверяем статистику
        self.assertGreater(self.orchestrator.statistics["total_deployments"], initial_deployments)

        # Выполняем масштабирование
        services = self.orchestrator.get_services()
        if services:
            self.orchestrator.scale_service(services[0].service_id, 2)

        # Проверяем статистику масштабирования
        self.assertGreater(self.orchestrator.statistics["total_scaling_operations"], initial_scaling)

    def test_configuration_validation(self):
        """Тест валидации конфигурации"""
        self.orchestrator.initialize()

        config = self.orchestrator.k8s_config
        self.assertIn("api_server", config)
        self.assertIn("namespace", config)
        self.assertIn("timeout", config)
        self.assertIn("enable_auto_scaling", config)

    def test_auto_scaling_enabled(self):
        """Тест включения автоматического масштабирования"""
        self.orchestrator.initialize()

        self.assertTrue(self.orchestrator.auto_scaling_enabled)
        self.assertTrue(self.orchestrator.k8s_config["enable_auto_scaling"])


if __name__ == '__main__':
    unittest.main()