#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система аналитики безопасности
Глубокий анализ данных, метрик и трендов безопасности
"""

import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
import numpy as np

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    """Типы аналитики"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEHAVIORAL = "behavioral"
    THREAT = "threat"
    COMPLIANCE = "compliance"
    INCIDENT = "incident"

class AnalyticsLevel(Enum):
    """Уровни аналитики"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class AnalyticsMetric:
    """Метрика аналитики"""
    name: str
    value: float
    timestamp: datetime
    category: str
    level: AnalyticsLevel
    description: str = ""
    
    def __init__(self, name: str, value: float, category: str, level: AnalyticsLevel = AnalyticsLevel.BASIC, description: str = ""):
        self.name = name
        self.value = value
        self.timestamp = datetime.now()
        self.category = category
        self.level = level
        self.description = description

@dataclass
class AnalyticsReport:
    """Отчет аналитики"""
    report_id: str
    title: str
    analytics_type: AnalyticsType
    metrics: List[AnalyticsMetric]
    summary: str
    recommendations: List[str]
    created_at: datetime
    confidence_score: float = 0.0
    
    def __init__(self, report_id: str, title: str, analytics_type: AnalyticsType, metrics: List[AnalyticsMetric], summary: str, recommendations: List[str]):
        self.report_id = report_id
        self.title = title
        self.analytics_type = analytics_type
        self.metrics = metrics
        self.summary = summary
        self.recommendations = recommendations
        self.created_at = datetime.now()
        self.confidence_score = 0.0

class SecurityAnalytics:
    """
    Система аналитики безопасности
    Глубокий анализ данных, метрик и трендов
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[AnalyticsMetric]] = {}
        self.reports: List[AnalyticsReport] = []
        self.analytics_config: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.SecurityAnalytics")
        
    async def initialize(self):
        """Инициализация системы аналитики"""
        try:
            self.analytics_config = {
                "data_retention_days": 30,
                "real_time_analysis": True,
                "deep_learning_enabled": True,
                "anomaly_detection": True,
                "trend_analysis": True,
                "predictive_analytics": True
            }
            self.logger.info("Система аналитики безопасности инициализирована")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации аналитики: {e}")
            return False
    
    async def collect_metric(self, name: str, value: float, category: str, level: AnalyticsLevel = AnalyticsLevel.BASIC, description: str = "") -> bool:
        """Сбор метрики"""
        try:
            metric = AnalyticsMetric(name, value, category, level, description)
            
            if category not in self.metrics:
                self.metrics[category] = []
            
            self.metrics[category].append(metric)
            
            # Ограничиваем количество метрик для производительности
            if len(self.metrics[category]) > 1000:
                self.metrics[category] = self.metrics[category][-1000:]
            
            self.logger.debug(f"Метрика {name} добавлена: {value}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сбора метрики {name}: {e}")
            return False
    
    async def analyze_security_trends(self) -> Dict[str, Any]:
        """Анализ трендов безопасности"""
        try:
            if "security" not in self.metrics:
                return {"error": "Нет данных для анализа"}
            
            security_metrics = self.metrics["security"]
            if len(security_metrics) < 2:
                return {"error": "Недостаточно данных для анализа трендов"}
            
            # Анализ трендов
            values = [m.value for m in security_metrics[-30:]]  # Последние 30 метрик
            
            trend_analysis = {
                "total_metrics": len(security_metrics),
                "average_value": statistics.mean(values),
                "median_value": statistics.median(values),
                "std_deviation": statistics.stdev(values) if len(values) > 1 else 0,
                "trend_direction": "increasing" if values[-1] > values[0] else "decreasing",
                "volatility": "high" if statistics.stdev(values) > statistics.mean(values) * 0.5 else "low",
                "anomalies_detected": self._detect_anomalies(values),
                "confidence_score": min(0.95, len(values) / 100)
            }
            
            return trend_analysis
        except Exception as e:
            self.logger.error(f"Ошибка анализа трендов безопасности: {e}")
            return {"error": str(e)}
    
    async def analyze_performance_metrics(self) -> Dict[str, Any]:
        """Анализ метрик производительности"""
        try:
            if "performance" not in self.metrics:
                return {"error": "Нет данных для анализа"}
            
            perf_metrics = self.metrics["performance"]
            if len(perf_metrics) < 2:
                return {"error": "Недостаточно данных для анализа производительности"}
            
            values = [m.value for m in perf_metrics[-50:]]  # Последние 50 метрик
            
            performance_analysis = {
                "total_metrics": len(perf_metrics),
                "average_performance": statistics.mean(values),
                "peak_performance": max(values),
                "min_performance": min(values),
                "performance_stability": "stable" if statistics.stdev(values) < statistics.mean(values) * 0.2 else "unstable",
                "bottlenecks_detected": self._detect_bottlenecks(values),
                "optimization_opportunities": self._find_optimization_opportunities(values),
                "confidence_score": min(0.95, len(values) / 50)
            }
            
            return performance_analysis
        except Exception as e:
            self.logger.error(f"Ошибка анализа производительности: {e}")
            return {"error": str(e)}
    
    async def analyze_behavioral_patterns(self) -> Dict[str, Any]:
        """Анализ поведенческих паттернов"""
        try:
            if "behavioral" not in self.metrics:
                return {"error": "Нет данных для анализа"}
            
            behavioral_metrics = self.metrics["behavioral"]
            if len(behavioral_metrics) < 10:
                return {"error": "Недостаточно данных для анализа поведения"}
            
            values = [m.value for m in behavioral_metrics[-100:]]  # Последние 100 метрик
            
            behavioral_analysis = {
                "total_metrics": len(behavioral_metrics),
                "behavioral_patterns": self._identify_behavioral_patterns(values),
                "anomalous_behaviors": self._detect_anomalous_behaviors(values),
                "user_activity_levels": self._analyze_activity_levels(values),
                "risk_assessment": self._assess_behavioral_risk(values),
                "confidence_score": min(0.95, len(values) / 100)
            }
            
            return behavioral_analysis
        except Exception as e:
            self.logger.error(f"Ошибка анализа поведенческих паттернов: {e}")
            return {"error": str(e)}
    
    async def analyze_threat_intelligence(self) -> Dict[str, Any]:
        """Анализ разведки угроз"""
        try:
            if "threat" not in self.metrics:
                return {"error": "Нет данных для анализа"}
            
            threat_metrics = self.metrics["threat"]
            if len(threat_metrics) < 5:
                return {"error": "Недостаточно данных для анализа угроз"}
            
            values = [m.value for m in threat_metrics[-50:]]  # Последние 50 метрик
            
            threat_analysis = {
                "total_metrics": len(threat_metrics),
                "threat_level": self._assess_threat_level(values),
                "threat_categories": self._categorize_threats(threat_metrics),
                "emerging_threats": self._identify_emerging_threats(values),
                "threat_trends": self._analyze_threat_trends(values),
                "recommended_actions": self._recommend_threat_actions(values),
                "confidence_score": min(0.95, len(values) / 50)
            }
            
            return threat_analysis
        except Exception as e:
            self.logger.error(f"Ошибка анализа разведки угроз: {e}")
            return {"error": str(e)}
    
    async def generate_comprehensive_report(self) -> AnalyticsReport:
        """Генерация комплексного отчета"""
        try:
            report_id = f"analytics_report_{int(time.time())}"
            
            # Собираем все анализы
            security_trends = await self.analyze_security_trends()
            performance_metrics = await self.analyze_performance_metrics()
            behavioral_patterns = await self.analyze_behavioral_patterns()
            threat_intelligence = await self.analyze_threat_intelligence()
            
            # Создаем метрики для отчета
            report_metrics = []
            for category, metrics in self.metrics.items():
                if metrics:
                    latest_metric = metrics[-1]
                    report_metrics.append(latest_metric)
            
            # Генерируем сводку
            summary = self._generate_report_summary(security_trends, performance_metrics, behavioral_patterns, threat_intelligence)
            
            # Генерируем рекомендации
            recommendations = self._generate_recommendations(security_trends, performance_metrics, behavioral_patterns, threat_intelligence)
            
            # Создаем отчет
            report = AnalyticsReport(
                report_id=report_id,
                title="Комплексный отчет аналитики безопасности",
                analytics_type=AnalyticsType.SECURITY,
                metrics=report_metrics,
                summary=summary,
                recommendations=recommendations
            )
            
            # Рассчитываем confidence score
            report.confidence_score = self._calculate_confidence_score(report_metrics)
            
            self.reports.append(report)
            self.logger.info(f"Комплексный отчет {report_id} создан")
            
            return report
        except Exception as e:
            self.logger.error(f"Ошибка генерации комплексного отчета: {e}")
            return None
    
    async def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """Получение данных для dashboard аналитики"""
        try:
            dashboard_data = {
                "total_metrics": sum(len(metrics) for metrics in self.metrics.values()),
                "categories": list(self.metrics.keys()),
                "recent_metrics": self._get_recent_metrics(10),
                "trends": await self._get_trend_summary(),
                "alerts": await self._get_analytics_alerts(),
                "performance_summary": await self._get_performance_summary(),
                "security_summary": await self._get_security_summary(),
                "last_updated": datetime.now().isoformat()
            }
            
            return dashboard_data
        except Exception as e:
            self.logger.error(f"Ошибка получения данных dashboard: {e}")
            return {"error": str(e)}
    
    def _detect_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """Обнаружение аномалий в данных"""
        if len(values) < 3:
            return []
        
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        threshold = 2 * std_val
        
        anomalies = []
        for i, value in enumerate(values):
            if abs(value - mean_val) > threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "deviation": abs(value - mean_val),
                    "severity": "high" if abs(value - mean_val) > 3 * std_val else "medium"
                })
        
        return anomalies
    
    def _detect_bottlenecks(self, values: List[float]) -> List[Dict[str, Any]]:
        """Обнаружение узких мест в производительности"""
        bottlenecks = []
        threshold = statistics.mean(values) * 0.7  # 70% от среднего значения
        
        for i, value in enumerate(values):
            if value < threshold:
                bottlenecks.append({
                    "index": i,
                    "value": value,
                    "impact": "high" if value < threshold * 0.5 else "medium"
                })
        
        return bottlenecks
    
    def _find_optimization_opportunities(self, values: List[float]) -> List[str]:
        """Поиск возможностей для оптимизации"""
        opportunities = []
        
        if statistics.stdev(values) > statistics.mean(values) * 0.3:
            opportunities.append("Высокая вариативность производительности - требуется стабилизация")
        
        if min(values) < statistics.mean(values) * 0.8:
            opportunities.append("Обнаружены периоды низкой производительности - требуется оптимизация")
        
        if len([v for v in values if v > statistics.mean(values) * 1.2]) > len(values) * 0.1:
            opportunities.append("Периодические пики нагрузки - рекомендуется масштабирование")
        
        return opportunities
    
    def _identify_behavioral_patterns(self, values: List[float]) -> List[Dict[str, Any]]:
        """Идентификация поведенческих паттернов"""
        patterns = []
        
        # Анализ цикличности
        if len(values) >= 24:  # Минимум сутки данных
            daily_pattern = self._analyze_daily_pattern(values)
            if daily_pattern:
                patterns.append(daily_pattern)
        
        # Анализ трендов
        if len(values) >= 7:
            trend_pattern = self._analyze_trend_pattern(values)
            if trend_pattern:
                patterns.append(trend_pattern)
        
        return patterns
    
    def _detect_anomalous_behaviors(self, values: List[float]) -> List[Dict[str, Any]]:
        """Обнаружение аномального поведения"""
        anomalous_behaviors = []
        
        # Анализ резких изменений
        for i in range(1, len(values)):
            change = abs(values[i] - values[i-1])
            if change > statistics.mean(values) * 0.5:  # Изменение больше 50% от среднего
                anomalous_behaviors.append({
                    "timestamp": i,
                    "change": change,
                    "severity": "high" if change > statistics.mean(values) else "medium",
                    "description": f"Резкое изменение активности: {change:.2f}"
                })
        
        return anomalous_behaviors
    
    def _analyze_activity_levels(self, values: List[float]) -> Dict[str, Any]:
        """Анализ уровней активности"""
        if not values:
            return {}
        
        mean_activity = statistics.mean(values)
        
        return {
            "low_activity": len([v for v in values if v < mean_activity * 0.5]),
            "normal_activity": len([v for v in values if mean_activity * 0.5 <= v <= mean_activity * 1.5]),
            "high_activity": len([v for v in values if v > mean_activity * 1.5]),
            "peak_activity": max(values),
            "average_activity": mean_activity
        }
    
    def _assess_behavioral_risk(self, values: List[float]) -> Dict[str, Any]:
        """Оценка поведенческого риска"""
        if not values:
            return {"risk_level": "unknown", "risk_score": 0}
        
        # Анализ стабильности поведения
        stability = 1 - (statistics.stdev(values) / statistics.mean(values))
        
        # Анализ аномалий
        anomalies = self._detect_anomalies(values)
        anomaly_ratio = len(anomalies) / len(values)
        
        # Расчет общего риска
        risk_score = (1 - stability) * 0.6 + anomaly_ratio * 0.4
        
        if risk_score < 0.2:
            risk_level = "low"
        elif risk_score < 0.5:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "stability": stability,
            "anomaly_ratio": anomaly_ratio,
            "anomalies_count": len(anomalies)
        }
    
    def _assess_threat_level(self, values: List[float]) -> str:
        """Оценка уровня угрозы"""
        if not values:
            return "unknown"
        
        mean_threat = statistics.mean(values)
        
        if mean_threat < 0.3:
            return "low"
        elif mean_threat < 0.6:
            return "medium"
        else:
            return "high"
    
    def _categorize_threats(self, threat_metrics: List[AnalyticsMetric]) -> Dict[str, int]:
        """Категоризация угроз"""
        categories = {}
        for metric in threat_metrics:
            category = metric.category
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _identify_emerging_threats(self, values: List[float]) -> List[Dict[str, Any]]:
        """Идентификация новых угроз"""
        emerging_threats = []
        
        # Анализ роста угроз
        if len(values) >= 7:
            recent_avg = statistics.mean(values[-7:])
            older_avg = statistics.mean(values[:-7]) if len(values) > 7 else recent_avg
            
            if recent_avg > older_avg * 1.5:
                emerging_threats.append({
                    "type": "increasing_threat_level",
                    "growth_rate": (recent_avg - older_avg) / older_avg,
                    "description": "Обнаружен рост уровня угроз"
                })
        
        return emerging_threats
    
    def _analyze_threat_trends(self, values: List[float]) -> Dict[str, Any]:
        """Анализ трендов угроз"""
        if len(values) < 2:
            return {"trend": "insufficient_data"}
        
        # Простой анализ тренда
        if values[-1] > values[0]:
            trend = "increasing"
        elif values[-1] < values[0]:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_rate": (values[-1] - values[0]) / values[0] if values[0] != 0 else 0,
            "volatility": statistics.stdev(values) if len(values) > 1 else 0
        }
    
    def _recommend_threat_actions(self, values: List[float]) -> List[str]:
        """Рекомендации по действиям против угроз"""
        recommendations = []
        
        threat_level = self._assess_threat_level(values)
        
        if threat_level == "high":
            recommendations.append("Немедленно активировать план реагирования на инциденты")
            recommendations.append("Усилить мониторинг безопасности")
            recommendations.append("Провести дополнительный анализ угроз")
        elif threat_level == "medium":
            recommendations.append("Усилить мониторинг подозрительной активности")
            recommendations.append("Обновить правила безопасности")
        else:
            recommendations.append("Продолжить регулярный мониторинг")
            recommendations.append("Поддерживать текущий уровень безопасности")
        
        return recommendations
    
    def _generate_report_summary(self, security_trends: Dict, performance_metrics: Dict, behavioral_patterns: Dict, threat_intelligence: Dict) -> str:
        """Генерация сводки отчета"""
        summary_parts = []
        
        if "error" not in security_trends:
            summary_parts.append(f"Анализ безопасности: {security_trends.get('trend_direction', 'unknown')} тренд")
        
        if "error" not in performance_metrics:
            summary_parts.append(f"Производительность: {performance_metrics.get('performance_stability', 'unknown')}")
        
        if "error" not in behavioral_patterns:
            risk_level = behavioral_patterns.get('risk_assessment', {}).get('risk_level', 'unknown')
            summary_parts.append(f"Поведенческий риск: {risk_level}")
        
        if "error" not in threat_intelligence:
            threat_level = threat_intelligence.get('threat_level', 'unknown')
            summary_parts.append(f"Уровень угроз: {threat_level}")
        
        return ". ".join(summary_parts) + "."
    
    def _generate_recommendations(self, security_trends: Dict, performance_metrics: Dict, behavioral_patterns: Dict, threat_intelligence: Dict) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        # Рекомендации по безопасности
        if "error" not in security_trends and security_trends.get('trend_direction') == 'increasing':
            recommendations.append("Усилить меры безопасности в связи с растущим трендом угроз")
        
        # Рекомендации по производительности
        if "error" not in performance_metrics:
            opportunities = performance_metrics.get('optimization_opportunities', [])
            recommendations.extend(opportunities[:3])  # Топ-3 возможности
        
        # Рекомендации по поведению
        if "error" not in behavioral_patterns:
            risk_level = behavioral_patterns.get('risk_assessment', {}).get('risk_level', 'unknown')
            if risk_level == 'high':
                recommendations.append("Провести дополнительный анализ подозрительной активности")
        
        # Рекомендации по угрозам
        if "error" not in threat_intelligence:
            threat_actions = threat_intelligence.get('recommended_actions', [])
            recommendations.extend(threat_actions[:2])  # Топ-2 действия
        
        return recommendations[:10]  # Ограничиваем до 10 рекомендаций
    
    def _calculate_confidence_score(self, metrics: List[AnalyticsMetric]) -> float:
        """Расчет confidence score"""
        if not metrics:
            return 0.0
        
        # Базовый confidence на основе количества метрик
        base_confidence = min(0.8, len(metrics) / 100)
        
        # Дополнительный confidence на основе разнообразия категорий
        categories = set(metric.category for metric in metrics)
        category_bonus = min(0.2, len(categories) / 10)
        
        return min(0.95, base_confidence + category_bonus)
    
    def _get_recent_metrics(self, count: int) -> List[Dict[str, Any]]:
        """Получение последних метрик"""
        all_metrics = []
        for category_metrics in self.metrics.values():
            all_metrics.extend(category_metrics)
        
        # Сортируем по времени и берем последние
        recent_metrics = sorted(all_metrics, key=lambda m: m.timestamp, reverse=True)[:count]
        
        return [
            {
                "name": metric.name,
                "value": metric.value,
                "category": metric.category,
                "timestamp": metric.timestamp.isoformat(),
                "description": metric.description
            }
            for metric in recent_metrics
        ]
    
    async def _get_trend_summary(self) -> Dict[str, Any]:
        """Получение сводки трендов"""
        try:
            security_trends = await self.analyze_security_trends()
            return {
                "security_trend": security_trends.get('trend_direction', 'unknown'),
                "confidence": security_trends.get('confidence_score', 0.0)
            }
        except:
            return {"security_trend": "unknown", "confidence": 0.0}
    
    async def _get_analytics_alerts(self) -> List[Dict[str, Any]]:
        """Получение алертов аналитики"""
        alerts = []
        
        # Проверяем аномалии в каждой категории
        for category, metrics in self.metrics.items():
            if len(metrics) >= 3:
                values = [m.value for m in metrics[-10:]]
                anomalies = self._detect_anomalies(values)
                
                for anomaly in anomalies:
                    alerts.append({
                        "category": category,
                        "type": "anomaly",
                        "severity": anomaly.get('severity', 'medium'),
                        "description": f"Обнаружена аномалия в {category}: {anomaly.get('value', 0):.2f}"
                    })
        
        return alerts[:10]  # Ограничиваем до 10 алертов
    
    async def _get_performance_summary(self) -> Dict[str, Any]:
        """Получение сводки производительности"""
        try:
            perf_analysis = await self.analyze_performance_metrics()
            return {
                "average_performance": perf_analysis.get('average_performance', 0),
                "stability": perf_analysis.get('performance_stability', 'unknown'),
                "bottlenecks": len(perf_analysis.get('bottlenecks_detected', []))
            }
        except:
            return {"average_performance": 0, "stability": "unknown", "bottlenecks": 0}
    
    async def _get_security_summary(self) -> Dict[str, Any]:
        """Получение сводки безопасности"""
        try:
            security_analysis = await self.analyze_security_trends()
            return {
                "trend": security_analysis.get('trend_direction', 'unknown'),
                "volatility": security_analysis.get('volatility', 'unknown'),
                "anomalies": len(security_analysis.get('anomalies_detected', []))
            }
        except:
            return {"trend": "unknown", "volatility": "unknown", "anomalies": 0}
    
    def _analyze_daily_pattern(self, values: List[float]) -> Optional[Dict[str, Any]]:
        """Анализ дневного паттерна"""
        if len(values) < 24:
            return None
        
        # Простой анализ: сравниваем утренние и вечерние значения
        morning_values = values[:8]  # Первые 8 часов
        evening_values = values[-8:]  # Последние 8 часов
        
        morning_avg = statistics.mean(morning_values)
        evening_avg = statistics.mean(evening_values)
        
        if abs(morning_avg - evening_avg) > statistics.mean(values) * 0.2:
            return {
                "pattern": "daily_cycle",
                "morning_activity": morning_avg,
                "evening_activity": evening_avg,
                "difference": abs(morning_avg - evening_avg)
            }
        
        return None
    
    def _analyze_trend_pattern(self, values: List[float]) -> Optional[Dict[str, Any]]:
        """Анализ трендового паттерна"""
        if len(values) < 7:
            return None
        
        # Простой анализ тренда
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg * 1.1:
            return {
                "pattern": "increasing_trend",
                "growth_rate": (second_avg - first_avg) / first_avg,
                "description": "Обнаружен растущий тренд"
            }
        elif second_avg < first_avg * 0.9:
            return {
                "pattern": "decreasing_trend",
                "decline_rate": (first_avg - second_avg) / first_avg,
                "description": "Обнаружен убывающий тренд"
            }
        
        return None

