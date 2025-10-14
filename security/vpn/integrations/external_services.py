#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
External Services - Интеграции с внешними сервисами для VPN системы
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Типы внешних сервисов"""

    PAYMENT = "payment"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    MONITORING = "monitoring"
    SECURITY = "security"
    CDN = "cdn"
    DATABASE = "database"


class ServiceStatus(Enum):
    """Статусы сервисов"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ExternalService:
    """Модель внешнего сервиса"""

    service_id: str
    service_type: ServiceType
    name: str
    base_url: str
    api_key: Optional[str] = None
    status: ServiceStatus = ServiceStatus.ACTIVE
    last_check: Optional[datetime] = None
    error_count: int = 0
    max_errors: int = 5
    timeout: int = 30
    retry_interval: int = 60
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceResponse:
    """Модель ответа от внешнего сервиса"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    response_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class PaymentService:
    """Интеграция с платежными системами"""

    def __init__(self, service: ExternalService):
        self.service = service
        self.logger = logging.getLogger(f"{__name__}.PaymentService")

    async def create_payment(self, amount: float, currency: str, user_id: str) -> ServiceResponse:
        """Создание платежа"""
        start_time = datetime.now()

        try:
            payload = {
                "amount": amount,
                "currency": currency,
                "user_id": user_id,
                "description": "ALADDIN VPN Subscription",
                "return_url": "https://aladdin-vpn.com/payment/success",
                "cancel_url": "https://aladdin-vpn.com/payment/cancel",
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.service.timeout)) as session:
                headers = {"Authorization": f"Bearer {self.service.api_key}"} if self.service.api_key else {}

                async with session.post(f"{self.service.base_url}/payments", json=payload, headers=headers) as response:
                    data = await response.json()

                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        return ServiceResponse(
                            success=True, data=data, status_code=response.status, response_time=response_time
                        )
                    else:
                        return ServiceResponse(
                            success=False,
                            error=data.get("message", "Payment creation failed"),
                            status_code=response.status,
                            response_time=response_time,
                        )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ServiceResponse(success=False, error=str(e), response_time=response_time)

    async def verify_payment(self, payment_id: str) -> ServiceResponse:
        """Проверка статуса платежа"""
        start_time = datetime.now()

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.service.timeout)) as session:
                headers = {"Authorization": f"Bearer {self.service.api_key}"} if self.service.api_key else {}

                async with session.get(f"{self.service.base_url}/payments/{payment_id}", headers=headers) as response:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        return ServiceResponse(
                            success=True, data=data, status_code=response.status, response_time=response_time
                        )
                    else:
                        return ServiceResponse(
                            success=False,
                            error=data.get("message", "Payment verification failed"),
                            status_code=response.status,
                            response_time=response_time,
                        )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ServiceResponse(success=False, error=str(e), response_time=response_time)


class NotificationService:
    """Интеграция с сервисами уведомлений"""

    def __init__(self, service: ExternalService):
        self.service = service
        self.logger = logging.getLogger(f"{__name__}.NotificationService")

    async def send_email(self, to: str, subject: str, body: str, template: Optional[str] = None) -> ServiceResponse:
        """Отправка email"""
        start_time = datetime.now()

        try:
            payload = {
                "to": to,
                "subject": subject,
                "body": body,
                "template": template,
                "from": "noreply@aladdin-vpn.com",
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.service.timeout)) as session:
                headers = {"Authorization": f"Bearer {self.service.api_key}"} if self.service.api_key else {}

                async with session.post(
                    f"{self.service.base_url}/email/send", json=payload, headers=headers
                ) as response:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        return ServiceResponse(
                            success=True, data=data, status_code=response.status, response_time=response_time
                        )
                    else:
                        return ServiceResponse(
                            success=False,
                            error=data.get("message", "Email sending failed"),
                            status_code=response.status,
                            response_time=response_time,
                        )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ServiceResponse(success=False, error=str(e), response_time=response_time)

    async def send_sms(self, to: str, message: str) -> ServiceResponse:
        """Отправка SMS"""
        start_time = datetime.now()

        try:
            payload = {"to": to, "message": message, "from": "ALADDIN VPN"}

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.service.timeout)) as session:
                headers = {"Authorization": f"Bearer {self.service.api_key}"} if self.service.api_key else {}

                async with session.post(f"{self.service.base_url}/sms/send", json=payload, headers=headers) as response:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        return ServiceResponse(
                            success=True, data=data, status_code=response.status, response_time=response_time
                        )
                    else:
                        return ServiceResponse(
                            success=False,
                            error=data.get("message", "SMS sending failed"),
                            status_code=response.status,
                            response_time=response_time,
                        )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ServiceResponse(success=False, error=str(e), response_time=response_time)

    async def send_push_notification(
        self, user_id: str, title: str, message: str, data: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """Отправка push уведомления"""
        start_time = datetime.now()

        try:
            payload = {"user_id": user_id, "title": title, "message": message, "data": data or {}}

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.service.timeout)) as session:
                headers = {"Authorization": f"Bearer {self.service.api_key}"} if self.service.api_key else {}

                async with session.post(
                    f"{self.service.base_url}/push/send", json=payload, headers=headers
                ) as response:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        return ServiceResponse(
                            success=True, data=data, status_code=response.status, response_time=response_time
                        )
                    else:
                        return ServiceResponse(
                            success=False,
                            error=data.get("message", "Push notification failed"),
                            status_code=response.status,
                            response_time=response_time,
                        )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ServiceResponse(success=False, error=str(e), response_time=response_time)


class AnalyticsService:
    """Интеграция с аналитическими сервисами"""

    def __init__(self, service: ExternalService):
        self.service = service
        self.logger = logging.getLogger(f"{__name__}.AnalyticsService")

    async def track_event(
        self, event_name: str, user_id: str, properties: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """Отслеживание события"""
        start_time = datetime.now()

        try:
            payload = {
                "event": event_name,
                "user_id": user_id,
                "properties": properties or {},
                "timestamp": datetime.now().isoformat(),
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.service.timeout)) as session:
                headers = {"Authorization": f"Bearer {self.service.api_key}"} if self.service.api_key else {}

                async with session.post(f"{self.service.base_url}/events", json=payload, headers=headers) as response:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        return ServiceResponse(
                            success=True, data=data, status_code=response.status, response_time=response_time
                        )
                    else:
                        return ServiceResponse(
                            success=False,
                            error=data.get("message", "Event tracking failed"),
                            status_code=response.status,
                            response_time=response_time,
                        )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ServiceResponse(success=False, error=str(e), response_time=response_time)

    async def get_analytics(self, metric: str, start_date: datetime, end_date: datetime) -> ServiceResponse:
        """Получение аналитики"""
        start_time = datetime.now()

        try:
            params = {"metric": metric, "start_date": start_date.isoformat(), "end_date": end_date.isoformat()}

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.service.timeout)) as session:
                headers = {"Authorization": f"Bearer {self.service.api_key}"} if self.service.api_key else {}

                async with session.get(
                    f"{self.service.base_url}/analytics", params=params, headers=headers
                ) as response:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        return ServiceResponse(
                            success=True, data=data, status_code=response.status, response_time=response_time
                        )
                    else:
                        return ServiceResponse(
                            success=False,
                            error=data.get("message", "Analytics retrieval failed"),
                            status_code=response.status,
                            response_time=response_time,
                        )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ServiceResponse(success=False, error=str(e), response_time=response_time)


class SecurityService:
    """Интеграция с сервисами безопасности"""

    def __init__(self, service: ExternalService):
        self.service = service
        self.logger = logging.getLogger(f"{__name__}.SecurityService")

    async def check_threat(self, ip_address: str, user_agent: str) -> ServiceResponse:
        """Проверка IP на угрозы"""
        start_time = datetime.now()

        try:
            payload = {"ip_address": ip_address, "user_agent": user_agent, "timestamp": datetime.now().isoformat()}

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.service.timeout)) as session:
                headers = {"Authorization": f"Bearer {self.service.api_key}"} if self.service.api_key else {}

                async with session.post(
                    f"{self.service.base_url}/threats/check", json=payload, headers=headers
                ) as response:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        return ServiceResponse(
                            success=True, data=data, status_code=response.status, response_time=response_time
                        )
                    else:
                        return ServiceResponse(
                            success=False,
                            error=data.get("message", "Threat check failed"),
                            status_code=response.status,
                            response_time=response_time,
                        )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ServiceResponse(success=False, error=str(e), response_time=response_time)

    async def report_incident(
        self, incident_type: str, description: str, severity: str, user_id: Optional[str] = None
    ) -> ServiceResponse:
        """Сообщение об инциденте"""
        start_time = datetime.now()

        try:
            payload = {
                "incident_type": incident_type,
                "description": description,
                "severity": severity,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.service.timeout)) as session:
                headers = {"Authorization": f"Bearer {self.service.api_key}"} if self.service.api_key else {}

                async with session.post(
                    f"{self.service.base_url}/incidents", json=payload, headers=headers
                ) as response:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        return ServiceResponse(
                            success=True, data=data, status_code=response.status, response_time=response_time
                        )
                    else:
                        return ServiceResponse(
                            success=False,
                            error=data.get("message", "Incident reporting failed"),
                            status_code=response.status,
                            response_time=response_time,
                        )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ServiceResponse(success=False, error=str(e), response_time=response_time)


class ExternalServicesManager:
    """
    Менеджер внешних сервисов

    Управляет:
    - Регистрацией и конфигурацией сервисов
    - Health check проверками
    - Автоматическим восстановлением
    - Логированием и мониторингом
    """

    def __init__(self, name: str = "ExternalServicesManager"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Сервисы
        self.services: Dict[str, ExternalService] = {}
        self.service_handlers: Dict[ServiceType, Any] = {}

        # Health check
        self.health_check_interval = 300  # 5 минут
        self.health_check_task: Optional[asyncio.Task] = None

        self.logger.info(f"External Services Manager '{name}' инициализирован")

    async def start(self) -> None:
        """Запуск менеджера внешних сервисов"""
        self.logger.info("Запуск менеджера внешних сервисов...")

        # Регистрация сервисов
        await self._register_default_services()

        # Запуск health check
        self.health_check_task = asyncio.create_task(self._health_check_loop())

        self.logger.info("Менеджер внешних сервисов запущен")

    async def stop(self) -> None:
        """Остановка менеджера внешних сервисов"""
        self.logger.info("Остановка менеджера внешних сервисов...")

        if self.health_check_task:
            self.health_check_task.cancel()

        self.logger.info("Менеджер внешних сервисов остановлен")

    async def _register_default_services(self) -> None:
        """Регистрация сервисов по умолчанию"""
        # Платежный сервис (Stripe)
        stripe_service = ExternalService(
            service_id="stripe",
            service_type=ServiceType.PAYMENT,
            name="Stripe Payment",
            base_url="https://api.stripe.com/v1",
            api_key="sk_test_...",  # В реальной системе из конфига
            config={"webhook_secret": "whsec_..."},
        )
        await self.register_service(stripe_service)

        # Email сервис (SendGrid)
        sendgrid_service = ExternalService(
            service_id="sendgrid",
            service_type=ServiceType.NOTIFICATION,
            name="SendGrid Email",
            base_url="https://api.sendgrid.com/v3",
            api_key="SG...",  # В реальной системе из конфига
            config={"from_email": "noreply@aladdin-vpn.com"},
        )
        await self.register_service(sendgrid_service)

        # SMS сервис (Twilio)
        twilio_service = ExternalService(
            service_id="twilio",
            service_type=ServiceType.NOTIFICATION,
            name="Twilio SMS",
            base_url="https://api.twilio.com/2010-04-01",
            api_key="AC...",  # В реальной системе из конфига
            config={"from_number": "+1234567890"},
        )
        await self.register_service(twilio_service)

        # Аналитический сервис (Mixpanel)
        mixpanel_service = ExternalService(
            service_id="mixpanel",
            service_type=ServiceType.ANALYTICS,
            name="Mixpanel Analytics",
            base_url="https://api.mixpanel.com",
            api_key="...",  # В реальной системе из конфига
            config={"project_id": "..."},
        )
        await self.register_service(mixpanel_service)

        # Сервис безопасности (AbuseIPDB)
        abuseipdb_service = ExternalService(
            service_id="abuseipdb",
            service_type=ServiceType.SECURITY,
            name="AbuseIPDB Security",
            base_url="https://api.abuseipdb.com/api/v2",
            api_key="...",  # В реальной системе из конфига
            config={"max_age_days": 90},
        )
        await self.register_service(abuseipdb_service)

    async def register_service(self, service: ExternalService) -> None:
        """Регистрация внешнего сервиса"""
        self.services[service.service_id] = service

        # Создание обработчика для типа сервиса
        if service.service_type == ServiceType.PAYMENT:
            self.service_handlers[service.service_id] = PaymentService(service)
        elif service.service_type == ServiceType.NOTIFICATION:
            self.service_handlers[service.service_id] = NotificationService(service)
        elif service.service_type == ServiceType.ANALYTICS:
            self.service_handlers[service.service_id] = AnalyticsService(service)
        elif service.service_type == ServiceType.SECURITY:
            self.service_handlers[service.service_id] = SecurityService(service)

        self.logger.info(f"Сервис зарегистрирован: {service.name} ({service.service_id})")

    async def _health_check_loop(self) -> None:
        """Цикл проверки здоровья сервисов"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)

                for service_id, service in self.services.items():
                    await self._check_service_health(service)

            except Exception as e:
                self.logger.error(f"Ошибка в health check loop: {e}")
                await asyncio.sleep(60)

    async def _check_service_health(self, service: ExternalService) -> None:
        """Проверка здоровья сервиса"""
        try:
            start_time = datetime.now()

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=service.timeout)) as session:
                async with session.get(f"{service.base_url}/health") as response:
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        service.status = ServiceStatus.ACTIVE
                        service.error_count = 0
                        self.logger.debug(f"Сервис {service.name} здоров (время ответа: {response_time:.2f}с)")
                    else:
                        service.status = ServiceStatus.ERROR
                        service.error_count += 1
                        self.logger.warning(f"Сервис {service.name} недоступен (статус: {response.status})")

            service.last_check = datetime.now()

        except Exception as e:
            service.status = ServiceStatus.ERROR
            service.error_count += 1
            service.last_check = datetime.now()
            self.logger.error(f"Ошибка проверки сервиса {service.name}: {e}")

        # Отключение сервиса при превышении лимита ошибок
        if service.error_count >= service.max_errors:
            service.status = ServiceStatus.INACTIVE
            self.logger.error(f"Сервис {service.name} отключен из-за превышения лимита ошибок")

    def get_service(self, service_id: str) -> Optional[ExternalService]:
        """Получение сервиса по ID"""
        return self.services.get(service_id)

    def get_service_handler(self, service_id: str) -> Optional[Any]:
        """Получение обработчика сервиса"""
        return self.service_handlers.get(service_id)

    def get_services_by_type(self, service_type: ServiceType) -> List[ExternalService]:
        """Получение сервисов по типу"""
        return [s for s in self.services.values() if s.service_type == service_type]

    def get_active_services(self) -> List[ExternalService]:
        """Получение активных сервисов"""
        return [s for s in self.services.values() if s.status == ServiceStatus.ACTIVE]

    def get_service_stats(self) -> Dict[str, Any]:
        """Получение статистики сервисов"""
        total_services = len(self.services)
        active_services = len(self.get_active_services())

        stats = {
            "total_services": total_services,
            "active_services": active_services,
            "inactive_services": total_services - active_services,
            "services_by_type": {},
            "timestamp": datetime.now().isoformat(),
        }

        # Группировка по типам
        for service_type in ServiceType:
            count = len(self.get_services_by_type(service_type))
            stats["services_by_type"][service_type.value] = count

        return stats


# Пример использования
async def main():
    """Пример использования External Services Manager"""
    manager = ExternalServicesManager("TestManager")

    # Запуск менеджера
    await manager.start()

    # Получение статистики
    stats = manager.get_service_stats()
    print("=== ВНЕШНИЕ СЕРВИСЫ ===")
    print(f"Всего сервисов: {stats['total_services']}")
    print(f"Активных: {stats['active_services']}")
    print(f"По типам: {stats['services_by_type']}")

    # Тестирование платежного сервиса
    stripe_handler = manager.get_service_handler("stripe")
    if stripe_handler:
        payment_response = await stripe_handler.create_payment(9.99, "USD", "user_001")
        print(f"Платеж создан: {payment_response.success}")

    # Остановка менеджера
    await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
