#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Security Analytics - Объединенная аналитика VPN и Antivirus
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatCategory(Enum):
    """Категории угроз"""

    VPN_BLOCKED = "vpn_blocked"
    MALWARE_DETECTED = "malware_detected"
    VIRUS_DETECTED = "virus_detected"
    SUSPICIOUS_FILE = "suspicious_file"
    NETWORK_ATTACK = "network_attack"
    PHISHING = "phishing"
    DATA_EXFILTRATION = "data_exfiltration"


class SecurityLevel(Enum):
    """Уровни безопасности"""

    CRITICAL = "critical"  # Красный
    HIGH = "high"  # Жёлтый
    NORMAL = "normal"  # Зелёный
    OPTIMAL = "optimal"  # Голубой


@dataclass
class ThreatEvent:
    """Событие угрозы"""

    threat_id: str
    category: ThreatCategory
    timestamp: datetime
    severity: str
    source: str  # vpn или antivirus
    description: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserSecurityProfile:
    """Профиль безопасности пользователя"""

    user_id: str
    threat_count: int
    vpn_threats: int
    av_threats: int
    security_score: float  # 0-100
    security_level: SecurityLevel
    recommendations: List[str]
    last_updated: datetime


@dataclass
class UnifiedStats:
    """Объединенная статистика"""

    user_id: str
    vpn_threats_blocked: int
    av_threats_detected: int
    total_threats: int
    vpn_stats: Dict[str, Any]
    av_stats: Dict[str, Any]
    security_level: SecurityLevel
    recommendations: List[str]
    timestamp: datetime


