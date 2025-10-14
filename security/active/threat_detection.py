"""
Система обнаружения угроз для семей
ALADDIN Security System - Уровень 2: Активная защита
"""
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from core.base import SecurityBase
from core.security_base import SecurityEvent, SecurityRule, IncidentSeverity


class ThreatType(Enum):
    """Типы угроз"""
    MALWARE = "malware"  # Вредоносное ПО
    PHISHING = "phishing"  # Фишинг
    SCAM = "scam"  # Мошенничество
    SOCIAL_ENGINEERING = "social_engineering"  # Социальная инженерия
    DATA_BREACH = "data_breach"  # Утечка данных
    SUSPICIOUS_ACTIVITY = "suspicious_activity"  # Подозрительная активность
    UNAUTHORIZED_ACCESS = "unauthorized_access"  # Несанкционированный доступ
    CHILD_EXPLOITATION = "child_exploitation"  # Эксплуатация детей
    ELDERLY_FRAUD = "elderly_fraud"  # Мошенничество против пожилых


class ThreatSeverity(Enum):
    """Уровни серьезности угроз"""
    LOW = "low"  # Низкий
    MEDIUM = "medium"  # Средний
    HIGH = "high"  # Высокий
    CRITICAL = "critical"  # Критический


class ThreatSource(Enum):
    """Источники угроз"""
    EMAIL = "email"  # Электронная почта
    WEBSITE = "website"  # Веб-сайт
    PHONE = "phone"  # Телефон
    SMS = "sms"  # SMS
    SOCIAL_MEDIA = "social_media"  # Социальные сети
    FILE = "file"  # Файл
    NETWORK = "network"  # Сеть
    DEVICE = "device"  # Устройство
    APPLICATION = "application"  # Приложение


class DetectionMethod(Enum):
    """Методы обнаружения"""
    SIGNATURE = "signature"  # Сигнатурный анализ
    BEHAVIORAL = "behavioral"  # Поведенческий анализ
    HEURISTIC = "heuristic"  # Эвристический анализ
    MACHINE_LEARNING = "machine_learning"  # Машинное обучение
    RULE_BASED = "rule_based"  # Правила
    PATTERN_MATCHING = "pattern_matching"  # Сопоставление паттернов


@dataclass
class ThreatIndicator:
    """Индикатор угрозы"""
    indicator_id: str
    indicator_type: str
    value: str
    confidence: float  # Уверенность в обнаружении (0.0-1.0)
    source: ThreatSource
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatDetection:
    """Обнаружение угрозы"""
    detection_id: str
    threat_type: ThreatType
    severity: ThreatSeverity
    source: ThreatSource
    detection_method: DetectionMethod
    confidence: float  # Уверенность в обнаружении (0.0-1.0)
    indicators: List[ThreatIndicator] = field(default_factory=list)
    description: str = ""
    affected_user: Optional[str] = None
    affected_device: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatPattern:
    """Паттерн угрозы"""
    pattern_id: str
    name: str
    threat_type: ThreatType
    severity: ThreatSeverity
    patterns: List[str]  # Регулярные выражения или ключевые слова
    description: str = ""
    family_specific: bool = False  # Специфично для семей
    age_group: Optional[str] = None  # Целевая возрастная группа
    metadata: Dict[str, Any] = field(default_factory=dict)


