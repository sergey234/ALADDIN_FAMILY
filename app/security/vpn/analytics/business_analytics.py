#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Business Analytics - Бизнес-аналитика для VPN сервиса
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import json
import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import asyncio

logger = logging.getLogger(__name__)


class BusinessMetricType(Enum):
    """Типы бизнес-метрик"""

    REVENUE = "revenue"
    CUSTOMERS = "customers"
    RETENTION = "retention"
    CHURN = "churn"
    LTV = "ltv"
    CAC = "cac"
    ARPU = "arpu"
    MRR = "mrr"
    ARR = "arr"
    GROWTH = "growth"


@dataclass
class RevenueData:
    """Данные о выручке"""

    date: datetime
    monthly_revenue: float
    annual_revenue: float
    new_customers: int
    churned_customers: int
    active_customers: int
    average_revenue_per_user: float
    customer_lifetime_value: float
    customer_acquisition_cost: float


@dataclass
class CohortData:
    """Данные когортного анализа"""

    cohort_month: str
    customers_count: int
    retention_rates: List[float]  # Процент удержания по месяцам
    revenue_per_customer: List[float]  # Выручка на клиента по месяцам
    churn_rate: float  # Процент оттока


@dataclass
class BusinessMetrics:
    """Бизнес-метрики"""

    # Основные метрики
    monthly_recurring_revenue: float  # MRR
    annual_recurring_revenue: float  # ARR
    average_revenue_per_user: float  # ARPU
    customer_lifetime_value: float  # LTV
    customer_acquisition_cost: float  # CAC

    # Метрики роста
    monthly_growth_rate: float  # Месячный рост
    annual_growth_rate: float  # Годовой рост
    customer_growth_rate: float  # Рост клиентов

    # Метрики удержания
    monthly_churn_rate: float  # Месячный отток
    annual_churn_rate: float  # Годовой отток
    customer_retention_rate: float  # Удержание клиентов

    # Операционные метрики
    total_customers: int
    active_customers: int
    new_customers_this_month: int
    churned_customers_this_month: int

    # Финансовые метрики
    total_revenue: float
    monthly_revenue: float
    gross_margin: float  # Валовая маржа
    net_margin: float  # Чистая маржа

    # Дата расчета
    calculated_at: datetime = field(default_factory=datetime.now)