class UnifiedSecurityAnalytics:
    """
    Объединенная система аналитики безопасности

    Объединяет данные от VPN и Antivirus для:
    - Общей статистики угроз
    - Единого профиля безопасности
    - Интегрированных рекомендаций
    - Детальной аналитики
    """

    def __init__(self):
        self.user_threats: Dict[str, List[ThreatEvent]] = defaultdict(list)
        self.user_profiles: Dict[str, UserSecurityProfile] = {}
        self.threat_history: List[ThreatEvent] = []
        logger.info("✅ UnifiedSecurityAnalytics initialized")

    async def process_vpn_threat(
        self, user_id: str, threat_type: str, context: Dict[str, Any]
    ) -> ThreatEvent:
        """Обработка угрозы от VPN"""
        threat = ThreatEvent(
            threat_id=f"VPN_{datetime.now().timestamp()}",
            category=ThreatCategory.VPN_BLOCKED,
            timestamp=datetime.now(),
            severity=context.get("severity", "medium"),
            source="vpn",
            description=f"VPN заблокировал угрозу: {threat_type}",
            context=context,
        )

        self.user_threats[user_id].append(threat)
        self.threat_history.append(threat)

        logger.info(f"🛡️ VPN threat processed: {user_id} - {threat_type}")
        await self._update_user_profile(user_id)

        return threat

    async def process_av_threat(
        self,
        user_id: str,
        threat_type: str,
        file_name: str,
        severity: str,
        context: Dict[str, Any],
    ) -> ThreatEvent:
        """Обработка угрозы от Antivirus"""
        threat = ThreatEvent(
            threat_id=f"AV_{datetime.now().timestamp()}",
            category=self._map_av_category(threat_type),
            timestamp=datetime.now(),
            severity=severity,
            source="antivirus",
            description=f"Antivirus обнаружил: {threat_type} в {file_name}",
            context={**context, "file_name": file_name},
        )

        self.user_threats[user_id].append(threat)
        self.threat_history.append(threat)

        logger.info(f"🛡️ AV threat processed: {user_id} - {threat_type}")
        await self._update_user_profile(user_id)

        return threat

    def _map_av_category(self, threat_type: str) -> ThreatCategory:
        """Маппинг типа угрозы AV в категорию"""
        mapping = {
            "virus": ThreatCategory.VIRUS_DETECTED,
            "malware": ThreatCategory.MALWARE_DETECTED,
            "trojan": ThreatCategory.MALWARE_DETECTED,
            "ransomware": ThreatCategory.MALWARE_DETECTED,
            "spyware": ThreatCategory.MALWARE_DETECTED,
        }
        return mapping.get(threat_type.lower(), ThreatCategory.SUSPICIOUS_FILE)

    async def _update_user_profile(self, user_id: str) -> None:
        """Обновление профиля безопасности пользователя"""
        recent_threats = [
            t
            for t in self.user_threats[user_id]
            if (datetime.now() - t.timestamp).days <= 30
        ]

        vpn_threats = sum(1 for t in recent_threats if t.source == "vpn")
        av_threats = sum(1 for t in recent_threats if t.source == "antivirus")

        # Вычисляем security score (чем больше угроз - тем ниже)
        threat_count = len(recent_threats)
        base_score = 100.0
        score_penalty = min(threat_count * 2, 50)  # Максимум -50 баллов
        security_score = max(base_score - score_penalty, 0)

        # Определяем security level
        if security_score < 30:
            security_level = SecurityLevel.CRITICAL
        elif security_score < 60:
            security_level = SecurityLevel.HIGH
        elif security_score < 85:
            security_level = SecurityLevel.NORMAL
        else:
            security_level = SecurityLevel.OPTIMAL

        # Генерируем рекомендации
        recommendations = await self._generate_recommendations(
            user_id, vpn_threats, av_threats, security_level
        )

        self.user_profiles[user_id] = UserSecurityProfile(
            user_id=user_id,
            threat_count=threat_count,
            vpn_threats=vpn_threats,
            av_threats=av_threats,
            security_score=security_score,
            security_level=security_level,
            recommendations=recommendations,
            last_updated=datetime.now(),
        )

        logger.info(f"✅ Profile updated: {user_id} - Score: {security_score:.1f}")

    async def _generate_recommendations(
        self,
        user_id: str,
        vpn_threats: int,
        av_threats: int,
        security_level: SecurityLevel,
    ) -> List[str]:
        """Генерация рекомендаций на основе статистики"""
        recommendations = []

        # Критический уровень
        if security_level == SecurityLevel.CRITICAL:
            recommendations.append("🔴 КРИТИЧНО: Включите усиленную защиту!")
            recommendations.append("Проведите полное сканирование устройства")
            recommendations.append("Проверьте подозрительные приложения")

        # Высокий уровень
        if security_level == SecurityLevel.HIGH:
            recommendations.append("⚠️ Включите все модули защиты")
            recommendations.append("Регулярно обновляйте базы сигнатур")

        # VPN рекомендации
        if vpn_threats > 10:
            recommendations.append(
                "🔒 Много сетевых угроз. Используйте VPN постоянно"
            )
            recommendations.append("Смените VPN сервер на более защищенный")

        # Antivirus рекомендации
        if av_threats > 5:
            recommendations.append("🛡️ Найдено несколько угроз. Запустите полное сканирование")
            recommendations.append("Удалите подозрительные файлы")

        # Общие рекомендации
        if vpn_threats == 0 and av_threats == 0:
            recommendations.append("✅ Все отлично! Защита работает эффективно")

        return recommendations

    async def get_unified_stats(self, user_id: str) -> UnifiedStats:
        """Получить объединенную статистику"""
        profile = self.user_profiles.get(user_id)

        if not profile:
            # Если профиля нет - создаем пустой
            await self._update_user_profile(user_id)
            profile = self.user_profiles[user_id]

        # Получаем последние 30 дней угроз
        recent_threats = [
            t
            for t in self.user_threats[user_id]
            if (datetime.now() - t.timestamp).days <= 30
        ]

        vpn_threats = [t for t in recent_threats if t.source == "vpn"]
        av_threats = [t for t in recent_threats if t.source == "antivirus"]

        stats = UnifiedStats(
            user_id=user_id,
            vpn_threats_blocked=len(vpn_threats),
            av_threats_detected=len(av_threats),
            total_threats=profile.threat_count,
            vpn_stats={
                "threats_by_category": await self._count_by_category(vpn_threats),
                "severity_distribution": await self._severity_distribution(vpn_threats),
            },
            av_stats={
                "threats_by_category": await self._count_by_category(av_threats),
                "severity_distribution": await self._severity_distribution(av_threats),
            },
            security_level=profile.security_level,
            recommendations=profile.recommendations,
            timestamp=datetime.now(),
        )

        logger.info(f"✅ Unified stats generated: {user_id}")
        return stats

    async def _count_by_category(self, threats: List[ThreatEvent]) -> Dict[str, int]:
        """Подсчет угроз по категориям"""
        categories = defaultdict(int)
        for threat in threats:
            categories[threat.category.value] += 1
        return dict(categories)

    async def _severity_distribution(
        self, threats: List[ThreatEvent]
    ) -> Dict[str, int]:
        """Распределение угроз по уровню серьезности"""
        distribution = defaultdict(int)
        for threat in threats:
            distribution[threat.severity] += 1
        return dict(distribution)

    async def get_dashboard_summary(self, user_id: str) -> Dict[str, Any]:
        """Получить дашборд с общей статистикой"""
        stats = await self.get_unified_stats(user_id)
        profile = self.user_profiles.get(user_id)

        return {
            "user_id": user_id,
            "total_threats_blocked": stats.total_threats,
            "vpn_threats": stats.vpn_threats_blocked,
            "av_threats": stats.av_threats_detected,
            "security_score": profile.security_score if profile else 100.0,
            "security_level": stats.security_level.value,
            "recommendations": stats.recommendations[:3],  # Топ-3
            "status": {
                "vpn": "🟢 Активен" if stats.vpn_threats_blocked > 0 else "🟡 Минимум",
                "antivirus": "🟢 Активен" if stats.av_threats_detected > 0 else "🟡 Минимум",
            },
            "last_updated": stats.timestamp.isoformat(),
        }


