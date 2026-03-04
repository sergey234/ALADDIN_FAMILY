#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReferralManager - Менеджер реферальной системы ALADDIN
Версия 1.0 - Полная система рефералов с уникальными ссылками и скидками

Интегрируется с:
- SubscriptionManager (управление подписками)
- FamilyProfileManagerEnhanced (семейные профили)
- QRPaymentManager (система оплаты)
- FamilyNotificationManager (уведомления)

Автор: ALADDIN Security System
Версия: 1.0.0
Дата: 2025-01-27
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
import secrets
import string

from security.core.security_base import ComponentStatus, SecurityBase, SecurityLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReferralStatus(Enum):
    """Статусы реферала"""
    PENDING = "pending"         # Ожидает регистрации
    REGISTERED = "registered"   # Зарегистрирован
    CONVERTED = "converted"     # Конвертирован в платящего
    EXPIRED = "expired"         # Истек
    CANCELLED = "cancelled"     # Отменен


class DiscountType(Enum):
    """Типы скидок"""
    PERCENTAGE = "percentage"   # Процентная скидка
    FIXED_AMOUNT = "fixed_amount"  # Фиксированная сумма
    FREE_MONTHS = "free_months"    # Бесплатные месяцы
    UPGRADE = "upgrade"         # Обновление тарифа


class ReferralTier(Enum):
    """Уровни реферальной программы"""
    BRONZE = "bronze"           # Бронзовый (1-5 рефералов)
    SILVER = "silver"           # Серебряный (6-15 рефералов)
    GOLD = "gold"               # Золотой (16-30 рефералов)
    PLATINUM = "platinum"       # Платиновый (31+ рефералов)


@dataclass
class ReferralLink:
    """Реферальная ссылка"""
    link_id: str
    referrer_family_id: str
    referral_code: str
    referral_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None
    used_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Referral:
    """Реферал"""
    referral_id: str
    referrer_family_id: str
    referred_family_id: str
    referral_code: str
    status: ReferralStatus
    created_at: datetime
    converted_at: Optional[datetime] = None
    subscription_tier: Optional[str] = None
    discount_applied: Optional[Decimal] = None
    reward_amount: Optional[Decimal] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscountRule:
    """Правило скидки"""
    rule_id: str
    name: str
    discount_type: DiscountType
    discount_value: Decimal
    min_subscription_tier: str
    max_uses_per_user: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = True


@dataclass
class ReferralReward:
    """Награда за реферал (НЕ ДЕНЕЖНАЯ)"""
    reward_id: str
    referrer_family_id: str
    referred_family_id: str
    reward_type: str  # "premium_features", "extended_trial", "priority_support"
    reward_value: str  # Описание награды
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    status: str = "pending"


