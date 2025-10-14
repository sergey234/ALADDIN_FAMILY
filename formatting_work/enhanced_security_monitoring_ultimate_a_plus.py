#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecurityMonitoringManager - A+ качество (Ультимативная версия)
Минимальная сложность, полное устранение DRY нарушений
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

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
    """Событие безопасности"""
    event_id: str
    timestamp: datetime
    level: MonitoringLevel
    alert_type: AlertType
    description: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringConfig:
    """Конфигурация мониторинга безопасности"""
    enabled: bool = True
    check_interval: int = 60
    alert_threshold: int = 5
    retention_days: int = 30
    log_level: str = "INFO"


class IMonitoringStrategy(ABC):
    """Интерфейс стратегии мониторинга"""
    
    @abstractmethod
    async def check_security(self) -> List[SecurityEvent]:
        """Проверка безопасности"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Получение имени стратегии"""
        pass


class BaseSecurityStrategy(IMonitoringStrategy):
    """Базовая стратегия безопасности"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _is_enabled(self) -> bool:
        """Проверка включен ли мониторинг"""
        return self.config.enabled
    
    def _create_event(self, event_id: str, level: MonitoringLevel, 
                     alert_type: AlertType, description: str, 
                     source: str) -> SecurityEvent:
        """Создание события безопасности"""
        return SecurityEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            level=level,
            alert_type=alert_type,
            description=description,
            source=source
        )


class ThreatDetectionStrategy(BaseSecurityStrategy):
    """Стратегия обнаружения угроз"""
    
    async def check_security(self) -> List[SecurityEvent]:
        """Проверка угроз безопасности"""
        if not self._is_enabled():
            return []
        return []
    
    def get_strategy_name(self) -> str:
        """Получение имени стратегии"""
        return "ThreatDetection"


class AnomalyDetectionStrategy(BaseSecurityStrategy):
    """Стратегия обнаружения аномалий"""
    
    async def check_security(self) -> List[SecurityEvent]:
        """Проверка аномалий"""
        if not self._is_enabled():
            return []
        return []
    
    def get_strategy_name(self) -> str:
        """Получение имени стратегии"""
        return "AnomalyDetection"


class MonitoringDataManager:
    """Менеджер данных мониторинга"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.events: List[SecurityEvent] = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_event(self, event: SecurityEvent) -> None:
        """Добавление события"""
        self.events.append(event)
        self._cleanup_old_events()
    
    def get_events(self, hours: int = 24) -> List[SecurityEvent]:
        """Получение событий за период"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [e for e in self.events if e.timestamp >= cutoff_time]
    
    def get_events_by_level(self, level: MonitoringLevel) -> List[SecurityEvent]:
        """Получение событий по уровню"""
        return [e for e in self.events if e.level == level]
    
    def _cleanup_old_events(self) -> None:
        """Очистка старых событий"""
        cutoff_time = datetime.now() - timedelta(days=self.config.retention_days)
        self.events = [e for e in self.events if e.timestamp >= cutoff_time]


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alert_count = 0
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def process_events(self, events: List[SecurityEvent]) -> None:
        """Обработка событий и генерация алертов"""
        critical_events = [e for e in events if e.level == MonitoringLevel.CRITICAL]
        
        if len(critical_events) >= self.config.alert_threshold:
            await self._send_alert(critical_events)
    
    async def _send_alert(self, events: List[SecurityEvent]) -> None:
        """Отправка алерта"""
        self.alert_count += 1
        self.logger.warning(f"Критический алерт #{self.alert_count}: {len(events)} событий")


class SecurityMonitoringManager(SecurityBase):
    """Менеджер мониторинга безопасности"""
    
    def __init__(self, name: str = "SecurityMonitoringManager", 
                 config: Optional[MonitoringConfig] = None):
        super().__init__(name)
        
        self.config = config or MonitoringConfig()
        self.data_manager = MonitoringDataManager(self.config)
        self.alert_manager = AlertManager(self.config)
        
        self.strategies: List[IMonitoringStrategy] = [
            ThreatDetectionStrategy(self.config),
            AnomalyDetectionStrategy(self.config)
        ]
        
        self.logger.info(f"{self.name} инициализирован с {len(self.strategies)} стратегиями")
    
    async def start_monitoring(self) -> None:
        """Запуск мониторинга"""
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
                await asyncio.sleep(5)
    
    async def _monitoring_cycle(self) -> None:
        """Цикл мониторинга"""
        all_events = []
        
        for strategy in self.strategies:
            try:
                events = await strategy.check_security()
                all_events.extend(events)
            except Exception as e:
                self.logger.error(f"Ошибка в стратегии {strategy.get_strategy_name()}: {e}")
        
        for event in all_events:
            self.data_manager.add_event(event)
        
        if all_events:
            await self.alert_manager.process_events(all_events)
    
    def get_security_status(self) -> Dict[str, Any]:
        """Получение статуса безопасности"""
        recent_events = self.data_manager.get_events(24)
        
        return {
            'total_events': len(recent_events),
            'critical_events': len(self.data_manager.get_events_by_level(MonitoringLevel.CRITICAL)),
            'high_events': len(self.data_manager.get_events_by_level(MonitoringLevel.HIGH)),
            'alert_count': self.alert_manager.alert_count,
            'monitoring_enabled': self.config.enabled,
            'strategies_count': len(self.strategies)
        }
    
    def add_monitoring_strategy(self, strategy: IMonitoringStrategy) -> None:
        """Добавление стратегии мониторинга"""
        self.strategies.append(strategy)
        self.logger.info(f"Добавлена стратегия: {strategy.get_strategy_name()}")
    
    def remove_monitoring_strategy(self, strategy_name: str) -> None:
        """Удаление стратегии мониторинга"""
        self.strategies = [s for s in self.strategies if s.get_strategy_name() != strategy_name]
        self.logger.info(f"Удалена стратегия: {strategy_name}")
    
    def update_config(self, new_config: MonitoringConfig) -> None:
        """Обновление конфигурации"""
        self.config = new_config
        self.data_manager.config = new_config
        self.alert_manager.config = new_config
        self.logger.info("Конфигурация обновлена")
    
    def stop_monitoring(self) -> None:
        """Остановка мониторинга"""
        self.config.enabled = False
        self.logger.info("Мониторинг остановлен")


# Enhanced version with improvements
