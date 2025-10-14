# -*- coding: utf-8 -*-
"""
ParentalControlBot v2.5 - Модульная архитектура
Версия: 2.5
Дата: 2025-09-21
Лицензия: MIT
"""

import logging
import structlog
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import threading
import time

# Внутренние импорты
from core.security_base import SecurityBase
from security.bots.parental_control_bot import (
    ChildProfile, ContentAnalysisResult, ActivityAlert,
    AlertData,
    validate_child_data, validate_content_request
)

# Компоненты
from security.bots.components.child_profile_manager import ChildProfileManager
from security.bots.components.content_analyzer import ContentAnalyzer
from security.bots.components.time_monitor import TimeMonitor
from security.bots.components.notification_service import NotificationService


class ParentalControlBotV2(SecurityBase):
    """
    Бот родительского контроля версии 2.5 с модульной архитектурой

    Основные компоненты:
    - ChildProfileManager: Управление профилями детей
    - ContentAnalyzer: Анализ контента
    - TimeMonitor: Мониторинг времени использования
    - NotificationService: Сервис уведомлений
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация бота родительского контроля

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///parental_control_bot_v2.db",
            "content_analysis_enabled": True,
            "location_tracking_enabled": True,
            "social_media_monitoring": True,
            "educational_recommendations": True,
            "ml_enabled": True,
            "adaptive_learning": True,
            "real_time_monitoring": True,
            "bedtime_mode": True,
            "emergency_alerts": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_enabled": True,
            "log_level": "INFO",
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self._setup_enhanced_logging()

        self.profile_manager = ChildProfileManager(self.logger)
        self.content_analyzer = ContentAnalyzer(self.logger)
        self.time_monitor = TimeMonitor(self.logger)
        self.notification_service = NotificationService(self.logger)

        # Статистика
        self.stats = {
            "total_children": 0,
            "active_children": 0,
            "content_blocks": 0,
            "time_violations": 0,
            "suspicious_activities": 0,
            "educational_recommendations": 0,
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(f"ParentalControlBotV2 {name} инициализирован с модульной архитектурой")

    def _setup_enhanced_logging(self) -> None:
        """Настройка улучшенного логирования с контекстом"""
        try:
            # Настройка structlog
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

            # Создание контекстного логгера
            self.context_logger = structlog.get_logger().bind(
                component="parental_control_bot_v2",
                bot_name=self.name,
                version="2.5"
            )

            # Настройка уровней логирования
            log_level = self.config.get("log_level", "INFO")
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

        except Exception as e:
            # Fallback к стандартному логированию
            self.context_logger = self.logger
            self.logger.warning(f"Не удалось настроить enhanced logging: {e}")

    def _log_with_context(self, level: str, message: str, **kwargs) -> None:
        """Логирование с контекстом"""
        try:
            log_method = getattr(self.context_logger, level.lower())
            log_method(message, **kwargs)
        except Exception:
            # Fallback к стандартному логированию
            getattr(self.logger, level.lower())(f"{message} | Context: {kwargs}")

    def _log_error_with_context(self, error: Exception, context: str, **kwargs) -> None:
        """Логирование ошибок с контекстом"""
        try:
            self.context_logger.error(
                f"Ошибка в {context}: {str(error)}",
                error_type=type(error).__name__,
                error_message=str(error),
                context=context,
                **kwargs,
                exc_info=True
            )
        except Exception:
            self.logger.error(f"Ошибка в {context}: {error} | Context: {kwargs}", exc_info=True)

    async def start(self) -> bool:
        """Запуск бота родительского контроля"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("ParentalControlBotV2 уже запущен")
                    return True

                # Запуск мониторинга
                self.running = True
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_worker
                )
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

                self.logger.info("ParentalControlBotV2 запущен успешно")
                return True

        except Exception as e:
            self._log_error_with_context(
                e, "start",
                operation="bot_startup",
                config_keys=list(self.config.keys())
            )
            return False

    async def stop(self) -> bool:
        """Остановка бота родительского контроля"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("ParentalControlBotV2 уже остановлен")
                    return True

                self.running = False

                # Ожидание завершения потоков
                if self.monitoring_thread and self.monitoring_thread.is_alive():
                    self.monitoring_thread.join(timeout=5)

                self.logger.info("ParentalControlBotV2 остановлен")
                return True

        except Exception as e:
            self._log_error_with_context(e, "stop", operation="bot_shutdown")
            return False

    # ==================== МЕТОДЫ УПРАВЛЕНИЯ ПРОФИЛЯМИ ====================

    async def add_child_profile(self, child_data: Dict[str, Any]) -> str:
        """Добавление профиля ребенка"""
        try:
            child_id = await self.profile_manager.add_profile(child_data)

            # Обновление статистики
            self.stats["total_children"] += 1
            self.stats["active_children"] += 1

            self._log_with_context(
                "info", "Профиль ребенка добавлен",
                child_id=child_id,
                operation="add_child_profile"
            )
            return child_id

        except Exception as e:
            self._log_error_with_context(
                e, "add_child_profile",
                child_data_keys=list(child_data.keys()) if child_data else [],
                operation="add_child_profile"
            )
            raise

    async def get_child_profile(self, child_id: str) -> Optional[ChildProfile]:
        """Получение профиля ребенка"""
        return await self.profile_manager.get_profile(child_id)

    async def update_child_profile(self, child_id: str, updates: Dict[str, Any]) -> bool:
        """Обновление профиля ребенка"""
        return await self.profile_manager.update_profile(child_id, updates)

    async def delete_child_profile(self, child_id: str) -> bool:
        """Удаление профиля ребенка"""
        success = await self.profile_manager.delete_profile(child_id)
        if success:
            self.stats["active_children"] = max(0, self.stats["active_children"] - 1)
        return success

    async def get_all_profiles(self) -> Dict[str, ChildProfile]:
        """Получение всех профилей"""
        return await self.profile_manager.get_all_profiles()

    # ==================== МЕТОДЫ АНАЛИЗА КОНТЕНТА ====================

    async def analyze_content(self, url: str, child_id: str) -> ContentAnalysisResult:
        """Анализ контента для ребенка"""
        try:
            # Получение профиля для определения возраста
            profile = await self.profile_manager.get_profile(child_id)
            child_age = profile.age if profile else 10

            result = await self.content_analyzer.analyze_content(url, child_id, child_age)

            # Обновление статистики
            if result.action.value == "block":
                self.stats["content_blocks"] += 1

            return result

        except Exception as e:
            self._log_error_with_context(
                e, "analyze_content",
                url=url, child_id=child_id,
                operation="analyze_content"
            )
            raise

    # ==================== МЕТОДЫ МОНИТОРИНГА ВРЕМЕНИ ====================

    async def start_device_session(self, child_id: str, device_type: str) -> bool:
        """Начало сессии использования устройства"""
        return await self.time_monitor.start_session(child_id, device_type)

    async def end_device_session(self, child_id: str, device_type: str) -> Optional[int]:
        """Завершение сессии использования устройства"""
        return await self.time_monitor.end_session(child_id, device_type)

    async def set_time_limit(self, child_id: str, device_type: str, minutes: int) -> bool:
        """Установка лимита времени"""
        success = await self.time_monitor.set_time_limit(child_id, device_type, minutes)
        if success:
            self._log_with_context(
                "info", "Лимит времени установлен",
                child_id=child_id, device_type=device_type, minutes=minutes,
                operation="set_time_limit"
            )
        return success

    async def check_time_violation(self, child_id: str, device_type: str) -> Optional[ActivityAlert]:
        """Проверка нарушения лимита времени"""
        alert = await self.time_monitor.check_time_violation(child_id, device_type)
        if alert:
            # Отправка уведомления
            await self.notification_service.send_alert(alert)
            self.stats["time_violations"] += 1
        return alert

    async def get_usage_report(self, child_id: str) -> Dict[str, Any]:
        """Получение отчета об использовании"""
        return await self.time_monitor.get_usage_report(child_id)

    # ==================== МЕТОДЫ УВЕДОМЛЕНИЙ ====================

    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Отправка алерта"""
        try:
            # Валидация данных
            validated_data = AlertData(**alert_data)

            # Создание алерта
            alert = ActivityAlert(
                child_id=validated_data.child_id,
                alert_type=validated_data.alert_type,
                severity=validated_data.severity,
                message=validated_data.message,
                timestamp=datetime.now(),
                action_required=validated_data.severity in ['high', 'critical'],
                data=validated_data.data,
            )

            # Отправка уведомления
            return await self.notification_service.send_alert(alert)

        except Exception as e:
            self._log_error_with_context(
                e, "send_alert",
                alert_data_keys=list(alert_data.keys()) if alert_data else [],
                operation="send_alert"
            )
            return False

    # ==================== МЕТОДЫ СТАТУСА ====================

    async def get_child_status(self, child_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса ребенка"""
        try:
            profile = await self.profile_manager.get_profile(child_id)
            if not profile:
                return None

            # Получение дневной статистики
            daily_usage = await self.time_monitor.get_daily_usage(child_id)

            return {
                "child_id": child_id,
                "name": profile.name,
                "age": profile.age,
                "age_group": profile.age_group,
                "is_monitored": True,  # Всегда активно в v2
                "daily_usage": daily_usage,
                "time_limits": profile.time_limits or {},
                "restrictions": profile.restrictions or {},
                "safe_zones": profile.safe_zones or [],
                "last_update": (
                    profile.updated_at.isoformat()
                    if profile.updated_at else None
                ),
            }

        except Exception as e:
            self._log_error_with_context(e, "get_child_status", child_id=child_id)
            return None

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            # Получение статистики от компонентов
            profile_stats = await self.profile_manager.get_stats()
            analysis_stats = await self.content_analyzer.get_stats()
            time_stats = await self.time_monitor.get_stats()
            notification_stats = await self.notification_service.get_stats()

            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "version": "2.5",
                "architecture": "modular",
                "config": self.config,
                "stats": self.stats,
                "component_stats": {
                    "profiles": {
                        "total": profile_stats.total_profiles,
                        "active": profile_stats.active_profiles,
                        "by_age_group": profile_stats.profiles_by_age_group
                    },
                    "content_analysis": {
                        "total_analyses": analysis_stats.total_analyses,
                        "blocks_by_category": analysis_stats.blocks_by_category,
                        "average_risk_score": analysis_stats.average_risk_score
                    },
                    "time_monitoring": {
                        "total_usage_minutes": time_stats.total_usage_minutes,
                        "violations_count": time_stats.violations_count
                    },
                    "notifications": {
                        "total_sent": notification_stats.total_sent,
                        "sent_by_channel": notification_stats.sent_by_channel,
                        "failed_deliveries": notification_stats.failed_deliveries
                    }
                },
                "last_update": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self._log_error_with_context(e, "get_status")
            return {"error": str(e)}

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def _monitoring_worker(self):
        """Рабочий поток мониторинга"""
        while self.running:
            try:
                # Здесь можно добавить периодические проверки
                time.sleep(60)  # Проверка каждую минуту
            except Exception as e:
                self.logger.error(f"Ошибка в мониторинге: {e}")

    # ==================== ВАЛИДАЦИОННЫЕ МЕТОДЫ ====================

    def validate_child_data(self, child_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Валидация данных ребенка"""
        return validate_child_data(child_data)

    def validate_content_request(self, url: str, child_id: str) -> Tuple[bool, Optional[str]]:
        """Валидация запроса анализа контента"""
        return validate_content_request(url, child_id)

    async def validate_time_limit_data(self, device_type: str, minutes: int) -> Tuple[bool, Optional[str]]:
        """Валидация данных лимита времени"""
        return await self.time_monitor.validate_time_limit_data(device_type, minutes)

    async def validate_alert_data(self, alert_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Валидация данных алерта"""
        return await self.notification_service.validate_alert_data(alert_data)

    # ==================== МЕТОДЫ ПОИСКА ====================

    async def search_profiles(self, query: str) -> List[ChildProfile]:
        """Поиск профилей"""
        return await self.profile_manager.search_profiles(query)

    async def get_profiles_by_parent(self, parent_id: str) -> List[ChildProfile]:
        """Получение профилей по родителю"""
        return await self.profile_manager.get_profiles_by_parent(parent_id)

    async def get_profiles_by_age_group(self, age_group: str) -> List[ChildProfile]:
        """Получение профилей по возрастной группе"""
        return await self.profile_manager.get_profiles_by_age_group(age_group)

    # ==================== МЕТОДЫ КОНФИГУРАЦИИ ====================

    async def add_custom_content_pattern(self, category: str, pattern: str):
        """Добавление пользовательского паттерна контента"""
        from security.bots.parental_control_bot import ContentCategory
        category_enum = ContentCategory(category)
        await self.content_analyzer.add_custom_pattern(category_enum, pattern)

    async def add_custom_notification_template(self, template_data: Dict[str, Any]):
        """Добавление пользовательского шаблона уведомлений"""
        from security.bots.components.notification_service import (
            NotificationTemplate, NotificationChannel, NotificationPriority
        )

        template = NotificationTemplate(
            template_id=template_data["template_id"],
            subject=template_data["subject"],
            message=template_data["message"],
            channel=NotificationChannel(template_data["channel"]),
            priority=NotificationPriority(template_data["priority"]),
            variables=template_data.get("variables", [])
        )

        return await self.notification_service.add_template(template)

    async def get_notification_history(self, child_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение истории уведомлений"""
        return await self.notification_service.get_notification_history(child_id, limit)