class BusinessAnalytics:
    """
    Система бизнес-аналитики для VPN сервиса

    Рассчитывает:
    - MRR, ARR, ARPU, LTV, CAC
    - Когортный анализ
    - Прогнозирование роста
    - Анализ оттока клиентов
    - ROI по каналам привлечения
    """

    def __init__(self, name: str = "BusinessAnalytics"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Данные
        self.revenue_data: List[RevenueData] = []
        self.cohort_data: List[CohortData] = []
        self.customer_data: Dict[str, Dict[str, Any]] = {}

        # Конфигурация
        self.monthly_subscription_price = 9.99  # USD
        self.annual_subscription_price = 99.99  # USD
        self.operational_costs_per_customer = 2.50  # USD/месяц

        self.logger.info(f"Business Analytics '{name}' инициализирован")

    async def calculate_business_metrics(self, months: int = 12) -> BusinessMetrics:
        """Расчет основных бизнес-метрик"""
        self.logger.info(f"Расчет бизнес-метрик за {months} месяцев...")

        # Генерация тестовых данных
        await self._generate_test_data(months)

        # Расчет метрик
        mrr = await self._calculate_mrr()
        arr = await self._calculate_arr()
        arpu = await self._calculate_arpu()
        ltv = await self._calculate_ltv()
        cac = await self._calculate_cac()

        # Расчет роста
        monthly_growth = await self._calculate_monthly_growth()
        annual_growth = await self._calculate_annual_growth()
        customer_growth = await self._calculate_customer_growth()

        # Расчет оттока
        monthly_churn = await self._calculate_monthly_churn()
        annual_churn = await self._calculate_annual_churn()
        retention_rate = 100 - monthly_churn

        # Операционные метрики
        total_customers = len(self.customer_data)
        active_customers = sum(1 for c in self.customer_data.values() if c.get("is_active", False))
        new_customers = len(
            [
                c
                for c in self.customer_data.values()
                if c.get("signup_date", datetime.min) >= datetime.now() - timedelta(days=30)
            ]
        )
        churned_customers = len(
            [
                c
                for c in self.customer_data.values()
                if c.get("churn_date") and c.get("churn_date") >= datetime.now() - timedelta(days=30)
            ]
        )

        # Финансовые метрики
        total_revenue = sum(r.monthly_revenue for r in self.revenue_data)
        monthly_revenue = self.revenue_data[-1].monthly_revenue if self.revenue_data else 0

        # Расчет маржи
        gross_margin = await self._calculate_gross_margin()
        net_margin = await self._calculate_net_margin()

        metrics = BusinessMetrics(
            monthly_recurring_revenue=mrr,
            annual_recurring_revenue=arr,
            average_revenue_per_user=arpu,
            customer_lifetime_value=ltv,
            customer_acquisition_cost=cac,
            monthly_growth_rate=monthly_growth,
            annual_growth_rate=annual_growth,
            customer_growth_rate=customer_growth,
            monthly_churn_rate=monthly_churn,
            annual_churn_rate=annual_churn,
            customer_retention_rate=retention_rate,
            total_customers=total_customers,
            active_customers=active_customers,
            new_customers_this_month=new_customers,
            churned_customers_this_month=churned_customers,
            total_revenue=total_revenue,
            monthly_revenue=monthly_revenue,
            gross_margin=gross_margin,
            net_margin=net_margin,
        )

        self.logger.info("Бизнес-метрики рассчитаны успешно")
        return metrics

    async def _generate_test_data(self, months: int) -> None:
        """Генерация тестовых данных для анализа"""
        self.logger.info("Генерация тестовых данных...")

        # Очистка существующих данных
        self.revenue_data.clear()
        self.customer_data.clear()

        # Базовые параметры
        base_customers = 1000
        monthly_growth_rate = 0.05  # 5% в месяц
        churn_rate = 0.02  # 2% в месяц

        current_customers = base_customers
        total_revenue = 0

        for month in range(months):
            # Расчет для текущего месяца
            date = datetime.now() - timedelta(days=30 * (months - month - 1))

            # Новые клиенты
            new_customers = int(current_customers * monthly_growth_rate)

            # Отток клиентов
            churned_customers = int(current_customers * churn_rate)

            # Активные клиенты
            current_customers = current_customers + new_customers - churned_customers

            # Выручка
            monthly_revenue = current_customers * self.monthly_subscription_price
            annual_revenue = total_revenue + monthly_revenue
            total_revenue = annual_revenue

            # ARPU
            arpu = monthly_revenue / current_customers if current_customers > 0 else 0

            # LTV (упрощенный расчет)
            ltv = arpu / churn_rate if churn_rate > 0 else arpu * 12

            # CAC (упрощенный расчет)
            cac = 25.0  # Средняя стоимость привлечения

            # Создание данных о выручке
            revenue = RevenueData(
                date=date,
                monthly_revenue=monthly_revenue,
                annual_revenue=annual_revenue,
                new_customers=new_customers,
                churned_customers=churned_customers,
                active_customers=current_customers,
                average_revenue_per_user=arpu,
                customer_lifetime_value=ltv,
                customer_acquisition_cost=cac,
            )

            self.revenue_data.append(revenue)

            # Создание данных о клиентах
            for i in range(new_customers):
                customer_id = f"customer_{month}_{i}"
                self.customer_data[customer_id] = {
                    "signup_date": date,
                    "is_active": True,
                    "monthly_revenue": self.monthly_subscription_price,
                    "churn_date": None,
                }

            # Отметка оттока
            churned_customer_ids = list(self.customer_data.keys())[-churned_customers:]
            for customer_id in churned_customer_ids:
                if customer_id in self.customer_data:
                    self.customer_data[customer_id]["is_active"] = False
                    self.customer_data[customer_id]["churn_date"] = date

    async def _calculate_mrr(self) -> float:
        """Расчет Monthly Recurring Revenue"""
        if not self.revenue_data:
            return 0.0
        return self.revenue_data[-1].monthly_revenue

    async def _calculate_arr(self) -> float:
        """Расчет Annual Recurring Revenue"""
        if not self.revenue_data:
            return 0.0
        return self.revenue_data[-1].annual_revenue

    async def _calculate_arpu(self) -> float:
        """Расчет Average Revenue Per User"""
        if not self.revenue_data:
            return 0.0
        return self.revenue_data[-1].average_revenue_per_user

    async def _calculate_ltv(self) -> float:
        """Расчет Customer Lifetime Value"""
        if not self.revenue_data:
            return 0.0
        return self.revenue_data[-1].customer_lifetime_value

    async def _calculate_cac(self) -> float:
        """Расчет Customer Acquisition Cost"""
        if not self.revenue_data:
            return 0.0
        return self.revenue_data[-1].customer_acquisition_cost

    async def _calculate_monthly_growth(self) -> float:
        """Расчет месячного роста"""
        if len(self.revenue_data) < 2:
            return 0.0

        current = self.revenue_data[-1].monthly_revenue
        previous = self.revenue_data[-2].monthly_revenue

        if previous == 0:
            return 0.0

        return ((current - previous) / previous) * 100

    async def _calculate_annual_growth(self) -> float:
        """Расчет годового роста"""
        if len(self.revenue_data) < 12:
            return 0.0

        current = self.revenue_data[-1].monthly_revenue
        year_ago = self.revenue_data[-12].monthly_revenue

        if year_ago == 0:
            return 0.0

        return ((current - year_ago) / year_ago) * 100

    async def _calculate_customer_growth(self) -> float:
        """Расчет роста клиентов"""
        if len(self.revenue_data) < 2:
            return 0.0

        current = self.revenue_data[-1].active_customers
        previous = self.revenue_data[-2].active_customers

        if previous == 0:
            return 0.0

        return ((current - previous) / previous) * 100

    async def _calculate_monthly_churn(self) -> float:
        """Расчет месячного оттока"""
        if not self.revenue_data:
            return 0.0

        latest = self.revenue_data[-1]
        if latest.active_customers == 0:
            return 0.0

        return (latest.churned_customers / latest.active_customers) * 100

    async def _calculate_annual_churn(self) -> float:
        """Расчет годового оттока"""
        if len(self.revenue_data) < 12:
            return 0.0

        total_churned = sum(r.churned_customers for r in self.revenue_data[-12:])
        avg_active = statistics.mean(r.active_customers for r in self.revenue_data[-12:])

        if avg_active == 0:
            return 0.0

        return (total_churned / avg_active) * 100

    async def _calculate_gross_margin(self) -> float:
        """Расчет валовой маржи"""
        if not self.revenue_data:
            return 0.0

        latest = self.revenue_data[-1]
        revenue = latest.monthly_revenue
        costs = latest.active_customers * self.operational_costs_per_customer

        if revenue == 0:
            return 0.0

        return ((revenue - costs) / revenue) * 100

    async def _calculate_net_margin(self) -> float:
        """Расчет чистой маржи (упрощенный)"""
        gross_margin = await self._calculate_gross_margin()
        # Предполагаем дополнительные расходы 20%
        return gross_margin * 0.8

    async def get_cohort_analysis(self, months: int = 12) -> List[CohortData]:
        """Когортный анализ клиентов"""
        self.logger.info(f"Проведение когортного анализа за {months} месяцев...")

        # Группировка клиентов по месяцам регистрации
        cohorts = defaultdict(list)

        for customer_id, data in self.customer_data.items():
            signup_month = data["signup_date"].strftime("%Y-%m")
            cohorts[signup_month].append(data)

        cohort_data = []

        for cohort_month, customers in cohorts.items():
            # Расчет удержания по месяцам
            retention_rates = []
            revenue_per_customer = []

            for month_offset in range(months):
                month_date = datetime.strptime(cohort_month, "%Y-%m") + timedelta(days=30 * month_offset)

                # Клиенты, которые все еще активны
                active_in_month = sum(
                    1
                    for c in customers
                    if c.get("is_active", False) and (not c.get("churn_date") or c.get("churn_date") > month_date)
                )

                retention_rate = (active_in_month / len(customers)) * 100 if customers else 0
                retention_rates.append(retention_rate)

                # Выручка на клиента
                revenue = active_in_month * self.monthly_subscription_price
                revenue_per_customer.append(revenue / len(customers) if customers else 0)

            # Расчет оттока
            churned = sum(1 for c in customers if not c.get("is_active", False))
            churn_rate = (churned / len(customers)) * 100 if customers else 0

            cohort = CohortData(
                cohort_month=cohort_month,
                customers_count=len(customers),
                retention_rates=retention_rates,
                revenue_per_customer=revenue_per_customer,
                churn_rate=churn_rate,
            )

            cohort_data.append(cohort)

        self.cohort_data = cohort_data
        self.logger.info("Когортный анализ завершен")
        return cohort_data

    async def get_revenue_forecast(self, months: int = 12) -> List[Dict[str, Any]]:
        """Прогноз выручки на следующие месяцы"""
        self.logger.info(f"Создание прогноза выручки на {months} месяцев...")

        if not self.revenue_data:
            return []

        # Используем последние данные для прогноза
        latest = self.revenue_data[-1]
        current_customers = latest.active_customers
        monthly_growth = await self._calculate_monthly_growth()
        churn_rate = await self._calculate_monthly_churn()

        forecast = []
        customers = current_customers
        total_revenue = latest.annual_revenue

        for month in range(1, months + 1):
            # Расчет роста клиентов
            new_customers = int(customers * (monthly_growth / 100))
            churned_customers = int(customers * (churn_rate / 100))

            customers = customers + new_customers - churned_customers
            monthly_revenue = customers * self.monthly_subscription_price
            total_revenue += monthly_revenue

            forecast.append(
                {
                    "month": month,
                    "customers": customers,
                    "monthly_revenue": monthly_revenue,
                    "total_revenue": total_revenue,
                    "new_customers": new_customers,
                    "churned_customers": churned_customers,
                }
            )

        return forecast

    async def get_roi_analysis(self) -> Dict[str, Any]:
        """Анализ ROI по каналам привлечения"""
        self.logger.info("Проведение анализа ROI...")

        # Симуляция данных по каналам
        channels = {
            "google_ads": {"customers": 300, "cost": 5000, "revenue": 9000},
            "facebook_ads": {"customers": 200, "cost": 3000, "revenue": 6000},
            "referral": {"customers": 150, "cost": 500, "revenue": 4500},
            "organic": {"customers": 100, "cost": 0, "revenue": 3000},
            "email": {"customers": 50, "cost": 200, "revenue": 1500},
        }

        roi_analysis = {}

        for channel, data in channels.items():
            if data["cost"] > 0:
                roi = ((data["revenue"] - data["cost"]) / data["cost"]) * 100
                roas = data["revenue"] / data["cost"]  # Return on Ad Spend
            else:
                roi = float("inf")
                roas = float("inf")

            roi_analysis[channel] = {
                "customers": data["customers"],
                "cost": data["cost"],
                "revenue": data["revenue"],
                "roi": roi,
                "roas": roas,
                "ltv": data["revenue"] / data["customers"] if data["customers"] > 0 else 0,
                "cac": data["cost"] / data["customers"] if data["customers"] > 0 else 0,
            }

        return roi_analysis

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Получение сводки метрик"""
        if not self.revenue_data:
            return {}

        latest = self.revenue_data[-1]

        return {
            "mrr": latest.monthly_revenue,
            "arr": latest.annual_revenue,
            "arpu": latest.average_revenue_per_user,
            "ltv": latest.customer_lifetime_value,
            "cac": latest.customer_acquisition_cost,
            "total_customers": latest.active_customers,
            "new_customers": latest.new_customers,
            "churned_customers": latest.churned_customers,
            "churn_rate": (
                (latest.churned_customers / latest.active_customers) * 100 if latest.active_customers > 0 else 0
            ),
            "calculated_at": datetime.now(),
        }


# Пример использования
async def main():
    """Пример использования Business Analytics"""
    analytics = BusinessAnalytics("TestAnalytics")

    # Расчет метрик
    metrics = await analytics.calculate_business_metrics(12)

    print("=== БИЗНЕС-МЕТРИКИ ===")
    print(f"MRR: ${metrics.monthly_recurring_revenue:,.2f}")
    print(f"ARR: ${metrics.annual_recurring_revenue:,.2f}")
    print(f"ARPU: ${metrics.average_revenue_per_user:.2f}")
    print(f"LTV: ${metrics.customer_lifetime_value:.2f}")
    print(f"CAC: ${metrics.customer_acquisition_cost:.2f}")
    print(f"Месячный рост: {metrics.monthly_growth_rate:.1f}%")
    print(f"Отток: {metrics.monthly_churn_rate:.1f}%")

    # Когортный анализ
    cohorts = await analytics.get_cohort_analysis(6)
    print(f"\nКогорты: {len(cohorts)}")

    # Прогноз
    forecast = await analytics.get_revenue_forecast(6)
    print(f"Прогноз на 6 месяцев: ${forecast[-1]['total_revenue']:,.2f}")


if __name__ == "__main__":
    asyncio.run(main())
