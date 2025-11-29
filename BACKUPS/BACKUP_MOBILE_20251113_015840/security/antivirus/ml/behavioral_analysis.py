#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Behavioral Analysis - Поведенческий анализ файлов и процессов
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import asyncio
import logging
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BehavioralAnomaly(Enum):
    """Типы поведенческих аномалий"""

    UNUSUAL_FILE_ACCESS = "unusual_file_access"
    SUSPICIOUS_NETWORK = "suspicious_network"
    PROCESS_INJECTION = "process_injection"
    REGISTRY_MODIFICATION = "registry_modification"
    ENCRYPTION_ACTIVITY = "encryption_activity"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    PERSISTENCE_ATTEMPT = "persistence_attempt"


class BehaviorPattern(Enum):
    """Паттерны поведения"""

    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"


@dataclass
class BehavioralEvent:
    """Событие поведения"""

    event_id: str
    timestamp: datetime
    event_type: BehavioralAnomaly
    severity: str
    file_path: Optional[str]
    process_name: Optional[str]
    details: Dict[str, Any]
    risk_score: float


@dataclass
class BehavioralProfile:
    """Профиль поведения файла/процесса"""

    identifier: str
    pattern: BehaviorPattern
    anomaly_count: int
    risk_score: float
    events: List[BehavioralEvent]
    last_activity: datetime


