#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ThreatIntelligenceAgent - Агент разведки угроз ALADDIN
Обеспечивает сбор, анализ и прогнозирование угроз из внешних источников
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime
from enum import Enum


# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from core.base import SecurityBase
except ImportError:
    # Fallback для тестирования
    class SecurityBase:
        def __init__(self, name):
            self.name = name
            self.logs = []

        def log_activity(self, message, level="info"):
            self.logs.append("{}: {}".format(level.upper(), message))
            print("{}: {}".format(level.upper(), message))


class ThreatType(Enum):
    """Типы угроз"""

    MALWARE = "malware"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    APT = "apt"
    BOTNET = "botnet"
    DDOS = "ddos"
    VULNERABILITY = "vulnerability"
    EXPLOIT = "exploit"
    SOCIAL_ENGINEERING = "social_engineering"
    INSIDER_THREAT = "insider_threat"


class ThreatSeverity(Enum):
    """Уровни серьезности угроз"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class IOCType(Enum):
    """Типы индикаторов компрометации"""

    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    EMAIL = "email"
    FILE_HASH = "file_hash"
    REGISTRY_KEY = "registry_key"
    MUTEX = "mutex"
    CERTIFICATE = "certificate"
    USER_AGENT = "user_agent"
    JA3_FINGERPRINT = "ja3_fingerprint"


class ThreatSource(Enum):
    """Источники угроз"""

    OPEN_SOURCE = "open_source"
    COMMERCIAL = "commercial"
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    COMMUNITY = "community"
    INTERNAL = "internal"
    PARTNER = "partner"
    VENDOR = "vendor"


class ThreatIntelligence:
    """Класс для хранения разведывательных данных о угрозах"""

    def __init__(self, threat_id, title, description, threat_type, severity):
        self.threat_id = threat_id
        self.title = title
        self.description = description
        self.threat_type = threat_type
        self.severity = severity
        self.iocs = []
        self.tags = []
        self.source = None
        self.confidence = 0.0
        self.first_seen = None
        self.last_seen = None
        self.affected_systems = []
        self.attack_vectors = []
        self.mitigation_actions = []
        self.references = []
        self.raw_data = {}

    def add_ioc(self, ioc_type, value, description=""):
        """Добавление индикатора компрометации
        
        Args:
            ioc_type (IOCType): Тип индикатора компрометации
            value (str): Значение индикатора
            description (str): Описание индикатора
            
        Raises:
            ValueError: Если параметры некорректны
        """
        if not isinstance(ioc_type, IOCType):
            raise ValueError("ioc_type должен быть экземпляром IOCType")
        
        if not isinstance(value, str) or not value.strip():
            raise ValueError("value должен быть непустой строкой")
            
        if not isinstance(description, str):
            raise ValueError("description должен быть строкой")

        self.iocs.append(
            {
                "type": ioc_type,
                "value": value.strip(),
                "description": description.strip(),
                "added_at": datetime.now(),
            }
        )

    def add_tag(self, tag):
        """Добавление тега
        
        Args:
            tag (str): Тег для добавления
            
        Raises:
            ValueError: Если тег некорректен
        """
        if not isinstance(tag, str) or not tag.strip():
            raise ValueError("tag должен быть непустой строкой")
            
        tag = tag.strip()
        if tag not in self.tags:
            self.tags.append(tag)

    def set_source(self, source, reliability=0.5):
        """Установка источника угрозы
        
        Args:
            source (ThreatSource): Источник угрозы
            reliability (float): Надежность источника (0.0-1.0)
            
        Raises:
            ValueError: Если параметры некорректны
        """
        if not isinstance(source, ThreatSource):
            raise ValueError("source должен быть экземпляром ThreatSource")
            
        if not isinstance(reliability, (int, float)) or not (0.0 <= reliability <= 1.0):
            raise ValueError("reliability должен быть числом от 0.0 до 1.0")
            
        self.source = {
            "name": source,
            "reliability": float(reliability),
            "added_at": datetime.now(),
        }

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "threat_id": self.threat_id,
            "title": self.title,
            "description": self.description,
            "threat_type": (
                self.threat_type.value
                if hasattr(self.threat_type, "value")
                else str(self.threat_type)
            ),
            "severity": (
                self.severity.value
                if hasattr(self.severity, "value")
                else str(self.severity)
            ),
            "iocs": self.iocs,
            "tags": self.tags,
            "source": self.source,
            "confidence": self.confidence,
            "first_seen": (
                self.first_seen.isoformat() if self.first_seen else None
            ),
            "last_seen": (
                self.last_seen.isoformat() if self.last_seen else None
            ),
            "affected_systems": self.affected_systems,
            "attack_vectors": self.attack_vectors,
            "mitigation_actions": self.mitigation_actions,
            "references": self.references,
            "raw_data": self.raw_data,
        }


class ThreatIntelligenceMetrics:
    """Метрики агента разведки угроз"""

    def __init__(self):
        # Общие метрики
        self.total_threats_collected = 0
        self.threats_by_type = {}
        self.threats_by_severity = {}
        self.threats_by_source = {}

        # Метрики IOCs
        self.total_iocs_collected = 0
        self.iocs_by_type = {}
        self.unique_iocs = 0
        self.duplicate_iocs = 0

        # Метрики источников
        self.active_sources = 0
        self.reliable_sources = 0
        self.source_uptime = {}
        self.source_errors = {}

        # Метрики производительности
        self.collection_speed = 0.0  # угроз в минуту
        self.processing_time = 0.0  # среднее время обработки
        self.api_calls_made = 0
        self.api_errors = 0
        self.data_quality_score = 0.0

        # Метрики точности
        self.threat_accuracy = 0.0
        self.ioc_accuracy = 0.0
        self.false_positive_rate = 0.0
        self.true_positive_rate = 0.0

        # Временные метрики
        self.last_collection_time = None
        self.collection_duration = 0.0
        self.last_update_time = None
        self.update_frequency = 0.0

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "total_threats_collected": self.total_threats_collected,
            "threats_by_type": self.threats_by_type,
            "threats_by_severity": self.threats_by_severity,
            "threats_by_source": self.threats_by_source,
            "total_iocs_collected": self.total_iocs_collected,
            "iocs_by_type": self.iocs_by_type,
            "unique_iocs": self.unique_iocs,
            "duplicate_iocs": self.duplicate_iocs,
            "active_sources": self.active_sources,
            "reliable_sources": self.reliable_sources,
            "source_uptime": self.source_uptime,
            "source_errors": self.source_errors,
            "collection_speed": self.collection_speed,
            "processing_time": self.processing_time,
            "api_calls_made": self.api_calls_made,
            "api_errors": self.api_errors,
            "data_quality_score": self.data_quality_score,
            "threat_accuracy": self.threat_accuracy,
            "ioc_accuracy": self.ioc_accuracy,
            "false_positive_rate": self.false_positive_rate,
            "true_positive_rate": self.true_positive_rate,
            "last_collection_time": (
                self.last_collection_time.isoformat()
                if self.last_collection_time
                else None
            ),
            "collection_duration": self.collection_duration,
            "last_update_time": (
                self.last_update_time.isoformat()
                if self.last_update_time
                else None
            ),
            "update_frequency": self.update_frequency,
        }


class ThreatIntelligenceAgent(SecurityBase):
    """Агент разведки угроз ALADDIN"""

    def __init__(self, name="ThreatIntelligenceAgent"):
        SecurityBase.__init__(self, name)

        # Конфигурация агента
        self.collection_interval = 300  # 5 минут
        self.update_interval = 3600  # 1 час
        self.retention_days = 90  # 90 дней
        self.max_threats_per_collection = 1000
        self.max_iocs_per_threat = 100

        # Хранилища данных
        self.threats = {}  # threat_id -> ThreatIntelligence
        self.iocs = {}  # ioc_value -> IOC data
        self.sources = {}  # source_name -> source_config
        self.threat_sources = {}  # source_name -> threat_source_data
        self.metrics = ThreatIntelligenceMetrics()

        # AI модели для анализа
        self.ml_models = {}
        self.threat_classifier = None
        self.ioc_analyzer = None
        self.severity_predictor = None
        self.source_reliability_analyzer = None
        self.trend_analyzer = None

        # Базы данных угроз
        self.threat_feeds = {}
        self.ioc_databases = {}
        self.vulnerability_feeds = {}
        self.malware_feeds = {}

        # Настройки API
        self.api_keys = {}
        self.rate_limits = {}
        self.timeout_settings = {}

        # Системы валидации
        self.whitelist_system = {}
        self.blacklist_system = {}
        self.confidence_scoring = {}
        self.quality_control = {}

    def initialize(self):
        """Инициализация агента"""
        try:
            self.log_activity("Инициализация ThreatIntelligenceAgent...")

            # Инициализация AI моделей
            self._initialize_ai_models()

            # Загрузка конфигурации источников
            self._load_threat_sources()

            # Инициализация баз данных
            self._initialize_databases()

            # Запуск фоновых процессов
            self._start_background_processes()

            self.log_activity(
                "ThreatIntelligenceAgent инициализирован успешно"
            )
            return True

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации ThreatIntelligenceAgent: {}".format(
                    str(e)
                ),
                "error",
            )
            return False

    def _initialize_ai_models(self):
        """Инициализация AI моделей"""
        try:
            self.log_activity("Инициализация AI моделей для разведки угроз...")

            # Классификатор угроз
            self.threat_classifier = {
                "model_type": "deep_learning_ensemble",
                "features": [
                    "threat_description",
                    "ioc_patterns",
                    "source_reliability",
                    "temporal_features",
                    "severity_indicators",
                    "attack_vectors",
                ],
                "accuracy": 0.95,
                "confidence_threshold": 0.85,
                "last_trained": datetime.now(),
            }

            # Анализатор IOCs
            self.ioc_analyzer = {
                "model_type": "neural_network",
                "features": [
                    "ioc_type",
                    "ioc_value",
                    "context",
                    "reputation",
                    "temporal_patterns",
                    "geographic_data",
                    "network_analysis",
                ],
                "accuracy": 0.92,
                "confidence_threshold": 0.80,
                "last_trained": datetime.now(),
            }

            # Предиктор серьезности
            self.severity_predictor = {
                "model_type": "gradient_boosting",
                "features": [
                    "threat_type",
                    "ioc_count",
                    "source_reliability",
                    "affected_systems",
                    "attack_complexity",
                    "impact_potential",
                ],
                "accuracy": 0.88,
                "confidence_threshold": 0.75,
                "last_trained": datetime.now(),
            }

            # Анализатор надежности источников
            self.source_reliability_analyzer = {
                "model_type": "random_forest",
                "features": [
                    "historical_accuracy",
                    "data_freshness",
                    "coverage",
                    "false_positive_rate",
                    "update_frequency",
                    "peer_validation",
                ],
                "accuracy": 0.90,
                "confidence_threshold": 0.80,
                "last_trained": datetime.now(),
            }

            # Анализатор трендов
            self.trend_analyzer = {
                "model_type": "time_series_lstm",
                "features": [
                    "threat_frequency",
                    "severity_trends",
                    "geographic_distribution",
                    "attack_evolution",
                    "seasonal_patterns",
                    "emerging_threats",
                ],
                "accuracy": 0.87,
                "confidence_threshold": 0.70,
                "last_trained": datetime.now(),
            }

            self.ml_models = {
                "threat_classifier": self.threat_classifier,
                "ioc_analyzer": self.ioc_analyzer,
                "severity_predictor": self.severity_predictor,
                "source_reliability_analyzer": (
                    self.source_reliability_analyzer
                ),
                "trend_analyzer": self.trend_analyzer,
            }

            self.log_activity("AI модели инициализированы успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации AI моделей: {}".format(str(e)), "error"
            )

    def _load_threat_sources(self):
        """Загрузка конфигурации источников угроз"""
        try:
            self.log_activity("Загрузка источников угроз...")

            # Открытые источники
            self.sources["open_source"] = {
                "name": "Open Source Intelligence",
                "type": "open_source",
                "urls": [
                    "https://feeds.feedburner.com/Threatpost",
                    "https://krebsonsecurity.com/feed/",
                    "https://www.bleepingcomputer.com/feed/",
                ],
                "update_interval": 3600,  # 1 час
                "reliability": 0.7,
                "active": True,
            }

            # Коммерческие источники
            self.sources["commercial"] = {
                "name": "Commercial Threat Intelligence",
                "type": "commercial",
                "api_endpoints": [
                    "https://api.threatintel.com/v1/threats",
                    "https://api.securityfeeds.com/v2/iocs",
                ],
                "update_interval": 1800,  # 30 минут
                "reliability": 0.9,
                "active": True,
            }

            # Правительственные источники
            self.sources["government"] = {
                "name": "Government Threat Intelligence",
                "type": "government",
                "urls": [
                    "https://www.cisa.gov/feeds",
                    "https://www.ncsc.gov.uk/feeds",
                ],
                "update_interval": 7200,  # 2 часа
                "reliability": 0.95,
                "active": True,
            }

            # Академические источники
            self.sources["academic"] = {
                "name": "Academic Research",
                "type": "academic",
                "urls": ["https://research.university.edu/cyberthreats/feed"],
                "update_interval": 86400,  # 24 часа
                "reliability": 0.8,
                "active": True,
            }

            self.log_activity("Источники угроз загружены успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка загрузки источников угроз: {}".format(str(e)), "error"
            )

    def _initialize_databases(self):
        """Инициализация баз данных"""
        try:
            self.log_activity("Инициализация баз данных угроз...")

            # Инициализация баз данных угроз
            self.threat_feeds = {
                "malware": set(),
                "phishing": set(),
                "ransomware": set(),
                "apt": set(),
                "vulnerability": set(),
            }

            self.ioc_databases = {
                "ip_addresses": set(),
                "domains": set(),
                "urls": set(),
                "file_hashes": set(),
                "email_addresses": set(),
            }

            self.vulnerability_feeds = {
                "cve": {},
                "exploit_db": {},
                "security_advisories": {},
            }

            self.malware_feeds = {
                "signatures": set(),
                "families": set(),
                "behavioral_patterns": set(),
            }

            self.log_activity("Базы данных инициализированы успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации баз данных: {}".format(str(e)), "error"
            )

    def _start_background_processes(self):
        """Запуск фоновых процессов"""
        try:
            self.log_activity("Запуск фоновых процессов...")

            # Здесь будут запущены фоновые процессы
            # В реальной реализации это будут отдельные потоки

            self.log_activity("Фоновые процессы запущены")

        except Exception as e:
            self.log_activity(
                "Ошибка запуска фоновых процессов: {}".format(str(e)), "error"
            )

    def collect_threats(self):
        """Сбор угроз из всех источников"""
        try:
            self.log_activity("Начало сбора угроз...")
            start_time = time.time()

            collected_threats = 0

            for source_name, source_config in self.sources.items():
                if source_config.get("active", False):
                    threats = self._collect_from_source(
                        source_name, source_config
                    )
                    collected_threats += len(threats)

                    # Обновление метрик
                    self.metrics.api_calls_made += 1
                    if source_name not in self.metrics.source_errors:
                        self.metrics.source_errors[source_name] = 0

            # Обновление метрик
            self.metrics.total_threats_collected += collected_threats
            self.metrics.last_collection_time = datetime.now()
            self.metrics.collection_duration = time.time() - start_time
            self.metrics.collection_speed = (
                collected_threats / (self.metrics.collection_duration / 60)
                if self.metrics.collection_duration > 0
                else 0
            )

            self.log_activity(
                "Сбор угроз завершен. Собрано: {}".format(collected_threats)
            )
            return collected_threats

        except Exception as e:
            self.log_activity("Ошибка сбора угроз: {}".format(str(e)), "error")
            return 0

    def _collect_from_source(self, source_name, source_config):
        """Сбор угроз из конкретного источника"""
        try:
            threats = []

            if source_config["type"] == "open_source":
                threats = self._collect_from_rss_feeds(source_config)
            elif source_config["type"] == "commercial":
                threats = self._collect_from_api(source_config)
            elif source_config["type"] == "government":
                threats = self._collect_from_government_feeds(source_config)
            elif source_config["type"] == "academic":
                threats = self._collect_from_academic_sources(source_config)

            return threats

        except Exception as e:
            self.log_activity(
                "Ошибка сбора из источника {}: {}".format(source_name, str(e)),
                "error",
            )
            return []

    def _collect_from_rss_feeds(self, source_config):
        """Сбор угроз из RSS лент"""
        try:
            threats = []

            # Симуляция сбора из RSS лент
            for i in range(5):  # Симулируем 5 угроз
                threat = ThreatIntelligence(
                    threat_id="rss_threat_{}_{}".format(int(time.time()), i),
                    title="RSS Threat {}".format(i),
                    description="Threat collected from RSS feed",
                    threat_type=ThreatType.MALWARE,
                    severity=ThreatSeverity.MEDIUM,
                )

                threat.set_source("RSS Feed", 0.7)
                threat.add_ioc(IOCType.IP_ADDRESS, "192.168.1.{}".format(i))
                threat.add_tag("rss_collected")

                threats.append(threat)
                self.threats[threat.threat_id] = threat

            return threats

        except Exception as e:
            self.log_activity(
                "Ошибка сбора из RSS лент: {}".format(str(e)), "error"
            )
            return []

    def _collect_from_api(self, source_config):
        """Сбор угроз из API"""
        try:
            threats = []

            # Симуляция сбора из API
            for i in range(3):  # Симулируем 3 угрозы
                threat = ThreatIntelligence(
                    threat_id="api_threat_{}_{}".format(int(time.time()), i),
                    title="API Threat {}".format(i),
                    description="Threat collected from commercial API",
                    threat_type=ThreatType.APT,
                    severity=ThreatSeverity.HIGH,
                )

                threat.set_source("Commercial API", 0.9)
                threat.add_ioc(IOCType.DOMAIN, "malicious{}.com".format(i))
                threat.add_ioc(
                    IOCType.FILE_HASH,
                    hashlib.md5("malware_{}".format(i).encode()).hexdigest(),
                )
                threat.add_tag("api_collected")

                threats.append(threat)
                self.threats[threat.threat_id] = threat

            return threats

        except Exception as e:
            self.log_activity(
                "Ошибка сбора из API: {}".format(str(e)), "error"
            )
            return []

    def _collect_from_government_feeds(self, source_config):
        """Сбор угроз из правительственных источников"""
        try:
            threats = []

            # Симуляция сбора из правительственных источников
            for i in range(2):  # Симулируем 2 угрозы
                threat = ThreatIntelligence(
                    threat_id="gov_threat_{}_{}".format(int(time.time()), i),
                    title="Government Threat {}".format(i),
                    description="Threat collected from government source",
                    threat_type=ThreatType.VULNERABILITY,
                    severity=ThreatSeverity.CRITICAL,
                )

                threat.set_source("Government Feed", 0.95)
                threat.add_ioc(IOCType.IP_ADDRESS, "10.0.0.{}".format(i))
                threat.add_tag("government_collected")

                threats.append(threat)
                self.threats[threat.threat_id] = threat

            return threats

        except Exception as e:
            self.log_activity(
                "Ошибка сбора из правительственных источников: {}".format(
                    str(e)
                ),
                "error",
            )
            return []

    def _collect_from_academic_sources(self, source_config):
        """Сбор угроз из академических источников"""
        try:
            threats = []

            # Симуляция сбора из академических источников
            for i in range(1):  # Симулируем 1 угрозу
                threat = ThreatIntelligence(
                    threat_id="academic_threat_{}_{}".format(
                        int(time.time()), i
                    ),
                    title="Academic Threat {}".format(i),
                    description="Threat collected from academic research",
                    threat_type=ThreatType.SOCIAL_ENGINEERING,
                    severity=ThreatSeverity.MEDIUM,
                )

                threat.set_source("Academic Research", 0.8)
                threat.add_ioc(IOCType.EMAIL, "phishing{}.edu".format(i))
                threat.add_tag("academic_collected")

                threats.append(threat)
                self.threats[threat.threat_id] = threat

            return threats

        except Exception as e:
            self.log_activity(
                "Ошибка сбора из академических источников: {}".format(str(e)),
                "error",
            )
            return []

    def analyze_threats(self):
        """Анализ собранных угроз"""
        try:
            self.log_activity("Начало анализа угроз...")
            start_time = time.time()

            analyzed_count = 0

            for threat_id, threat in self.threats.items():
                # Анализ угрозы
                self._analyze_single_threat(threat)
                analyzed_count += 1

            # Обновление метрик
            self.metrics.processing_time = time.time() - start_time
            self.metrics.data_quality_score = self._calculate_data_quality()

            self.log_activity(
                "Анализ угроз завершен. Проанализировано: {}".format(
                    analyzed_count
                )
            )
            return analyzed_count

        except Exception as e:
            self.log_activity(
                "Ошибка анализа угроз: {}".format(str(e)), "error"
            )
            return 0

    def _analyze_single_threat(self, threat):
        """Анализ отдельной угрозы"""
        try:
            # Классификация угрозы
            threat_classification = self._classify_threat(threat)
            threat.threat_type = threat_classification.get(
                "type", threat.threat_type
            )

            # Предсказание серьезности
            predicted_severity = self._predict_severity(threat)
            threat.severity = predicted_severity.get(
                "severity", threat.severity
            )

            # Анализ IOCs
            ioc_analysis = self._analyze_iocs(threat)
            threat.confidence = ioc_analysis.get(
                "confidence", threat.confidence
            )

            # Обновление временных меток
            if not threat.first_seen:
                threat.first_seen = datetime.now()
            threat.last_seen = datetime.now()

        except Exception as e:
            self.log_activity(
                "Ошибка анализа угрозы {}: {}".format(
                    threat.threat_id, str(e)
                ),
                "error",
            )

    def _classify_threat(self, threat):
        """Классификация угрозы"""
        try:
            # Симуляция классификации угрозы
            classification_score = 0.85

            return {
                "type": threat.threat_type,
                "confidence": classification_score,
                "model_used": "threat_classifier",
            }

        except Exception as e:
            self.log_activity(
                "Ошибка классификации угрозы: {}".format(str(e)), "error"
            )
            return {"type": threat.threat_type, "confidence": 0.5}

    def _predict_severity(self, threat):
        """Предсказание серьезности угрозы"""
        try:
            # Симуляция предсказания серьезности
            severity_score = 0.8

            return {
                "severity": threat.severity,
                "confidence": severity_score,
                "model_used": "severity_predictor",
            }

        except Exception as e:
            self.log_activity(
                "Ошибка предсказания серьезности: {}".format(str(e)), "error"
            )
            return {"severity": threat.severity, "confidence": 0.5}

    def _analyze_iocs(self, threat):
        """Анализ индикаторов компрометации"""
        try:
            # Симуляция анализа IOCs
            ioc_confidence = 0.9

            return {
                "confidence": ioc_confidence,
                "ioc_count": len(threat.iocs),
                "model_used": "ioc_analyzer",
            }

        except Exception as e:
            self.log_activity(
                "Ошибка анализа IOCs: {}".format(str(e)), "error"
            )
            return {"confidence": 0.5, "ioc_count": 0}

    def _calculate_data_quality(self):
        """Расчет качества данных"""
        try:
            if not self.threats:
                return 0.0

            quality_factors = []

            for threat in self.threats.values():
                threat_quality = 0.0

                # Качество описания
                if threat.description and len(threat.description) > 50:
                    threat_quality += 0.2

                # Наличие IOCs
                if threat.iocs:
                    threat_quality += 0.3

                # Наличие источника
                if threat.source:
                    threat_quality += 0.2

                # Наличие тегов
                if threat.tags:
                    threat_quality += 0.1

                # Уровень уверенности
                threat_quality += threat.confidence * 0.2

                quality_factors.append(threat_quality)

            return (
                sum(quality_factors) / len(quality_factors)
                if quality_factors
                else 0.0
            )

        except Exception as e:
            self.log_activity(
                "Ошибка расчета качества данных: {}".format(str(e)), "error"
            )
            return 0.0

    def generate_report(self):
        """Генерация отчета о разведке угроз"""
        try:
            self.log_activity("Генерация отчета о разведке угроз...")

            report = {
                "report_id": "threat_intel_{}".format(int(time.time())),
                "generated_at": datetime.now().isoformat(),
                "agent_name": self.name,
                "summary": {
                    "total_threats": len(self.threats),
                    "threats_by_type": self._get_threats_by_type(),
                    "threats_by_severity": self._get_threats_by_severity(),
                    "total_iocs": sum(
                        len(threat.iocs) for threat in self.threats.values()
                    ),
                    "data_quality_score": self.metrics.data_quality_score,
                },
                "threats": [
                    threat.to_dict() for threat in self.threats.values()
                ],
                "metrics": self.metrics.to_dict(),
                "recommendations": self._generate_recommendations(),
            }

            # Сохранение отчета
            report_dir = "data/threat_intelligence_reports"
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            report_file = os.path.join(
                report_dir,
                "threat_intel_report_{}.json".format(int(time.time())),
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.log_activity("Отчет сохранен: {}".format(report_file))
            return report

        except Exception as e:
            self.log_activity(
                "Ошибка генерации отчета: {}".format(str(e)), "error"
            )
            # Возвращаем базовый отчет даже при ошибке
            return {
                "report_id": "threat_intel_error_{}".format(int(time.time())),
                "generated_at": datetime.now().isoformat(),
                "agent_name": self.name,
                "error": str(e),
                "summary": {"total_threats": 0, "error": True},
                "threats": [],
                "metrics": {},
                "recommendations": []
            }

    def _get_threats_by_type(self):
        """Получение угроз по типам"""
        try:
            threats_by_type = {}
            for threat in self.threats.values():
                threat_type = (
                    threat.threat_type.value
                    if hasattr(threat.threat_type, "value")
                    else str(threat.threat_type)
                )
                threats_by_type[threat_type] = (
                    threats_by_type.get(threat_type, 0) + 1
                )
            return threats_by_type
        except Exception as e:
            self.log_activity(
                "Ошибка получения угроз по типам: {}".format(str(e)), "error"
            )
            return {}

    def _get_threats_by_severity(self):
        """Получение угроз по серьезности"""
        try:
            threats_by_severity = {}
            for threat in self.threats.values():
                severity = (
                    threat.severity.value
                    if hasattr(threat.severity, "value")
                    else str(threat.severity)
                )
                threats_by_severity[severity] = (
                    threats_by_severity.get(severity, 0) + 1
                )
            return threats_by_severity
        except Exception as e:
            self.log_activity(
                "Ошибка получения угроз по серьезности: {}".format(str(e)),
                "error",
            )
            return {}

    def _generate_recommendations(self):
        """Генерация рекомендаций"""
        try:
            recommendations = []

            # Рекомендации на основе анализа угроз
            if len(self.threats) > 0:
                recommendations.append(
                    {
                        "type": "threat_response",
                        "priority": "high",
                        "description": (
                            "Обнаружены новые угрозы, рекомендуется обновить "
                            "системы защиты"
                        ),
                        "action": (
                            "Обновить сигнатуры антивируса и правила файрвола"
                        ),
                    }
                )

            # Рекомендации по качеству данных
            if self.metrics.data_quality_score < 0.7:
                recommendations.append(
                    {
                        "type": "data_quality",
                        "priority": "medium",
                        "description": (
                            "Низкое качество данных, рекомендуется улучшить "
                            "источники"
                        ),
                        "action": "Добавить более надежные источники угроз",
                    }
                )

            # Рекомендации по производительности
            if self.metrics.collection_speed < 10:
                recommendations.append(
                    {
                        "type": "performance",
                        "priority": "low",
                        "description": "Низкая скорость сбора данных",
                        "action": "Оптимизировать процессы сбора и обработки",
                    }
                )

            return recommendations

        except Exception as e:
            self.log_activity(
                "Ошибка генерации рекомендаций: {}".format(str(e)), "error"
            )
            return []

    def stop(self):
        """Остановка агента"""
        try:
            self.log_activity("Остановка ThreatIntelligenceAgent...")

            # Остановка фоновых процессов
            # В реальной реализации здесь будет остановка потоков

            # Сохранение данных
            self._save_data()

            self.log_activity("ThreatIntelligenceAgent остановлен")

        except Exception as e:
            self.log_activity(
                "Ошибка остановки ThreatIntelligenceAgent: {}".format(str(e)),
                "error",
            )

    def __iter__(self):
        """Итерация по угрозам"""
        return iter(self.threats.values())
    
    def __enter__(self):
        """Контекстный менеджер - вход"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        self.stop()
        if exc_type:
            self.log_activity(f"Ошибка в контексте: {exc_val}", "error")
        return False  # Не подавляем исключения

    def _save_data(self):
        """Сохранение данных агента"""
        try:
            data_dir = "data/threat_intelligence"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            # Сохранение угроз
            threats_file = os.path.join(data_dir, "threats.json")
            with open(threats_file, "w") as f:
                json.dump(
                    {
                        tid: threat.to_dict()
                        for tid, threat in self.threats.items()
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Сохранение метрик
            metrics_file = os.path.join(data_dir, "metrics.json")
            with open(metrics_file, "w") as f:
                json.dump(
                    self.metrics.to_dict(), f, indent=2, ensure_ascii=False
                )

            self.log_activity("Данные сохранены в {}".format(data_dir))

        except Exception as e:
            self.log_activity(
                "Ошибка сохранения данных: {}".format(str(e)), "error"
            )


if __name__ == "__main__":
    # Тестирование агента
    agent = ThreatIntelligenceAgent()

    if agent.initialize():
        print("ThreatIntelligenceAgent инициализирован успешно")

        # Сбор угроз
        threats_collected = agent.collect_threats()
        print("Собрано угроз: {}".format(threats_collected))

        # Анализ угроз
        threats_analyzed = agent.analyze_threats()
        print("Проанализировано угроз: {}".format(threats_analyzed))

        # Генерация отчета
        report = agent.generate_report()
        if report:
            print("Отчет сгенерирован: {}".format(report["report_id"]))

        # Остановка агента
        agent.stop()
    else:
        print("Ошибка инициализации ThreatIntelligenceAgent")