class ThreatDetectionService(SecurityBase):
    """Сервис обнаружения угроз для семей"""

    def __init__(self, name: str = "ThreatDetection", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.logger = logging.getLogger(__name__)
        # Хранилища данных
        self.threat_patterns: Dict[str, ThreatPattern] = {}
        self.detected_threats: Dict[str, ThreatDetection] = {}
        self.threat_indicators: Dict[str, ThreatIndicator] = {}
        self.family_threat_history: Dict[str, List[str]] = {}  # user_id -> threat_ids
        # Настройки обнаружения
        self.detection_thresholds = {
            ThreatSeverity.LOW: 0.3,
            ThreatSeverity.MEDIUM: 0.5,
            ThreatSeverity.HIGH: 0.7,
            ThreatSeverity.CRITICAL: 0.9
        }
        # Инициализация
        self._initialize_threat_patterns()
        self._initialize_family_protection_rules()

    def _initialize_threat_patterns(self) -> None:
        """Инициализация паттернов угроз"""
        try:
            # Паттерны для семей
            family_patterns = [
                {
                    "pattern_id": "child_online_predator",
                    "name": "Онлайн-хищник",
                    "threat_type": ThreatType.CHILD_EXPLOITATION,
                    "severity": ThreatSeverity.CRITICAL,
                    "patterns": [
                        r"встретимся\s+наедине",
                        r"не\s+говори\s+родителям",
                        r"это\s+наш\s+секрет",
                        r"пришли\s+фото",
                        r"сколько\s+тебе\s+лет"
                    ],
                    "description": "Обнаружение попыток эксплуатации детей",
                    "family_specific": True,
                    "age_group": "child"
                },
                {
                    "pattern_id": "elderly_tech_support_scam",
                    "name": "Техподдержка-мошенники",
                    "threat_type": ThreatType.ELDERLY_FRAUD,
                    "severity": ThreatSeverity.HIGH,
                    "patterns": [
                        r"ваш\s+компьютер\s+заражен",
                        r"срочно\s+установите\s+программу",
                        r"ваша\s+карта\s+заблокирована",
                        r"переведите\s+деньги\s+для\s+разблокировки",
                        r"микрософт\s+техподдержка"
                    ],
                    "description": "Обнаружение мошенничества против пожилых",
                    "family_specific": True,
                    "age_group": "elderly"
                },
                {
                    "pattern_id": "phishing_family_data",
                    "name": "Фишинг семейных данных",
                    "threat_type": ThreatType.PHISHING,
                    "severity": ThreatSeverity.HIGH,
                    "patterns": [
                        r"подтвердите\s+данные\s+ребенка",
                        r"школьные\s+документы",
                        r"медицинская\s+справка",
                        r"пенсионные\s+начисления",
                        r"семейный\s+кабинет"
                    ],
                    "description": "Фишинг семейной информации",
                    "family_specific": True
                },
                {
                    "pattern_id": "malware_download",
                    "name": "Загрузка вредоносного ПО",
                    "threat_type": ThreatType.MALWARE,
                    "severity": ThreatSeverity.HIGH,
                    "patterns": [
                        r"\.exe\s+скачать",
                        r"бесплатная\s+игра\s+скачать",
                        r"кряк\s+программы",
                        r"взлом\s+игры",
                        r"халява\s+скачать"
                    ],
                    "description": "Обнаружение попыток загрузки вредоносного ПО"
                },
                {
                    "pattern_id": "suspicious_communication",
                    "name": "Подозрительная коммуникация",
                    "threat_type": ThreatType.SUSPICIOUS_ACTIVITY,
                    "severity": ThreatSeverity.MEDIUM,
                    "patterns": [
                        r"неизвестный\s+номер",
                        r"подозрительное\s+сообщение",
                        r"неожиданная\s+ссылка",
                        r"странный\s+запрос"
                    ],
                    "description": "Обнаружение подозрительной коммуникации"
                }
            ]
            for pattern_data in family_patterns:
                pattern = ThreatPattern(
                    pattern_id=pattern_data["pattern_id"],
                    name=pattern_data["name"],
                    threat_type=ThreatType(pattern_data["threat_type"]),
                    severity=ThreatSeverity(pattern_data["severity"]),
                    patterns=pattern_data["patterns"],
                    description=pattern_data["description"],
                    family_specific=pattern_data.get("family_specific", False),
                    age_group=pattern_data.get("age_group"),
                    metadata=pattern_data.get("metadata", {})
                )
                self.threat_patterns[pattern.pattern_id] = pattern
            self.logger.info(f"Инициализировано {len(self.threat_patterns)} паттернов угроз")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации паттернов угроз: {e}")

    def _initialize_family_protection_rules(self) -> None:
        """Инициализация правил семейной защиты"""
        try:
            # Создаем правила для семейной защиты
            family_rules = [
                SecurityRule(
                    "Защита детей от онлайн-угроз", "family_protection", {
                        "age_group": "child", "threat_type": "child_exploitation"}, [
                        "block", "notify_parents", "log_incident"]), SecurityRule(
                    "Защита пожилых от мошенничества", "family_protection", {
                        "age_group": "elderly", "threat_type": "elderly_fraud"}, [
                            "block", "notify_family", "log_incident"]), SecurityRule(
                                "Защита семейных данных", "family_protection", {
                                    "threat_type": "phishing", "family_data": True}, [
                                        "block", "notify_family", "log_incident"])]
            for i, rule in enumerate(family_rules):
                self.security_rules[f"rule_{i}"] = rule
            self.logger.info(f"Инициализировано {len(family_rules)} правил семейной защиты")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации правил семейной защиты: {e}")

    def analyze_content(self, content: str, source: ThreatSource,
                        user_id: Optional[str] = None,
                        user_age: Optional[int] = None) -> List[ThreatDetection]:
        """Анализ контента на наличие угроз"""
        try:
            detections = []
            content_lower = content.lower()
            for pattern in self.threat_patterns.values():
                # Проверяем соответствие возрастной группе
                if pattern.age_group and user_age:
                    if pattern.age_group == "child" and user_age >= 18:
                        continue
                    elif pattern.age_group == "elderly" and user_age < 65:
                        continue
                # Проверяем паттерны
                matches = []
                for pattern_regex in pattern.patterns:
                    if re.search(pattern_regex, content_lower, re.IGNORECASE):
                        matches.append(pattern_regex)
                if matches:
                    # Рассчитываем уверенность
                    confidence = min(len(matches) / len(pattern.patterns) + 0.3, 1.0)
                    # Создаем индикатор угрозы
                    indicator = ThreatIndicator(
                        indicator_id=f"ind_{len(self.threat_indicators) + 1}",
                        indicator_type="pattern_match",
                        value=f"Найдено {len(matches)} совпадений",
                        confidence=confidence,
                        source=source,
                        metadata={"matched_patterns": matches}
                    )
                    self.threat_indicators[indicator.indicator_id] = indicator
                    # Создаем обнаружение угрозы
                    detection = ThreatDetection(
                        detection_id=f"threat_{len(self.detected_threats) + 1}",
                        threat_type=pattern.threat_type,
                        severity=pattern.severity,
                        source=source,
                        detection_method=DetectionMethod.PATTERN_MATCHING,
                        confidence=confidence,
                        indicators=[indicator],
                        description=f"Обнаружена угроза: {pattern.name}",
                        affected_user=user_id,
                        metadata={
                            "pattern_id": pattern.pattern_id,
                            "matched_patterns": matches,
                            "content_preview": content[:100] + "..." if len(content) > 100 else content
                        }
                    )
                    self.detected_threats[detection.detection_id] = detection
                    detections.append(detection)
                    # Добавляем в историю пользователя
                    if user_id:
                        if user_id not in self.family_threat_history:
                            self.family_threat_history[user_id] = []
                        self.family_threat_history[user_id].append(detection.detection_id)
                    # Создаем событие безопасности
                    security_event = SecurityEvent(
                        event_type="threat_detected",
                        severity=self._map_threat_severity_to_incident(pattern.severity),
                        description=f"Обнаружена угроза: {pattern.name}",
                        source="ThreatDetection"
                    )
                    security_event.metadata = {
                        "detection_id": detection.detection_id,
                        "threat_type": pattern.threat_type.value,
                        "severity": pattern.severity.value,
                        "confidence": confidence,
                        "user_id": user_id,
                        "user_age": user_age
                    }
                    # Добавляем событие безопасности в журнал
                    self.add_security_event(
                        event_type="threat_detected",
                        severity=pattern.severity.value,
                        description=f"Обнаружена угроза: {pattern.name}",
                        source="ThreatDetection",
                        metadata={
                            "detection_id": detection.detection_id,
                            "threat_type": pattern.threat_type.value,
                            "severity": pattern.severity.value,
                            "confidence": confidence,
                            "user_id": user_id,
                            "user_age": user_age
                        }
                    )
            return detections
        except Exception as e:
            self.logger.error(f"Ошибка анализа контента: {e}")
            return []

    def _map_threat_severity_to_incident(self, severity: ThreatSeverity) -> IncidentSeverity:
        """Маппинг серьезности угрозы в серьезность инцидента"""
        mapping = {
            ThreatSeverity.LOW: IncidentSeverity.LOW,
            ThreatSeverity.MEDIUM: IncidentSeverity.MEDIUM,
            ThreatSeverity.HIGH: IncidentSeverity.HIGH,
            ThreatSeverity.CRITICAL: IncidentSeverity.CRITICAL
        }
        return mapping.get(severity, IncidentSeverity.MEDIUM)

    def analyze_file(self, file_path: str, file_hash: str,
                     user_id: Optional[str] = None) -> List[ThreatDetection]:
        """Анализ файла на наличие угроз"""
        try:
            detections = []
            # Проверяем хеш файла в базе известных угроз
            if self._is_known_malware_hash(file_hash):
                detection = ThreatDetection(
                    detection_id=f"malware_{len(self.detected_threats) + 1}",
                    threat_type=ThreatType.MALWARE,
                    severity=ThreatSeverity.CRITICAL,
                    source=ThreatSource.FILE,
                    detection_method=DetectionMethod.SIGNATURE,
                    confidence=0.95,
                    description=f"Обнаружен известный вредоносный файл: {file_path}",
                    affected_user=user_id,
                    metadata={"file_path": file_path, "file_hash": file_hash}
                )
                self.detected_threats[detection.detection_id] = detection
                detections.append(detection)
            # Проверяем подозрительные расширения файлов
            suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
            file_extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
            if f'.{file_extension}' in suspicious_extensions:
                detection = ThreatDetection(
                    detection_id=f"suspicious_file_{len(self.detected_threats) + 1}",
                    threat_type=ThreatType.SUSPICIOUS_ACTIVITY,
                    severity=ThreatSeverity.MEDIUM,
                    source=ThreatSource.FILE,
                    detection_method=DetectionMethod.HEURISTIC,
                    confidence=0.6,
                    description=f"Подозрительный тип файла: {file_path}",
                    affected_user=user_id,
                    metadata={"file_path": file_path, "extension": file_extension}
                )
                self.detected_threats[detection.detection_id] = detection
                detections.append(detection)
            return detections
        except Exception as e:
            self.logger.error(f"Ошибка анализа файла: {e}")
            return []

    def _is_known_malware_hash(self, file_hash: str) -> bool:
        """Проверка хеша файла на известные вредоносные программы"""
        # В реальной системе здесь была бы база данных известных хешей
        known_malware_hashes = {
            "d41d8cd98f00b204e9800998ecf8427e",  # Пример хеша
            "5d41402abc4b2a76b9719d911017c592",  # Пример хеша
        }
        return file_hash.lower() in known_malware_hashes

    def analyze_network_activity(self, source_ip: str, destination_ip: str,
                                 port: int, protocol: str,
                                 user_id: Optional[str] = None) -> List[ThreatDetection]:
        """Анализ сетевой активности на наличие угроз"""
        try:
            detections = []
            # Проверяем подозрительные IP-адреса
            if self._is_suspicious_ip(source_ip) or self._is_suspicious_ip(destination_ip):
                detection = ThreatDetection(
                    detection_id=f"network_threat_{len(self.detected_threats) + 1}",
                    threat_type=ThreatType.SUSPICIOUS_ACTIVITY,
                    severity=ThreatSeverity.HIGH,
                    source=ThreatSource.NETWORK,
                    detection_method=DetectionMethod.SIGNATURE,
                    confidence=0.8,
                    description=f"Подозрительная сетевая активность: {source_ip} -> {destination_ip}",
                    affected_user=user_id,
                    metadata={
                        "source_ip": source_ip,
                        "destination_ip": destination_ip,
                        "port": port,
                        "protocol": protocol
                    }
                )
                self.detected_threats[detection.detection_id] = detection
                detections.append(detection)
            # Проверяем подозрительные порты
            suspicious_ports = [22, 23, 135, 139, 445, 1433, 3389]  # SSH, Telnet, RDP и др.
            if port in suspicious_ports:
                detection = ThreatDetection(
                    detection_id=f"suspicious_port_{len(self.detected_threats) + 1}",
                    threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                    severity=ThreatSeverity.MEDIUM,
                    source=ThreatSource.NETWORK,
                    detection_method=DetectionMethod.RULE_BASED,
                    confidence=0.6,
                    description=f"Подозрительный порт: {port}",
                    affected_user=user_id,
                    metadata={"port": port, "protocol": protocol}
                )
                self.detected_threats[detection.detection_id] = detection
                detections.append(detection)
            return detections
        except Exception as e:
            self.logger.error(f"Ошибка анализа сетевой активности: {e}")
            return []

    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Проверка IP-адреса на подозрительность"""
        # В реальной системе здесь была бы база данных подозрительных IP
        suspicious_ips = [
            "192.168.1.100",  # Пример подозрительного IP
            "10.0.0.1",       # Пример подозрительного IP
        ]
        return ip_address in suspicious_ips

    def get_threat_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Получение сводки по угрозам"""
        try:
            if user_id:
                # Угрозы для конкретного пользователя
                user_threats = [
                    threat for threat in self.detected_threats.values()
                    if threat.affected_user == user_id
                ]
            else:
                # Все угрозы
                user_threats = list(self.detected_threats.values())
            # Статистика по типам угроз
            threat_type_stats = {}
            for threat in user_threats:
                threat_type = threat.threat_type.value
                if threat_type not in threat_type_stats:
                    threat_type_stats[threat_type] = 0
                threat_type_stats[threat_type] += 1
            # Статистика по серьезности
            severity_stats = {}
            for threat in user_threats:
                severity = threat.severity.value
                if severity not in severity_stats:
                    severity_stats[severity] = 0
                severity_stats[severity] += 1
            # Статистика по источникам
            source_stats = {}
            for threat in user_threats:
                source = threat.source.value
                if source not in source_stats:
                    source_stats[source] = 0
                source_stats[source] += 1
            return {
                "total_threats": len(user_threats),
                "threats_by_type": threat_type_stats,
                "threats_by_severity": severity_stats,
                "threats_by_source": source_stats,
                "recent_threats": [
                    {
                        "detection_id": threat.detection_id,
                        "threat_type": threat.threat_type.value,
                        "severity": threat.severity.value,
                        "confidence": threat.confidence,
                        "timestamp": threat.timestamp.isoformat(),
                        "description": threat.description
                    }
                    for threat in sorted(user_threats, key=lambda x: x.timestamp, reverse=True)[:10]
                ]
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения сводки по угрозам: {e}")
            return {}

    def get_family_protection_status(self) -> Dict[str, Any]:
        """Получение статуса семейной защиты"""
        try:
            # Статистика по семейным угрозам
            family_threats = [
                threat for threat in self.detected_threats.values()
                if threat.threat_type in [ThreatType.CHILD_EXPLOITATION, ThreatType.ELDERLY_FRAUD]
            ]
            # Статистика по возрастным группам
            age_group_stats = {}
            for user_id, threat_ids in self.family_threat_history.items():
                user_threats = [
                    self.detected_threats[threat_id] for threat_id in threat_ids
                    if threat_id in self.detected_threats
                ]
                # Определяем возрастную группу по типу угроз
                for threat in user_threats:
                    if threat.threat_type == ThreatType.CHILD_EXPLOITATION:
                        age_group = "child"
                    elif threat.threat_type == ThreatType.ELDERLY_FRAUD:
                        age_group = "elderly"
                    else:
                        age_group = "adult"
                    if age_group not in age_group_stats:
                        age_group_stats[age_group] = 0
                    age_group_stats[age_group] += 1
            return {
                "family_protection_active": True,
                "total_family_threats": len(family_threats),
                "threats_by_age_group": age_group_stats,
                "active_patterns": len(self.threat_patterns),
                "protection_rules": len(self.security_rules),
                "last_scan": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса семейной защиты: {e}")
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы обнаружения угроз"""
        try:
            return {
                "service_name": self.name,
                "status": "active",
                "total_threats_detected": len(self.detected_threats),
                "active_patterns": len(self.threat_patterns),
                "protection_rules": len(self.security_rules),
                "family_protection": self.get_family_protection_status(),
                "threat_summary": self.get_threat_summary(),
                "last_activity": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}