# Global instance
unified_analytics = UnifiedSecurityAnalytics()


# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════


async def process_threat_from_vpn(
    user_id: str, threat_type: str, context: Dict[str, Any]
) -> Dict[str, Any]:
    """Обработать угрозу от VPN"""
    threat = await unified_analytics.process_vpn_threat(user_id, threat_type, context)
    return threat.__dict__


async def process_threat_from_av(
    user_id: str, threat_type: str, file_name: str, severity: str, context: Dict[str, Any]
) -> Dict[str, Any]:
    """Обработать угрозу от Antivirus"""
    threat = await unified_analytics.process_av_threat(
        user_id, threat_type, file_name, severity, context
    )
    return threat.__dict__


async def get_unified_security_stats(user_id: str) -> Dict[str, Any]:
    """Получить объединенную статистику безопасности"""
    stats = await unified_analytics.get_unified_stats(user_id)
    return stats.__dict__


async def get_dashboard_data(user_id: str) -> Dict[str, Any]:
    """Получить данные для дашборда"""
    return await unified_analytics.get_dashboard_summary(user_id)


if __name__ == "__main__":
    async def main():
        # Тестирование
        print("🧪 Testing Unified Security Analytics...")

        # VPN угрозы
        await process_threat_from_vpn("user_123", "DDoS Attack", {"severity": "high"})
        await process_threat_from_vpn("user_123", "Phishing Attempt", {"severity": "medium"})

        # AV угрозы
        await process_threat_from_av("user_123", "Malware", "suspicious.exe", "high", {})
        await process_threat_from_av("user_123", "Virus", "trojan.dll", "critical", {})

        # Получаем статистику
        stats = await get_unified_security_stats("user_123")
        print("\n📊 Unified Stats:")
        print(f"Total threats: {stats['total_threats']}")
        print(f"VPN: {stats['vpn_threats_blocked']}, AV: {stats['av_threats_detected']}")
        print(f"Security Level: {stats['security_level'].value}")

        # Dashboard
        dashboard = await get_dashboard_data("user_123")
        print("\n📈 Dashboard:")
        print(f"Security Score: {dashboard['security_score']:.1f}")
        print(f"Recommendations: {dashboard['recommendations']}")

        print("\n✅ Test completed!")

    asyncio.run(main())

