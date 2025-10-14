#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер вызова служб экстренного реагирования
Применение Single Responsibility принципа
"""

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
    """Менеджер вызова служб экстренного реагирования"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.service_calls: Dict[str, EmergencyResponse] = {}
        self.emergency_services = self._initialize_emergency_services()

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
            event: Экстренное событие
            service_type: Тип службы

        Returns:
            EmergencyResponse: Ответ службы
        """
        try:
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
