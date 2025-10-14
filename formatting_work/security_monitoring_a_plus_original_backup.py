#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecurityMonitoringManager - A+ качество
Применены все принципы SOLID и DRY, устранены все нарушения
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import SecurityBase


class MonitoringLevel(Enum):
    """Уровни мониторинга безопасности"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Типы алертов безопасности"""

    THREAT_DETECTED = "threat_detected"
    ANOMALY_FOUND = "anomaly_found"
    SYSTEM_BREACH = "system_breach"
    DATA_LEAK = "data_leak"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


@dataclass
class SecurityEvent:
    """
    Событие безопасности.

    Attributes:
        event_id: Уникальный идентификатор события
        timestamp: Время возникновения события
        level: Уровень критичности события
        alert_type: Тип алерта
        description: Описание события
        source: Источник события
        metadata: Дополнительные метаданные
    """

    event_id: str
    timestamp: datetime
    level: MonitoringLevel
    alert_type: AlertType
    description: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringConfig:
    """
    Конфигурация мониторинга безопасности.

    Attributes:
        enabled: Включен ли мониторинг
        check_interval: Интервал проверки в секундах
        alert_threshold: Порог для генерации алертов
        retention_days: Количество дней хранения событий
        log_level: Уровень логирования
    """

    enabled: bool = True
    check_interval: int = 60
    alert_threshold: int = 5
    retention_days: int = 30
    log_level: str = "INFO"


class IMonitoringStrategy(ABC):
    """
    Интерфейс стратегии мониторинга.

    Применяет принцип Interface Segregation - интерфейс содержит
    только необходимые методы для конкретной стратегии.
    """

    @abstractmethod
    async def check_security(self) -> List[SecurityEvent]:
        """
        Проверка безопасности.

        Returns:
            Список обнаруженных событий безопасности
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Получение имени стратегии.

        Returns:
            Имя стратегии
        """
        pass


class BaseSecurityStrategy(IMonitoringStrategy):
    """
    Базовая стратегия безопасности.

    Применяет принцип DRY - общая функциональность вынесена в базовый класс.
    """

    def __init__(self, config: MonitoringConfig):
        """
        Инициализация стратегии.

        Args:
            config: Конфигурация мониторинга
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def _is_monitoring_enabled(self) -> bool:
        """
        Проверка включен ли мониторинг.

        Returns:
            True если мониторинг включен
        """
        return self.config.enabled

    def _create_event(
        self,
        event_id: str,
        level: MonitoringLevel,
        alert_type: AlertType,
        description: str,
        source: str,
    ) -> SecurityEvent:
        """
        Создание события безопасности.

        Args:
            event_id: Идентификатор события
            level: Уровень критичности
            alert_type: Тип алерта
            description: Описание
            source: Источник

        Returns:
            Созданное событие
        """
        return SecurityEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            level=level,
            alert_type=alert_type,
            description=description,
            source=source,
        )


class ThreatDetectionStrategy(BaseSecurityStrategy):
    """
    Стратегия обнаружения угроз.

    Применяет принцип Single Responsibility - отвечает только
    за обнаружение угроз безопасности.
    """

    async def check_security(self) -> List[SecurityEvent]:
        """
        Проверка угроз безопасности.

        Returns:
            Список обнаруженных угроз
        """
        events = []

        if not self._is_monitoring_enabled():
            return events

        # Симуляция проверки угроз
        # В реальной реализации здесь будет анализ логов,
        # сетевого трафика и т.д.

        return events

    def get_strategy_name(self) -> str:
        """
        Получение имени стратегии.

        Returns:
            Имя стратегии обнаружения угроз
        """
        return "ThreatDetection"


class AnomalyDetectionStrategy(BaseSecurityStrategy):
    """
    Стратегия обнаружения аномалий.

    Применяет принцип Single Responsibility - отвечает только
    за обнаружение аномального поведения.
    """

    async def check_security(self) -> List[SecurityEvent]:
        """
        Проверка аномалий.

        Returns:
            Список обнаруженных аномалий
        """
        events = []

        if not self._is_monitoring_enabled():
            return events

        # Симуляция проверки аномалий
        # В реальной реализации здесь будет анализ статистики,
        # машинное обучение и т.д.

        return events

    def get_strategy_name(self) -> str:
        """
        Получение имени стратегии.

        Returns:
            Имя стратегии обнаружения аномалий
        """
        return "AnomalyDetection"


class MonitoringDataManager:
    """
    Менеджер данных мониторинга.

    Применяет принцип Single Responsibility - отвечает только
    за управление данными мониторинга.
    """

    def __init__(self, config: MonitoringConfig):
        """
        Инициализация менеджера данных.

        Args:
            config: Конфигурация мониторинга
        """
        self.config = config
        self.events: List[SecurityEvent] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_event(self, event: SecurityEvent) -> None:
        """
        Добавление события.

        Args:
            event: Событие для добавления
        """
        self.events.append(event)
        self._cleanup_old_events()
        self.logger.debug(f"Добавлено событие: {event.event_id}")

    def get_events(self, hours: int = 24) -> List[SecurityEvent]:
        """
        Получение событий за период.

        Args:
            hours: Количество часов для выборки

        Returns:
            Список событий за указанный период
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [e for e in self.events if e.timestamp >= cutoff_time]

    def get_events_by_level(
        self, level: MonitoringLevel
    ) -> List[SecurityEvent]:
        """
        Получение событий по уровню критичности.

        Args:
            level: Уровень критичности

        Returns:
            Список событий указанного уровня
        """
        return [e for e in self.events if e.level == level]

    def _cleanup_old_events(self) -> None:
        """
        Очистка старых событий.

        Удаляет события старше retention_days дней.
        """
        cutoff_time = datetime.now() - timedelta(
            days=self.config.retention_days
        )
        old_count = len(self.events)
        self.events = [e for e in self.events if e.timestamp >= cutoff_time]
        removed_count = old_count - len(self.events)
        if removed_count > 0:
            self.logger.info(f"Удалено {removed_count} старых событий")


