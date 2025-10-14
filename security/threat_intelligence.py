# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Threat Intelligence Module
Модуль разведки угроз для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import hashlib
import json
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from core.base import ComponentStatus, SecurityBase, SecurityLevel


class ThreatCategory(Enum):
    """Категории угроз"""

    MALWARE = "malware"
    PHISHING = "phishing"
    SOCIAL_ENGINEERING = "social_engineering"
    DATA_BREACH = "data_breach"
    NETWORK_ATTACK = "network_attack"
    INSIDER_THREAT = "insider_threat"
    ZERO_DAY = "zero_day"
    RANSOMWARE = "ransomware"
    APT = "apt"
    DDoS = "ddos"


class ThreatSource(Enum):
    """Источники угроз"""

    INTERNAL = "internal"
    EXTERNAL = "external"
    THIRD_PARTY = "third_party"
    OPEN_SOURCE = "open_source"
    VENDOR = "vendor"
    COMMUNITY = "community"


class ThreatIndicator:
    """Класс для представления индикатора угрозы"""

    def __init__(
        self,
        indicator_type: str,
        value: str,
        threat_category: ThreatCategory,
        confidence: float = 0.5,
        source: ThreatSource = ThreatSource.EXTERNAL,
    ):
        self.indicator_type = indicator_type  # IP, domain, hash, URL, etc.
        self.value = value
        self.threat_category = threat_category
        self.confidence = confidence
        self.source = source
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.seen_count = 1
        self.is_active = True
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}

    def update_sighting(self):
        """Обновление информации о наблюдении"""
        self.last_seen = datetime.now()
        self.seen_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "indicator_type": self.indicator_type,
            "value": self.value,
            "threat_category": self.threat_category.value,
            "confidence": self.confidence,
            "source": self.source.value,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "seen_count": self.seen_count,
            "is_active": self.is_active,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class ThreatReport:
    """Класс для представления отчета об угрозе"""

    def __init__(
        self,
        threat_id: str,
        title: str,
        description: str,
        threat_category: ThreatCategory,
        severity: SecurityLevel,
    ):
        self.threat_id = threat_id
        self.title = title
        self.description = description
        self.threat_category = threat_category
        self.severity = severity
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.indicators: List[ThreatIndicator] = []
        self.recommendations: List[str] = []
        self.mitigation_steps: List[str] = []
        self.references: List[str] = []
        self.status = "active"

    def add_indicator(self, indicator: ThreatIndicator):
        """Добавление индикатора к отчету"""
        self.indicators.append(indicator)
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "threat_id": self.threat_id,
            "title": self.title,
            "description": self.description,
            "threat_category": self.threat_category.value,
            "severity": self.severity.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "indicators": [ind.to_dict() for ind in self.indicators],
            "recommendations": self.recommendations,
            "mitigation_steps": self.mitigation_steps,
            "references": self.references,
            "status": self.status,
        }


