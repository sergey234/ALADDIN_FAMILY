#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Общий интерфейс для мониторинга угроз

Этот модуль определяет общий интерфейс для всех агентов мониторинга угроз,
позволяя им обмениваться данными и синхронизировать информацию.

Дата создания: 9 декабря 2025
Версия: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ThreatEvent:
    """Событие угрозы для обмена между агентами"""
    event_id: str
    agent_name: str
    threat_type: str  # "breach", "malware", "phishing", "suspicious_activity"
    severity: str  # "low", "medium", "high", "critical"
    source: str  # Источник угрозы
    target: str  # Цель (email, domain, IP, etc.)
    timestamp: str
    metadata: Dict[str, Any]
    description: Optional[str] = None


class ThreatMonitoringInterface(ABC):
    """
    Общий интерфейс для мониторинга угроз

    Все агенты мониторинга должны реализовывать этот интерфейс
    для обеспечения совместимости и обмена данными.
    """

    @abstractmethod
    def collect_threats(self) -> List[Dict[str, Any]]:
        """
        Сбор угроз из всех доступных источников

        Returns:
            Список словарей с информацией об угрозах
        """
        raise NotImplementedError

    @abstractmethod
    def analyze_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Анализ собранных угроз

        Args:
            threats: Список угроз для анализа

        Returns:
            Список проанализированных угроз с дополнительной информацией
        """
        raise NotImplementedError

    @abstractmethod
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Отправка уведомления об угрозе

        Args:
            alert: Словарь с информацией об уведомлении

        Returns:
            True если уведомление отправлено успешно, False иначе
        """
        raise NotImplementedError

    def share_threat_event(self, event: ThreatEvent) -> bool:
        """
        Обмен информацией об угрозе с другими агентами

        Args:
            event: Событие угрозы

        Returns:
            True если событие успешно передано
        """
        # Базовая реализация - может быть переопределена
        return True

    def receive_threat_event(self, event: ThreatEvent) -> bool:
        """
        Получение информации об угрозе от другого агента

        Args:
            event: Событие угрозы от другого агента

        Returns:
            True если событие успешно обработано
        """
        # Базовая реализация - может быть переопределена
        return True


class ThreatEventBus:
    """
    Шина событий для обмена информацией между агентами мониторинга

    Паттерн Observer/Publisher-Subscriber для синхронизации информации
    """

    def __init__(self):
        self.subscribers: Dict[str, List[ThreatMonitoringInterface]] = {}
        self.event_history: List[ThreatEvent] = []
        self.max_history_size = 1000

    def subscribe(self, agent: ThreatMonitoringInterface, event_types: Optional[List[str]] = None):
        """
        Подписка агента на события

        Args:
            agent: Агент для подписки
            event_types: Типы событий для подписки (None = все типы)
        """
        if event_types is None:
            event_types = ["*"]  # Подписка на все события

        for event_type in event_types:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []

            if agent not in self.subscribers[event_type]:
                self.subscribers[event_type].append(agent)

    def unsubscribe(self, agent: ThreatMonitoringInterface, event_types: Optional[List[str]] = None):
        """
        Отписка агента от событий

        Args:
            agent: Агент для отписки
            event_types: Типы событий для отписки (None = все типы)
        """
        if event_types is None:
            event_types = list(self.subscribers.keys())

        for event_type in event_types:
            if event_type in self.subscribers:
                if agent in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(agent)

    def publish(self, event: ThreatEvent) -> int:
        """
        Публикация события для всех подписчиков

        Args:
            event: Событие для публикации

        Returns:
            Количество агентов, получивших событие
        """
        notified_count = 0

        # Добавляем событие в историю
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)  # Удаляем самое старое событие

        # Уведомляем подписчиков на конкретный тип события
        if event.threat_type in self.subscribers:
            for agent in self.subscribers[event.threat_type]:
                try:
                    if agent.receive_threat_event(event):
                        notified_count += 1
                except Exception as e:
                    # Логируем ошибку, но не прерываем процесс
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Ошибка при уведомлении агента {agent.__class__.__name__}: {e}")

        # Уведомляем подписчиков на все события
        if "*" in self.subscribers:
            for agent in self.subscribers["*"]:
                try:
                    if agent.receive_threat_event(event):
                        notified_count += 1
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Ошибка при уведомлении агента {agent.__class__.__name__}: {e}")

        return notified_count

    def get_event_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[ThreatEvent]:
        """
        Получение истории событий

        Args:
            event_type: Фильтр по типу события (None = все типы)
            limit: Максимальное количество событий

        Returns:
            Список событий
        """
        if event_type is None:
            return self.event_history[-limit:]
        else:
            filtered = [e for e in self.event_history if e.threat_type == event_type]
            return filtered[-limit:]

    def get_subscribers_count(self) -> Dict[str, int]:
        """
        Получение статистики подписчиков

        Returns:
            Словарь {тип_события: количество_подписчиков}
        """
        return {event_type: len(agents) for event_type, agents in self.subscribers.items()}


# Глобальный экземпляр шины событий
_threat_event_bus: Optional[ThreatEventBus] = None


def get_threat_event_bus() -> ThreatEventBus:
    """
    Получение глобального экземпляра шины событий

    Returns:
        Экземпляр ThreatEventBus
    """
    global _threat_event_bus
    if _threat_event_bus is None:
        _threat_event_bus = ThreatEventBus()
    return _threat_event_bus


def reset_threat_event_bus():
    """
    Сброс глобальной шины событий (для тестирования)
    """
    global _threat_event_bus
    _threat_event_bus = None