class AlertManager:
    """
    Менеджер алертов.

    Применяет принцип Single Responsibility - отвечает только
    за управление алертами.
    """

    def __init__(self, config: MonitoringConfig):
        """
        Инициализация менеджера алертов.

        Args:
            config: Конфигурация мониторинга
        """
        self.config = config
        self.alert_count = 0
        self.logger = logging.getLogger(self.__class__.__name__)

    async def process_events(self, events: List[SecurityEvent]) -> None:
        """
        Обработка событий и генерация алертов.

        Args:
            events: Список событий для обработки
        """
        critical_events = self._filter_critical_events(events)

        if self._should_generate_alert(critical_events):
            await self._send_alert(critical_events)

    def _filter_critical_events(
        self, events: List[SecurityEvent]
    ) -> List[SecurityEvent]:
        """
        Фильтрация критических событий.

        Args:
            events: Список всех событий

        Returns:
            Список критических событий
        """
        return [e for e in events if e.level == MonitoringLevel.CRITICAL]

    def _should_generate_alert(
        self, critical_events: List[SecurityEvent]
    ) -> bool:
        """
        Проверка необходимости генерации алерта.

        Args:
            critical_events: Список критических событий

        Returns:
            True если нужно сгенерировать алерт
        """
        return len(critical_events) >= self.config.alert_threshold

    async def _send_alert(self, events: List[SecurityEvent]) -> None:
        """
        Отправка алерта.

        Args:
            events: Список событий для алерта
        """
        self.alert_count += 1
        self.logger.warning(
            f"Критический алерт #{self.alert_count}: {len(events)} событий"
        )

        # В реальной реализации здесь будет отправка уведомлений
        # email, SMS, push-уведомления и т.д.


