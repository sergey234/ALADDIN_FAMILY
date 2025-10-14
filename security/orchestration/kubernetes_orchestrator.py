# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Kubernetes Orchestrator
Оркестратор Kubernetes для масштабирования системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import time
import threading
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import random

from core.base import ComponentStatus, SecurityBase


class PodStatus(Enum):
    """Статусы подов"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class ServiceStatus(Enum):
    """Статусы сервисов"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SCALING = "scaling"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ScalingStrategy(Enum):
    """Стратегии масштабирования"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    AUTO = "auto"
    MANUAL = "manual"


@dataclass
class PodInfo:
    """Информация о поде"""
    pod_id: str
    name: str
    namespace: str
    status: PodStatus
    cpu_usage: float
    memory_usage: float
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    node_name: str = ""
    image: str = ""
    labels: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.labels is None:
            self.labels = {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['last_updated'] = self.last_updated.isoformat() if self.last_updated else None
        return data


@dataclass
class ServiceInfo:
    """Информация о сервисе"""
    service_id: str
    name: str
    namespace: str
    status: ServiceStatus
    replicas: int
    desired_replicas: int
    cpu_limit: float
    memory_limit: float
    scaling_strategy: ScalingStrategy
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    labels: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.labels is None:
            self.labels = {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['status'] = self.status.value
        data['scaling_strategy'] = self.scaling_strategy.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['last_updated'] = self.last_updated.isoformat() if self.last_updated else None
        return data


@dataclass
class NodeInfo:
    """Информация о ноде"""
    node_id: str
    name: str
    status: str
    cpu_capacity: float
    memory_capacity: float
    cpu_allocatable: float
    memory_allocatable: float
    cpu_usage: float
    memory_usage: float
    pod_count: int
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    labels: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.labels is None:
            self.labels = {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['last_updated'] = self.last_updated.isoformat() if self.last_updated else None
        return data


@dataclass
class OrchestrationMetrics:
    """Метрики оркестрации"""
    total_pods: int = 0
    running_pods: int = 0
    failed_pods: int = 0
    total_services: int = 0
    active_services: int = 0
    total_nodes: int = 0
    available_nodes: int = 0
    total_cpu_usage: float = 0.0
    total_memory_usage: float = 0.0
    scaling_operations: int = 0
    last_scaling: Optional[datetime] = None

    def __post_init__(self):
        if self.last_scaling is None:
            self.last_scaling = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['last_scaling'] = self.last_scaling.isoformat() if self.last_scaling else None
        return data

    def update_metrics(self, pods: List[PodInfo], services: List[ServiceInfo], nodes: List[NodeInfo]):
        """Обновление метрик"""
        self.total_pods = len(pods)
        self.running_pods = len([p for p in pods if p.status == PodStatus.RUNNING])
        self.failed_pods = len([p for p in pods if p.status == PodStatus.FAILED])

        self.total_services = len(services)
        self.active_services = len([s for s in services if s.status == ServiceStatus.ACTIVE])

        self.total_nodes = len(nodes)
        self.available_nodes = len([n for n in nodes if n.status == "Ready"])

        self.total_cpu_usage = sum(p.cpu_usage for p in pods)
        self.total_memory_usage = sum(p.memory_usage for p in pods)


class KubernetesOrchestrator(SecurityBase):
    """Оркестратор Kubernetes для ALADDIN Security System"""

    def __init__(self, name: str = "KubernetesOrchestrator"):
        super().__init__(name)

        # Конфигурация оркестратора
        self.default_namespace = "aladdin-security"
        self.max_replicas = 10
        self.min_replicas = 1
        self.scaling_threshold = 0.8
        self.health_check_interval = 30
        self.auto_scaling_enabled = True

        # Хранилище данных
        self.pods: Dict[str, PodInfo] = {}
        self.services: Dict[str, ServiceInfo] = {}
        self.nodes: Dict[str, NodeInfo] = {}
        self.orchestration_metrics: OrchestrationMetrics = OrchestrationMetrics()
        self.orchestration_lock = threading.RLock()

        # Kubernetes конфигурация
        self.k8s_config = {
            "api_server": "https://kubernetes.default.svc",
            "namespace": self.default_namespace,
            "timeout": 30,
            "retry_attempts": 3,
            "enable_auto_scaling": True,
            "enable_health_checks": True,
            "enable_resource_monitoring": True,
            "scaling_cooldown": 300,  # 5 минут
            "max_scaling_operations_per_hour": 20
        }

        # Статистика
        self.statistics: Dict[str, Any] = {
            "total_deployments": 0,
            "successful_deployments": 0,
            "failed_deployments": 0,
            "total_scaling_operations": 0,
            "start_time": None,
            "last_deployment": None,
            "last_scaling": None
        }

    def initialize(self) -> bool:
        """Инициализация оркестратора Kubernetes"""
        try:
            self.log_activity("Инициализация Kubernetes Orchestrator", "info")
            self.status = ComponentStatus.RUNNING
            self.statistics["start_time"] = datetime.now()

            # Инициализация Kubernetes клиента
            self._initialize_k8s_client()

            # Загрузка существующих ресурсов
            self._load_existing_resources()

            # Запуск фоновых задач
            self._start_background_tasks()

            self.log_activity("Kubernetes Orchestrator успешно инициализирован", "info")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации Kubernetes Orchestrator: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def stop(self) -> bool:
        """Остановка оркестратора Kubernetes"""
        try:
            self.log_activity("Остановка Kubernetes Orchestrator", "info")
            self.status = ComponentStatus.STOPPED

            # Остановка фоновых задач
            self._stop_background_tasks()

            # Сохранение состояния
            self._save_orchestration_state()

            # Очистка данных
            with self.orchestration_lock:
                self.pods.clear()
                self.services.clear()
                self.nodes.clear()

            self.log_activity("Kubernetes Orchestrator остановлен", "info")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка остановки Kubernetes Orchestrator: {e}", "error")
            return False

    def deploy_service(self, service_config: Dict[str, Any]) -> bool:
        """Развертывание сервиса"""
        try:
            with self.orchestration_lock:
                self.statistics["total_deployments"] += 1

                # Создание сервиса
                service_info = self._create_service_info(service_config)
                self.services[service_info.service_id] = service_info

                # Создание подов
                pods_created = self._create_pods_for_service(service_info)

                if pods_created:
                    self.statistics["successful_deployments"] += 1
                    self.statistics["last_deployment"] = datetime.now()
                    self.log_activity(
                        f"Сервис {service_info.name} успешно развернут с {len(pods_created)} подами",
                        "info"
                    )
                    return True
                else:
                    self.statistics["failed_deployments"] += 1
                    self.log_activity(f"Ошибка развертывания сервиса {service_info.name}", "error")
                    return False

        except Exception as e:
            self.log_activity(f"Ошибка развертывания сервиса: {e}", "error")
            self.statistics["failed_deployments"] += 1
            return False

    def scale_service(self, service_id: str, replicas: int) -> bool:
        """Масштабирование сервиса"""
        try:
            with self.orchestration_lock:
                if service_id not in self.services:
                    self.log_activity(f"Сервис {service_id} не найден", "warning")
                    return False

                service = self.services[service_id]

                # Проверка лимитов
                if replicas > self.max_replicas:
                    replicas = self.max_replicas
                elif replicas < self.min_replicas:
                    replicas = self.min_replicas

                # Обновление желаемого количества реплик
                service.desired_replicas = replicas
                service.status = ServiceStatus.SCALING
                service.last_updated = datetime.now()

                # Создание или удаление подов
                current_pods = [p for p in self.pods.values() if p.labels and p.labels.get("service_id") == service_id]

                if replicas > len(current_pods):
                    # Увеличение количества подов
                    self._create_additional_pods(service, replicas - len(current_pods))
                elif replicas < len(current_pods):
                    # Уменьшение количества подов
                    self._remove_excess_pods(current_pods, len(current_pods) - replicas)

                # Обновление статуса
                service.replicas = replicas
                service.status = ServiceStatus.ACTIVE
                service.last_updated = datetime.now()

                # Обновление метрик
                self.orchestration_metrics.scaling_operations += 1
                self.orchestration_metrics.last_scaling = datetime.now()
                self.statistics["total_scaling_operations"] += 1
                self.statistics["last_scaling"] = datetime.now()

                self.log_activity(
                    f"Сервис {service.name} масштабирован до {replicas} реплик",
                    "info"
                )
                return True

        except Exception as e:
            self.log_activity(f"Ошибка масштабирования сервиса {service_id}: {e}", "error")
            return False

    def get_pods(self, service_id: Optional[str] = None) -> List[PodInfo]:
        """Получение списка подов"""
        try:
            with self.orchestration_lock:
                if service_id:
                    return [p for p in self.pods.values() if p.labels and p.labels.get("service_id") == service_id]
                return list(self.pods.values())
        except Exception as e:
            self.log_activity(f"Ошибка получения подов: {e}", "error")
            return []

    def get_services(self) -> List[ServiceInfo]:
        """Получение списка сервисов"""
        try:
            with self.orchestration_lock:
                return list(self.services.values())
        except Exception as e:
            self.log_activity(f"Ошибка получения сервисов: {e}", "error")
            return []

    def get_nodes(self) -> List[NodeInfo]:
        """Получение списка нод"""
        try:
            with self.orchestration_lock:
                return list(self.nodes.values())
        except Exception as e:
            self.log_activity(f"Ошибка получения нод: {e}", "error")
            return []

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Получение статуса оркестратора"""
        try:
            with self.orchestration_lock:
                # Обновление метрик
                self.orchestration_metrics.update_metrics(
                    list(self.pods.values()),
                    list(self.services.values()),
                    list(self.nodes.values())
                )

                return {
                    "status": self.status.value,
                    "total_pods": len(self.pods),
                    "total_services": len(self.services),
                    "total_nodes": len(self.nodes),
                    "metrics": self.orchestration_metrics.to_dict(),
                    "statistics": self.statistics,
                    "config": self.k8s_config,
                    "auto_scaling_enabled": self.auto_scaling_enabled
                }
        except Exception as e:
            self.log_activity(f"Ошибка получения статуса оркестратора: {e}", "error")
            return {}

    def _initialize_k8s_client(self):
        """Инициализация Kubernetes клиента"""
        try:
            # Симуляция инициализации Kubernetes клиента
            self.log_activity("Kubernetes клиент инициализирован", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Kubernetes клиента: {e}", "error")

    def _load_existing_resources(self):
        """Загрузка существующих ресурсов"""
        try:
            # Симуляция загрузки существующих ресурсов
            # В реальной системе здесь был бы запрос к Kubernetes API

            # Создание тестовых нод
            for i in range(3):
                node = NodeInfo(
                    node_id=f"node-{i}",
                    name=f"worker-node-{i}",
                    status="Ready",
                    cpu_capacity=4.0,
                    memory_capacity=8.0,
                    cpu_allocatable=3.5,
                    memory_allocatable=7.0,
                    cpu_usage=random.uniform(0.1, 0.5),
                    memory_usage=random.uniform(0.2, 0.6),
                    pod_count=random.randint(1, 5)
                )
                self.nodes[node.node_id] = node

            self.log_activity(f"Загружено {len(self.nodes)} нод", "info")
        except Exception as e:
            self.log_activity(f"Ошибка загрузки существующих ресурсов: {e}", "error")

    def _start_background_tasks(self):
        """Запуск фоновых задач"""
        try:
            # Запуск задачи мониторинга здоровья
            health_thread = threading.Thread(
                target=self._health_monitoring_task,
                daemon=True
            )
            health_thread.start()

            # Запуск задачи автоматического масштабирования
            if self.auto_scaling_enabled:
                scaling_thread = threading.Thread(
                    target=self._auto_scaling_task,
                    daemon=True
                )
                scaling_thread.start()

            self.log_activity("Фоновые задачи запущены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка запуска фоновых задач: {e}", "error")

    def _stop_background_tasks(self):
        """Остановка фоновых задач"""
        try:
            # Фоновые задачи остановятся автоматически при остановке оркестратора
            self.log_activity("Фоновые задачи остановлены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка остановки фоновых задач: {e}", "error")

    def _create_service_info(self, service_config: Dict[str, Any]) -> ServiceInfo:
        """Создание информации о сервисе"""
        service_info = ServiceInfo(
            service_id=f"service-{int(time.time() * 1000)}-{random.randint(1000, 9999)}",
            name=service_config.get("name", "unknown-service"),
            namespace=service_config.get("namespace", self.default_namespace),
            status=ServiceStatus.ACTIVE,
            replicas=service_config.get("replicas", 1),
            desired_replicas=service_config.get("replicas", 1),
            cpu_limit=service_config.get("cpu_limit", 0.5),
            memory_limit=service_config.get("memory_limit", 1.0),
            scaling_strategy=ScalingStrategy(service_config.get("scaling_strategy", "auto")),
            labels=service_config.get("labels", {})
        )
        return service_info

    def _create_pods_for_service(self, service_info: ServiceInfo) -> List[PodInfo]:
        """Создание подов для сервиса"""
        try:
            pods = []
            for i in range(service_info.replicas):
                pod = PodInfo(
                    pod_id=f"pod-{service_info.service_id}-{i}",
                    name=f"{service_info.name}-{i}",
                    namespace=service_info.namespace,
                    status=PodStatus.RUNNING,
                    cpu_usage=random.uniform(0.1, 0.3),
                    memory_usage=random.uniform(0.2, 0.4),
                    node_name=random.choice(list(self.nodes.keys())),
                    image=service_info.labels.get("image", "aladdin/security:latest") if service_info.labels else "aladdin/security:latest",
                    labels={"service_id": service_info.service_id}
                )
                self.pods[pod.pod_id] = pod
                pods.append(pod)
            return pods
        except Exception as e:
            self.log_activity(f"Ошибка создания подов: {e}", "error")
            return []

    def _create_additional_pods(self, service: ServiceInfo, count: int):
        """Создание дополнительных подов"""
        try:
            for i in range(count):
                pod = PodInfo(
                    pod_id=f"pod-{service.service_id}-{int(time.time())}-{i}",
                    name=f"{service.name}-{int(time.time())}-{i}",
                    namespace=service.namespace,
                    status=PodStatus.RUNNING,
                    cpu_usage=random.uniform(0.1, 0.3),
                    memory_usage=random.uniform(0.2, 0.4),
                    node_name=random.choice(list(self.nodes.keys())),
                    image=service.labels.get("image", "aladdin/security:latest") if service.labels else "aladdin/security:latest",
                    labels={"service_id": service.service_id}
                )
                self.pods[pod.pod_id] = pod
        except Exception as e:
            self.log_activity(f"Ошибка создания дополнительных подов: {e}", "error")

    def _remove_excess_pods(self, pods: List[PodInfo], count: int):
        """Удаление избыточных подов"""
        try:
            # Удаляем последние поды
            for pod in pods[-count:]:
                if pod.pod_id in self.pods:
                    del self.pods[pod.pod_id]
        except Exception as e:
            self.log_activity(f"Ошибка удаления избыточных подов: {e}", "error")

    def _health_monitoring_task(self):
        """Задача мониторинга здоровья"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(self.health_check_interval)

                # Проверка здоровья подов
                for pod in self.pods.values():
                    # Симуляция случайных сбоев
                    if random.random() < 0.01:  # 1% вероятность сбоя
                        pod.status = PodStatus.FAILED
                        self.log_activity(f"Под {pod.name} перешел в состояние FAILED", "warning")

                # Проверка здоровья сервисов
                for service in self.services.values():
                    service_pods = [p for p in self.pods.values() if p.labels.get("service_id") == service.service_id]
                    running_pods = [p for p in service_pods if p.status == PodStatus.RUNNING]

                    if len(running_pods) < service.desired_replicas:
                        service.status = ServiceStatus.ERROR
                        self.log_activity(f"Сервис {service.name} имеет недостаточно работающих подов", "warning")

        except Exception as e:
            self.log_activity(f"Ошибка задачи мониторинга здоровья: {e}", "error")

    def _auto_scaling_task(self):
        """Задача автоматического масштабирования"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(60)  # Проверка каждую минуту

                for service in self.services.values():
                    if service.scaling_strategy != ScalingStrategy.AUTO:
                        continue

                    service_pods = [p for p in self.pods.values() if p.labels.get("service_id") == service.service_id]
                    if not service_pods:
                        continue

                    # Расчет средней загрузки
                    avg_cpu = sum(p.cpu_usage for p in service_pods) / len(service_pods)

                    # Принятие решения о масштабировании
                    if avg_cpu > self.scaling_threshold and service.replicas < self.max_replicas:
                        self.scale_service(service.service_id, service.replicas + 1)
                    elif avg_cpu < 0.3 and service.replicas > self.min_replicas:
                        self.scale_service(service.service_id, service.replicas - 1)

        except Exception as e:
            self.log_activity(f"Ошибка задачи автоматического масштабирования: {e}", "error")

    def _save_orchestration_state(self):
        """Сохранение состояния оркестрации"""
        try:
            import os
            os.makedirs("/tmp/aladdin_orchestration", exist_ok=True)

            data_to_save = {
                "pods": {k: v.to_dict() for k, v in self.pods.items()},
                "services": {k: v.to_dict() for k, v in self.services.items()},
                "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
                "metrics": self.orchestration_metrics.to_dict(),
                "statistics": self.statistics,
                "saved_at": datetime.now().isoformat()
            }

            with open("/tmp/aladdin_orchestration/last_state.json", 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            self.log_activity("Состояние оркестрации сохранено", "info")
        except Exception as e:
            self.log_activity(f"Ошибка сохранения состояния оркестрации: {e}", "error")
