#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер вызова служб экстренного реагирования
Применение Single Responsibility принципа
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from security.ai_agents.emergency_location_utils import LocationServiceFinder
from security.ai_agents.emergency_models import (
    EmergencyEvent,
    EmergencyResponse,
    EmergencyService,
)
from security.microservices.emergency_formatters import (
    EmergencyMessageFormatter,
)


class EmergencyServiceCaller:
    """
    Менеджер вызова служб экстренного реагирования

    Поддерживает синхронные и асинхронные операции для вызова экстренных служб.
    Включает валидацию параметров, обработку ошибок и расширенное логирование.

    Attributes:
        logger: Логгер для записи событий
        service_calls: Словарь активных вызовов служб
        emergency_services: Конфигурация доступных служб
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.service_calls: Dict[str, EmergencyResponse] = {}
        self.emergency_services = self._initialize_emergency_services()

    def _validate_emergency_event(self, event: EmergencyEvent) -> bool:
        """
        Валидация экстренного события

        Args:
            event: Экстренное событие для валидации

        Returns:
            bool: True если событие валидно, False иначе

        Raises:
            ValueError: Если событие невалидно
        """
        if not isinstance(event, EmergencyEvent):
            raise ValueError("event должен быть экземпляром EmergencyEvent")

        if not event.event_id or not isinstance(event.event_id, str):
            raise ValueError("event_id должен быть непустой строкой")

        if not event.emergency_type:
            raise ValueError("emergency_type обязателен")

        if not event.location or not isinstance(event.location, dict):
            raise ValueError("location должен быть словарем")

        coordinates = event.location.get("coordinates")
        if not coordinates:
            raise ValueError("coordinates обязательны в location")

        if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 2:
            raise ValueError(
                "coordinates должны быть списком или кортежем из 2 элементов"
            )

        try:
            lat, lon = float(coordinates[0]), float(coordinates[1])
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Координаты вне допустимого диапазона")
        except (ValueError, TypeError):
            raise ValueError("coordinates должны содержать валидные числа")

        return True

    def _validate_service_type(self, service_type: EmergencyService) -> bool:
        """
        Валидация типа службы

        Args:
            service_type: Тип службы для валидации

        Returns:
            bool: True если тип валиден, False иначе

        Raises:
            ValueError: Если тип службы невалиден
        """
        if not isinstance(service_type, EmergencyService):
            raise ValueError(
                "service_type должен быть экземпляром EmergencyService"
            )

        if service_type not in self.emergency_services:
            raise ValueError(f"Неизвестный тип службы: {service_type}")

        return True

    def _validate_response_id(self, response_id: str) -> bool:
        """
        Валидация ID ответа

        Args:
            response_id: ID ответа для валидации

        Returns:
            bool: True если ID валиден, False иначе

        Raises:
            ValueError: Если ID невалиден
        """
        if not isinstance(response_id, str) or not response_id.strip():
            raise ValueError("response_id должен быть непустой строкой")

        return True

    def _initialize_emergency_services(
        self,
    ) -> Dict[EmergencyService, Dict[str, Any]]:
        """
        Инициализировать службы экстренного реагирования

        Returns:
            Dict: Конфигурация служб
        """
        return {
            EmergencyService.POLICE: {
                "name": "Полиция",
                "phone": "102",
                "coordinates": (55.7558, 37.6176),  # Москва
                "response_time_minutes": 15,
                "available": True,
            },
            EmergencyService.FIRE: {
                "name": "Пожарная служба",
                "phone": "101",
                "coordinates": (55.7558, 37.6176),
                "response_time_minutes": 10,
                "available": True,
            },
            EmergencyService.MEDICAL: {
                "name": "Скорая помощь",
                "phone": "103",
                "coordinates": (55.7558, 37.6176),
                "response_time_minutes": 12,
                "available": True,
            },
            EmergencyService.SECURITY: {
                "name": "Частная охрана",
                "phone": "+7-495-123-45-67",
                "coordinates": (55.7558, 37.6176),
                "response_time_minutes": 20,
                "available": True,
            },
        }

    def call_emergency_service(
        self, event: EmergencyEvent, service_type: EmergencyService
    ) -> EmergencyResponse:
        """
        Вызвать службу экстренного реагирования

        Args:
            event (EmergencyEvent): Экстренное событие с валидными координатами
            service_type (EmergencyService): Тип службы (POLICE, FIRE, MEDICAL,
                SECURITY)

        Returns:
            EmergencyResponse: Ответ службы с уникальным response_id

        Raises:
            ValueError: Если event или service_type невалидны
            RuntimeError: Если служба недоступна или произошла ошибка отправки

        Example:
            >>> caller = EmergencyServiceCaller()
            >>> event = EmergencyEvent(...)
            >>> response = caller.call_emergency_service(
            ...     event, EmergencyService.POLICE)
            >>> print(response.response_id)
            'resp_1758492000000'
        """
        try:
            # Валидация параметров
            self._validate_emergency_event(event)
            self._validate_service_type(service_type)

            service_config = self.emergency_services.get(service_type)
            if not service_config:
                raise ValueError(f"Неизвестный тип службы: {service_type}")

            if not service_config["available"]:
                raise ValueError(f"Служба {service_config['name']} недоступна")

            # Формируем сообщение для службы
            message = EmergencyMessageFormatter.format_service_call_message(
                service_config["name"], event
            )

            # Создаем ответ службы
            response = EmergencyResponse(
                response_id=f"resp_{int(datetime.now().timestamp() * 1000)}",
                event_id=event.event_id,
                service_type=service_type,
                service_name=service_config["name"],
                service_phone=service_config["phone"],
                message=message,
                status="dispatched",
                dispatched_at=datetime.now(),
                estimated_arrival=datetime.now().timestamp()
                + (service_config["response_time_minutes"] * 60),
            )

            # Сохраняем вызов
            self.service_calls[response.response_id] = response

            # В реальной системе здесь отправка запроса в службу
            self._send_service_request(service_config, message, event)

            self.logger.info(
                f"Вызвана служба {service_config['name']} "
                f"для события {event.event_id}"
            )
            return response

        except Exception as e:
            self.logger.error(f"Ошибка вызова службы: {e}")
            raise

    async def call_emergency_service_async(
        self, event: EmergencyEvent, service_type: EmergencyService
    ) -> EmergencyResponse:
        """
        Асинхронно вызвать службу экстренного реагирования

        Args:
            event: Экстренное событие
            service_type: Тип службы

        Returns:
            EmergencyResponse: Ответ службы

        Raises:
            ValueError: Если параметры невалидны
            RuntimeError: Если служба недоступна
        """
        try:
            # Валидация параметров
            self._validate_emergency_event(event)
            self._validate_service_type(service_type)

            service_config = self.emergency_services.get(service_type)
            if not service_config:
                raise ValueError(f"Неизвестный тип службы: {service_type}")

            if not service_config["available"]:
                raise ValueError(f"Служба {service_config['name']} недоступна")

            # Формируем сообщение для службы
            message = EmergencyMessageFormatter.format_service_call_message(
                service_config["name"], event
            )

            # Создаем ответ службы
            response = EmergencyResponse(
                response_id=f"resp_{int(datetime.now().timestamp() * 1000)}",
                event_id=event.event_id,
                service_type=service_type,
                service_name=service_config["name"],
                service_phone=service_config["phone"],
                message=message,
                status="dispatched",
                dispatched_at=datetime.now(),
            )

            # Сохраняем вызов
            self.service_calls[response.response_id] = response

            # Имитируем асинхронную отправку запроса
            await asyncio.sleep(0.1)  # Имитация сетевого запроса

            success = await self._send_service_request_async(
                service_config, message, event
            )

            if success:
                self.logger.info(
                    f"Вызвана служба {service_config['name']} "
                    f"для события {event.event_id}"
                )
            else:
                response.status = "failed"
                self.logger.warning(
                    f"Не удалось вызвать службу {service_config['name']} "
                    f"для события {event.event_id}"
                )

            return response

        except Exception as e:
            self.logger.error(f"Ошибка асинхронного вызова службы: {e}")
            raise

    def _send_service_request(
        self,
        service_config: Dict[str, Any],
        message: str,
        event: EmergencyEvent,
    ) -> bool:
        """
        Отправить запрос в службу

        Args:
            service_config: Конфигурация службы
            message: Сообщение
            event: Событие

        Returns:
            bool: True если запрос отправлен успешно
        """
        try:
            # В реальной системе здесь интеграция с API служб
            self.logger.info(
                f"Запрос отправлен в {service_config['name']}: "
                f"{message[:100]}..."
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки запроса в службу: {e}")
            return False

    async def _send_service_request_async(
        self,
        service_config: Dict[str, Any],
        message: str,
        event: EmergencyEvent,
    ) -> bool:
        """
        Асинхронно отправить запрос в службу

        Args:
            service_config: Конфигурация службы
            message: Сообщение для службы
            event: Экстренное событие

        Returns:
            bool: True если запрос отправлен успешно, False иначе
        """
        try:
            # Имитируем асинхронную отправку запроса
            await asyncio.sleep(0.05)  # Имитация сетевой задержки

            self.logger.info(
                f"Запрос отправлен в {service_config['name']}: "
                f"{message[:100]}..."
            )

            # Имитируем успешную отправку
            return True

        except Exception as e:
            self.logger.error(
                f"Ошибка асинхронной отправки запроса в службу: {e}"
            )
            return False

    def get_nearest_services(
        self, event: EmergencyEvent, max_distance_km: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Получить ближайшие службы к событию

        Args:
            event: Экстренное событие
            max_distance_km: Максимальное расстояние в км

        Returns:
            List[Dict[str, Any]]: Список ближайших служб
        """
        try:
            event_coords = event.location.get("coordinates")
            if not event_coords:
                return []

            # Преобразуем координаты события в кортеж если необходимо
            if isinstance(event_coords, list):
                event_coords = tuple(event_coords)

            # Подготавливаем данные служб
            services_data = []
            for service_type, config in self.emergency_services.items():
                if config["available"]:
                    services_data.append(
                        {
                            "service_type": service_type,
                            "name": config["name"],
                            "phone": config["phone"],
                            "coordinates": config["coordinates"],
                            "response_time_minutes": config[
                                "response_time_minutes"
                            ],
                        }
                    )

            # Находим ближайшие службы
            nearest_services = LocationServiceFinder.find_nearest_services(
                event_coords, services_data
            )

            # Фильтруем по максимальному расстоянию
            filtered_services = [
                service
                for service in nearest_services
                if service["distance"] <= max_distance_km
            ]

            return filtered_services

        except Exception as e:
            self.logger.error(f"Ошибка поиска ближайших служб: {e}")
            return []

    def update_response_status(
        self,
        response_id: str,
        status: str,
        additional_info: Optional[str] = None,
    ) -> bool:
        """
        Обновить статус ответа службы

        Args:
            response_id: ID ответа
            status: Новый статус
            additional_info: Дополнительная информация

        Returns:
            bool: True если обновлено успешно
        """
        try:
            response = self.service_calls.get(response_id)
            if not response:
                return False

            response.status = status
            if additional_info:
                response.additional_info = additional_info

            if status == "arrived":
                response.arrived_at = datetime.now()
            elif status == "completed":
                response.completed_at = datetime.now()

            self.logger.info(
                f"Статус ответа {response_id} обновлен на {status}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления статуса ответа: {e}")
            return False

    def get_response(self, response_id: str) -> Optional[EmergencyResponse]:
        """
        Получить ответ службы по ID

        Args:
            response_id: ID ответа

        Returns:
            Optional[EmergencyResponse]: Ответ службы или None
        """
        return self.service_calls.get(response_id)

    def get_responses_for_event(
        self, event_id: str
    ) -> List[EmergencyResponse]:
        """
        Получить все ответы для события

        Args:
            event_id: ID события

        Returns:
            List[EmergencyResponse]: Список ответов
        """
        return [
            response
            for response in self.service_calls.values()
            if response.event_id == event_id
        ]

    def get_service_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику вызовов служб

        Returns:
            Dict[str, Any]: Статистика
        """
        try:
            # Проверяем наличие атрибутов
            if not hasattr(self, "service_calls"):
                self.logger.warning(
                    "service_calls attribute not found, initializing"
                )
                self.service_calls = {}
            total_calls = len(self.service_calls)
            dispatched_calls = len(
                [
                    r
                    for r in self.service_calls.values()
                    if r.status == "dispatched"
                ]
            )
            arrived_calls = len(
                [
                    r
                    for r in self.service_calls.values()
                    if r.status == "arrived"
                ]
            )
            completed_calls = len(
                [
                    r
                    for r in self.service_calls.values()
                    if r.status == "completed"
                ]
            )

            # Статистика по типам служб
            service_stats = {}
            for response in self.service_calls.values():
                service_type = response.service_type.value
                if service_type not in service_stats:
                    service_stats[service_type] = 0
                service_stats[service_type] += 1

            return {
                "total_calls": total_calls,
                "dispatched_calls": dispatched_calls,
                "arrived_calls": arrived_calls,
                "completed_calls": completed_calls,
                "completion_rate": (completed_calls / max(total_calls, 1))
                * 100,
                "service_type_statistics": service_stats,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики служб: {e}")
            return {}

    def get_available_services(self) -> List[Dict[str, Any]]:
        """
        Получить доступные службы

        Returns:
            List[Dict[str, Any]]: Список доступных служб
        """
        return [
            {
                "service_type": service_type.value,
                "name": config["name"],
                "phone": config["phone"],
                "response_time_minutes": config["response_time_minutes"],
            }
            for service_type, config in self.emergency_services.items()
            if config["available"]
        ]

    def __str__(self) -> str:
        """
        Строковое представление объекта

        Returns:
            str: Строковое представление EmergencyServiceCaller
        """
        return (
            f"EmergencyServiceCaller("
            f"calls={len(self.service_calls)}, "
            f"services={len(self.emergency_services)})"
        )

    def __repr__(self) -> str:
        """
        Техническое представление объекта

        Returns:
            str: Техническое представление EmergencyServiceCaller
        """
        return (
            f"EmergencyServiceCaller("
            f"service_calls={self.service_calls}, "
            f"emergency_services={self.emergency_services})"
        )

    def __eq__(self, other: object) -> bool:
        """
        Сравнение объектов на равенство

        Args:
            other: Другой объект для сравнения

        Returns:
            bool: True если объекты равны, False иначе
        """
        if not isinstance(other, EmergencyServiceCaller):
            return False
        return (
            self.service_calls == other.service_calls
            and self.emergency_services == other.emergency_services
        )

    def __hash__(self) -> int:
        """
        Хеширование объекта

        Returns:
            int: Хеш объекта
        """
        # Используем только неизменяемые данные для хеширования
        service_calls_hash = hash(tuple(sorted(self.service_calls.keys())))
        emergency_services_hash = hash(
            tuple(
                sorted(
                    service_type.value
                    for service_type in self.emergency_services.keys()
                )
            )
        )
        return hash((service_calls_hash, emergency_services_hash))

    def __lt__(self, other: object) -> bool:
        """
        Сравнение объектов на меньше (по количеству вызовов)

        Args:
            other: Другой объект для сравнения

        Returns:
            bool: True если у self меньше вызовов чем у other
        """
        if not isinstance(other, EmergencyServiceCaller):
            return NotImplemented
        return len(self.service_calls) < len(other.service_calls)

    def __le__(self, other: object) -> bool:
        """
        Сравнение объектов на меньше или равно

        Args:
            other: Другой объект для сравнения

        Returns:
            bool: True если у self меньше или равно вызовов чем у other
        """
        if not isinstance(other, EmergencyServiceCaller):
            return NotImplemented
        return len(self.service_calls) <= len(other.service_calls)

    def __gt__(self, other: object) -> bool:
        """
        Сравнение объектов на больше (по количеству вызовов)

        Args:
            other: Другой объект для сравнения

        Returns:
            bool: True если у self больше вызовов чем у other
        """
        if not isinstance(other, EmergencyServiceCaller):
            return NotImplemented
        return len(self.service_calls) > len(other.service_calls)

    def __ge__(self, other: object) -> bool:
        """
        Сравнение объектов на больше или равно

        Args:
            other: Другой объект для сравнения

        Returns:
            bool: True если у self больше или равно вызовов чем у other
        """
        if not isinstance(other, EmergencyServiceCaller):
            return NotImplemented
        return len(self.service_calls) >= len(other.service_calls)

    def __ne__(self, other: object) -> bool:
        """
        Сравнение объектов на неравенство

        Args:
            other: Другой объект для сравнения

        Returns:
            bool: True если объекты не равны
        """
        return not self.__eq__(other)

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка состояния службы экстренного вызова

        Returns:
            Dict[str, Any]: Статус здоровья службы
        """
        try:
            import asyncio

            health_status = {
                "status": "healthy",
                "timestamp": asyncio.get_event_loop().time(),
                "service": "EmergencyServiceCaller",
                "components": {
                    "logger_initialized": self.logger is not None,
                    "emergency_services_loaded": len(self.emergency_services) > 0,
                    "service_calls_tracking": len(self.service_calls) >= 0,
                    "validation_methods": True
                },
                "metrics": {
                    "total_emergency_services": len(self.emergency_services),
                    "active_service_calls": len(self.service_calls),
                    "available_service_types": list(self.emergency_services.keys())
                }
            }

            # Проверка загруженных служб
            if len(self.emergency_services) == 0:
                health_status["status"] = "degraded"
                health_status["components"]["emergency_services_loaded"] = False

            # Проверка активных вызовов
            if len(self.service_calls) > 100:  # Большое количество активных вызовов
                health_status["status"] = "degraded"
                health_status["components"]["high_call_volume"] = True

            # Проверка статистики служб
            stats = self.get_service_statistics()
            if stats.get("total_calls", 0) > 1000:  # Большое количество общих вызовов
                health_status["status"] = "degraded"
                health_status["components"]["high_total_calls"] = True

            return health_status

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": asyncio.get_event_loop().time(),
                "service": "EmergencyServiceCaller",
                "error": str(e)
            }
