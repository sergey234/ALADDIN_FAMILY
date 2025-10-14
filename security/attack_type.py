#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Attack Type Classifier
Классификатор типов атак и угроз

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-25
"""

import json
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase, SecurityLevel
from core.logging_module import LoggingManager


class AttackCategory(Enum):
    """Категории атак"""

    MALWARE = "malware"
    NETWORK = "network"
    WEB_APPLICATION = "web_application"
    SOCIAL_ENGINEERING = "social_engineering"
    INSIDER_THREAT = "insider_threat"
    PHYSICAL = "physical"
    SUPPLY_CHAIN = "supply_chain"
    ZERO_DAY = "zero_day"


class AttackVector(Enum):
    """Векторы атак"""

    NETWORK = "network"
    EMAIL = "email"
    WEB = "web"
    MOBILE = "mobile"
    PHYSICAL = "physical"
    SOCIAL = "social"
    SUPPLY_CHAIN = "supply_chain"
    CLOUD = "cloud"


class AttackSeverity(Enum):
    """Серьезность атак"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AttackStatus(Enum):
    """Статусы атак"""

    DETECTED = "detected"
    ANALYZING = "analyzing"
    CONTAINED = "contained"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class AttackPattern:
    """Паттерн атаки"""

    def __init__(
        self,
        pattern_id: str,
        name: str,
        category: AttackCategory,
        vector: AttackVector,
        severity: AttackSeverity,
        description: str,
        indicators: List[str] = None,
        mitigation: List[str] = None,
        references: List[str] = None,
    ):
        self.pattern_id = pattern_id
        self.name = name
        self.category = category
        self.vector = vector
        self.severity = severity
        self.description = description
        self.indicators = indicators or []
        self.mitigation = mitigation or []
        self.references = references or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class AttackTypeClassifier(SecurityBase):
    """
    Классификатор типов атак и угроз.

    Обеспечивает автоматическую классификацию атак,
    определение векторов атак и рекомендации по противодействию.
    """

    def __init__(
        self,
        name: str = "AttackTypeClassifier",
        security_level: SecurityLevel = SecurityLevel.HIGH,
    ):
        super().__init__(name, security_level)
        self.logger = LoggingManager()
        self.status = ComponentStatus.ACTIVE

        # База знаний атак
        self.attack_patterns: Dict[str, AttackPattern] = {}

        # Статистика классификации
        self.classification_stats = {
            "total_classified": 0,
            "correct_classifications": 0,
            "false_positives": 0,
            "unknown_patterns": 0,
        }

        # Инициализируем базовые паттерны атак
        self._initialize_attack_patterns()

        self.logger.log(
            "INFO", f"AttackTypeClassifier инициализирован: {name}"
        )

    def _initialize_attack_patterns(self):
        """Инициализация базовых паттернов атак"""

        # Malware атаки
        self._add_attack_pattern(
            "malware_001",
            "Ransomware",
            AttackCategory.MALWARE,
            AttackVector.NETWORK,
            AttackSeverity.CRITICAL,
            "Шифрование файлов с требованием выкупа",
            [
                "Файлы с расширениями .encrypted, .locked",
                "Подозрительная активность в сети",
                "Неожиданное шифрование файлов",
            ],
            [
                "Изолировать зараженные системы",
                "Восстановить данные из резервных копий",
                "Обновить антивирусные системы",
            ],
        )

        self._add_attack_pattern(
            "malware_002",
            "Trojan",
            AttackCategory.MALWARE,
            AttackVector.EMAIL,
            AttackSeverity.HIGH,
            "Троянская программа для кражи данных",
            [
                "Подозрительные email вложения",
                "Необычная сетевая активность",
                "Создание новых процессов",
            ],
            [
                "Сканирование антивирусом",
                "Анализ сетевого трафика",
                "Удаление вредоносного ПО",
            ],
        )

        # Network атаки
        self._add_attack_pattern(
            "network_001",
            "DDoS Attack",
            AttackCategory.NETWORK,
            AttackVector.NETWORK,
            AttackSeverity.HIGH,
            'Распределенная атака типа "отказ в обслуживании"',
            [
                "Аномально высокий трафик",
                "Множественные IP-адреса",
                "Превышение лимитов соединений",
            ],
            [
                "Активировать DDoS защиту",
                "Использовать CDN",
                "Настроить rate limiting",
            ],
        )

        self._add_attack_pattern(
            "network_002",
            "Port Scanning",
            AttackCategory.NETWORK,
            AttackVector.NETWORK,
            AttackSeverity.MEDIUM,
            "Сканирование портов для поиска уязвимостей",
            [
                "Множественные подключения к портам",
                "Быстрые последовательные запросы",
                "Подключения к нестандартным портам",
            ],
            [
                "Настроить firewall",
                "Мониторить сетевую активность",
                "Использовать intrusion detection",
            ],
        )

        # Web Application атаки
        self._add_attack_pattern(
            "web_001",
            "SQL Injection",
            AttackCategory.WEB_APPLICATION,
            AttackVector.WEB,
            AttackSeverity.CRITICAL,
            "Внедрение SQL-кода в параметры приложения",
            [
                "Подозрительные SQL-запросы в логах",
                "Ошибки базы данных",
                "Необычные параметры в URL",
            ],
            [
                "Использовать параметризованные запросы",
                "Валидировать пользовательский ввод",
                "Применить принцип минимальных привилегий",
            ],
        )

        self._add_attack_pattern(
            "web_002",
            "Cross-Site Scripting (XSS)",
            AttackCategory.WEB_APPLICATION,
            AttackVector.WEB,
            AttackSeverity.HIGH,
            "Внедрение вредоносного JavaScript кода",
            [
                "Подозрительный JavaScript в запросах",
                "Аномальная активность в браузере",
                "Кража сессионных cookies",
            ],
            [
                "Экранирование пользовательского ввода",
                "Использование Content Security Policy",
                "Валидация и санитизация данных",
            ],
        )

        # Social Engineering атаки
        self._add_attack_pattern(
            "social_001",
            "Phishing",
            AttackCategory.SOCIAL_ENGINEERING,
            AttackVector.EMAIL,
            AttackSeverity.HIGH,
            "Фишинговая атака через поддельные email",
            [
                "Подозрительные email адреса",
                "Ссылки на поддельные сайты",
                "Запросы конфиденциальной информации",
            ],
            [
                "Обучение пользователей",
                "Фильтрация email",
                "Проверка подлинности отправителя",
            ],
        )

        self._add_attack_pattern(
            "social_002",
            "Vishing",
            AttackCategory.SOCIAL_ENGINEERING,
            AttackVector.SOCIAL,
            AttackSeverity.MEDIUM,
            "Голосовой фишинг через телефонные звонки",
            [
                "Подозрительные телефонные звонки",
                "Запросы конфиденциальной информации по телефону",
                "Имитация официальных организаций",
            ],
            [
                "Верификация личности звонящего",
                "Политика неразглашения информации по телефону",
                "Обучение сотрудников",
            ],
        )

        # Insider Threat атаки
        self._add_attack_pattern(
            "insider_001",
            "Data Exfiltration",
            AttackCategory.INSIDER_THREAT,
            AttackVector.NETWORK,
            AttackSeverity.CRITICAL,
            "Кража данных внутренним нарушителем",
            [
                "Аномальное копирование файлов",
                "Использование внешних носителей",
                "Необычная активность в нерабочее время",
            ],
            [
                "Мониторинг доступа к данным",
                "Ограничение использования внешних носителей",
                "Анализ поведения пользователей",
            ],
        )

        # Zero Day атаки
        self._add_attack_pattern(
            "zeroday_001",
            "Zero Day Exploit",
            AttackCategory.ZERO_DAY,
            AttackVector.NETWORK,
            AttackSeverity.CRITICAL,
            "Эксплойт для неизвестной уязвимости",
            [
                "Аномальное поведение системы",
                "Неожиданные сбои приложений",
                "Подозрительная активность процессов",
            ],
            [
                "Мониторинг аномалий",
                "Применение принципа минимальных привилегий",
                "Быстрое реагирование на инциденты",
            ],
        )

    def _add_attack_pattern(
        self,
        pattern_id: str,
        name: str,
        category: AttackCategory,
        vector: AttackVector,
        severity: AttackSeverity,
        description: str,
        indicators: List[str],
        mitigation: List[str],
    ):
        """Добавление нового паттерна атаки"""

        pattern = AttackPattern(
            pattern_id=pattern_id,
            name=name,
            category=category,
            vector=vector,
            severity=severity,
            description=description,
            indicators=indicators,
            mitigation=mitigation,
        )

        self.attack_patterns[pattern_id] = pattern

    def classify_attack(
        self, indicators: List[str], context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Классификация атаки на основе индикаторов.

        Args:
            indicators: Список индикаторов атаки
            context: Дополнительный контекст

        Returns:
            Dict: Результат классификации
        """
        try:
            self.classification_stats["total_classified"] += 1

            # Поиск совпадений с паттернами атак
            matches = []
            for pattern_id, pattern in self.attack_patterns.items():
                match_score = self._calculate_match_score(
                    indicators, pattern.indicators
                )
                if match_score > 0.3:  # Порог совпадения
                    matches.append({"pattern": pattern, "score": match_score})

            # Сортируем по релевантности
            matches.sort(key=lambda x: x["score"], reverse=True)

            if matches:
                best_match = matches[0]
                self.classification_stats["correct_classifications"] += 1

                result = {
                    "attack_detected": True,
                    "confidence": best_match["score"],
                    "attack_type": {
                        "id": best_match["pattern"].pattern_id,
                        "name": best_match["pattern"].name,
                        "category": best_match["pattern"].category.value,
                        "vector": best_match["pattern"].vector.value,
                        "severity": best_match["pattern"].severity.value,
                        "description": best_match["pattern"].description,
                    },
                    "mitigation": best_match["pattern"].mitigation,
                    "alternative_matches": [
                        {
                            "name": match["pattern"].name,
                            "score": match["score"],
                        }
                        for match in matches[1:3]  # Топ-3 альтернативы
                    ],
                }
            else:
                self.classification_stats["unknown_patterns"] += 1
                result = {
                    "attack_detected": False,
                    "confidence": 0.0,
                    "message": "Неизвестный тип атаки",
                    "suggestions": self._get_general_mitigation(),
                }

            result["classification_id"] = f"class_{int(time.time())}"
            result["timestamp"] = datetime.now().isoformat()

            self.logger.log(
                "INFO",
                f"Классификация завершена: "
                f"{result.get('attack_type', {}).get('name', 'Unknown')}",
            )
            return result

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка классификации атаки: {e}")
            return {
                "attack_detected": False,
                "error": str(e),
                "classification_id": f"error_{int(time.time())}",
            }

    def _calculate_match_score(
        self, indicators: List[str], pattern_indicators: List[str]
    ) -> float:
        """
        Расчет степени совпадения индикаторов.

        Args:
            indicators: Индикаторы атаки
            pattern_indicators: Индикаторы паттерна

        Returns:
            float: Оценка совпадения (0-1)
        """
        if not indicators or not pattern_indicators:
            return 0.0

        matches = 0
        for indicator in indicators:
            indicator_lower = indicator.lower()
            for pattern_indicator in pattern_indicators:
                pattern_lower = pattern_indicator.lower()
                # Проверяем частичное совпадение
                if (
                    indicator_lower in pattern_lower
                    or pattern_lower in indicator_lower
                    or self._calculate_text_similarity(
                        indicator_lower, pattern_lower
                    )
                    > 0.7
                ):
                    matches += 1
                    break

        return matches / len(indicators)

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Простой расчет схожести текста.

        Args:
            text1: Первый текст
            text2: Второй текст

        Returns:
            float: Степень схожести (0-1)
        """
        # Простая реализация на основе общих слов
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _get_general_mitigation(self) -> List[str]:
        """Получение общих рекомендаций по противодействию"""
        return [
            "Изолировать подозрительные системы",
            "Собрать и проанализировать логи",
            "Уведомить команду безопасности",
            "Провести дополнительное расследование",
            "Обновить системы мониторинга",
        ]

    def get_attack_patterns(
        self,
        category: Optional[AttackCategory] = None,
        severity: Optional[AttackSeverity] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получение паттернов атак с фильтрацией.

        Args:
            category: Категория атак
            severity: Серьезность атак

        Returns:
            List[Dict]: Список паттернов атак
        """
        try:
            patterns = []

            for pattern in self.attack_patterns.values():
                if category and pattern.category != category:
                    continue
                if severity and pattern.severity != severity:
                    continue

                patterns.append(
                    {
                        "id": pattern.pattern_id,
                        "name": pattern.name,
                        "category": pattern.category.value,
                        "vector": pattern.vector.value,
                        "severity": pattern.severity.value,
                        "description": pattern.description,
                        "indicators_count": len(pattern.indicators),
                        "mitigation_count": len(pattern.mitigation),
                    }
                )

            return patterns

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка получения паттернов атак: {e}")
            return []

    def add_custom_attack_pattern(
        self,
        name: str,
        category: AttackCategory,
        vector: AttackVector,
        severity: AttackSeverity,
        description: str,
        indicators: List[str],
        mitigation: List[str],
    ) -> str:
        """
        Добавление пользовательского паттерна атаки.

        Args:
            name: Название атаки
            category: Категория атаки
            vector: Вектор атаки
            severity: Серьезность атаки
            description: Описание атаки
            indicators: Индикаторы атаки
            mitigation: Рекомендации по противодействию

        Returns:
            str: ID созданного паттерна
        """
        try:
            pattern_id = f"custom_{int(time.time())}"

            self._add_attack_pattern(
                pattern_id=pattern_id,
                name=name,
                category=category,
                vector=vector,
                severity=severity,
                description=description,
                indicators=indicators,
                mitigation=mitigation,
            )

            self.logger.log(
                "INFO",
                f"Добавлен пользовательский паттерн: {name} ({pattern_id})",
            )
            return pattern_id

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка добавления паттерна: {e}")
            return ""

    def get_classification_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики классификации.

        Returns:
            Dict: Статистика классификации
        """
        total = self.classification_stats["total_classified"]

        if total == 0:
            accuracy = 0.0
        else:
            accuracy = (
                self.classification_stats["correct_classifications"] / total
            )

        return {
            "total_classifications": total,
            "correct_classifications": self.classification_stats[
                "correct_classifications"
            ],
            "false_positives": self.classification_stats["false_positives"],
            "unknown_patterns": self.classification_stats["unknown_patterns"],
            "accuracy": round(accuracy * 100, 2),
            "attack_patterns_count": len(self.attack_patterns),
            "last_updated": datetime.now().isoformat(),
        }

    def export_attack_patterns(self, format: str = "json") -> Optional[str]:
        """
        Экспорт базы знаний атак.

        Args:
            format: Формат экспорта

        Returns:
            Optional[str]: Путь к файлу экспорта
        """
        try:
            if format == "json":
                export_data = {
                    "attack_patterns": [],
                    "export_info": {
                        "timestamp": datetime.now().isoformat(),
                        "total_patterns": len(self.attack_patterns),
                        "version": "1.0",
                    },
                }

                for pattern in self.attack_patterns.values():
                    export_data["attack_patterns"].append(
                        {
                            "id": pattern.pattern_id,
                            "name": pattern.name,
                            "category": pattern.category.value,
                            "vector": pattern.vector.value,
                            "severity": pattern.severity.value,
                            "description": pattern.description,
                            "indicators": pattern.indicators,
                            "mitigation": pattern.mitigation,
                            "created_at": pattern.created_at.isoformat(),
                            "updated_at": pattern.updated_at.isoformat(),
                        }
                    )

                filename = f"attack_patterns_{int(time.time())}.json"
                filepath = f"exports/{filename}"

                # Создаем директорию exports если её нет
                import os

                os.makedirs("exports", exist_ok=True)

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                self.logger.log(
                    "INFO", f"База знаний экспортирована: {filepath}"
                )
                return filepath

            return None

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка экспорта: {e}")
            return None


# Пример использования
if __name__ == "__main__":
    # Создаем классификатор
    classifier = AttackTypeClassifier()

    # Пример классификации атаки
    indicators = [
        "Подозрительные SQL-запросы в логах",
        "Ошибки базы данных",
        "Необычные параметры в URL",
    ]

    result = classifier.classify_attack(indicators)
    print(f"Результат классификации: {result}")

    # Получаем статистику
    stats = classifier.get_classification_statistics()
    print(f"Статистика: {stats}")

    # Получаем паттерны атак
    patterns = classifier.get_attack_patterns(severity=AttackSeverity.CRITICAL)
    print(f"Критические атаки: {len(patterns)}")
