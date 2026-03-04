#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubscriptionManager - Менеджер подписок и тарифных планов ALADDIN
Версия 1.0 - Полная система управления подписками с QR-код оплатой

Интегрируется с:
- FamilyProfileManagerEnhanced (семейные профили)
- QRPaymentManager (QR-код оплата)
- FamilyNotificationManager (уведомления)
- PersonalizationAgent (AI-персонализация)

Автор: ALADDIN Security System
Версия: 1.0.0
Дата: 2025-01-27
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from decimal import Decimal

from security.core.security_base import ComponentStatus, SecurityBase, SecurityLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubscriptionTier(Enum):
    """Тарифные планы подписок"""
    FREEMIUM = "freemium"      # Бесплатный
    BASIC = "basic"            # 290₽/месяц
    BASIC_3M = "basic_3m"      # 783₽ за 3 месяца (скидка 10%)
    BASIC_6M = "basic_6m"      # 1479₽ за 6 месяцев (скидка 15%)
    BASIC_12M = "basic_12m"    # 2784₽ за 12 месяцев (скидка 20%)
    FAMILY = "family"          # 490₽/месяц
    FAMILY_3M = "family_3m"    # 1323₽ за 3 месяца (скидка 10%)
    FAMILY_6M = "family_6m"    # 2499₽ за 6 месяцев (скидка 15%)
    FAMILY_12M = "family_12m"  # 4704₽ за 12 месяцев (скидка 20%)
    PREMIUM = "premium"        # 900₽/месяц
    PREMIUM_3M = "premium_3m"  # 2430₽ за 3 месяца (скидка 10%)
    PREMIUM_6M = "premium_6m"  # 4590₽ за 6 месяцев (скидка 15%)
    PREMIUM_12M = "premium_12m"  # 8640₽ за 12 месяцев (скидка 20%)
    CUSTOM = "custom"          # 1500₽/месяц


class SubscriptionStatus(Enum):
    """Статусы подписки"""
    ACTIVE = "active"          # Активная
    TRIAL = "trial"            # Тестовый период
    EXPIRED = "expired"        # Истекла
    CANCELLED = "cancelled"    # Отменена
    SUSPENDED = "suspended"    # Приостановлена
    PENDING = "pending"        # Ожидает оплаты


class PaymentStatus(Enum):
    """Статусы оплаты"""
    PENDING = "pending"        # Ожидает оплаты
    PROCESSING = "processing"  # Обрабатывается
    COMPLETED = "completed"    # Завершена
    FAILED = "failed"          # Неудачная
    REFUNDED = "refunded"      # Возвращена


