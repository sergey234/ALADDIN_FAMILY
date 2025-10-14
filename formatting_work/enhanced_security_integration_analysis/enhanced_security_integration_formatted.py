#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Security Integration для ALADDIN Security System
Интеграция расширенных компонентов безопасности

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from advanced_behavioral_analytics import (
    AdvancedBehavioralAnalytics,
    AnomalyType,
    EntityType,
    RiskLevel,
)
from advanced_threat_intelligence import (
    AdvancedThreatIntelligence,
    AdvancedThreatSource,
    ThreatCategory,
    ThreatSeverity,
)


class EnhancedSecurityIntegration:
    """Интеграция расширенных компонентов безопасности"""

    def __init__(self):
        self.threat_intelligence = AdvancedThreatIntelligence()
        self.behavioral_analytics = AdvancedBehavioralAnalytics()
        self.integration_status = {
            "threat_intelligence": False,
            "behavioral_analytics": False,
            "last_check": None,
        }

    async def initialize(self):
        """Инициализация интеграции"""
        try:
            # Инициализируем Threat Intelligence
            await self.threat_intelligence.load_yara_rules()
            self.integration_status["threat_intelligence"] = True

            # Инициализируем Behavioral Analytics
            self.integration_status["behavioral_analytics"] = True

            self.integration_status["last_check"] = datetime.now()

            print("✅ Enhanced Security Integration initialized successfully")

        except Exception as e:
            print(f"❌ Error initializing Enhanced Security Integration: {e}")

    async def comprehensive_security_analysis(
        self,
        user_id: str,
        indicator: str,
        indicator_type: str = "ip",
        behavior_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Комплексный анализ безопасности"""

        results = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "indicator": indicator,
            "indicator_type": indicator_type,
            "threat_intelligence": {},
            "behavioral_analysis": {},
            "risk_assessment": {},
            "recommendations": [],
            "overall_risk_score": 0.0,
        }

        # 1. Threat Intelligence анализ
        try:
            threat_result = (
                await self.threat_intelligence.comprehensive_threat_check(
                    indicator, indicator_type
                )
            )
            results["threat_intelligence"] = threat_result

            # Добавляем рекомендации на основе угроз
            if threat_result["total_threats"] > 0:
                results["recommendations"].append(
                    f"Обнаружено {threat_result['total_threats']} угроз"
                )
                if threat_result["max_severity"] == "critical":
                    results["recommendations"].append(
                        "Критический уровень угроз - немедленное вмешательство"
                    )
                elif threat_result["max_severity"] == "high":
                    results["recommendations"].append(
                        "Высокий уровень угроз - усиленный мониторинг"
                    )

        except Exception as e:
            results["threat_intelligence"] = {"error": str(e)}

        # 2. Behavioral Analytics анализ
        if behavior_data:
            try:
                # Анализируем поведение пользователя
                user_profile = (
                    await self.behavioral_analytics.analyze_user_behavior(
                        user_id, behavior_data
                    )
                )

                # Обнаруживаем аномалии
                anomalies = await self.behavioral_analytics.detect_anomalies(
                    user_id, EntityType.USER, behavior_data
                )

                # Рассчитываем риск
                risk_assessment = (
                    await self.behavioral_analytics.calculate_risk_score(
                        user_id, EntityType.USER
                    )
                )

                results["behavioral_analysis"] = {
                    "user_profile": user_profile.to_dict(),
                    "anomalies_detected": len(anomalies),
                    "anomalies": [anomaly.to_dict() for anomaly in anomalies],
                    "risk_assessment": risk_assessment.to_dict(),
                }

                # Добавляем рекомендации на основе аномалий
                if anomalies:
                    high_risk_anomalies = [
                        a
                        for a in anomalies
                        if a.severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]
                    ]
                    if high_risk_anomalies:
                        results["recommendations"].append(
                            f"Обнаружено {len(high_risk_anomalies)} высокорисковых аномалий поведения"
                        )

            except Exception as e:
                results["behavioral_analysis"] = {"error": str(e)}

        # 3. Общая оценка риска
        threat_score = results["threat_intelligence"].get(
            "confidence_score", 0
        )
        behavior_score = (
            results["behavioral_analysis"]
            .get("risk_assessment", {})
            .get("overall_risk_score", 0)
        )

        if threat_score > 0 and behavior_score > 0:
            results["overall_risk_score"] = (threat_score + behavior_score) / 2
        elif threat_score > 0:
            results["overall_risk_score"] = threat_score
        elif behavior_score > 0:
            results["overall_risk_score"] = behavior_score

        # 4. Общие рекомендации
        if results["overall_risk_score"] > 80:
            results["recommendations"].append(
                "Критический уровень риска - немедленные действия"
            )
        elif results["overall_risk_score"] > 60:
            results["recommendations"].append(
                "Высокий уровень риска - усиленный мониторинг"
            )
        elif results["overall_risk_score"] > 40:
            results["recommendations"].append(
                "Средний уровень риска - регулярный мониторинг"
            )
        else:
            results["recommendations"].append(
                "Низкий уровень риска - стандартный мониторинг"
            )

        return results

    async def real_time_monitoring(
        self, monitoring_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Real-time мониторинг"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_results": {},
            "alerts": [],
            "actions_taken": [],
        }

        # Мониторинг пользователей
        if "users" in monitoring_data:
            for user_data in monitoring_data["users"]:
                user_id = user_data.get("user_id")
                if user_id:
                    # Проверяем поведение
                    anomalies = (
                        await self.behavioral_analytics.detect_anomalies(
                            user_id, EntityType.USER, user_data
                        )
                    )

                    if anomalies:
                        high_risk_anomalies = [
                            a
                            for a in anomalies
                            if a.severity
                            in [RiskLevel.HIGH, RiskLevel.CRITICAL]
                        ]
                        if high_risk_anomalies:
                            results["alerts"].append(
                                {
                                    "type": "behavioral_anomaly",
                                    "user_id": user_id,
                                    "severity": "high",
                                    "anomalies": len(high_risk_anomalies),
                                    "description": f"Обнаружено {len(high_risk_anomalies)} высокорисковых аномалий",
                                }
                            )

        # Мониторинг сетевого трафика
        if "network_traffic" in monitoring_data:
            for traffic in monitoring_data["network_traffic"]:
                ip = traffic.get("source_ip")
                if ip:
                    # Проверяем в Threat Intelligence
                    threat_result = await self.threat_intelligence.comprehensive_threat_check(
                        ip, "ip"
                    )

                    if threat_result["total_threats"] > 0:
                        results["alerts"].append(
                            {
                                "type": "threat_detected",
                                "ip": ip,
                                "threats": threat_result["total_threats"],
                                "severity": threat_result["max_severity"],
                                "description": f"Обнаружено {threat_result['total_threats']} угроз для IP {ip}",
                            }
                        )

        # Мониторинг устройств
        if "devices" in monitoring_data:
            for device_data in monitoring_data["devices"]:
                device_id = device_data.get("device_id")
                if device_id:
                    # Анализируем поведение устройства
                    device_profile = await self.behavioral_analytics.analyze_entity_behavior(
                        device_id, EntityType.DEVICE, device_data
                    )

                    anomalies = (
                        await self.behavioral_analytics.detect_anomalies(
                            device_id, EntityType.DEVICE, device_data
                        )
                    )

                    if anomalies:
                        results["alerts"].append(
                            {
                                "type": "device_anomaly",
                                "device_id": device_id,
                                "anomalies": len(anomalies),
                                "description": f"Обнаружено {len(anomalies)} аномалий на устройстве",
                            }
                        )

        return results

    async def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Получение данных для дашборда безопасности"""
        try:
            # Статистика Threat Intelligence
            threat_stats = (
                await self.threat_intelligence.get_threat_statistics()
            )

            # Статистика Behavioral Analytics
            behavior_stats = (
                await self.behavioral_analytics.get_analytics_summary()
            )

            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "threat_intelligence": threat_stats,
                "behavioral_analytics": behavior_stats,
                "integration_status": self.integration_status,
                "overall_metrics": {
                    "total_threats": threat_stats.get("total_threats", 0),
                    "user_profiles": behavior_stats.get("user_profiles", 0),
                    "entity_profiles": behavior_stats.get(
                        "entity_profiles", 0
                    ),
                    "total_anomalies": behavior_stats.get(
                        "total_anomalies", 0
                    ),
                    "risk_assessments": behavior_stats.get(
                        "risk_assessments", 0
                    ),
                },
            }

            return dashboard_data

        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def export_security_report(
        self, report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Экспорт отчета по безопасности"""
        report = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "threat_intelligence_summary": {},
            "behavioral_analytics_summary": {},
            "recommendations": [],
            "next_steps": [],
        }

        try:
            # Данные Threat Intelligence
            threat_stats = (
                await self.threat_intelligence.get_threat_statistics()
            )
            report["threat_intelligence_summary"] = threat_stats

            # Данные Behavioral Analytics
            behavior_stats = (
                await self.behavioral_analytics.get_analytics_summary()
            )
            report["behavioral_analytics_summary"] = behavior_stats

            # Рекомендации
            if threat_stats.get("total_threats", 0) > 100:
                report["recommendations"].append(
                    "Высокое количество угроз - усилить мониторинг"
                )

            if behavior_stats.get("total_anomalies", 0) > 50:
                report["recommendations"].append(
                    "Много аномалий поведения - проверить настройки детекции"
                )

            # Следующие шаги
            report["next_steps"] = [
                "Регулярно обновлять YARA правила",
                "Мониторить новые источники угроз",
                "Анализировать ложные срабатывания",
                "Оптимизировать алгоритмы детекции",
            ]

        except Exception as e:
            report["error"] = str(e)

        return report


# Пример использования
async def main():
    """Основная функция"""
    integration = EnhancedSecurityIntegration()

    # Инициализация
    await integration.initialize()

    # Комплексный анализ безопасности
    user_behavior = {
        "location": "Moscow",
        "device": "iPhone",
        "application": "ALADDIN Mobile",
        "session_duration": 45,
        "activity_count": 25,  # Подозрительно высокая активность
    }

    analysis_result = await integration.comprehensive_security_analysis(
        "user_123", "192.168.1.100", "ip", user_behavior
    )

    print("Comprehensive Security Analysis:")
    print(json.dumps(analysis_result, indent=2))

    # Real-time мониторинг
    monitoring_data = {
        "users": [user_behavior],
        "network_traffic": [{"source_ip": "192.168.1.100"}],
        "devices": [
            {"device_id": "device_123", "performance_metrics": {"cpu": 85.0}}
        ],
    }

    monitoring_result = await integration.real_time_monitoring(monitoring_data)
    print("\nReal-time Monitoring:")
    print(json.dumps(monitoring_result, indent=2))

    # Данные для дашборда
    dashboard_data = await integration.get_security_dashboard_data()
    print("\nDashboard Data:")
    print(json.dumps(dashboard_data, indent=2))

    # Отчет по безопасности
    security_report = await integration.export_security_report()
    print("\nSecurity Report:")
    print(json.dumps(security_report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