class SecurityAnalyticsManager:
    """
    Менеджер системы аналитики безопасности
    """
    
    def __init__(self):
        self.analytics = SecurityAnalytics()
        self.is_initialized = False
        self.logger = logging.getLogger(f"{__name__}.SecurityAnalyticsManager")
    
    async def initialize(self):
        """Инициализация менеджера"""
        try:
            self.is_initialized = await self.analytics.initialize()
            if self.is_initialized:
                self.logger.info("Менеджер аналитики безопасности инициализирован")
            return self.is_initialized
        except Exception as e:
            self.logger.error(f"Ошибка инициализации менеджера аналитики: {e}")
            return False
    
    async def add_metric(self, name: str, value: float, category: str, level: AnalyticsLevel = AnalyticsLevel.BASIC, description: str = "") -> bool:
        """Добавление метрики"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.analytics.collect_metric(name, value, category, level, description)
    
    async def get_analytics_report(self) -> Optional[AnalyticsReport]:
        """Получение отчета аналитики"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.analytics.generate_comprehensive_report()
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Получение данных для dashboard"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.analytics.get_analytics_dashboard_data()
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья системы аналитики"""
        try:
            return {
                "status": "healthy" if self.is_initialized else "not_initialized",
                "metrics_count": sum(len(metrics) for metrics in self.analytics.metrics.values()),
                "reports_count": len(self.analytics.reports),
                "categories": list(self.analytics.metrics.keys()),
                "last_activity": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка health check: {e}")
            return {"status": "error", "error": str(e)}

# Экспорт основных классов
__all__ = [
    'SecurityAnalytics',
    'SecurityAnalyticsManager',
    'AnalyticsMetric',
    'AnalyticsReport',
    'AnalyticsType',
    'AnalyticsLevel'
]