# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Network Security Agent
AI агент сетевой безопасности для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import random

from core.base import ComponentStatus, SecurityBase


class NetworkThreatType(Enum):
    """Типы сетевых угроз"""
    DDoS = "ddos"
    PORT_SCAN = "port_scan"
    BRUTE_FORCE = "brute_force"
    MALWARE = "malware"
    PHISHING = "phishing"
    MAN_IN_THE_MIDDLE = "mitm"
    DNS_SPOOFING = "dns_spoofing"
    ARP_SPOOFING = "arp_spoofing"
    UNKNOWN = "unknown"


class NetworkProtocol(Enum):
    """Сетевые протоколы"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    FTP = "ftp"
    SSH = "ssh"
    TELNET = "telnet"
    SMTP = "smtp"
    DNS = "dns"
    DHCP = "dhcp"
    SNMP = "snmp"


class ThreatSeverity(Enum):
    """Уровни серьезности угроз"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NetworkStatus(Enum):
    """Статусы сети"""
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    COMPROMISED = "compromised"
    UNDER_ATTACK = "under_attack"
    MAINTENANCE = "maintenance"


@dataclass
class NetworkPacket:
    """Сетевой пакет"""
    packet_id: str
    timestamp: datetime
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: NetworkProtocol
    packet_size: int
    payload: Optional[bytes] = None
    flags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.flags is None:
            self.flags = {}
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['protocol'] = self.protocol.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.payload:
            data['payload'] = self.payload.hex()
        return data


@dataclass
class NetworkThreat:
    """Сетевая угроза"""
    threat_id: str
    threat_type: NetworkThreatType
    severity: ThreatSeverity
    source_ip: str
    destination_ip: str
    protocol: NetworkProtocol
    port: int
    timestamp: datetime
    description: str
    confidence: float
    indicators: List[str]
    mitigation_actions: List[str]
    affected_services: List[str]
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['threat_type'] = self.threat_type.value
        data['severity'] = self.severity.value
        data['protocol'] = self.protocol.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class NetworkFlow:
    """Сетевой поток"""
    flow_id: str
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: NetworkProtocol
    start_time: datetime
    end_time: Optional[datetime]
    packets_sent: int
    bytes_sent: int
    packets_received: int
    bytes_received: int
    duration: float
    status: NetworkStatus
    threat_score: float
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['protocol'] = self.protocol.value
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat() if self.end_time else None
        data['status'] = self.status.value
        return data


@dataclass
class NetworkAnalysis:
    """Результат сетевого анализа"""
    analysis_id: str
    timestamp: datetime
    network_status: NetworkStatus
    threat_level: ThreatSeverity
    total_threats: int
    active_flows: int
    blocked_connections: int
    allowed_connections: int
    threats_detected: List[NetworkThreat]
    suspicious_flows: List[NetworkFlow]
    recommendations: List[str]
    network_metrics: Dict[str, Any]
    analysis_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['network_status'] = self.network_status.value
        data['threat_level'] = self.threat_level.value
        data['timestamp'] = self.timestamp.isoformat()
        data['threats_detected'] = [threat.to_dict() for threat in self.threats_detected]
        data['suspicious_flows'] = [flow.to_dict() for flow in self.suspicious_flows]
        return data


@dataclass
class NetworkMetrics:
    """Метрики сетевой безопасности"""
    total_packets_analyzed: int = 0
    total_flows_monitored: int = 0
    threats_detected: int = 0
    ddos_attacks_blocked: int = 0
    port_scans_detected: int = 0
    brute_force_attempts: int = 0
    malware_connections: int = 0
    phishing_attempts: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    average_analysis_time: float = 0.0
    last_analysis: Optional[datetime] = None

    def __post_init__(self):
        if self.last_analysis is None:
            self.last_analysis = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['last_analysis'] = self.last_analysis.isoformat() if self.last_analysis else None
        return data


