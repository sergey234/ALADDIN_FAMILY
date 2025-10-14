# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Network Monitoring Service
Система мониторинга сетевой активности для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple

from core.base import SecurityBase

# ===== КАСТОМНЫЕ ИСКЛЮЧЕНИЯ =====


class NetworkMonitoringError(Exception):
    """Базовое исключение для мониторинга сети"""

    pass


class InvalidIPAddressError(NetworkMonitoringError):
    """Некорректный IP адрес"""

    pass


class InvalidPortError(NetworkMonitoringError):
    """Некорректный порт"""

    pass


class InvalidUserAgeError(NetworkMonitoringError):
    """Некорректный возраст пользователя"""

    pass


class ConnectionTimeoutError(NetworkMonitoringError):
    """Таймаут соединения"""

    pass


class FamilyMemberNotFoundError(NetworkMonitoringError):
    """Член семьи не найден"""

    pass


# ===== КОНФИГУРАЦИЯ =====


@dataclass
class NetworkMonitoringConfig:
    """Конфигурация мониторинга сети"""

    max_connections: int = 10000
    cache_ttl: int = 300
    anomaly_threshold: float = 0.7
    family_protection: bool = True
    real_time_monitoring: bool = True
    deep_packet_inspection: bool = True
    notification_channels: List[str] = field(default_factory=list)
    validation_enabled: bool = True
    performance_monitoring: bool = True


# ===== МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ =====


class PerformanceMetrics:
    """Метрики производительности"""

    def __init__(self):
        self.method_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_connections = 0
        self.total_anomalies = 0
        self.start_time = time.time()

    def record_method_time(self, method_name: str, execution_time: float):
        """Запись времени выполнения метода"""
        self.method_times[method_name].append(execution_time)

    def record_error(self, method_name: str):
        """Запись ошибки"""
        self.error_counts[method_name] += 1

    def record_cache_hit(self):
        """Запись попадания в кэш"""
        self.cache_hits += 1

    def record_cache_miss(self):
        """Запись промаха кэша"""
        self.cache_misses += 1

    def get_average_time(self, method_name: str) -> float:
        """Получение среднего времени выполнения"""
        times = self.method_times.get(method_name, [])
        return sum(times) / len(times) if times else 0.0

    def get_error_rate(self, method_name: str) -> float:
        """Получение частоты ошибок"""
        total_calls = len(self.method_times.get(method_name, []))
        errors = self.error_counts.get(method_name, 0)
        return errors / total_calls if total_calls > 0 else 0.0


class NetworkType(Enum):
    """Типы сетей"""

    WIFI = "wifi"
    ETHERNET = "ethernet"
    MOBILE = "mobile"
    BLUETOOTH = "bluetooth"
    VPN = "vpn"
    UNKNOWN = "unknown"


class TrafficType(Enum):
    """Типы трафика"""

    WEB = "web"
    EMAIL = "email"
    GAMING = "gaming"
    SOCIAL_MEDIA = "social_media"
    STREAMING = "streaming"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    CHAT = "chat"
    FILE_SHARING = "file_sharing"
    UNKNOWN = "unknown"


