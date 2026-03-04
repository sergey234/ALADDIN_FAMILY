#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI Categories Agent
Агент для родительского контроля AI-сайтов и приложений

Функциональность:
- Блокировка/разрешение AI-сайтов (ChatGPT, Midjourney, DALL-E, Claude, Gemini)
- Настройки по времени (блокировка в определенное время)
- Настройки по возрасту
- Уведомления родителям о попытках доступа

Дата создания: 11 декабря 2025
Версия: 1.0.0
"""

import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

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
            self.config = config or {}
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


class AISiteCategory(Enum):
    """Категории AI-сайтов"""
    TEXT_GENERATION = "text_generation"  # ChatGPT, Claude, Gemini
    IMAGE_GENERATION = "image_generation"  # Midjourney, DALL-E, Stable Diffusion
    CODE_GENERATION = "code_generation"  # GitHub Copilot, Codeium
    VOICE_GENERATION = "voice_generation"  # ElevenLabs, Murf
    VIDEO_GENERATION = "video_generation"  # Runway, Pika
    OTHER = "other"


@dataclass
class AISite:
    """Информация об AI-сайте"""
    id: str
    name: str
    domain: str
    category: AISiteCategory
    description: Optional[str] = None
    age_restriction: Optional[int] = None  # Минимальный возраст (лет)
    requires_account: bool = True  # Требуется ли регистрация
    is_free: bool = False  # Бесплатный ли доступ
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['category'] = self.category.value
        return result


@dataclass
class TimeRestriction:
    """Ограничение по времени доступа"""
    start_time: str  # "HH:MM" формат, например "09:00"
    end_time: str  # "HH:MM" формат, например "18:00"
    days_of_week: List[int]  # [0-6] где 0=понедельник, 6=воскресенье
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgeRestriction:
    """Ограничение по возрасту"""
    min_age: int  # Минимальный возраст в годах
    require_parental_approval: bool = True  # Требуется ли одобрение родителей
    block_completely: bool = False  # Полная блокировка для этого возраста

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AISiteStatus:
    """Статус AI-сайта для пользователя"""
    site_id: str
    user_id: str
    is_blocked: bool
    is_allowed: bool
    time_restriction: Optional[TimeRestriction] = None
    age_restriction: Optional[AgeRestriction] = None
    last_access_attempt: Optional[str] = None
    access_count: int = 0
    blocked_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.time_restriction:
            result['time_restriction'] = self.time_restriction.to_dict()
        if self.age_restriction:
            result['age_restriction'] = self.age_restriction.to_dict()
        return result


@dataclass
class AccessAttempt:
    """Попытка доступа к AI-сайту"""
    id: str
    user_id: str
    site_id: str
    timestamp: str
    was_blocked: bool
    reason: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AICategoriesAgent(SecurityBase, ThreatMonitoringInterface):
    """
    Агент для родительского контроля AI-сайтов и приложений

    Функциональность:
    - Блокировка/разрешение AI-сайтов
    - Настройки по времени
    - Настройки по возрасту
    - Уведомления родителям
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация агента

        Args:
            config: Конфигурация агента
                - notify_parents: Отправлять ли уведомления родителям (по умолчанию True)
                - default_block_all: Блокировать ли все AI-сайты по умолчанию (по умолчанию False)
        """
        super().__init__(config)

        # Инициализация логгера
        self.logger = logging.getLogger(self.__class__.__name__)

        # Конфигурация
        config_dict = config if config is not None else {}
        self.notify_parents = config_dict.get("notify_parents", True)
        self.default_block_all = config_dict.get("default_block_all", False)

        # Список известных AI-сайтов
        self.ai_sites = self._initialize_ai_sites()

        # Словарь статусов сайтов для пользователей: {user_id: {site_id: AISiteStatus}}
        self.user_site_status: Dict[str, Dict[str, AISiteStatus]] = {}

        # История попыток доступа: {user_id: [AccessAttempt]}
        self.access_history: Dict[str, List[AccessAttempt]] = {}

        # Интеграция с ThreatEventBus для уведомлений
        try:
            self.event_bus = get_threat_event_bus()
            if self.event_bus:
                self.event_bus.subscribe(self, event_types=["ai_access", "*"])
                self.logger.info("✅ Подписан на ThreatEventBus")
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось подключиться к ThreatEventBus: {e}")
            self.event_bus = None

        self.logger.info("🤖 AICategoriesAgent инициализирован")

    def _initialize_ai_sites(self) -> Dict[str, AISite]:
        """
        Инициализация списка известных AI-сайтов

        Returns:
            Словарь AI-сайтов: {site_id: AISite}
        """
        sites = [
            # Российские AI-сервисы (самые популярные в России)
            AISite(
                id="alice",
                name="Алиса AI",
                domain="yandex.ru/alice",
                category=AISiteCategory.TEXT_GENERATION,
                description="Голосовой ассистент и AI от Яндекса (14.3% пользователей в России)",
                age_restriction=6,  # Алиса безопасна для детей
                requires_account=False,
                is_free=True
            ),
            AISite(
                id="yandexgpt",
                name="YandexGPT",
                domain="yandex.ru/gpt",
                category=AISiteCategory.TEXT_GENERATION,
                description="AI чат-бот от Яндекса (60% предпочтений в России)",
                age_restriction=13,
                requires_account=True,
                is_free=True
            ),
            AISite(
                id="gigachat",
                name="GigaChat",
                domain="gigachat.ru",
                category=AISiteCategory.TEXT_GENERATION,
                description="Российский AI чат-бот от Сбербанка (4% пользователей)",
                age_restriction=13,
                requires_account=True,
                is_free=True
            ),
            AISite(
                id="kandinsky",
                name="Kandinsky",
                domain="kandinsky.ai",
                category=AISiteCategory.IMAGE_GENERATION,
                description="Генерация изображений от Яндекса",
                age_restriction=13,
                requires_account=True,
                is_free=True
            ),
            AISite(
                id="shedevrum",
                name="Шедеврум",
                domain="shedevrum.ai",
                category=AISiteCategory.IMAGE_GENERATION,
                description="Российский сервис генерации изображений",
                age_restriction=13,
                requires_account=True,
                is_free=True
            ),
            # Международные AI-сервисы
            AISite(
                id="chatgpt",
                name="ChatGPT",
                domain="chat.openai.com",
                category=AISiteCategory.TEXT_GENERATION,
                description="AI чат-бот от OpenAI (3.5% пользователей в России)",
                age_restriction=13,
                requires_account=True,
                is_free=False
            ),
            AISite(
                id="deepseek",
                name="DeepSeek",
                domain="deepseek.com",
                category=AISiteCategory.TEXT_GENERATION,
                description="Китайский AI чат-бот (9.4% пользователей в России)",
                age_restriction=13,
                requires_account=True,
                is_free=True
            ),
            AISite(
                id="claude",
                name="Claude",
                domain="claude.ai",
                category=AISiteCategory.TEXT_GENERATION,
                description="AI ассистент от Anthropic",
                age_restriction=13,
                requires_account=True,
                is_free=False
            ),
            AISite(
                id="gemini",
                name="Google Gemini",
                domain="gemini.google.com",
                category=AISiteCategory.TEXT_GENERATION,
                description="AI ассистент от Google",
                age_restriction=13,
                requires_account=True,
                is_free=True
            ),
        ]

        return {site.id: site for site in sites}

    def get_ai_sites(self) -> List[Dict[str, Any]]:
        """
        Получить список всех AI-сайтов

        Returns:
            Список AI-сайтов в формате словарей
        """
        return [site.to_dict() for site in self.ai_sites.values()]

    def get_site_by_id(self, site_id: str) -> Optional[AISite]:
        """
        Получить информацию о сайте по ID

        Args:
            site_id: ID сайта

        Returns:
            AISite или None если не найден
        """
        return self.ai_sites.get(site_id)

    def block_sites(
        self,
        user_id: str,
        site_ids: List[str],
        time_restriction: Optional[TimeRestriction] = None
    ) -> Dict[str, Any]:
        """
        Заблокировать AI-сайты для пользователя

        Args:
            user_id: ID пользователя
            site_ids: Список ID сайтов для блокировки
            time_restriction: Ограничение по времени (опционально)

        Returns:
            Результат блокировки
        """
        if user_id not in self.user_site_status:
            self.user_site_status[user_id] = {}

        blocked = []
        not_found = []

        for site_id in site_ids:
            if site_id not in self.ai_sites:
                not_found.append(site_id)
                continue

            # Создаем или обновляем статус
            if site_id not in self.user_site_status[user_id]:
                self.user_site_status[user_id][site_id] = AISiteStatus(
                    site_id=site_id,
                    user_id=user_id,
                    is_blocked=True,
                    is_allowed=False,
                    time_restriction=time_restriction
                )
            else:
                status = self.user_site_status[user_id][site_id]
                status.is_blocked = True
                status.is_allowed = False
                status.time_restriction = time_restriction

            blocked.append(site_id)
            self.logger.info(f"🔒 Заблокирован сайт {site_id} для пользователя {user_id}")

        return {
            "status": "success",
            "blocked": blocked,
            "not_found": not_found,
            "total_blocked": len(blocked)
        }

    def allow_sites(
        self,
        user_id: str,
        site_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Разрешить доступ к AI-сайтам для пользователя

        Args:
            user_id: ID пользователя
            site_ids: Список ID сайтов для разрешения

        Returns:
            Результат разрешения
        """
        if user_id not in self.user_site_status:
            self.user_site_status[user_id] = {}

        allowed = []
        not_found = []

        for site_id in site_ids:
            if site_id not in self.ai_sites:
                not_found.append(site_id)
                continue

            # Создаем или обновляем статус
            if site_id not in self.user_site_status[user_id]:
                self.user_site_status[user_id][site_id] = AISiteStatus(
                    site_id=site_id,
                    user_id=user_id,
                    is_blocked=False,
                    is_allowed=True
                )
            else:
                status = self.user_site_status[user_id][site_id]
                status.is_blocked = False
                status.is_allowed = True
                status.time_restriction = None  # Убираем ограничение по времени

            allowed.append(site_id)
            self.logger.info(f"✅ Разрешен доступ к сайту {site_id} для пользователя {user_id}")

        return {
            "status": "success",
            "allowed": allowed,
            "not_found": not_found,
            "total_allowed": len(allowed)
        }

    def check_access(
        self,
        user_id: str,
        site_id: str,
        user_age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Проверить доступ пользователя к AI-сайту

        Args:
            user_id: ID пользователя
            site_id: ID сайта
            user_age: Возраст пользователя (опционально)

        Returns:
            Результат проверки доступа
        """
        # Проверяем существование сайта
        site = self.get_site_by_id(site_id)
        if not site:
            return {
                "allowed": False,
                "blocked": True,
                "reason": "site_not_found",
                "message": f"Сайт {site_id} не найден"
            }

        # Получаем статус для пользователя
        user_status = self.user_site_status.get(user_id, {})
        site_status = user_status.get(site_id)

        # Если статуса нет, используем настройки по умолчанию
        if not site_status:
            if self.default_block_all:
                return {
                    "allowed": False,
                    "blocked": True,
                    "reason": "default_block",
                    "message": "Все AI-сайты заблокированы по умолчанию"
                }
            else:
                # Проверяем только возраст
                if user_age and site.age_restriction:
                    if user_age < site.age_restriction:
                        return {
                            "allowed": False,
                            "blocked": True,
                            "reason": "age_restriction",
                            "message": f"Минимальный возраст для {site.name}: {site.age_restriction} лет"
                        }

                return {
                    "allowed": True,
                    "blocked": False,
                    "reason": "default_allow",
                    "message": "Доступ разрешен"
                }

        # Проверяем явную блокировку
        if site_status.is_blocked:
            # Проверяем ограничение по времени
            if site_status.time_restriction and site_status.time_restriction.enabled:
                if self._is_time_allowed(site_status.time_restriction):
                    # В разрешенное время - доступ открыт
                    return {
                        "allowed": True,
                        "blocked": False,
                        "reason": "time_allowed",
                        "message": "Доступ разрешен в это время"
                    }
                else:
                    # В запрещенное время - блокируем
                    reason = f"Доступ запрещен в это время. Разрешенное время: {site_status.time_restriction.start_time} - {site_status.time_restriction.end_time}"
                    self._record_access_attempt(user_id, site_id, blocked=True, reason=reason)
                    return {
                        "allowed": False,
                        "blocked": True,
                        "reason": "time_restriction",
                        "message": reason
                    }

            # Блокировка без ограничения по времени
            reason = f"Сайт {site.name} заблокирован"
            self._record_access_attempt(user_id, site_id, blocked=True, reason=reason)
            return {
                "allowed": False,
                "blocked": True,
                "reason": "blocked",
                "message": reason
            }

        # Проверяем явное разрешение
        if site_status.is_allowed:
            # Проверяем ограничение по возрасту
            if user_age and site.age_restriction:
                if user_age < site.age_restriction:
                    reason = f"Минимальный возраст для {site.name}: {site.age_restriction} лет"
                    self._record_access_attempt(user_id, site_id, blocked=True, reason=reason)
                    return {
                        "allowed": False,
                        "blocked": True,
                        "reason": "age_restriction",
                        "message": reason
                    }

            # Доступ разрешен
            self._record_access_attempt(user_id, site_id, blocked=False)
            return {
                "allowed": True,
                "blocked": False,
                "reason": "allowed",
                "message": "Доступ разрешен"
            }

        # По умолчанию разрешаем (если нет явных настроек)
        self._record_access_attempt(user_id, site_id, blocked=False)
        return {
            "allowed": True,
            "blocked": False,
            "reason": "default",
            "message": "Доступ разрешен"
        }

    def _is_time_allowed(self, time_restriction: TimeRestriction) -> bool:
        """
        Проверить, разрешено ли время доступа

        Args:
            time_restriction: Ограничение по времени

        Returns:
            True если время разрешено, False иначе
        """
        if not time_restriction.enabled:
            return True

        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()  # 0=понедельник, 6=воскресенье

        # Проверяем день недели
        if current_day not in time_restriction.days_of_week:
            return False

        # Парсим время начала и конца
        try:
            start = datetime.strptime(time_restriction.start_time, "%H:%M").time()
            end = datetime.strptime(time_restriction.end_time, "%H:%M").time()
        except ValueError:
            self.logger.error(f"Неверный формат времени: {time_restriction.start_time} или {time_restriction.end_time}")
            return True  # В случае ошибки разрешаем доступ

        # Проверяем, находится ли текущее время в разрешенном диапазоне
        return start <= current_time <= end

    def _record_access_attempt(
        self,
        user_id: str,
        site_id: str,
        blocked: bool,
        reason: Optional[str] = None
    ):
        """
        Записать попытку доступа

        Args:
            user_id: ID пользователя
            site_id: ID сайта
            blocked: Была ли попытка заблокирована
            reason: Причина блокировки (если была)
        """
        if user_id not in self.access_history:
            self.access_history[user_id] = []

        attempt = AccessAttempt(
            id=f"{user_id}_{site_id}_{int(time.time())}",
            user_id=user_id,
            site_id=site_id,
            timestamp=datetime.now().isoformat(),
            was_blocked=blocked,
            reason=reason
        )

        self.access_history[user_id].append(attempt)

        # Обновляем счетчики в статусе
        if user_id in self.user_site_status and site_id in self.user_site_status[user_id]:
            status = self.user_site_status[user_id][site_id]
            if blocked:
                status.blocked_count += 1
            else:
                status.access_count += 1
            status.last_access_attempt = attempt.timestamp

        # Отправляем уведомление родителям если попытка была заблокирована
        if blocked and self.notify_parents:
            self._notify_parents(user_id, site_id, reason)

    def _notify_parents(self, user_id: str, site_id: str, reason: Optional[str] = None):
        """
        Отправить уведомление родителям о попытке доступа

        Args:
            user_id: ID пользователя
            site_id: ID сайта
            reason: Причина блокировки
        """
        site = self.get_site_by_id(site_id)
        site_name = site.name if site else site_id

        # Создаем событие для ThreatEventBus
        if self.event_bus:
            try:
                event = ThreatEvent(
                    event_id=f"ai_access_blocked_{user_id}_{site_id}_{int(time.time())}",
                    agent_name="ai_categories_agent",
                    threat_type="ai_access_blocked",
                    severity="low",
                    source=user_id,
                    target=site_id,
                    timestamp=datetime.now().isoformat(),
                    description=f"Попытка доступа к заблокированному AI-сайту {site_name}",
                    metadata={
                        "site_id": site_id,
                        "site_name": site_name,
                        "reason": reason
                    }
                )
                self.event_bus.publish(event)
                self.logger.info(f"📧 Уведомление родителям отправлено: {user_id} пытался получить доступ к {site_name}")
            except Exception as e:
                self.logger.error(f"Ошибка при отправке уведомления родителям: {e}")
        else:
            self.logger.warning("ThreatEventBus недоступен, уведомление не отправлено")

    def get_status(self, user_id: str) -> Dict[str, Any]:
        """
        Получить статус всех AI-сайтов для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Статус всех сайтов
        """
        user_status = self.user_site_status.get(user_id, {})

        sites_status = []
        for site_id, site in self.ai_sites.items():
            site_status = user_status.get(site_id)
            if site_status:
                sites_status.append(site_status.to_dict())
            else:
                # Создаем статус по умолчанию
                default_status = AISiteStatus(
                    site_id=site_id,
                    user_id=user_id,
                    is_blocked=self.default_block_all,
                    is_allowed=not self.default_block_all
                )
                sites_status.append(default_status.to_dict())

        return {
            "user_id": user_id,
            "sites": sites_status,
            "total_sites": len(self.ai_sites),
            "blocked_count": sum(1 for s in sites_status if s.get("is_blocked", False)),
            "allowed_count": sum(1 for s in sites_status if s.get("is_allowed", False))
        }

    def get_access_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Получить историю попыток доступа

        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей

        Returns:
            Список попыток доступа
        """
        history = self.access_history.get(user_id, [])
        # Сортируем по времени (новые первыми) и ограничиваем
        sorted_history = sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]
        return [attempt.to_dict() for attempt in sorted_history]

    def set_age_restriction(
        self,
        user_id: str,
        site_id: str,
        age_restriction: AgeRestriction
    ) -> Dict[str, Any]:
        """
        Установить ограничение по возрасту для сайта

        Args:
            user_id: ID пользователя
            site_id: ID сайта
            age_restriction: Ограничение по возрасту

        Returns:
            Результат установки ограничения
        """
        if site_id not in self.ai_sites:
            return {
                "status": "error",
                "message": f"Сайт {site_id} не найден"
            }

        if user_id not in self.user_site_status:
            self.user_site_status[user_id] = {}

        if site_id not in self.user_site_status[user_id]:
            self.user_site_status[user_id][site_id] = AISiteStatus(
                site_id=site_id,
                user_id=user_id,
                is_blocked=False,
                is_allowed=False
            )

        self.user_site_status[user_id][site_id].age_restriction = age_restriction
        self.logger.info(f"🔒 Установлено ограничение по возрасту для {site_id}: минимум {age_restriction.min_age} лет")

        return {
            "status": "success",
            "message": f"Ограничение по возрасту установлено для {site_id}"
        }

    # MARK: - ThreatMonitoringInterface методы

    def collect_threats(self) -> List[Dict[str, Any]]:
        """
        Сбор угроз (ThreatMonitoringInterface)
        
        Returns:
            Список угроз (попытки доступа к заблокированным AI-сайтам)
        """
        threats = []
        
        for user_id, history in self.access_history.items():
            for attempt in history:
                if attempt.was_blocked:
                    threats.append({
                        "event_id": attempt.id,
                        "agent_name": "ai_categories_agent",
                        "threat_type": "ai_access_blocked",
                        "severity": "low",
                        "source": user_id,
                        "target": attempt.site_id,
                        "timestamp": attempt.timestamp,
                        "description": f"Попытка доступа к заблокированному AI-сайту: {attempt.reason}",
                        "metadata": {
                            "site_id": attempt.site_id,
                            "reason": attempt.reason
                        }
                    })
        
        return threats

    def analyze_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Анализ угроз (ThreatMonitoringInterface)
        
        Args:
            threats: Список угроз для анализа
            
        Returns:
            Список проанализированных угроз
        """
        analyzed = []
        
        for threat in threats:
            # Добавляем рекомендации
            threat["recommendations"] = [
                "Проверьте настройки родительского контроля",
                "Убедитесь что ограничения по возрасту настроены правильно"
            ]
            analyzed.append(threat)
        
        return analyzed

    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Отправка уведомления (ThreatMonitoringInterface)
        
        Args:
            alert: Словарь с информацией об уведомлении
            
        Returns:
            True если уведомление отправлено успешно
        """
        try:
            if self.event_bus:
                event = ThreatEvent(
                    event_id=alert.get("event_id", f"ai_alert_{int(time.time())}"),
                    agent_name="ai_categories_agent",
                    threat_type=alert.get("threat_type", "ai_access_blocked"),
                    severity=alert.get("severity", "low"),
                    source=alert.get("source", ""),
                    target=alert.get("target", ""),
                    timestamp=alert.get("timestamp", datetime.now().isoformat()),
                    description=alert.get("description", ""),
                    metadata=alert.get("metadata", {})
                )
                self.event_bus.publish(event)
                self.logger.info(f"📧 Уведомление отправлено: {alert.get('description', '')}")
                return True
            else:
                self.logger.warning("ThreatEventBus недоступен, уведомление не отправлено")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка при отправке уведомления: {e}")
            return False


# Для локального тестирования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Создаем агента
    agent = AICategoriesAgent()

    # Тестируем получение списка сайтов
    print("📋 Список AI-сайтов:")
    sites = agent.get_ai_sites()
    for site in sites:
        print(f"  - {site['name']} ({site['id']}): {site['category']}")

    # Тестируем блокировку
    print("\n🔒 Тест блокировки:")
    result = agent.block_sites("user123", ["chatgpt", "midjourney"])
    print(f"  Результат: {result}")

    # Тестируем проверку доступа
    print("\n🔍 Тест проверки доступа:")
    access_result = agent.check_access("user123", "chatgpt", user_age=15)
    print(f"  Результат: {access_result}")

    # Тестируем получение статуса
    print("\n📊 Тест получения статуса:")
    status = agent.get_status("user123")
    print(f"  Заблокировано: {status['blocked_count']}")
    print(f"  Разрешено: {status['allowed_count']}")

    print("\n✅ Тестирование завершено")
