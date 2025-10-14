#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile Security Agent Main - Основной агент мобильной безопасности
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


# Типы угроз
class ThreatType(Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_LEAK = "data_leak"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    LOCATION_TRACKING = "location_tracking"
    APP_VULNERABILITY = "app_vulnerability"
    NETWORK_ATTACK = "network_attack"
    ROOT_JAILBREAK = "root_jailbreak"
    UNKNOWN = "unknown"


@dataclass
class SecurityThreat:
    """Угроза безопасности"""

    threat_id: str
    threat_type: ThreatType
    severity: str
    confidence: float
    timestamp: datetime
    device_id: str
    details: Dict[str, Any]


class MobileSecurityAgentMain:
    """Основной агент мобильной безопасности"""

    def __init__(self):
        self.logger = logging.getLogger("ALADDIN.MobileSecurityAgentMain")
        self.threats = {}
        self.device_profiles = {}
        self.security_policies = {}
        self.stats = {
            "threats_detected": 0,
            "threats_blocked": 0,
            "false_positives": 0,
            "devices_monitored": 0,
        }
        self._init_security_policies()

    def _init_security_policies(self) -> None:
        """Инициализация политик безопасности"""
        try:
            self.security_policies = {
                "malware_detection": {
                    "enabled": True,
                    "threshold": 0.8,
                    "action": "block",
                },
                "phishing_protection": {
                    "enabled": True,
                    "threshold": 0.7,
                    "action": "warn",
                },
                "data_leak_prevention": {
                    "enabled": True,
                    "threshold": 0.9,
                    "action": "block",
                },
                "unauthorized_access": {
                    "enabled": True,
                    "threshold": 0.6,
                    "action": "block",
                },
            }
            self.logger.info("Политики безопасности инициализированы")
        except Exception as e:
            self.logger.error(
                f"Ошибка инициализации политик безопасности: {e}"
            )

    def detect_threat(self, threat_data: SecurityThreat) -> Dict[str, Any]:
        """Обнаружение угрозы"""
        try:
            self.stats["threats_detected"] += 1

            # Анализ угрозы
            threat_analysis = self._analyze_threat(threat_data)

            # Применение политик безопасности
            policy_action = self._apply_security_policies(
                threat_data, threat_analysis
            )

            # Генерация рекомендаций
            recommendations = self._generate_recommendations(
                threat_data, threat_analysis
            )

            result = {
                "threat_id": threat_data.threat_id,
                "threat_type": threat_data.threat_type.value,
                "severity": threat_data.severity,
                "confidence": threat_data.confidence,
                "analysis": threat_analysis,
                "policy_action": policy_action,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
            }

            # Сохранение угрозы
            self.threats[threat_data.threat_id] = threat_data

            # Обновление статистики
            if policy_action["action"] == "block":
                self.stats["threats_blocked"] += 1

            self.logger.info(
                f"Обнаружена угроза {threat_data.threat_id}: "
                f"{threat_data.threat_type.value}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Ошибка обнаружения угрозы: {e}")
            return {"error": str(e)}

    def _analyze_threat(self, threat: SecurityThreat) -> Dict[str, Any]:
        """Анализ угрозы"""
        try:
            analysis = {
                "risk_score": threat.confidence,
                "threat_indicators": [],
                "behavioral_patterns": [],
                "device_context": {},
            }

            # Анализ индикаторов угрозы
            if threat.threat_type == ThreatType.MALWARE:
                analysis["threat_indicators"].extend(
                    [
                        "suspicious_code_execution",
                        "unusual_network_activity",
                        "file_system_modifications",
                    ]
                )
            elif threat.threat_type == ThreatType.PHISHING:
                analysis["threat_indicators"].extend(
                    [
                        "suspicious_url_patterns",
                        "fake_ui_elements",
                        "credential_harvesting",
                    ]
                )
            elif threat.threat_type == ThreatType.DATA_LEAK:
                analysis["threat_indicators"].extend(
                    [
                        "unauthorized_data_access",
                        "suspicious_data_transmission",
                        "privacy_violations",
                    ]
                )

            # Анализ поведенческих паттернов
            analysis["behavioral_patterns"] = (
                self._analyze_behavioral_patterns(threat)
            )

            # Анализ контекста устройства
            analysis["device_context"] = self._analyze_device_context(threat)

            return analysis

        except Exception as e:
            self.logger.error(f"Ошибка анализа угрозы: {e}")
            return {"risk_score": 0.5}

    def _analyze_behavioral_patterns(
        self, threat: SecurityThreat
    ) -> List[str]:
        """Анализ поведенческих паттернов"""
        try:
            patterns = []

            # Анализ времени возникновения угрозы
            current_hour = threat.timestamp.hour
            if current_hour < 6 or current_hour > 22:
                patterns.append("unusual_timing")

            # Анализ частоты угроз
            device_threats = [
                t
                for t in self.threats.values()
                if t.device_id == threat.device_id
            ]

            if len(device_threats) > 5:
                patterns.append("high_frequency")

            # Анализ типов угроз
            threat_types = [t.threat_type for t in device_threats]
            if len(set(threat_types)) > 3:
                patterns.append("diverse_threat_types")

            return patterns

        except Exception as e:
            self.logger.error(f"Ошибка анализа поведенческих паттернов: {e}")
            return []

    def _analyze_device_context(
        self, threat: SecurityThreat
    ) -> Dict[str, Any]:
        """Анализ контекста устройства"""
        try:
            device_id = threat.device_id

            # Получение профиля устройства
            if device_id not in self.device_profiles:
                self.device_profiles[device_id] = {
                    "first_seen": threat.timestamp,
                    "threat_count": 0,
                    "last_activity": threat.timestamp,
                }

            device_profile = self.device_profiles[device_id]
            device_profile["threat_count"] += 1
            device_profile["last_activity"] = threat.timestamp

            return {
                "device_id": device_id,
                "threat_count": device_profile["threat_count"],
                "first_seen": device_profile["first_seen"].isoformat(),
                "last_activity": device_profile["last_activity"].isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа контекста устройства: {e}")
            return {}

    def _apply_security_policies(
        self, threat: SecurityThreat, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Применение политик безопасности"""
        try:
            threat_type = threat.threat_type.value
            confidence = threat.confidence

            # Поиск соответствующей политики
            policy_key = None
            for key in self.security_policies:
                if threat_type in key or key in threat_type:
                    policy_key = key
                    break

            if not policy_key:
                policy_key = "malware_detection"  # Политика по умолчанию

            policy = self.security_policies[policy_key]

            # Проверка порога
            if confidence >= policy["threshold"]:
                action = policy["action"]
            else:
                action = "monitor"

            return {
                "policy": policy_key,
                "action": action,
                "threshold": policy["threshold"],
                "confidence": confidence,
                "enabled": policy["enabled"],
            }

        except Exception as e:
            self.logger.error(f"Ошибка применения политик безопасности: {e}")
            return {"action": "monitor", "policy": "unknown"}

    def _generate_recommendations(
        self, threat: SecurityThreat, analysis: Dict[str, Any]
    ) -> List[str]:
        """Генерация рекомендаций"""
        try:
            recommendations = []

            if threat.threat_type == ThreatType.MALWARE:
                recommendations.extend(
                    [
                        "Немедленно удалить подозрительное приложение",
                        "Запустить полное сканирование устройства",
                        "Обновить антивирусные базы данных",
                    ]
                )
            elif threat.threat_type == ThreatType.PHISHING:
                recommendations.extend(
                    [
                        "Не переходить по подозрительным ссылкам",
                        "Проверить подлинность сайта",
                        "Изменить пароли для затронутых аккаунтов",
                    ]
                )
            elif threat.threat_type == ThreatType.DATA_LEAK:
                recommendations.extend(
                    [
                        "Проверить настройки приватности приложений",
                        "Ограничить доступ к личным данным",
                        "Включить шифрование данных",
                    ]
                )
            elif threat.threat_type == ThreatType.ROOT_JAILBREAK:
                recommendations.extend(
                    [
                        "Удалить root/jailbreak приложения",
                        "Восстановить заводские настройки",
                        "Обновить операционную систему",
                    ]
                )

            # Общие рекомендации
            recommendations.extend(
                [
                    "Регулярно обновлять приложения",
                    "Использовать надежные пароли",
                    "Включить двухфакторную аутентификацию",
                ]
            )

            return recommendations

        except Exception as e:
            self.logger.error(f"Ошибка генерации рекомендаций: {e}")
            return ["Обратиться к специалисту по безопасности"]

    def get_device_security_status(self, device_id: str) -> Dict[str, Any]:
        """Получение статуса безопасности устройства"""
        try:
            device_threats = [
                t for t in self.threats.values() if t.device_id == device_id
            ]

            if device_id not in self.device_profiles:
                return {"error": "Устройство не найдено"}

            device_profile = self.device_profiles[device_id]

            return {
                "device_id": device_id,
                "threat_count": len(device_threats),
                "last_threat": (
                    max(
                        device_threats, key=lambda x: x.timestamp
                    ).timestamp.isoformat()
                    if device_threats
                    else None
                ),
                "first_seen": device_profile["first_seen"].isoformat(),
                "last_activity": device_profile["last_activity"].isoformat(),
                "security_score": self._calculate_security_score(
                    device_threats
                ),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса устройства: {e}")
            return {"error": str(e)}

    def _calculate_security_score(
        self, threats: List[SecurityThreat]
    ) -> float:
        """Расчет скора безопасности"""
        try:
            if not threats:
                return 1.0

            # Базовый скор
            base_score = 1.0

            # Штрафы за угрозы
            for threat in threats:
                if threat.severity == "critical":
                    base_score -= 0.3
                elif threat.severity == "high":
                    base_score -= 0.2
                elif threat.severity == "medium":
                    base_score -= 0.1
                else:
                    base_score -= 0.05

            return max(0.0, min(1.0, base_score))

        except Exception as e:
            self.logger.error(f"Ошибка расчета скора безопасности: {e}")
            return 0.5

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса агента"""
        try:
            return {
                "threats_detected": self.stats["threats_detected"],
                "threats_blocked": self.stats["threats_blocked"],
                "false_positives": self.stats["false_positives"],
                "devices_monitored": len(self.device_profiles),
                "active_threats": len(self.threats),
                "status": "active",
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}

    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            self.threats.clear()
            self.device_profiles.clear()
            self.security_policies.clear()
            self.stats = {
                "threats_detected": 0,
                "threats_blocked": 0,
                "false_positives": 0,
                "devices_monitored": 0,
            }
        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")


# Глобальный экземпляр
mobile_security_agent_main = MobileSecurityAgentMain()
