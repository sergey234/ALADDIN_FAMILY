# -*- coding: utf-8 -*-
"""
ALADDIN Security System - MAX Messenger Protection
Защита в MAX мессенджере

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List


@dataclass
class MAXMessageAnalysis:
    """Результат анализа сообщения MAX"""

    is_safe: bool
    message_type: str
    threat_level: str
    confidence: float
    suspicious_indicators: List[str]
    timestamp: datetime
    recommended_action: str
    details: Dict[str, Any]


class MAXMessengerProtection:
    """Система защиты в MAX мессенджере"""

    def __init__(
        self, config_path: str = "config/max_messenger_protection_config.json"
    ):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = self.setup_logger()

        # Статистика
        self.total_messages_analyzed = 0
        self.threats_detected = 0
        self.blocked_messages = 0

        # Паттерны угроз в MAX
        self.max_threat_patterns = self.load_max_threat_patterns()

    def load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию защиты MAX"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем базовую конфигурацию
            default_config = {
                "enabled": True,
                "strict_mode": True,
                "auto_block_threats": True,
                "monitor_government_bots": True,
                "monitor_fake_accounts": True,
                "monitor_spam": True,
                "monitor_phishing": True,
                "threat_detection_threshold": 0.7,
            }

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

            return default_config

    def load_max_threat_patterns(self) -> Dict[str, Any]:
        """Загружает паттерны угроз в MAX"""
        return {
            "fake_government_bots": [
                "официальный бот",
                "государственный сервис",
                "правительственный бот",
                "бот госуслуг",
                "официальная информация",
                "государственные услуги",
            ],
            "phishing_attempts": [
                "перейдите по ссылке",
                "подтвердите данные",
                "обновите информацию",
                "проверьте аккаунт",
                "безопасность вашего аккаунта",
                "подозрительная активность",
            ],
            "spam_patterns": [
                "быстрые деньги",
                "заработок дома",
                "инвестиции",
                "криптовалюта",
                "многоуровневый маркетинг",
                "пирамида",
            ],
            "fake_news": [
                "эксклюзивная информация",
                "секретные данные",
                "инсайдерская информация",
                "фейковые новости",
                "дезинформация",
            ],
            "social_engineering": [
                "срочно нужно",
                "не говори никому",
                "конфиденциально",
                "только для вас",
                "ограниченное предложение",
            ],
        }

    def setup_logger(self) -> logging.Logger:
        """Настраивает логгер"""
        logger = logging.getLogger("max_messenger_protection")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler("logs/max_messenger_protection.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def monitor_max_messenger(
        self, message_data: Dict[str, Any]
    ) -> MAXMessageAnalysis:
        """
        Мониторинг сообщений в MAX мессенджере
        """
        try:
            self.total_messages_analyzed += 1

            # Извлечение данных сообщения
            message_text = message_data.get("text", "").lower()
            sender_id = message_data.get("sender_id", "")
            sender_type = message_data.get("sender_type", "user")
            message_type = message_data.get("message_type", "text")
            timestamp = message_data.get("timestamp", datetime.now())

            # Анализ сообщения
            analysis_result = self._analyze_message_content(
                message_text, sender_type, message_type
            )

            # Определение типа сообщения
            detected_message_type = self._classify_message_type(
                message_text, sender_type
            )

            # Оценка уровня угрозы
            threat_level = self._assess_threat_level(
                analysis_result, sender_type
            )

            # Расчет уверенности
            confidence = self._calculate_confidence(
                analysis_result, threat_level
            )

            # Определение безопасности
            is_safe = confidence < self.config.get(
                "threat_detection_threshold", 0.7
            )

            # Рекомендуемые действия
            recommended_action = self._get_recommended_action(
                is_safe, threat_level, analysis_result
            )

            # Обновление статистики
            if not is_safe:
                self.threats_detected += 1

            if recommended_action == "block":
                self.blocked_messages += 1

            result = MAXMessageAnalysis(
                is_safe=is_safe,
                message_type=detected_message_type,
                threat_level=threat_level,
                confidence=confidence,
                suspicious_indicators=analysis_result.get("indicators", []),
                timestamp=timestamp,
                recommended_action=recommended_action,
                details={
                    "sender_id": sender_id,
                    "sender_type": sender_type,
                    "message_type": message_type,
                    "analysis_result": analysis_result,
                    "analysis_method": "max_messenger_protection",
                },
            )

            self.logger.info(
                f"MAX message analysis: safe={is_safe}, type={detected_message_type}, threat={threat_level}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error monitoring MAX messenger: {str(e)}")
            return MAXMessageAnalysis(
                is_safe=False,
                message_type="unknown",
                threat_level="error",
                confidence=0.0,
                suspicious_indicators=["Analysis error"],
                timestamp=datetime.now(),
                recommended_action="retry_analysis",
                details={"error": str(e)},
            )

    def _analyze_message_content(
        self, message_text: str, sender_type: str, message_type: str
    ) -> Dict[str, Any]:
        """Анализ содержимого сообщения"""
        analysis_result = {"indicators": [], "scores": {}, "total_score": 0.0}

        # Анализ фейковых государственных ботов
        fake_bot_score = self._check_fake_government_bots(message_text)
        if fake_bot_score > 0.5:
            analysis_result["indicators"].append(
                f"Fake government bot (score: {fake_bot_score:.2f})"
            )
            analysis_result["scores"]["fake_bot"] = fake_bot_score

        # Анализ фишинга
        phishing_score = self._check_phishing_attempts(message_text)
        if phishing_score > 0.5:
            analysis_result["indicators"].append(
                f"Phishing attempt (score: {phishing_score:.2f})"
            )
            analysis_result["scores"]["phishing"] = phishing_score

        # Анализ спама
        spam_score = self._check_spam_patterns(message_text)
        if spam_score > 0.5:
            analysis_result["indicators"].append(
                f"Spam content (score: {spam_score:.2f})"
            )
            analysis_result["scores"]["spam"] = spam_score

        # Анализ фейковых новостей
        fake_news_score = self._check_fake_news(message_text)
        if fake_news_score > 0.5:
            analysis_result["indicators"].append(
                f"Fake news (score: {fake_news_score:.2f})"
            )
            analysis_result["scores"]["fake_news"] = fake_news_score

        # Анализ социальной инженерии
        social_engineering_score = self._check_social_engineering(message_text)
        if social_engineering_score > 0.5:
            analysis_result["indicators"].append(
                f"Social engineering (score: {social_engineering_score:.2f})"
            )
            analysis_result["scores"][
                "social_engineering"
            ] = social_engineering_score

        # Расчет общего счета
        analysis_result["total_score"] = (
            max(analysis_result["scores"].values())
            if analysis_result["scores"]
            else 0.0
        )

        return analysis_result

    def _check_fake_government_bots(self, message_text: str) -> float:
        """Проверка на фейковые государственные боты"""
        patterns = self.max_threat_patterns["fake_government_bots"]
        matches = sum(1 for pattern in patterns if pattern in message_text)
        return matches / len(patterns) if patterns else 0.0

    def _check_phishing_attempts(self, message_text: str) -> float:
        """Проверка на фишинг"""
        patterns = self.max_threat_patterns["phishing_attempts"]
        matches = sum(1 for pattern in patterns if pattern in message_text)
        return matches / len(patterns) if patterns else 0.0

    def _check_spam_patterns(self, message_text: str) -> float:
        """Проверка на спам"""
        patterns = self.max_threat_patterns["spam_patterns"]
        matches = sum(1 for pattern in patterns if pattern in message_text)
        return matches / len(patterns) if patterns else 0.0

    def _check_fake_news(self, message_text: str) -> float:
        """Проверка на фейковые новости"""
        patterns = self.max_threat_patterns["fake_news"]
        matches = sum(1 for pattern in patterns if pattern in message_text)
        return matches / len(patterns) if patterns else 0.0

    def _check_social_engineering(self, message_text: str) -> float:
        """Проверка на социальную инженерию"""
        patterns = self.max_threat_patterns["social_engineering"]
        matches = sum(1 for pattern in patterns if pattern in message_text)
        return matches / len(patterns) if patterns else 0.0

    def _classify_message_type(
        self, message_text: str, sender_type: str
    ) -> str:
        """Классификация типа сообщения"""
        if sender_type == "bot":
            if any(
                pattern in message_text
                for pattern in self.max_threat_patterns["fake_government_bots"]
            ):
                return "fake_government_bot"
            else:
                return "legitimate_bot"
        elif any(
            pattern in message_text
            for pattern in self.max_threat_patterns["phishing_attempts"]
        ):
            return "phishing"
        elif any(
            pattern in message_text
            for pattern in self.max_threat_patterns["spam_patterns"]
        ):
            return "spam"
        elif any(
            pattern in message_text
            for pattern in self.max_threat_patterns["fake_news"]
        ):
            return "fake_news"
        else:
            return "normal_message"

    def _assess_threat_level(
        self, analysis_result: Dict[str, Any], sender_type: str
    ) -> str:
        """Оценка уровня угрозы"""
        total_score = analysis_result.get("total_score", 0.0)

        # Бонус за ботов
        if sender_type == "bot":
            total_score += 0.2

        if total_score >= 0.8:
            return "critical"
        elif total_score >= 0.6:
            return "high"
        elif total_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _calculate_confidence(
        self, analysis_result: Dict[str, Any], threat_level: str
    ) -> float:
        """Расчет уверенности"""
        base_confidence = analysis_result.get("total_score", 0.0)

        # Модификаторы уверенности
        if threat_level == "critical":
            return min(base_confidence + 0.2, 1.0)
        elif threat_level == "high":
            return min(base_confidence + 0.1, 1.0)
        else:
            return base_confidence

    def _get_recommended_action(
        self, is_safe: bool, threat_level: str, analysis_result: Dict[str, Any]
    ) -> str:
        """Получение рекомендуемого действия"""
        if not is_safe:
            if threat_level == "critical":
                return "block"
            elif threat_level == "high":
                return "warn_and_monitor"
            else:
                return "monitor"
        else:
            return "allow"

    def detect_fake_government_bots(
        self, bot_messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Детекция фейковых государственных ботов
        """
        try:
            fake_bots = []
            legitimate_bots = []

            for message_data in bot_messages:
                analysis = self.monitor_max_messenger(message_data)

                if analysis.message_type == "fake_government_bot":
                    fake_bots.append(
                        {"message_data": message_data, "analysis": analysis}
                    )
                else:
                    legitimate_bots.append(
                        {"message_data": message_data, "analysis": analysis}
                    )

            result = {
                "fake_bots_count": len(fake_bots),
                "legitimate_bots_count": len(legitimate_bots),
                "total_bots_analyzed": len(bot_messages),
                "fake_bots": fake_bots,
                "legitimate_bots": legitimate_bots,
                "timestamp": datetime.now().isoformat(),
            }

            self.logger.info(
                f"Fake government bots detection: {len(fake_bots)} fake, {len(legitimate_bots)} legitimate"
            )

            return result

        except Exception as e:
            self.logger.error(
                f"Error detecting fake government bots: {str(e)}"
            )
            return {"error": str(e)}

    def secure_max_communication(
        self, communication_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обеспечение безопасности коммуникации в MAX
        """
        try:
            participants = communication_data.get("participants", [])
            messages = communication_data.get("messages", [])

            # Анализ участников
            participant_analysis = self._analyze_participants(participants)

            # Анализ сообщений
            message_analysis = []
            for message in messages:
                analysis = self.monitor_max_messenger(message)
                message_analysis.append(analysis)

            # Оценка безопасности коммуникации
            security_score = self._calculate_communication_security(
                participant_analysis, message_analysis
            )

            # Рекомендации по безопасности
            security_recommendations = self._get_security_recommendations(
                security_score, participant_analysis, message_analysis
            )

            result = {
                "security_score": security_score,
                "participant_analysis": participant_analysis,
                "message_analysis": message_analysis,
                "security_recommendations": security_recommendations,
                "timestamp": datetime.now().isoformat(),
            }

            self.logger.info(
                f"MAX communication security: score={security_score:.2f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error securing MAX communication: {str(e)}")
            return {"error": str(e)}

    def _analyze_participants(
        self, participants: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Анализ участников коммуникации"""
        analysis = {
            "total_participants": len(participants),
            "bot_count": 0,
            "user_count": 0,
            "suspicious_participants": 0,
            "participant_details": [],
        }

        for participant in participants:
            participant_type = participant.get("type", "user")
            if participant_type == "bot":
                analysis["bot_count"] += 1
            else:
                analysis["user_count"] += 1

            # Проверка на подозрительность
            if self._is_suspicious_participant(participant):
                analysis["suspicious_participants"] += 1

            analysis["participant_details"].append(
                {
                    "id": participant.get("id"),
                    "type": participant_type,
                    "suspicious": self._is_suspicious_participant(participant),
                }
            )

        return analysis

    def _is_suspicious_participant(self, participant: Dict[str, Any]) -> bool:
        """Проверка на подозрительного участника"""
        # Простая логика проверки
        join_date = participant.get("join_date")
        if join_date and join_date > datetime.now() - timedelta(days=1):
            return True  # Недавно созданный аккаунт

        if not participant.get("profile_photo"):
            return True  # Нет фото профиля

        return False

    def _calculate_communication_security(
        self,
        participant_analysis: Dict[str, Any],
        message_analysis: List[MAXMessageAnalysis],
    ) -> float:
        """Расчет безопасности коммуникации"""
        security_score = 1.0

        # Штрафы за подозрительных участников
        suspicious_ratio = (
            participant_analysis["suspicious_participants"]
            / participant_analysis["total_participants"]
        )
        security_score -= suspicious_ratio * 0.5

        # Штрафы за небезопасные сообщения
        unsafe_messages = sum(
            1 for analysis in message_analysis if not analysis.is_safe
        )
        if message_analysis:
            unsafe_ratio = unsafe_messages / len(message_analysis)
            security_score -= unsafe_ratio * 0.3

        return max(security_score, 0.0)

    def _get_security_recommendations(
        self,
        security_score: float,
        participant_analysis: Dict[str, Any],
        message_analysis: List[MAXMessageAnalysis],
    ) -> List[str]:
        """Получение рекомендаций по безопасности"""
        recommendations = []

        if security_score < 0.5:
            recommendations.append("Критически низкий уровень безопасности")
            recommendations.append("Рекомендуется прекратить коммуникацию")
        elif security_score < 0.7:
            recommendations.append("Низкий уровень безопасности")
            recommendations.append("Рекомендуется усилить мониторинг")
        else:
            recommendations.append("Уровень безопасности приемлемый")

        if participant_analysis["suspicious_participants"] > 0:
            recommendations.append("Обнаружены подозрительные участники")

        unsafe_messages = sum(
            1 for analysis in message_analysis if not analysis.is_safe
        )
        if unsafe_messages > 0:
            recommendations.append(
                f"Обнаружено {unsafe_messages} небезопасных сообщений"
            )

        return recommendations

    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику работы"""
        threat_rate = (
            (self.threats_detected / self.total_messages_analyzed * 100)
            if self.total_messages_analyzed > 0
            else 0
        )

        return {
            "total_messages_analyzed": self.total_messages_analyzed,
            "threats_detected": self.threats_detected,
            "threat_detection_rate": threat_rate,
            "blocked_messages": self.blocked_messages,
            "protection_enabled": self.config.get("enabled", True),
            "monitor_government_bots": self.config.get(
                "monitor_government_bots", True
            ),
            "threat_detection_threshold": self.config.get(
                "threat_detection_threshold", 0.7
            ),
        }
