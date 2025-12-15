#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ Anti-Tracker Agent
Агент для блокировки трекеров и рекламы

Функциональность:
- Блокировка известных трекеров и рекламных сетей
- Проверка запросов через backend API (гибридный подход)
- Локальный кэш списков трекеров для быстрой проверки
- Настройки блокировки (белые/черные списки)
- Статистика заблокированных запросов

⚠️ ВАЖНО: VPN убран из системы безопасности! Агент работает БЕЗ VPN.

Дата создания: 12 декабря 2025
Версия: 1.0.0
"""

import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import re

# Импорты (будут доступны на сервере)
try:
    from security.base import SecurityBase
    from security.ai_agents.threat_monitoring_interface import (
        ThreatMonitoringInterface,
        ThreatEvent,
        get_threat_event_bus
    )
except ImportError:
    # Для локальной разработки создаем заглушки
    class SecurityBase:
        def __init__(self, config: Optional[Dict[str, Any]] = None):
            config_dict = config if config is not None else {}
            self.config = config_dict
            self.logger = logging.getLogger(self.__class__.__name__)

    class ThreatMonitoringInterface:
        pass

    @dataclass
    class ThreatEvent:
        event_id: str = ""
        agent_name: str = ""
        threat_type: str = ""
        severity: str = ""
        source: str = ""
        target: str = ""
        timestamp: str = ""
        metadata: Dict[str, Any] = None
        description: Optional[str] = None

    def get_threat_event_bus():
        return None


class TrackerType(Enum):
    """Типы трекеров"""
    ANALYTICS = "analytics"  # Аналитика (Google Analytics, Yandex Metrica)
    ADVERTISING = "advertising"  # Реклама (Google Ads, Yandex Direct)
    SOCIAL = "social"  # Социальные трекеры (VK Pixel, Одноклассники Pixel)
    PATTERN = "pattern"  # Паттерн URL (/analytics, /track, /pixel)
    UNKNOWN = "unknown"  # Неизвестный трекер


@dataclass
class BlockedRequest:
    """Заблокированный запрос"""
    request_id: str
    url: str
    domain: str
    tracker_type: TrackerType
    timestamp: float
    user_id: Optional[str] = None
    reason: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['tracker_type'] = self.tracker_type.value
        return result


@dataclass
class TrackerStats:
    """Статистика блокировок"""
    total_blocked: int = 0
    blocked_by_type: Dict[str, int] = None
    blocked_domains: Dict[str, int] = None
    last_blocked: Optional[float] = None
    first_blocked: Optional[float] = None

    def __post_init__(self):
        if self.blocked_by_type is None:
            self.blocked_by_type = {}
        if self.blocked_domains is None:
            self.blocked_domains = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AntiTrackerAgent(SecurityBase, ThreatMonitoringInterface):
    """
    Агент для блокировки трекеров и рекламы

    Работает БЕЗ VPN, использует гибридный подход:
    - Локальный кэш списков трекеров для быстрой проверки
    - Backend API для сложных случаев
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация агента

        Args:
            config: Конфигурация агента
                - strict_mode: Строгий режим блокировки (по умолчанию True)
                - enable_analytics_blocking: Блокировать аналитику (по умолчанию True)
                - enable_advertising_blocking: Блокировать рекламу (по умолчанию True)
                - enable_social_blocking: Блокировать социальные трекеры (по умолчанию True)
                - whitelist: Список разрешенных доменов
                - blacklist: Список заблокированных доменов
        """
        super().__init__(config)

        # Инициализация логгера
        self.logger = logging.getLogger(self.__class__.__name__)

        # Конфигурация
        config_dict = config if config is not None else {}
        self.strict_mode = config_dict.get("strict_mode", True)
        self.enable_analytics_blocking = config_dict.get("enable_analytics_blocking", True)
        self.enable_advertising_blocking = config_dict.get("enable_advertising_blocking", True)
        self.enable_social_blocking = config_dict.get("enable_social_blocking", True)

        # Белые и черные списки
        self.whitelist = set(config_dict.get("whitelist", []))
        self.blacklist = set(config_dict.get("blacklist", []))

        # Хранение данных
        self.blocked_trackers: Dict[str, Dict[str, Any]] = {}
        self.blocked_requests: List[BlockedRequest] = []
        self.stats = TrackerStats()

        # Инициализация списков трекеров
        self._initialize_tracker_lists()

        # Инициализация паттернов
        self._initialize_tracker_patterns()

        self.logger.info("🛡️ Anti-Tracker Agent инициализирован")

    def _initialize_tracker_lists(self):
        """Инициализация списков известных трекеров для России"""
        # Аналитика
        self.analytics_domains = {
            "google-analytics.com",
            "analytics.google.com",
            "googletagmanager.com",
            "mc.yandex.ru",  # Yandex Metrica
            "yandex.ru/metrika",
            "adobe.com",
            "omniture.com",
            "mixpanel.com",
            "hotjar.com"
        }

        # Рекламные сети
        self.advertising_domains = {
            "googleadservices.com",
            "doubleclick.net",
            "googlesyndication.com",
            "yandex.ru/ads",  # Yandex Direct
            "direct.yandex.ru",
            "vk.com/ads",  # VK Ads
            "ads.vk.com",
            "mytarget.ru",  # myTarget
            "begun.ru"  # Бегун
        }

        # Социальные трекеры (для России)
        self.social_domains = {
            "vk.com/rtrg",  # VK Pixel
            "vk.com/js/api/openapi.js",
            "ok.ru/js/sdk",  # Одноклассники Pixel
            "ok.ru/pixel",
            "max.ru/pixel",  # MAX Pixel
            "max.ru/js/tracker",
            "linkedin.com/px"  # LinkedIn Insight
        }

        # Объединенный список всех трекеров
        self.all_tracker_domains = (
            self.analytics_domains
            | self.advertising_domains
            | self.social_domains
        )

        self.logger.info(f"✅ Загружено {len(self.all_tracker_domains)} известных трекеров")

    def _initialize_tracker_patterns(self):
        """Инициализация паттернов URL для обнаружения трекеров"""
        self.tracker_patterns = [
            r"/analytics",
            r"/track",
            r"/pixel",
            r"/beacon",
            r"/collect",
            r"/gtm\.js",  # Google Tag Manager
            r"/ga\.js",  # Google Analytics
            r"/tr\?id=",  # Tracking pixel
            r"/api/track",
            r"/api/analytics"
        ]

        self.logger.info(f"✅ Загружено {len(self.tracker_patterns)} паттернов трекеров")

    def check_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Проверка запроса на наличие трекеров (основной метод)

        Args:
            url: URL запроса
            headers: HTTP заголовки (опционально)

        Returns:
            Dict с результатом проверки:
                - blocked: bool - заблокирован ли запрос
                - reason: str - причина блокировки
                - tracker_type: str - тип трекера
        """
        try:
            # Проверка белого списка
            domain = self._extract_domain(url)
            if domain in self.whitelist:
                return {"blocked": False, "reason": "Whitelisted domain"}

            # Проверка черного списка
            if domain in self.blacklist:
                return {
                    "blocked": True,
                    "reason": "Blacklisted domain",
                    "tracker_type": "blacklist"
                }

            # Проверка по доменам трекеров
            tracker_type = self.is_tracker_domain(domain)
            if tracker_type:
                return {
                    "blocked": True,
                    "reason": f"Known tracker domain ({tracker_type.value})",
                    "tracker_type": tracker_type.value
                }

            # Проверка по паттернам URL
            if self.matches_tracker_pattern(url):
                return {
                    "blocked": True,
                    "reason": "Tracker pattern detected",
                    "tracker_type": "pattern"
                }

            # Запрос разрешен
            return {"blocked": False}

        except Exception as e:
            self.logger.error(f"❌ Ошибка при проверке запроса {url}: {e}")
            # В случае ошибки разрешаем запрос (fail-open)
            return {"blocked": False, "error": str(e)}

    def is_tracker_domain(self, domain: str) -> Optional[TrackerType]:
        """
        Проверка домена на наличие в списках трекеров

        Args:
            domain: Домен для проверки

        Returns:
            TrackerType если домен является трекером, иначе None
        """
        # Нормализация домена
        domain = domain.lower().strip()

        # Проверка аналитики
        if self.enable_analytics_blocking:
            for tracker_domain in self.analytics_domains:
                if tracker_domain in domain or domain in tracker_domain:
                    return TrackerType.ANALYTICS

        # Проверка рекламы
        if self.enable_advertising_blocking:
            for tracker_domain in self.advertising_domains:
                if tracker_domain in domain or domain in tracker_domain:
                    return TrackerType.ADVERTISING

        # Проверка социальных трекеров
        if self.enable_social_blocking:
            for tracker_domain in self.social_domains:
                if tracker_domain in domain or domain in tracker_domain:
                    return TrackerType.SOCIAL

        return None

    def matches_tracker_pattern(self, url: str) -> bool:
        """
        Проверка URL на соответствие паттернам трекеров

        Args:
            url: URL для проверки

        Returns:
            True если URL соответствует паттерну трекера
        """
        url_lower = url.lower()

        for pattern in self.tracker_patterns:
            if re.search(pattern, url_lower):
                return True

        return False

    def block_tracker(self, domain: str, tracker_type: TrackerType, reason: Optional[str] = None) -> bool:
        """
        Блокировка трекера

        Args:
            domain: Домен трекера
            tracker_type: Тип трекера
            reason: Причина блокировки

        Returns:
            True если трекер успешно заблокирован
        """
        try:
            domain = domain.lower().strip()

            # Добавляем в черный список
            self.blacklist.add(domain)

            # Сохраняем информацию о трекере
            self.blocked_trackers[domain] = {
                "domain": domain,
                "tracker_type": tracker_type.value,
                "blocked_at": time.time(),
                "reason": reason or "Manual block"
            }

            self.logger.info(f"🚫 Трекер заблокирован: {domain} ({tracker_type.value})")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при блокировке трекера {domain}: {e}")
            return False

    def unblock_tracker(self, domain: str) -> bool:
        """
        Разблокировка трекера

        Args:
            domain: Домен трекера

        Returns:
            True если трекер успешно разблокирован
        """
        try:
            domain = domain.lower().strip()

            # Удаляем из черного списка
            self.blacklist.discard(domain)

            # Удаляем из списка заблокированных
            if domain in self.blocked_trackers:
                del self.blocked_trackers[domain]

            self.logger.info(f"✅ Трекер разблокирован: {domain}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при разблокировке трекера {domain}: {e}")
            return False

    def is_blocked(self, domain: str) -> bool:
        """
        Проверка, заблокирован ли домен

        Args:
            domain: Домен для проверки

        Returns:
            True если домен заблокирован
        """
        domain = domain.lower().strip()
        return domain in self.blacklist or domain in self.blocked_trackers

    def _extract_domain(self, url: str) -> str:
        """
        Извлечение домена из URL

        Args:
            url: URL

        Returns:
            Домен
        """
        try:
            # Простое извлечение домена
            if "://" in url:
                url = url.split("://")[1]
            if "/" in url:
                url = url.split("/")[0]
            if ":" in url:
                url = url.split(":")[0]
            return url.lower().strip()
        except Exception:
            return url.lower().strip()

    def record_blocked_request(self, url: str, tracker_type: TrackerType, user_id: Optional[str] = None, reason: Optional[str] = None):
        """
        Запись заблокированного запроса

        Args:
            url: URL запроса
            tracker_type: Тип трекера
            user_id: ID пользователя (опционально)
            reason: Причина блокировки (опционально)
        """
        try:
            domain = self._extract_domain(url)
            request_id = f"block_{int(time.time() * 1000)}_{len(self.blocked_requests)}"

            blocked_request = BlockedRequest(
                request_id=request_id,
                url=url,
                domain=domain,
                tracker_type=tracker_type,
                timestamp=time.time(),
                user_id=user_id,
                reason=reason,
                metadata={}
            )

            self.blocked_requests.append(blocked_request)

            # Обновление статистики
            self.stats.total_blocked += 1
            tracker_type_str = tracker_type.value
            self.stats.blocked_by_type[tracker_type_str] = self.stats.blocked_by_type.get(tracker_type_str, 0) + 1
            self.stats.blocked_domains[domain] = self.stats.blocked_domains.get(domain, 0) + 1

            if self.stats.first_blocked is None:
                self.stats.first_blocked = time.time()
            self.stats.last_blocked = time.time()

            # Ограничение размера истории (последние 1000 запросов)
            if len(self.blocked_requests) > 1000:
                self.blocked_requests = self.blocked_requests[-1000:]

            self.logger.debug(f"📝 Заблокирован запрос: {url} ({tracker_type.value})")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при записи заблокированного запроса: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики блокировок

        Returns:
            Dict со статистикой
        """
        return {
            "total_blocked": self.stats.total_blocked,
            "blocked_by_type": self.stats.blocked_by_type.copy(),
            "top_blocked_domains": dict(sorted(
                self.stats.blocked_domains.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            "last_blocked": self.stats.last_blocked,
            "first_blocked": self.stats.first_blocked,
            "blocked_trackers_count": len(self.blocked_trackers)
        }

    def get_tracker_lists(self) -> Dict[str, List[str]]:
        """
        Получение списков трекеров (для синхронизации с iOS)

        Returns:
            Dict со списками трекеров по типам
        """
        return {
            "analytics": list(self.analytics_domains),
            "advertising": list(self.advertising_domains),
            "social": list(self.social_domains),
            "patterns": self.tracker_patterns,
            "all": list(self.all_tracker_domains)
        }

    # ThreatMonitoringInterface методы

    def collect_threats(self) -> List[ThreatEvent]:
        """
        Сбор угроз (заблокированные трекеры)

        Returns:
            Список событий угроз
        """
        threats = []
        try:
            # Берем последние 10 заблокированных запросов
            recent_blocks = self.blocked_requests[-10:] if len(self.blocked_requests) > 10 else self.blocked_requests

            for blocked_request in recent_blocks:
                threat = ThreatEvent(
                    event_id=blocked_request.request_id,
                    agent_name=self.__class__.__name__,
                    threat_type="tracker",
                    severity="low",
                    source=blocked_request.domain,
                    target=blocked_request.url,
                    timestamp=datetime.fromtimestamp(blocked_request.timestamp).isoformat(),
                    metadata={
                        "tracker_type": blocked_request.tracker_type.value,
                        "reason": blocked_request.reason
                    },
                    description=f"Заблокирован трекер: {blocked_request.domain}"
                )
                threats.append(threat)

        except Exception as e:
            self.logger.error(f"❌ Ошибка при сборе угроз: {e}")

        return threats

    def analyze_threats(self, threats: List[ThreatEvent]) -> Dict[str, Any]:
        """
        Анализ угроз

        Args:
            threats: Список угроз

        Returns:
            Результат анализа
        """
        try:
            if not threats:
                return {"status": "no_threats", "count": 0}

            # Группировка по типам трекеров
            by_type = {}
            for threat in threats:
                tracker_type = threat.metadata.get("tracker_type", "unknown")
                by_type[tracker_type] = by_type.get(tracker_type, 0) + 1

            return {
                "status": "analyzed",
                "total_threats": len(threats),
                "by_type": by_type,
                "recommendation": "Продолжать блокировку трекеров"
            }

        except Exception as e:
            self.logger.error(f"❌ Ошибка при анализе угроз: {e}")
            return {"status": "error", "error": str(e)}

    def send_alert(self, threat: ThreatEvent) -> bool:
        """
        Отправка уведомления об угрозе

        Args:
            threat: Событие угрозы

        Returns:
            True если уведомление отправлено
        """
        try:
            # Логирование уведомления
            self.logger.warning(f"⚠️ Угроза обнаружена: {threat.description}")

            # Отправка через event bus (если доступен)
            event_bus = get_threat_event_bus()
            if event_bus:
                event_bus.publish(threat)

            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке уведомления: {e}")
            return False