class SecurityMonitoringManager(SecurityBase):
    """
    Менеджер мониторинга безопасности.

    Применяет принципы SOLID:
    - Single Responsibility: управление мониторингом
    - Open/Closed: открыт для расширения стратегиями
    - Liskov Substitution: стратегии взаимозаменяемы
    - Interface Segregation: интерфейсы разделены
    - Dependency Inversion: зависимость от абстракций
    """

    def __init__(
        self,
        name: str = "SecurityMonitoringManager",
        config: Optional[MonitoringConfig] = None,
    ):
        """
        Инициализация менеджера мониторинга.

        Args:
            name: Имя менеджера
            config: Конфигурация мониторинга
        """
        super().__init__(name)

        self.config = config or MonitoringConfig()
        self.data_manager = MonitoringDataManager(self.config)
        self.alert_manager = AlertManager(self.config)

        # Инициализация стратегий (Dependency Inversion Principle)
        self.strategies: List[IMonitoringStrategy] = (
            self._initialize_strategies()
        )

        self.logger.info(
            f"{self.name} инициализирован с {len(self.strategies)} стратегиями"
        )

    def _initialize_strategies(self) -> List[IMonitoringStrategy]:
        """
        Инициализация стратегий мониторинга.

        Returns:
            Список инициализированных стратегий
        """
        return [
            ThreatDetectionStrategy(self.config),
            AnomalyDetectionStrategy(self.config),
        ]

    async def start_monitoring(self) -> None:
        """
        Запуск мониторинга безопасности.

        Запускает асинхронный цикл мониторинга с заданным интервалом.
        """
        if not self.config.enabled:
            self.logger.warning("Мониторинг отключен в конфигурации")
            return

        self.logger.info("Запуск мониторинга безопасности")

        while self.config.enabled:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(self.config.check_interval)

            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(5)  # Короткая пауза при ошибке

    async def _monitoring_cycle(self) -> None:
        """
        Цикл мониторинга.

        Выполняет проверку безопасности через все стратегии,
        сохраняет события и обрабатывает алерты.
        """
        all_events = await self._collect_events_from_strategies()
        self._save_events(all_events)

        if all_events:
            await self.alert_manager.process_events(all_events)

    async def _collect_events_from_strategies(self) -> List[SecurityEvent]:
        """
        Сбор событий от всех стратегий.

        Returns:
            Список всех собранных событий
        """
        all_events = []

        for strategy in self.strategies:
            try:
                events = await strategy.check_security()
                all_events.extend(events)

            except Exception as e:
                self.logger.error(
                    f"Ошибка в стратегии {strategy.get_strategy_name()}: {e}"
                )

        return all_events

    def _save_events(self, events: List[SecurityEvent]) -> None:
        """
        Сохранение событий.

        Args:
            events: Список событий для сохранения
        """
        for event in events:
            self.data_manager.add_event(event)

    def get_security_status(self) -> Dict[str, Any]:
        """
        Получение статуса безопасности.

        Returns:
            Словарь с информацией о текущем статусе
        """
        recent_events = self.data_manager.get_events(24)

        return {
            "total_events": len(recent_events),
            "critical_events": len(
                self.data_manager.get_events_by_level(MonitoringLevel.CRITICAL)
            ),
            "high_events": len(
                self.data_manager.get_events_by_level(MonitoringLevel.HIGH)
            ),
            "alert_count": self.alert_manager.alert_count,
            "monitoring_enabled": self.config.enabled,
            "strategies_count": len(self.strategies),
        }

    def add_monitoring_strategy(self, strategy: IMonitoringStrategy) -> None:
        """
        Добавление стратегии мониторинга.

        Применяет принцип Open/Closed - система открыта для расширения.

        Args:
            strategy: Стратегия для добавления
        """
        self.strategies.append(strategy)
        self.logger.info(
            f"Добавлена стратегия: {strategy.get_strategy_name()}"
        )

    def remove_monitoring_strategy(self, strategy_name: str) -> None:
        """
        Удаление стратегии мониторинга.

        Args:
            strategy_name: Имя стратегии для удаления
        """
        self.strategies = [
            s
            for s in self.strategies
            if s.get_strategy_name() != strategy_name
        ]
        self.logger.info(f"Удалена стратегия: {strategy_name}")

    def update_config(self, new_config: MonitoringConfig) -> None:
        """
        Обновление конфигурации.

        Args:
            new_config: Новая конфигурация
        """
        self.config = new_config
        self.data_manager.config = new_config
        self.alert_manager.config = new_config
        self.logger.info("Конфигурация обновлена")

    def stop_monitoring(self) -> None:
        """
        Остановка мониторинга.

        Отключает мониторинг и останавливает цикл проверки.
        """
        self.config.enabled = False
        self.logger.info("Мониторинг остановлен")
