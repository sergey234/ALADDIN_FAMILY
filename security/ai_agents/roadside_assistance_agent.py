#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚑 Roadside Assistance Agent
Агент для предоставления помощи на дороге 24/7

Функциональность:
- Вызов помощи на дороге (буксировка, запуск двигателя, замена колеса и др.)
- Интеграция с партнерскими службами помощи
- Отслеживание статуса помощи в реальном времени
- История запросов помощи
- Отмена запросов

Дата создания: 14 декабря 2025
Версия: 1.0.0
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

# HTTP клиент
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

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


class ProblemType(Enum):
    """Типы проблем на дороге"""
    TOWING = "towing"  # Буксировка
    JUMP_START = "jump_start"  # Запуск двигателя
    TIRE_CHANGE = "tire_change"  # Замена колеса
    LOCKOUT = "lockout"  # Открытие замка
    FUEL_DELIVERY = "fuel_delivery"  # Доставка топлива
    BATTERY_REPLACEMENT = "battery_replacement"  # Замена аккумулятора
    WINDSHIELD_REPAIR = "windshield_repair"  # Ремонт лобового стекла
    OTHER = "other"  # Другое


class AssistanceStatus(Enum):
    """Статусы помощи"""
    PENDING = "pending"  # Запрос создан, ожидает диспетчера
    DISPATCHED = "dispatched"  # Диспетчер назначил службу помощи
    ON_WAY = "on_way"  # Служба помощи в пути
    ARRIVED = "arrived"  # Служба помощи прибыла на место
    IN_PROGRESS = "in_progress"  # Помощь оказывается
    COMPLETED = "completed"  # Помощь оказана, проблема решена
    CANCELLED = "cancelled"  # Запрос отменен
    FAILED = "failed"  # Ошибка при оказании помощи


class PartnerType(Enum):
    """Типы партнеров"""
    ROSGOSSTRAH = "rosgosstrah"  # Росгосстрах
    ALFASTRAHOVANIE = "alfastrahovanie"  # АльфаСтрахование
    INGOSSTRAH = "ingosstrah"  # Ингосстрах
    RESO = "reso"  # РЕСО-Гарантия
    MANUAL = "manual"  # Ручной вызов (без партнера)


@dataclass
class Location:
    """Местоположение"""
    latitude: float
    longitude: float
    address: Optional[str] = None
    accuracy: Optional[float] = None  # Точность в метрах

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VehicleInfo:
    """Информация о транспортном средстве"""
    make: Optional[str] = None  # Марка (Toyota, BMW и т.д.)
    model: Optional[str] = None  # Модель (Camry, X5 и т.д.)
    year: Optional[int] = None  # Год выпуска
    color: Optional[str] = None  # Цвет
    license_plate: Optional[str] = None  # Номерной знак
    vin: Optional[str] = None  # VIN номер

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ServiceProvider:
    """Информация о службе помощи"""
    name: str  # Название службы
    phone: str  # Контактный телефон
    vehicle_number: Optional[str] = None  # Номер автомобиля службы
    driver_name: Optional[str] = None  # Имя водителя
    estimated_arrival: Optional[str] = None  # Ожидаемое время прибытия (ISO format)
    current_location: Optional[Location] = None  # Текущее местоположение службы

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.current_location:
            result["current_location"] = self.current_location.to_dict()
        return result


@dataclass
class AssistanceRequest:
    """Запрос на помощь"""
    request_id: str  # Уникальный ID запроса
    user_id: str  # ID пользователя
    partner: str  # Партнер (rosgosstrah, alfastrahovanie и т.д.)
    problem_type: ProblemType  # Тип проблемы
    status: AssistanceStatus  # Статус помощи
    location: Location  # Местоположение
    description: Optional[str] = None  # Описание проблемы
    vehicle_info: Optional[VehicleInfo] = None  # Информация о транспортном средстве
    service_provider: Optional[ServiceProvider] = None  # Информация о службе помощи
    partner_request_id: Optional[str] = None  # ID запроса у партнера
    created_at: Optional[str] = None  # Время создания (ISO format)
    updated_at: Optional[str] = None  # Время последнего обновления (ISO format)
    completed_at: Optional[str] = None  # Время завершения (ISO format)
    estimated_arrival: Optional[str] = None  # Ожидаемое время прибытия (ISO format)
    cost: Optional[float] = None  # Стоимость услуги
    notes: Optional[str] = None  # Дополнительные заметки

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "partner": self.partner,
            "problem_type": self.problem_type.value,
            "status": self.status.value,
            "location": self.location.to_dict(),
            "description": self.description,
            "partner_request_id": self.partner_request_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "estimated_arrival": self.estimated_arrival,
            "cost": self.cost,
            "notes": self.notes
        }
        if self.vehicle_info:
            result["vehicle_info"] = self.vehicle_info.to_dict()
        if self.service_provider:
            result["service_provider"] = self.service_provider.to_dict()
        return result