class NetworkSecurityAgent(SecurityBase):
    """AI агент сетевой безопасности для ALADDIN Security System"""

    def __init__(self, name: str = "NetworkSecurityAgent"):
        super().__init__(name)

        # Конфигурация агента
        self.analysis_interval = 10  # секунды
        self.packet_retention_hours = 2
        self.flow_retention_hours = 24
        self.threat_detection_threshold = 0.7
        self.ddos_threshold = 1000  # пакетов в секунду
        self.port_scan_threshold = 50  # портов за минуту
        self.brute_force_threshold = 10  # попыток за минуту

        # Хранилище данных
        self.network_packets: List[NetworkPacket] = []
        self.network_flows: Dict[str, NetworkFlow] = {}
        self.detected_threats: List[NetworkThreat] = []
        self.network_metrics: NetworkMetrics = NetworkMetrics()
        self.analysis_lock = threading.RLock()

        # AI компоненты для анализа
        self.ai_enabled = True
        self.ml_models = {
            "threat_classifier": None,
            "anomaly_detector": None,
            "flow_analyzer": None,
            "packet_inspector": None,
            "ddos_detector": None,
            "intrusion_detector": None
        }

        # Статистика
        self.statistics: Dict[str, Any] = {
            "total_analyses_performed": 0,
            "total_packets_processed": 0,
            "total_flows_analyzed": 0,
            "start_time": None,
            "last_analysis": None,
            "average_analysis_time": 0.0,
            "detection_accuracy": 0.0
        }

        # Сетевые правила
        self.network_rules: Dict[str, Any] = {
            "blocked_ips": set(),
            "blocked_ports": set(),
            "allowed_protocols": {p.value for p in NetworkProtocol},
            "rate_limits": {
                "packets_per_second": 1000,
                "connections_per_minute": 100,
                "bytes_per_second": 1000000
            }
        }

    def initialize(self) -> bool:
        """Инициализация агента сетевой безопасности"""
        try:
            self.log_activity("Инициализация Network Security Agent", "info")
            self.status = ComponentStatus.RUNNING
            self.statistics["start_time"] = datetime.now()

            # Инициализация AI моделей
            self._initialize_ai_models()

            # Загрузка сетевых правил
            self._load_network_rules()

            # Запуск фоновых задач
            self._start_background_tasks()

            self.log_activity("Network Security Agent успешно инициализирован", "info")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации Network Security Agent: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def stop(self) -> bool:
        """Остановка агента сетевой безопасности"""
        try:
            self.log_activity("Остановка Network Security Agent", "info")
            self.status = ComponentStatus.STOPPED

            # Остановка фоновых задач
            self._stop_background_tasks()

            # Сохранение состояния
            self._save_network_state()

            # Очистка данных
            with self.analysis_lock:
                self.network_packets.clear()
                self.network_flows.clear()
                self.detected_threats.clear()

            self.log_activity("Network Security Agent остановлен", "info")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка остановки Network Security Agent: {e}", "error")
            return False

    def analyze_packet(self, packet_data: Dict[str, Any]) -> Optional[NetworkThreat]:
        """Анализ сетевого пакета"""
        try:
            with self.analysis_lock:
                start_time = time.time()

                # Создание объекта пакета
                packet = self._create_network_packet(packet_data)

                # Добавление пакета в историю
                self._add_network_packet(packet)

                # Анализ пакета на угрозы
                threat = self._analyze_packet_threats(packet)

                if threat:
                    # Добавление угрозы в список
                    self._add_detected_threat(threat)

                    # Обновление метрик
                    self._update_network_metrics(threat)

                # Обновление статистики
                analysis_time = time.time() - start_time
                self.statistics["total_packets_processed"] += 1
                self.statistics["last_analysis"] = datetime.now()
                self.statistics["average_analysis_time"] = (
                    (self.statistics["average_analysis_time"] *
                     (self.statistics["total_packets_processed"] - 1) +
                     analysis_time) / self.statistics["total_packets_processed"]
                )

                return threat

        except Exception as e:
            self.log_activity(f"Ошибка анализа пакета: {e}", "error")
            return None

    def analyze_network_flow(self, flow_data: Dict[str, Any]) -> Optional[NetworkFlow]:
        """Анализ сетевого потока"""
        try:
            with self.analysis_lock:
                # Создание объекта потока
                flow = self._create_network_flow(flow_data)

                # Добавление потока в мониторинг
                self._add_network_flow(flow)

                # Анализ потока на подозрительность
                self._analyze_flow_suspiciousness(flow)

                return flow

        except Exception as e:
            self.log_activity(f"Ошибка анализа сетевого потока: {e}", "error")
            return None

    def get_network_analysis(self) -> Optional[NetworkAnalysis]:
        """Получение анализа сети"""
        try:
            with self.analysis_lock:
                # Анализ текущего состояния сети
                network_status = self._assess_network_status()
                threat_level = self._assess_threat_level()

                # Подсчет метрик
                total_threats = len(self.detected_threats)
                active_flows = len([f for f in self.network_flows.values() if f.end_time is None])
                blocked_connections = len(self.network_rules["blocked_ips"])
                allowed_connections = len(self.network_flows) - blocked_connections

                # Получение подозрительных потоков
                suspicious_flows = [
                    f for f in self.network_flows.values()
                    if f.threat_score > self.threat_detection_threshold
                ]

                # Генерация рекомендаций
                recommendations = self._generate_network_recommendations(
                    network_status, threat_level, total_threats
                )

                # Создание анализа
                analysis = NetworkAnalysis(
                    analysis_id=f"analysis-{int(time.time() * 1000)}",
                    timestamp=datetime.now(),
                    network_status=network_status,
                    threat_level=threat_level,
                    total_threats=total_threats,
                    active_flows=active_flows,
                    blocked_connections=blocked_connections,
                    allowed_connections=allowed_connections,
                    threats_detected=self.detected_threats[-10:],  # Последние 10 угроз
                    suspicious_flows=suspicious_flows[-5:],  # Последние 5 подозрительных потоков
                    recommendations=recommendations,
                    network_metrics=self.network_metrics.to_dict(),
                    analysis_metadata={
                        "packets_analyzed": len(self.network_packets),
                        "flows_monitored": len(self.network_flows),
                        "analysis_duration": 0.1,
                        "ai_models_used": list(self.ml_models.keys())
                    }
                )

                return analysis

        except Exception as e:
            self.log_activity(f"Ошибка получения анализа сети: {e}", "error")
            return None

    def get_network_metrics(self) -> NetworkMetrics:
        """Получение метрик сетевой безопасности"""
        try:
            with self.analysis_lock:
                return self.network_metrics
        except Exception as e:
            self.log_activity(f"Ошибка получения метрик сети: {e}", "error")
            return NetworkMetrics()

    def get_agent_status(self) -> Dict[str, Any]:
        """Получение статуса агента"""
        try:
            with self.analysis_lock:
                return {
                    "status": self.status.value,
                    "total_packets": len(self.network_packets),
                    "total_flows": len(self.network_flows),
                    "total_threats": len(self.detected_threats),
                    "metrics": self.network_metrics.to_dict(),
                    "statistics": self.statistics,
                    "ai_enabled": self.ai_enabled,
                    "analysis_interval": self.analysis_interval,
                    "network_rules": {
                        "blocked_ips_count": len(self.network_rules["blocked_ips"]),
                        "blocked_ports_count": len(self.network_rules["blocked_ports"]),
                        "allowed_protocols": list(self.network_rules["allowed_protocols"])
                    }
                }
        except Exception as e:
            self.log_activity(f"Ошибка получения статуса агента: {e}", "error")
            return {}

    def block_ip(self, ip_address: str, reason: str = "Security threat") -> bool:
        """Блокировка IP адреса"""
        try:
            with self.analysis_lock:
                self.network_rules["blocked_ips"].add(ip_address)
                self.log_activity(f"IP адрес {ip_address} заблокирован: {reason}", "warning")
                return True
        except Exception as e:
            self.log_activity(f"Ошибка блокировки IP адреса: {e}", "error")
            return False

    def unblock_ip(self, ip_address: str) -> bool:
        """Разблокировка IP адреса"""
        try:
            with self.analysis_lock:
                self.network_rules["blocked_ips"].discard(ip_address)
                self.log_activity(f"IP адрес {ip_address} разблокирован", "info")
                return True
        except Exception as e:
            self.log_activity(f"Ошибка разблокировки IP адреса: {e}", "error")
            return False

    def _initialize_ai_models(self):
        """Инициализация AI моделей"""
        try:
            # Симуляция инициализации AI моделей
            self.log_activity("AI модели сетевой безопасности инициализированы", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации AI моделей: {e}", "error")

    def _load_network_rules(self):
        """Загрузка сетевых правил"""
        try:
            # Добавление тестовых заблокированных IP
            test_blocked_ips = ["192.168.1.100", "10.0.0.50", "172.16.0.25"]
            self.network_rules["blocked_ips"].update(test_blocked_ips)

            # Добавление заблокированных портов
            test_blocked_ports = {23, 135, 139, 445, 1433, 3389}
            self.network_rules["blocked_ports"].update(test_blocked_ports)

            self.log_activity(
                f"Загружено {len(test_blocked_ips)} заблокированных IP и "
                f"{len(test_blocked_ports)} заблокированных портов", "info"
            )
        except Exception as e:
            self.log_activity(f"Ошибка загрузки сетевых правил: {e}", "error")

    def _start_background_tasks(self):
        """Запуск фоновых задач"""
        try:
            # Запуск задачи анализа сети
            analysis_thread = threading.Thread(
                target=self._network_analysis_task,
                daemon=True
            )
            analysis_thread.start()

            # Запуск задачи очистки данных
            cleanup_thread = threading.Thread(
                target=self._data_cleanup_task,
                daemon=True
            )
            cleanup_thread.start()

            self.log_activity("Фоновые задачи запущены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка запуска фоновых задач: {e}", "error")

    def _stop_background_tasks(self):
        """Остановка фоновых задач"""
        try:
            # Фоновые задачи остановятся автоматически при остановке агента
            self.log_activity("Фоновые задачи остановлены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка остановки фоновых задач: {e}", "error")

    def _create_network_packet(self, packet_data: Dict[str, Any]) -> NetworkPacket:
        """Создание объекта сетевого пакета"""
        try:
            packet = NetworkPacket(
                packet_id=f"packet-{int(time.time() * 1000)}-{random.randint(1000, 9999)}",
                timestamp=datetime.now(),
                source_ip=packet_data.get("source_ip", "0.0.0.0"),
                destination_ip=packet_data.get("destination_ip", "0.0.0.0"),
                source_port=packet_data.get("source_port", 0),
                destination_port=packet_data.get("destination_port", 0),
                protocol=NetworkProtocol(packet_data.get("protocol", "tcp")),
                packet_size=packet_data.get("packet_size", 0),
                payload=packet_data.get("payload"),
                flags=packet_data.get("flags", {}),
                metadata=packet_data.get("metadata", {})
            )

            return packet

        except Exception as e:
            self.log_activity(f"Ошибка создания сетевого пакета: {e}", "error")
            # Возвращаем базовый пакет
            return NetworkPacket(
                packet_id=f"packet-{int(time.time() * 1000)}",
                timestamp=datetime.now(),
                source_ip="0.0.0.0",
                destination_ip="0.0.0.0",
                source_port=0,
                destination_port=0,
                protocol=NetworkProtocol.TCP,
                packet_size=0
            )

    def _add_network_packet(self, packet: NetworkPacket):
        """Добавление сетевого пакета"""
        try:
            self.network_packets.append(packet)

            # Ограничиваем количество пакетов
            max_packets = 10000
            if len(self.network_packets) > max_packets:
                self.network_packets = self.network_packets[-max_packets:]

            # Очищаем старые пакеты
            cutoff_time = datetime.now() - timedelta(hours=self.packet_retention_hours)
            self.network_packets = [
                p for p in self.network_packets
                if p.timestamp > cutoff_time
            ]

            self.network_metrics.total_packets_analyzed += 1

        except Exception as e:
            self.log_activity(f"Ошибка добавления сетевого пакета: {e}", "error")

    def _analyze_packet_threats(self, packet: NetworkPacket) -> Optional[NetworkThreat]:
        """Анализ пакета на угрозы"""
        try:
            # Проверка на заблокированные IP
            if packet.source_ip in self.network_rules["blocked_ips"]:
                return self._create_threat(
                    NetworkThreatType.MALWARE,
                    ThreatSeverity.HIGH,
                    packet,
                    "Заблокированный IP адрес"
                )

            # Проверка на заблокированные порты
            if packet.destination_port in self.network_rules["blocked_ports"]:
                return self._create_threat(
                    NetworkThreatType.PORT_SCAN,
                    ThreatSeverity.MEDIUM,
                    packet,
                    "Попытка подключения к заблокированному порту"
                )

            # Проверка на подозрительные протоколы
            if packet.protocol not in [NetworkProtocol(p) for p in self.network_rules["allowed_protocols"]]:
                return self._create_threat(
                    NetworkThreatType.MALWARE,
                    ThreatSeverity.MEDIUM,
                    packet,
                    "Использование неразрешенного протокола"
                )

            # Проверка на аномальный размер пакета
            if packet.packet_size > 65535:  # Максимальный размер IP пакета
                return self._create_threat(
                    NetworkThreatType.DDoS,
                    ThreatSeverity.HIGH,
                    packet,
                    "Аномально большой размер пакета"
                )

            # Проверка на частые пакеты (DDoS)
            recent_packets = [
                p for p in self.network_packets[-100:]
                if p.source_ip == packet.source_ip and
                p.timestamp > datetime.now() - timedelta(seconds=1)
            ]
            if len(recent_packets) > self.ddos_threshold:
                return self._create_threat(
                    NetworkThreatType.DDoS,
                    ThreatSeverity.CRITICAL,
                    packet,
                    "Обнаружена DDoS атака"
                )

            return None

        except Exception as e:
            self.log_activity(f"Ошибка анализа угроз пакета: {e}", "error")
            return None

    def _create_threat(self, threat_type: NetworkThreatType, severity: ThreatSeverity,
                       packet: NetworkPacket, description: str) -> NetworkThreat:
        """Создание объекта угрозы"""
        try:
            threat = NetworkThreat(
                threat_id=f"threat-{int(time.time() * 1000)}",
                threat_type=threat_type,
                severity=severity,
                source_ip=packet.source_ip,
                destination_ip=packet.destination_ip,
                protocol=packet.protocol,
                port=packet.destination_port,
                timestamp=datetime.now(),
                description=description,
                confidence=0.8,
                indicators=[description],
                mitigation_actions=self._get_mitigation_actions(threat_type),
                affected_services=[f"port_{packet.destination_port}"],
                metadata={"packet_id": packet.packet_id}
            )

            return threat

        except Exception as e:
            self.log_activity(f"Ошибка создания угрозы: {e}", "error")
            return None

    def _get_mitigation_actions(self, threat_type: NetworkThreatType) -> List[str]:
        """Получение действий по устранению угроз"""
        try:
            actions_map = {
                NetworkThreatType.DDoS: [
                    "Блокировать IP адрес источника",
                    "Включить rate limiting",
                    "Перенаправить трафик через фильтр"
                ],
                NetworkThreatType.PORT_SCAN: [
                    "Блокировать IP адрес",
                    "Усилить мониторинг портов",
                    "Уведомить администратора"
                ],
                NetworkThreatType.BRUTE_FORCE: [
                    "Временно заблокировать IP",
                    "Увеличить задержку между попытками",
                    "Требовать дополнительную аутентификацию"
                ],
                NetworkThreatType.MALWARE: [
                    "Немедленно заблокировать IP",
                    "Сканировать систему на вредоносное ПО",
                    "Изолировать зараженные системы"
                ],
                NetworkThreatType.PHISHING: [
                    "Блокировать подозрительные домены",
                    "Фильтровать входящие сообщения",
                    "Обновить базу данных угроз"
                ]
            }

            return actions_map.get(threat_type, ["Провести дополнительное расследование"])

        except Exception as e:
            self.log_activity(f"Ошибка получения действий по устранению: {e}", "error")
            return ["Ошибка анализа - требуется ручная проверка"]

    def _add_detected_threat(self, threat: NetworkThreat):
        """Добавление обнаруженной угрозы"""
        try:
            self.detected_threats.append(threat)

            # Ограничиваем количество угроз
            max_threats = 1000
            if len(self.detected_threats) > max_threats:
                self.detected_threats = self.detected_threats[-max_threats:]

            # Автоматическая блокировка критических угроз
            if threat.severity == ThreatSeverity.CRITICAL:
                self.block_ip(threat.source_ip, f"Критическая угроза: {threat.description}")

        except Exception as e:
            self.log_activity(f"Ошибка добавления обнаруженной угрозы: {e}", "error")

    def _update_network_metrics(self, threat: NetworkThreat):
        """Обновление метрик сети"""
        try:
            self.network_metrics.threats_detected += 1
            self.network_metrics.last_analysis = datetime.now()

            if threat.threat_type == NetworkThreatType.DDoS:
                self.network_metrics.ddos_attacks_blocked += 1
            elif threat.threat_type == NetworkThreatType.PORT_SCAN:
                self.network_metrics.port_scans_detected += 1
            elif threat.threat_type == NetworkThreatType.BRUTE_FORCE:
                self.network_metrics.brute_force_attempts += 1
            elif threat.threat_type == NetworkThreatType.MALWARE:
                self.network_metrics.malware_connections += 1
            elif threat.threat_type == NetworkThreatType.PHISHING:
                self.network_metrics.phishing_attempts += 1

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрик сети: {e}", "error")

    def _create_network_flow(self, flow_data: Dict[str, Any]) -> NetworkFlow:
        """Создание объекта сетевого потока"""
        try:
            flow = NetworkFlow(
                flow_id=f"flow-{int(time.time() * 1000)}-{random.randint(1000, 9999)}",
                source_ip=flow_data.get("source_ip", "0.0.0.0"),
                destination_ip=flow_data.get("destination_ip", "0.0.0.0"),
                source_port=flow_data.get("source_port", 0),
                destination_port=flow_data.get("destination_port", 0),
                protocol=NetworkProtocol(flow_data.get("protocol", "tcp")),
                start_time=datetime.now(),
                end_time=None,
                packets_sent=flow_data.get("packets_sent", 0),
                bytes_sent=flow_data.get("bytes_sent", 0),
                packets_received=flow_data.get("packets_received", 0),
                bytes_received=flow_data.get("bytes_received", 0),
                duration=0.0,
                status=NetworkStatus.NORMAL,
                threat_score=0.0,
                metadata=flow_data.get("metadata", {})
            )

            return flow

        except Exception as e:
            self.log_activity(f"Ошибка создания сетевого потока: {e}", "error")
            return None

    def _add_network_flow(self, flow: NetworkFlow):
        """Добавление сетевого потока"""
        try:
            self.network_flows[flow.flow_id] = flow
            self.network_metrics.total_flows_monitored += 1

            # Ограничиваем количество потоков
            max_flows = 5000
            if len(self.network_flows) > max_flows:
                # Удаляем самые старые потоки
                oldest_flows = sorted(
                    self.network_flows.items(),
                    key=lambda x: x[1].start_time
                )[:len(self.network_flows) - max_flows]

                for flow_id, _ in oldest_flows:
                    del self.network_flows[flow_id]

        except Exception as e:
            self.log_activity(f"Ошибка добавления сетевого потока: {e}", "error")

    def _analyze_flow_suspiciousness(self, flow: NetworkFlow):
        """Анализ подозрительности потока"""
        try:
            threat_score = 0.0

            # Проверка на заблокированные IP
            if flow.source_ip in self.network_rules["blocked_ips"]:
                threat_score += 0.8

            # Проверка на заблокированные порты
            if flow.destination_port in self.network_rules["blocked_ports"]:
                threat_score += 0.6

            # Проверка на аномальный объем трафика
            if flow.bytes_sent > 1000000:  # 1MB
                threat_score += 0.3

            # Проверка на частые соединения
            recent_flows = [
                f for f in self.network_flows.values()
                if f.source_ip == flow.source_ip and
                f.start_time > datetime.now() - timedelta(minutes=1)
            ]
            if len(recent_flows) > 10:
                threat_score += 0.4

            # Обновление потока
            flow.threat_score = min(threat_score, 1.0)
            if threat_score > self.threat_detection_threshold:
                flow.status = NetworkStatus.SUSPICIOUS

        except Exception as e:
            self.log_activity(f"Ошибка анализа подозрительности потока: {e}", "error")

    def _assess_network_status(self) -> NetworkStatus:
        """Оценка состояния сети"""
        try:
            # Анализ последних угроз
            recent_threats = [
                t for t in self.detected_threats
                if t.timestamp > datetime.now() - timedelta(minutes=5)
            ]

            if not recent_threats:
                return NetworkStatus.NORMAL

            # Проверка на критические угрозы
            critical_threats = [t for t in recent_threats if t.severity == ThreatSeverity.CRITICAL]
            if critical_threats:
                return NetworkStatus.UNDER_ATTACK

            # Проверка на высокие угрозы
            high_threats = [t for t in recent_threats if t.severity == ThreatSeverity.HIGH]
            if len(high_threats) > 5:
                return NetworkStatus.COMPROMISED

            # Проверка на подозрительные потоки
            suspicious_flows = [
                f for f in self.network_flows.values()
                if f.status == NetworkStatus.SUSPICIOUS
            ]
            if len(suspicious_flows) > 10:
                return NetworkStatus.SUSPICIOUS

            return NetworkStatus.NORMAL

        except Exception as e:
            self.log_activity(f"Ошибка оценки состояния сети: {e}", "error")
            return NetworkStatus.NORMAL

    def _assess_threat_level(self) -> ThreatSeverity:
        """Оценка уровня угроз"""
        try:
            # Анализ последних угроз
            recent_threats = [
                t for t in self.detected_threats
                if t.timestamp > datetime.now() - timedelta(minutes=10)
            ]

            if not recent_threats:
                return ThreatSeverity.LOW

            # Подсчет угроз по серьезности
            critical_count = len([t for t in recent_threats if t.severity == ThreatSeverity.CRITICAL])
            high_count = len([t for t in recent_threats if t.severity == ThreatSeverity.HIGH])
            medium_count = len([t for t in recent_threats if t.severity == ThreatSeverity.MEDIUM])

            if critical_count > 0:
                return ThreatSeverity.CRITICAL
            elif high_count > 3:
                return ThreatSeverity.HIGH
            elif medium_count > 5:
                return ThreatSeverity.MEDIUM
            else:
                return ThreatSeverity.LOW

        except Exception as e:
            self.log_activity(f"Ошибка оценки уровня угроз: {e}", "error")
            return ThreatSeverity.MEDIUM

    def _generate_network_recommendations(self, network_status: NetworkStatus,
                                          threat_level: ThreatSeverity,
                                          total_threats: int) -> List[str]:
        """Генерация рекомендаций по сети"""
        try:
            recommendations = []

            if network_status == NetworkStatus.UNDER_ATTACK:
                recommendations.extend([
                    "Немедленно активировать режим экстренной защиты",
                    "Блокировать все подозрительные IP адреса",
                    "Уведомить команду безопасности",
                    "Активировать дополнительные фильтры"
                ])
            elif network_status == NetworkStatus.COMPROMISED:
                recommendations.extend([
                    "Усилить мониторинг сети",
                    "Провести глубокий анализ безопасности",
                    "Обновить правила брандмауэра",
                    "Проверить все активные соединения"
                ])
            elif network_status == NetworkStatus.SUSPICIOUS:
                recommendations.extend([
                    "Увеличить частоту мониторинга",
                    "Проверить подозрительные потоки",
                    "Обновить базу данных угроз"
                ])
            else:
                recommendations.extend([
                    "Продолжить стандартный мониторинг",
                    "Регулярно обновлять правила безопасности"
                ])

            if threat_level == ThreatSeverity.CRITICAL:
                recommendations.append("Критический уровень угроз - требуется немедленное вмешательство")
            elif threat_level == ThreatSeverity.HIGH:
                recommendations.append("Высокий уровень угроз - усилить защиту")

            return recommendations

        except Exception as e:
            self.log_activity(f"Ошибка генерации рекомендаций: {e}", "error")
            return ["Ошибка анализа - требуется ручная проверка"]

    def _network_analysis_task(self):
        """Задача анализа сети"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(self.analysis_interval)

                # Анализ накопленных данных
                self._analyze_accumulated_data()

        except Exception as e:
            self.log_activity(f"Ошибка задачи анализа сети: {e}", "error")

    def _data_cleanup_task(self):
        """Задача очистки данных"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(3600)  # Каждый час

                # Очистка старых данных
                self._cleanup_old_data()

        except Exception as e:
            self.log_activity(f"Ошибка задачи очистки данных: {e}", "error")

    def _analyze_accumulated_data(self):
        """Анализ накопленных данных"""
        try:
            # Анализ паттернов в пакетах
            if len(self.network_packets) > 100:
                self._analyze_packet_patterns()

            # Анализ потоков на аномалии
            if len(self.network_flows) > 50:
                self._analyze_flow_anomalies()

        except Exception as e:
            self.log_activity(f"Ошибка анализа накопленных данных: {e}", "error")

    def _analyze_packet_patterns(self):
        """Анализ паттернов в пакетах"""
        try:
            # Простой анализ паттернов
            recent_packets = self.network_packets[-100:]

            # Группировка по IP адресам
            ip_counts = {}
            for packet in recent_packets:
                ip_counts[packet.source_ip] = ip_counts.get(packet.source_ip, 0) + 1

            # Поиск подозрительных IP
            for ip, count in ip_counts.items():
                if count > 50:  # Более 50 пакетов за период
                    if ip not in self.network_rules["blocked_ips"]:
                        self.log_activity(f"Подозрительная активность с IP {ip}: {count} пакетов", "warning")

        except Exception as e:
            self.log_activity(f"Ошибка анализа паттернов пакетов: {e}", "error")

    def _analyze_flow_anomalies(self):
        """Анализ аномалий в потоках"""
        try:
            # Анализ аномальных потоков
            for flow in self.network_flows.values():
                if flow.threat_score > 0.5 and flow.status == NetworkStatus.NORMAL:
                    flow.status = NetworkStatus.SUSPICIOUS
                    self.log_activity(f"Поток {flow.flow_id} помечен как подозрительный", "warning")

        except Exception as e:
            self.log_activity(f"Ошибка анализа аномалий потоков: {e}", "error")

    def _cleanup_old_data(self):
        """Очистка старых данных"""
        try:
            current_time = datetime.now()

            # Очистка старых пакетов
            cutoff_packets = current_time - timedelta(hours=self.packet_retention_hours)
            self.network_packets = [
                p for p in self.network_packets
                if p.timestamp > cutoff_packets
            ]

            # Очистка старых потоков
            cutoff_flows = current_time - timedelta(hours=self.flow_retention_hours)
            flows_to_remove = [
                flow_id for flow_id, flow in self.network_flows.items()
                if flow.start_time < cutoff_flows
            ]
            for flow_id in flows_to_remove:
                del self.network_flows[flow_id]

            # Очистка старых угроз
            cutoff_threats = current_time - timedelta(hours=24)
            self.detected_threats = [
                t for t in self.detected_threats
                if t.timestamp > cutoff_threats
            ]

            self.log_activity("Очистка старых данных завершена", "info")

        except Exception as e:
            self.log_activity(f"Ошибка очистки старых данных: {e}", "error")

    def _save_network_state(self):
        """Сохранение состояния сетевой безопасности"""
        try:
            import os
            os.makedirs("/tmp/aladdin_network", exist_ok=True)

            data_to_save = {
                "threats": [threat.to_dict() for threat in self.detected_threats[-100:]],
                "flows": {k: v.to_dict() for k, v in list(self.network_flows.items())[-50:]},
                "metrics": self.network_metrics.to_dict(),
                "statistics": self.statistics,
                "network_rules": {
                    "blocked_ips": list(self.network_rules["blocked_ips"]),
                    "blocked_ports": list(self.network_rules["blocked_ports"]),
                    "allowed_protocols": list(self.network_rules["allowed_protocols"])
                },
                "saved_at": datetime.now().isoformat()
            }

            with open("/tmp/aladdin_network/last_state.json", 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            self.log_activity("Состояние сетевой безопасности сохранено", "info")
        except Exception as e:
            self.log_activity(f"Ошибка сохранения состояния сетевой безопасности: {e}", "error")
