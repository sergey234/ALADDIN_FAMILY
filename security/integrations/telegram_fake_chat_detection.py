# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Telegram Fake Chat Detection
Детекция фейковых рабочих чатов в Telegram

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
class TelegramChatAnalysis:
    """Результат анализа Telegram чата"""

    is_fake: bool
    confidence: float
    chat_type: str
    risk_level: str
    suspicious_indicators: List[str]
    timestamp: datetime
    recommended_action: str
    details: Dict[str, Any]


class TelegramFakeChatDetection:
    """Система детекции фейковых чатов в Telegram"""

    def __init__(
        self, config_path: str = "config/telegram_detection_config.json"
    ):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = self.setup_logger()

        # Статистика
        self.total_chats_analyzed = 0
        self.fake_chats_detected = 0
        self.blocked_chats = 0

        # Паттерны фейковых чатов
        self.fake_chat_patterns = self.load_fake_chat_patterns()

    def load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию детекции Telegram"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем базовую конфигурацию
            default_config = {
                "enabled": True,
                "strict_mode": True,
                "auto_block_fake_chats": True,
                "detection_threshold": 0.7,
                "analyze_group_chats": True,
                "analyze_private_chats": True,
                "check_admin_verification": True,
                "monitor_message_patterns": True,
            }

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

            return default_config

    def load_fake_chat_patterns(self) -> Dict[str, Any]:
        """Загружает паттерны фейковых чатов"""
        return {
            "fake_work_chat_indicators": [
                "рабочий чат",
                "коллектив",
                "сотрудники",
                "начальство",
                "работа",
                "офис",
            ],
            "fake_school_indicators": [
                "школьный чат",
                "родители",
                "учителя",
                "класс",
                "школа",
                "директор",
            ],
            "fake_housing_indicators": [
                "жилой комплекс",
                "ЖК",
                "соседи",
                "управляющая",
                "дом",
                "квартира",
            ],
            "fake_kindergarten_indicators": [
                "детский сад",
                "воспитатели",
                "группа",
                "детки",
                "садик",
            ],
            "suspicious_admin_messages": [
                "обновление данных",
                "проверка документов",
                "подтверждение личности",
                "безопасный счет",
                "перевод денег",
                "срочно нужно",
                "не говори никому",
            ],
            "gosuslugi_phishing": [
                "госуслуги",
                "личный кабинет",
                "подтверждение",
                "документы",
                "паспорт",
                "СНИЛС",
                "ИНН",
            ],
        }

    def setup_logger(self) -> logging.Logger:
        """Настраивает логгер"""
        logger = logging.getLogger("telegram_fake_chat_detection")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler("logs/telegram_fake_chat_detection.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def analyze_telegram_chat(
        self, chat_data: Dict[str, Any]
    ) -> TelegramChatAnalysis:
        """
        Анализирует Telegram чат на предмет фейковости
        """
        try:
            self.total_chats_analyzed += 1

            # Извлечение данных чата
            chat_title = chat_data.get("title", "").lower()
            chat_description = chat_data.get("description", "").lower()
            admin_count = chat_data.get("admin_count", 0)
            member_count = chat_data.get("member_count", 0)
            recent_messages = chat_data.get("recent_messages", [])

            # Анализ подозрительных индикаторов
            suspicious_indicators = []
            total_score = 0.0

            # 1. Анализ названия и описания чата
            title_score = self._analyze_chat_title(
                chat_title, chat_description
            )
            if title_score > 0.5:
                suspicious_indicators.append(
                    f"Suspicious title/description (score: {title_score:.2f})"
                )
                total_score += title_score * 0.3

            # 2. Анализ структуры чата
            structure_score = self._analyze_chat_structure(
                admin_count, member_count
            )
            if structure_score > 0.5:
                suspicious_indicators.append(
                    f"Suspicious chat structure (score: {structure_score:.2f})"
                )
                total_score += structure_score * 0.2

            # 3. Анализ сообщений
            messages_score = self._analyze_recent_messages(recent_messages)
            if messages_score > 0.5:
                suspicious_indicators.append(
                    f"Suspicious messages (score: {messages_score:.2f})"
                )
                total_score += messages_score * 0.4

            # 4. Анализ администраторов
            admin_score = self._analyze_admin_behavior(chat_data)
            if admin_score > 0.5:
                suspicious_indicators.append(
                    f"Suspicious admin behavior (score: {admin_score:.2f})"
                )
                total_score += admin_score * 0.1

            # Определение типа чата
            chat_type = self._determine_chat_type(chat_title, chat_description)

            # Определение риска
            risk_level = self._determine_risk_level(total_score)

            # Определение фейковости
            is_fake = total_score >= self.config.get(
                "detection_threshold", 0.7
            )

            # Рекомендуемые действия
            recommended_action = self._get_recommended_action(
                total_score, is_fake
            )

            # Обновление статистики
            if is_fake:
                self.fake_chats_detected += 1

            result = TelegramChatAnalysis(
                is_fake=is_fake,
                confidence=total_score,
                chat_type=chat_type,
                risk_level=risk_level,
                suspicious_indicators=suspicious_indicators,
                timestamp=datetime.now(),
                recommended_action=recommended_action,
                details={
                    "title_score": title_score,
                    "structure_score": structure_score,
                    "messages_score": messages_score,
                    "admin_score": admin_score,
                    "total_score": total_score,
                    "chat_data": chat_data,
                },
            )

            self.logger.info(
                f"Chat analyzed: fake={is_fake}, type={chat_type}, confidence={total_score:.2f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error analyzing chat: {str(e)}")
            return TelegramChatAnalysis(
                is_fake=False,
                confidence=0.0,
                chat_type="unknown",
                risk_level="error",
                suspicious_indicators=["Analysis error"],
                timestamp=datetime.now(),
                recommended_action="retry_analysis",
                details={"error": str(e)},
            )

    def _analyze_chat_title(self, title: str, description: str) -> float:
        """Анализ названия и описания чата"""
        score = 0.0

        # Проверка на типичные названия фейковых чатов
        fake_patterns = (
            self.fake_chat_patterns["fake_work_chat_indicators"]
            + self.fake_chat_patterns["fake_school_indicators"]
            + self.fake_chat_patterns["fake_housing_indicators"]
            + self.fake_chat_patterns["fake_kindergarten_indicators"]
        )

        text_to_analyze = f"{title} {description}".lower()

        # Подсчет совпадений
        matches = sum(
            1 for pattern in fake_patterns if pattern in text_to_analyze
        )
        score = matches / len(fake_patterns) if fake_patterns else 0.0

        return min(score, 1.0)

    def _analyze_chat_structure(
        self, admin_count: int, member_count: int
    ) -> float:
        """Анализ структуры чата"""
        score = 0.0

        # Подозрительные соотношения
        if admin_count == 0:
            score += 0.3  # Нет администраторов
        elif admin_count > member_count * 0.1:
            score += 0.2  # Слишком много администраторов

        if member_count < 5:
            score += 0.4  # Слишком мало участников
        elif member_count > 1000:
            score += 0.2  # Слишком много участников

        return min(score, 1.0)

    def _analyze_recent_messages(
        self, messages: List[Dict[str, Any]]
    ) -> float:
        """Анализ последних сообщений"""
        score = 0.0

        if not messages:
            return 0.0

        # Анализ сообщений администраторов
        admin_messages = [
            msg for msg in messages if msg.get("is_admin", False)
        ]

        if admin_messages:
            suspicious_patterns = (
                self.fake_chat_patterns["suspicious_admin_messages"]
                + self.fake_chat_patterns["gosuslugi_phishing"]
            )

            for message in admin_messages:
                message_text = message.get("text", "").lower()

                # Проверка на подозрительные паттерны
                for pattern in suspicious_patterns:
                    if pattern in message_text:
                        score += 0.3
                        break

        return min(score, 1.0)

    def _analyze_admin_behavior(self, chat_data: Dict[str, Any]) -> float:
        """Анализ поведения администраторов"""
        score = 0.0

        admins = chat_data.get("admins", [])

        for admin in admins:
            # Проверка на подозрительные характеристики
            if admin.get("is_bot", False):
                score += 0.2

            if admin.get("join_date") and admin.get(
                "join_date"
            ) > datetime.now() - timedelta(days=1):
                score += 0.3  # Недавно созданный аккаунт

            if not admin.get("profile_photo", False):
                score += 0.1  # Нет фото профиля

        return min(score, 1.0)

    def _determine_chat_type(self, title: str, description: str) -> str:
        """Определение типа чата"""
        text = f"{title} {description}".lower()

        if any(
            pattern in text
            for pattern in self.fake_chat_patterns["fake_work_chat_indicators"]
        ):
            return "work_chat"
        elif any(
            pattern in text
            for pattern in self.fake_chat_patterns["fake_school_indicators"]
        ):
            return "school_chat"
        elif any(
            pattern in text
            for pattern in self.fake_chat_patterns["fake_housing_indicators"]
        ):
            return "housing_chat"
        elif any(
            pattern in text
            for pattern in self.fake_chat_patterns[
                "fake_kindergarten_indicators"
            ]
        ):
            return "kindergarten_chat"
        else:
            return "unknown"

    def _determine_risk_level(self, score: float) -> str:
        """Определение уровня риска"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"

    def _get_recommended_action(self, score: float, is_fake: bool) -> str:
        """Получение рекомендуемого действия"""
        if is_fake:
            if score >= 0.8:
                return "block_and_report"
            else:
                return "warn_and_monitor"
        else:
            return "allow"

    async def detect_fake_work_groups(
        self, group_chats: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Детекция фейковых рабочих групп
        """
        try:
            fake_groups = []
            suspicious_groups = []

            for chat_data in group_chats:
                analysis = self.analyze_telegram_chat(chat_data)

                if analysis.is_fake:
                    fake_groups.append(
                        {"chat_data": chat_data, "analysis": analysis}
                    )
                elif analysis.risk_level in ["high", "medium"]:
                    suspicious_groups.append(
                        {"chat_data": chat_data, "analysis": analysis}
                    )

            result = {
                "fake_groups_count": len(fake_groups),
                "suspicious_groups_count": len(suspicious_groups),
                "total_groups_analyzed": len(group_chats),
                "fake_groups": fake_groups,
                "suspicious_groups": suspicious_groups,
                "timestamp": datetime.now().isoformat(),
            }

            self.logger.info(
                f"Fake groups detection: {len(fake_groups)} fake, {len(suspicious_groups)} suspicious"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error detecting fake work groups: {str(e)}")
            return {"error": str(e)}

    def verify_chat_authenticity(
        self, chat_id: str, verification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Верификация подлинности чата
        """
        try:
            # Проверка различных аспектов подлинности
            verification_score = 0.0
            verification_details = {}

            # 1. Проверка администраторов
            admin_verification = self._verify_admins(
                verification_data.get("admins", [])
            )
            verification_score += admin_verification["score"] * 0.3
            verification_details["admin_verification"] = admin_verification

            # 2. Проверка истории чата
            history_verification = self._verify_chat_history(
                verification_data.get("history", [])
            )
            verification_score += history_verification["score"] * 0.3
            verification_details["history_verification"] = history_verification

            # 3. Проверка участников
            member_verification = self._verify_members(
                verification_data.get("members", [])
            )
            verification_score += member_verification["score"] * 0.2
            verification_details["member_verification"] = member_verification

            # 4. Проверка метаданных
            metadata_verification = self._verify_metadata(
                verification_data.get("metadata", {})
            )
            verification_score += metadata_verification["score"] * 0.2
            verification_details["metadata_verification"] = (
                metadata_verification
            )

            is_authentic = verification_score >= 0.7

            result = {
                "chat_id": chat_id,
                "is_authentic": is_authentic,
                "verification_score": verification_score,
                "verification_details": verification_details,
                "timestamp": datetime.now().isoformat(),
            }

            self.logger.info(
                f"Chat authenticity verification: {chat_id}, authentic={is_authentic}, score={verification_score:.2f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error verifying chat authenticity: {str(e)}")
            return {"error": str(e)}

    def _verify_admins(self, admins: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Верификация администраторов"""
        score = 0.0
        issues = []

        if not admins:
            issues.append("No administrators")
            return {"score": 0.0, "issues": issues}

        for admin in admins:
            if admin.get("is_bot", False):
                issues.append("Bot administrator")
                score -= 0.2

            if not admin.get("profile_photo", False):
                issues.append("Admin without profile photo")
                score -= 0.1

            if admin.get("join_date") and admin.get(
                "join_date"
            ) > datetime.now() - timedelta(days=7):
                issues.append("Recently created admin account")
                score -= 0.3

        return {"score": max(0.0, 1.0 + score), "issues": issues}

    def _verify_chat_history(
        self, history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Верификация истории чата"""
        score = 0.0
        issues = []

        if not history:
            issues.append("No chat history")
            return {"score": 0.0, "issues": issues}

        # Проверка возраста чата
        oldest_message = min(
            history, key=lambda x: x.get("date", datetime.now())
        )
        chat_age = datetime.now() - oldest_message.get("date", datetime.now())

        if chat_age.days < 1:
            issues.append("Very new chat")
            score -= 0.5
        elif chat_age.days < 7:
            issues.append("Recently created chat")
            score -= 0.2

        return {"score": max(0.0, 1.0 + score), "issues": issues}

    def _verify_members(self, members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Верификация участников"""
        score = 0.0
        issues = []

        if len(members) < 3:
            issues.append("Too few members")
            score -= 0.4
        elif len(members) > 500:
            issues.append("Too many members")
            score -= 0.2

        # Проверка активности участников
        active_members = [
            m
            for m in members
            if m.get("last_seen", datetime.now())
            > datetime.now() - timedelta(days=30)
        ]
        if len(active_members) < len(members) * 0.5:
            issues.append("Many inactive members")
            score -= 0.2

        return {"score": max(0.0, 1.0 + score), "issues": issues}

    def _verify_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Верификация метаданных"""
        score = 0.0
        issues = []

        if not metadata.get("description"):
            issues.append("No chat description")
            score -= 0.2

        if not metadata.get("invite_link"):
            issues.append("No invite link")
            score -= 0.1

        return {"score": max(0.0, 1.0 + score), "issues": issues}

    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику работы"""
        fake_rate = (
            (self.fake_chats_detected / self.total_chats_analyzed * 100)
            if self.total_chats_analyzed > 0
            else 0
        )

        return {
            "total_chats_analyzed": self.total_chats_analyzed,
            "fake_chats_detected": self.fake_chats_detected,
            "fake_detection_rate": fake_rate,
            "blocked_chats": self.blocked_chats,
            "detection_enabled": self.config.get("enabled", True),
            "detection_threshold": self.config.get("detection_threshold", 0.7),
        }