class Features(Enum):
    """Функции системы безопасности"""
    # Freemium (бесплатно)
    BASIC_VPN = "basic_vpn"                    # 100MB/день
    BASIC_ANTIVIRUS = "basic_antivirus"        # Базовый антивирус
    BASIC_FAMILY_CONTROL = "basic_family_control"  # Базовый родительский контроль
    PHISHING_PROTECTION = "phishing_protection"    # Защита от фишинга
    AD_BLOCKING = "ad_blocking"                # Блокировка рекламы
    SAFE_SEARCH = "safe_search"                # Безопасный поиск
    BASIC_NOTIFICATIONS = "basic_notifications"    # Базовые уведомления

    # Basic (290₽/месяц)
    UNLIMITED_VPN = "unlimited_vpn"            # VPN безлимит
    ADVANCED_ANTIVIRUS = "advanced_antivirus"  # Расширенный антивирус
    PARENTAL_CONTROL_8_FUNCTIONS = "parental_control_8_functions"  # 8 функций родительского контроля
    CHILD_PROTECTION_6_FUNCTIONS = "child_protection_6_functions"  # 6 функций защиты детей
    ELDERLY_PROTECTION_8_FUNCTIONS = "elderly_protection_8_functions"  # 8 функций защиты пожилых
    FAMILY_PROFILES_5_FUNCTIONS = "family_profiles_5_functions"    # 5 функций семейных профилей
    AI_BEHAVIOR_ANALYSIS = "ai_behavior_analysis"  # AI анализ поведения
    FRAUD_PROTECTION = "fraud_protection"      # Защита от мошенничества
    DEEPFAKE_DETECTION = "deepfake_detection"  # Детекция deepfake
    EMERGENCY_RESPONSE = "emergency_response"  # Экстренное реагирование
    GAMING_SECURITY = "gaming_security"        # Игровая безопасность
    DEVICE_PROTECTION = "device_protection"    # Защита устройств
    SOCIAL_NETWORKS = "social_networks"        # Социальные сети
    TRAFFIC_ENCRYPTION = "traffic_encryption"  # Шифрование трафика
    ANONYMITY = "anonymity"                    # Анонимность
    LEAK_PROTECTION = "leak_protection"        # Защита от утечек
    FILE_SCANNING = "file_scanning"            # Сканирование файлов
    VIRUS_DETECTION = "virus_detection"        # Детекция вирусов
    THREAT_QUARANTINE = "threat_quarantine"    # Карантин угроз
    UPDATES = "updates"                        # Обновления
    PRIORITY_SUPPORT = "priority_support"      # Приоритетная поддержка

    # Family (490₽/месяц)
    UP_TO_6_DEVICES = "up_to_6_devices"       # До 6 устройств
    ADVANCED_PARENTAL_CONTROL = "advanced_parental_control"  # Расширенный родительский контроль
    ADVANCED_CHILD_PROTECTION = "advanced_child_protection"  # Продвинутая защита детей
    ADVANCED_ELDERLY_PROTECTION = "advanced_elderly_protection"  # Улучшенная защита пожилых
    FAMILY_GROUPS_ROLES = "family_groups_roles"  # Семейные группы и роли
    CENTRALIZED_MANAGEMENT = "centralized_management"  # Централизованное управление
    FAMILY_ANALYTICS = "family_analytics"     # Семейная аналитика
    GAMIFICATION = "gamification"             # Геймификация для детей
    EDUCATIONAL_CONTENT = "educational_content"  # Образовательный контент
    PSYCHOLOGICAL_SUPPORT = "psychological_support"  # Психологическая поддержка
    FAMILY_NOTIFICATIONS = "family_notifications"  # Семейные уведомления
    EMERGENCY_CONTACTS = "emergency_contacts"  # Экстренные контакты
    MEDICAL_REMINDERS = "medical_reminders"    # Медицинские напоминания
    TECHNICAL_SUPPORT = "technical_support"    # Техническая поддержка
    VOICE_CONTROL = "voice_control"           # Голосовое управление
    FAMILY_REFERRAL_SYSTEM = "family_referral_system"  # Семейная реферальная система

    # Premium (900₽/месяц)
    PREDICTIVE_PROTECTION = "predictive_protection"  # Предиктивная защита
    MACHINE_LEARNING = "machine_learning"     # Машинное обучение
    ADVANCED_ANALYTICS = "advanced_analytics"  # Продвинутая аналитика
    CUSTOM_INTEGRATIONS = "custom_integrations"  # Кастомные интеграции
    API_ACCESS = "api_access"                 # API доступ
    WHITELIST_IP = "whitelist_ip"             # Белый список IP
    CUSTOM_RULES = "custom_rules"             # Кастомные правила
    EXTENDED_REPORTING = "extended_reporting"  # Расширенная отчетность
    IOT_PROTECTION = "iot_protection"         # Интеграция с IoT
    SMART_HOME = "smart_home"                 # Умный дом
    CAR_SECURITY = "car_security"             # Автомобильная безопасность
    PERSONAL_AI_ASSISTANT = "personal_ai_assistant"  # Персональный AI-помощник
    SUPPORT_24_7 = "support_24_7"             # Приоритетная поддержка 24/7

    # Custom (1500₽/месяц)
    UP_TO_50_USERS = "up_to_50_users"        # До 50 сотрудников
    CENTRALIZED_MANAGEMENT_CORP = "centralized_management_corp"  # Централизованное управление
    CUSTOM_INTEGRATIONS_CORP = "custom_integrations_corp"  # Кастомные интеграции
    API_ACCESS_CORP = "api_access_corp"       # API доступ
    WHITELIST_IP_CORP = "whitelist_ip_corp"   # Белый список IP
    CUSTOM_RULES_CORP = "custom_rules_corp"   # Кастомные правила
    EXTENDED_REPORTING_CORP = "extended_reporting_corp"  # Расширенная отчетность
    CORPORATE_INTEGRATIONS = "corporate_integrations"  # Интеграция с корпоративными системами
    USER_MANAGEMENT = "user_management"       # Управление пользователями
    ROLES_PERMISSIONS = "roles_permissions"   # Роли и права доступа
    SECURITY_AUDIT = "security_audit"         # Аудит безопасности
    COMPLIANCE_STANDARDS = "compliance_standards"  # Соответствие стандартам
    SUPPORT_24_7_CORP = "support_24_7_corp"   # Техническая поддержка 24/7
    PERSONAL_MANAGER = "personal_manager"     # Персональный менеджер


@dataclass
class SubscriptionPlan:
    """План подписки"""
    tier: SubscriptionTier
    name: str
    price: Decimal
    currency: str = "RUB"
    billing_period: str = "monthly"  # monthly, 3months, 6months, 12months, yearly
    period_months: int = 1  # 1, 3, 6, 12
    discount_percent: Optional[int] = None  # Процент скидки
    original_price: Optional[Decimal] = None  # Цена без скидки
    trial_days: int = 0
    max_devices: int = 1
    features: Set[Features] = field(default_factory=set)
    description: str = ""
    is_active: bool = True
    
    @property
    def monthly_price(self) -> Decimal:
        """Цена за месяц (для сравнения)"""
        return self.price / Decimal(self.period_months)
    
    @property
    def savings(self) -> Optional[Decimal]:
        """Экономия при долгосрочной подписке"""
        if self.original_price:
            return self.original_price - self.price
        return None


