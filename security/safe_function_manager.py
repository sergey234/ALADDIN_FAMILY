# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Safe Function Manager
Главный менеджер безопасных функций ALADDIN

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import hashlib
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

# Redis imports with fallback
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from typing import Protocol

from core.base import ComponentStatus, SecurityBase, SecurityLevel
from security.advanced_monitoring_manager import (
    AlertSeverity,
    MetricType,
    MonitoringRule,
    advanced_monitoring_manager,
)
from security.async_io_manager import get_io_manager_sync
from security.lazy_wrappers import get_lazy_manager, get_lazy_system_stats
from security.search_indexer import get_search_indexer, get_search_stats
from security.pagination_system import UniversalPaginationSystem
from security.circuit_breaker import CircuitBreakerConfig, SmartCircuitBreaker
from security.compliance_audit import ComplianceAuditor

# НОВЫЕ КОМПОНЕНТЫ COMPLIANCE
from security.compliance_manager import ComplianceManager
from security.compliance_reporting import ComplianceReporter
from security.health_check_system import HealthCheckManager, HealthCheckSystem
from security.incident_response import (
    IncidentResponseManager,
    IncidentResponseSystem,
)
from security.microservices.redis_cache_manager import RedisCacheManager

# ИНТЕГРАЦИЯ С MICROSERVICES
from security.microservices.service_mesh_manager import (
    ServiceEndpoint,
    ServiceInfo,
    ServiceMeshManager,
    ServiceType,
)
from security.reactive.performance_optimizer import PerformanceOptimizer

# ИНТЕГРАЦИЯ С AUTO SCALING ENGINE
from security.scaling.auto_scaling_engine import (
    AutoScalingEngine,
    MetricData,
    ScalingAction,
    ScalingRule,
    ScalingTrigger,
)

# НОВЫЕ КОМПОНЕНТЫ МОНИТОРИНГА
from security.security_analytics import (
    SecurityAnalytics,
    SecurityAnalyticsManager,
)
from security.security_monitoring import SecurityMonitoring
from security.smart_monitoring import smart_monitoring

# НОВЫЕ ОПТИМИЗАЦИИ ПРОИЗВОДИТЕЛЬНОСТИ
from security.thread_pool_manager import get_thread_pool

# ============================================================================
# ИНТЕРФЕЙСЫ (PROTOCOLS) - ПРИОРИТЕТ 2
# ============================================================================


class MonitoringInterface(Protocol):
    """Интерфейс для мониторинга"""

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Логирование события"""
        ...

    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик"""
        ...