class ReferralManager(SecurityBase):
    """
    Менеджер реферальной системы ALADDIN

    Функции:
    - Генерация уникальных реферальных ссылок
    - Отслеживание рефералов
    - Система скидок и наград
    - Аналитика конверсий
    - Интеграция с подписками
    """

    def __init__(self):
        """Инициализация менеджера рефералов"""
        super().__init__()

        # Хранилища данных
        self.referral_links: Dict[str, ReferralLink] = {}
        self.referrals: Dict[str, Referral] = {}
        self.discount_rules: Dict[str, DiscountRule] = {}
        self.rewards: Dict[str, ReferralReward] = {}
        self.family_referral_stats: Dict[str, Dict[str, Any]] = {}

        # Конфигурация
        self.base_url = "https://aladdin-security.ru/referral"
        self.default_discount_percentage = Decimal("20")  # 20% скидка
        self.default_discount_months = 3  # 3 месяца скидки
        self.referral_link_expiry_days = 365  # 1 год

        # НЕ ДЕНЕЖНЫЕ НАГРАДЫ
        self.reward_types = {
            "premium_features": "Доступ к премиум функциям на 1 месяц",
            "extended_trial": "Продление тестового периода на 15 дней",
            "priority_support": "Приоритетная поддержка на 3 месяца",
            "family_analytics": "Расширенная семейная аналитика на 2 месяца",
            "voice_control": "Голосовое управление на 1 месяц"
        }

        # Инициализация правил скидок
        self._initialize_discount_rules()

        # Статус компонента
        self.status = ComponentStatus.ACTIVE
        self.security_level = SecurityLevel.HIGH

        logger.info("ReferralManager инициализирован")

    def _initialize_discount_rules(self) -> None:
        """Инициализация правил скидок"""

        # Правило 1: Скидка для пригласившего
        self.discount_rules["referrer_discount"] = DiscountRule(
            rule_id="referrer_discount",
            name="Скидка для пригласившего",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("20"),
            min_subscription_tier="basic",
            max_uses_per_user=None,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=365)
        )

        # Правило 2: Скидка для приглашенного
        self.discount_rules["referred_discount"] = DiscountRule(
            rule_id="referred_discount",
            name="Скидка для приглашенного",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("20"),
            min_subscription_tier="basic",
            max_uses_per_user=1,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=365)
        )

        # Правило 3: Годовая подписка - постоянная скидка
        self.discount_rules["yearly_discount"] = DiscountRule(
            rule_id="yearly_discount",
            name="Постоянная скидка за годовую подписку",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10"),
            min_subscription_tier="family",
            max_uses_per_user=None,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=365)
        )

        # Правило 4: Семейная подписка - дополнительная скидка
        self.discount_rules["family_discount"] = DiscountRule(
            rule_id="family_discount",
            name="Дополнительная скидка за семейную подписку",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("5"),
            min_subscription_tier="family",
            max_uses_per_user=None,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=365)
        )

    async def generate_referral_link(self, family_id: str,
                                     expires_days: Optional[int] = None,
                                     max_uses: Optional[int] = None) -> Dict[str, Any]:
        """
        Генерация уникальной реферальной ссылки

        Args:
            family_id: ID семьи-приглашающего
            expires_days: Дни действия ссылки (по умолчанию 365)
            max_uses: Максимальное количество использований

        Returns:
            Информация о созданной ссылке
        """
        try:
            # Генерируем уникальный код
            referral_code = self._generate_referral_code()

            # Создаем ID ссылки
            link_id = str(uuid.uuid4())

            # Определяем срок действия
            expires_days = expires_days or self.referral_link_expiry_days
            expires_at = datetime.now() + timedelta(days=expires_days)

            # Создаем URL
            referral_url = f"{self.base_url}/{referral_code}"

            # Создаем ссылку
            referral_link = ReferralLink(
                link_id=link_id,
                referrer_family_id=family_id,
                referral_code=referral_code,
                referral_url=referral_url,
                created_at=datetime.now(),
                expires_at=expires_at,
                max_uses=max_uses,
                used_count=0,
                is_active=True
            )

            # Сохраняем ссылку
            self.referral_links[link_id] = referral_link

            # Инициализируем статистику семьи
            if family_id not in self.family_referral_stats:
                self.family_referral_stats[family_id] = {
                    "total_links": 0,
                    "total_referrals": 0,
                    "converted_referrals": 0,
                    "total_rewards": Decimal("0"),
                    "referral_tier": ReferralTier.BRONZE.value
                }

            self.family_referral_stats[family_id]["total_links"] += 1

            logger.info(f"Создана реферальная ссылка {referral_code} для семьи {family_id}")

            return {
                "success": True,
                "link_id": link_id,
                "referral_code": referral_code,
                "referral_url": referral_url,
                "expires_at": expires_at.isoformat(),
                "max_uses": max_uses,
                "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={referral_url}"
            }

        except Exception as e:
            logger.error(f"Ошибка генерации реферальной ссылки: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_referral_code(self, length: int = 8) -> str:
        """Генерация уникального реферального кода"""
        while True:
            # Генерируем код из букв и цифр
            characters = string.ascii_uppercase + string.digits
            code = ''.join(secrets.choice(characters) for _ in range(length))

            # Проверяем уникальность
            if not any(link.referral_code == code for link in self.referral_links.values()):
                return code

    async def process_referral(self, referral_code: str, referred_family_id: str) -> Dict[str, Any]:
        """
        Обработка реферала по коду

        Args:
            referral_code: Код реферальной ссылки
            referred_family_id: ID приглашенной семьи

        Returns:
            Результат обработки реферала
        """
        try:
            # Находим реферальную ссылку
            referral_link = None
            for link in self.referral_links.values():
                if link.referral_code == referral_code:
                    referral_link = link
                    break

            if not referral_link:
                return {
                    "success": False,
                    "error": "Реферальная ссылка не найдена"
                }

            # Проверяем активность ссылки
            if not referral_link.is_active:
                return {
                    "success": False,
                    "error": "Реферальная ссылка неактивна"
                }

            # Проверяем срок действия
            if referral_link.expires_at and datetime.now() > referral_link.expires_at:
                return {
                    "success": False,
                    "error": "Реферальная ссылка истекла"
                }

            # Проверяем максимальное количество использований
            if referral_link.max_uses and referral_link.used_count >= referral_link.max_uses:
                return {
                    "success": False,
                    "error": "Превышено максимальное количество использований"
                }

            # Проверяем, что семья не приглашает сама себя
            if referral_link.referrer_family_id == referred_family_id:
                return {
                    "success": False,
                    "error": "Нельзя использовать собственную реферальную ссылку"
                }

            # Проверяем, что семья еще не была приглашена
            existing_referral = None
            for referral in self.referrals.values():
                if (referral.referred_family_id == referred_family_id and
                        referral.status != ReferralStatus.CANCELLED):
                    existing_referral = referral
                    break

            if existing_referral:
                return {
                    "success": False,
                    "error": "Семья уже была приглашена по реферальной программе"
                }

            # Создаем реферал
            referral_id = str(uuid.uuid4())
            referral = Referral(
                referral_id=referral_id,
                referrer_family_id=referral_link.referrer_family_id,
                referred_family_id=referred_family_id,
                referral_code=referral_code,
                status=ReferralStatus.REGISTERED,
                created_at=datetime.now()
            )

            # Сохраняем реферал
            self.referrals[referral_id] = referral

            # Обновляем счетчик использований ссылки
            referral_link.used_count += 1

            # Обновляем статистику
            self._update_referral_stats(referral_link.referrer_family_id)

            logger.info(f"Обработан реферал {referral_id}: {referral_link.referrer_family_id} -> {referred_family_id}")

            return {
                "success": True,
                "referral_id": referral_id,
                "referrer_family_id": referral_link.referrer_family_id,
                "referred_family_id": referred_family_id,
                "discount_available": True,
                "discount_percentage": float(self.default_discount_percentage)
            }

        except Exception as e:
            logger.error(f"Ошибка обработки реферала: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def apply_discount(self, family_id: str, subscription_tier: str,
                             referral_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Применение скидки к подписке

        Args:
            family_id: ID семьи
            subscription_tier: Тариф подписки
            referral_id: ID реферала (если есть)

        Returns:
            Информация о примененной скидке
        """
        try:
            # Находим подходящие правила скидок
            applicable_rules = []

            for rule in self.discount_rules.values():
                if not rule.is_active:
                    continue

                # Проверяем минимальный тариф
                if self._compare_subscription_tiers(subscription_tier, rule.min_subscription_tier) < 0:
                    continue

                # Проверяем срок действия
                if rule.valid_from and datetime.now() < rule.valid_from:
                    continue
                if rule.valid_until and datetime.now() > rule.valid_until:
                    continue

                # Проверяем максимальное количество использований
                if rule.max_uses_per_user:
                    user_uses = self._count_user_discount_uses(family_id, rule.rule_id)
                    if user_uses >= rule.max_uses_per_user:
                        continue

                applicable_rules.append(rule)

            if not applicable_rules:
                return {
                    "success": False,
                    "error": "Нет подходящих правил скидок"
                }

            # Выбираем лучшее правило (с наибольшей скидкой)
            best_rule = max(applicable_rules, key=lambda r: r.discount_value)

            # Применяем скидку
            discount_amount = await self._calculate_discount_amount(
                family_id, subscription_tier, best_rule
            )

            # Если есть реферал, обновляем его статус
            if referral_id and referral_id in self.referrals:
                referral = self.referrals[referral_id]
                referral.status = ReferralStatus.CONVERTED
                referral.converted_at = datetime.now()
                referral.subscription_tier = subscription_tier
                referral.discount_applied = discount_amount

                # Создаем награду для пригласившего
                await self._create_referral_reward(referral)

            logger.info(f"Применена скидка {discount_amount}₽ для семьи {family_id}, тариф {subscription_tier}")

            return {
                "success": True,
                "discount_type": best_rule.discount_type.value,
                "discount_value": float(best_rule.discount_value),
                "discount_amount": float(discount_amount),
                "rule_name": best_rule.name,
                "referral_id": referral_id
            }

        except Exception as e:
            logger.error(f"Ошибка применения скидки: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _compare_subscription_tiers(self, tier1: str, tier2: str) -> int:
        """Сравнение тарифных планов (для определения минимального)"""
        tier_hierarchy = {
            "freemium": 0,
            "basic": 1,
            "family": 2,
            "premium": 3,
            "custom": 4
        }

        level1 = tier_hierarchy.get(tier1, 0)
        level2 = tier_hierarchy.get(tier2, 0)

        if level1 < level2:
            return -1
        elif level1 > level2:
            return 1
        else:
            return 0

    def _count_user_discount_uses(self, family_id: str, rule_id: str) -> int:
        """Подсчет использований скидки пользователем"""
        count = 0
        for referral in self.referrals.values():
            if (referral.referred_family_id == family_id and
                referral.status == ReferralStatus.CONVERTED and
                    rule_id in referral.metadata.get("applied_rules", [])):
                count += 1
        return count

    async def _calculate_discount_amount(self, family_id: str, subscription_tier: str,
                                         rule: DiscountRule) -> Decimal:
        """Расчет суммы скидки"""
        # Базовые цены тарифов (в реальной системе должны браться из SubscriptionManager)
        tier_prices = {
            "freemium": Decimal("0"),
            "basic": Decimal("290"),
            "family": Decimal("490"),
            "premium": Decimal("900"),
            "custom": Decimal("1500")
        }

        base_price = tier_prices.get(subscription_tier, Decimal("0"))

        if rule.discount_type == DiscountType.PERCENTAGE:
            return base_price * rule.discount_value / Decimal("100")
        elif rule.discount_type == DiscountType.FIXED_AMOUNT:
            return min(rule.discount_value, base_price)
        elif rule.discount_type == DiscountType.FREE_MONTHS:
            # Для бесплатных месяцев возвращаем полную стоимость
            return base_price
        else:
            return Decimal("0")

    async def _create_referral_reward(self, referral: Referral) -> None:
        """Создание НЕ ДЕНЕЖНОЙ награды за реферал"""
        try:
            # Выбираем тип награды на основе тарифа
            reward_type = self._select_reward_type(referral.subscription_tier)
            reward_value = self.reward_types.get(reward_type, "Дополнительные функции")

            reward = ReferralReward(
                reward_id=str(uuid.uuid4()),
                referrer_family_id=referral.referrer_family_id,
                referred_family_id=referral.referred_family_id,
                reward_type=reward_type,
                reward_value=reward_value,
                status="pending"
            )

            self.rewards[reward.reward_id] = reward

            # Обновляем статистику (считаем количество наград, не сумму)
            if referral.referrer_family_id in self.family_referral_stats:
                if "total_rewards_count" not in self.family_referral_stats[referral.referrer_family_id]:
                    self.family_referral_stats[referral.referrer_family_id]["total_rewards_count"] = 0
                self.family_referral_stats[referral.referrer_family_id]["total_rewards_count"] += 1

            logger.info(
                f"Создана НЕ ДЕНЕЖНАЯ награда {reward.reward_id} для семьи "
                f"{referral.referrer_family_id}: {reward_value}")

        except Exception as e:
            logger.error(f"Ошибка создания награды: {e}")

    def _select_reward_type(self, subscription_tier: str) -> str:
        """Выбор типа награды на основе тарифа"""
        if subscription_tier in ["premium", "custom"]:
            return "premium_features"
        elif subscription_tier == "family":
            return "family_analytics"
        elif subscription_tier == "basic":
            return "extended_trial"
        else:
            return "priority_support"

    def _update_referral_stats(self, family_id: str) -> None:
        """Обновление статистики рефералов семьи"""
        if family_id not in self.family_referral_stats:
            self.family_referral_stats[family_id] = {
                "total_links": 0,
                "total_referrals": 0,
                "converted_referrals": 0,
                "total_rewards": Decimal("0"),
                "referral_tier": ReferralTier.BRONZE.value
            }

        # Подсчитываем рефералов
        total_referrals = 0
        converted_referrals = 0

        for referral in self.referrals.values():
            if referral.referrer_family_id == family_id:
                total_referrals += 1
                if referral.status == ReferralStatus.CONVERTED:
                    converted_referrals += 1

        # Обновляем статистику
        self.family_referral_stats[family_id]["total_referrals"] = total_referrals
        self.family_referral_stats[family_id]["converted_referrals"] = converted_referrals

        # Определяем уровень реферальной программы
        if converted_referrals >= 31:
            tier = ReferralTier.PLATINUM
        elif converted_referrals >= 16:
            tier = ReferralTier.GOLD
        elif converted_referrals >= 6:
            tier = ReferralTier.SILVER
        else:
            tier = ReferralTier.BRONZE

        self.family_referral_stats[family_id]["referral_tier"] = tier.value

    async def get_referral_stats(self, family_id: str) -> Dict[str, Any]:
        """Получение статистики рефералов семьи"""
        if family_id not in self.family_referral_stats:
            return {
                "total_links": 0,
                "total_referrals": 0,
                "converted_referrals": 0,
                "conversion_rate": 0.0,
                "total_rewards": 0.0,
                "referral_tier": ReferralTier.BRONZE.value,
                "active_links": 0
            }

        stats = self.family_referral_stats[family_id].copy()

        # Добавляем процент конверсии
        if stats["total_referrals"] > 0:
            stats["conversion_rate"] = float(stats["converted_referrals"] / stats["total_referrals"] * 100)
        else:
            stats["conversion_rate"] = 0.0

        # Подсчитываем активные ссылки
        active_links = 0
        for link in self.referral_links.values():
            if (link.referrer_family_id == family_id and
                link.is_active and
                    (not link.expires_at or datetime.now() < link.expires_at)):
                active_links += 1

        stats["active_links"] = active_links
        stats["total_rewards"] = float(stats["total_rewards"])

        return stats

    async def get_referral_links(self, family_id: str) -> List[Dict[str, Any]]:
        """Получение реферальных ссылок семьи"""
        links = []

        for link in self.referral_links.values():
            if link.referrer_family_id == family_id:
                links.append({
                    "link_id": link.link_id,
                    "referral_code": link.referral_code,
                    "referral_url": link.referral_url,
                    "created_at": link.created_at.isoformat(),
                    "expires_at": link.expires_at.isoformat() if link.expires_at else None,
                    "max_uses": link.max_uses,
                    "used_count": link.used_count,
                    "is_active": link.is_active,
                    "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={link.referral_url}"
                })

        # Сортируем по дате создания (новые первые)
        links.sort(key=lambda x: x["created_at"], reverse=True)

        return links

    async def get_referral_history(self, family_id: str) -> List[Dict[str, Any]]:
        """Получение истории рефералов семьи"""
        history = []

        for referral in self.referrals.values():
            if referral.referrer_family_id == family_id:
                history.append({
                    "referral_id": referral.referral_id,
                    "referred_family_id": referral.referred_family_id,
                    "referral_code": referral.referral_code,
                    "status": referral.status.value,
                    "created_at": referral.created_at.isoformat(),
                    "converted_at": referral.converted_at.isoformat() if referral.converted_at else None,
                    "subscription_tier": referral.subscription_tier,
                    "discount_applied": float(referral.discount_applied) if referral.discount_applied else None,
                    "reward_amount": float(referral.reward_amount) if referral.reward_amount else None
                })

        # Сортируем по дате создания (новые первые)
        history.sort(key=lambda x: x["created_at"], reverse=True)

        return history

    async def get_reward_progress(self, family_id: str) -> Dict[str, Any]:
        """Возвращает прогресс по наградам для семьи"""
        stats = await self.get_referral_stats(family_id)
        converted = stats.get("converted_referrals", 0)

        reward_definitions = [
            {
                "reward_id": "reward_1",
                "title_key": "referral_reward_1_title",
                "subtitle_key": "referral_reward_1_subtitle",
                "amount_key": "referral_reward_1_amount",
                "reward_value": "-20%",
                "icon": "percent.circle.fill",
                "required_converted": 1
            },
            {
                "reward_id": "reward_3",
                "title_key": "referral_reward_3_title",
                "subtitle_key": "referral_reward_3_subtitle",
                "amount_key": "referral_reward_3_amount",
                "reward_value": "-30%",
                "icon": "crown.fill",
                "required_converted": 3
            },
            {
                "reward_id": "reward_10",
                "title_key": "referral_reward_10_title",
                "subtitle_key": "referral_reward_10_subtitle",
                "amount_key": "referral_reward_10_amount",
                "reward_value": "1 месяц",
                "icon": "star.fill",
                "required_converted": 10
            }
        ]

        unlocked_rewards = [
            reward for reward in self.rewards.values()
            if reward.referrer_family_id == family_id
        ]
        unlocked_rewards.sort(key=lambda r: r.created_at)

        unlocked_index = 0
        progress = []

        for definition in reward_definitions:
            required = definition["required_converted"]
            is_unlocked = converted >= required
            unlocked_at = None

            if is_unlocked and unlocked_index < len(unlocked_rewards):
                unlocked_at = unlocked_rewards[unlocked_index].created_at.isoformat()
                unlocked_index += 1

            progress.append({
                "reward_id": definition["reward_id"],
                "title_key": definition["title_key"],
                "subtitle_key": definition["subtitle_key"],
                "amount_key": definition["amount_key"],
                "reward_value": definition["reward_value"],
                "icon": definition["icon"],
                "required_converted": required,
                "status": "unlocked" if is_unlocked else "locked",
                "remaining": max(required - converted, 0),
                "unlocked_at": unlocked_at
            })

        return {
            "total_converted": converted,
            "rewards": progress
        }

    async def deactivate_referral_link(self, link_id: str) -> Dict[str, Any]:
        """Деактивация реферальной ссылки"""
        try:
            if link_id not in self.referral_links:
                return {
                    "success": False,
                    "error": "Реферальная ссылка не найдена"
                }

            link = self.referral_links[link_id]
            link.is_active = False

            logger.info(f"Реферальная ссылка {link_id} деактивирована")

            return {
                "success": True,
                "link_id": link_id,
                "is_active": False
            }

        except Exception as e:
            logger.error(f"Ошибка деактивации ссылки: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_global_referral_stats(self) -> Dict[str, Any]:
        """Получение глобальной статистики рефералов"""
        stats = {
            "total_links": len(self.referral_links),
            "active_links": 0,
            "total_referrals": len(self.referrals),
            "converted_referrals": 0,
            "total_rewards": Decimal("0"),
            "by_tier": {
                "bronze": 0,
                "silver": 0,
                "gold": 0,
                "platinum": 0
            }
        }

        # Подсчет активных ссылок
        for link in self.referral_links.values():
            if (link.is_active and
                    (not link.expires_at or datetime.now() < link.expires_at)):
                stats["active_links"] += 1

        # Подсчет конвертированных рефералов
        for referral in self.referrals.values():
            if referral.status == ReferralStatus.CONVERTED:
                stats["converted_referrals"] += 1

        # Подсчет наград
        for reward in self.rewards.values():
            stats["total_rewards"] += reward.reward_amount

        # Подсчет по уровням
        for family_stats in self.family_referral_stats.values():
            tier = family_stats["referral_tier"]
            stats["by_tier"][tier] += 1

        stats["total_rewards"] = float(stats["total_rewards"])

        return stats

    def get_status(self) -> ComponentStatus:
        """Получение статуса компонента"""
        return self.status

    def get_security_level(self) -> SecurityLevel:
        """Получение уровня безопасности"""
        return self.security_level

    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья компонента"""
        try:
            global_stats = await self.get_global_referral_stats()

            return {
                "status": "healthy",
                "component": "ReferralManager",
                "timestamp": datetime.now().isoformat(),
                "stats": global_stats,
                "memory_usage": "normal"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "component": "ReferralManager",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }


# Создание глобального экземпляра
referral_manager = ReferralManager()


async def main():
    """Тестирование ReferralManager"""
    print("🧪 Тестирование ReferralManager")
    print("=" * 50)

    # Генерация реферальной ссылки
    link_result = await referral_manager.generate_referral_link("test_family_123")
    print(f"Создание ссылки: {link_result}")

    if link_result["success"]:
        referral_code = link_result["referral_code"]

        # Обработка реферала
        referral_result = await referral_manager.process_referral(
            referral_code, "test_family_456"
        )
        print(f"Обработка реферала: {referral_result}")

        # Применение скидки
        if referral_result["success"]:
            discount_result = await referral_manager.apply_discount(
                "test_family_456", "basic", referral_result["referral_id"]
            )
            print(f"Применение скидки: {discount_result}")

        # Получение статистики
        stats = await referral_manager.get_referral_stats("test_family_123")
        print(f"Статистика: {stats}")

        # Получение ссылок
        links = await referral_manager.get_referral_links("test_family_123")
        print(f"Ссылки: {len(links)}")

        # Глобальная статистика
        global_stats = await referral_manager.get_global_referral_stats()
        print(f"Глобальная статистика: {global_stats}")


if __name__ == "__main__":
    asyncio.run(main())