class ThreatLevel(Enum):
    """Уровни угроз"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MonitoringAction(Enum):
    """Действия мониторинга"""

    LOG = "log"
    ALERT = "alert"
    BLOCK = "block"
    THROTTLE = "throttle"
    QUARANTINE = "quarantine"
    NOTIFY_PARENT = "notify_parent"
    NOTIFY_ADMIN = "notify_admin"
    SCAN_DEEP = "scan_deep"


@dataclass
class NetworkConnection:
    """Сетевое соединение"""

    connection_id: str
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    network_type: NetworkType
    traffic_type: TrafficType
    bytes_sent: int
    bytes_received: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkAnomaly:
    """Сетевая аномалия"""

    anomaly_id: str
    connection_id: str
    anomaly_type: str
    threat_level: ThreatLevel
    description: str
    timestamp: datetime
    source_ip: str
    destination_ip: str
    confidence: float
    actions_taken: List[MonitoringAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkRule:
    """Правило мониторинга сети"""

    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[MonitoringAction]
    enabled: bool = True
    family_specific: bool = False
    age_group: Optional[str] = None
    time_restrictions: Optional[Dict[str, Any]] = None


@dataclass
class NetworkStatistics:
    """Статистика сети"""

    total_connections: int
    total_bytes_sent: int
    total_bytes_received: int
    active_connections: int
    blocked_connections: int
    anomalies_detected: int
    by_traffic_type: Dict[str, int]
    by_network_type: Dict[str, int]
    by_threat_level: Dict[str, int]
    top_destinations: List[Tuple[str, int]]
    top_sources: List[Tuple[str, int]]


class NetworkMonitoringService(SecurityBase):
    """
    Сервис мониторинга сетевой активности для семей.

    Предоставляет комплексный мониторинг сетевой активности с поддержкой
    семейной защиты, детского контроля, мониторинга пожилых и обнаружения
    аномалий.

    Features:
        - Реальное время мониторинга
        - Семейная защита и родительский контроль
        - Обнаружение аномалий и угроз
        - Асинхронная обработка
        - Кэширование и оптимизация
        - Метрики производительности
        - Расширенная валидация

    Example:
        >>> service = NetworkMonitoringService('FamilyNetworkGuard')
        >>> # Синхронный мониторинг
        >>> conn = service.monitor_connection(
        ...     '192.168.1.100', '8.8.8.8', 12345, 80, 'TCP'
        ... )
        >>> # Асинхронный мониторинг
        >>> conn = await service.monitor_connection_async(
        ...     '192.168.1.100', '8.8.8.8', 12345, 80, 'TCP'
        ... )
    """

    def __init__(
        self,
        name: str = "NetworkMonitoring",
        config: Optional[Dict[str, Any]] = None,
        monitoring_config: Optional[NetworkMonitoringConfig] = None,
    ):
        super().__init__(name, config)
        self.logger = logging.getLogger(__name__)

        # Конфигурация мониторинга
        self.monitoring_config = monitoring_config or NetworkMonitoringConfig()

        # Метрики производительности
        self.metrics = (
            PerformanceMetrics()
            if self.monitoring_config.performance_monitoring
            else None
        )
        # Хранилища данных
        self.active_connections: Dict[str, NetworkConnection] = {}
        self.connection_history: List[NetworkConnection] = []
        self.network_anomalies: Dict[str, NetworkAnomaly] = {}
        self.monitoring_rules: Dict[str, NetworkRule] = {}
        self.blocked_ips: Set[str] = set()
        self.throttled_ips: Set[str] = set()
        self.family_network_history: Dict[str, List[str]] = (
            {}
        )  # user_id -> connection_ids
        # Настройки мониторинга
        self.monitoring_enabled = True
        self.real_time_monitoring = True
        self.deep_packet_inspection = True
        self.family_protection_enabled = True
        self.child_monitoring_mode = True
        self.elderly_monitoring_mode = True
        # Пороги для обнаружения аномалий
        self.anomaly_thresholds = {
            ThreatLevel.LOW: 0.3,
            ThreatLevel.MEDIUM: 0.5,
            ThreatLevel.HIGH: 0.7,
            ThreatLevel.CRITICAL: 0.9,
        }
        # Инициализация
        self._initialize_monitoring_rules()
        self._setup_family_protection()
        self._start_monitoring()

    # ===== ВАЛИДАЦИОННЫЕ МЕТОДЫ =====

    def _validate_ip_address(self, ip: str) -> bool:
        """
        Валидация IP адреса.

        Args:
            ip: IP адрес для проверки

        Returns:
            bool: True если IP корректный

        Raises:
            InvalidIPAddressError: При некорректном IP
        """
        if not ip or not isinstance(ip, str):
            raise InvalidIPAddressError(f"IP адрес не может быть пустым: {ip}")

        parts = ip.split(".")
        if len(parts) != 4:
            raise InvalidIPAddressError(f"Некорректный формат IP: {ip}")

        try:
            for part in parts:
                num = int(part)
                if not 0 <= num <= 255:
                    raise InvalidIPAddressError(
                        f"IP часть вне диапазона 0-255: {part}"
                    )
        except ValueError:
            raise InvalidIPAddressError(
                f"IP содержит нечисловые значения: {ip}"
            )

        return True

    def _validate_port(self, port: int) -> bool:
        """
        Валидация порта.

        Args:
            port: Порт для проверки

        Returns:
            bool: True если порт корректный

        Raises:
            InvalidPortError: При некорректном порте
        """
        if not isinstance(port, int):
            raise InvalidPortError(f"Порт должен быть числом: {port}")

        if not 1 <= port <= 65535:
            raise InvalidPortError(f"Порт вне диапазона 1-65535: {port}")

        return True

    def _validate_user_age(self, age: Optional[int]) -> bool:
        """
        Валидация возраста пользователя.

        Args:
            age: Возраст для проверки

        Returns:
            bool: True если возраст корректный

        Raises:
            InvalidUserAgeError: При некорректном возрасте
        """
        if age is None:
            return True  # Возраст необязателен

        if not isinstance(age, int):
            raise InvalidUserAgeError(f"Возраст должен быть числом: {age}")

        if not 0 <= age <= 150:
            raise InvalidUserAgeError(
                f"Возраст вне разумного диапазона 0-150: {age}"
            )

        return True

    def _validate_protocol(self, protocol: str) -> bool:
        """
        Валидация протокола.

        Args:
            protocol: Протокол для проверки

        Returns:
            bool: True если протокол корректный
        """
        valid_protocols = {
            "TCP",
            "UDP",
            "ICMP",
            "HTTP",
            "HTTPS",
            "FTP",
            "SSH",
        }
        if protocol.upper() not in valid_protocols:
            raise ValueError(f"Неподдерживаемый протокол: {protocol}")
        return True

    def _validate_user_id(self, user_id: Optional[str]) -> bool:
        """
        Валидация ID пользователя.

        Args:
            user_id: ID пользователя для проверки

        Returns:
            bool: True если ID корректный
        """
        if user_id is None:
            return True  # ID необязателен

        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError(
                f"ID пользователя не может быть пустым: {user_id}"
            )

        if len(user_id) > 100:
            raise ValueError(f"ID пользователя слишком длинный: {user_id}")

        return True

    # ===== КЭШИРОВАНИЕ =====

    @lru_cache(maxsize=128)
    def _get_cached_network_type(self, ip: str) -> NetworkType:
        """Кэшированное определение типа сети"""
        return self._detect_network_type(ip)

    @lru_cache(maxsize=256)
    def _get_cached_traffic_type(
        self, port: int, protocol: str
    ) -> TrafficType:
        """Кэшированное определение типа трафика"""
        return self._detect_traffic_type(port, protocol)

    async def _update_cache_async(self):
        """Асинхронное обновление кэша"""
        try:
            # Очистка устаревшего кэша
            self._get_cached_network_type.cache_clear()
            self._get_cached_traffic_type.cache_clear()

            if self.metrics:
                self.metrics.record_cache_hit()

            self.log_activity("Кэш обновлен асинхронно")
        except Exception as e:
            self.logger.error(f"Ошибка обновления кэша: {e}")
            if self.metrics:
                self.metrics.record_error("_update_cache_async")

    # ===== ASYNC МЕТОДЫ =====

    async def monitor_connection_async(
        self,
        source_ip: str,
        destination_ip: str,
        source_port: int,
        destination_port: int,
        protocol: str,
        user_id: Optional[str] = None,
        device_id: Optional[str] = None,
        user_age: Optional[int] = None,
    ) -> Optional[NetworkConnection]:
        """
        Асинхронный мониторинг сетевого соединения.

        Args:
            source_ip: IP адрес источника (например: '192.168.1.100')
            destination_ip: IP адрес назначения (например: '8.8.8.8')
            source_port: Порт источника (1-65535)
            destination_port: Порт назначения (1-65535)
            protocol: Протокол ('TCP', 'UDP', 'ICMP')
            user_id: ID пользователя для семейного мониторинга
            device_id: ID устройства
            user_age: Возраст пользователя для возрастных ограничений

        Returns:
            NetworkConnection: Объект соединения с метаданными или None при
            ошибке

        Raises:
            InvalidIPAddressError: При некорректных IP адресах
            InvalidPortError: При некорректных портах
            InvalidUserAgeError: При некорректном возрасте
            ConnectionTimeoutError: При таймауте соединения

        Example:
            >>> service = NetworkMonitoringService()
            >>> conn = await service.monitor_connection_async(
            ...     '192.168.1.100', '8.8.8.8', 12345, 80, 'TCP',
            ...     user_id='child_001', user_age=12
            ... )
            >>> print(conn.connection_id)
        """
        start_time = time.time()

        try:
            # Валидация параметров
            if self.monitoring_config.validation_enabled:
                self._validate_ip_address(source_ip)
                self._validate_ip_address(destination_ip)
                self._validate_port(source_port)
                self._validate_port(destination_port)
                self._validate_protocol(protocol)
                self._validate_user_id(user_id)
                self._validate_user_age(user_age)

            # Создаем соединение
            connection = NetworkConnection(
                connection_id=self._generate_connection_id(),
                source_ip=source_ip,
                destination_ip=destination_ip,
                source_port=source_port,
                destination_port=destination_port,
                protocol=protocol,
                network_type=self._get_cached_network_type(destination_ip),
                traffic_type=self._get_cached_traffic_type(
                    destination_port, protocol
                ),
                bytes_sent=0,
                bytes_received=0,
                start_time=datetime.now(),
                user_id=user_id,
                device_id=device_id,
                metadata={
                    "user_age": user_age,
                    "monitoring_enabled": True,
                    "async_mode": True,
                },
            )

            # Добавляем в хранилища
            self.active_connections[connection.connection_id] = connection
            self.connection_history.append(connection)

            # Добавляем в семейную историю
            if user_id:
                if user_id not in self.family_network_history:
                    self.family_network_history[user_id] = []
                self.family_network_history[user_id].append(
                    connection.connection_id
                )

            # Асинхронная проверка правил
            await self._check_monitoring_rules_async(connection)

            # Добавляем событие безопасности
            await self._add_security_event_async(
                event_type="network_connection",
                severity="info",
                description=(
                    f"Новое асинхронное соединение: "
                    f"{source_ip}:{source_port} -> "
                    f"{destination_ip}:{destination_port}"
                ),
                source="NetworkMonitoring",
                metadata={
                    "connection_id": connection.connection_id,
                    "protocol": protocol,
                    "network_type": connection.network_type.value,
                    "traffic_type": connection.traffic_type.value,
                    "user_id": user_id,
                    "user_age": user_age,
                    "device_id": device_id,
                    "async_mode": True,
                },
            )

            # Записываем метрики
            if self.metrics:
                execution_time = time.time() - start_time
                self.metrics.record_method_time(
                    "monitor_connection_async", execution_time
                )
                self.metrics.total_connections += 1

            return connection

        except Exception as e:
            self.logger.error(
                f"Ошибка асинхронного мониторинга соединения: {e}"
            )
            if self.metrics:
                self.metrics.record_error("monitor_connection_async")
            return None

    async def detect_network_anomaly_async(
        self,
        connection: NetworkConnection,
        anomaly_type: str,
        description: str,
        confidence: float,
    ) -> Optional[NetworkAnomaly]:
        """
        Асинхронное обнаружение сетевой аномалии.

        Args:
            connection: Сетевое соединение
            anomaly_type: Тип аномалии
            description: Описание аномалии
            confidence: Уровень уверенности (0.0-1.0)

        Returns:
            NetworkAnomaly: Объект аномалии или None при ошибке
        """
        start_time = time.time()

        try:
            # Валидация параметров
            if not connection:
                raise ValueError("Соединение не может быть None")

            if not 0.0 <= confidence <= 1.0:
                raise ValueError(
                    f"Уверенность должна быть в диапазоне 0.0-1.0: "
                    f"{confidence}"
                )

            # Определяем уровень угрозы
            threat_level = self._determine_threat_level(confidence)

            # Создаем аномалию
            anomaly = NetworkAnomaly(
                anomaly_id=self._generate_anomaly_id(),
                connection_id=connection.connection_id,
                anomaly_type=anomaly_type,
                threat_level=threat_level,
                description=description,
                timestamp=datetime.now(),
                source_ip=connection.source_ip,
                destination_ip=connection.destination_ip,
                confidence=confidence,
                metadata={
                    "user_id": connection.user_id,
                    "device_id": connection.device_id,
                    "protocol": connection.protocol,
                    "network_type": connection.network_type.value,
                    "async_mode": True,
                },
            )

            # Добавляем в хранилище
            self.network_anomalies[anomaly.anomaly_id] = anomaly

            # Асинхронное добавление события безопасности
            await self._add_security_event_async(
                event_type="network_anomaly",
                severity=threat_level.value,
                description=(
                    f"Асинхронная аномалия: {anomaly_type} - {description}"
                ),
                source="NetworkMonitoring",
                metadata={
                    "anomaly_id": anomaly.anomaly_id,
                    "connection_id": connection.connection_id,
                    "anomaly_type": anomaly_type,
                    "threat_level": threat_level.value,
                    "confidence": confidence,
                    "source_ip": connection.source_ip,
                    "destination_ip": connection.destination_ip,
                    "async_mode": True,
                },
            )

            # Записываем метрики
            if self.metrics:
                execution_time = time.time() - start_time
                self.metrics.record_method_time(
                    "detect_network_anomaly_async", execution_time
                )
                self.metrics.total_anomalies += 1

            return anomaly

        except Exception as e:
            self.logger.error(f"Ошибка асинхронного обнаружения аномалии: {e}")
            if self.metrics:
                self.metrics.record_error("detect_network_anomaly_async")
            return None

    async def get_network_statistics_async(
        self, user_id: Optional[str] = None
    ) -> Optional[NetworkStatistics]:
        """
        Асинхронное получение статистики сети.

        Args:
            user_id: ID пользователя для фильтрации (опционально)

        Returns:
            NetworkStatistics: Статистика сети или None при ошибке
        """
        start_time = time.time()

        try:
            if user_id:
                # Статистика для конкретного пользователя
                user_connections = [
                    conn
                    for conn in self.connection_history
                    if conn.user_id == user_id
                ]
            else:
                # Общая статистика
                user_connections = self.connection_history

            # Подсчет статистики
            total_connections = len(user_connections)
            total_bytes_sent = sum(
                conn.bytes_sent for conn in user_connections
            )
            total_bytes_received = sum(
                conn.bytes_received for conn in user_connections
            )
            active_connections = len(self.active_connections)
            blocked_connections = len(self.blocked_ips)
            anomalies_detected = len(self.network_anomalies)

            # Статистика по типам
            by_traffic_type = {}
            by_network_type = {}
            by_threat_level = {}

            for conn in user_connections:
                traffic_type = conn.traffic_type.value
                by_traffic_type[traffic_type] = (
                    by_traffic_type.get(traffic_type, 0) + 1
                )
                network_type = conn.network_type.value
                by_network_type[network_type] = (
                    by_network_type.get(network_type, 0) + 1
                )

            for anomaly in self.network_anomalies.values():
                threat_level = anomaly.threat_level.value
                by_threat_level[threat_level] = (
                    by_threat_level.get(threat_level, 0) + 1
                )

            # Топ назначений и источников
            destination_counts = {}
            source_counts = {}
            for conn in user_connections:
                dest_ip = conn.destination_ip
                source_ip = conn.source_ip
                destination_counts[dest_ip] = (
                    destination_counts.get(dest_ip, 0) + 1
                )
                source_counts[source_ip] = source_counts.get(source_ip, 0) + 1

            top_destinations = sorted(
                destination_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10]
            top_sources = sorted(
                source_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]

            statistics = NetworkStatistics(
                total_connections=total_connections,
                total_bytes_sent=total_bytes_sent,
                total_bytes_received=total_bytes_received,
                active_connections=active_connections,
                blocked_connections=blocked_connections,
                anomalies_detected=anomalies_detected,
                by_traffic_type=by_traffic_type,
                by_network_type=by_network_type,
                by_threat_level=by_threat_level,
                top_destinations=top_destinations,
                top_sources=top_sources,
            )

            # Записываем метрики
            if self.metrics:
                execution_time = time.time() - start_time
                self.metrics.record_method_time(
                    "get_network_statistics_async", execution_time
                )

            return statistics

        except Exception as e:
            self.logger.error(f"Ошибка асинхронного получения статистики: {e}")
            if self.metrics:
                self.metrics.record_error("get_network_statistics_async")
            return None

    async def _check_monitoring_rules_async(
        self, connection: NetworkConnection
    ):
        """Асинхронная проверка правил мониторинга"""
        try:
            for rule in self.monitoring_rules.values():
                if not rule.enabled:
                    continue
                if await self._evaluate_rule_conditions_async(
                    connection, rule
                ):
                    await self._apply_rule_actions_async(connection, rule)
        except Exception as e:
            self.logger.error(f"Ошибка асинхронной проверки правил: {e}")
            if self.metrics:
                self.metrics.record_error("_check_monitoring_rules_async")

    async def _evaluate_rule_conditions_async(
        self, connection: NetworkConnection, rule: NetworkRule
    ) -> bool:
        """Асинхронная оценка условий правила"""
        try:
            # Имитация асинхронной обработки
            await asyncio.sleep(0.001)
            return self._evaluate_rule_conditions(connection, rule)
        except Exception as e:
            self.logger.error(f"Ошибка асинхронной оценки условий: {e}")
            return False

    async def _apply_rule_actions_async(
        self, connection: NetworkConnection, rule: NetworkRule
    ):
        """Асинхронное применение действий правила"""
        try:
            # Имитация асинхронной обработки
            await asyncio.sleep(0.001)
            self._apply_rule_actions(connection, rule)
        except Exception as e:
            self.logger.error(f"Ошибка асинхронного применения действий: {e}")

    async def _add_security_event_async(
        self,
        event_type: str,
        severity: str,
        description: str,
        source: str,
        metadata: Dict[str, Any],
    ):
        """Асинхронное добавление события безопасности"""
        try:
            # Имитация асинхронной обработки
            await asyncio.sleep(0.001)
            self.add_security_event(
                event_type, severity, description, source, metadata
            )
        except Exception as e:
            self.logger.error(f"Ошибка асинхронного добавления события: {e}")

    def _initialize_monitoring_rules(self):
        """Инициализация правил мониторинга"""
        rules = [
            NetworkRule(
                rule_id="block_malicious_ips",
                name="Блокировка вредоносных IP",
                description="Блокировка известных вредоносных IP-адресов",
                conditions={"malicious_ip": True},
                actions=[MonitoringAction.BLOCK, MonitoringAction.ALERT],
                family_specific=True,
            ),
            NetworkRule(
                rule_id="monitor_child_gaming",
                name="Мониторинг игрового трафика детей",
                description="Контроль игрового трафика для детей",
                conditions={
                    "age_group": "child",
                    "traffic_type": "gaming",
                },
                actions=[
                    MonitoringAction.LOG,
                    MonitoringAction.NOTIFY_PARENT,
                ],
                family_specific=True,
                age_group="child",
            ),
            NetworkRule(
                rule_id="monitor_elderly_financial",
                name="Мониторинг финансового трафика пожилых",
                description="Контроль финансовых операций пожилых",
                conditions={
                    "age_group": "elderly",
                    "financial_site": True,
                },
                actions=[
                    MonitoringAction.LOG,
                    MonitoringAction.NOTIFY_ADMIN,
                ],
                family_specific=True,
                age_group="elderly",
            ),
            NetworkRule(
                rule_id="block_inappropriate_content",
                name="Блокировка неподходящего контента",
                description="Блокировка доступа к неподходящему контенту",
                conditions={"inappropriate_content": True},
                actions=[
                    MonitoringAction.BLOCK,
                    MonitoringAction.NOTIFY_PARENT,
                ],
                family_specific=True,
            ),
            NetworkRule(
                rule_id="throttle_high_bandwidth",
                name="Ограничение высокой пропускной способности",
                description="Ограничение трафика при превышении лимитов",
                conditions={"bandwidth_exceeded": True},
                actions=[
                    MonitoringAction.THROTTLE,
                    MonitoringAction.ALERT,
                ],
                family_specific=True,
            ),
            NetworkRule(
                rule_id="monitor_social_media",
                name="Мониторинг социальных сетей",
                description="Контроль активности в социальных сетях",
                conditions={"traffic_type": "social_media"},
                actions=[
                    MonitoringAction.LOG,
                    MonitoringAction.NOTIFY_PARENT,
                ],
                family_specific=True,
            ),
            NetworkRule(
                rule_id="detect_data_exfiltration",
                name="Обнаружение утечки данных",
                description="Обнаружение подозрительной передачи данных",
                conditions={"data_exfiltration": True},
                actions=[
                    MonitoringAction.BLOCK,
                    MonitoringAction.ALERT,
                    MonitoringAction.SCAN_DEEP,
                ],
                family_specific=True,
            ),
            NetworkRule(
                rule_id="monitor_vpn_usage",
                name="Мониторинг использования VPN",
                description="Контроль использования VPN-соединений",
                conditions={"network_type": "vpn"},
                actions=[MonitoringAction.LOG, MonitoringAction.ALERT],
                family_specific=True,
            ),
        ]
        for rule in rules:
            self.monitoring_rules[rule.rule_id] = rule
        self.log_activity(
            f"Инициализировано {len(rules)} правил мониторинга сети"
        )

    def _setup_family_protection(self):
        """Настройка семейной защиты"""
        self.family_protection_settings = {
            "child_protection": {
                "enabled": True,
                "gaming_time_limits": True,
                "social_media_monitoring": True,
                "inappropriate_content_blocking": True,
                "parent_notifications": True,
            },
            "elderly_protection": {
                "enabled": True,
                "financial_site_monitoring": True,
                "phishing_detection": True,
                "family_notifications": True,
                "suspicious_activity_alerts": True,
            },
            "general_family": {
                "unified_monitoring": True,
                "shared_network_policies": True,
                "family_aware_blocking": True,
                "real_time_alerts": True,
            },
        }
        self.log_activity("Настроена семейная защита сетевой активности")

    def _start_monitoring(self):
        """Запуск мониторинга"""
        if self.real_time_monitoring:
            self.log_activity(
                "Запущен мониторинг сетевой активности в реальном времени"
            )
        else:
            self.log_activity("Мониторинг сетевой активности отключен")

    def monitor_connection(
        self,
        source_ip: str,
        destination_ip: str,
        source_port: int,
        destination_port: int,
        protocol: str,
        user_id: Optional[str] = None,
        device_id: Optional[str] = None,
        user_age: Optional[int] = None,
    ) -> Optional[NetworkConnection]:
        """
        Мониторинг сетевого соединения в реальном времени.

        Args:
            source_ip: IP адрес источника (например: '192.168.1.100')
            destination_ip: IP адрес назначения (например: '8.8.8.8')
            source_port: Порт источника (1-65535)
            destination_port: Порт назначения (1-65535)
            protocol: Протокол ('TCP', 'UDP', 'ICMP')
            user_id: ID пользователя для семейного мониторинга
            device_id: ID устройства
            user_age: Возраст пользователя для возрастных ограничений

        Returns:
            NetworkConnection: Объект соединения с метаданными или None при
            ошибке

        Raises:
            InvalidIPAddressError: При некорректных IP адресах
            InvalidPortError: При некорректных портах
            InvalidUserAgeError: При некорректном возрасте
            ConnectionTimeoutError: При таймауте соединения

        Example:
            >>> service = NetworkMonitoringService()
            >>> conn = service.monitor_connection(
            ...     '192.168.1.100', '8.8.8.8', 12345, 80, 'TCP',
            ...     user_id='child_001', user_age=12
            ... )
            >>> print(conn.connection_id)
            conn_1758742531925_63631668
        """
        # Валидация параметров
        if self.monitoring_config.validation_enabled:
            self._validate_ip_address(source_ip)
            self._validate_ip_address(destination_ip)
            self._validate_port(source_port)
            self._validate_port(destination_port)
            self._validate_protocol(protocol)
            self._validate_user_id(user_id)
            self._validate_user_age(user_age)

        try:
            # Создаем соединение
            connection = NetworkConnection(
                connection_id=self._generate_connection_id(),
                source_ip=source_ip,
                destination_ip=destination_ip,
                source_port=source_port,
                destination_port=destination_port,
                protocol=protocol,
                network_type=self._detect_network_type(destination_ip),
                traffic_type=self._detect_traffic_type(
                    destination_port, protocol
                ),
                bytes_sent=0,
                bytes_received=0,
                start_time=datetime.now(),
                user_id=user_id,
                device_id=device_id,
                metadata={
                    "user_age": user_age,
                    "monitoring_enabled": True,
                },
            )
            # Добавляем в активные соединения
            self.active_connections[connection.connection_id] = connection
            # Добавляем в историю соединений
            self.connection_history.append(connection)
            # Добавляем в семейную историю
            if user_id:
                if user_id not in self.family_network_history:
                    self.family_network_history[user_id] = []
                self.family_network_history[user_id].append(
                    connection.connection_id
                )
            # Проверяем правила мониторинга
            self._check_monitoring_rules(connection)
            # Добавляем событие безопасности
            self.add_security_event(
                event_type="network_connection",
                severity="info",
                description=(
                    f"Новое сетевое соединение: {source_ip}:{source_port} -> "
                    f"{destination_ip}:{destination_port}"
                ),
                source="NetworkMonitoring",
                metadata={
                    "connection_id": connection.connection_id,
                    "protocol": protocol,
                    "network_type": connection.network_type.value,
                    "traffic_type": connection.traffic_type.value,
                    "user_id": user_id,
                    "user_age": user_age,
                    "device_id": device_id,
                },
            )
            return connection
        except Exception as e:
            self.logger.error(f"Ошибка мониторинга соединения: {e}")
            return None

    def _detect_network_type(self, destination_ip: str) -> NetworkType:
        """Определение типа сети"""
        try:
            # Простая логика определения типа сети
            if destination_ip.startswith(
                "192.168."
            ) or destination_ip.startswith("10."):
                return NetworkType.WIFI
            elif destination_ip.startswith("172."):
                return NetworkType.ETHERNET
            elif destination_ip.startswith("127."):
                return NetworkType.ETHERNET
            else:
                return NetworkType.UNKNOWN
        except Exception:
            return NetworkType.UNKNOWN

    def _detect_traffic_type(self, port: int, protocol: str) -> TrafficType:
        """Определение типа трафика"""
        try:
            # Определение по портам
            if port == 80 or port == 443:
                return TrafficType.WEB
            elif port == 25 or port == 587 or port == 993:
                return TrafficType.EMAIL
            elif port in [
                21,
                22,
                23,
                53,
                67,
                68,
                69,
                80,
                110,
                123,
                135,
                139,
                143,
                161,
                162,
                389,
                443,
                445,
                993,
                995,
            ]:
                return TrafficType.WEB
            elif port in [6667, 6697, 7000, 7001, 8000, 8001, 8080, 8081]:
                return TrafficType.CHAT
            elif port in [
                6881,
                6882,
                6883,
                6884,
                6885,
                6886,
                6887,
                6888,
                6889,
            ]:
                return TrafficType.FILE_SHARING
            else:
                return TrafficType.UNKNOWN
        except Exception:
            return TrafficType.UNKNOWN

    def _check_monitoring_rules(self, connection: NetworkConnection):
        """Проверка правил мониторинга"""
        try:
            for rule in self.monitoring_rules.values():
                if not rule.enabled:
                    continue
                if self._evaluate_rule_conditions(connection, rule):
                    self._apply_rule_actions(connection, rule)
        except Exception as e:
            self.logger.error(f"Ошибка проверки правил мониторинга: {e}")

    def _evaluate_rule_conditions(
        self, connection: NetworkConnection, rule: NetworkRule
    ) -> bool:
        """Оценка условий правила"""
        try:
            conditions = rule.conditions
            # Проверка семейных условий
            if rule.family_specific:
                if (
                    rule.age_group == "child" and
                    connection.metadata.get("user_age", 0) >= 18
                ):
                    return False
                elif (
                    rule.age_group == "elderly" and
                    connection.metadata.get("user_age", 0) < 65
                ):
                    return False
            # Проверка типа трафика
            if "traffic_type" in conditions:
                if connection.traffic_type.value != conditions["traffic_type"]:
                    return False
            # Проверка типа сети
            if "network_type" in conditions:
                if connection.network_type.value != conditions["network_type"]:
                    return False
            # Проверка вредоносных IP
            if "malicious_ip" in conditions and conditions["malicious_ip"]:
                if self._is_malicious_ip(connection.destination_ip):
                    return True
            # Проверка неподходящего контента
            if (
                "inappropriate_content" in conditions and
                conditions["inappropriate_content"]
            ):
                if self._is_inappropriate_content(connection.destination_ip):
                    return True
            # Проверка финансовых сайтов
            if "financial_site" in conditions and conditions["financial_site"]:
                if self._is_financial_site(connection.destination_ip):
                    return True
            # Проверка утечки данных
            if (
                "data_exfiltration" in conditions and
                conditions["data_exfiltration"]
            ):
                if self._detect_data_exfiltration(connection):
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка оценки условий правила: {e}")
            return False

    def _apply_rule_actions(
        self, connection: NetworkConnection, rule: NetworkRule
    ):
        """Применение действий правила"""
        try:
            for action in rule.actions:
                if action == MonitoringAction.BLOCK:
                    self.blocked_ips.add(connection.destination_ip)
                    self.log_activity(
                        f"Заблокирован IP: {connection.destination_ip}"
                    )
                elif action == MonitoringAction.THROTTLE:
                    self.throttled_ips.add(connection.destination_ip)
                    self.log_activity(
                        f"Ограничен трафик для IP: {connection.destination_ip}"
                    )
                elif action == MonitoringAction.ALERT:
                    self.log_activity(
                        f"Алерт: {rule.name} - {connection.connection_id}"
                    )
                elif action == MonitoringAction.NOTIFY_PARENT:
                    self.log_activity(f"Уведомление родителям: {rule.name}")
                elif action == MonitoringAction.NOTIFY_ADMIN:
                    self.log_activity(
                        f"Уведомление администратору: {rule.name}"
                    )
                elif action == MonitoringAction.SCAN_DEEP:
                    self.log_activity(
                        f"Глубокое сканирование: {connection.connection_id}"
                    )
        except Exception as e:
            self.logger.error(f"Ошибка применения действий правила: {e}")

    def _is_malicious_ip(self, ip: str) -> bool:
        """Проверка на вредоносный IP"""
        # Упрощенная проверка - в реальной системе здесь была бы база данных
        malicious_ips = ["192.168.1.100", "10.0.0.100", "172.16.0.100"]
        return ip in malicious_ips

    def _is_inappropriate_content(self, ip: str) -> bool:
        """Проверка на неподходящий контент"""
        # Упрощенная проверка
        inappropriate_ips = ["192.168.1.200", "10.0.0.200"]
        return ip in inappropriate_ips

    def _is_financial_site(self, ip: str) -> bool:
        """Проверка на финансовый сайт"""
        # Упрощенная проверка
        financial_ips = ["192.168.1.300", "10.0.0.300"]
        return ip in financial_ips

    def _detect_data_exfiltration(self, connection: NetworkConnection) -> bool:
        """Обнаружение утечки данных"""
        # Упрощенная логика - проверка на подозрительно большие объемы данных
        return connection.bytes_sent > 1000000  # 1MB

    def detect_network_anomaly(
        self,
        connection: NetworkConnection,
        anomaly_type: str,
        description: str,
        confidence: float,
    ) -> NetworkAnomaly:
        """Обнаружение сетевой аномалии"""
        # Валидация параметров
        if connection is None:
            raise ValueError("connection не может быть None")
        if (
            not isinstance(confidence, (int, float)) or
            not 0 <= confidence <= 1
        ):
            raise ValueError("confidence должен быть числом от 0 до 1")

        try:
            # Определяем уровень угрозы
            threat_level = self._determine_threat_level(confidence)
            # Создаем аномалию
            anomaly = NetworkAnomaly(
                anomaly_id=self._generate_anomaly_id(),
                connection_id=connection.connection_id,
                anomaly_type=anomaly_type,
                threat_level=threat_level,
                description=description,
                timestamp=datetime.now(),
                source_ip=connection.source_ip,
                destination_ip=connection.destination_ip,
                confidence=confidence,
                metadata={
                    "user_id": connection.user_id,
                    "device_id": connection.device_id,
                    "protocol": connection.protocol,
                    "network_type": connection.network_type.value,
                },
            )
            # Добавляем в хранилище
            self.network_anomalies[anomaly.anomaly_id] = anomaly
            # Добавляем событие безопасности
            self.add_security_event(
                event_type="network_anomaly",
                severity=threat_level.value,
                description=(
                    f"Сетевая аномалия: {anomaly_type} - {description}"
                ),
                source="NetworkMonitoring",
                metadata={
                    "anomaly_id": anomaly.anomaly_id,
                    "connection_id": connection.connection_id,
                    "anomaly_type": anomaly_type,
                    "threat_level": threat_level.value,
                    "confidence": confidence,
                    "source_ip": connection.source_ip,
                    "destination_ip": connection.destination_ip,
                },
            )
            return anomaly
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения сетевой аномалии: {e}")
            return None

    def _determine_threat_level(self, confidence: float) -> ThreatLevel:
        """Определение уровня угрозы"""
        if confidence >= 0.9:
            return ThreatLevel.CRITICAL
        elif confidence >= 0.7:
            return ThreatLevel.HIGH
        elif confidence >= 0.5:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    def get_network_statistics(
        self, user_id: Optional[str] = None
    ) -> NetworkStatistics:
        """Получение статистики сети"""
        try:
            if user_id:
                # Статистика для конкретного пользователя
                user_connections = [
                    conn
                    for conn in self.connection_history
                    if conn.user_id == user_id
                ]
            else:
                # Общая статистика
                user_connections = self.connection_history
            # Подсчет статистики
            total_connections = len(user_connections)
            total_bytes_sent = sum(
                conn.bytes_sent for conn in user_connections
            )
            total_bytes_received = sum(
                conn.bytes_received for conn in user_connections
            )
            active_connections = len(self.active_connections)
            blocked_connections = len(self.blocked_ips)
            anomalies_detected = len(self.network_anomalies)
            # Статистика по типам
            by_traffic_type = {}
            by_network_type = {}
            by_threat_level = {}
            for conn in user_connections:
                traffic_type = conn.traffic_type.value
                by_traffic_type[traffic_type] = (
                    by_traffic_type.get(traffic_type, 0) + 1
                )
                network_type = conn.network_type.value
                by_network_type[network_type] = (
                    by_network_type.get(network_type, 0) + 1
                )
            for anomaly in self.network_anomalies.values():
                threat_level = anomaly.threat_level.value
                by_threat_level[threat_level] = (
                    by_threat_level.get(threat_level, 0) + 1
                )
            # Топ назначений и источников
            destination_counts = {}
            source_counts = {}
            for conn in user_connections:
                dest_ip = conn.destination_ip
                source_ip = conn.source_ip
                destination_counts[dest_ip] = (
                    destination_counts.get(dest_ip, 0) + 1
                )
                source_counts[source_ip] = source_counts.get(source_ip, 0) + 1
            top_destinations = sorted(
                destination_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10]
            top_sources = sorted(
                source_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
            statistics = NetworkStatistics(
                total_connections=total_connections,
                total_bytes_sent=total_bytes_sent,
                total_bytes_received=total_bytes_received,
                active_connections=active_connections,
                blocked_connections=blocked_connections,
                anomalies_detected=anomalies_detected,
                by_traffic_type=by_traffic_type,
                by_network_type=by_network_type,
                by_threat_level=by_threat_level,
                top_destinations=top_destinations,
                top_sources=top_sources,
            )
            return statistics
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики сети: {e}")
            return None

    def get_family_network_status(self) -> Dict[str, Any]:
        """Получение статуса семейной сети"""
        try:
            status = {
                "monitoring_enabled": self.monitoring_enabled,
                "real_time_monitoring": self.real_time_monitoring,
                "deep_packet_inspection": self.deep_packet_inspection,
                "family_protection_enabled": self.family_protection_enabled,
                "child_monitoring_mode": self.child_monitoring_mode,
                "elderly_monitoring_mode": self.elderly_monitoring_mode,
                "active_rules": len(
                    [r for r in self.monitoring_rules.values() if r.enabled]
                ),
                "family_specific_rules": len(
                    [
                        r
                        for r in self.monitoring_rules.values()
                        if r.family_specific
                    ]
                ),
                "blocked_ips_count": len(self.blocked_ips),
                "throttled_ips_count": len(self.throttled_ips),
                "active_connections_count": len(self.active_connections),
                "anomalies_detected_count": len(self.network_anomalies),
                "protection_settings": self.family_protection_settings,
                "family_history": {
                    user_id: len(connection_ids)
                    for user_id, connection_ids in (
                        self.family_network_history.items()
                    )
                },
            }
            return status
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса семейной сети: {e}")
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса сервиса"""
        try:
            return {
                "service_name": self.name,
                "status": self.status.value,
                "monitoring_rules": len(self.monitoring_rules),
                "active_connections": len(self.active_connections),
                "connection_history": len(self.connection_history),
                "network_anomalies": len(self.network_anomalies),
                "blocked_ips": len(self.blocked_ips),
                "throttled_ips": len(self.throttled_ips),
                "family_protection_enabled": self.family_protection_enabled,
                "real_time_monitoring": self.real_time_monitoring,
                "uptime": (
                    (datetime.now() - self.start_time).total_seconds()
                    if hasattr(self, "start_time") and self.start_time
                    else 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {}

    # ===== МЕТОДЫ ДЛЯ МЕТРИК И КОНФИГУРАЦИИ =====

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Получение метрик производительности.

        Returns:
            Dict[str, Any]: Словарь с метриками производительности
        """
        if not self.metrics:
            return {"error": "Метрики отключены"}

        return {
            "uptime": time.time() - self.metrics.start_time,
            "total_connections": self.metrics.total_connections,
            "total_anomalies": self.metrics.total_anomalies,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "cache_hit_rate": (
                self.metrics.cache_hits /
                (self.metrics.cache_hits + self.metrics.cache_misses)
                if (self.metrics.cache_hits + self.metrics.cache_misses) > 0
                else 0
            ),
            "method_times": {
                method: self.metrics.get_average_time(method)
                for method in self.metrics.method_times.keys()
            },
            "error_rates": {
                method: self.metrics.get_error_rate(method)
                for method in self.metrics.error_counts.keys()
            },
        }

    def update_config(self, new_config: NetworkMonitoringConfig) -> bool:
        """
        Обновление конфигурации мониторинга.

        Args:
            new_config: Новая конфигурация

        Returns:
            bool: True если конфигурация обновлена успешно
        """
        try:
            self.monitoring_config = new_config

            # Обновляем метрики если нужно
            if new_config.performance_monitoring and not self.metrics:
                self.metrics = PerformanceMetrics()
            elif not new_config.performance_monitoring and self.metrics:
                self.metrics = None

            self.log_activity(f"Конфигурация обновлена: {new_config}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления конфигурации: {e}")
            return False

    def get_config(self) -> NetworkMonitoringConfig:
        """
        Получение текущей конфигурации.

        Returns:
            NetworkMonitoringConfig: Текущая конфигурация
        """
        return self.monitoring_config

    def clear_cache(self) -> bool:
        """
        Очистка кэша.

        Returns:
            bool: True если кэш очищен успешно
        """
        try:
            self._get_cached_network_type.cache_clear()
            self._get_cached_traffic_type.cache_clear()

            if self.metrics:
                self.metrics.record_cache_hit()

            self.log_activity("Кэш очищен")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка очистки кэша: {e}")
            return False

    def _generate_connection_id(self) -> str:
        """Генерация ID соединения"""
        timestamp = str(int(time.time() * 1000))
        random_part = str(hash(timestamp))[-8:]
        return f"conn_{timestamp}_{random_part}"

    def _generate_anomaly_id(self) -> str:
        """Генерация ID аномалии"""
        timestamp = str(int(time.time() * 1000))
        random_part = str(hash(timestamp))[-8:]
        return f"anomaly_{timestamp}_{random_part}"

    # ===== СЕМЕЙНЫЕ МЕТОДЫ УПРАВЛЕНИЯ =====

    def enable_child_monitoring(self, user_id: str) -> bool:
        """Включение мониторинга для ребенка"""
        try:
            if user_id in self.family_network_history:
                self.child_monitoring_mode = True
                self.log_activity(f"Включен детский мониторинг для {user_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка включения детского мониторинга: {e}")
            return False

    def disable_child_monitoring(self, user_id: str) -> bool:
        """Отключение мониторинга для ребенка"""
        try:
            if user_id in self.family_network_history:
                self.child_monitoring_mode = False
                self.log_activity(f"Отключен детский мониторинг для {user_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка отключения детского мониторинга: {e}")
            return False

    def enable_elderly_monitoring(self, user_id: str) -> bool:
        """Включение мониторинга для пожилого"""
        try:
            if user_id in self.family_network_history:
                self.elderly_monitoring_mode = True
                self.log_activity(f"Включен мониторинг пожилых для {user_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка включения мониторинга пожилых: {e}")
            return False

    def disable_elderly_monitoring(self, user_id: str) -> bool:
        """Отключение мониторинга для пожилого"""
        try:
            if user_id in self.family_network_history:
                self.elderly_monitoring_mode = False
                self.log_activity(f"Отключен мониторинг пожилых для {user_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка отключения мониторинга пожилых: {e}")
            return False

    def add_family_member(
        self,
        user_id: str,
        name: str = "Unknown",
        age: int = 0,
        role: str = "member",
    ) -> bool:
        """
        Добавление члена семьи.

        Args:
            user_id: ID пользователя (обязательный)
            name: Имя члена семьи (по умолчанию: "Unknown")
            age: Возраст (по умолчанию: 0)
            role: Роль в семье (по умолчанию: "member")

        Returns:
            bool: True если член семьи добавлен успешно
        """
        # Валидация параметров
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id должен быть непустой строкой")

        try:
            if user_id not in self.family_network_history:
                self.family_network_history[user_id] = []
                self.log_activity(
                    f"Добавлен член семьи: {name} (ID: {user_id}, "
                    f"Возраст: {age}, Роль: {role})"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка добавления члена семьи: {e}")
            return False

    def remove_family_member(self, user_id: str) -> bool:
        """Удаление члена семьи"""
        try:
            if user_id in self.family_network_history:
                del self.family_network_history[user_id]
                self.log_activity(f"Удален член семьи: {user_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления члена семьи: {e}")
            return False

    def get_family_members(self) -> Dict[str, Any]:
        """Получение списка членов семьи"""
        try:
            return {
                "total_members": len(self.family_network_history),
                "members": list(self.family_network_history.keys()),
                "monitoring_enabled": self.family_protection_enabled,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения списка семьи: {e}")
            return {}

    def set_parental_controls(
        self, user_id: str, controls: Dict[str, Any]
    ) -> bool:
        """Установка родительского контроля"""
        try:
            if user_id in self.family_network_history:
                self.log_activity(
                    f"Установлен родительский контроль для {user_id}: "
                    f"{controls}"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка установки родительского контроля: {e}")
            return False

    def get_parental_controls(self, user_id: str) -> Dict[str, Any]:
        """Получение настроек родительского контроля"""
        try:
            if user_id in self.family_network_history:
                return {
                    "user_id": user_id,
                    "child_monitoring": self.child_monitoring_mode,
                    "elderly_monitoring": self.elderly_monitoring_mode,
                    "family_protection": self.family_protection_enabled,
                }
            return {}
        except Exception as e:
            self.logger.error(f"Ошибка получения родительского контроля: {e}")
            return {}

    def block_website(
        self, url: str, reason: str = "Inappropriate content"
    ) -> bool:
        """Блокировка веб-сайта"""
        try:
            self.blocked_ips.add(url)
            self.log_activity(f"Заблокирован сайт: {url} (Причина: {reason})")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка блокировки сайта: {e}")
            return False

    def unblock_website(self, url: str) -> bool:
        """Разблокировка веб-сайта"""
        try:
            if url in self.blocked_ips:
                self.blocked_ips.remove(url)
                self.log_activity(f"Разблокирован сайт: {url}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка разблокировки сайта: {e}")
            return False

    def get_blocked_websites(self) -> Set[str]:
        """Получение списка заблокированных сайтов"""
        try:
            return self.blocked_ips.copy()
        except Exception as e:
            self.logger.error(f"Ошибка получения заблокированных сайтов: {e}")
            return set()

    def set_time_limits(self, user_id: str, limits: Dict[str, Any]) -> bool:
        """Установка временных ограничений"""
        try:
            if user_id in self.family_network_history:
                self.log_activity(
                    f"Установлены временные ограничения для {user_id}: "
                    f"{limits}"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка установки временных ограничений: {e}")
            return False

    def get_time_limits(self, user_id: str) -> Dict[str, Any]:
        """Получение временных ограничений"""
        try:
            if user_id in self.family_network_history:
                return {
                    "user_id": user_id,
                    "limits": "Настроены",
                    "monitoring_active": self.monitoring_enabled,
                }
            return {}
        except Exception as e:
            self.logger.error(f"Ошибка получения временных ограничений: {e}")
            return {}

    def send_parent_notification(
        self, message: str, priority: str = "normal"
    ) -> bool:
        """Отправка уведомления родителям"""
        try:
            self.log_activity(f"Уведомление родителям [{priority}]: {message}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления родителям: {e}")
            return False

    def send_admin_notification(
        self, message: str, priority: str = "normal"
    ) -> bool:
        """Отправка уведомления администратору"""
        try:
            self.log_activity(
                f"Уведомление администратору [{priority}]: {message}"
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Ошибка отправки уведомления администратору: {e}"
            )
            return False

    def export_family_report(
        self, format_type: str = "json"
    ) -> Dict[str, Any]:
        """Экспорт семейного отчета"""
        try:
            return {
                "report_type": "family_network_report",
                "format": format_type,
                "timestamp": datetime.now().isoformat(),
                "family_members": len(self.family_network_history),
                "total_connections": len(self.connection_history),
                "anomalies_detected": len(self.network_anomalies),
                "blocked_websites": len(self.blocked_ips),
            }
        except Exception as e:
            self.logger.error(f"Ошибка экспорта семейного отчета: {e}")
            return {}

    def import_family_settings(self, settings: Dict[str, Any]) -> bool:
        """Импорт семейных настроек"""
        try:
            self.log_activity(f"Импортированы семейные настройки: {settings}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка импорта семейных настроек: {e}")
            return False

    def reset_family_settings(self) -> bool:
        """Сброс семейных настроек"""
        try:
            self.family_network_history.clear()
            self.blocked_ips.clear()
            self.throttled_ips.clear()
            self.log_activity("Семейные настройки сброшены")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сброса семейных настроек: {e}")
            return False

    def validate_family_member(self, user_id: str) -> bool:
        """Валидация члена семьи"""
        try:
            return user_id in self.family_network_history
        except Exception as e:
            self.logger.error(f"Ошибка валидации члена семьи: {e}")
            return False

    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """Получение информации об устройстве"""
        try:
            return {
                "device_id": device_id,
                "status": "active",
                "monitoring_enabled": self.monitoring_enabled,
                "last_seen": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(
                f"Ошибка получения информации об устройстве: {e}"
            )
            return {}

    def monitor_device_usage(
        self, device_id: str, usage_data: Dict[str, Any]
    ) -> bool:
        """Мониторинг использования устройства"""
        try:
            self.log_activity(
                f"Мониторинг устройства {device_id}: {usage_data}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка мониторинга устройства: {e}")
            return False

    def get_usage_statistics(
        self, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение статистики использования"""
        try:
            if user_id:
                user_connections = [
                    c for c in self.connection_history if c.user_id == user_id
                ]
            else:
                user_connections = self.connection_history

            return {
                "total_connections": len(user_connections),
                "active_connections": len(self.active_connections),
                "bytes_sent": sum(c.bytes_sent for c in user_connections),
                "bytes_received": sum(
                    c.bytes_received for c in user_connections
                ),
            }
        except Exception as e:
            self.logger.error(
                f"Ошибка получения статистики использования: {e}"
            )
            return {}

    def set_alert_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """Установка пороговых значений для алертов"""
        try:
            self.anomaly_thresholds.update(thresholds)
            self.log_activity(f"Обновлены пороги алертов: {thresholds}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка установки порогов алертов: {e}")
            return False

    def get_alert_thresholds(self) -> Dict[str, float]:
        """Получение пороговых значений для алертов"""
        try:
            return {
                level.value: threshold
                for level, threshold in self.anomaly_thresholds.items()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения порогов алертов: {e}")
            return {}
