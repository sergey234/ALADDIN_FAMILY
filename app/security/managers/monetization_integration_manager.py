#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonetizationIntegrationManager - Интеграционный менеджер монетизации ALADDIN
Версия 1.0 - Полная интеграция всех систем монетизации

Интегрирует:
- SubscriptionManager (управление подписками)
- QRPaymentManager (QR-код оплата)
- ReferralManager (реферальная система)
- PersonalizationAgent (AI-персонализация)
- ABTestingManager (A/B тестирование)
- FamilyNotificationManagerEnhanced (уведомления)

Автор: ALADDIN Security System
Версия: 1.0.0
Дата: 2025-01-27
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from security.core.security_base import ComponentStatus, SecurityBase, SecurityLevel

# Импорт всех менеджеров монетизации
from security.managers.subscription_manager import (
    SubscriptionManager, SubscriptionTier
)
from security.managers.qr_payment_manager import (
    QRPaymentManager, PaymentStatus, YukassaConfig
)
from security.managers.referral_manager import (
    ReferralManager
)
from security.managers.ab_testing_manager import (
    ABTestingManager, TestType
)
from security.ai_agents.personalization_agent import (
    PersonalizationAgent
)
from security.family.family_notification_manager_enhanced import (
    FamilyNotificationManagerEnhanced, NotificationType
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MonetizationConfig:
    """Конфигурация системы монетизации"""
    yukassa_shop_id: str = "your_shop_id"
    yukassa_secret_key: str = "your_secret_key"
    yukassa_test_mode: bool = True
    base_url: str = "https://aladdin-security.ru"
    notification_retention_days: int = 30
    trial_reminder_days: List[int] = field(default_factory=lambda: [7, 3, 1])
    subscription_reminder_days: List[int] = field(default_factory=lambda: [7, 3, 1])


@dataclass
class MonetizationStats:
    """Статистика системы монетизации"""
    total_families: int = 0
    active_subscriptions: int = 0
    trial_subscriptions: int = 0
    total_revenue: float = 0.0
    conversion_rate: float = 0.0
    referral_signups: int = 0
    ab_tests_active: int = 0
    notifications_sent: int = 0
    personalization_recommendations: int = 0


class MonetizationIntegrationManager(SecurityBase):
    """
    Интеграционный менеджер монетизации ALADDIN

    Объединяет все системы монетизации:
    - Управление подписками
    - QR-код оплата
    - Реферальная система
    - AI-персонализация
    - A/B тестирование
    - Уведомления
    """

    def __init__(self, config: Optional[MonetizationConfig] = None):
        """
        Инициализация интеграционного менеджера

        Args:
            config: Конфигурация системы монетизации
        """
        super().__init__()

        # Конфигурация
        self.config = config or MonetizationConfig()

        # Инициализация всех менеджеров
        self.subscription_manager = SubscriptionManager()
        self.qr_payment_manager = QRPaymentManager(
            YukassaConfig(
                shop_id=self.config.yukassa_shop_id,
                secret_key=self.config.yukassa_secret_key,
                test_mode=self.config.yukassa_test_mode
            )
        )
        self.referral_manager = ReferralManager()
        self.personalization_agent = PersonalizationAgent()
        self.ab_testing_manager = ABTestingManager()
        self.notification_manager = FamilyNotificationManagerEnhanced()

        # Статус компонента
        self.status = ComponentStatus.ACTIVE
        self.security_level = SecurityLevel.HIGH

        logger.info("MonetizationIntegrationManager инициализирован")

    async def create_family_subscription(self, family_id: str,
                                         subscription_tier: SubscriptionTier,
                                         referral_code: Optional[str] = None,
                                         trial_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Создание подписки для семьи с полной интеграцией

        Args:
            family_id: ID семьи
            subscription_tier: Тариф подписки
            referral_code: Код реферальной ссылки (если есть)
            trial_days: Дни тестового периода

        Returns:
            Результат создания подписки
        """
        try:
            # 1. Создаем подписку
            subscription_result = await self.subscription_manager.create_subscription(
                family_id=family_id,
                tier=subscription_tier,
                trial_days=trial_days
            )

            if not subscription_result["success"]:
                return subscription_result

            # 2. Обрабатываем реферал (если есть)
            if referral_code:
                referral_result = await self.referral_manager.process_referral(
                    referral_code=referral_code,
                    referred_family_id=family_id
                )

                if referral_result["success"]:
                    # Применяем скидку
                    discount_result = await self.referral_manager.apply_discount(
                        family_id=family_id,
                        subscription_tier=subscription_tier.value,
                        referral_id=referral_result["referral_id"]
                    )

                    if discount_result["success"]:
                        subscription_result["discount_applied"] = discount_result["discount_amount"]
                        subscription_result["referral_id"] = referral_result["referral_id"]

            # 3. Анализируем поведение пользователя
            behavior_data = {
                "family_size": 1,  # Базовое значение
                "device_count": 1,
                "tech_savviness": 0.5,
                "security_concern": 0.7,
                "budget_sensitivity": 0.5,
                "usage_patterns": {
                    "intensity": 0.5,
                    "peak_hours_usage": 0.5,
                    "weekend_usage": 0.5,
                    "mobile_usage": 0.5
                },
                "preferences": {
                    "preferred_tariff": subscription_tier.value
                }
            }

            await self.personalization_agent.analyze_user_behavior(family_id, behavior_data)

            # 4. Отправляем уведомления
            if subscription_result.get("trial_days", 0) > 0:
                # Уведомление о начале тестового периода
                await self.notification_manager.send_family_alert(
                    family_id=family_id,
                    notification_type=NotificationType.TRIAL_STARTED,
                    priority=self.notification_manager.NotificationPriority.MEDIUM,
                    title="Тестовый период начался!",
                    message=f"Добро пожаловать! У вас есть {subscription_result['trial_days']} дней "
                    f"для тестирования тарифа {subscription_tier.value}",
                    channels=[self.notification_manager.NotificationChannel.IN_APP]
                )

                # Планируем напоминания о тестовом периоде
                for days in self.config.trial_reminder_days:
                    if days < subscription_result["trial_days"]:
                        reminder_time = datetime.now() + timedelta(days=subscription_result["trial_days"] - days)
                        await self.notification_manager.schedule_subscription_reminder(
                            family_id=family_id,
                            reminder_type="trial_reminder",
                            scheduled_time=reminder_time,
                            metadata={
                                "days_left": days,
                                "subscription_tier": subscription_tier.value
                            }
                        )
            else:
                # Уведомление об активации подписки
                await self.notification_manager.send_family_alert(
                    family_id=family_id,
                    notification_type=NotificationType.SUBSCRIPTION_ACTIVATED,
                    priority=self.notification_manager.NotificationPriority.HIGH,
                    title="Подписка активирована!",
                    message=f"Ваша подписка {subscription_tier.value} успешно активирована",
                    channels=[self.notification_manager.NotificationChannel.IN_APP]
                )

            logger.info(f"Создана подписка для семьи {family_id}, тариф {subscription_tier.value}")

            return {
                "success": True,
                "subscription_id": subscription_result["subscription_id"],
                "tier": subscription_tier.value,
                "status": subscription_result["status"],
                "trial_days": subscription_result.get("trial_days", 0),
                "discount_applied": subscription_result.get("discount_applied"),
                "referral_id": subscription_result.get("referral_id")
            }

        except Exception as e:
            logger.error(f"Ошибка создания подписки: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_payment(self, family_id: str, subscription_tier: str,
                              amount: float, payment_method: str = "qr_code") -> Dict[str, Any]:
        """
        Обработка платежа с полной интеграцией

        Args:
            family_id: ID семьи
            subscription_tier: Тариф подписки
            amount: Сумма платежа
            payment_method: Способ оплаты

        Returns:
            Результат обработки платежа
        """
        try:
            # 1. Создаем платеж
            payment_result = await self.qr_payment_manager.create_payment(
                family_id=family_id,
                subscription_tier=subscription_tier,
                amount=amount,
                description=f"Оплата подписки {subscription_tier}"
            )

            if not payment_result["success"]:
                return payment_result

            # 2. Отправляем QR-код уведомление
            if payment_result.get("qr_code"):
                await self.notification_manager.send_qr_payment_notification(
                    family_id=family_id,
                    subscription_tier=subscription_tier,
                    amount=amount,
                    qr_code=payment_result["qr_code"]
                )

            # 3. Планируем напоминания об оплате
            reminder_time = datetime.now() + timedelta(hours=24)  # Напоминание через 24 часа
            await self.notification_manager.schedule_subscription_reminder(
                family_id=family_id,
                reminder_type="payment_reminder",
                scheduled_time=reminder_time,
                metadata={
                    "payment_id": payment_result["payment_id"],
                    "subscription_tier": subscription_tier,
                    "amount": amount
                }
            )

            logger.info(f"Создан платеж для семьи {family_id}, сумма {amount}₽")

            return payment_result

        except Exception as e:
            logger.error(f"Ошибка обработки платежа: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def complete_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Завершение платежа с активацией подписки

        Args:
            payment_id: ID платежа

        Returns:
            Результат завершения платежа
        """
        try:
            # 1. Проверяем статус платежа
            payment_status = await self.qr_payment_manager.check_payment_status(payment_id)

            if not payment_status["success"]:
                return payment_status

            if payment_status["status"] != PaymentStatus.COMPLETED.value:
                return {
                    "success": False,
                    "error": f"Платеж не завершен (статус: {payment_status['status']})"
                }

            # 2. Получаем информацию о платеже
            payment_info = await self.qr_payment_manager.get_payment_history(
                payment_status["family_id"]
            )

            if not payment_info:
                return {
                    "success": False,
                    "error": "Информация о платеже не найдена"
                }

            # 3. Активируем подписку
            family_id = payment_status["family_id"]
            subscription_result = await self.subscription_manager.create_subscription(
                family_id=family_id,
                tier=SubscriptionTier.BASIC,  # Базовый тариф по умолчанию
                trial_days=0  # Без тестового периода
            )

            if not subscription_result["success"]:
                return subscription_result

            # 4. Отправляем уведомление об успешной оплате
            await self.notification_manager.send_payment_success_notification(
                family_id=family_id,
                subscription_tier=subscription_result["tier"],
                amount=payment_status.get("amount", 0)
            )

            # 5. Генерируем рекомендации
            recommendation = await self.personalization_agent.recommend_tariff(family_id)

            if recommendation["success"]:
                await self.notification_manager.send_tariff_recommendation(
                    family_id=family_id,
                    recommended_tariff=recommendation["recommendation_type"],
                    discount=recommendation.get("discount_percentage", 0)
                )

            logger.info(f"Платеж {payment_id} завершен, подписка активирована")

            return {
                "success": True,
                "payment_id": payment_id,
                "subscription_id": subscription_result["subscription_id"],
                "family_id": family_id,
                "amount": payment_status.get("amount", 0)
            }

        except Exception as e:
            logger.error(f"Ошибка завершения платежа: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_referral_link(self, family_id: str) -> Dict[str, Any]:
        """
        Генерация реферальной ссылки с уведомлениями

        Args:
            family_id: ID семьи

        Returns:
            Результат генерации ссылки
        """
        try:
            # 1. Генерируем реферальную ссылку
            referral_result = await self.referral_manager.generate_referral_link(family_id)

            if not referral_result["success"]:
                return referral_result

            # 2. Отправляем уведомление о создании ссылки
            await self.notification_manager.send_referral_notification(
                family_id=family_id,
                referral_code=referral_result["referral_code"],
                notification_type=NotificationType.REFERRAL_LINK_CREATED
            )

            logger.info(f"Создана реферальная ссылка для семьи {family_id}")

            return referral_result

        except Exception as e:
            logger.error(f"Ошибка генерации реферальной ссылки: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_ab_test(self, test_name: str, test_type: str,
                             variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Создание A/B теста с интеграцией

        Args:
            test_name: Название теста
            test_type: Тип теста
            variants: Варианты теста

        Returns:
            Результат создания теста
        """
        try:
            # 1. Создаем A/B тест
            test_result = await self.ab_testing_manager.create_test(
                name=test_name,
                description=f"A/B тест {test_name}",
                test_type=getattr(TestType, test_type.upper()),
                variants=variants,
                success_metrics=[],  # Будет заполнено автоматически
                min_sample_size=100,
                max_duration_days=7
            )

            if not test_result["success"]:
                return test_result

            # 2. Запускаем тест
            start_result = await self.ab_testing_manager.start_test(test_result["test_id"])

            if not start_result["success"]:
                return start_result

            logger.info(f"Создан A/B тест {test_name}")

            return test_result

        except Exception as e:
            logger.error(f"Ошибка создания A/B теста: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_personalized_recommendations(self, family_id: str) -> Dict[str, Any]:
        """
        Получение персонализированных рекомендаций

        Args:
            family_id: ID семьи

        Returns:
            Рекомендации для семьи
        """
        try:
            # 1. Получаем рекомендации от AI-агента
            recommendations = await self.personalization_agent.get_recommendations(family_id)

            # 2. Получаем профиль пользователя
            profile = await self.personalization_agent.get_user_profile(family_id)

            # 3. Получаем реферальную статистику
            referral_stats = await self.referral_manager.get_referral_stats(family_id)

            # 4. Получаем статистику подписок
            subscription_stats = await self.subscription_manager.get_subscription_stats()

            return {
                "success": True,
                "family_id": family_id,
                "recommendations": recommendations,
                "user_profile": profile,
                "referral_stats": referral_stats,
                "subscription_stats": subscription_stats
            }

        except Exception as e:
            logger.error(f"Ошибка получения рекомендаций: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_daily_tasks(self) -> Dict[str, Any]:
        """
        Обработка ежедневных задач монетизации

        Returns:
            Результат обработки задач
        """
        try:
            tasks_completed = {
                "trial_reminders": 0,
                "subscription_reminders": 0,
                "notifications_sent": 0,
                "ab_tests_checked": 0,
                "old_data_cleaned": 0
            }

            # 1. Обработка запланированных уведомлений
            notifications_sent = await self.notification_manager.process_scheduled_notifications()
            tasks_completed["notifications_sent"] = notifications_sent

            # 2. Проверка истечения тестовых периодов
            expired_trials = await self.subscription_manager.check_trial_expiry()
            tasks_completed["trial_reminders"] = len(expired_trials)

            # 3. Очистка старых данных
            old_notifications = await self.notification_manager.cleanup_old_notifications()
            old_subscriptions = await self.subscription_manager.cleanup_expired_subscriptions()
            tasks_completed["old_data_cleaned"] = old_notifications + old_subscriptions

            # 4. Проверка A/B тестов
            active_tests = await self.ab_testing_manager.get_active_tests()
            tasks_completed["ab_tests_checked"] = len(active_tests)

            # Проверяем завершенные тесты
            for test in active_tests:
                test_id = test["test_id"]
                results = await self.ab_testing_manager.get_test_results(test_id)

                if results["success"] and results.get(
                    "statistical_analysis",
                        {}).get("significance") != "not_significant":
                    # Тест завершен, можно применить результаты
                    await self.ab_testing_manager.complete_test(test_id)

            logger.info(f"Ежедневные задачи выполнены: {tasks_completed}")

            return {
                "success": True,
                "tasks_completed": tasks_completed,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка обработки ежедневных задач: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_monetization_stats(self) -> MonetizationStats:
        """
        Получение статистики системы монетизации

        Returns:
            Статистика монетизации
        """
        try:
            # Получаем статистику от всех менеджеров
            subscription_stats = await self.subscription_manager.get_subscription_stats()
            referral_stats = await self.referral_manager.get_global_referral_stats()
            ab_stats = await self.ab_testing_manager.get_manager_stats()
            notification_stats = await self.notification_manager.get_notification_stats()
            personalization_stats = await self.personalization_agent.get_agent_stats()

            # Формируем общую статистику
            stats = MonetizationStats(
                total_families=subscription_stats["total_subscriptions"],
                active_subscriptions=subscription_stats["active_subscriptions"],
                trial_subscriptions=subscription_stats["trial_subscriptions"],
                total_revenue=float(subscription_stats["total_revenue"]),
                conversion_rate=0.0,  # Будет рассчитано отдельно
                referral_signups=referral_stats["total_referrals"],
                ab_tests_active=ab_stats["active_tests"],
                notifications_sent=notification_stats["total_sent"],
                personalization_recommendations=personalization_stats["total_recommendations"]
            )

            # Рассчитываем конверсию
            if stats.total_families > 0:
                stats.conversion_rate = (stats.active_subscriptions / stats.total_families) * 100

            return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return MonetizationStats()

    async def health_check_all_components(self) -> Dict[str, Any]:
        """
        Проверка здоровья всех компонентов монетизации

        Returns:
            Статус всех компонентов
        """
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "components": {},
                "overall_status": "healthy"
            }

            # Проверяем каждый компонент
            components = {
                "subscription_manager": self.subscription_manager,
                "qr_payment_manager": self.qr_payment_manager,
                "referral_manager": self.referral_manager,
                "personalization_agent": self.personalization_agent,
                "ab_testing_manager": self.ab_testing_manager,
                "notification_manager": self.notification_manager
            }

            unhealthy_components = 0

            for name, component in components.items():
                try:
                    health = await component.health_check()
                    health_status["components"][name] = health

                    if health["status"] != "healthy":
                        unhealthy_components += 1

                except Exception as e:
                    health_status["components"][name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    unhealthy_components += 1

            # Определяем общий статус
            if unhealthy_components > 0:
                health_status["overall_status"] = "degraded" if unhealthy_components < len(components) else "unhealthy"

            return health_status

        except Exception as e:
            logger.error(f"Ошибка проверки здоровья компонентов: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "unhealthy",
                "error": str(e)
            }

    def get_status(self) -> ComponentStatus:
        """Получение статуса компонента"""
        return self.status

    def get_security_level(self) -> SecurityLevel:
        """Получение уровня безопасности"""
        return self.security_level

    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья интеграционного менеджера"""
        try:
            # Проверяем все компоненты
            components_health = await self.health_check_all_components()

            # Получаем статистику
            stats = await self.get_monetization_stats()

            return {
                "status": "healthy",
                "component": "MonetizationIntegrationManager",
                "timestamp": datetime.now().isoformat(),
                "components_health": components_health,
                "monetization_stats": {
                    "total_families": stats.total_families,
                    "active_subscriptions": stats.active_subscriptions,
                    "total_revenue": stats.total_revenue,
                    "conversion_rate": stats.conversion_rate
                },
                "memory_usage": "normal"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "component": "MonetizationIntegrationManager",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }


# Создание глобального экземпляра
monetization_integration_manager = MonetizationIntegrationManager()


async def main():
    """Тестирование MonetizationIntegrationManager"""
    print("🧪 Тестирование MonetizationIntegrationManager")
    print("=" * 60)

    # Тест создания подписки
    subscription_result = await monetization_integration_manager.create_family_subscription(
        family_id="test_family_123",
        subscription_tier=SubscriptionTier.BASIC,
        trial_days=7
    )
    print(f"Создание подписки: {subscription_result}")

    # Тест обработки платежа
    payment_result = await monetization_integration_manager.process_payment(
        family_id="test_family_123",
        subscription_tier="basic",
        amount=290.0
    )
    print(f"Обработка платежа: {payment_result}")

    # Тест генерации реферальной ссылки
    referral_result = await monetization_integration_manager.generate_referral_link("test_family_123")
    print(f"Генерация реферальной ссылки: {referral_result}")

    # Тест получения рекомендаций
    recommendations = await monetization_integration_manager.get_personalized_recommendations("test_family_123")
    print(f"Персонализированные рекомендации: {recommendations['success']}")

    # Тест ежедневных задач
    daily_tasks = await monetization_integration_manager.process_daily_tasks()
    print(f"Ежедневные задачи: {daily_tasks}")

    # Тест статистики
    stats = await monetization_integration_manager.get_monetization_stats()
    print(f"Статистика монетизации: {stats}")

    # Тест проверки здоровья
    health = await monetization_integration_manager.health_check_all_components()
    print(f"Проверка здоровья: {health['overall_status']}")


if __name__ == "__main__":
    asyncio.run(main())
