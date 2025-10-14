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
        # Дополнительные атрибуты для расширенной функциональности
        self.config = {
            "auto_export": False,
            "export_interval": 3600,  # секунды
            "max_threats_history": 1000,
            "enable_notifications": True,
        }
        self.notifications = []
        self.last_export_time = None
        self.initialization_time = datetime.now()
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

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта в словарь"""
        try:
            return {
                "threats_count": len(self.threats),
                "devices_count": len(self.device_profiles),
                "stats": self.stats.copy(),
                "security_policies": self.security_policies.copy(),
            }
        except Exception as e:
            self.logger.error(f"Ошибка преобразования в словарь: {e}")
            return {"error": str(e)}

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Восстановление объекта из словаря"""
        try:
            if "stats" in data:
                self.stats.update(data["stats"])
            if "security_policies" in data:
                self.security_policies.update(data["security_policies"])
            self.logger.info("Объект успешно восстановлен из словаря")
        except Exception as e:
            self.logger.error(f"Ошибка восстановления из словаря: {e}")

    def validate_threat_data(self, threat_data: Any) -> bool:
        """Валидация данных угрозы"""
        try:
            if not isinstance(threat_data, SecurityThreat):
                return False

            required_fields = [
                "threat_id",
                "threat_type",
                "severity",
                "confidence",
                "timestamp",
                "device_id",
                "details",
            ]

            for field in required_fields:
                if not hasattr(threat_data, field):
                    return False

            # Дополнительные проверки
            if not isinstance(threat_data.confidence, (int, float)):
                return False
            if not 0 <= threat_data.confidence <= 1:
                return False

            return True
        except Exception as e:
            self.logger.error(f"Ошибка валидации данных угрозы: {e}")
            return False

    def get_threat_statistics(self) -> Dict[str, Any]:
        """Получение статистики по угрозам"""
        try:
            threat_types = {}
            severity_counts = {}

            for threat in self.threats.values():
                # Подсчет по типам
                threat_type = threat.threat_type.value
                threat_types[threat_type] = (
                    threat_types.get(threat_type, 0) + 1
                )

                # Подсчет по серьезности
                severity_counts[threat.severity] = (
                    severity_counts.get(threat.severity, 0) + 1
                )

            return {
                "total_threats": len(self.threats),
                "threat_types": threat_types,
                "severity_distribution": severity_counts,
                "devices_affected": len(self.device_profiles),
                "average_confidence": (
                    sum(t.confidence for t in self.threats.values())
                    / len(self.threats)
                    if self.threats
                    else 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики угроз: {e}")
            return {"error": str(e)}

    def export_threats(self, file_path: str = "threats_export.json") -> bool:
        """Экспорт угроз в файл"""
        try:
            import json
            from datetime import datetime

            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "threats": [
                    {
                        "threat_id": threat.threat_id,
                        "threat_type": threat.threat_type.value,
                        "severity": threat.severity,
                        "confidence": threat.confidence,
                        "timestamp": threat.timestamp.isoformat(),
                        "device_id": threat.device_id,
                        "details": threat.details,
                    }
                    for threat in self.threats.values()
                ],
                "statistics": self.get_threat_statistics(),
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Угрозы успешно экспортированы в {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка экспорта угроз: {e}")
            return False

    def import_threats(self, file_path: str) -> bool:
        """Импорт угроз из файла"""
        try:
            import json
            from datetime import datetime

            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            imported_count = 0
            for threat_data in import_data.get("threats", []):
                try:
                    threat = SecurityThreat(
                        threat_id=threat_data["threat_id"],
                        threat_type=ThreatType(threat_data["threat_type"]),
                        severity=threat_data["severity"],
                        confidence=threat_data["confidence"],
                        timestamp=datetime.fromisoformat(
                            threat_data["timestamp"]
                        ),
                        device_id=threat_data["device_id"],
                        details=threat_data["details"],
                    )
                    self.threats[threat.threat_id] = threat
                    imported_count += 1
                except Exception as e:
                    threat_id = threat_data.get('threat_id', 'unknown')
                    self.logger.warning(
                        f"Ошибка импорта угрозы {threat_id}: {e}"
                    )

            self.logger.info(
                f"Успешно импортировано {imported_count} угроз из {file_path}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка импорта угроз: {e}")
            return False

    def reset_statistics(self) -> None:
        """Сброс статистики"""
        try:
            self.stats = {
                "threats_detected": 0,
                "threats_blocked": 0,
                "false_positives": 0,
                "devices_monitored": 0,
            }
            self.logger.info("Статистика успешно сброшена")
        except Exception as e:
            self.logger.error(f"Ошибка сброса статистики: {e}")

    def update_security_policy(
        self, policy_name: str, policy_data: Dict[str, Any]
    ) -> bool:
        """Обновление политики безопасности"""
        try:
            if policy_name not in self.security_policies:
                self.logger.warning(f"Политика {policy_name} не найдена")
                return False

            # Валидация данных политики
            required_fields = ["enabled", "threshold", "action"]
            for field in required_fields:
                if field not in policy_data:
                    self.logger.error(
                        f"Отсутствует обязательное поле {field} в политике"
                    )
                    return False

            self.security_policies[policy_name].update(policy_data)
            self.logger.info(f"Политика {policy_name} успешно обновлена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления политики {policy_name}: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """Получение конфигурации"""
        try:
            return self.config.copy()
        except Exception as e:
            self.logger.error(f"Ошибка получения конфигурации: {e}")
            return {}

    def update_config(self, config_updates: Dict[str, Any]) -> bool:
        """Обновление конфигурации"""
        try:
            self.config.update(config_updates)
            self.logger.info("Конфигурация успешно обновлена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления конфигурации: {e}")
            return False

    def add_notification(self, message: str, level: str = "info") -> None:
        """Добавление уведомления"""
        try:
            notification = {
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat(),
            }
            self.notifications.append(notification)

            # Ограничиваем количество уведомлений
            if len(self.notifications) > 100:
                self.notifications = self.notifications[-100:]

        except Exception as e:
            self.logger.error(f"Ошибка добавления уведомления: {e}")

    def get_notifications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение уведомлений"""
        try:
            return (
                self.notifications[-limit:]
                if limit > 0
                else self.notifications
            )
        except Exception as e:
            self.logger.error(f"Ошибка получения уведомлений: {e}")
            return []

    def clear_notifications(self) -> None:
        """Очистка уведомлений"""
        try:
            self.notifications.clear()
            self.logger.info("Уведомления очищены")
        except Exception as e:
            self.logger.error(f"Ошибка очистки уведомлений: {e}")


# Глобальный экземпляр
mobile_security_agent_main = MobileSecurityAgentMain()