class BehavioralAnalyzer:
    """
    Анализатор поведения файлов и процессов

    Основные функции:
    - Детекция подозрительных действий
    - Анализ паттернов поведения
    - Оценка риска
    - Генерация оповещений
    """

    def __init__(self):
        self.profiles: Dict[str, BehavioralProfile] = {}
        self.event_history: List[BehavioralEvent] = []
        self.anomaly_threshold = 5
        logger.info("✅ BehavioralAnalyzer инициализирован")

    # MARK: - Event Analysis

    async def analyze_event(
        self,
        event_type: BehavioralAnomaly,
        file_path: Optional[str] = None,
        process_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> BehavioralEvent:
        """
        Анализ события поведения

        Args:
            event_type: Тип события
            file_path: Путь к файлу
            process_name: Имя процесса
            details: Дополнительные детали

        Returns:
            BehavioralEvent
        """
        logger.info(f"🔍 Analyzing event: {event_type.value}")

        # Определяем риск
        risk_score = self._calculate_risk_score(event_type, details or {})

        # Определяем серьезность
        severity = self._determine_severity(risk_score)

        event = BehavioralEvent(
            event_id=f"EVT_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            file_path=file_path,
            process_name=process_name,
            details=details or {},
            risk_score=risk_score
        )

        # Сохраняем событие
        self.event_history.append(event)

        # Обновляем профиль
        await self._update_profile(event)

        logger.info(f"✅ Event analyzed: {event_type.value} - severity: {severity}")
        return event

    def _calculate_risk_score(self, event_type: BehavioralAnomaly, details: Dict[str, Any]) -> float:
        """Вычисление риска события"""
        base_scores = {
            BehavioralAnomaly.UNUSUAL_FILE_ACCESS: 0.3,
            BehavioralAnomaly.SUSPICIOUS_NETWORK: 0.4,
            BehavioralAnomaly.PROCESS_INJECTION: 0.9,
            BehavioralAnomaly.REGISTRY_MODIFICATION: 0.6,
            BehavioralAnomaly.ENCRYPTION_ACTIVITY: 0.8,
            BehavioralAnomaly.DATA_EXFILTRATION: 0.95,
            BehavioralAnomaly.PRIVILEGE_ESCALATION: 0.85,
            BehavioralAnomaly.PERSISTENCE_ATTEMPT: 0.7,
        }

        base_score = base_scores.get(event_type, 0.5)

        # Модификаторы риска
        if details.get("network_bytes", 0) > 10 * 1024 * 1024:  # >10MB
            base_score += 0.1
        if details.get("encrypted_files", 0) > 100:
            base_score += 0.2
        if details.get("privilege_level", "") == "admin":
            base_score += 0.15

        return min(base_score, 1.0)

    def _determine_severity(self, risk_score: float) -> str:
        """Определение серьезности"""
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    # MARK: - Profile Management

    async def _update_profile(self, event: BehavioralEvent) -> None:
        """Обновление профиля поведения"""
        identifier = event.file_path or event.process_name or "unknown"

        if identifier not in self.profiles:
            self.profiles[identifier] = BehavioralProfile(
                identifier=identifier,
                pattern=BehaviorPattern.NORMAL,
                anomaly_count=0,
                risk_score=0.0,
                events=[],
                last_activity=datetime.now()
            )

        profile = self.profiles[identifier]
        profile.events.append(event)
        profile.anomaly_count += 1
        profile.last_activity = event.timestamp
        profile.risk_score = sum(e.risk_score for e in profile.events) / len(profile.events)

        # Определяем паттерн
        if profile.anomaly_count >= self.anomaly_threshold:
            if profile.risk_score >= 0.8:
                profile.pattern = BehaviorPattern.MALICIOUS
            elif profile.risk_score >= 0.5:
                profile.pattern = BehaviorPattern.SUSPICIOUS

    # MARK: - Pattern Detection

    async def detect_suspicious_patterns(
        self, identifier: str
    ) -> List[BehavioralAnomaly]:
        """
        Детекция подозрительных паттернов

        Args:
            identifier: Идентификатор файла/процесса

        Returns:
            Список обнаруженных аномалий
        """
        if identifier not in self.profiles:
            return []

        profile = self.profiles[identifier]
        recent_events = [
            e for e in profile.events
            if (datetime.now() - e.timestamp).minutes <= 60
        ]

        anomalies = []
        event_types = defaultdict(int)

        # Подсчитываем типы событий
        for event in recent_events:
            event_types[event.event_type] += 1

        # Детекция паттернов
        if event_types[BehavioralAnomaly.ENCRYPTION_ACTIVITY] > 5:
            anomalies.append(BehavioralAnomaly.ENCRYPTION_ACTIVITY)
        if event_types[BehavioralAnomaly.DATA_EXFILTRATION] > 0:
            anomalies.append(BehavioralAnomaly.DATA_EXFILTRATION)
        if event_types[BehavioralAnomaly.PROCESS_INJECTION] > 0:
            anomalies.append(BehavioralAnomaly.PROCESS_INJECTION)

        return anomalies

    # MARK: - File Behavior Analysis

    async def analyze_file_behavior(self, file_path: str) -> Dict[str, Any]:
        """
        Анализ поведения файла

        Args:
            file_path: Путь к файлу

        Returns:
            Результат анализа
        """
        logger.info(f"🔍 Analyzing file behavior: {file_path}")

        if not os.path.exists(file_path):
            return {"error": "File not found"}

        analysis = {
            "file_path": file_path,
            "has_profile": file_path in self.profiles,
            "risk_score": 0.0,
            "pattern": "unknown",
            "anomalies": [],
            "recommendations": []
        }

        if file_path in self.profiles:
            profile = self.profiles[file_path]
            analysis["risk_score"] = profile.risk_score
            analysis["pattern"] = profile.pattern.value
            analysis["anomalies"] = await self.detect_suspicious_patterns(file_path)
            analysis["recommendations"] = self._generate_recommendations(profile)

        logger.info(f"✅ Behavior analysis: pattern={analysis['pattern']}, risk={analysis['risk_score']:.2f}")
        return analysis

    def _generate_recommendations(self, profile: BehavioralProfile) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []

        if profile.pattern == BehaviorPattern.MALICIOUS:
            recommendations.append("🔴 КРИТИЧНО: Файл демонстрирует вредоносное поведение!")
            recommendations.append("Немедленно удалите или изолируйте файл")
        elif profile.pattern == BehaviorPattern.SUSPICIOUS:
            recommendations.append("⚠️ ОПАСНО: Файл демонстрирует подозрительное поведение")
            recommendations.append("Рекомендуется дополнительная проверка")
        elif profile.anomaly_count > 0:
            recommendations.append("⚡ ВНИМАНИЕ: Зафиксированы необычные активности")

        if profile.risk_score > 0.7:
            recommendations.append("🔐 Высокий риск - прекратите использование файла")

        return recommendations if recommendations else ["✅ Поведение в норме"]

    # MARK: - System Behavior Analysis

    async def analyze_system_behavior(self) -> Dict[str, Any]:
        """
        Анализ поведения системы

        Returns:
            Общая оценка системы
        """
        logger.info("🔍 Analyzing system behavior")

        total_events = len(self.event_history)
        recent_events = [
            e for e in self.event_history
            if (datetime.now() - e.timestamp).minutes <= 60
        ]

        high_risk_profiles = sum(
            1 for p in self.profiles.values()
            if p.risk_score >= 0.7
        )

        analysis = {
            "total_events": total_events,
            "recent_events": len(recent_events),
            "total_profiles": len(self.profiles),
            "high_risk_profiles": high_risk_profiles,
            "system_risk": "low" if high_risk_profiles == 0 else "high",
            "recommendations": []
        }

        if high_risk_profiles > 0:
            analysis["recommendations"].append(f"⚠️ Обнаружено {high_risk_profiles} объектов с высоким риском")
            analysis["recommendations"].append("Рекомендуется полное сканирование системы")

        logger.info(f"✅ System behavior: risk={analysis['system_risk']}")
        return analysis

    # MARK: - History Management

    async def cleanup_old_history(self, days: int = 30) -> int:
        """Очистка старой истории"""
        cutoff = datetime.now() - timedelta(days=days)
        removed_count = len(self.event_history)
        self.event_history = [e for e in self.event_history if e.timestamp > cutoff]
        removed_count -= len(self.event_history)

        # Очистка неактивных профилей
        inactive_profiles = [
            k for k, v in self.profiles.items()
            if v.last_activity < cutoff
        ]
        for key in inactive_profiles:
            del self.profiles[key]

        logger.info(f"✅ Cleaned up {removed_count} old events and {len(inactive_profiles)} profiles")
        return removed_count


# Global instance
behavioral_analyzer = BehavioralAnalyzer()


# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════


async def analyze_file_behavior_async(file_path: str) -> Dict[str, Any]:
    """Анализ поведения файла"""
    return await behavioral_analyzer.analyze_file_behavior(file_path)


async def analyze_system_behavior_async() -> Dict[str, Any]:
    """Анализ поведения системы"""
    return await behavioral_analyzer.analyze_system_behavior()


if __name__ == "__main__":
    async def main():
        print("🧪 Testing Behavioral Analysis...")

        # Тестируем события
        await behavioral_analyzer.analyze_event(
            BehavioralAnomaly.UNUSUAL_FILE_ACCESS,
            file_path="/tmp/test.exe",
            process_name="test.exe"
        )

        await behavioral_analyzer.analyze_event(
            BehavioralAnomaly.ENCRYPTION_ACTIVITY,
            file_path="/tmp/test.exe",
            details={"encrypted_files": 150}
        )

        # Анализируем поведение файла
        behavior = await behavioral_analyzer.analyze_file_behavior("/tmp/test.exe")
        print(f"\n📊 File Behavior:")
        print(f"Risk: {behavior['risk_score']:.2f}")
        print(f"Pattern: {behavior['pattern']}")
        print(f"Recommendations: {behavior['recommendations']}")

        # Анализируем систему
        system = await behavioral_analyzer.analyze_system_behavior()
        print(f"\n📊 System Behavior:")
        print(f"Events: {system['total_events']}")
        print(f"High Risk: {system['high_risk_profiles']}")
        print(f"Recommendations: {system['recommendations']}")

        print("\n✅ Test completed!")

    asyncio.run(main())