class CacheInterface(Protocol):
    """Интерфейс для кэширования"""

    def get(self, key: str) -> Optional[Any]:
        """Получение из кэша"""
        ...

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Сохранение в кэш"""
        ...


class DatabaseInterface(Protocol):
    """Интерфейс для базы данных"""

    def save_function_data(self, function_id: str, data: Dict[str, Any]) -> bool:
        """Сохранение данных функции"""
        ...

    def load_function_data(self, function_id: str) -> Optional[Dict[str, Any]]:
        """Загрузка данных функции"""
        ...


# ============================================================================
# ЛЕНИВАЯ ИНИЦИАЛИЗАЦИЯ - ПРИОРИТЕТ 2
# ============================================================================


class LazyInitializer:
    """Класс для ленивой инициализации компонентов"""

    def __init__(self, factory_func: Callable[[], Any]):
        self._factory = factory_func
        self._instance = None
        self._lock = threading.Lock()

    def get(self) -> Any:
        """Получение экземпляра с ленивой инициализацией"""
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._factory()
        return self._instance

    def reset(self) -> None:
        """Сброс экземпляра для повторной инициализации"""
        with self._lock:
            self._instance = None


# Простой класс SecurityAlert для совместимости
class SecurityAlert:
    def __init__(self, alert_type: str, message: str, severity: str = "medium"):
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.timestamp = datetime.now()


class FunctionStatus(Enum):
    """Статусы функций"""

    DISABLED = "disabled"
    ENABLED = "enabled"
    ACTIVE = "active"  # Добавляем поддержку статуса 'active'
    RUNNING = "running"  # Добавляем поддержку статуса 'running'
    TESTING = "testing"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    SLEEPING = "sleeping"  # Новый статус для спящего режима


class SecurityFunction:
    """Класс для представления безопасной функции"""

    def __init__(
        self,
        function_id: str,
        name: str,
        description: str,
        function_type: str,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
    ):
        self.function_id = function_id
        self.name = name
        self.description = description
        self.function_type = function_type
        self.security_level = security_level
        self.status = FunctionStatus.DISABLED
        self.created_at = datetime.now()
        self.last_execution = None
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        self.average_execution_time = 0.0
        self.dependencies = []
        self.config = {}
        self.is_critical = False
        self.auto_enable = False

        # Поля для спящего режима
        self.auto_sleep = False
        self.sleep_after_hours = 24
        self.last_activity = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "function_id": self.function_id,
            "name": self.name,
            "description": self.description,
            "function_type": self.function_type,
            "security_level": self.security_level.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_execution": (self.last_execution.isoformat() if self.last_execution else None),
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "average_execution_time": self.average_execution_time,
            "dependencies": self.dependencies,
            "is_critical": self.is_critical,
            "auto_enable": self.auto_enable,
            "auto_sleep": self.auto_sleep,
            "sleep_after_hours": self.sleep_after_hours,
            "last_activity": (self.last_activity.isoformat() if self.last_activity else None),
        }


class SafeFunctionManager(SecurityBase):
    """Главный менеджер безопасных функций ALADDIN"""

    def __init__(self, name: str = "SafeFunctionManager", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Конфигурация менеджера
        self.auto_test_interval = config.get("auto_test_interval", 3600) if config else 3600  # 1 час
        self.max_concurrent_functions = config.get("max_concurrent_functions", 50) if config else 50
        self.function_timeout = config.get("function_timeout", 300) if config else 300  # 5 минут
        self.enable_auto_management = config.get("enable_auto_management", False) if config else False

        # Конфигурация спящего режима - ВОЗВРАЩЕНО ПОСЛЕ ИСПРАВЛЕНИЯ
        # ДВОЙНОЙ БЛОКИРОВКИ
        self.enable_sleep_mode = config.get("enable_sleep_mode", False) if config else False
        self.sleep_check_interval = config.get("sleep_check_interval", 3600) if config else 3600  # 1 час
        self.default_sleep_hours = config.get("default_sleep_hours", 24) if config else 24
        self.auto_sleep_enabled = config.get("auto_sleep_enabled", False) if config else False
        self.sleep_grace_period = config.get("sleep_grace_period", 300) if config else 300  # 5 минут

        # Хранилище функций
        self.functions = {}
        self.function_handlers = {}
        self.function_dependencies = {}
        self.execution_queue = []
        self.active_executions = {}

        # Статистика
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.functions_enabled = 0
        self.functions_disabled = 0
        self.functions_sleeping = 0

        # Статистика спящего режима
        self.sleep_transitions = 0
        self.wake_transitions = 0
        self.auto_sleep_count = 0
        self.manual_sleep_count = 0
        self.manual_wake_count = 0

        # Кэширование - НОВОЕ УЛУЧШЕНИЕ
        self.redis_enabled = config.get("redis_enabled", True) if config else True
        # Конфигурация новых систем
        self.lazy_enabled = config.get("lazy_enabled", True) if config else True
        self.search_enabled = config.get("search_enabled", True) if config else True
        self.pagination_enabled = config.get("pagination_enabled", True) if config else True
        self.redis_url = config.get("redis_url", "redis://localhost:6379/0") if config else "redis://localhost:6379/0"
        self.cache_ttl = config.get("cache_ttl", 3600) if config else 3600  # 1 час
        self.redis_client = None
        self.cache_hits = 0
        self.cache_misses = 0

        # Встроенный кэш в памяти (fallback)
        self.memory_cache = {}
        self.cache_timestamps = {}

        # Circuit Breaker для отказоустойчивости
        self.circuit_breakers: Dict[str, SmartCircuitBreaker] = {}
        self.circuit_breaker_enabled = config.get("circuit_breaker_enabled", True) if config else True

        # НОВЫЕ ОПТИМИЗАЦИИ ПРОИЗВОДИТЕЛЬНОСТИ
        # Пул потоков для эффективного выполнения функций
        self.thread_pool = None
        self.thread_pool_enabled = config.get("thread_pool_enabled", True) if config else True
        self.max_thread_pool_workers = config.get("max_thread_pool_workers", 10) if config else 10

        # Асинхронный I/O менеджер для оптимизации файловых операций
        self.async_io_manager = None
        self.async_io_enabled = config.get("async_io_enabled", True) if config else True

        # ServiceMeshManager для управления микросервисами
        self.service_mesh_manager = None
        self.service_mesh_enabled = config.get("service_mesh_enabled", True) if config else True
        self.service_mesh_config = config.get("service_mesh_config", {}) if config else {}

        # Инициализация Redis
        if self.redis_enabled and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                self.redis_client.ping()  # Проверка подключения
                self.log_activity("Redis подключен успешно", "info")
            except Exception as e:
                self.log_activity(f"Redis недоступен: {e}, используем встроенный кэш", "warning")
                self.redis_enabled = False
                self.redis_client = None
        else:
            if not REDIS_AVAILABLE:
                self.log_activity("Redis модуль не установлен, используем встроенный кэш", "info")
            self.redis_enabled = False

        # Оптимизация производительности - ВОЗВРАЩЕНО ПОСЛЕ ИСПРАВЛЕНИЯ
        # ДВОЙНОЙ БЛОКИРОВКИ
        self.performance_optimizer = PerformanceOptimizer(f"{name}PerformanceOptimizer")
        self.optimization_enabled = config.get("optimization_enabled", True) if config else True
        # Redis Cache Manager для кэширования
        self.redis_cache_manager = None
        self.redis_cache_enabled = config.get("redis_cache_enabled", True) if config else True
        if self.redis_cache_enabled:
            try:
                self.redis_cache_manager = RedisCacheManager("SafeFunctionManagerCache")
                if not self.redis_cache_manager.initialize():
                    self.log_activity("Ошибка инициализации Redis Cache Manager", "warning")
                    self.redis_cache_manager = None
                else:
                    self.log_activity("Redis Cache Manager инициализирован успешно", "info")
            except Exception as e:
                self.log_activity(f"Ошибка создания Redis Cache Manager: {e}", "warning")
                self.redis_cache_manager = None
        self.optimization_interval = config.get("optimization_interval", 300) if config else 300  # 5 минут
        self.performance_metrics = []
        self.optimization_results = []

        # Интеграция с SecurityMonitoring
        self.security_monitoring = SecurityMonitoring({"name": f"{name}SecurityMonitoring"})
        self.monitoring_integration_enabled = config.get("monitoring_integration_enabled", True) if config else True
        self.security_alerts = []
        self.monitoring_rules = {}

        # ИНТЕГРАЦИЯ С AUTO SCALING ENGINE
        self.auto_scaling_engine = None
        self.scaling_enabled = config.get("scaling_enabled", True) if config else True
        self.scaling_config = config.get("scaling_config", {}) if config else {}

        # НОВЫЕ КОМПОНЕНТЫ МОНИТОРИНГА
        # Security Analytics для глубокой аналитики
        self.security_analytics = None
        self.analytics_enabled = config.get("analytics_enabled", True) if config else True
        self.analytics_config = config.get("analytics_config", {}) if config else {}

        # Incident Response для автоматического реагирования
        self.incident_response = None
        self.incident_response_enabled = config.get("incident_response_enabled", True) if config else True
        self.incident_response_config = config.get("incident_response_config", {}) if config else {}

        # Health Check System для комплексной проверки здоровья
        self.health_check_system = None
        self.health_check_enabled = config.get("health_check_enabled", True) if config else True
        self.health_check_config = config.get("health_check_config", {}) if config else {}

        # Блокировки
        self.execution_lock = threading.Lock()
        self.function_lock = threading.Lock()

        # Фоновые потоки
        self.sleep_management_thread = None
        self.sleep_management_active = False
        self.sleep_management_stop_event = threading.Event()

        # АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ SFM
        # Инициализируем SFM автоматически при создании
        self.initialize()

    def initialize(self) -> bool:
        """Инициализация менеджера безопасных функций"""
        try:
            self.log_activity(f"Инициализация менеджера безопасных функций {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Инициализация персистентности
            self._initialize_persistence()

            # Регистрация базовых функций
            self._register_basic_functions()

            # Загрузка сохраненных функций ПОСЛЕ регистрации базовых
            self._load_saved_functions()

            # Сохранение всех функций после загрузки
            self._save_functions()

            # Настройка зависимостей
            self._setup_dependencies()

            # Настройка обработчика EmergencyMLAnalyzer
            self._setup_emergencymlanalyzer_handler()

            # Инициализация критических функций
            self._initialize_critical_functions()

            # Инициализация новых компонентов системы
            self._initialize_lazy_system()
            self._initialize_search_system()
            self._initialize_pagination_system()

            # Отмечаем завершение инициализации
            self._initialization_complete = True

            # Запуск автоматического управления
            if self.enable_auto_management:
                self._start_auto_management()

            # Запуск автоматического управления спящим режимом
            if self.enable_sleep_mode and self.auto_sleep_enabled:
                self._start_sleep_management()

            # Настройка мониторинга
            self._setup_monitoring_rules()

            # Настройка мониторинга безопасности
            self._setup_security_monitoring_rules()

            # Периодическое обновление метрик
            self._update_monitoring_metrics()
            # self._update_security_monitoring_data()  # Временно отключено

            # Инициализация оптимизаций производительности
            self._initialize_performance_optimizations()

            # Инициализация ServiceMeshManager
            self._initialize_service_mesh_manager()

            # Инициализация AutoScalingEngine
            self._initialize_auto_scaling_engine()

            # Инициализация систем безопасности
            self._initialize_health_check_system()
            self._initialize_incident_response()
            self._initialize_security_analytics()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(f"Менеджер безопасных функций {self.name} успешно инициализирован")
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера безопасных функций {self.name}: {e}",
                "error",
            )
            return False

    # ==================== ОПТИМИЗАЦИИ ПРОИЗВОДИТЕЛЬНОСТИ ====================

    def _initialize_performance_optimizations(self):
        """Инициализация оптимизаций производительности"""
        try:
            # Инициализация пула потоков
            if self.thread_pool_enabled:
                self.thread_pool = get_thread_pool()
                self.log_activity(f"Пул потоков инициализирован: {self.max_thread_pool_workers} воркеров", "info")

            # Инициализация асинхронного I/O менеджера
            if self.async_io_enabled:
                try:
                    self.async_io_manager = get_io_manager_sync()
                    self.log_activity("Асинхронный I/O менеджер инициализирован", "info")
                except Exception as e:
                    self.log_activity(f"Ошибка инициализации Async IO Manager: {e}", "warning")
                    self.async_io_manager = None

            self.log_activity("Оптимизации производительности инициализированы", "info")

        except Exception as e:
            self.log_activity(f"Ошибка инициализации оптимизаций производительности: {e}", "error")

    def _initialize_service_mesh_manager(self):
        """Инициализация ServiceMeshManager для управления микросервисами"""
        try:
            if self.service_mesh_enabled:
                # Создаем конфигурацию для ServiceMeshManager
                mesh_config = {
                    "enable_circuit_breaker": True,
                    "enable_load_balancing": True,
                    "enable_health_checks": True,
                    "enable_metrics": True,
                    "enable_caching": True,
                    "enable_async": True,
                    "enable_prometheus": True,
                    "enable_redis": self.redis_enabled,
                    "redis_url": self.redis_url,
                    "cache_ttl": self.cache_ttl,
                    "max_retries": 3,
                    "timeout": 30,
                    "health_check_interval": 60,
                    "metrics_interval": 30,
                    "log_level": "INFO",
                }

                # Объединяем с пользовательской конфигурацией
                mesh_config.update(self.service_mesh_config)

                # Инициализируем ServiceMeshManager
                self.service_mesh_manager = ServiceMeshManager(name=f"{self.name}ServiceMesh", config=mesh_config)

                self.log_activity("ServiceMeshManager инициализирован успешно", "info")

                # Регистрируем базовые сервисы SFM
                self._register_sfm_services()

            else:
                self.log_activity("ServiceMeshManager отключен в конфигурации", "info")

        except Exception as e:
            self.log_activity(f"Ошибка инициализации ServiceMeshManager: {e}", "error")
            self.service_mesh_manager = None

    def _register_sfm_services(self):
        """Регистрация сервисов SFM в ServiceMeshManager"""
        try:
            if not self.service_mesh_manager:
                return

            # Регистрируем основной сервис SFM
            endpoint = ServiceEndpoint(
                service_id="sfm_main", host="localhost", port=8000, protocol="http", path="/sfm", weight=100
            )

            service_info = ServiceInfo(
                service_id="sfm_main",
                name="Safe Function Manager",
                description="Главный менеджер безопасных функций ALADDIN",
                service_type=ServiceType.API,
                version="1.0.0",
                endpoints=[endpoint],
                dependencies=[],
            )

            # Регистрируем сервис
            self.service_mesh_manager.register_service(service_info)

            self.log_activity("SFM сервисы зарегистрированы в ServiceMeshManager", "info")

        except Exception as e:
            self.log_activity(f"Ошибка регистрации SFM сервисов: {e}", "error")

    # ==================== REDIS КЭШИРОВАНИЕ ====================

    def get_cached_result(self, function_id: str, args_hash: str) -> Optional[Any]:
        """Получение результата из кэша (Redis или встроенный)"""
        try:
            key = f"sfm:{function_id}:{args_hash}"

            # Пробуем Redis сначала
            if self.redis_enabled and self.redis_client:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    self.cache_hits += 1
                    self.log_activity(f"Результат получен из Redis кэша для {function_id}", "debug")
                    import json

                    return json.loads(cached_data)
                else:
                    self.cache_misses += 1
                    return None

            # Fallback на встроенный кэш
            else:
                if key in self.memory_cache:
                    # Проверяем TTL
                    if time.time() - self.cache_timestamps.get(key, 0) < self.cache_ttl:
                        self.cache_hits += 1
                        self.log_activity(f"Результат получен из встроенного кэша для {function_id}", "debug")
                        return self.memory_cache[key]
                    else:
                        # Удаляем устаревший кэш
                        del self.memory_cache[key]
                        del self.cache_timestamps[key]

                self.cache_misses += 1
                return None

        except Exception as e:
            self.log_activity(f"Ошибка чтения кэша: {e}", "error")
            return None

    def cache_result(self, function_id: str, args_hash: str, result: Any) -> None:
        """Сохранение результата в кэш (Redis или встроенный)"""
        try:
            key = f"sfm:{function_id}:{args_hash}"

            # Пробуем Redis сначала
            if self.redis_enabled and self.redis_client:
                # Сериализация результата с обработкой специальных типов
                import json

                serialized_result = json.dumps(result, default=str, ensure_ascii=False)
                self.redis_client.setex(key, self.cache_ttl, serialized_result)
                self.log_activity(f"Результат сохранен в Redis кэш для {function_id}", "debug")

            # Fallback на встроенный кэш
            else:
                self.memory_cache[key] = result
                self.cache_timestamps[key] = time.time()
                self.log_activity(f"Результат сохранен во встроенный кэш для {function_id}", "debug")

        except Exception as e:
            self.log_activity(f"Ошибка записи в кэш: {e}", "error")

    def clear_cache(self, function_id: Optional[str] = None) -> bool:
        """Очистка кэша (Redis или встроенный)"""
        try:
            if self.redis_enabled and self.redis_client:
                # Очистка Redis кэша
                if function_id:
                    pattern = f"sfm:{function_id}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                        self.log_activity(f"Redis кэш очищен для функции {function_id}", "info")
                else:
                    pattern = "sfm:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                        self.log_activity("Весь Redis кэш SFM очищен", "info")
            else:
                # Очистка встроенного кэша
                if function_id:
                    pattern = f"sfm:{function_id}:"
                    keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(pattern)]
                    for key in keys_to_remove:
                        del self.memory_cache[key]
                        del self.cache_timestamps[key]
                    self.log_activity(f"Встроенный кэш очищен для функции {function_id}", "info")
                else:
                    self.memory_cache.clear()
                    self.cache_timestamps.clear()
                    self.log_activity("Весь встроенный кэш SFM очищен", "info")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка очистки кэша: {e}", "error")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "redis_enabled": self.redis_enabled,
            "cache_type": "Redis" if (self.redis_enabled and self.redis_client) else "Встроенный",
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": round(hit_rate, 2),
            "cache_ttl": self.cache_ttl,
            "redis_connected": self.redis_client is not None,
            "memory_cache_size": len(self.memory_cache),
            "cache_entries": len(self.memory_cache) if not self.redis_enabled else "N/A",
        }

    # ==================== CIRCUIT BREAKER ====================

    def get_circuit_breaker(self, function_id: str) -> SmartCircuitBreaker:
        """Получение Circuit Breaker для функции"""
        if function_id not in self.circuit_breakers:
            config = CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=3,
                timeout=60.0,
                adaptive_threshold=True,
                min_calls_for_analysis=10,
                error_rate_threshold=0.5,
                consecutive_errors=3,
            )
            self.circuit_breakers[function_id] = SmartCircuitBreaker(f"sfm_{function_id}", config)

            # Настраиваем callback'и
            self.circuit_breakers[function_id].on_state_change = self._on_circuit_breaker_state_change
            self.circuit_breakers[function_id].on_alert = self._on_circuit_breaker_alert

        return self.circuit_breakers[function_id]

    def _on_circuit_breaker_state_change(self, name: str, old_state, new_state):
        """Callback при изменении состояния Circuit Breaker"""
        self.log_activity(
            f"Circuit Breaker {name}: {old_state.value} -> {new_state.value}",
            "warning" if new_state.value == "open" else "info",
        )

    def _on_circuit_breaker_alert(self, alert_data: Dict[str, Any]):
        """Callback при алерте Circuit Breaker"""
        self.log_activity(f"Circuit Breaker alert: {alert_data.get('state', 'unknown')}", "warning")

        # Отправляем в умную систему мониторинга
        smart_monitoring.add_metric(
            "circuit_breaker_state",
            1 if alert_data["state"] == "open" else 0,
            {"circuit_breaker": alert_data["circuit_breaker"]},
        )

    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Получение статистики Circuit Breaker'ов"""
        if not self.circuit_breakers:
            return {"enabled": False, "circuit_breakers": {}}

        return {
            "enabled": self.circuit_breaker_enabled,
            "total_circuit_breakers": len(self.circuit_breakers),
            "circuit_breakers": {name: cb.get_stats() for name, cb in self.circuit_breakers.items()},
        }

    def _register_basic_functions(self):
        """Регистрация базовых функций"""
        basic_functions = [
            {
                "function_id": "core_base",
                "name": "CoreBase",
                "description": "Базовая архитектура системы",
                "function_type": "core",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
            {
                "function_id": "service_base",
                "name": "ServiceBase",
                "description": "Базовый сервис",
                "function_type": "core",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
            {
                "function_id": "security_base",
                "name": "SecurityBase",
                "description": "Базовая безопасность",
                "function_type": "security",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
            {
                "function_id": "database",
                "name": "Database",
                "description": "Модуль базы данных",
                "function_type": "core",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
            {
                "function_id": "configuration",
                "name": "Configuration",
                "description": "Управление конфигурацией",
                "function_type": "core",
                "security_level": SecurityLevel.MEDIUM,
                "is_critical": False,
                "auto_enable": True,
            },
            {
                "function_id": "logging_module",
                "name": "LoggingModule",
                "description": "Система логирования",
                "function_type": "core",
                "security_level": SecurityLevel.MEDIUM,
                "is_critical": False,
                "auto_enable": True,
            },
            {
                "function_id": "authentication",
                "name": "Authentication",
                "description": "Аутентификация",
                "function_type": "security",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
            {
                "function_id": "emergencymlanalyzer",
                "name": "EmergencyMLAnalyzer",
                "description": "ML анализатор экстренных ситуаций",
                "function_type": "ai_agent",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
        ]

        for func_data in basic_functions:
            # Регистрируем без сохранения в файл (сохранение будет после загрузки)
            function = SecurityFunction(
                function_id=func_data["function_id"],
                name=func_data["name"],
                description=func_data["description"],
                function_type=func_data["function_type"],
                security_level=func_data["security_level"],
            )
            function.is_critical = func_data["is_critical"]
            function.auto_enable = func_data["auto_enable"]

            self.functions[func_data["function_id"]] = function

            # Включаем функцию если требуется
            if func_data["auto_enable"]:
                self.enable_function(func_data["function_id"])

        self.log_activity(f"Зарегистрировано {len(basic_functions)} базовых функций")

    def _setup_dependencies(self):
        """Настройка зависимостей между функциями"""
        dependencies = {
            "service_base": ["core_base"],
            "security_base": ["core_base"],
            "database": ["core_base"],
            "configuration": ["core_base"],
            "logging_module": ["core_base"],
            "authentication": ["core_base", "database"],
            "emergencymlanalyzer": ["core_base", "security_base"],
        }

        for function_id, deps in dependencies.items():
            if function_id in self.functions:
                self.functions[function_id].dependencies = deps

        self.log_activity("Зависимости между функциями настроены")

    def _initialize_critical_functions(self):
        """Инициализация критических функций"""
        for function in self.functions.values():
            if function.is_critical and function.auto_enable:
                self.enable_function(function.function_id)

        self.log_activity("Критические функции инициализированы")

    def _start_auto_management(self):
        """Запуск автоматического управления"""
        # Здесь будет логика автоматического управления
        self.log_activity("Автоматическое управление функциями запущено")

    def register_function(
        self,
        function_id: str,
        name: str,
        description: str,
        function_type: str,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
        is_critical: bool = False,
        auto_enable: bool = False,
        handler: Optional[Callable] = None,
    ) -> bool:
        """
        Регистрация новой функции

        Args:
            function_id: Уникальный ID функции
            name: Название функции
            description: Описание функции
            function_type: Тип функции
            security_level: Уровень безопасности
            is_critical: Критическая функция
            auto_enable: Автоматическое включение
            handler: Обработчик функции (опционально)

        Returns:
            bool: True если функция зарегистрирована
        """
        try:
            with self.function_lock:
                # Валидация входных данных
                valid_id, id_error = self._validate_function_id(function_id)
                if not valid_id:
                    self.log_activity(f"Ошибка валидации function_id: {id_error}", "error")
                    return False

                valid_name, name_error = self._validate_function_name(name)
                if not valid_name:
                    self.log_activity(f"Ошибка валидации name: {name_error}", "error")
                    return False

                # Санитизация входных данных
                sanitized_name = self._sanitize_input(name)
                sanitized_description = self._sanitize_input(description)

                if function_id in self.functions:
                    self.log_activity(f"Функция {function_id} уже зарегистрирована", "warning")
                    return False

                function = SecurityFunction(
                    function_id=function_id,
                    name=sanitized_name,
                    description=sanitized_description,
                    function_type=function_type,
                    security_level=security_level,
                )
                function.is_critical = is_critical
                function.auto_enable = auto_enable

                self.functions[function_id] = function

                # Регистрируем обработчик если предоставлен
                if handler is not None:
                    self.function_handlers[function_id] = handler
                    self.log_activity(f"Зарегистрирован обработчик для функции: {name} ({function_id})")

                self.log_activity(f"Зарегистрирована функция: {name} ({function_id})")
            # Автоматическое включение если требуется - ВЫНЕСЕНО ИЗ БЛОКИРОВКИ
            if auto_enable:
                self.enable_function(function_id)

            # Автоматическое сохранение при изменениях (только если не инициализация)
            if hasattr(self, "_initialization_complete") and self._initialization_complete:
                self.save_functions()

            return True

        except Exception as e:
            self.log_activity(f"Ошибка регистрации функции {function_id}: {e}", "error")
            return False

    def unregister_function(self, function_id: str) -> bool:
        """
        Отмена регистрации функции

        Args:
            function_id: ID функции

        Returns:
            bool: True если функция отменена
        """
        try:
            with self.function_lock:
                if function_id not in self.functions:
                    return False

                # Проверка зависимостей
                if self._has_dependent_functions(function_id):
                    self.log_activity(f"Невозможно удалить функцию {function_id}: " "есть зависимые функции", "error")
                    return False

                # Отключение функции
                self.disable_function(function_id)

                # Удаление функции
                del self.functions[function_id]

                self.log_activity(f"Функция {function_id} отменена")
                return True

        except Exception as e:
            self.log_activity(f"Ошибка отмены регистрации функции {function_id}: {e}", "error")
            return False

    def _has_dependent_functions(self, function_id: str) -> bool:
        """Проверка наличия зависимых функций"""
        for function in self.functions.values():
            if function_id in function.dependencies:
                return True
        return False

    def enable_function(self, function_id: str) -> bool:
        """
        Включение функции

        Args:
            function_id: ID функции

        Returns:
            bool: True если функция включена
        """
        try:
            with self.function_lock:
                if function_id not in self.functions:
                    return False

                function = self.functions[function_id]

                # Проверка зависимостей
                if not self._check_dependencies(function_id):
                    self.log_activity(
                        f"Невозможно включить функцию {function_id}: " f"зависимости не удовлетворены", "error"
                    )
                    return False

                if function.status == FunctionStatus.ENABLED:
                    return True

                function.status = FunctionStatus.ENABLED
                self.functions_enabled += 1
                self.functions_disabled = max(0, self.functions_disabled - 1)

                self.log_activity(f"Функция {function_id} включена")
                return True

        except Exception as e:
            self.log_activity(f"Ошибка включения функции {function_id}: {e}", "error")
            return False

    def disable_function(self, function_id: str) -> bool:
        """
        Отключение функции

        Args:
            function_id: ID функции

        Returns:
            bool: True если функция отключена
        """
        try:
            with self.function_lock:
                if function_id not in self.functions:
                    return False

                function = self.functions[function_id]

                if function.status == FunctionStatus.DISABLED:
                    return True

                function.status = FunctionStatus.DISABLED
                self.functions_disabled += 1
                self.functions_enabled = max(0, self.functions_enabled - 1)

                self.log_activity(f"Функция {function_id} отключена")
                return True

        except Exception as e:
            self.log_activity(f"Ошибка отключения функции {function_id}: {e}", "error")
            return False

    def _check_dependencies(self, function_id: str) -> bool:
        """Проверка зависимостей функции"""
        if function_id not in self.functions:
            return False

        function = self.functions[function_id]

        for dep_id in function.dependencies:
            if dep_id not in self.functions:
                return False

            dep_function = self.functions[dep_id]
            if dep_function.status != FunctionStatus.ENABLED:
                return False

        return True

    def execute_function(self, function_id: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any, str]:
        """
        Выполнение функции

        Args:
            function_id: ID функции
            params: Параметры выполнения

        Returns:
            Tuple[bool, Any, str]: (успех, результат, сообщение)
        """
        try:
            with self.execution_lock:
                # Валидация function_id
                valid_id, id_error = self._validate_function_id(function_id)
                if not valid_id:
                    self._log_security_event("INVALID_FUNCTION_ID", function_id, {"error": id_error})
                    return (False, None, f"Ошибка валидации function_id: {id_error}")

                # Валидация параметров
                if params is not None:
                    valid_params, params_error = self._validate_function_params(params)
                    if not valid_params:
                        self._log_security_event("INVALID_PARAMS", function_id, {"error": params_error})
                        return (False, None, f"Ошибка валидации параметров: {params_error}")

                # Проверка существования функции
                if function_id not in self.functions:
                    return (False, None, f"Функция {function_id} не найдена")

                function = self.functions[function_id]

                # Проверка на угрозы безопасности
                if not self._check_security_threats(function_id, params):
                    self._log_security_event("SECURITY_THREAT_DETECTED", function_id, {"params": params})
                    return False, None, "Обнаружена угроза безопасности"

                # Проверка статуса функции
                if function.status != FunctionStatus.ENABLED:
                    return (
                        False,
                        None,
                        f"Функция {function_id} не активна " f"(статус: {function.status.value})",
                    )

                # Проверка лимита одновременных выполнений
                if len(self.active_executions) >= self.max_concurrent_functions:
                    return (False, None, "Достигнут лимит одновременных выполнений")

                # Создание задачи выполнения
                execution_id = f"{function_id}_{int(time.time())}"
                self.active_executions[execution_id] = {
                    "function_id": function_id,
                    "start_time": datetime.now(),
                    "params": params or {},
                }

            # ==================== REDIS КЭШИРОВАНИЕ ====================
            # Проверка кэша перед выполнением
            import json

            args_hash = hashlib.md5(json.dumps(params or {}, sort_keys=True).encode()).hexdigest()

            cached_result = self.get_cached_result(function_id, args_hash)
            if cached_result is not None:
                # Результат найден в кэше
                self.log_activity(f"Результат получен из кэша для {function_id}", "debug")
                return True, cached_result, "Результат получен из кэша"

            # Выполнение функции
            start_time = time.time()
            try:
                result = self._execute_function_handler(function_id, params or {})
                execution_time = time.time() - start_time

                # Сохранение результата в кэш
                self.cache_result(function_id, args_hash, result)

                # Обновление статистики
                self._update_function_stats(function_id, True, execution_time)

                self.log_activity(f"Функция {function_id} выполнена успешно за " f"{execution_time:.2f}с")
                return True, result, "Функция выполнена успешно"

            except Exception as e:
                execution_time = time.time() - start_time
                self._update_function_stats(function_id, False, execution_time)

                self.log_activity(f"Ошибка выполнения функции {function_id}: {e}", "error")
                return False, None, f"Ошибка выполнения: {e}"

            finally:
                # Удаление из активных выполнений
                with self.execution_lock:
                    if execution_id in self.active_executions:
                        del self.active_executions[execution_id]

        except Exception as e:
            self.log_activity(f"Системная ошибка выполнения функции {function_id}: {e}", "error")
            return False, None, f"Системная ошибка: {e}"

    def execute_function_async(self, function_id: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Асинхронное выполнение функции с использованием пула потоков

        Args:
            function_id: ID функции
            params: Параметры выполнения

        Returns:
            Future объект для получения результата
        """
        try:
            if not self.thread_pool_enabled or not self.thread_pool:
                # Fallback на синхронное выполнение
                return self.execute_function(function_id, params)

            # Создание задачи для пула потоков
            future = self.thread_pool.submit(self.execute_function, function_id, params)

            self.log_activity(f"Асинхронное выполнение функции {function_id} запущено", "info")

            return future

        except Exception as e:
            self.log_activity(f"Ошибка асинхронного выполнения функции {function_id}: {e}", "error")
            # Fallback на синхронное выполнение
            return self.execute_function(function_id, params)

    def save_functions_async(self) -> Any:
        """
        Асинхронное сохранение функций с использованием I/O менеджера

        Returns:
            Future объект для получения результата
        """
        try:
            if not self.async_io_enabled or not self.async_io_manager:
                # Fallback на синхронное сохранение
                self._save_functions()
                return True

            # Создание задачи для асинхронного I/O
            future = self.async_io_manager.submit_task(self._save_functions)

            self.log_activity("Асинхронное сохранение функций запущено", "info")

            return future

        except Exception as e:
            self.log_activity(f"Ошибка асинхронного сохранения функций: {e}", "error")
            # Fallback на синхронное сохранение
            self._save_functions()
            return True

    def load_functions_async(self) -> Any:
        """
        Асинхронная загрузка функций с использованием I/O менеджера

        Returns:
            Future объект для получения результата
        """
        try:
            if not self.async_io_enabled or not self.async_io_manager:
                # Fallback на синхронную загрузку
                self._load_saved_functions()
                return True

            # Создание задачи для асинхронного I/O
            future = self.async_io_manager.submit_task(self._load_saved_functions)

            self.log_activity("Асинхронная загрузка функций запущена", "info")

            return future

        except Exception as e:
            self.log_activity(f"Ошибка асинхронной загрузки функций: {e}", "error")
            # Fallback на синхронную загрузку
            self._load_saved_functions()
            return True

    def shutdown_optimizations(self):
        """Корректное завершение работы оптимизаций"""
        try:
            # Завершение пула потоков
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
                self.log_activity("Пул потоков завершен", "info")

            # Завершение асинхронного I/O менеджера
            if self.async_io_manager:
                self.async_io_manager.shutdown()
                self.log_activity("Асинхронный I/O менеджер завершен", "info")

            self.log_activity("Оптимизации успешно завершены", "info")

        except Exception as e:
            self.log_activity(f"Ошибка завершения оптимизаций: {e}", "error")

    def _execute_function_handler(self, function_id: str, params: Dict[str, Any]) -> Any:
        """Выполнение обработчика функции"""
        if function_id in self.function_handlers:
            handler = self.function_handlers[function_id]
            return handler(params)
        else:
            # Заглушка для функций без обработчика
            return {"status": "executed", "function_id": function_id, "params": params}

    def _update_function_stats(self, function_id: str, success: bool, execution_time: float):
        """Обновление статистики функции"""
        if function_id not in self.functions:
            return

        function = self.functions[function_id]
        function.execution_count += 1
        function.last_execution = datetime.now()

        if success:
            function.success_count += 1
            self.successful_executions += 1
        else:
            function.error_count += 1
            self.failed_executions += 1

        # Обновление среднего времени выполнения
        total_time = function.average_execution_time * (function.execution_count - 1) + execution_time
        function.average_execution_time = total_time / function.execution_count

        self.total_executions += 1

    def register_function_handler(self, function_id: str, handler: Callable) -> bool:
        """
        Регистрация обработчика функции

        Args:
            function_id: ID функции
            handler: Обработчик функции

        Returns:
            bool: True если обработчик зарегистрирован
        """
        try:
            if function_id not in self.functions:
                return False

            self.function_handlers[function_id] = handler
            self.log_activity(f"Зарегистрирован обработчик для функции {function_id}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка регистрации обработчика функции {function_id}: {e}", "error")
            return False

    def get_function_status(self, function_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение статуса функции

        Args:
            function_id: ID функции

        Returns:
            Optional[Dict[str, Any]]: Статус функции
        """
        if function_id not in self.functions:
            return None

        function = self.functions[function_id]
        return function.to_dict()

    def get_all_functions_status(self) -> List[Dict[str, Any]]:
        """
        Получение статуса всех функций

        Returns:
            List[Dict[str, Any]]: Список статусов функций
        """
        return [function.to_dict() for function in self.functions.values()]

    def get_enabled_functions(self) -> List[Dict[str, Any]]:
        """
        Получение включенных функций

        Returns:
            List[Dict[str, Any]]: Список включенных функций
        """
        return [function.to_dict() for function in self.functions.values() if function.status == FunctionStatus.ENABLED]

    def get_critical_functions(self) -> List[Dict[str, Any]]:
        """
        Получение критических функций

        Returns:
            List[Dict[str, Any]]: Список критических функций
        """
        return [function.to_dict() for function in self.functions.values() if function.is_critical]

    def get_function_dependencies(self, function_id: str) -> List[str]:
        """
        Получение зависимостей функции

        Args:
            function_id: ID функции

        Returns:
            List[str]: Список зависимостей
        """
        if function_id not in self.functions:
            return []

        return self.functions[function_id].dependencies.copy()

    def get_dependent_functions(self, function_id: str) -> List[str]:
        """
        Получение функций, зависящих от указанной

        Args:
            function_id: ID функции

        Returns:
            List[str]: Список зависимых функций
        """
        dependent_functions = []
        for func_id, function in self.functions.items():
            if function_id in function.dependencies:
                dependent_functions.append(func_id)

        return dependent_functions

    def test_function(self, function_id: str) -> Tuple[bool, str]:
        """
        Тестирование функции

        Args:
            function_id: ID функции

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            if function_id not in self.functions:
                return False, f"Функция {function_id} не найдена"

            function = self.functions[function_id]
            original_status = function.status

            # Временное включение для тестирования
            function.status = FunctionStatus.TESTING

            # Выполнение теста
            success, result, message = self.execute_function(function_id, {"test": True})

            # Восстановление статуса
            function.status = original_status

            if success:
                self.log_activity(f"Тест функции {function_id} пройден успешно")
                return True, "Тест пройден успешно"
            else:
                self.log_activity(f"Тест функции {function_id} провален: {message}", "error")
                return False, f"Тест провален: {message}"

        except Exception as e:
            self.log_activity(f"Ошибка тестирования функции {function_id}: {e}", "error")
            return False, f"Ошибка тестирования: {e}"

    def get_status(self) -> Dict[str, Any]:
        """
        Получение общего статуса SFM с кэш-статистикой

        Returns:
            Dict[str, Any]: Общий статус SFM
        """
        try:
            # Базовые метрики
            sleeping_functions = len([f for f in self.functions.values() if f.status == FunctionStatus.SLEEPING])

            # Статистика кэша Redis
            cache_stats = self.get_cache_stats()

            # Статистика Circuit Breaker
            circuit_breaker_stats = self.get_circuit_breaker_stats()

            # Статистика умного мониторинга
            monitoring_stats = smart_monitoring.get_alert_stats()

            return {
                "manager_name": self.name,
                "status": self.status.value,
                "total_functions": len(self.functions),
                "enabled_functions": self.functions_enabled,
                "disabled_functions": self.functions_disabled,
                "sleeping_functions": sleeping_functions,
                "critical_functions": len([f for f in self.functions.values() if f.is_critical]),
                "total_executions": self.total_executions,
                "successful_executions": self.successful_executions,
                "failed_executions": self.failed_executions,
                "active_executions": len(self.active_executions),
                "execution_success_rate": (
                    (self.successful_executions / self.total_executions * 100) if self.total_executions > 0 else 0
                ),
                "functions_by_type": self._get_functions_by_type(),
                "functions_by_security_level": (self._get_functions_by_security_level()),
                "functions_by_status": self._get_functions_by_status(),
                "redis_cache": cache_stats,
                "circuit_breaker": circuit_breaker_stats,
                "smart_monitoring": monitoring_stats,
                "uptime_seconds": ((datetime.now() - self.start_time).total_seconds() if self.start_time else 0),
                "last_activity": (self.last_activity.isoformat() if self.last_activity else None),
            }

        except Exception as e:
            self.log_activity("Ошибка в методе", "error")
            return {"error": str(e)}

    def get_safe_function_stats(self) -> Dict[str, Any]:
        """
        Получение статистики менеджера безопасных функций

        Returns:
            Dict[str, Any]: Статистика менеджера
        """
        sleeping_functions = len([f for f in self.functions.values() if f.status == FunctionStatus.SLEEPING])

        return {
            "total_functions": len(self.functions),
            "enabled_functions": self.functions_enabled,
            "disabled_functions": self.functions_disabled,
            "sleeping_functions": sleeping_functions,
            "critical_functions": len([f for f in self.functions.values() if f.is_critical]),
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "active_executions": len(self.active_executions),
            "execution_success_rate": (
                (self.successful_executions / self.total_executions * 100) if self.total_executions > 0 else 0
            ),
            "functions_by_type": self._get_functions_by_type(),
            "functions_by_security_level": (self._get_functions_by_security_level()),
            "functions_by_status": self._get_functions_by_status(),
        }

    def _get_functions_by_type(self) -> Dict[str, int]:
        """Получение количества функций по типам"""
        types_count = {}
        for function in self.functions.values():
            func_type = function.function_type
            types_count[func_type] = types_count.get(func_type, 0) + 1
        return types_count

    def _get_functions_by_security_level(self) -> Dict[str, int]:
        """Получение количества функций по уровням безопасности"""
        levels_count = {}
        for function in self.functions.values():
            level = function.security_level.value
            levels_count[level] = levels_count.get(level, 0) + 1
        return levels_count

    def _get_functions_by_status(self) -> Dict[str, int]:
        """Получение количества функций по статусам"""
        status_count = {}
        for function in self.functions.values():
            status = function.status.value
            status_count[status] = status_count.get(status, 0) + 1
        return status_count

    def sleep_function(self, function_id: str) -> bool:
        """
        Перевод функции в спящий режим

        Args:
            function_id: ID функции

        Returns:
            bool: True если функция переведена в спящий режим
        """
        try:
            with self.function_lock:
                if function_id not in self.functions:
                    return False

                function = self.functions[function_id]

                # Проверка, что функция не критическая
                if function.is_critical:
                    self.log_activity(
                        f"Невозможно перевести критическую функцию " f"{function_id} в спящий режим", "warning"
                    )
                    return False

                # Перевод в спящий режим
                function.status = FunctionStatus.SLEEPING
                function.last_activity = datetime.now()

                # Обновление статистики
                self.sleep_transitions += 1
                self.manual_sleep_count += 1
                self.functions_sleeping += 1
                self.functions_enabled = max(0, self.functions_enabled - 1)

                # Отправляем метрики в мониторинг
                self._update_monitoring_metrics()

                # Отправляем алерт если критическая функция переведена в сон
                if function.is_critical:
                    from security.advanced_monitoring_manager import (
                        AlertSeverity,
                    )

                    self._send_monitoring_alert(
                        alert_id=f"critical_sleep_{function_id}",
                        title=f"Critical Function Sleeping: {function.name}",
                        message=(f"Critical function {function.name} " f"has been put to sleep"),
                        severity=AlertSeverity.WARNING,
                        metric_name="sfm_critical_sleeping_count",
                        current_value=1,
                    )

                    # Мониторинг безопасности
                    self._monitor_function_security(function_id, "sleep", {"function_name": function.name})

                self.log_activity(f"Функция {function_id} переведена в спящий режим")
                return True

        except Exception as e:
            self.log_activity(f"Ошибка перевода функции {function_id} в спящий режим: {e}", "error")
            return False

    def wake_function(self, function_id: str) -> bool:
        """
        Пробуждение функции из спящего режима

        Args:
            function_id: ID функции

        Returns:
            bool: True если функция пробуждена
        """
        try:
            with self.function_lock:
                if function_id not in self.functions:
                    return False

                function = self.functions[function_id]

                # Проверка статуса
                if function.status != FunctionStatus.SLEEPING:
                    self.log_activity(
                        f"Функция {function_id} не в спящем режиме " f"(статус: {function.status.value})", "warning"
                    )
                    return False

                # Проверка зависимостей
                if not self._check_dependencies(function_id):
                    self.log_activity(
                        f"Невозможно пробудить функцию {function_id}: " f"зависимости не удовлетворены", "error"
                    )
                    return False

                # Пробуждение функции
                function.status = FunctionStatus.ENABLED
                function.last_activity = datetime.now()

                # Обновление статистики
                self.wake_transitions += 1
                self.manual_wake_count += 1
                self.functions_enabled += 1
                self.functions_sleeping = max(0, self.functions_sleeping - 1)

                # Отправляем метрики в мониторинг
                self._update_monitoring_metrics()

                self.log_activity(f"Функция {function_id} пробуждена из спящего режима")
                return True

        except Exception as e:
            self.log_activity(f"Ошибка пробуждения функции {function_id}: {e}", "error")
            return False

    def register_function_with_sleep(
        self,
        function_id: str,
        name: str,
        description: str,
        function_type: str,
        handler: Optional[Callable] = None,
        security_level: SecurityLevel = (SecurityLevel.MEDIUM),
        dependencies: Optional[List[str]] = None,
        is_critical: bool = False,
        auto_sleep: bool = True,
        sleep_after_hours: int = 24,
    ) -> bool:
        """
        Регистрация функции с поддержкой спящего режима

        Args:
            function_id: ID функции
            name: Название функции
            description: Описание функции
            function_type: Тип функции
            handler: Обработчик функции
            security_level: Уровень безопасности
            dependencies: Список зависимостей
            is_critical: Критическая ли функция
            auto_sleep: Автоматический перевод в спящий режим
            sleep_after_hours: Через сколько часов переводить в спящий режим

        Returns:
            bool: True если функция зарегистрирована
        """
        try:
            with self.function_lock:
                if function_id in self.functions:
                    return False

                # Создание функции
                function = SecurityFunction(
                    function_id=function_id,
                    name=name,
                    description=description,
                    function_type=function_type,
                    security_level=security_level,
                )

                # Настройка зависимостей
                if dependencies:
                    function.dependencies = dependencies

                # Настройка критичности
                function.is_critical = is_critical

                # Настройка спящего режима
                if auto_sleep and not is_critical:
                    function.status = FunctionStatus.SLEEPING
                    function.auto_sleep = True
                    function.sleep_after_hours = sleep_after_hours
                else:
                    function.status = FunctionStatus.DISABLED
                    function.auto_sleep = False

                # Регистрация обработчика
                if handler:
                    self.function_handlers[function_id] = handler

                # Сохранение функции
                self.functions[function_id] = function

                # Обновление статистики
                if function.status == FunctionStatus.SLEEPING:
                    self.functions_disabled += 1
                elif function.status == FunctionStatus.ENABLED:
                    self.functions_enabled += 1

                self.log_activity(f"Зарегистрирована функция с поддержкой спящего режима: " f"{name} ({function_id})")
                return True

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def get_sleeping_functions(self) -> List[Dict[str, Any]]:
        """
        Получение списка функций в спящем режиме

        Returns:
            List[Dict[str, Any]]: Список функций в спящем режиме
        """
        sleeping_functions = []
        for function in self.functions.values():
            if function.status == FunctionStatus.SLEEPING:
                sleeping_functions.append(function.to_dict())
        return sleeping_functions

    def auto_sleep_management(self) -> int:
        """
        Автоматическое управление спящим режимом

        Returns:
            int: Количество функций переведенных в спящий режим
        """
        sleep_count = 0
        current_time = datetime.now()

        try:
            with self.function_lock:
                for function_id, function in self.functions.items():
                    # Пропускаем критические функции
                    if function.is_critical:
                        continue

                    # Пропускаем уже спящие функции
                    if function.status == FunctionStatus.SLEEPING:
                        continue

                    # Проверяем время неактивности
                    if function.last_activity:
                        inactive_hours = (current_time - function.last_activity).total_seconds() / 3600
                        if inactive_hours >= function.sleep_after_hours:
                            function.status = FunctionStatus.SLEEPING
                            function.last_activity = current_time
                            sleep_count += 1

                            # Обновление статистики
                            self.sleep_transitions += 1
                            self.functions_sleeping += 1
                            self.functions_enabled = max(0, self.functions_enabled - 1)

                            self.log_activity(f"Функция {function_id} автоматически " f"переведена в спящий режим")

        except Exception:
            self.log_activity("Ошибка в методе", "error")

        return sleep_count

    def _start_sleep_management(self):
        """Запуск автоматического управления спящим режимом"""
        try:
            if self.sleep_management_thread and self.sleep_management_thread.is_alive():
                return

            self.sleep_management_stop_event.clear()
            self.sleep_management_active = True
            self.sleep_management_thread = threading.Thread(
                target=self._sleep_management_worker, name="SleepManagementWorker", daemon=True
            )
            self.sleep_management_thread.start()

            self.log_activity("Автоматическое управление спящим режимом запущено")

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _stop_sleep_management(self):
        """Остановка автоматического управления спящим режимом"""
        try:
            if not self.sleep_management_active:
                return

            self.sleep_management_stop_event.set()
            self.sleep_management_active = False

            if self.sleep_management_thread and self.sleep_management_thread.is_alive():
                self.sleep_management_thread.join(timeout=5)

            self.log_activity("Автоматическое управление спящим режимом остановлено")

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _sleep_management_worker(self):
        """Рабочий поток для автоматического управления спящим режимом"""
        while not self.sleep_management_stop_event.is_set():
            try:
                # Выполняем автоматическое управление спящим режимом
                sleep_count = self.auto_sleep_management()

                if sleep_count > 0:
                    self.auto_sleep_count += sleep_count

                    # Отправляем метрики в мониторинг
                    self._update_monitoring_metrics()

                    # Отправляем алерт если много функций переведено в сон
                    if sleep_count > 10:  # Более 10 функций за раз
                        from security.advanced_monitoring_manager import (
                            AlertSeverity,
                        )

                        self._send_monitoring_alert(
                            alert_id=f"mass_sleep_{int(time.time())}",
                            title=(f"Mass Sleep Transition: " f"{sleep_count} functions"),
                            message=(f"{sleep_count} functions were automatically " f"put to sleep"),
                            severity=AlertSeverity.INFO,
                            metric_name="sfm_sleeping_functions_count",
                            current_value=sleep_count,
                        )

                        # Мониторинг безопасности для массового перевода
                        self._monitor_function_security("system", "mass_sleep", {"count": sleep_count})

                    self.log_activity(f"Автоматически переведено в сон: " f"{sleep_count} функций")

                # Ждем до следующей проверки
                self.sleep_management_stop_event.wait(self.sleep_check_interval)

            except Exception:
                self.log_activity("Ошибка в методе", "error")
                # Ждем 60 секунд перед повторной попыткой
                self.sleep_management_stop_event.wait(60)

    def get_sleep_statistics(self) -> Dict[str, Any]:
        """Получение статистики спящего режима"""
        return {
            "sleep_transitions": self.sleep_transitions,
            "wake_transitions": self.wake_transitions,
            "auto_sleep_count": self.auto_sleep_count,
            "manual_sleep_count": self.manual_sleep_count,
            "manual_wake_count": self.manual_wake_count,
            "functions_sleeping": self.functions_sleeping,
            "sleep_management_active": self.sleep_management_active,
            "sleep_check_interval": self.sleep_check_interval,
            "default_sleep_hours": self.default_sleep_hours,
        }

    def configure_sleep_mode(
        self,
        enable_sleep_mode: bool = None,
        sleep_check_interval: int = None,
        default_sleep_hours: int = None,
        auto_sleep_enabled: bool = None,
        sleep_grace_period: int = None,
    ) -> bool:
        """Конфигурация спящего режима"""
        try:
            with self.function_lock:
                if enable_sleep_mode is not None:
                    self.enable_sleep_mode = enable_sleep_mode

                if sleep_check_interval is not None:
                    self.sleep_check_interval = sleep_check_interval

                if default_sleep_hours is not None:
                    self.default_sleep_hours = default_sleep_hours

                if auto_sleep_enabled is not None:
                    self.auto_sleep_enabled = auto_sleep_enabled

                if sleep_grace_period is not None:
                    self.sleep_grace_period = sleep_grace_period

                # Перезапускаем управление спящим режимом если нужно
                if self.enable_sleep_mode and self.auto_sleep_enabled:
                    if not self.sleep_management_active:
                        self._start_sleep_management()
                else:
                    if self.sleep_management_active:
                        self._stop_sleep_management()

                self.log_activity("Конфигурация спящего режима обновлена")
                return True

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def _send_monitoring_metric(
        self, metric_name: str, value: float, metric_type: MetricType = MetricType.SYSTEM, tags: Dict[str, str] = None
    ):
        """Отправка метрики в систему мониторинга"""
        try:
            if tags is None:
                tags = {}

            # Добавляем теги SFM
            tags.update({"component": "SafeFunctionManager", "manager_name": self.name})

            advanced_monitoring_manager.add_metric(name=metric_name, value=value, metric_type=metric_type, tags=tags)
        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _send_monitoring_alert(
        self,
        alert_id: str,
        title: str,
        message: str,
        severity,
        metric_name: str = None,
        threshold_value: float = None,
        current_value: float = None,
    ):
        """Отправка алерта в систему мониторинга"""
        try:
            from security.advanced_monitoring_manager import AlertSeverity

            # Преобразуем строку в AlertSeverity если нужно
            if isinstance(severity, str):
                severity = AlertSeverity(severity)

            advanced_monitoring_manager.add_alert(
                alert_id=alert_id,
                title=title,
                message=message,
                severity=severity,
                metric_name=metric_name or "sfm_general",
                threshold_value=threshold_value or 0,
                current_value=current_value or 0,
                tags={"component": "SafeFunctionManager", "manager_name": self.name},
            )
        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _setup_monitoring_rules(self):
        """Настройка правил мониторинга для SFM"""
        try:
            from security.advanced_monitoring_manager import MonitoringRule

            # Правило для критических функций в спящем режиме
            critical_sleep_rule = MonitoringRule(
                rule_id="sfm_critical_sleeping",
                name="Critical Functions Sleeping",
                metric_name="sfm_critical_sleeping_count",
                condition=">",
                threshold=0,
                severity=AlertSeverity.WARNING,
                cooldown=300,
            )
            advanced_monitoring_manager.add_monitoring_rule(critical_sleep_rule)

            # Правило для высокого количества спящих функций
            high_sleep_rule = MonitoringRule(
                rule_id="sfm_high_sleeping_count",
                name="High Sleeping Functions Count",
                metric_name="sfm_sleeping_functions_count",
                condition=">",
                threshold=50,  # Более 50 спящих функций
                severity=AlertSeverity.INFO,
                cooldown=600,
            )
            advanced_monitoring_manager.add_monitoring_rule(high_sleep_rule)

            # Правило для ошибок в управлении спящим режимом
            sleep_error_rule = MonitoringRule(
                rule_id="sfm_sleep_errors",
                name="Sleep Management Errors",
                metric_name="sfm_sleep_errors_count",
                condition=">",
                threshold=0,
                severity=AlertSeverity.ERROR,
                cooldown=60,
            )
            advanced_monitoring_manager.add_monitoring_rule(sleep_error_rule)

            self.log_activity("Правила мониторинга SFM настроены")

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _update_monitoring_metrics(self):
        """Обновление метрик для мониторинга"""
        try:
            # Общее количество функций
            total_functions = len(self.functions)
            self._send_monitoring_metric("sfm_total_functions", total_functions)

            # Количество спящих функций
            sleeping_count = len([f for f in self.functions.values() if f.status == FunctionStatus.SLEEPING])
            self._send_monitoring_metric("sfm_sleeping_functions_count", sleeping_count)

            # Количество критических функций в спящем режиме
            critical_sleeping = len(
                [f for f in self.functions.values() if (f.status == FunctionStatus.SLEEPING and f.is_critical)]
            )
            self._send_monitoring_metric("sfm_critical_sleeping_count", critical_sleeping)

            # Количество активных выполнений
            active_executions = len(self.active_executions)
            self._send_monitoring_metric("sfm_active_executions", active_executions)

            # Статистика спящего режима
            sleep_stats = self.get_sleep_statistics()
            self._send_monitoring_metric("sfm_sleep_transitions", sleep_stats["sleep_transitions"])
            self._send_monitoring_metric("sfm_wake_transitions", sleep_stats["wake_transitions"])
            self._send_monitoring_metric("sfm_auto_sleep_count", sleep_stats["auto_sleep_count"])

            # Производительность
            if hasattr(self, "execution_times") and self.execution_times:
                avg_execution_time = sum(self.execution_times) / len(self.execution_times)
                self._send_monitoring_metric("sfm_avg_execution_time", avg_execution_time, MetricType.PERFORMANCE)

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрик мониторинга: {e}", "error")

    def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Получение данных для дашборда мониторинга"""
        try:
            # Базовые метрики
            total_functions = len(self.functions)
            enabled_functions = len([f for f in self.functions.values() if f.status == FunctionStatus.ENABLED])
            sleeping_functions = len([f for f in self.functions.values() if f.status == FunctionStatus.SLEEPING])
            disabled_functions = len([f for f in self.functions.values() if f.status == FunctionStatus.DISABLED])

            # Статистика по типам функций
            function_types = {}
            for function in self.functions.values():
                func_type = function.function_type
                if func_type not in function_types:
                    function_types[func_type] = {"total": 0, "enabled": 0, "sleeping": 0, "disabled": 0}

                function_types[func_type]["total"] += 1
                if function.status == FunctionStatus.ENABLED:
                    function_types[func_type]["enabled"] += 1
                elif function.status == FunctionStatus.SLEEPING:
                    function_types[func_type]["sleeping"] += 1
                elif function.status == FunctionStatus.DISABLED:
                    function_types[func_type]["disabled"] += 1

            # Статистика спящего режима
            sleep_stats = self.get_sleep_statistics()

            return {
                "manager_name": self.name,
                "status": self.status.value,
                "total_functions": total_functions,
                "enabled_functions": enabled_functions,
                "sleeping_functions": sleeping_functions,
                "disabled_functions": disabled_functions,
                "function_types": function_types,
                "sleep_statistics": sleep_stats,
                "active_executions": len(self.active_executions),
                "uptime_seconds": ((datetime.now() - self.start_time).total_seconds() if self.start_time else 0),
                "last_activity": (self.last_activity.isoformat() if self.last_activity else None),
            }

        except Exception as e:
            self.log_activity("Ошибка в методе", "error")
            return {"error": str(e)}

    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Сбор метрик производительности"""
        try:
            import psutil

            # Системные метрики - ИСПРАВЛЕНО: убран блокирующий вызов
            # Было 1 секунда, стало 0.1
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Метрики SFM
            total_functions = len(self.functions)
            enabled_functions = len([f for f in self.functions.values() if f.status == FunctionStatus.ENABLED])
            sleeping_functions = len([f for f in self.functions.values() if f.status == FunctionStatus.SLEEPING])
            active_executions = len(self.active_executions)

            # Время выполнения
            avg_execution_time = 0
            if hasattr(self, "execution_times") and self.execution_times:
                avg_execution_time = sum(self.execution_times) / len(self.execution_times)

            metrics = {
                "timestamp": datetime.now(),
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "total_functions": total_functions,
                "enabled_functions": enabled_functions,
                "sleeping_functions": sleeping_functions,
                "active_executions": active_executions,
                "avg_execution_time": avg_execution_time,
                "sleep_transitions": self.sleep_transitions,
                "wake_transitions": self.wake_transitions,
            }

            # Сохраняем метрики
            self.performance_metrics.append(metrics)

            # Ограничиваем количество сохраненных метрик
            if len(self.performance_metrics) > 1000:
                self.performance_metrics = self.performance_metrics[-500:]

            return metrics

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return {}

    def _optimize_sleep_management(self) -> bool:
        """Оптимизация управления спящим режимом"""
        try:
            if not self.optimization_enabled:
                return False

            # Собираем текущие метрики
            current_metrics = self._collect_performance_metrics()
            if not current_metrics:
                return False

            # Анализируем производительность
            optimization_applied = False

            # Оптимизация 1: Увеличение интервала проверки при низкой нагрузке
            if current_metrics.get("cpu_usage", 0) < 30 and current_metrics.get("sleeping_functions", 0) > 10:

                # Максимум 60 секунд
                new_interval = min(self.sleep_check_interval * 2, 60)
                if new_interval != self.sleep_check_interval:
                    self.sleep_check_interval = new_interval
                    self.log_activity(f"Оптимизация: увеличен интервал проверки до " f"{new_interval}с")
                    optimization_applied = True

            # Оптимизация 2: Уменьшение интервала при высокой нагрузке
            elif current_metrics.get("cpu_usage", 0) > 70 and current_metrics.get("sleeping_functions", 0) < 5:

                # Минимум 5 секунд
                new_interval = max(self.sleep_check_interval // 2, 5)
                if new_interval != self.sleep_check_interval:
                    self.sleep_check_interval = new_interval
                    self.log_activity(f"Оптимизация: уменьшен интервал проверки до " f"{new_interval}с")
                    optimization_applied = True

            # Оптимизация 3: Адаптивное время сна
            if current_metrics.get("memory_usage", 0) > 80:
                # При высокой нагрузке памяти - более агрессивный сон
                # Минимум 3.6 секунды
                new_sleep_hours = max(self.default_sleep_hours * 0.5, 0.001)
                if new_sleep_hours != self.default_sleep_hours:
                    self.default_sleep_hours = new_sleep_hours
                    self.log_activity(f"Оптимизация: уменьшено время до сна до " f"{new_sleep_hours}ч")
                    optimization_applied = True

            elif current_metrics.get("memory_usage", 0) < 30:
                # При низкой нагрузке памяти - менее агрессивный сон
                # Максимум 24 часа
                new_sleep_hours = min(self.default_sleep_hours * 2, 24)
                if new_sleep_hours != self.default_sleep_hours:
                    self.default_sleep_hours = new_sleep_hours
                    self.log_activity(f"Оптимизация: увеличено время до сна до {new_sleep_hours}ч")
                    optimization_applied = True

            # Отправляем метрики в мониторинг
            if optimization_applied:
                self._send_monitoring_metric("sfm_optimization_applied", 1, MetricType.PERFORMANCE)
                self._send_monitoring_metric(
                    "sfm_sleep_check_interval", self.sleep_check_interval, MetricType.PERFORMANCE
                )
                self._send_monitoring_metric(
                    "sfm_default_sleep_hours", self.default_sleep_hours, MetricType.PERFORMANCE
                )

            return optimization_applied

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def _optimize_function_execution(self) -> bool:
        """Оптимизация выполнения функций"""
        try:
            if not self.optimization_enabled:
                return False

            # Собираем метрики
            current_metrics = self._collect_performance_metrics()
            if not current_metrics:
                return False

            optimization_applied = False

            # Оптимизация 1: Очистка старых метрик выполнения
            if hasattr(self, "execution_times") and len(self.execution_times) > 1000:
                self.execution_times = self.execution_times[-500:]  # Оставляем только последние 500
                self.log_activity("Оптимизация: очищены старые метрики выполнения")
                optimization_applied = True

            # Оптимизация 2: Очистка неактивных выполнений
            if len(self.active_executions) > 100:
                # Удаляем выполнения старше 1 часа
                current_time = datetime.now()
                old_executions = []
                for exec_id, exec_data in self.active_executions.items():
                    if (current_time - exec_data.get("start_time", current_time)).total_seconds() > 3600:
                        old_executions.append(exec_id)

                for exec_id in old_executions:
                    del self.active_executions[exec_id]

                if old_executions:
                    self.log_activity(f"Оптимизация: удалено {len(old_executions)} старых выполнений")
                    optimization_applied = True

            # Оптимизация 3: Адаптивное управление потоками
            if current_metrics.get("cpu_usage", 0) > 80:
                # При высокой нагрузке CPU - принудительный сон неактивных функций
                inactive_count = 0
                for function in self.functions.values():
                    if (
                        function.status == FunctionStatus.ENABLED
                        and not function.is_critical
                        and function.last_activity
                        and (datetime.now() - function.last_activity).total_seconds() > 300
                    ):  # 5 минут

                        self.sleep_function(function.function_id)
                        inactive_count += 1

                if inactive_count > 0:
                    self.log_activity(
                        f"Оптимизация: принудительно переведено в сон {inactive_count} неактивных функций"
                    )
                    optimization_applied = True

            return optimization_applied

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def _run_performance_optimization(self):
        """Запуск оптимизации производительности"""
        try:
            if not self.optimization_enabled:
                return

            # Оптимизация управления спящим режимом
            sleep_optimized = self._optimize_sleep_management()

            # Оптимизация выполнения функций
            execution_optimized = self._optimize_function_execution()

            # Общая оптимизация через PerformanceOptimizer
            if hasattr(self.performance_optimizer, "optimize_system"):
                system_optimized = self.performance_optimizer.optimize_system()
            else:
                system_optimized = False

            # Логируем результаты
            if sleep_optimized or execution_optimized or system_optimized:
                self.log_activity("Оптимизация производительности выполнена")

                # Отправляем метрики
                self._send_monitoring_metric(
                    "sfm_optimization_sleep", 1 if sleep_optimized else 0, MetricType.PERFORMANCE
                )
                self._send_monitoring_metric(
                    "sfm_optimization_execution", 1 if execution_optimized else 0, MetricType.PERFORMANCE
                )
                self._send_monitoring_metric(
                    "sfm_optimization_system", 1 if system_optimized else 0, MetricType.PERFORMANCE
                )

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        try:
            current_metrics = self._collect_performance_metrics()

            # Статистика оптимизации
            optimization_stats = {
                "optimization_enabled": self.optimization_enabled,
                "optimization_interval": self.optimization_interval,
                "total_optimizations": len(self.optimization_results),
                "recent_metrics_count": len(self.performance_metrics),
                "sleep_check_interval": self.sleep_check_interval,
                "default_sleep_hours": self.default_sleep_hours,
            }

            return {
                "current_metrics": current_metrics,
                "optimization_stats": optimization_stats,
                "recent_metrics": self.performance_metrics[-10:] if self.performance_metrics else [],
                "optimization_results": self.optimization_results[-5:] if self.optimization_results else [],
            }

        except Exception as e:
            self.log_activity("Ошибка в методе", "error")
            return {"error": str(e)}

    def configure_performance_optimization(
        self, optimization_enabled: bool = None, optimization_interval: int = None
    ) -> bool:
        """Конфигурация оптимизации производительности"""
        try:
            with self.function_lock:
                if optimization_enabled is not None:
                    self.optimization_enabled = optimization_enabled

                if optimization_interval is not None:
                    self.optimization_interval = max(60, optimization_interval)  # Минимум 1 минута

                self.log_activity("Конфигурация оптимизации производительности обновлена")
                return True

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def _setup_security_monitoring_rules(self):
        """Настройка правил мониторинга безопасности для SFM"""
        try:
            if not self.monitoring_integration_enabled:
                return

            # Правило 1: Мониторинг критических функций в спящем режиме
            critical_sleep_rule = MonitoringRule(
                rule_id="sfm_critical_sleeping_security",
                name="Critical Functions Sleeping Security Alert",
                description="Security alert when critical functions are sleeping",
                monitoring_type="REAL_TIME",
                condition="critical_functions_sleeping > 0",
                severity="HIGH",
                enabled=True,
                cooldown=300,
            )
            self.monitoring_rules["critical_sleeping"] = critical_sleep_rule
            self.security_monitoring.add_monitoring_rule(critical_sleep_rule)

            # Правило 2: Мониторинг массового перевода в сон
            mass_sleep_rule = MonitoringRule(
                rule_id="sfm_mass_sleep_security",
                name="Mass Sleep Transition Security Alert",
                description="Security alert for mass sleep transitions",
                monitoring_type="EVENT_DRIVEN",
                condition="sleep_transitions_per_minute > 10",
                severity="MEDIUM",
                enabled=True,
                cooldown=600,
            )
            self.monitoring_rules["mass_sleep"] = mass_sleep_rule
            self.security_monitoring.add_monitoring_rule(mass_sleep_rule)

            # Правило 3: Мониторинг ошибок в управлении спящим режимом
            sleep_error_rule = MonitoringRule(
                rule_id="sfm_sleep_errors_security",
                name="Sleep Management Errors Security Alert",
                description="Security alert for sleep management errors",
                monitoring_type="EVENT_DRIVEN",
                condition="sleep_errors > 0",
                severity="HIGH",
                enabled=True,
                cooldown=60,
            )
            self.monitoring_rules["sleep_errors"] = sleep_error_rule
            self.security_monitoring.add_monitoring_rule(sleep_error_rule)

            # Правило 4: Мониторинг производительности SFM
            performance_rule = MonitoringRule(
                rule_id="sfm_performance_security",
                name="SFM Performance Security Alert",
                description="Security alert for SFM performance issues",
                monitoring_type="PERIODIC",
                condition="avg_execution_time > 5.0",
                severity="MEDIUM",
                enabled=True,
                cooldown=300,
            )
            self.monitoring_rules["performance"] = performance_rule
            self.security_monitoring.add_monitoring_rule(performance_rule)

            self.log_activity("Правила мониторинга безопасности SFM настроены")

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _send_security_alert(
        self,
        alert_id: str,
        title: str,
        message: str,
        severity: str = "MEDIUM",
        component: str = "SafeFunctionManager",
        alert_type: str = "FUNCTION_MANAGEMENT",
    ):
        """Отправка алерта безопасности"""
        try:
            if not self.monitoring_integration_enabled:
                return

            alert = SecurityAlert(
                alert_id=alert_id,
                title=title,
                message=message,
                severity=severity,
                alert_type=alert_type,
                component=component,
                source="SafeFunctionManager",
                timestamp=datetime.now(),
                status="ACTIVE",
            )

            # Добавляем алерт в SecurityMonitoringManager
            self.security_monitoring.add_alert(alert)

            # Сохраняем локально
            self.security_alerts.append(alert)

            # Ограничиваем количество сохраненных алертов
            if len(self.security_alerts) > 1000:
                self.security_alerts = self.security_alerts[-500:]

            self.log_activity(f"Отправлен алерт безопасности: {alert_id}")

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _monitor_function_security(self, function_id: str, action: str, details: Dict[str, Any] = None):
        """Мониторинг безопасности функций"""
        try:
            if not self.monitoring_integration_enabled:
                return

            function = self.functions.get(function_id)
            if not function:
                return

            # Проверяем критические функции
            if function.is_critical and action == "sleep":
                self._send_security_alert(
                    alert_id=f"critical_sleep_{function_id}_{int(time.time())}",
                    title=f"Critical Function Sleeping: {function.name}",
                    message=f"Critical function {function.name} has been put to sleep",
                    severity="HIGH",
                    component="SafeFunctionManager",
                    alert_type="CRITICAL_FUNCTION_SLEEP",
                )

            # Мониторинг массовых операций
            if action == "mass_sleep" and details:
                sleep_count = details.get("count", 0)
                if sleep_count > 10:
                    self._send_security_alert(
                        alert_id=f"mass_sleep_{int(time.time())}",
                        title=f"Mass Sleep Transition: {sleep_count} functions",
                        message=f"{sleep_count} functions were put to sleep simultaneously",
                        severity="MEDIUM",
                        component="SafeFunctionManager",
                        alert_type="MASS_SLEEP_TRANSITION",
                    )

            # Мониторинг ошибок
            if action == "error" and details:
                error_message = details.get("error", "Unknown error")
                self._send_security_alert(
                    alert_id=f"sfm_error_{function_id}_{int(time.time())}",
                    title=f"SFM Error: {function.name}",
                    message=f"Error in function {function.name}: {error_message}",
                    severity="HIGH",
                    component="SafeFunctionManager",
                    alert_type="FUNCTION_ERROR",
                )

        except Exception as e:
            self.log_activity(f"Ошибка мониторинга безопасности функции {function_id}: {e}", "error")

    def _update_security_monitoring_data(self):
        """Обновление данных мониторинга безопасности"""
        try:
            if not self.monitoring_integration_enabled:
                return

            # Собираем данные для мониторинга
            monitoring_data = {
                "critical_functions_sleeping": len(
                    [f for f in self.functions.values() if f.is_critical and f.status == FunctionStatus.SLEEPING]
                ),
                "total_functions": len(self.functions),
                "sleeping_functions": len([f for f in self.functions.values() if f.status == FunctionStatus.SLEEPING]),
                "enabled_functions": len([f for f in self.functions.values() if f.status == FunctionStatus.ENABLED]),
                "sleep_transitions_per_minute": self.sleep_transitions,  # Упрощенная метрика
                "sleep_errors": 0,  # Будет обновляться при ошибках
                "avg_execution_time": 0,  # Будет обновляться из метрик производительности
                "last_update": datetime.now().isoformat(),
            }

            # Обновляем данные в SecurityMonitoringManager
            self.security_monitoring.monitoring_data["sfm"] = monitoring_data

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def get_security_monitoring_status(self) -> Dict[str, Any]:
        """Получение статуса мониторинга безопасности"""
        try:
            if not self.monitoring_integration_enabled:
                return {"enabled": False, "message": "Security monitoring integration disabled"}

            # Получаем статус от SecurityMonitoringManager
            security_status = self.security_monitoring.get_monitoring_stats()

            # Добавляем специфичные для SFM данные
            sfm_security_data = {
                "enabled": True,
                "monitoring_rules_count": len(self.monitoring_rules),
                "security_alerts_count": len(self.security_alerts),
                "recent_alerts": [alert.to_dict() for alert in self.security_alerts[-5:]],
                "critical_functions_sleeping": len(
                    [f for f in self.functions.values() if f.is_critical and f.status == FunctionStatus.SLEEPING]
                ),
                "monitoring_data": self.security_monitoring.monitoring_data.get("sfm", {}),
                "security_monitoring_status": security_status,
            }

            return sfm_security_data

        except Exception as e:
            self.log_activity("Ошибка в методе", "error")
            return {"enabled": False, "error": str(e)}

    def configure_security_monitoring(
        self, monitoring_integration_enabled: bool = None, alert_retention_days: int = None
    ) -> bool:
        """Конфигурация мониторинга безопасности"""
        try:
            with self.function_lock:
                if monitoring_integration_enabled is not None:
                    self.monitoring_integration_enabled = monitoring_integration_enabled

                if alert_retention_days is not None:
                    self.security_monitoring.alert_retention_days = alert_retention_days

                # Перезапускаем мониторинг если нужно
                if self.monitoring_integration_enabled:
                    self._setup_security_monitoring_rules()

                self.log_activity("Конфигурация мониторинга безопасности обновлена")
                return True

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def start(self) -> bool:
        """Запуск менеджера безопасных функций"""
        try:
            self.log_activity(f"Запуск менеджера безопасных функций {self.name}")
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(f"Менеджер безопасных функций {self.name} успешно запущен")
            return True
        except Exception:
            self.status = ComponentStatus.ERROR
            self.log_activity("Ошибка в методе", "error")
            return False

    def stop(self) -> bool:
        """Остановка менеджера безопасных функций"""
        try:
            self.log_activity(f"Остановка менеджера безопасных функций {self.name}")

            # Остановка управления спящим режимом
            self._stop_sleep_management()

            # Остановка AutoScalingEngine
            if hasattr(self, "auto_scaling_engine") and self.auto_scaling_engine:
                try:
                    self.auto_scaling_engine.stop()
                    self.log_activity("Ошибка в методе", "error")
                except Exception:
                    self.log_activity("Ошибка в методе", "error")

            # Остановка всех активных выполнений
            with self.execution_lock:
                self.active_executions.clear()

            # Отключение всех функций
            for function_id in list(self.functions.keys()):
                self.disable_function(function_id)

            self.status = ComponentStatus.STOPPED
            self.log_activity(f"Менеджер безопасных функций {self.name} успешно остановлен")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера безопасных функций {self.name}: {e}",
                "error",
            )
            return False

    def _validate_function_id(self, function_id: str) -> Tuple[bool, str]:
        """
        Валидация идентификатора функции

        Args:
            function_id (str): Идентификатор функции для валидации

        Returns:
            Tuple[bool, str]: (валидный, сообщение об ошибке)
        """
        try:
            if not function_id:
                return False, "Идентификатор функции не может быть пустым"

            if not isinstance(function_id, str):
                return False, "Идентификатор функции должен быть строкой"

            if len(function_id) < 3:
                return False, "Идентификатор функции должен содержать минимум 3 символа"

            if len(function_id) > 100:
                return False, "Идентификатор функции не должен превышать 100 символов"

            # Проверка на недопустимые символы
            import re

            if not re.match(r"^[a-zA-Z0-9_-]+$", function_id):
                return False, "Идентификатор функции может содержать только буквы, цифры, дефисы и подчеркивания"

            # Проверка на SQL инъекции
            dangerous_patterns = [
                ";",
                "--",
                "/*",
                "*/",
                "xp_",
                "sp_",
                "exec",
                "execute",
                "select",
                "insert",
                "update",
                "delete",
                "drop",
                "create",
                "alter",
            ]
            function_id_lower = function_id.lower()
            for pattern in dangerous_patterns:
                if pattern in function_id_lower:
                    return False, f"Идентификатор функции содержит потенциально опасный паттерн: {pattern}"

            return True, "Идентификатор функции валиден"

        except Exception as e:
            return False, f"Ошибка валидации идентификатора функции: {e}"

    def _validate_function_name(self, name: str) -> Tuple[bool, str]:
        """
        Валидация названия функции

        Args:
            name (str): Название функции для валидации

        Returns:
            Tuple[bool, str]: (валидное, сообщение об ошибке)
        """
        try:
            if not name:
                return False, "Название функции не может быть пустым"

            if not isinstance(name, str):
                return False, "Название функции должно быть строкой"

            if len(name) < 3:
                return False, "Название функции должно содержать минимум 3 символа"

            if len(name) > 200:
                return False, "Название функции не должно превышать 200 символов"

            # Проверка на XSS атаки
            dangerous_patterns = ["<script", "</script", "javascript:", "onload=", "onerror=", "onclick="]
            name_lower = name.lower()
            for pattern in dangerous_patterns:
                if pattern in name_lower:
                    return False, f"Название функции содержит потенциально опасный паттерн: {pattern}"

            return True, "Название функции валидно"

        except Exception as e:
            return False, f"Ошибка валидации названия функции: {e}"

    def _validate_function_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Валидация параметров функции

        Args:
            params (Dict[str, Any]): Параметры для валидации

        Returns:
            Tuple[bool, str]: (валидные, сообщение об ошибке)
        """
        try:
            if params is None:
                return True, "Параметры не предоставлены"

            if not isinstance(params, dict):
                return False, "Параметры должны быть словарем"

            if len(params) > 50:
                return False, "Количество параметров не должно превышать 50"

            for key, value in params.items():
                # Валидация ключа
                if not isinstance(key, str):
                    return False, f"Ключ параметра должен быть строкой: {key}"

                if len(key) > 100:
                    return False, f"Ключ параметра слишком длинный: {key}"

                # Проверка на SQL инъекции в ключе
                dangerous_patterns = [";", "--", "/*", "*/", "xp_", "sp_", "exec", "execute"]
                key_lower = key.lower()
                for pattern in dangerous_patterns:
                    if pattern in key_lower:
                        return False, f"Ключ параметра содержит опасный паттерн: {key}"

                # Валидация значения
                if isinstance(value, str):
                    if len(value) > 10000:
                        return False, f"Значение параметра слишком длинное: {key}"

                    # Проверка на XSS в строковых значениях
                    dangerous_patterns = ["<script", "</script", "javascript:", "onload=", "onerror="]
                    value_lower = value.lower()
                    for pattern in dangerous_patterns:
                        if pattern in value_lower:
                            return False, f"Значение параметра содержит опасный паттерн: {key}"

                elif isinstance(value, (int, float, bool)):
                    # Числовые и булевы значения безопасны
                    continue

                elif isinstance(value, (list, dict)):
                    # Проверяем вложенные структуры
                    if len(str(value)) > 50000:
                        return False, f"Значение параметра слишком большое: {key}"

                else:
                    return False, f"Неподдерживаемый тип параметра: {key} ({type(value).__name__})"

            return True, "Параметры валидны"

        except Exception as e:
            return False, f"Ошибка валидации параметров: {e}"

    def _sanitize_input(self, input_data: str) -> str:
        """
        Санитизация входных данных

        Args:
            input_data (str): Данные для санитизации

        Returns:
            str: Санитизированные данные
        """
        try:
            if not isinstance(input_data, str):
                return str(input_data)

            # Удаляем потенциально опасные символы
            import html

            sanitized = html.escape(input_data)

            # Удаляем лишние пробелы
            sanitized = " ".join(sanitized.split())

            # Ограничиваем длину
            if len(sanitized) > 1000:
                sanitized = sanitized[:1000] + "..."

            return sanitized

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return str(input_data)

    def _log_security_event(self, event_type: str, function_id: str, details: Dict[str, Any] = None):
        """
        Логирование события безопасности

        Args:
            event_type (str): Тип события безопасности
            function_id (str): ID функции
            details (Dict[str, Any]): Дополнительные детали
        """
        try:
            security_event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "function_id": function_id,
                "manager_name": self.name,
                "details": details or {},
            }

            # Логируем событие
            self.log_activity("Ошибка в методе", "error")

            # Отправляем в мониторинг безопасности
            self._monitor_function_security(function_id, "security_event", security_event)

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _check_security_threats(self, function_id: str, params: Dict[str, Any] = None) -> bool:
        """
        Проверка на угрозы безопасности

        Args:
            function_id (str): ID функции
            params (Dict[str, Any]): Параметры функции

        Returns:
            bool: True если угроз не обнаружено
        """
        try:
            threats_detected = False

            # Проверка на подозрительную активность
            if function_id in self.functions:
                function = self.functions[function_id]

                # Проверка частоты вызовов
                if hasattr(function, "last_execution") and function.last_execution:
                    time_since_last = (datetime.now() - function.last_execution).total_seconds()
                    if time_since_last < 1:  # Менее секунды между вызовами
                        self._log_security_event(
                            "RAPID_EXECUTION",
                            function_id,
                            {"time_since_last": time_since_last, "execution_count": function.execution_count},
                        )
                        threats_detected = True

                # Проверка на аномальное количество ошибок
                if function.error_count > 10 and function.execution_count > 0:
                    error_rate = (function.error_count / function.execution_count) * 100
                    if error_rate > 50:  # Более 50% ошибок
                        self._log_security_event(
                            "HIGH_ERROR_RATE",
                            function_id,
                            {
                                "error_count": function.error_count,
                                "execution_count": function.execution_count,
                                "error_rate": error_rate,
                            },
                        )
                        threats_detected = True

            # Проверка параметров на подозрительные паттерны
            if params:
                for key, value in params.items():
                    if isinstance(value, str):
                        # Проверка на попытки инъекций
                        suspicious_patterns = [
                            "union select",
                            "drop table",
                            "delete from",
                            "insert into",
                            "update set",
                            "exec(",
                            "eval(",
                            "system(",
                            "shell_exec",
                        ]

                        value_lower = value.lower()
                        for pattern in suspicious_patterns:
                            if pattern in value_lower:
                                self._log_security_event(
                                    "INJECTION_ATTEMPT",
                                    function_id,
                                    {"parameter": key, "value": value[:100], "pattern": pattern},  # Первые 100 символов
                                )
                                threats_detected = True
                                break

            return not threats_detected

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def get_security_status(self) -> Dict[str, Any]:
        """
        Получение статуса безопасности

        Returns:
            Dict[str, Any]: Статус безопасности
        """
        try:
            # Статистика безопасности
            security_stats = {
                "total_functions": len(self.functions),
                "critical_functions": len([f for f in self.functions.values() if f.is_critical]),
                "high_security_functions": len(
                    [f for f in self.functions.values() if f.security_level == SecurityLevel.HIGH]
                ),
                "medium_security_functions": len(
                    [f for f in self.functions.values() if f.security_level == SecurityLevel.MEDIUM]
                ),
                "low_security_functions": len(
                    [f for f in self.functions.values() if f.security_level == SecurityLevel.LOW]
                ),
                "functions_with_errors": len([f for f in self.functions.values() if f.error_count > 0]),
                "active_executions": len(self.active_executions),
                "security_alerts_count": len(self.security_alerts),
            }

            # Анализ рисков
            risk_analysis = {"high_risk_functions": [], "medium_risk_functions": [], "low_risk_functions": []}

            for function in self.functions.values():
                risk_score = 0

                # Критичность
                if function.is_critical:
                    risk_score += 3

                # Уровень безопасности
                if function.security_level == SecurityLevel.LOW:
                    risk_score += 2
                elif function.security_level == SecurityLevel.MEDIUM:
                    risk_score += 1

                # Частота ошибок
                if function.execution_count > 0:
                    error_rate = (function.error_count / function.execution_count) * 100
                    if error_rate > 30:
                        risk_score += 2
                    elif error_rate > 10:
                        risk_score += 1

                # Классификация риска
                if risk_score >= 4:
                    risk_analysis["high_risk_functions"].append(
                        {
                            "function_id": function.function_id,
                            "name": function.name,
                            "risk_score": risk_score,
                            "reasons": self._get_risk_reasons(function, risk_score),
                        }
                    )
                elif risk_score >= 2:
                    risk_analysis["medium_risk_functions"].append(
                        {
                            "function_id": function.function_id,
                            "name": function.name,
                            "risk_score": risk_score,
                            "reasons": self._get_risk_reasons(function, risk_score),
                        }
                    )
                else:
                    risk_analysis["low_risk_functions"].append(
                        {"function_id": function.function_id, "name": function.name, "risk_score": risk_score}
                    )

            return {
                "security_stats": security_stats,
                "risk_analysis": risk_analysis,
                "monitoring_status": self.get_security_monitoring_status(),
                "last_security_check": datetime.now().isoformat(),
            }

        except Exception as e:
            self.log_activity("Ошибка в методе", "error")
            return {"error": str(e)}

    def _get_risk_reasons(self, function, risk_score: int) -> List[str]:
        """
        Получение причин риска для функции

        Args:
            function: Объект функции
            risk_score (int): Оценка риска

        Returns:
            List[str]: Список причин риска
        """
        reasons = []

        if function.is_critical:
            reasons.append("Критическая функция")

        if function.security_level == SecurityLevel.LOW:
            reasons.append("Низкий уровень безопасности")

        if function.execution_count > 0:
            error_rate = (function.error_count / function.execution_count) * 100
            if error_rate > 30:
                reasons.append(f"Высокий процент ошибок ({error_rate:.1f}%)")
            elif error_rate > 10:
                reasons.append(f"Средний процент ошибок ({error_rate:.1f}%)")

        return reasons

    def _initialize_persistence(self):
        """Инициализация персистентности"""
        try:
            import os

            # Создаем директорию для данных если не существует
            self.data_dir = os.path.join(os.getcwd(), "data", "sfm")
            os.makedirs(self.data_dir, exist_ok=True)

            # Файл реестра функций
            self.registry_file = os.path.join(self.data_dir, "function_registry.json")

            # Добавляем атрибут _persistence_file для совместимости
            self._persistence_file = self.registry_file

            self.log_activity("Персистентность SFM инициализирована")

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _load_saved_functions(self):
        """Загрузка сохраненных функций и обработчиков"""
        try:
            import os

            print("🔍 DEBUG: _load_saved_functions() вызван!")
            self.log_activity("Начинаем загрузку сохраненных функций...")

            print(f"🔍 DEBUG: Проверяем файл: {self.registry_file}")
            print(f"🔍 DEBUG: Файл существует: {os.path.exists(self.registry_file)}")

            if os.path.exists(self.registry_file):
                print(f"🔍 DEBUG: Файл найден: {self.registry_file}")
                print("🔍 DEBUG: Начинаем чтение файла...")
                try:
                    import json

                    with open(self.registry_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    print("🔍 DEBUG: Файл прочитан успешно!")
                except Exception as e:
                    print(f"🔍 DEBUG: Ошибка чтения файла: {e}")
                    return

                print(f"🔍 DEBUG: Файл прочитан, данные: {data}")
                print(f"🔍 DEBUG: Ключи в data: {list(data.keys())}")
                print(f"🔍 DEBUG: functions в data: {data.get('functions', {})}")

                # Загружаем функции из файла
                functions_loaded = 0
                print(f"🔍 DEBUG: Найдено {len(data.get('functions', {}))} функций в файле")
                self.log_activity(f"Найдено {len(data.get('functions', {}))} функций в файле")

                print("🔍 DEBUG: Начинаем цикл загрузки функций...")
                for func_id, func_data in data.get("functions", {}).items():
                    try:
                        print(f"🔍 DEBUG: Загружаем функцию: {func_id}")
                        self.log_activity(f"Загружаем функцию: {func_id}")

                        # Создаем объект функции из сохраненных данных (перезаписываем существующие)
                        func = SecurityFunction(
                            function_id=func_data.get("function_id", func_id),
                            name=func_data.get("name", func_id),
                            description=func_data.get("description", ""),
                            function_type=func_data.get("function_type", "unknown"),
                            security_level=SecurityLevel(func_data.get("security_level", "MEDIUM")),
                        )

                        # Восстанавливаем состояние
                        func.status = FunctionStatus(func_data.get("status", "enabled"))
                        func.is_critical = func_data.get("is_critical", False)
                        func.execution_count = func_data.get("execution_count", 0)
                        func.success_count = func_data.get("success_count", 0)
                        func.error_count = func_data.get("error_count", 0)

                        self.functions[func_id] = func
                        functions_loaded += 1
                        print(f"🔍 DEBUG: Функция {func_id} загружена успешно")
                    except Exception as e:
                        print(f"🔍 DEBUG: ОШИБКА при загрузке функции {func_id}: {e}")
                        self.log_activity(f"Ошибка загрузки функции {func_id}: {e}", "error")
                        continue
                    self.log_activity(f"Функция {func_id} загружена успешно")

                # Загружаем обработчики из файла
                handlers_loaded = 0
                for func_id, handler_data in data.get("handlers", {}).items():
                    # Создаем обработчик на основе сохраненных данных (перезаписываем существующие)
                    handler_name = handler_data.get("function_name", "unknown")

                    # Для простых функций создаем заглушку
                    def create_handler_wrapper(func_id, handler_name):
                        def wrapper(*args, **kwargs):
                            return {
                                "status": "success",
                                "function_id": func_id,
                                "handler_name": handler_name,
                                "message": f"Обработчик {handler_name} выполнен успешно",
                            }

                        return wrapper

                    self.function_handlers[func_id] = create_handler_wrapper(func_id, handler_name)
                    handlers_loaded += 1

                self.log_activity(f"Загружено {functions_loaded} функций и {handlers_loaded} обработчиков")
            else:
                self.log_activity("Файл реестра не найден, начинаем с пустого состояния")

        except Exception as e:
            self.log_activity(f"Ошибка загрузки сохраненных функций: {e}", "error")

    # ==================== SERVICEMESHMANAGER ИНТЕГРАЦИЯ ====================

    def get_service_mesh_manager(self) -> Optional[ServiceMeshManager]:
        """Получение экземпляра ServiceMeshManager"""
        return self.service_mesh_manager

    def is_service_mesh_enabled(self) -> bool:
        """Проверка, включен ли ServiceMeshManager"""
        return self.service_mesh_enabled and self.service_mesh_manager is not None

    def register_service_in_mesh(self, service_info: ServiceInfo) -> bool:
        """Регистрация сервиса в ServiceMeshManager"""
        try:
            if not self.is_service_mesh_enabled():
                self.log_activity("Ошибка в методе", "error")
                return False

            result = self.service_mesh_manager.register_service(service_info)
            self.log_activity("Ошибка в методе", "error")
            return result

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def unregister_service_from_mesh(self, service_id: str) -> bool:
        """Отмена регистрации сервиса из ServiceMeshManager"""
        try:
            if not self.is_service_mesh_enabled():
                self.log_activity("Ошибка в методе", "error")
                return False

            result = self.service_mesh_manager.unregister_service(service_id)
            self.log_activity("Ошибка в методе", "error")
            return result

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def get_service_health(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Получение состояния здоровья сервиса"""
        try:
            if not self.is_service_mesh_enabled():
                return None

            health_summary = self.service_mesh_manager.get_service_health_summary(service_id)
            if health_summary:
                return {
                    "service_id": service_id,
                    "status": getattr(health_summary, "status", "unknown"),
                    "is_healthy": getattr(health_summary, "is_healthy", False),
                    "response_time": getattr(health_summary, "response_time", 0),
                    "last_check": getattr(health_summary, "last_check", None),
                }
            return None

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return None

    def get_service_metrics(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Получение метрик сервиса"""
        try:
            if not self.is_service_mesh_enabled():
                return None

            # Используем get_service_status для получения метрик
            status = self.service_mesh_manager.get_service_status(service_id)
            if status:
                return {
                    "service_id": service_id,
                    "metrics": status.get("metrics", {}),
                    "performance": status.get("performance", {}),
                    "statistics": status.get("statistics", {}),
                }
            return None

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return None

    def list_services_in_mesh(self) -> List[Dict[str, Any]]:
        """Получение списка всех сервисов в ServiceMesh"""
        try:
            if not self.is_service_mesh_enabled():
                return []

            # Используем get_all_health_summaries для получения списка сервисов
            health_summaries = self.service_mesh_manager.get_all_health_summaries()
            services = []
            for service_id, summary in health_summaries.items():
                services.append(
                    {
                        "service_id": service_id,
                        "name": getattr(summary, "name", service_id),
                        "status": getattr(summary, "status", "unknown"),
                        "health": getattr(summary, "is_healthy", False),
                    }
                )
            return services

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return []

    def enable_service_mesh(self) -> bool:
        """Включение ServiceMeshManager"""
        try:
            if self.service_mesh_manager is not None:
                self.log_activity("Ошибка в методе", "error")
                return True

            self.service_mesh_enabled = True
            self._initialize_service_mesh_manager()

            if self.service_mesh_manager is not None:
                self.log_activity("Ошибка в методе", "error")
                return True
            else:
                self.log_activity("Ошибка в методе", "error")
                return False

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def disable_service_mesh(self) -> bool:
        """Отключение ServiceMeshManager"""
        try:
            if self.service_mesh_manager is None:
                self.log_activity("Ошибка в методе", "error")
                return True

            # Останавливаем ServiceMeshManager
            if hasattr(self.service_mesh_manager, "stop"):
                self.service_mesh_manager.stop()

            self.service_mesh_manager = None
            self.service_mesh_enabled = False

            self.log_activity("Ошибка в методе", "error")
            return True

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def get_service_mesh_status(self) -> Dict[str, Any]:
        """Получение статуса ServiceMeshManager"""
        try:
            status = {
                "enabled": self.service_mesh_enabled,
                "initialized": self.service_mesh_manager is not None,
                "config": self.service_mesh_config,
                "services_count": 0,
                "health_status": "unknown",
            }

            if self.service_mesh_manager:
                try:
                    services = self.list_services_in_mesh()
                    status["services_count"] = len(services)
                    status["health_status"] = "healthy"
                except Exception:
                    status["health_status"] = "unhealthy"

            return status

        except Exception as e:
            self.log_activity("Ошибка в методе", "error")
            return {
                "enabled": False,
                "initialized": False,
                "config": {},
                "services_count": 0,
                "health_status": "error",
                "error": str(e),
            }

    def _save_functions(self):
        """Сохранение функций и обработчиков в файл"""
        try:
            import json
            import os

            # Загружаем существующий реестр для обновления
            existing_functions = {}
            if os.path.exists(self.registry_file):
                try:
                    with open(self.registry_file, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                    existing_functions = existing_data.get("functions", {})
                    self.log_activity(f"Загружен существующий реестр с {len(existing_functions)} функциями")
                except Exception as e:
                    self.log_activity(f"Ошибка чтения существующего реестра: {e}")
                    existing_functions = {}

            # Объединяем существующие функции с новыми
            all_functions = existing_functions.copy()

            # Обновляем/добавляем функции из памяти SFM
            for func_id, func in self.functions.items():
                all_functions[func_id] = {
                    "function_id": func.function_id,
                    "name": func.name,
                    "description": func.description,
                    "function_type": func.function_type,
                    "security_level": func.security_level.value,
                    "status": func.status.value,
                    "is_critical": func.is_critical,
                    "execution_count": func.execution_count,
                    "success_count": func.success_count,
                    "error_count": func.error_count,
                    "created_at": datetime.now().isoformat(),
                    "auto_enable": False,
                    "wake_time": None,
                    "emergency_wake_up": False,
                    "features": [],
                    "dependencies": [],
                    "config": {},
                    "metrics": {},
                    "last_execution": None,
                    "last_status_check": None,
                    "version": "1.0.0",
                    "author": "AI Agent",
                    "license": "Proprietary",
                    "tags": [],
                    "sleep_state": {
                        "sleep_time": None,
                        "previous_status": func.status.value,
                        "minimal_system_sleep": False,
                    },
                }

            data = {"functions": all_functions, "handlers": {}, "last_updated": datetime.now().isoformat()}

            # Сохраняем обработчики
            for func_id, handler in self.function_handlers.items():
                data["handlers"][func_id] = {
                    "type": type(handler).__name__,
                    "function_name": handler.__name__ if hasattr(handler, "__name__") else "lambda",
                    "module": handler.__module__ if hasattr(handler, "__module__") else "unknown",
                }

            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.log_activity(
                f"Реестр обновлен: {len(all_functions)} функций "
                f"(добавлено/обновлено: {len(self.functions)}) и "
                f"{len(self.function_handlers)} обработчиков"
            )

        except Exception as e:
            self.log_activity(f"Ошибка сохранения функций: {e}", "error")

    def _setup_emergencymlanalyzer_handler(self):
        """Настройка обработчика для EmergencyMLAnalyzer"""
        try:

            def emergencymlanalyzer_handler(*args, **kwargs):
                """Обработчик для EmergencyMLAnalyzer"""
                try:
                    # Импортируем EmergencyMLAnalyzer
                    from security.ai_agents.emergency_ml_analyzer import (
                        EmergencyMLAnalyzer,
                    )

                    # Создаем экземпляр
                    analyzer = EmergencyMLAnalyzer()

                    # Возвращаем результат
                    return {
                        "status": "success",
                        "function_id": "emergencymlanalyzer",
                        "handler_name": "EmergencyMLAnalyzer",
                        "message": "EmergencyMLAnalyzer успешно инициализирован",
                        "analyzer": analyzer,
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "function_id": "emergencymlanalyzer",
                        "handler_name": "EmergencyMLAnalyzer",
                        "message": f"Ошибка инициализации EmergencyMLAnalyzer: {e}",
                    }

            # Регистрируем обработчик
            self.register_function_handler("emergencymlanalyzer", emergencymlanalyzer_handler)
            self.log_activity("Обработчик EmergencyMLAnalyzer настроен")

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def _initialize_auto_scaling_engine(self):
        """Инициализация AutoScalingEngine для автоматического масштабирования"""
        try:
            if not self.scaling_enabled:
                self.log_activity("Ошибка в методе", "error")
                return

            # Создаем экземпляр AutoScalingEngine
            self.auto_scaling_engine = AutoScalingEngine(name=f"{self.name}ScalingEngine")

            # Инициализируем движок
            if self.auto_scaling_engine.initialize():
                self.log_activity("Ошибка в методе", "error")

                # Добавляем правила масштабирования для SFM
                self._setup_scaling_rules()

            else:
                self.log_activity("Ошибка в методе", "error")
                self.auto_scaling_engine = None

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            self.auto_scaling_engine = None

    def _setup_scaling_rules(self):
        """Настройка правил масштабирования для SFM"""
        try:
            if not self.auto_scaling_engine:
                return

            # Правило для масштабирования на основе количества активных функций
            active_functions_rule = ScalingRule(
                rule_id="active_functions_scaling",
                name="Масштабирование по активным функциям",
                service_id="sfm_functions",
                metric_name="cpu_usage",
                trigger=ScalingTrigger.CPU_HIGH,
                threshold=0.7,  # 70% загрузки
                action=ScalingAction.SCALE_UP,
                min_replicas=1,
                max_replicas=10,
                cooldown_period=300,  # 5 минут
                enabled=True,
            )

            # Правило для масштабирования на основе ошибок
            error_rate_rule = ScalingRule(
                rule_id="error_rate_scaling",
                name="Масштабирование по ошибкам",
                service_id="sfm_functions",
                metric_name="error_rate",
                trigger=ScalingTrigger.CUSTOM,
                threshold=0.1,  # 10% ошибок
                action=ScalingAction.SCALE_UP,
                min_replicas=1,
                max_replicas=5,
                cooldown_period=600,  # 10 минут
                enabled=True,
            )

            # Добавляем правила
            self.auto_scaling_engine.add_scaling_rule(active_functions_rule)
            self.auto_scaling_engine.add_scaling_rule(error_rate_rule)

            self.log_activity("Ошибка в методе", "error")

        except Exception:
            self.log_activity("Ошибка в методе", "error")

    def get_scaling_status(self) -> Dict[str, Any]:
        """Получение статуса масштабирования"""
        try:
            if not self.auto_scaling_engine:
                return {
                    "enabled": False,
                    "status": "not_initialized",
                    "message": "AutoScalingEngine не инициализирован",
                }

            status = self.auto_scaling_engine.get_engine_status()
            rules = self.auto_scaling_engine.get_scaling_rules()
            metrics = self.auto_scaling_engine.get_scaling_metrics()

            return {
                "enabled": True,
                "status": status.get("status", "unknown"),
                "rules_count": len(rules),
                "metrics": metrics,
                "engine_status": status,
            }

        except Exception as e:
            return {"enabled": False, "status": "error", "message": f"Ошибка получения статуса масштабирования: {e}"}

    def collect_scaling_metrics(self) -> bool:
        """Сбор метрик для масштабирования"""
        try:
            if not self.auto_scaling_engine:
                return False

            # Собираем метрики SFM
            cpu_usage = self._calculate_cpu_usage()
            memory_usage = self._calculate_memory_usage()
            error_rate = self._calculate_error_rate()
            active_functions = len([f for f in self.functions.values() if f.get("status") == "active"])

            # Создаем метрику
            metric = MetricData(
                service_id="sfm_functions",
                metric_type="system_metrics",
                value=cpu_usage,
                timestamp=datetime.now(),
                metadata={
                    "memory_usage": memory_usage,
                    "error_rate": error_rate,
                    "active_functions": active_functions,
                    "total_functions": len(self.functions),
                },
            )

            # Отправляем метрику в движок масштабирования
            return self.auto_scaling_engine.collect_metric(metric)

        except Exception:
            self.log_activity("Ошибка в методе", "error")
            return False

    def _calculate_cpu_usage(self) -> float:
        """Расчет использования CPU"""
        try:
            # Простой расчет на основе активных функций
            active_functions = len([f for f in self.functions.values() if f.get("status") == "active"])
            total_functions = len(self.functions)

            if total_functions == 0:
                return 0.0

            # Базовое использование + нагрузка от активных функций
            base_usage = 0.1  # 10% базовая нагрузка
            function_load = (active_functions / total_functions) * 0.8  # до 80% от функций

            return min(base_usage + function_load, 1.0)

        except Exception:
            return 0.5  # 50% по умолчанию

    def _calculate_memory_usage(self) -> float:
        """Расчет использования памяти"""
        try:
            # Простой расчет на основе количества функций
            total_functions = len(self.functions)
            base_memory = 0.1  # 10% базовая память
            function_memory = (total_functions / 100) * 0.7  # 70% от количества функций

            return min(base_memory + function_memory, 1.0)

        except Exception:
            return 0.3  # 30% по умолчанию

    def health_check(self) -> bool:
        """
        health_check method for SFM.

        Returns:
            bool: Результат операции health_check
        """
        try:
            self.logger.info("health_check() called")
            # TODO: Implement health_check functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in health_check(): {e}")
            return False

    def status(self) -> bool:
        """
        status method for SFM.

        Returns:
            bool: Результат операции status
        """
        try:
            self.logger.info("status() called")
            # TODO: Implement status functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in status(): {e}")
            return False

    def is_active(self) -> bool:
        """
        is_active method for SFM.

        Returns:
            bool: Результат операции is_active
        """
        try:
            self.logger.info("is_active() called")
            # TODO: Implement is_active functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in is_active(): {e}")
            return False

    def check_health(self) -> bool:
        """
        check_health method for SFM.

        Returns:
            bool: Результат операции check_health
        """
        try:
            self.logger.info("check_health() called")
            # TODO: Implement check_health functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in check_health(): {e}")
            return False

    def restart(self) -> bool:
        """
        restart method for SFM.

        Returns:
            bool: Результат операции restart
        """
        try:
            self.logger.info("restart() called")
            # TODO: Implement restart functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in restart(): {e}")
            return False

    def configure(self) -> bool:
        """
        configure method for SFM.

        Returns:
            bool: Результат операции configure
        """
        try:
            self.logger.info("configure() called")
            # TODO: Implement configure functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in configure(): {e}")
            return False

    def validate(self) -> bool:
        """
        validate method for SFM.

        Returns:
            bool: Результат операции validate
        """
        try:
            self.logger.info("validate() called")
            # TODO: Implement validate functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in validate(): {e}")
            return False

    def update(self) -> bool:
        """
        update method for SFM.

        Returns:
            bool: Результат операции update
        """
        try:
            self.logger.info("update() called")
            # TODO: Implement update functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in update(): {e}")
            return False

    def refresh(self) -> bool:
        """
        refresh method for SFM.

        Returns:
            bool: Результат операции refresh
        """
        try:
            self.logger.info("refresh() called")
            # TODO: Implement refresh functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in refresh(): {e}")
            return False

    def sync(self) -> bool:
        """
        sync method for SFM.

        Returns:
            bool: Результат операции sync
        """
        try:
            self.logger.info("sync() called")
            # TODO: Implement sync functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in sync(): {e}")
            return False

    def backup(self) -> bool:
        """
        backup method for SFM.

        Returns:
            bool: Результат операции backup
        """
        try:
            self.logger.info("backup() called")
            # TODO: Implement backup functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in backup(): {e}")
            return False

    def restore(self) -> bool:
        """
        restore method for SFM.

        Returns:
            bool: Результат операции restore
        """
        try:
            self.logger.info("restore() called")
            # TODO: Implement restore functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in restore(): {e}")
            return False

    def export(self) -> bool:
        """
        export method for SFM.

        Returns:
            bool: Результат операции export
        """
        try:
            self.logger.info("export() called")
            # TODO: Implement export functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in export(): {e}")
            return False

    def import_data(self) -> bool:
        """
        import_data method for SFM.

        Returns:
            bool: Результат операции import_data
        """
        try:
            self.logger.info("import_data() called")
            # TODO: Implement import_data functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in import_data(): {e}")
            return False

    def scan(self) -> bool:
        """
        scan method for SFM.

        Returns:
            bool: Результат операции scan
        """
        try:
            self.logger.info("scan() called")
            # TODO: Implement scan functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in scan(): {e}")
            return False

    def analyze(self) -> bool:
        """
        analyze method for SFM.

        Returns:
            bool: Результат операции analyze
        """
        try:
            self.logger.info("analyze() called")
            # TODO: Implement analyze functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in analyze(): {e}")
            return False

    def monitor(self) -> bool:
        """
        monitor method for SFM.

        Returns:
            bool: Результат операции monitor
        """
        try:
            self.logger.info("monitor() called")
            # TODO: Implement monitor functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in monitor(): {e}")
            return False

    def alert(self) -> bool:
        """
        alert method for SFM.

        Returns:
            bool: Результат операции alert
        """
        try:
            self.logger.info("alert() called")
            # TODO: Implement alert functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in alert(): {e}")
            return False

    def notify(self) -> bool:
        """
        notify method for SFM.

        Returns:
            bool: Результат операции notify
        """
        try:
            self.logger.info("notify() called")
            # TODO: Implement notify functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in notify(): {e}")
            return False

    def report(self) -> bool:
        """
        report method for SFM.

        Returns:
            bool: Результат операции report
        """
        try:
            self.logger.info("report() called")
            # TODO: Implement report functionality
            return True
        except Exception as e:
            self.logger.error(f"Error in report(): {e}")
            return False

    def _calculate_error_rate(self) -> float:
        """Расчет коэффициента ошибок"""
        try:
            if self.total_executions == 0:
                return 0.0

            return self.failed_executions / self.total_executions

        except Exception:
            return 0.0

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Получение статистики оптимизации"""
        try:
            stats = {
                "memory_pool": {"size": 0, "max_size": 1000, "hits": 0, "misses": 0, "evictions": 0, "hit_rate": 0.0},
                "import_optimizer": {"cached_imports": 0, "cached": 0, "loaded": 0, "errors": 0},
                "performance_optimizer": None,
                "redis_cache": None,
                "async_io": None,
            }

            # Проверяем наличие компонентов оптимизации
            if hasattr(self, "performance_optimizer") and self.performance_optimizer:
                try:
                    stats["performance_optimizer"] = self.performance_optimizer.get_performance_report()
                except Exception:
                    stats["performance_optimizer"] = {"status": "unavailable"}

            if hasattr(self, "redis_cache_manager") and self.redis_cache_manager:
                try:
                    stats["redis_cache"] = self.redis_cache_manager.get_cache_info()
                except Exception:
                    stats["redis_cache"] = {"status": "unavailable"}

            if hasattr(self, "async_io_manager") and self.async_io_manager:
                try:
                    stats["async_io"] = self.async_io_manager.get_stats()
                except Exception:
                    stats["async_io"] = {"status": "unavailable"}

            return stats

        except Exception as e:
            self.log_activity(f"Ошибка получения статистики оптимизации: {e}", "error")
            return {
                "memory_pool": {"size": 0, "max_size": 1000, "hits": 0, "misses": 0, "evictions": 0, "hit_rate": 0.0},
                "import_optimizer": {"cached_imports": 0, "cached": 0, "loaded": 0, "errors": 0},
                "performance_optimizer": None,
                "redis_cache": None,
                "async_io": None,
            }

    # ============================================================================
    # МЕТОДЫ ПОИСКА ФУНКЦИЙ - КРИТИЧЕСКИ ВАЖНЫЕ ДЛЯ ПРОДАКШЕНА
    # ============================================================================

    def search_functions(
        self, query: str, category: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск функций по запросу с фильтрацией по категории и статусу

        Args:
            query: Поисковый запрос (поиск по имени, описанию, function_id)
            category: Фильтр по категории (FAMILY, SECURITY, AI_ML, etc.)
            status: Фильтр по статусу (enabled, disabled, active, etc.)

        Returns:
            List[Dict[str, Any]]: Список найденных функций
        """
        try:
            results = []
            query_lower = query.lower()

            for function_id, function in self.functions.items():
                # Проверка соответствия запросу
                matches_query = (
                    query_lower in function.name.lower()
                    or query_lower in function.description.lower()
                    or query_lower in function_id.lower()
                    or query_lower in function.function_type.lower()
                )

                # Проверка фильтра по категории
                matches_category = category is None or function.function_type.upper() == category.upper()

                # Проверка фильтра по статусу
                matches_status = status is None or function.status.value.lower() == status.lower()

                if matches_query and matches_category and matches_status:
                    results.append(function.to_dict())

            self.log_activity(f"Поиск функций: '{query}' найдено {len(results)} результатов", "info")
            return results

        except Exception as e:
            self.log_activity(f"Ошибка поиска функций: {e}", "error")
            return []

    def find_function(self, func_id: str) -> Optional[Dict[str, Any]]:
        """
        Поиск конкретной функции по ID

        Args:
            func_id: ID функции для поиска

        Returns:
            Optional[Dict[str, Any]]: Данные функции или None если не найдена
        """
        try:
            if func_id in self.functions:
                function = self.functions[func_id]
                self.log_activity(f"Функция найдена: {func_id}", "info")
                return function.to_dict()
            else:
                self.log_activity(f"Функция не найдена: {func_id}", "warning")
                return None

        except Exception as e:
            self.log_activity(f"Ошибка поиска функции {func_id}: {e}", "error")
            return None

    def get_functions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Получение всех функций определенной категории

        Args:
            category: Категория функций (FAMILY, SECURITY, AI_ML, etc.)

        Returns:
            List[Dict[str, Any]]: Список функций категории
        """
        try:
            results = []
            category_upper = category.upper()

            for function in self.functions.values():
                if function.function_type.upper() == category_upper:
                    results.append(function.to_dict())

            self.log_activity(f"Найдено {len(results)} функций категории {category}", "info")
            return results

        except Exception as e:
            self.log_activity(f"Ошибка получения функций категории {category}: {e}", "error")
            return []

    def get_functions_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Получение всех функций определенного статуса

        Args:
            status: Статус функций (enabled, disabled, active, sleeping, etc.)

        Returns:
            List[Dict[str, Any]]: Список функций статуса
        """
        try:
            results = []
            status_lower = status.lower()

            for function in self.functions.values():
                if function.status.value.lower() == status_lower:
                    results.append(function.to_dict())

            self.log_activity(f"Найдено {len(results)} функций со статусом {status}", "info")
            return results

        except Exception as e:
            self.log_activity(f"Ошибка получения функций статуса {status}: {e}", "error")
            return []

    def get_functions_by_type(self, function_type: str) -> List[Dict[str, Any]]:
        """
        Получение функций по типу (совместимость с существующим API)

        Args:
            function_type: Тип функций

        Returns:
            List[Dict[str, Any]]: Список функций типа
        """
        try:
            results = []

            for function in self.functions.values():
                if function.function_type == function_type:
                    results.append(function.to_dict())

            self.log_activity(f"Найдено {len(results)} функций типа {function_type}", "info")
            return results

        except Exception as e:
            self.log_activity(f"Ошибка получения функций типа {function_type}: {e}", "error")
            return []

    def search_functions_advanced(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        security_level: Optional[str] = None,
        is_critical: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Расширенный поиск функций с множественными фильтрами

        Args:
            query: Поисковый запрос
            category: Фильтр по категории
            status: Фильтр по статусу
            security_level: Фильтр по уровню безопасности
            is_critical: Фильтр по критичности
            limit: Ограничение количества результатов

        Returns:
            Dict[str, Any]: Результаты поиска с метаданными
        """
        try:
            results = []
            filters_applied = []

            for function_id, function in self.functions.items():
                # Применение всех фильтров
                matches = True

                # Фильтр по запросу
                if query:
                    query_lower = query.lower()
                    if not (
                        query_lower in function.name.lower()
                        or query_lower in function.description.lower()
                        or query_lower in function_id.lower()
                        or query_lower in function.function_type.lower()
                    ):
                        matches = False

                # Фильтр по категории
                if category and function.function_type.upper() != category.upper():
                    matches = False

                # Фильтр по статусу
                if status and function.status.value.lower() != status.lower():
                    matches = False

                # Фильтр по уровню безопасности
                if security_level and function.security_level.value.lower() != security_level.lower():
                    matches = False

                # Фильтр по критичности
                if is_critical is not None and function.is_critical != is_critical:
                    matches = False

                if matches:
                    results.append(function.to_dict())

            # Применение лимита
            if limit and len(results) > limit:
                results = results[:limit]
                filters_applied.append(f"limit={limit}")

            # Формирование ответа
            response = {
                "functions": results,
                "total_found": len(results),
                "filters_applied": filters_applied,
                "search_params": {
                    "query": query,
                    "category": category,
                    "status": status,
                    "security_level": security_level,
                    "is_critical": is_critical,
                    "limit": limit,
                },
            }

            self.log_activity(f"Расширенный поиск: найдено {len(results)} функций", "info")
            return response

        except Exception as e:
            self.log_activity(f"Ошибка расширенного поиска: {e}", "error")
            return {"functions": [], "total_found": 0, "filters_applied": [], "search_params": {}, "error": str(e)}

    def _initialize_security_analytics(self):
        """Инициализация системы аналитики безопасности"""
        try:
            if self.analytics_enabled:
                self.security_analytics = SecurityAnalyticsManager()
                # Инициализация будет выполнена асинхронно при первом использовании
                self.log_activity("Security Analytics Manager создан", "info")
            else:
                self.log_activity("Security Analytics отключен", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Security Analytics: {e}", "error")
            self.security_analytics = None

    def _initialize_incident_response(self):
        """Инициализация системы реагирования на инциденты"""
        try:
            if self.incident_response_enabled:
                self.incident_response = IncidentResponseManager()
                # Инициализация будет выполнена асинхронно при первом использовании
                self.log_activity("Incident Response Manager создан", "info")
            else:
                self.log_activity("Incident Response отключен", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Incident Response: {e}", "error")
            self.incident_response = None

    def _initialize_health_check_system(self):
        """Инициализация системы Health Check"""
        try:
            if self.health_check_enabled:
                self.health_check_system = HealthCheckManager()
                # Инициализация будет выполнена асинхронно при первом использовании
                self.log_activity("Health Check Manager создан", "info")
            else:
                self.log_activity("Health Check отключен", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Health Check: {e}", "error")
            self.health_check_system = None

    def _initialize_compliance_manager(self):
        """Инициализация системы управления соответствием"""
        try:
            if not hasattr(self, "compliance_manager"):
                self.compliance_manager = None
            if not hasattr(self, "compliance_enabled"):
                self.compliance_enabled = True
            if not hasattr(self, "compliance_config"):
                self.compliance_config = {}

            if self.compliance_enabled:
                self.compliance_manager = ComplianceManager(self.compliance_config)
                # Инициализация будет выполнена асинхронно при первом использовании
                self.log_activity("Compliance Manager создан", "info")
            else:
                self.log_activity("Compliance Manager отключен", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Compliance Manager: {e}", "error")
            self.compliance_manager = None

    def _initialize_compliance_auditor(self):
        """Инициализация системы аудита соответствия"""
        try:
            if not hasattr(self, "compliance_auditor"):
                self.compliance_auditor = None
            if not hasattr(self, "compliance_audit_enabled"):
                self.compliance_audit_enabled = True
            if not hasattr(self, "compliance_audit_config"):
                self.compliance_audit_config = {}

            if self.compliance_audit_enabled:
                self.compliance_auditor = ComplianceAuditor(self.compliance_audit_config)
                # Инициализация будет выполнена асинхронно при первом использовании
                self.log_activity("Compliance Auditor создан", "info")
            else:
                self.log_activity("Compliance Auditor отключен", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Compliance Auditor: {e}", "error")
            self.compliance_auditor = None

    def _initialize_compliance_reporter(self):
        """Инициализация системы отчетности по соответствию"""
        try:
            if not hasattr(self, "compliance_reporter"):
                self.compliance_reporter = None
            if not hasattr(self, "compliance_reporting_enabled"):
                self.compliance_reporting_enabled = True
            if not hasattr(self, "compliance_reporting_config"):
                self.compliance_reporting_config = {}

            if self.compliance_reporting_enabled:
                self.compliance_reporter = ComplianceReporter(self.compliance_reporting_config)
                # Инициализация будет выполнена асинхронно при первом использовании
                self.log_activity("Compliance Reporter создан", "info")
            else:
                self.log_activity("Compliance Reporter отключен", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Compliance Reporter: {e}", "error")
            self.compliance_reporter = None

    async def get_compliance_dashboard_data(self) -> Dict[str, Any]:
        """Получение данных для dashboard compliance"""
        try:
            dashboard_data = {
                "compliance_manager": await self._get_compliance_manager_data(),
                "compliance_auditor": await self._get_compliance_auditor_data(),
                "compliance_reporter": await self._get_compliance_reporter_data(),
                "timestamp": datetime.now().isoformat(),
            }
            return dashboard_data
        except Exception as e:
            self.log_activity(f"Ошибка получения данных compliance dashboard: {e}", "error")
            return {"error": str(e)}

    async def _get_compliance_manager_data(self) -> Dict[str, Any]:
        """Получение данных Compliance Manager"""
        try:
            if self.compliance_manager:
                await self.compliance_manager.initialize()
                return await self.compliance_manager.get_dashboard_data()
            return {"status": "not_available"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _get_compliance_auditor_data(self) -> Dict[str, Any]:
        """Получение данных Compliance Auditor"""
        try:
            if self.compliance_auditor:
                await self.compliance_auditor.initialize()
                return await self.compliance_auditor.get_dashboard_data()
            return {"status": "not_available"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _get_compliance_reporter_data(self) -> Dict[str, Any]:
        """Получение данных Compliance Reporter"""
        try:
            if self.compliance_reporter:
                await self.compliance_reporter.initialize()
                return await self.compliance_reporter.get_dashboard_data()
            return {"status": "not_available"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _initialize_lazy_system(self):
        """Инициализация системы lazy loading"""
        try:
            if self.lazy_enabled:
                self.lazy_manager = get_lazy_manager()
                success = True  # Lazy manager уже инициализирован
                if success:
                    self.log_activity("Lazy Loading система инициализирована", "info")
                else:
                    self.log_activity("Ошибка инициализации Lazy Loading системы", "error")
            else:
                self.log_activity("Lazy Loading система отключена", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Lazy Loading системы: {e}", "error")

    def _initialize_search_system(self):
        """Инициализация системы поиска"""
        try:
            if self.search_enabled:
                self.search_indexer = get_search_indexer()
                success = True  # Search indexer уже инициализирован
                if success:
                    self.log_activity("Search Indexer система инициализирована", "info")
                else:
                    self.log_activity("Ошибка инициализации Search Indexer системы", "error")
            else:
                self.log_activity("Search Indexer система отключена", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Search Indexer системы: {e}", "error")

    def _initialize_pagination_system(self):
        """Инициализация системы пагинации"""
        try:
            if self.pagination_enabled:
                self.pagination_system = UniversalPaginationSystem("SFM_Pagination")
                success = True  # Pagination system уже инициализирован
                if success:
                    self.log_activity("Pagination система инициализирована", "info")
                else:
                    self.log_activity("Ошибка инициализации Pagination системы", "error")
            else:
                self.log_activity("Pagination система отключена", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации Pagination системы: {e}", "error")

    # Методы для работы с новыми компонентами
    def get_lazy_system_stats(self) -> Dict[str, Any]:
        """Получение статистики lazy loading системы"""
        try:
            if self.lazy_manager:
                if hasattr(self.lazy_manager, 'get_stats'):
                    return get_lazy_system_stats()
                else:
                    return {"status": "lazy_system_initialized", "functions": 0}
            return {"error": "Lazy system not initialized"}
        except Exception as e:
            return {"error": str(e)}

    def get_search_system_stats(self) -> Dict[str, Any]:
        """Получение статистики поисковой системы"""
        try:
            if self.search_indexer:
                return get_search_stats()
            else:
                return {"status": "search_system_initialized", "indexed_functions": 0}
            return {"error": "Search system not initialized"}
        except Exception as e:
            return {"error": str(e)}

    def get_pagination_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы пагинации"""
        try:
            if self.pagination_system:
                return self.pagination_system.get_stats()
            return {"error": "Pagination system not initialized"}
        except Exception as e:
            return {"error": str(e)}

    def paginate_functions(
        self, page: int = 1, per_page: int = 10, category: str = None, status: str = None
    ) -> Dict[str, Any]:
        """Пагинация функций"""
        try:
            if self.pagination_system:
                # Получение всех функций
                all_functions = list(self.functions.values())

                # Фильтрация по категории
                if category:
                    all_functions = [f for f in all_functions if f.category == category]

                # Фильтрация по статусу
                if status:
                    all_functions = [f for f in all_functions if f.status.value == status]

                # Пагинация
                result = self.pagination_system.paginate(all_functions, page, per_page)
                return result
            return {"error": "Pagination system not initialized"}
        except Exception as e:
            return {"error": str(e)}