@dataclass
class Subscription:
    """Подписка пользователя"""
    subscription_id: str
    family_id: str
    tier: SubscriptionTier
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime]
    trial_end_date: Optional[datetime]
    auto_renew: bool = True
    payment_status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Payment:
    """Платеж"""
    payment_id: str
    subscription_id: str
    amount: Decimal
    currency: str = "RUB"
    status: PaymentStatus
    payment_method: str = "qr_code"
    qr_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SubscriptionManager(SecurityBase):
    """
    Менеджер подписок и тарифных планов ALADDIN

    Управляет:
    - Тарифными планами
    - Подписками пользователей
    - Платежами
    - Доступом к функциям
    - Тестовыми периодами
    """

    def __init__(self):
        """Инициализация менеджера подписок"""
        super().__init__()
        self.subscriptions: Dict[str, Subscription] = {}
        self.payments: Dict[str, Payment] = {}
        self.plans: Dict[SubscriptionTier, SubscriptionPlan] = {}
        self.feature_gates: Dict[str, Set[Features]] = {}
        self.trial_periods: Dict[str, datetime] = {}

        # Инициализация тарифных планов
        self._initialize_plans()

        # Статус компонента
        self.status = ComponentStatus.ACTIVE
        self.security_level = SecurityLevel.HIGH

        logger.info("SubscriptionManager инициализирован")

    def _initialize_plans(self) -> None:
        """Инициализация тарифных планов"""

        # FREEMIUM (бесплатно)
        self.plans[SubscriptionTier.FREEMIUM] = SubscriptionPlan(
            tier=SubscriptionTier.FREEMIUM,
            name="Freemium",
            price=Decimal("0"),
            trial_days=0,
            max_devices=1,
            features={
                Features.BASIC_VPN,
                Features.BASIC_ANTIVIRUS,
                Features.BASIC_FAMILY_CONTROL,
                Features.PHISHING_PROTECTION,
                Features.AD_BLOCKING,
                Features.SAFE_SEARCH,
                Features.BASIC_NOTIFICATIONS
            },
            description="Базовые функции безопасности бесплатно"
        )

        # BASIC (290₽/месяц)
        self.plans[SubscriptionTier.BASIC] = SubscriptionPlan(
            tier=SubscriptionTier.BASIC,
            name="Basic",
            price=Decimal("290"),
            trial_days=30,  # ИЗМЕНЕНО: 30 дней вместо 7
            max_devices=4,
            features={
                # Все из Freemium
                Features.BASIC_VPN,
                Features.BASIC_ANTIVIRUS,
                Features.BASIC_FAMILY_CONTROL,
                Features.PHISHING_PROTECTION,
                Features.AD_BLOCKING,
                Features.SAFE_SEARCH,
                Features.BASIC_NOTIFICATIONS,
                # Дополнительные функции
                Features.UNLIMITED_VPN,
                Features.ADVANCED_ANTIVIRUS,
                Features.PARENTAL_CONTROL_8_FUNCTIONS,
                Features.CHILD_PROTECTION_6_FUNCTIONS,
                Features.ELDERLY_PROTECTION_8_FUNCTIONS,
                Features.FAMILY_PROFILES_5_FUNCTIONS,
                Features.AI_BEHAVIOR_ANALYSIS,
                Features.FRAUD_PROTECTION,
                Features.DEEPFAKE_DETECTION,
                Features.EMERGENCY_RESPONSE,
                Features.GAMING_SECURITY,
                Features.DEVICE_PROTECTION,
                Features.SOCIAL_NETWORKS,
                Features.TRAFFIC_ENCRYPTION,
                Features.ANONYMITY,
                Features.LEAK_PROTECTION,
                Features.FILE_SCANNING,
                Features.VIRUS_DETECTION,
                Features.THREAT_QUARANTINE,
                Features.UPDATES,
                Features.PRIORITY_SUPPORT
            },
            description="Расширенные функции безопасности для семьи"
        )

        # FAMILY (490₽/месяц)
        self.plans[SubscriptionTier.FAMILY] = SubscriptionPlan(
            tier=SubscriptionTier.FAMILY,
            name="Family",
            price=Decimal("490"),
            trial_days=30,  # ИЗМЕНЕНО: 30 дней вместо 14
            max_devices=6,
            features={
                # Все из Basic
                *self.plans[SubscriptionTier.BASIC].features,
                # Дополнительные семейные функции
                Features.UP_TO_6_DEVICES,
                Features.ADVANCED_PARENTAL_CONTROL,
                Features.ADVANCED_CHILD_PROTECTION,
                Features.ADVANCED_ELDERLY_PROTECTION,
                Features.FAMILY_GROUPS_ROLES,
                Features.CENTRALIZED_MANAGEMENT,
                Features.FAMILY_ANALYTICS,
                Features.GAMIFICATION,
                Features.EDUCATIONAL_CONTENT,
                Features.PSYCHOLOGICAL_SUPPORT,
                Features.FAMILY_NOTIFICATIONS,
                Features.EMERGENCY_CONTACTS,
                Features.MEDICAL_REMINDERS,
                Features.TECHNICAL_SUPPORT,
                Features.VOICE_CONTROL,
                Features.FAMILY_REFERRAL_SYSTEM
            },
            description="Полная семейная защита с геймификацией"
        )

        # PREMIUM (900₽/месяц)
        self.plans[SubscriptionTier.PREMIUM] = SubscriptionPlan(
            tier=SubscriptionTier.PREMIUM,
            name="Premium",
            price=Decimal("900"),
            trial_days=30,  # ИЗМЕНЕНО: 30 дней вместо 14
            max_devices=6,
            features={
                # Все из Family
                *self.plans[SubscriptionTier.FAMILY].features,
                # Дополнительные премиум функции
                Features.PREDICTIVE_PROTECTION,
                Features.MACHINE_LEARNING,
                Features.ADVANCED_ANALYTICS,
                Features.CUSTOM_INTEGRATIONS,
                Features.API_ACCESS,
                Features.WHITELIST_IP,
                Features.CUSTOM_RULES,
                Features.EXTENDED_REPORTING,
                Features.IOT_PROTECTION,
                Features.SMART_HOME,
                Features.CAR_SECURITY,
                Features.PERSONAL_AI_ASSISTANT,
                Features.SUPPORT_24_7
            },
            description="Продвинутая защита с AI и IoT"
        )

        # CUSTOM (1500₽/месяц)
        self.plans[SubscriptionTier.CUSTOM] = SubscriptionPlan(
            tier=SubscriptionTier.CUSTOM,
            name="Custom",
            price=Decimal("1500"),
            trial_days=30,  # ИЗМЕНЕНО: 30 дней вместо 14
            max_devices=50,
            features={
                # Все из Premium
                *self.plans[SubscriptionTier.PREMIUM].features,
                # Дополнительные корпоративные функции
                Features.UP_TO_50_USERS,
                Features.CENTRALIZED_MANAGEMENT_CORP,
                Features.CUSTOM_INTEGRATIONS_CORP,
                Features.API_ACCESS_CORP,
                Features.WHITELIST_IP_CORP,
                Features.CUSTOM_RULES_CORP,
                Features.EXTENDED_REPORTING_CORP,
                Features.CORPORATE_INTEGRATIONS,
                Features.USER_MANAGEMENT,
                Features.ROLES_PERMISSIONS,
                Features.SECURITY_AUDIT,
                Features.COMPLIANCE_STANDARDS,
                Features.SUPPORT_24_7_CORP,
                Features.PERSONAL_MANAGER
            },
            description="Корпоративная защита с персональным менеджером"
        )

    
        # BASIC 3 месяца (783₽, скидка 10%)
        self.plans[SubscriptionTier.BASIC_3M] = SubscriptionPlan(
            tier=SubscriptionTier.BASIC_3M,
            name="Basic 3 месяца",
            price=Decimal("783"),
            currency="RUB",
            billing_period="3months",
            period_months=3,
            discount_percent=10,
            original_price=Decimal("870"),  # 290 * 3
            trial_days=30,
            max_devices=4,
            features=self.plans[SubscriptionTier.BASIC].features.copy(),
            description="Basic на 3 месяца со скидкой 10%"
        )

        # BASIC 6 месяцев (1479₽, скидка 15%)
        self.plans[SubscriptionTier.BASIC_6M] = SubscriptionPlan(
            tier=SubscriptionTier.BASIC_6M,
            name="Basic 6 месяцев",
            price=Decimal("1479"),
            currency="RUB",
            billing_period="6months",
            period_months=6,
            discount_percent=15,
            original_price=Decimal("1740"),  # 290 * 6
            trial_days=30,
            max_devices=4,
            features=self.plans[SubscriptionTier.BASIC].features.copy(),
            description="Basic на 6 месяцев со скидкой 15%"
        )

        # BASIC 12 месяцев (2780₽, скидка 20%, экономия 700₽)
        self.plans[SubscriptionTier.BASIC_12M] = SubscriptionPlan(
            tier=SubscriptionTier.BASIC_12M,
            name="Basic 12 месяцев",
            price=Decimal("2780"),
            currency="RUB",
            billing_period="12months",
            period_months=12,
            discount_percent=20,
            original_price=Decimal("3480"),  # 290 * 12
            trial_days=30,
            max_devices=4,
            features=self.plans[SubscriptionTier.BASIC].features.copy(),
            description="Basic на 12 месяцев со скидкой 20%"
        )

        # FAMILY 3 месяца (1323₽, скидка 10%)
        self.plans[SubscriptionTier.FAMILY_3M] = SubscriptionPlan(
            tier=SubscriptionTier.FAMILY_3M,
            name="Family 3 месяца",
            price=Decimal("1323"),
            currency="RUB",
            billing_period="3months",
            period_months=3,
            discount_percent=10,
            original_price=Decimal("1470"),  # 490 * 3
            trial_days=30,
            max_devices=6,
            features=self.plans[SubscriptionTier.FAMILY].features.copy(),
            description="Family на 3 месяца со скидкой 10%"
        )

        # FAMILY 6 месяцев (2499₽, скидка 15%)
        self.plans[SubscriptionTier.FAMILY_6M] = SubscriptionPlan(
            tier=SubscriptionTier.FAMILY_6M,
            name="Family 6 месяцев",
            price=Decimal("2499"),
            currency="RUB",
            billing_period="6months",
            period_months=6,
            discount_percent=15,
            original_price=Decimal("2940"),  # 490 * 6
            trial_days=30,
            max_devices=6,
            features=self.plans[SubscriptionTier.FAMILY].features.copy(),
            description="Family на 6 месяцев со скидкой 15%"
        )

        # FAMILY 12 месяцев (4704₽, скидка 20%)
        self.plans[SubscriptionTier.FAMILY_12M] = SubscriptionPlan(
            tier=SubscriptionTier.FAMILY_12M,
            name="Family 12 месяцев",
            price=Decimal("4704"),
            currency="RUB",
            billing_period="12months",
            period_months=12,
            discount_percent=20,
            original_price=Decimal("5880"),  # 490 * 12
            trial_days=30,
            max_devices=6,
            features=self.plans[SubscriptionTier.FAMILY].features.copy(),
            description="Family на 12 месяцев со скидкой 20%"
        )

        # PREMIUM 3 месяца (2430₽, скидка 10%)
        self.plans[SubscriptionTier.PREMIUM_3M] = SubscriptionPlan(
            tier=SubscriptionTier.PREMIUM_3M,
            name="Premium 3 месяца",
            price=Decimal("2430"),
            currency="RUB",
            billing_period="3months",
            period_months=3,
            discount_percent=10,
            original_price=Decimal("2700"),  # 900 * 3
            trial_days=30,
            max_devices=6,
            features=self.plans[SubscriptionTier.PREMIUM].features.copy(),
            description="Premium на 3 месяца со скидкой 10%"
        )

        # PREMIUM 6 месяцев (4590₽, скидка 15%)
        self.plans[SubscriptionTier.PREMIUM_6M] = SubscriptionPlan(
            tier=SubscriptionTier.PREMIUM_6M,
            name="Premium 6 месяцев",
            price=Decimal("4590"),
            currency="RUB",
            billing_period="6months",
            period_months=6,
            discount_percent=15,
            original_price=Decimal("5400"),  # 900 * 6
            trial_days=30,
            max_devices=6,
            features=self.plans[SubscriptionTier.PREMIUM].features.copy(),
            description="Premium на 6 месяцев со скидкой 15%"
        )

        # PREMIUM 12 месяцев (8640₽, скидка 20%)
        self.plans[SubscriptionTier.PREMIUM_12M] = SubscriptionPlan(
            tier=SubscriptionTier.PREMIUM_12M,
            name="Premium 12 месяцев",
            price=Decimal("8640"),
            currency="RUB",
            billing_period="12months",
            period_months=12,
            discount_percent=20,
            original_price=Decimal("10800"),  # 900 * 12
            trial_days=30,
            max_devices=6,
            features=self.plans[SubscriptionTier.PREMIUM].features.copy(),
            description="Premium на 12 месяцев со скидкой 20%"
        )

    async def create_subscription(self, family_id: str, tier: SubscriptionTier,
                                  trial_days: Optional[int] = None,
                                  period_months: Optional[int] = None) -> Dict[str, Any]:
        """
        Создание новой подписки

        Args:
            family_id: ID семьи
            tier: Тарифный план
            trial_days: Дни тестового периода (если None, используется из плана)

        Returns:
            Информация о созданной подписке
        """
        try:
            # Проверяем, есть ли уже активная подписка
            existing_subscription = await self.get_active_subscription(family_id)
            if existing_subscription:
                return {
                    "success": False,
                    "error": "У семьи уже есть активная подписка",
                    "subscription_id": existing_subscription.subscription_id
                }

            # Получаем план
            plan = self.plans.get(tier)
            if not plan:
                return {
                    "success": False,
                    "error": f"Тарифный план {tier.value} не найден"
                }

            # Определяем тестовый период
            trial_days = trial_days if trial_days is not None else plan.trial_days

            # Создаем подписку
            subscription_id = str(uuid.uuid4())
            now = datetime.now()

            # Определяем даты
            if trial_days > 0:
                trial_end_date = now + timedelta(days=trial_days)
                end_date = None
                status = SubscriptionStatus.TRIAL
            else:
                trial_end_date = None
                # Определяем период подписки
                if period_months is not None and period_months > 0:
                    # Используем указанный период
                    subscription_days = period_months * 30
                else:
                    # Используем период из плана
                    plan_period_months = plan.period_months if hasattr(plan, 'period_months') else 1
                    subscription_days = plan_period_months * 30
                
                end_date = now + timedelta(days=subscription_days)
                status = SubscriptionStatus.ACTIVE

            subscription = Subscription(
                subscription_id=subscription_id,
                family_id=family_id,
                tier=tier,
                status=status,
                start_date=now,
                end_date=end_date,
                trial_end_date=trial_end_date,
                auto_renew=True
            )

            # Сохраняем подписку
            self.subscriptions[subscription_id] = subscription

            # Инициализируем доступ к функциям
            self.feature_gates[family_id] = plan.features.copy()

            # Если есть тестовый период, сохраняем его
            if trial_days > 0:
                self.trial_periods[family_id] = trial_end_date

            logger.info(f"Создана подписка {subscription_id} для семьи {family_id}, тариф {tier.value}")

            return {
                "success": True,
                "subscription_id": subscription_id,
                "tier": tier.value,
                "status": status.value,
                "trial_days": trial_days,
                "trial_end_date": trial_end_date.isoformat() if trial_end_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "features_count": len(plan.features)
            }

        except Exception as e:
            logger.error(f"Ошибка создания подписки: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_active_subscription(self, family_id: str) -> Optional[Subscription]:
        """Получение активной подписки семьи"""
        for subscription in self.subscriptions.values():
            if (subscription.family_id == family_id and
                    subscription.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]):
                return subscription
        return None

    async def check_feature_access(self, family_id: str, feature: Features) -> bool:
        """
        Проверка доступа к функции

        Args:
            family_id: ID семьи
            feature: Функция для проверки

        Returns:
            True если доступ разрешен
        """
        try:
            # Получаем активную подписку
            subscription = await self.get_active_subscription(family_id)
            if not subscription:
                # Если нет подписки, проверяем только бесплатные функции
                freemium_features = self.plans[SubscriptionTier.FREEMIUM].features
                return feature in freemium_features

            # Получаем доступные функции
            available_features = self.feature_gates.get(family_id, set())

            # Проверяем доступ
            has_access = feature in available_features

            logger.debug(f"Проверка доступа семьи {family_id} к функции {feature.value}: {has_access}")

            return has_access

        except Exception as e:
            logger.error(f"Ошибка проверки доступа к функции: {e}")
            return False

    async def upgrade_subscription(self, family_id: str, new_tier: SubscriptionTier) -> Dict[str, Any]:
        """
        Обновление подписки на более высокий тариф

        Args:
            family_id: ID семьи
            new_tier: Новый тарифный план

        Returns:
            Результат обновления
        """
        try:
            # Получаем текущую подписку
            current_subscription = await self.get_active_subscription(family_id)
            if not current_subscription:
                return {
                    "success": False,
                    "error": "У семьи нет активной подписки"
                }

            # Проверяем, что новый тариф выше текущего
            tier_hierarchy = {
                SubscriptionTier.FREEMIUM: 0,
                SubscriptionTier.BASIC: 1,
                SubscriptionTier.FAMILY: 2,
                SubscriptionTier.PREMIUM: 3,
                SubscriptionTier.CUSTOM: 4
            }

            current_level = tier_hierarchy.get(current_subscription.tier, 0)
            new_level = tier_hierarchy.get(new_tier, 0)

            if new_level <= current_level:
                return {
                    "success": False,
                    "error": "Новый тариф должен быть выше текущего"
                }

            # Получаем новый план
            new_plan = self.plans.get(new_tier)
            if not new_plan:
                return {
                    "success": False,
                    "error": f"Тарифный план {new_tier.value} не найден"
                }

            # Обновляем подписку
            current_subscription.tier = new_tier
            current_subscription.updated_at = datetime.now()

            # Обновляем доступ к функциям
            self.feature_gates[family_id] = new_plan.features.copy()

            logger.info(f"Подписка семьи {family_id} обновлена с {current_subscription.tier.value} на {new_tier.value}")

            return {
                "success": True,
                "old_tier": current_subscription.tier.value,
                "new_tier": new_tier.value,
                "new_features_count": len(new_plan.features),
                "price": float(new_plan.price)
            }

        except Exception as e:
            logger.error(f"Ошибка обновления подписки: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def cancel_subscription(self, family_id: str) -> Dict[str, Any]:
        """
        Отмена подписки

        Args:
            family_id: ID семьи

        Returns:
            Результат отмены
        """
        try:
            # Получаем активную подписку
            subscription = await self.get_active_subscription(family_id)
            if not subscription:
                return {
                    "success": False,
                    "error": "У семьи нет активной подписки"
                }

            # Отменяем подписку
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.updated_at = datetime.now()
            subscription.auto_renew = False

            # Оставляем только бесплатные функции
            freemium_features = self.plans[SubscriptionTier.FREEMIUM].features
            self.feature_gates[family_id] = freemium_features.copy()

            logger.info(f"Подписка семьи {family_id} отменена")

            return {
                "success": True,
                "subscription_id": subscription.subscription_id,
                "cancelled_at": subscription.updated_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка отмены подписки: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def check_trial_expiry(self) -> List[Dict[str, Any]]:
        """
        Проверка истечения тестовых периодов

        Returns:
            Список истекших тестовых периодов
        """
        expired_trials = []
        now = datetime.now()

        for family_id, trial_end_date in self.trial_periods.items():
            if now >= trial_end_date:
                # Получаем подписку
                subscription = await self.get_active_subscription(family_id)
                if subscription and subscription.status == SubscriptionStatus.TRIAL:
                    # Переводим в статус "истекла"
                    subscription.status = SubscriptionStatus.EXPIRED
                    subscription.updated_at = now

                    # Оставляем только бесплатные функции
                    freemium_features = self.plans[SubscriptionTier.FREEMIUM].features
                    self.feature_gates[family_id] = freemium_features.copy()

                    expired_trials.append({
                        "family_id": family_id,
                        "subscription_id": subscription.subscription_id,
                        "tier": subscription.tier.value,
                        "expired_at": trial_end_date.isoformat()
                    })

                    logger.info(f"Тестовый период семьи {family_id} истек")

        return expired_trials

    async def check_expiring_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Проверка подписок, заканчивающихся через 3 и 1 день

        Returns:
            Список подписок с информацией о днях до окончания
        """
        expiring_subscriptions = []
        now = datetime.now()

        for subscription in self.subscriptions.values():
            if subscription.status != SubscriptionStatus.ACTIVE:
                continue

            if not subscription.end_date:
                continue

            days_until_expiry = (subscription.end_date - now).days

            if days_until_expiry in [3, 1]:
                expiring_subscriptions.append({
                    "subscription_id": subscription.subscription_id,
                    "family_id": subscription.family_id,
                    "tier": subscription.tier.value,
                    "days_until_expiry": days_until_expiry,
                    "end_date": subscription.end_date.isoformat()
                })

        return expiring_subscriptions

    async def send_subscription_renewal_notification(
        self,
        family_id: str,
        days_until_expiry: int,
        tier: SubscriptionTier
    ) -> bool:
        """
        Отправка уведомления о приближающемся окончании подписки

        Args:
            family_id: ID семьи
            days_until_expiry: Дней до окончания (3 или 1)
            tier: Тарифный план

        Returns:
            True если уведомление отправлено успешно
        """
        try:
            # Импортируем только при необходимости (избегаем циклических импортов)
            try:
                from security.family.family_notification_manager_enhanced import (
                    family_notification_manager_enhanced,
                    NotificationType,
                    NotificationPriority,
                    NotificationChannel
                )
            except ImportError:
                logger.warning("FamilyNotificationManagerEnhanced не найден, уведомления не будут отправлены")
                return False

            # Определяем текст уведомления
            if days_until_expiry == 3:
                title = "Подписка заканчивается через 3 дня"
                message = f"Ваша подписка {tier.value} заканчивается через 3 дня. Продлите подписку, чтобы продолжить пользоваться сервисом."
            elif days_until_expiry == 1:
                title = "Подписка заканчивается завтра"
                message = f"Ваша подписка {tier.value} заканчивается завтра. Продлите подписку сейчас, чтобы не потерять доступ к функциям."
            else:
                return False

            # Отправляем уведомление
            await family_notification_manager_enhanced.send_family_alert(
                family_id=family_id,
                notification_type=NotificationType.SUBSCRIPTION_EXPIRING,
                priority=NotificationPriority.HIGH,
                title=title,
                message=message,
                channels=[NotificationChannel.IN_APP],
                metadata={
                    "days_until_expiry": days_until_expiry,
                    "subscription_tier": tier.value,
                    "type": "subscription_renewal"
                },
                action_required=True,
                action_url="/tariffs"  # Ссылка на экран тарифов
            )

            logger.info(f"Отправлено уведомление о подписке для семьи {family_id}, дней до окончания: {days_until_expiry}")
            return True

        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о подписке: {e}")
            return False

    async def check_and_send_renewal_notifications(self) -> Dict[str, Any]:
        """
        Проверка подписок и отправка уведомлений о приближающемся окончании

        Returns:
            Статистика отправленных уведомлений
        """
        try:
            expiring_subscriptions = await self.check_expiring_subscriptions()

            sent_count = 0
            failed_count = 0

            for subscription_info in expiring_subscriptions:
                success = await self.send_subscription_renewal_notification(
                    family_id=subscription_info["family_id"],
                    days_until_expiry=subscription_info["days_until_expiry"],
                    tier=SubscriptionTier(subscription_info["tier"])
                )

                if success:
                    sent_count += 1
                else:
                    failed_count += 1

            logger.info(f"Проверка подписок завершена: отправлено {sent_count}, ошибок {failed_count}")

            return {
                "success": True,
                "checked": len(expiring_subscriptions),
                "sent": sent_count,
                "failed": failed_count,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка проверки и отправки уведомлений: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_subscription_stats(self) -> Dict[str, Any]:
        """Получение статистики подписок"""
        stats = {
            "total_subscriptions": len(self.subscriptions),
            "active_subscriptions": 0,
            "trial_subscriptions": 0,
            "expired_subscriptions": 0,
            "cancelled_subscriptions": 0,
            "by_tier": {},
            "total_revenue": Decimal("0")
        }

        for subscription in self.subscriptions.values():
            # Подсчет по статусам
            if subscription.status == SubscriptionStatus.ACTIVE:
                stats["active_subscriptions"] += 1
            elif subscription.status == SubscriptionStatus.TRIAL:
                stats["trial_subscriptions"] += 1
            elif subscription.status == SubscriptionStatus.EXPIRED:
                stats["expired_subscriptions"] += 1
            elif subscription.status == SubscriptionStatus.CANCELLED:
                stats["cancelled_subscriptions"] += 1

            # Подсчет по тарифам
            tier_name = subscription.tier.value
            stats["by_tier"][tier_name] = stats["by_tier"].get(tier_name, 0) + 1

            # Подсчет доходов (только для активных подписок)
            if subscription.status == SubscriptionStatus.ACTIVE:
                plan = self.plans.get(subscription.tier)
                if plan:
                    stats["total_revenue"] += plan.price

        return stats

    async def get_available_plans(self) -> List[Dict[str, Any]]:
        """Получение доступных тарифных планов"""
        plans = []

        for tier, plan in self.plans.items():
            if plan.is_active:
                plans.append({
                    "tier": tier.value,
                    "name": plan.name,
                    "price": float(plan.price),
                    "currency": plan.currency,
                    "billing_period": plan.billing_period,
                    "trial_days": plan.trial_days,
                    "max_devices": plan.max_devices,
                    "features_count": len(plan.features),
                    "description": plan.description
                })

        return plans

    async def cleanup_expired_subscriptions(self) -> int:
        """Очистка истекших подписок"""
        cleaned_count = 0
        now = datetime.now()

        for subscription in list(self.subscriptions.values()):
            if (subscription.status == SubscriptionStatus.EXPIRED and
                    subscription.end_date and now > subscription.end_date):

                # Удаляем подписку
                del self.subscriptions[subscription.subscription_id]

                # Очищаем доступ к функциям
                if subscription.family_id in self.feature_gates:
                    del self.feature_gates[subscription.family_id]

                cleaned_count += 1
                logger.info(f"Удалена истекшая подписка {subscription.subscription_id}")

        return cleaned_count

    def get_status(self) -> ComponentStatus:
        """Получение статуса компонента"""
        return self.status

    def get_security_level(self) -> SecurityLevel:
        """Получение уровня безопасности"""
        return self.security_level

    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья компонента"""
        try:
            stats = await self.get_subscription_stats()

            return {
                "status": "healthy",
                "component": "SubscriptionManager",
                "timestamp": datetime.now().isoformat(),
                "stats": stats,
                "memory_usage": "normal"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "component": "SubscriptionManager",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }


# Создание глобального экземпляра
subscription_manager = SubscriptionManager()


async def main():
    """Тестирование SubscriptionManager"""
    print("🧪 Тестирование SubscriptionManager")
    print("=" * 50)

    # Создание тестовой подписки
    result = await subscription_manager.create_subscription(
        family_id="test_family_123",
        tier=SubscriptionTier.BASIC
    )
    print(f"Создание подписки: {result}")

    # Проверка доступа к функции
    has_access = await subscription_manager.check_feature_access(
        family_id="test_family_123",
        feature=Features.UNLIMITED_VPN
    )
    print(f"Доступ к UNLIMITED_VPN: {has_access}")

    # Получение статистики
    stats = await subscription_manager.get_subscription_stats()
    print(f"Статистика: {stats}")

    # Получение доступных планов
    plans = await subscription_manager.get_available_plans()
    print(f"Доступные планы: {len(plans)}")


if __name__ == "__main__":
    asyncio.run(main())