class RoadsideAssistanceAgent(SecurityBase, ThreatMonitoringInterface):
    """
    Агент для помощи на дороге 24/7

    Функциональность:
    - Вызов помощи на дороге
    - Интеграция с партнерскими службами
    - Отслеживание статуса помощи
    - История запросов
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация агента

        Args:
            config: Конфигурация агента
        """
        super().__init__(config)

        # Инициализация logger (всегда, так как SecurityBase может не инициализировать)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Конфигурация (используем локальную переменную вместо self.config)
        config_dict = config if config is not None else {}
        self.default_partner = config_dict.get("default_partner", PartnerType.MANUAL.value)
        self.status_check_interval_seconds = int(config_dict.get("status_check_interval_seconds", 30))
        self.max_wait_time_minutes = int(config_dict.get("max_wait_time_minutes", 120))
        self.enable_auto_status_check = config_dict.get("enable_auto_status_check", True)

        # Партнерские API ключи (в продакшене из переменных окружения)
        self.partner_api_keys = {
            PartnerType.ROSGOSSTRAH.value: config_dict.get("rosgosstrah_api_key", ""),
            PartnerType.ALFASTRAHOVANIE.value: config_dict.get("alfastrahovanie_api_key", ""),
            PartnerType.INGOSSTRAH.value: config_dict.get("ingosstrah_api_key", ""),
            PartnerType.RESO.value: config_dict.get("reso_api_key", "")
        }

        # Партнерские API endpoints (в продакшене из конфигурации)
        self.partner_api_endpoints = {
            PartnerType.ROSGOSSTRAH.value: config_dict.get(
                "rosgosstrah_api_url",
                "https://api.rosgosstrah.ru/roadside-assistance"
            ),
            PartnerType.ALFASTRAHOVANIE.value: config_dict.get(
                "alfastrahovanie_api_url",
                "https://api.alfastrah.ru/roadside-assistance"
            ),
            PartnerType.INGOSSTRAH.value: config_dict.get(
                "ingosstrah_api_url",
                "https://api.ingos.ru/roadside-assistance"
            ),
            PartnerType.RESO.value: config_dict.get(
                "reso_api_url",
                "https://api.reso.ru/roadside-assistance"
            )
        }

        # HTTP клиент
        self.session = None
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'ALADDIN-RoadsideAssistance/1.0',
                'Content-Type': 'application/json'
            })
            self.session.timeout = 30

        # Хранилище запросов (в продакшене будет БД)
        self.assistance_requests: Dict[str, AssistanceRequest] = {}

        # Threat monitoring
        self.threat_event_bus = get_threat_event_bus() if get_threat_event_bus else None

        self.logger.info("✅ Roadside Assistance Agent инициализирован")

    def call_assistance(
        self,
        user_id: str,
        problem_type: ProblemType,
        location: Location,
        description: Optional[str] = None,
        vehicle_info: Optional[VehicleInfo] = None,
        partner: Optional[str] = None
    ) -> AssistanceRequest:
        """
        Вызов помощи на дороге

        Args:
            user_id: ID пользователя
            problem_type: Тип проблемы
            location: Местоположение
            description: Описание проблемы
            vehicle_info: Информация о транспортном средстве
            partner: Партнер (если не указан, используется default_partner)

        Returns:
            AssistanceRequest: Созданный запрос на помощь

        Raises:
            ValueError: Если параметры некорректны
            RuntimeError: Если не удалось создать запрос
        """
        if not user_id:
            raise ValueError("user_id обязателен")
        if not location or not location.latitude or not location.longitude:
            raise ValueError("location с координатами обязателен")

        # Выбор партнера
        selected_partner = partner or self.default_partner

        # Генерация ID запроса
        request_id = f"RSA-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        self.logger.info(f"🚑 Создание запроса на помощь: {request_id} (пользователь: {user_id}, тип: {problem_type.value})")

        # Создание запроса
        assistance_request = AssistanceRequest(
            request_id=request_id,
            user_id=user_id,
            partner=selected_partner,
            problem_type=problem_type,
            status=AssistanceStatus.PENDING,
            location=location,
            description=description,
            vehicle_info=vehicle_info,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Отправка запроса партнеру (если не MANUAL)
        if selected_partner != PartnerType.MANUAL.value:
            try:
                partner_request = self._send_request_to_partner(assistance_request)
                if partner_request:
                    assistance_request.partner_request_id = partner_request.get("request_id")
                    assistance_request.status = AssistanceStatus.DISPATCHED
                    assistance_request.estimated_arrival = partner_request.get("estimated_arrival")
                    assistance_request.service_provider = ServiceProvider(
                        name=partner_request.get("service_provider", {}).get("name", "Служба помощи"),
                        phone=partner_request.get("service_provider", {}).get("phone", ""),
                        vehicle_number=partner_request.get("service_provider", {}).get("vehicle_number"),
                        driver_name=partner_request.get("service_provider", {}).get("driver_name"),
                        estimated_arrival=partner_request.get("estimated_arrival")
                    )
                    self.logger.info(f"✅ Запрос отправлен партнеру {selected_partner}: {assistance_request.partner_request_id}")
            except Exception as e:
                self.logger.error(f"❌ Ошибка при отправке запроса партнеру: {e}")
                # Продолжаем с MANUAL режимом
                assistance_request.partner = PartnerType.MANUAL.value
                assistance_request.status = AssistanceStatus.PENDING

        # Сохранение запроса
        self.assistance_requests[request_id] = assistance_request

        # Отправка события в threat monitoring
        if self.threat_event_bus:
            event = ThreatEvent(
                event_id=f"roadside_assistance_{request_id}",
                agent_name="RoadsideAssistanceAgent",
                threat_type="roadside_assistance_request",
                severity="info",
                source=user_id,
                target=selected_partner,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "request_id": request_id,
                    "problem_type": problem_type.value,
                    "location": location.to_dict()
                },
                description=f"Запрос на помощь на дороге: {problem_type.value}"
            )
            self.threat_event_bus.publish(event)

        return assistance_request

    def _send_request_to_partner(self, request: AssistanceRequest) -> Optional[Dict[str, Any]]:
        """
        Отправка запроса партнеру через API

        Args:
            request: Запрос на помощь

        Returns:
            Ответ партнера с информацией о запросе

        Note:
            В текущей реализации это заглушка. В продакшене будет реальная интеграция с API партнеров.
        """
        if not REQUESTS_AVAILABLE:
            self.logger.warning("⚠️ Библиотека requests не установлена. Реальная интеграция с партнерами недоступна.")
            return None

        partner = request.partner
        api_key = self.partner_api_keys.get(partner)
        api_url = self.partner_api_endpoints.get(partner)

        if not api_key or not api_url:
            self.logger.warning(f"⚠️ API ключ или URL не настроены для партнера {partner}")
            return None

        try:
            # Отправка запроса (заглушка - в продакшене реальный API вызов)
            self.logger.info(f"📤 Отправка запроса партнеру {partner}...")
            # Формирование запроса для партнера (в продакшене будет использовано)
            # partner_request_data = {
            #     "service_type": request.problem_type.value,
            #     "location": {
            #         "latitude": request.location.latitude,
            #         "longitude": request.location.longitude,
            #         "address": request.location.address
            #     },
            #     "description": request.description,
            #     "vehicle": request.vehicle_info.to_dict() if request.vehicle_info else {}
            # }
            # response = self.session.post(
            #     f"{api_url}/request",
            #     json=partner_request_data,
            #     headers={"Authorization": f"Bearer {api_key}"}
            # )
            # response.raise_for_status()
            # return response.json()

            # Заглушка для разработки
            return {
                "request_id": f"{partner.upper()}-{uuid.uuid4().hex[:8]}",
                "status": "dispatched",
                "estimated_arrival": (datetime.now().timestamp() + 1800).isoformat(),  # +30 минут
                "service_provider": {
                    "name": "Автопомощь 24/7",
                    "phone": "+79991111111",
                    "vehicle_number": "А123БВ777",
                    "driver_name": "Иван Иванов"
                }
            }
        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке запроса партнеру {partner}: {e}")
            raise

    def get_status(self, request_id: str) -> Optional[AssistanceRequest]:
        """
        Получить статус запроса на помощь

        Args:
            request_id: ID запроса

        Returns:
            AssistanceRequest или None, если запрос не найден
        """
        if request_id not in self.assistance_requests:
            return None

        request = self.assistance_requests[request_id]

        # Обновление статуса у партнера (если не MANUAL)
        if request.partner != PartnerType.MANUAL.value and request.partner_request_id:
            try:
                updated_status = self._check_partner_status(request)
                if updated_status:
                    request.status = AssistanceStatus(updated_status.get("status", request.status.value))
                    request.updated_at = datetime.now().isoformat()
                    if updated_status.get("estimated_arrival"):
                        request.estimated_arrival = updated_status.get("estimated_arrival")
                    if updated_status.get("service_provider"):
                        sp = updated_status.get("service_provider")
                        request.service_provider = ServiceProvider(
                            name=sp.get("name", ""),
                            phone=sp.get("phone", ""),
                            vehicle_number=sp.get("vehicle_number"),
                            driver_name=sp.get("driver_name"),
                            estimated_arrival=sp.get("estimated_arrival")
                        )
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось обновить статус у партнера: {e}")

        return request

    def _check_partner_status(self, request: AssistanceRequest) -> Optional[Dict[str, Any]]:
        """
        Проверка статуса у партнера через API

        Args:
            request: Запрос на помощь

        Returns:
            Обновленный статус от партнера

        Note:
            В текущей реализации это заглушка. В продакшене будет реальная интеграция с API партнеров.
        """
        if not REQUESTS_AVAILABLE or not request.partner_request_id:
            return None

        partner = request.partner
        api_key = self.partner_api_keys.get(partner)
        api_url = self.partner_api_endpoints.get(partner)

        if not api_key or not api_url:
            return None

        try:
            # Проверка статуса (заглушка - в продакшене реальный API вызов)
            # response = self.session.get(
            #     f"{api_url}/{request.partner_request_id}/status",
            #     headers={"Authorization": f"Bearer {api_key}"}
            # )
            # response.raise_for_status()
            # return response.json()

            # Заглушка для разработки
            return {
                "status": request.status.value,
                "estimated_arrival": request.estimated_arrival
            }
        except Exception as e:
            self.logger.error(f"❌ Ошибка при проверке статуса у партнера: {e}")
            return None

    def cancel_request(self, request_id: str) -> bool:
        """
        Отменить запрос на помощь

        Args:
            request_id: ID запроса

        Returns:
            True, если запрос успешно отменен, False иначе
        """
        if request_id not in self.assistance_requests:
            return False

        request = self.assistance_requests[request_id]

        # Проверка, можно ли отменить
        if request.status in [AssistanceStatus.COMPLETED, AssistanceStatus.CANCELLED]:
            return False

        # Отправка запроса на отмену партнеру
        if request.partner != PartnerType.MANUAL.value and request.partner_request_id:
            try:
                self._cancel_partner_request(request)
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось отменить запрос у партнера: {e}")

        # Обновление статуса
        request.status = AssistanceStatus.CANCELLED
        request.updated_at = datetime.now().isoformat()

        self.logger.info(f"✅ Запрос {request_id} отменен")

        return True

    def _cancel_partner_request(self, request: AssistanceRequest) -> None:
        """
        Отмена запроса у партнера через API

        Args:
            request: Запрос на помощь

        Note:
            В текущей реализации это заглушка. В продакшене будет реальная интеграция с API партнеров.
        """
        if not REQUESTS_AVAILABLE or not request.partner_request_id:
            return

        partner = request.partner
        api_key = self.partner_api_keys.get(partner)
        api_url = self.partner_api_endpoints.get(partner)

        if not api_key or not api_url:
            return

        try:
            # Отмена запроса (заглушка - в продакшене реальный API вызов)
            # self.session.post(
            #     f"{api_url}/{request.partner_request_id}/cancel",
            #     headers={"Authorization": f"Bearer {api_key}"}
            # )
            self.logger.info(f"📤 Отмена запроса у партнера {partner}: {request.partner_request_id}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка при отмене запроса у партнера: {e}")
            raise

    def get_history(self, user_id: str, limit: int = 10) -> List[AssistanceRequest]:
        """
        Получить историю запросов пользователя

        Args:
            user_id: ID пользователя
            limit: Максимальное количество запросов

        Returns:
            Список запросов на помощь
        """
        user_requests = [
            req for req in self.assistance_requests.values()
            if req.user_id == user_id
        ]

        # Сортировка по дате создания (новые первыми)
        user_requests.sort(key=lambda x: x.created_at or "", reverse=True)

        return user_requests[:limit]

    # ThreatMonitoringInterface методы
    def collect_threats(self) -> List[ThreatEvent]:
        """Сбор угроз (не применимо для этого агента)"""
        return []

    def analyze_threats(self, threats: List[ThreatEvent]) -> List[ThreatEvent]:
        """Анализ угроз (не применимо для этого агента)"""
        return []

    def send_alert(self, threat: ThreatEvent) -> bool:
        """Отправка уведомления (не применимо для этого агента)"""
        return True