class ThreatIntelligenceManager(SecurityBase):
    """Менеджер разведки угроз для системы ALADDIN"""

    def __init__(
        self,
        name: str = "ThreatIntelligenceManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация разведки угроз
        self.update_interval = (
            config.get("update_interval", 3600) if config else 3600
        )  # 1 час
        self.max_indicators = (
            config.get("max_indicators", 10000) if config else 10000
        )
        self.confidence_threshold = (
            config.get("confidence_threshold", 0.7) if config else 0.7
        )
        self.enable_auto_update = (
            config.get("enable_auto_update", True) if config else True
        )

        # Хранилище данных
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.threat_reports: Dict[str, ThreatReport] = {}
        self.threat_feeds: Dict[str, Any] = {}
        self.ioc_database: Dict[str, Any] = {}
        self.threat_patterns: Dict[str, Any] = {}

        # Статистика
        self.total_indicators = 0
        self.active_indicators = 0
        self.threats_detected = 0
        self.false_positives = 0
        self.feed_updates = 0

    def initialize(self) -> bool:
        """Инициализация менеджера разведки угроз"""
        try:
            self.log_activity(
                f"Инициализация менеджера разведки угроз {self.name}"
            )
            self.status = ComponentStatus.INITIALIZING

            # Загрузка базовых индикаторов угроз
            self._load_basic_indicators()

            # Настройка источников угроз
            self._setup_threat_feeds()

            # Инициализация базы данных IOC
            self._initialize_ioc_database()

            # Запуск автоматического обновления
            if self.enable_auto_update:
                self._start_auto_update()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер разведки угроз {self.name} успешно инициализирован"
            )
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера разведки угроз "
                f"{self.name}: {e}",
                "error",
            )
            return False

    def _load_basic_indicators(self):
        """Загрузка базовых индикаторов угроз"""
        basic_indicators = [
            {
                "type": "domain",
                "value": "malicious.example.com",
                "category": ThreatCategory.MALWARE,
                "confidence": 0.9,
                "source": ThreatSource.EXTERNAL,
                "tags": ["malware", "c2"],
            },
            {
                "type": "ip",
                "value": "192.168.1.100",
                "category": ThreatCategory.PHISHING,
                "confidence": 0.8,
                "source": ThreatSource.EXTERNAL,
                "tags": ["phishing", "spam"],
            },
            {
                "type": "hash",
                "value": "a1b2c3d4e5f6789012345678901234567890abcd",
                "category": ThreatCategory.RANSOMWARE,
                "confidence": 0.95,
                "source": ThreatSource.VENDOR,
                "tags": ["ransomware", "encryption"],
            },
        ]

        for indicator_data in basic_indicators:
            indicator = ThreatIndicator(
                indicator_type=indicator_data["type"],
                value=indicator_data["value"],
                threat_category=indicator_data["category"],
                confidence=indicator_data["confidence"],
                source=indicator_data["source"],
            )
            indicator.tags = indicator_data["tags"]

            self.add_indicator(indicator)

        self.log_activity(
            f"Загружено {len(basic_indicators)} базовых индикаторов угроз"
        )

    def _setup_threat_feeds(self):
        """Настройка источников угроз"""
        self.threat_feeds = {
            "openphish": {
                "url": "https://openphish.com/feed.txt",
                "type": "phishing",
                "enabled": True,
                "last_update": None,
            },
            "abuse_ch": {
                "url": "https://urlhaus.abuse.ch/downloads/text/",
                "type": "malware",
                "enabled": True,
                "last_update": None,
            },
            "tor_exit": {
                "url": "https://check.torproject.org/exit-addresses",
                "type": "network",
                "enabled": True,
                "last_update": None,
            },
        }
        self.log_activity("Источники угроз настроены")

    def _initialize_ioc_database(self):
        """Инициализация базы данных IOC"""
        self.ioc_database = {
            "ips": {},
            "domains": {},
            "urls": {},
            "hashes": {},
            "emails": {},
        }
        self.log_activity("База данных IOC инициализирована")

    def _start_auto_update(self):
        """Запуск автоматического обновления"""
        # Здесь будет логика автоматического обновления
        self.log_activity("Автоматическое обновление угроз запущено")

    def add_indicator(self, indicator: ThreatIndicator) -> bool:
        """
        Добавление индикатора угрозы

        Args:
            indicator: Индикатор угрозы

        Returns:
            bool: True если индикатор добавлен
        """
        try:
            # Создание уникального ключа
            indicator_key = f"{indicator.indicator_type}:{indicator.value}"

            if indicator_key in self.indicators:
                # Обновление существующего индикатора
                existing = self.indicators[indicator_key]
                existing.update_sighting()
                existing.confidence = max(
                    existing.confidence, indicator.confidence
                )
                existing.tags.extend(
                    [tag for tag in indicator.tags if tag not in existing.tags]
                )
                existing.metadata.update(indicator.metadata)
            else:
                # Добавление нового индикатора
                self.indicators[indicator_key] = indicator
                self.total_indicators += 1
                self.active_indicators += 1

                # Добавление в базу данных IOC
                self._add_to_ioc_database(indicator)

            self.log_activity(
                f"Добавлен индикатор угрозы: "
                f"{indicator.indicator_type}:{indicator.value}"
            )
            return True

        except Exception as e:
            self.log_activity(f"Ошибка добавления индикатора: {e}", "error")
            return False

    def _add_to_ioc_database(self, indicator: ThreatIndicator):
        """Добавление индикатора в базу данных IOC"""
        try:
            if indicator.indicator_type == "ip":
                self.ioc_database["ips"][indicator.value] = indicator
            elif indicator.indicator_type == "domain":
                self.ioc_database["domains"][indicator.value] = indicator
            elif indicator.indicator_type == "url":
                self.ioc_database["urls"][indicator.value] = indicator
            elif indicator.indicator_type == "hash":
                self.ioc_database["hashes"][indicator.value] = indicator
            elif indicator.indicator_type == "email":
                self.ioc_database["emails"][indicator.value] = indicator
        except Exception as e:
            self.log_activity(f"Ошибка добавления в базу IOC: {e}", "error")

    def check_indicator(
        self, indicator_type: str, value: str
    ) -> Tuple[bool, Optional[ThreatIndicator]]:
        """
        Проверка индикатора на наличие в базе угроз

        Args:
            indicator_type: Тип индикатора
            value: Значение индикатора

        Returns:
            Tuple[bool, Optional[ThreatIndicator]]: (найден, индикатор)
        """
        try:
            indicator_key = f"{indicator_type}:{value}"

            if indicator_key in self.indicators:
                indicator = self.indicators[indicator_key]
                if (
                    indicator.is_active
                    and indicator.confidence >= self.confidence_threshold
                ):
                    self.threats_detected += 1
                    self.log_activity(
                        f"Обнаружена угроза: {indicator_type}:{value}",
                        "warning",
                    )
                    return True, indicator

            return False, None

        except Exception as e:
            self.log_activity(f"Ошибка проверки индикатора: {e}", "error")
            return False, None

    def check_ip(
        self, ip_address: str
    ) -> Tuple[bool, Optional[ThreatIndicator]]:
        """Проверка IP адреса"""
        return self.check_indicator("ip", ip_address)

    def check_domain(
        self, domain: str
    ) -> Tuple[bool, Optional[ThreatIndicator]]:
        """Проверка домена"""
        return self.check_indicator("domain", domain)

    def check_url(self, url: str) -> Tuple[bool, Optional[ThreatIndicator]]:
        """Проверка URL"""
        return self.check_indicator("url", url)

    def check_hash(
        self, file_hash: str
    ) -> Tuple[bool, Optional[ThreatIndicator]]:
        """Проверка хеша файла"""
        return self.check_indicator("hash", file_hash)

    def check_email(
        self, email: str
    ) -> Tuple[bool, Optional[ThreatIndicator]]:
        """Проверка email"""
        return self.check_indicator("email", email)

    def create_threat_report(
        self,
        threat_id: str,
        title: str,
        description: str,
        threat_category: ThreatCategory,
        severity: SecurityLevel,
    ) -> Optional[ThreatReport]:
        """
        Создание отчета об угрозе

        Args:
            threat_id: ID угрозы
            title: Заголовок отчета
            description: Описание угрозы
            threat_category: Категория угрозы
            severity: Серьезность угрозы

        Returns:
            Optional[ThreatReport]: Созданный отчет или None в случае ошибки
        """
        try:
            report = ThreatReport(
                threat_id, title, description, threat_category, severity
            )
            self.threat_reports[threat_id] = report

            self.log_activity(f"Создан отчет об угрозе: {title}")
            return report

        except Exception as e:
            self.log_activity(
                f"Ошибка создания отчета об угрозе: {e}", "error"
            )
            return None

    def add_indicator_to_report(
        self, threat_id: str, indicator: ThreatIndicator
    ) -> bool:
        """
        Добавление индикатора к отчету об угрозе

        Args:
            threat_id: ID угрозы
            indicator: Индикатор угрозы

        Returns:
            bool: True если индикатор добавлен
        """
        try:
            if threat_id not in self.threat_reports:
                return False

            report = self.threat_reports[threat_id]
            report.add_indicator(indicator)

            self.log_activity(f"Индикатор добавлен к отчету {threat_id}")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка добавления индикатора к отчету: {e}", "error"
            )
            return False

    def get_threat_report(self, threat_id: str) -> Optional[ThreatReport]:
        """
        Получение отчета об угрозе

        Args:
            threat_id: ID угрозы

        Returns:
            Optional[ThreatReport]: Отчет об угрозе
        """
        if threat_id not in self.threat_reports:
            return None

        return self.threat_reports[threat_id]

    def get_all_threat_reports(self) -> List[Dict[str, Any]]:
        """
        Получение всех отчетов об угрозах

        Returns:
            List[Dict[str, Any]]: Список отчетов
        """
        return [report.to_dict() for report in self.threat_reports.values()]

    def search_indicators(
        self, query: str, indicator_type: Optional[str] = None
    ) -> List[ThreatIndicator]:
        """
        Поиск индикаторов угроз

        Args:
            query: Поисковый запрос
            indicator_type: Тип индикатора для фильтрации

        Returns:
            List[ThreatIndicator]: Список найденных индикаторов
        """
        try:
            results = []
            query_lower = query.lower()

            for indicator in self.indicators.values():
                if not indicator.is_active:
                    continue

                if (
                    indicator_type
                    and indicator.indicator_type != indicator_type
                ):
                    continue

                # Поиск по значению
                if query_lower in indicator.value.lower():
                    results.append(indicator)
                    continue

                # Поиск по тегам
                for tag in indicator.tags:
                    if query_lower in tag.lower():
                        results.append(indicator)
                        break

                # Поиск по метаданным
                for key, value in indicator.metadata.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        results.append(indicator)
                        break

            return results

        except Exception as e:
            self.log_activity(f"Ошибка поиска индикаторов: {e}", "error")
            return []

    def get_indicators_by_category(
        self, category: ThreatCategory
    ) -> List[ThreatIndicator]:
        """
        Получение индикаторов по категории

        Args:
            category: Категория угроз

        Returns:
            List[ThreatIndicator]: Список индикаторов
        """
        return [
            indicator
            for indicator in self.indicators.values()
            if indicator.threat_category == category and indicator.is_active
        ]

    def get_indicators_by_source(
        self, source: ThreatSource
    ) -> List[ThreatIndicator]:
        """
        Получение индикаторов по источнику

        Args:
            source: Источник угроз

        Returns:
            List[ThreatIndicator]: Список индикаторов
        """
        return [
            indicator
            for indicator in self.indicators.values()
            if indicator.source == source and indicator.is_active
        ]

    def update_threat_feed(self, feed_name: str) -> bool:
        """
        Обновление источника угроз

        Args:
            feed_name: Название источника

        Returns:
            bool: True если источник обновлен
        """
        try:
            if feed_name not in self.threat_feeds:
                return False

            feed = self.threat_feeds[feed_name]
            if not feed["enabled"]:
                return False

            # Здесь будет логика обновления источника
            # В реальной реализации здесь будет HTTP запрос к источнику

            feed["last_update"] = datetime.now()
            self.feed_updates += 1

            self.log_activity(f"Источник угроз {feed_name} обновлен")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка обновления источника {feed_name}: {e}", "error"
            )
            return False

    def deactivate_indicator(self, indicator_type: str, value: str) -> bool:
        """
        Деактивация индикатора угрозы

        Args:
            indicator_type: Тип индикатора
            value: Значение индикатора

        Returns:
            bool: True если индикатор деактивирован
        """
        try:
            indicator_key = f"{indicator_type}:{value}"

            if indicator_key in self.indicators:
                indicator = self.indicators[indicator_key]
                indicator.is_active = False
                self.active_indicators = max(0, self.active_indicators - 1)

                self.log_activity(
                    f"Индикатор деактивирован: {indicator_type}:{value}"
                )
                return True

            return False

        except Exception as e:
            self.log_activity(f"Ошибка деактивации индикатора: {e}", "error")
            return False

    def mark_false_positive(self, indicator_type: str, value: str) -> bool:
        """
        Отметка индикатора как ложного срабатывания

        Args:
            indicator_type: Тип индикатора
            value: Значение индикатора

        Returns:
            bool: True если индикатор отмечен
        """
        try:
            indicator_key = f"{indicator_type}:{value}"

            if indicator_key in self.indicators:
                indicator = self.indicators[indicator_key]
                indicator.confidence = 0.0
                if isinstance(indicator.tags, list):
                    indicator.tags.append("false_positive")
                else:
                    indicator.tags = list(indicator.tags) + ["false_positive"]
                self.false_positives += 1

                self.log_activity(
                    f"Индикатор отмечен как ложное срабатывание: "
                    f"{indicator_type}:{value}"
                )
                return True

            return False

        except Exception as e:
            self.log_activity(
                f"Ошибка отметки ложного срабатывания: {e}", "error"
            )
            return False

    def get_threat_intelligence_stats(self) -> Dict[str, Any]:
        """
        Получение статистики разведки угроз

        Returns:
            Dict[str, Any]: Статистика разведки угроз
        """
        return {
            "total_indicators": self.total_indicators,
            "active_indicators": self.active_indicators,
            "threats_detected": self.threats_detected,
            "false_positives": self.false_positives,
            "feed_updates": self.feed_updates,
            "total_reports": len(self.threat_reports),
            "indicators_by_type": self._get_indicators_by_type(),
            "indicators_by_category": self._get_indicators_by_category(),
            "indicators_by_source": self._get_indicators_by_source(),
        }

    def _get_indicators_by_type(self) -> Dict[str, int]:
        """Получение количества индикаторов по типам"""
        types_count: Dict[str, int] = {}
        for indicator in self.indicators.values():
            if indicator.is_active:
                indicator_type = indicator.indicator_type
                types_count[indicator_type] = (
                    types_count.get(indicator_type, 0) + 1
                )
        return types_count

    def _get_indicators_by_category(self) -> Dict[str, int]:
        """Получение количества индикаторов по категориям"""
        categories_count: Dict[str, int] = {}
        for indicator in self.indicators.values():
            if indicator.is_active:
                category = indicator.threat_category.value
                categories_count[category] = (
                    categories_count.get(category, 0) + 1
                )
        return categories_count

    def _get_indicators_by_source(self) -> Dict[str, int]:
        """Получение количества индикаторов по источникам"""
        sources_count: Dict[str, int] = {}
        for indicator in self.indicators.values():
            if indicator.is_active:
                source = indicator.source.value
                sources_count[source] = sources_count.get(source, 0) + 1
        return sources_count

    def export_indicators(self, format_type: str = "json") -> str:
        """
        Экспорт индикаторов угроз

        Args:
            format_type: Тип формата (json, csv, stix)

        Returns:
            str: Индикаторы в указанном формате
        """
        try:
            active_indicators = [
                ind for ind in self.indicators.values() if ind.is_active
            ]

            if format_type == "json":
                return json.dumps(
                    [ind.to_dict() for ind in active_indicators],
                    indent=2,
                    ensure_ascii=False,
                )
            elif format_type == "csv":
                return self._export_indicators_csv(active_indicators)
            elif format_type == "stix":
                return self._export_indicators_stix(active_indicators)
            else:
                raise ValueError(f"Неподдерживаемый формат: {format_type}")

        except Exception as e:
            self.log_activity(f"Ошибка экспорта индикаторов: {e}", "error")
            return ""

    def _export_indicators_csv(self, indicators: List[ThreatIndicator]) -> str:
        """Экспорт индикаторов в CSV формат"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow(
            [
                "Type",
                "Value",
                "Category",
                "Confidence",
                "Source",
                "First Seen",
                "Last Seen",
                "Tags",
            ]
        )

        # Данные
        for indicator in indicators:
            writer.writerow(
                [
                    indicator.indicator_type,
                    indicator.value,
                    indicator.threat_category.value,
                    indicator.confidence,
                    indicator.source.value,
                    indicator.first_seen.isoformat(),
                    indicator.last_seen.isoformat(),
                    ",".join(indicator.tags),
                ]
            )

        return output.getvalue()

    def _export_indicators_stix(
        self, indicators: List[ThreatIndicator]
    ) -> str:
        """Экспорт индикаторов в STIX формат"""
        # Базовая реализация STIX экспорта
        stix_data = {
            "type": "bundle",
            "id": (
                f"bundle--"
                f"{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
            ),
            "objects": [],
        }

        for indicator in indicators:
            stix_object = {
                "type": "indicator",
                "id": (
                    f"indicator--"
                    f"{hashlib.md5(indicator.value.encode()).hexdigest()[:8]}"
                ),
                "created": indicator.first_seen.isoformat(),
                "modified": indicator.last_seen.isoformat(),
                "pattern": (
                    f"[{indicator.indicator_type}:value = '{indicator.value}']"
                ),
                "pattern_type": "stix",
                "pattern_version": "2.1",
                "valid_from": indicator.first_seen.isoformat(),
                "labels": list(indicator.tags),
            }
            stix_data["objects"].append(stix_object)

        return json.dumps(stix_data, indent=2, ensure_ascii=False)

    def start(self) -> bool:
        """Запуск менеджера разведки угроз"""
        try:
            self.log_activity(f"Запуск менеджера разведки угроз {self.name}")
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер разведки угроз {self.name} успешно запущен"
            )
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера разведки угроз {self.name}: {e}",
                "error",
            )
            return False

    def stop(self) -> bool:
        """Остановка менеджера разведки угроз"""
        try:
            self.log_activity(
                f"Остановка менеджера разведки угроз {self.name}"
            )

            # Остановка автоматического обновления
            self.enable_auto_update = False

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Менеджер разведки угроз {self.name} успешно остановлен"
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера разведки угроз {self.name}: {e}",
                "error",
            )
            return False
