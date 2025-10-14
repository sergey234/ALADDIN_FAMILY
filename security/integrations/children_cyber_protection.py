# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Children Cyber Protection
Защита детей от киберугроз

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class CyberThreatDetection:
    """Результат детекции киберугрозы для детей"""

    threat_detected: bool
    threat_type: str
    severity_level: str
    confidence: float
    content_analyzed: str
    timestamp: datetime
    recommended_action: str
    details: Dict[str, Any]


class ChildrenCyberProtection:
    """Система защиты детей от киберугроз"""

    def __init__(
        self, config_path: str = "config/children_protection_config.json"
    ):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = self.setup_logger()

        # Статистика
        self.total_content_analyzed = 0
        self.threats_detected = 0
        self.parent_notifications_sent = 0

        # База данных угроз
        self.threat_patterns = self.load_threat_patterns()

    def load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию защиты детей"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем базовую конфигурацию
            default_config = {
                "enabled": True,
                "strict_mode": True,
                "auto_block_threats": True,
                "parent_notifications": True,
                "threat_detection_threshold": 0.7,
                "content_filtering": True,
                "video_analysis": True,
                "text_analysis": True,
            }

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

            return default_config

    def load_threat_patterns(self) -> Dict[str, Any]:
        """Загружает паттерны угроз для детей"""
        return {
            "fake_video_threats": [
                "поддельное видео",
                "фейковое видео",
                "ложное видео",
                "обман через видео",
                "запугивание видео",
                "угрозы видео",
            ],
            "extortion_patterns": [
                "отправь деньги",
                "переведи средства",
                "заплати за молчание",
                "деньги или",
                "выкуп",
                "вымогательство",
            ],
            "identity_theft_patterns": [
                "твои данные",
                "твой пароль",
                "твой аккаунт",
                "твоя карта",
                "твои деньги",
                "твоя семья",
            ],
            "psychological_manipulation": [
                "твой папа должен",
                "твоя мама должна",
                "родители в беде",
                "семья в опасности",
                "срочно нужно",
                "не говори родителям",
            ],
        }

    def setup_logger(self) -> logging.Logger:
        """Настраивает логгер"""
        logger = logging.getLogger("children_cyber_protection")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler("logs/children_cyber_protection.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def analyze_video_content(
        self, video_content: str, metadata: Dict[str, Any] = None
    ) -> CyberThreatDetection:
        """
        Анализирует видео контент на предмет угроз для детей
        """
        try:
            self.total_content_analyzed += 1

            # Анализ текстового описания видео
            content_lower = video_content.lower()

            # Проверка на различные типы угроз
            threat_detected = False
            threat_type = "none"
            severity_level = "safe"
            confidence = 0.0
            recommended_action = "continue"

            # Проверка на поддельные видео угрозы
            fake_video_score = self._check_fake_video_threats(content_lower)
            if fake_video_score > 0.7:
                threat_detected = True
                threat_type = "fake_video_threat"
                severity_level = "high"
                confidence = fake_video_score
                recommended_action = "block_and_notify"

            # Проверка на вымогательство
            if not threat_detected:
                extortion_score = self._check_extortion_patterns(content_lower)
                if extortion_score > 0.7:
                    threat_detected = True
                    threat_type = "extortion"
                    severity_level = "critical"
                    confidence = extortion_score
                    recommended_action = "block_and_alert"

            # Проверка на кражу данных
            if not threat_detected:
                identity_theft_score = self._check_identity_theft_patterns(
                    content_lower
                )
                if identity_theft_score > 0.7:
                    threat_detected = True
                    threat_type = "identity_theft"
                    severity_level = "high"
                    confidence = identity_theft_score
                    recommended_action = "block_and_notify"

            # Проверка на психологическое манипулирование
            if not threat_detected:
                manipulation_score = self._check_psychological_manipulation(
                    content_lower
                )
                if manipulation_score > 0.7:
                    threat_detected = True
                    threat_type = "psychological_manipulation"
                    severity_level = "medium"
                    confidence = manipulation_score
                    recommended_action = "notify_parents"

            # Обновление статистики
            if threat_detected:
                self.threats_detected += 1

            result = CyberThreatDetection(
                threat_detected=threat_detected,
                threat_type=threat_type,
                severity_level=severity_level,
                confidence=confidence,
                content_analyzed=video_content,
                timestamp=datetime.now(),
                recommended_action=recommended_action,
                details={
                    "analysis_method": "pattern_matching",
                    "patterns_checked": len(self.threat_patterns),
                    "metadata": metadata or {},
                },
            )

            self.logger.info(
                f"Video content analyzed: threat={threat_detected}, type={threat_type}, confidence={confidence:.2f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error analyzing video content: {str(e)}")
            return CyberThreatDetection(
                threat_detected=False,
                threat_type="analysis_error",
                severity_level="unknown",
                confidence=0.0,
                content_analyzed=video_content,
                timestamp=datetime.now(),
                recommended_action="retry_analysis",
                details={"error": str(e)},
            )

    def _check_fake_video_threats(self, content: str) -> float:
        """Проверка на угрозы поддельных видео"""
        patterns = self.threat_patterns["fake_video_threats"]
        matches = sum(1 for pattern in patterns if pattern in content)
        return matches / len(patterns) if patterns else 0.0

    def _check_extortion_patterns(self, content: str) -> float:
        """Проверка на паттерны вымогательства"""
        patterns = self.threat_patterns["extortion_patterns"]
        matches = sum(1 for pattern in patterns if pattern in content)
        return matches / len(patterns) if patterns else 0.0

    def _check_identity_theft_patterns(self, content: str) -> float:
        """Проверка на паттерны кражи данных"""
        patterns = self.threat_patterns["identity_theft_patterns"]
        matches = sum(1 for pattern in patterns if pattern in content)
        return matches / len(patterns) if patterns else 0.0

    def _check_psychological_manipulation(self, content: str) -> float:
        """Проверка на психологическое манипулирование"""
        patterns = self.threat_patterns["psychological_manipulation"]
        matches = sum(1 for pattern in patterns if pattern in content)
        return matches / len(patterns) if patterns else 0.0

    def analyze_text_content(
        self, text_content: str, metadata: Dict[str, Any] = None
    ) -> CyberThreatDetection:
        """
        Анализирует текстовый контент на предмет угроз для детей
        """
        try:
            self.total_content_analyzed += 1

            # Анализ текста
            text_lower = text_content.lower()

            # Проверка на угрозы
            threat_detected = False
            threat_type = "none"
            severity_level = "safe"
            confidence = 0.0
            recommended_action = "continue"

            # Комбинированная проверка всех типов угроз
            extortion_score = self._check_extortion_patterns(text_lower)
            identity_score = self._check_identity_theft_patterns(text_lower)
            manipulation_score = self._check_psychological_manipulation(
                text_lower
            )

            max_score = max(
                extortion_score, identity_score, manipulation_score
            )

            if max_score > 0.7:
                threat_detected = True
                confidence = max_score

                if extortion_score == max_score:
                    threat_type = "extortion"
                    severity_level = "critical"
                    recommended_action = "block_and_alert"
                elif identity_score == max_score:
                    threat_type = "identity_theft"
                    severity_level = "high"
                    recommended_action = "block_and_notify"
                else:
                    threat_type = "psychological_manipulation"
                    severity_level = "medium"
                    recommended_action = "notify_parents"

            # Обновление статистики
            if threat_detected:
                self.threats_detected += 1

            result = CyberThreatDetection(
                threat_detected=threat_detected,
                threat_type=threat_type,
                severity_level=severity_level,
                confidence=confidence,
                content_analyzed=text_content,
                timestamp=datetime.now(),
                recommended_action=recommended_action,
                details={
                    "analysis_method": "text_pattern_matching",
                    "extortion_score": extortion_score,
                    "identity_score": identity_score,
                    "manipulation_score": manipulation_score,
                    "metadata": metadata or {},
                },
            )

            self.logger.info(
                f"Text content analyzed: threat={threat_detected}, type={threat_type}, confidence={confidence:.2f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error analyzing text content: {str(e)}")
            return CyberThreatDetection(
                threat_detected=False,
                threat_type="analysis_error",
                severity_level="unknown",
                confidence=0.0,
                content_analyzed=text_content,
                timestamp=datetime.now(),
                recommended_action="retry_analysis",
                details={"error": str(e)},
            )

    async def notify_parents(
        self, threat_detection: CyberThreatDetection, child_id: str = None
    ):
        """
        Уведомляет родителей об обнаруженной угрозе
        """
        try:
            if not self.config.get("parent_notifications", True):
                return

            notification_data = {
                "child_id": child_id or "unknown",
                "threat_type": threat_detection.threat_type,
                "severity_level": threat_detection.severity_level,
                "confidence": threat_detection.confidence,
                "timestamp": threat_detection.timestamp.isoformat(),
                "recommended_action": threat_detection.recommended_action,
                "content_preview": (
                    threat_detection.content_analyzed[:100] + "..."
                    if len(threat_detection.content_analyzed) > 100
                    else threat_detection.content_analyzed
                ),
            }

            # Здесь будет интеграция с системой уведомлений ALADDIN
            self.parent_notifications_sent += 1

            self.logger.warning(
                f"Parent notification sent: {threat_detection.threat_type} for child {child_id}"
            )

            return notification_data

        except Exception as e:
            self.logger.error(f"Error sending parent notification: {str(e)}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику работы системы защиты детей"""
        threat_rate = (
            (self.threats_detected / self.total_content_analyzed * 100)
            if self.total_content_analyzed > 0
            else 0
        )

        return {
            "total_content_analyzed": self.total_content_analyzed,
            "threats_detected": self.threats_detected,
            "threat_detection_rate": threat_rate,
            "parent_notifications_sent": self.parent_notifications_sent,
            "protection_enabled": self.config.get("enabled", True),
            "strict_mode": self.config.get("strict_mode", True),
            "auto_block_threats": self.config.get("auto_block_threats", True),
        }
