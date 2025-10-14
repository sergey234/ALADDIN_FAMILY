#!/usr/bin/env python3
"""
📱 ALADDIN - SIM Card Monitoring Integration
Интеграция для мониторинга SIM-карт и защиты от мошенничества

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class SIMCardAnalysis:
    """Результат анализа SIM-карты"""

    sim_id: str
    phone_number: str
    is_legitimate: bool
    risk_score: float
    suspicious_indicators: List[str]
    recommendation: str
    timestamp: datetime
    details: Dict[str, Any]


@dataclass
class CallAnalysis:
    """Результат анализа звонка"""

    call_id: str
    caller_number: str
    receiver_number: str
    is_safe: bool
    caller_type: str  # family, friend, business, scam, unknown
    confidence: float
    blocking_recommendation: str
    timestamp: datetime
    details: Dict[str, Any]


class SIMCardMonitoring:
    """
    Система мониторинга SIM-карт и анализа звонков.
    Защищает от мошеннических звонков, не блокируя родных и друзей.
    """

    def __init__(
        self, config_path: str = "config/sim_card_monitoring_config.json"
    ):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = self.setup_logger()

        # Статистика
        self.total_calls_analyzed = 0
        self.scam_calls_blocked = 0
        self.false_positives = 0
        self.family_friends_allowed = 0

        # Базы данных
        self.trusted_contacts = self.load_trusted_contacts()
        self.scam_database = self.load_scam_database()
        self.carrier_database = self.load_carrier_database()

    def load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию мониторинга SIM-карт"""
        try:
            import json

            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем базовую конфигурацию
            default_config = {
                "enabled": True,
                "strict_mode": False,  # Важно: не строгий режим для семьи
                "auto_block_scams": True,
                "family_protection_mode": True,
                "call_analysis_threshold": 0.7,
                "sim_verification_enabled": True,
                "carrier_verification_enabled": True,
                "trusted_contacts_priority": True,
                "false_positive_prevention": True,
                "emergency_contacts_always_allowed": True,
                "business_hours_protection": True,
                "weekend_family_mode": True,
            }
            return default_config

    def setup_logger(self) -> logging.Logger:
        """Настройка логирования"""
        logger = logging.getLogger("sim_card_monitoring")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def load_trusted_contacts(self) -> Dict[str, Dict[str, Any]]:
        """Загружает базу доверенных контактов (семья, друзья)"""
        return {
            # Примеры доверенных контактов
            "+7-900-123-45-67": {
                "type": "family",
                "name": "Мама",
                "priority": "emergency",
                "always_allow": True,
                "added_date": "2024-01-01",
            },
            "+7-900-234-56-78": {
                "type": "family",
                "name": "Папа",
                "priority": "emergency",
                "always_allow": True,
                "added_date": "2024-01-01",
            },
            "+7-900-345-67-89": {
                "type": "friend",
                "name": "Лучший друг",
                "priority": "high",
                "always_allow": True,
                "added_date": "2024-01-15",
            },
            "+7-900-456-78-90": {
                "type": "work",
                "name": "Рабочий телефон",
                "priority": "medium",
                "always_allow": True,
                "added_date": "2024-02-01",
            },
        }

    def load_scam_database(self) -> Dict[str, Any]:
        """Загружает базу данных мошеннических номеров"""
        return {
            # Известные мошеннические номера
            "+7-800-555-00-00": {
                "type": "scam",
                "description": "Финансовое мошенничество",
                "confidence": 0.95,
                "reported_count": 150,
                "last_seen": "2024-12-01",
            },
            "+7-900-999-99-99": {
                "type": "scam",
                "description": "Социальная инженерия",
                "confidence": 0.88,
                "reported_count": 89,
                "last_seen": "2024-11-28",
            },
        }

    def load_carrier_database(self) -> Dict[str, Any]:
        """Загружает базу данных операторов связи"""
        return {
            "mts": {
                "prefixes": [
                    "+7-910",
                    "+7-915",
                    "+7-916",
                    "+7-917",
                    "+7-918",
                    "+7-919",
                ],
                "legitimate": True,
            },
            "megafon": {
                "prefixes": [
                    "+7-920",
                    "+7-921",
                    "+7-922",
                    "+7-923",
                    "+7-924",
                    "+7-925",
                ],
                "legitimate": True,
            },
            "beeline": {
                "prefixes": ["+7-903", "+7-905", "+7-906", "+7-909"],
                "legitimate": True,
            },
            "tele2": {
                "prefixes": ["+7-900", "+7-901", "+7-902", "+7-904", "+7-908"],
                "legitimate": True,
            },
            "virtual": {
                "prefixes": ["+7-800", "+7-804", "+7-808"],
                "legitimate": False,
                "warning": "Виртуальные номера - повышенный риск",
            },
        }

    def analyze_sim_card(self, sim_data: Dict[str, Any]) -> SIMCardAnalysis:
        """
        Анализирует SIM-карту на предмет легитимности.

        Args:
            sim_data: Данные SIM-карты

        Returns:
            SIMCardAnalysis: Результат анализа
        """
        self.logger.info(
            f"Анализ SIM-карты: {sim_data.get('phone_number', 'unknown')}"
        )

        sim_id = sim_data.get("sim_id", f"sim_{datetime.now().timestamp()}")
        phone_number = sim_data.get("phone_number", "")
        is_legitimate = True
        risk_score = 0.0
        suspicious_indicators = []
        recommendation = "allow"

        # Проверка на доверенные контакты
        if phone_number in self.trusted_contacts:
            contact_info = self.trusted_contacts[phone_number]
            if contact_info.get("always_allow", False):
                recommendation = "always_allow"
                self.logger.info(
                    f"SIM-карта {phone_number} в списке доверенных контактов"
                )
                return SIMCardAnalysis(
                    sim_id=sim_id,
                    phone_number=phone_number,
                    is_legitimate=True,
                    risk_score=0.0,
                    suspicious_indicators=[],
                    recommendation="always_allow",
                    timestamp=datetime.now(),
                    details=sim_data,
                )

        # Проверка на мошеннические номера
        if phone_number in self.scam_database:
            scam_info = self.scam_database[phone_number]
            is_legitimate = False
            risk_score = scam_info.get("confidence", 0.9)
            suspicious_indicators.append("known_scam_number")
            suspicious_indicators.append(scam_info.get("description", "scam"))
            recommendation = "block"
            self.logger.warning(
                f"SIM-карта {phone_number} в базе мошеннических номеров"
            )

        # Анализ оператора связи
        carrier_analysis = self.analyze_carrier(phone_number)
        if not carrier_analysis["is_legitimate"]:
            risk_score += 0.3
            suspicious_indicators.append("suspicious_carrier")
            if risk_score > 0.7:
                recommendation = "block"

        # Анализ паттернов номера
        number_pattern_analysis = self.analyze_number_patterns(phone_number)
        if number_pattern_analysis["is_suspicious"]:
            risk_score += number_pattern_analysis["risk_score"]
            suspicious_indicators.extend(number_pattern_analysis["indicators"])

        # Финальная оценка
        if risk_score >= self.config.get("call_analysis_threshold", 0.7):
            is_legitimate = False
            if recommendation != "block":
                recommendation = "block"

        # Обновление статистики
        if not is_legitimate:
            self.scam_calls_blocked += 1

        analysis = SIMCardAnalysis(
            sim_id=sim_id,
            phone_number=phone_number,
            is_legitimate=is_legitimate,
            risk_score=risk_score,
            suspicious_indicators=suspicious_indicators,
            recommendation=recommendation,
            timestamp=datetime.now(),
            details=sim_data,
        )

        self.logger.info(
            f"SIM card analysis: {sim_id}, legitimate={is_legitimate}, "
            f"risk={risk_score:.2f}, recommendation={recommendation}"
        )
        return analysis

    def analyze_call(self, call_data: Dict[str, Any]) -> CallAnalysis:
        """
        Анализирует входящий звонок на предмет безопасности.

        Args:
            call_data: Данные звонка

        Returns:
            CallAnalysis: Результат анализа
        """
        self.logger.info(
            f"Анализ звонка: {call_data.get('caller_number', 'unknown')}"
        )

        call_id = call_data.get(
            "call_id", f"call_{datetime.now().timestamp()}"
        )
        caller_number = call_data.get("caller_number", "")
        receiver_number = call_data.get("receiver_number", "")
        is_safe = True
        caller_type = "unknown"
        confidence = 1.0
        blocking_recommendation = "allow"

        # ПРИОРИТЕТ 1: Проверка на экстренные контакты
        if caller_number in self.trusted_contacts:
            contact_info = self.trusted_contacts[caller_number]
            caller_type = contact_info.get("type", "family")
            if contact_info.get("always_allow", False):
                is_safe = True
                confidence = 1.0
                blocking_recommendation = "never_block"
                self.family_friends_allowed += 1
                self.logger.info(
                    f"Звонок от доверенного контакта: {contact_info.get('name', caller_number)}"
                )
                return CallAnalysis(
                    call_id=call_id,
                    caller_number=caller_number,
                    receiver_number=receiver_number,
                    is_safe=True,
                    caller_type=caller_type,
                    confidence=confidence,
                    blocking_recommendation="never_block",
                    timestamp=datetime.now(),
                    details=call_data,
                )

        # ПРИОРИТЕТ 2: Проверка на мошеннические номера
        if caller_number in self.scam_database:
            scam_info = self.scam_database[caller_number]
            is_safe = False
            caller_type = "scam"
            confidence = scam_info.get("confidence", 0.9)
            blocking_recommendation = "block_immediately"
            self.scam_calls_blocked += 1
            self.logger.warning(
                f"Блокировка мошеннического звонка: {caller_number}"
            )
            return CallAnalysis(
                call_id=call_id,
                caller_number=caller_number,
                receiver_number=receiver_number,
                is_safe=False,
                caller_type=caller_type,
                confidence=confidence,
                blocking_recommendation="block_immediately",
                timestamp=datetime.now(),
                details=call_data,
            )

        # ПРИОРИТЕТ 3: Анализ контекста звонка
        context_analysis = self.analyze_call_context(call_data)

        # ПРИОРИТЕТ 4: Анализ поведения звонящего
        behavior_analysis = self.analyze_caller_behavior(
            caller_number, call_data
        )

        # ПРИОРИТЕТ 5: Временной анализ
        time_analysis = self.analyze_call_timing(call_data)

        # Объединение анализов
        total_risk = (
            context_analysis["risk_score"] * 0.4
            + behavior_analysis["risk_score"] * 0.4
            + time_analysis["risk_score"] * 0.2
        )

        # Определение типа звонящего
        if total_risk < 0.3:
            caller_type = "legitimate"
            confidence = 0.9
            blocking_recommendation = "allow"
        elif total_risk < 0.6:
            caller_type = "unknown"
            confidence = 0.7
            blocking_recommendation = "monitor"
        else:
            caller_type = "suspicious"
            confidence = 0.8
            blocking_recommendation = "block"
            is_safe = False

        # Обновление статистики
        self.total_calls_analyzed += 1

        analysis = CallAnalysis(
            call_id=call_id,
            caller_number=caller_number,
            receiver_number=receiver_number,
            is_safe=is_safe,
            caller_type=caller_type,
            confidence=confidence,
            blocking_recommendation=blocking_recommendation,
            timestamp=datetime.now(),
            details=call_data,
        )

        self.logger.info(
            f"Call analysis: {call_id}, safe={is_safe}, type={caller_type}, "
            f"confidence={confidence:.2f}, recommendation={blocking_recommendation}"
        )
        return analysis

    def analyze_carrier(self, phone_number: str) -> Dict[str, Any]:
        """Анализирует оператора связи"""
        for carrier, info in self.carrier_database.items():
            for prefix in info["prefixes"]:
                if phone_number.startswith(prefix):
                    return {
                        "carrier": carrier,
                        "is_legitimate": info["legitimate"],
                        "warning": info.get("warning", ""),
                    }

        return {
            "carrier": "unknown",
            "is_legitimate": False,
            "warning": "Неизвестный оператор",
        }

    def analyze_number_patterns(self, phone_number: str) -> Dict[str, Any]:
        """Анализирует паттерны номера телефона"""
        risk_score = 0.0
        indicators = []

        # Проверка на повторяющиеся цифры
        if len(set(phone_number)) < 4:
            risk_score += 0.3
            indicators.append("repeating_digits")

        # Проверка на последовательные цифры
        if "123456" in phone_number or "654321" in phone_number:
            risk_score += 0.4
            indicators.append("sequential_digits")

        # Проверка длины номера
        if len(phone_number) < 10 or len(phone_number) > 15:
            risk_score += 0.2
            indicators.append("unusual_length")

        return {
            "is_suspicious": risk_score > 0.5,
            "risk_score": risk_score,
            "indicators": indicators,
        }

    def analyze_call_context(
        self, call_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Анализирует контекст звонка"""
        risk_score = 0.0

        # Анализ времени звонка
        call_time = call_data.get("timestamp", datetime.now())
        if isinstance(call_time, str):
            call_time = datetime.fromisoformat(call_time)

        # Подозрительные часы (ночные звонки от неизвестных)
        if call_time.hour < 7 or call_time.hour > 22:
            risk_score += 0.2

        # Анализ частоты звонков
        caller_number = call_data.get("caller_number", "")
        recent_calls = self.get_recent_calls_count(caller_number, hours=24)
        if recent_calls > 5:  # Более 5 звонков за день
            risk_score += 0.3

        return {"risk_score": risk_score}

    def analyze_caller_behavior(
        self, caller_number: str, call_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Анализирует поведение звонящего"""
        risk_score = 0.0

        # Проверка истории звонков
        call_history = self.get_call_history(caller_number)

        # Если это первый звонок от номера
        if len(call_history) == 0:
            risk_score += 0.1

        # Если много звонков подряд
        recent_calls = [
            c
            for c in call_history
            if (
                datetime.now() - c.get("timestamp", datetime.now())
            ).total_seconds()
            < 3600
        ]
        if len(recent_calls) > 3:
            risk_score += 0.4

        return {"risk_score": risk_score}

    def analyze_call_timing(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует время звонка"""
        risk_score = 0.0

        call_time = call_data.get("timestamp", datetime.now())
        if isinstance(call_time, str):
            call_time = datetime.fromisoformat(call_time)

        # Рабочие часы - меньше риска
        if 9 <= call_time.hour <= 18:
            risk_score -= 0.1

        # Выходные - больше риска от неизвестных
        if call_time.weekday() >= 5:  # Суббота, воскресенье
            risk_score += 0.2

        return {"risk_score": max(risk_score, 0.0)}

    def get_recent_calls_count(
        self, caller_number: str, hours: int = 24
    ) -> int:
        """Получает количество недавних звонков от номера"""
        # В реальной системе здесь был бы запрос к базе данных
        return 0

    def get_call_history(self, caller_number: str) -> List[Dict[str, Any]]:
        """Получает историю звонков от номера"""
        # В реальной системе здесь был бы запрос к базе данных
        return []

    def add_trusted_contact(
        self, phone_number: str, contact_info: Dict[str, Any]
    ) -> bool:
        """Добавляет доверенный контакт"""
        try:
            self.trusted_contacts[phone_number] = contact_info
            self.logger.info(
                f"Добавлен доверенный контакт: {contact_info.get('name', phone_number)}"
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Ошибка добавления доверенного контакта: {str(e)}"
            )
            return False

    def report_scam_number(
        self, phone_number: str, scam_info: Dict[str, Any]
    ) -> bool:
        """Сообщает о мошенническом номере"""
        try:
            self.scam_database[phone_number] = scam_info
            self.logger.warning(
                f"Добавлен мошеннический номер: {phone_number}"
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Ошибка добавления мошеннического номера: {str(e)}"
            )
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику мониторинга"""
        false_positive_rate = (
            self.false_positives / max(self.total_calls_analyzed, 1) * 100
        )
        family_friends_rate = (
            self.family_friends_allowed
            / max(self.total_calls_analyzed, 1)
            * 100
        )

        return {
            "total_calls_analyzed": self.total_calls_analyzed,
            "scam_calls_blocked": self.scam_calls_blocked,
            "false_positives": self.false_positives,
            "family_friends_allowed": self.family_friends_allowed,
            "false_positive_rate": false_positive_rate,
            "family_friends_rate": family_friends_rate,
            "trusted_contacts_count": len(self.trusted_contacts),
            "scam_database_size": len(self.scam_database),
            "enabled": self.config.get("enabled", True),
            "family_protection_mode": self.config.get(
                "family_protection_mode", True
            ),
        }
