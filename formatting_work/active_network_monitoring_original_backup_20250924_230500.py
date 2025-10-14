# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Network Monitoring Service
Система мониторинга сетевой активности для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import logging
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from core.base import SecurityBase


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
    """Сервис мониторинга сетевой активности для семей"""

    def __init__(self, name: str = "NetworkMonitoring", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.logger = logging.getLogger(__name__)
        # Хранилища данных
        self.active_connections: Dict[str, NetworkConnection] = {}
        self.connection_history: List[NetworkConnection] = []
        self.network_anomalies: Dict[str, NetworkAnomaly] = {}
        self.monitoring_rules: Dict[str, NetworkRule] = {}
        self.blocked_ips: Set[str] = set()
        self.throttled_ips: Set[str] = set()
        self.family_network_history: Dict[str, List[str]] = {}  # user_id -> connection_ids
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
            ThreatLevel.CRITICAL: 0.9
        }
        # Инициализация
        self._initialize_monitoring_rules()
        self._setup_family_protection()
        self._start_monitoring()

    def _initialize_monitoring_rules(self):
        """Инициализация правил мониторинга"""
        rules = [
            NetworkRule(
                rule_id="block_malicious_ips",
                name="Блокировка вредоносных IP",
                description="Блокировка известных вредоносных IP-адресов",
                conditions={"malicious_ip": True},
                actions=[MonitoringAction.BLOCK, MonitoringAction.ALERT],
                family_specific=True
            ),
            NetworkRule(
                rule_id="monitor_child_gaming",
                name="Мониторинг игрового трафика детей",
                description="Контроль игрового трафика для детей",
                conditions={"age_group": "child", "traffic_type": "gaming"},
                actions=[MonitoringAction.LOG, MonitoringAction.NOTIFY_PARENT],
                family_specific=True,
                age_group="child"
            ),
            NetworkRule(
                rule_id="monitor_elderly_financial",
                name="Мониторинг финансового трафика пожилых",
                description="Контроль финансовых операций пожилых",
                conditions={"age_group": "elderly", "financial_site": True},
                actions=[MonitoringAction.LOG, MonitoringAction.NOTIFY_ADMIN],
                family_specific=True,
                age_group="elderly"
            ),
            NetworkRule(
                rule_id="block_inappropriate_content",
                name="Блокировка неподходящего контента",
                description="Блокировка доступа к неподходящему контенту",
                conditions={"inappropriate_content": True},
                actions=[MonitoringAction.BLOCK, MonitoringAction.NOTIFY_PARENT],
                family_specific=True
            ),
            NetworkRule(
                rule_id="throttle_high_bandwidth",
                name="Ограничение высокой пропускной способности",
                description="Ограничение трафика при превышении лимитов",
                conditions={"bandwidth_exceeded": True},
                actions=[MonitoringAction.THROTTLE, MonitoringAction.ALERT],
                family_specific=True
            ),
            NetworkRule(
                rule_id="monitor_social_media",
                name="Мониторинг социальных сетей",
                description="Контроль активности в социальных сетях",
                conditions={"traffic_type": "social_media"},
                actions=[MonitoringAction.LOG, MonitoringAction.NOTIFY_PARENT],
                family_specific=True
            ),
            NetworkRule(
                rule_id="detect_data_exfiltration",
                name="Обнаружение утечки данных",
                description="Обнаружение подозрительной передачи данных",
                conditions={"data_exfiltration": True},
                actions=[MonitoringAction.BLOCK, MonitoringAction.ALERT, MonitoringAction.SCAN_DEEP],
                family_specific=True
            ),
            NetworkRule(
                rule_id="monitor_vpn_usage",
                name="Мониторинг использования VPN",
                description="Контроль использования VPN-соединений",
                conditions={"network_type": "vpn"},
                actions=[MonitoringAction.LOG, MonitoringAction.ALERT],
                family_specific=True
            )
        ]
        for rule in rules:
            self.monitoring_rules[rule.rule_id] = rule
        self.log_activity(f"Инициализировано {len(rules)} правил мониторинга сети")

    def _setup_family_protection(self):
        """Настройка семейной защиты"""
        self.family_protection_settings = {
            "child_protection": {
                "enabled": True,
                "gaming_time_limits": True,
                "social_media_monitoring": True,
                "inappropriate_content_blocking": True,
                "parent_notifications": True
            },
            "elderly_protection": {
                "enabled": True,
                "financial_site_monitoring": True,
                "phishing_detection": True,
                "family_notifications": True,
                "suspicious_activity_alerts": True
            },
            "general_family": {
                "unified_monitoring": True,
                "shared_network_policies": True,
                "family_aware_blocking": True,
                "real_time_alerts": True
            }
        }
        self.log_activity("Настроена семейная защита сетевой активности")

    def _start_monitoring(self):
        """Запуск мониторинга"""
        if self.real_time_monitoring:
            self.log_activity("Запущен мониторинг сетевой активности в реальном времени")
        else:
            self.log_activity("Мониторинг сетевой активности отключен")

    def monitor_connection(self, source_ip: str, destination_ip: str,
                           source_port: int, destination_port: int,
                           protocol: str, user_id: Optional[str] = None,
                           device_id: Optional[str] = None,
                           user_age: Optional[int] = None) -> NetworkConnection:
        """Мониторинг сетевого соединения"""
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
                traffic_type=self._detect_traffic_type(destination_port, protocol),
                bytes_sent=0,
                bytes_received=0,
                start_time=datetime.now(),
                user_id=user_id,
                device_id=device_id,
                metadata={
                    "user_age": user_age,
                    "monitoring_enabled": True
                }
            )
            # Добавляем в активные соединения
            self.active_connections[connection.connection_id] = connection
            # Добавляем в историю соединений
            self.connection_history.append(connection)
            # Добавляем в семейную историю
            if user_id:
                if user_id not in self.family_network_history:
                    self.family_network_history[user_id] = []
                self.family_network_history[user_id].append(connection.connection_id)
            # Проверяем правила мониторинга
            self._check_monitoring_rules(connection)
            # Добавляем событие безопасности
            self.add_security_event(
                event_type="network_connection",
                severity="info",
                description=f"Новое сетевое соединение: {source_ip}:{source_port} -> {destination_ip}:{destination_port}",
                source="NetworkMonitoring",
                metadata={
                    "connection_id": connection.connection_id,
                    "protocol": protocol,
                    "network_type": connection.network_type.value,
                    "traffic_type": connection.traffic_type.value,
                    "user_id": user_id,
                    "user_age": user_age,
                    "device_id": device_id})
            return connection
        except Exception as e:
            self.logger.error(f"Ошибка мониторинга соединения: {e}")
            return None

    def _detect_network_type(self, destination_ip: str) -> NetworkType:
        """Определение типа сети"""
        try:
            # Простая логика определения типа сети
            if destination_ip.startswith("192.168.") or destination_ip.startswith("10."):
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
            elif port in [21, 22, 23, 53, 67, 68, 69, 80, 110, 123, 135, 139, 143, 161, 162, 389, 443, 445, 993, 995]:
                return TrafficType.WEB
            elif port in [6667, 6697, 7000, 7001, 8000, 8001, 8080, 8081]:
                return TrafficType.CHAT
            elif port in [6881, 6882, 6883, 6884, 6885, 6886, 6887, 6888, 6889]:
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

    def _evaluate_rule_conditions(self, connection: NetworkConnection, rule: NetworkRule) -> bool:
        """Оценка условий правила"""
        try:
            conditions = rule.conditions
            # Проверка семейных условий
            if rule.family_specific:
                if rule.age_group == "child" and connection.metadata.get("user_age", 0) >= 18:
                    return False
                elif rule.age_group == "elderly" and connection.metadata.get("user_age", 0) < 65:
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
            if "inappropriate_content" in conditions and conditions["inappropriate_content"]:
                if self._is_inappropriate_content(connection.destination_ip):
                    return True
            # Проверка финансовых сайтов
            if "financial_site" in conditions and conditions["financial_site"]:
                if self._is_financial_site(connection.destination_ip):
                    return True
            # Проверка утечки данных
            if "data_exfiltration" in conditions and conditions["data_exfiltration"]:
                if self._detect_data_exfiltration(connection):
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка оценки условий правила: {e}")
            return False

    def _apply_rule_actions(self, connection: NetworkConnection, rule: NetworkRule):
        """Применение действий правила"""
        try:
            for action in rule.actions:
                if action == MonitoringAction.BLOCK:
                    self.blocked_ips.add(connection.destination_ip)
                    self.log_activity(f"Заблокирован IP: {connection.destination_ip}")
                elif action == MonitoringAction.THROTTLE:
                    self.throttled_ips.add(connection.destination_ip)
                    self.log_activity(f"Ограничен трафик для IP: {connection.destination_ip}")
                elif action == MonitoringAction.ALERT:
                    self.log_activity(f"Алерт: {rule.name} - {connection.connection_id}")
                elif action == MonitoringAction.NOTIFY_PARENT:
                    self.log_activity(f"Уведомление родителям: {rule.name}")
                elif action == MonitoringAction.NOTIFY_ADMIN:
                    self.log_activity(f"Уведомление администратору: {rule.name}")
                elif action == MonitoringAction.SCAN_DEEP:
                    self.log_activity(f"Глубокое сканирование: {connection.connection_id}")
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

    def detect_network_anomaly(self, connection: NetworkConnection,
                               anomaly_type: str, description: str,
                               confidence: float) -> NetworkAnomaly:
        """Обнаружение сетевой аномалии"""
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
                    "network_type": connection.network_type.value
                }
            )
            # Добавляем в хранилище
            self.network_anomalies[anomaly.anomaly_id] = anomaly
            # Добавляем событие безопасности
            self.add_security_event(
                event_type="network_anomaly",
                severity=threat_level.value,
                description=f"Сетевая аномалия: {anomaly_type} - {description}",
                source="NetworkMonitoring",
                metadata={
                    "anomaly_id": anomaly.anomaly_id,
                    "connection_id": connection.connection_id,
                    "anomaly_type": anomaly_type,
                    "threat_level": threat_level.value,
                    "confidence": confidence,
                    "source_ip": connection.source_ip,
                    "destination_ip": connection.destination_ip
                }
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

    def get_network_statistics(self, user_id: Optional[str] = None) -> NetworkStatistics:
        """Получение статистики сети"""
        try:
            if user_id:
                # Статистика для конкретного пользователя
                user_connections = [
                    conn for conn in self.connection_history
                    if conn.user_id == user_id
                ]
            else:
                # Общая статистика
                user_connections = self.connection_history
            # Подсчет статистики
            total_connections = len(user_connections)
            total_bytes_sent = sum(conn.bytes_sent for conn in user_connections)
            total_bytes_received = sum(conn.bytes_received for conn in user_connections)
            active_connections = len(self.active_connections)
            blocked_connections = len(self.blocked_ips)
            anomalies_detected = len(self.network_anomalies)
            # Статистика по типам
            by_traffic_type = {}
            by_network_type = {}
            by_threat_level = {}
            for conn in user_connections:
                traffic_type = conn.traffic_type.value
                by_traffic_type[traffic_type] = by_traffic_type.get(traffic_type, 0) + 1
                network_type = conn.network_type.value
                by_network_type[network_type] = by_network_type.get(network_type, 0) + 1
            for anomaly in self.network_anomalies.values():
                threat_level = anomaly.threat_level.value
                by_threat_level[threat_level] = by_threat_level.get(threat_level, 0) + 1
            # Топ назначений и источников
            destination_counts = {}
            source_counts = {}
            for conn in user_connections:
                dest_ip = conn.destination_ip
                source_ip = conn.source_ip
                destination_counts[dest_ip] = destination_counts.get(dest_ip, 0) + 1
                source_counts[source_ip] = source_counts.get(source_ip, 0) + 1
            top_destinations = sorted(destination_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
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
                top_sources=top_sources
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
                "active_rules": len([r for r in self.monitoring_rules.values() if r.enabled]),
                "family_specific_rules": len([r for r in self.monitoring_rules.values() if r.family_specific]),
                "blocked_ips_count": len(self.blocked_ips),
                "throttled_ips_count": len(self.throttled_ips),
                "active_connections_count": len(self.active_connections),
                "anomalies_detected_count": len(self.network_anomalies),
                "protection_settings": self.family_protection_settings,
                "family_history": {
                    user_id: len(connection_ids)
                    for user_id, connection_ids in self.family_network_history.items()
                }
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
                "monitoring_rules": len(
                    self.monitoring_rules),
                "active_connections": len(
                    self.active_connections),
                "connection_history": len(
                    self.connection_history),
                "network_anomalies": len(
                    self.network_anomalies),
                "blocked_ips": len(
                    self.blocked_ips),
                "throttled_ips": len(
                    self.throttled_ips),
                "family_protection_enabled": self.family_protection_enabled,
                "real_time_monitoring": self.real_time_monitoring,
                "uptime": (
                    datetime.now() -
                    self.start_time).total_seconds() if hasattr(
                    self,
                    'start_time') and self.start_time else 0}
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {}

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