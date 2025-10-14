#!/usr/bin/env python3
"""
📱 ALADDIN - VK Messenger Protection Integration
Интеграция для защиты в VK мессенджере

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class VKMessageAnalysis:
    """Результат анализа сообщения VK"""

    message_id: str
    is_suspicious: bool
    threat_type: str
    risk_score: float
    sender_analysis: Dict[str, Any]
    content_analysis: Dict[str, Any]
    timestamp: datetime
    details: Dict[str, Any]


class VKMessengerProtection:
    """
    Система защиты в VK мессенджере.
    Анализирует сообщения, пользователей и группы на предмет угроз.
    """

    def __init__(self, config_path: str = "config/vk_messenger_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = self.setup_logger()

        # Статистика
        self.total_messages_analyzed = 0
        self.suspicious_messages_detected = 0
        self.blocked_users = 0

        # Паттерны угроз в VK
        self.vk_threat_patterns = self.load_vk_threat_patterns()

    def load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию защиты VK мессенджера"""
        try:
            import json

            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем базовую конфигурацию
            default_config = {
                "enabled": True,
                "strict_mode": True,
                "auto_block_suspicious": True,
                "monitor_private_messages": True,
                "monitor_group_messages": True,
                "monitor_comments": True,
                "monitor_wall_posts": True,
                "threat_detection_threshold": 0.7,
                "vk_api_enabled": False,
                "vk_token": "",
                "monitored_groups": [],
                "blacklisted_users": [],
            }
            return default_config

    def setup_logger(self) -> logging.Logger:
        """Настройка логирования"""
        logger = logging.getLogger("vk_messenger_protection")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def load_vk_threat_patterns(self) -> Dict[str, Any]:
        """Загружает паттерны угроз для VK"""
        return {
            "spam": {
                "keywords": [
                    "реклама",
                    "заработок",
                    "криптовалюта",
                    "инвестиции",
                    "быстрые деньги",
                ],
                "threshold": 0.6,
            },
            "phishing": {
                "keywords": [
                    "пароль",
                    "логин",
                    "вход",
                    "аккаунт",
                    "заблокирован",
                    "восстановить",
                ],
                "threshold": 0.8,
            },
            "scam": {
                "keywords": [
                    "бесплатно",
                    "подарок",
                    "выигрыш",
                    "приз",
                    "бонус",
                    "скидка",
                ],
                "threshold": 0.7,
            },
            "fake_news": {
                "keywords": [
                    "срочно",
                    "внимание",
                    "важно",
                    "секретно",
                    "только для вас",
                ],
                "threshold": 0.5,
            },
            "cyberbullying": {
                "keywords": [
                    "убить",
                    "умри",
                    "ненавижу",
                    "гей",
                    "транс",
                    "инвалид",
                ],
                "threshold": 0.8,
            },
            "extremism": {
                "keywords": [
                    "война",
                    "террор",
                    "взрыв",
                    "бомба",
                    "оружие",
                    "насилие",
                ],
                "threshold": 0.9,
            },
        }

    def analyze_vk_message(
        self, message_data: Dict[str, Any]
    ) -> VKMessageAnalysis:
        """
        Анализирует сообщение VK на предмет угроз.

        Args:
            message_data: Данные сообщения

        Returns:
            VKMessageAnalysis: Результат анализа
        """
        self.logger.info(
            f"Анализ сообщения VK: {message_data.get('id', 'unknown')}"
        )

        message_id = message_data.get(
            "id", f"msg_{datetime.now().timestamp()}"
        )
        is_suspicious = False
        threat_type = "none"
        risk_score = 0.0

        # Анализ отправителя
        sender_analysis = self.analyze_vk_sender(
            message_data.get("sender", {})
        )

        # Анализ содержимого
        content_analysis = self.analyze_vk_content(
            message_data.get("content", "")
        )

        # Анализ типа сообщения
        message_type = message_data.get("type", "text")
        if message_type in ["photo", "video", "audio", "document"]:
            media_analysis = self.analyze_vk_media(
                message_data.get("media", {})
            )
            content_analysis.update(media_analysis)

        # Расчет общего риска
        risk_score = (
            sender_analysis.get("risk_score", 0) * 0.4
            + content_analysis.get("risk_score", 0) * 0.6
        )

        # Определение типа угрозы
        if risk_score >= self.config.get("threat_detection_threshold", 0.7):
            is_suspicious = True
            threat_type = content_analysis.get(
                "threat_type", "suspicious_content"
            )

        # Обновление статистики
        self.total_messages_analyzed += 1
        if is_suspicious:
            self.suspicious_messages_detected += 1

        analysis = VKMessageAnalysis(
            message_id=message_id,
            is_suspicious=is_suspicious,
            threat_type=threat_type,
            risk_score=risk_score,
            sender_analysis=sender_analysis,
            content_analysis=content_analysis,
            timestamp=datetime.now(),
            details=message_data,
        )

        self.logger.info(
            f"VK message analysis: {message_id}, "
            f"suspicious={is_suspicious}, threat={threat_type}, "
            f"risk={risk_score:.2f}"
        )
        return analysis

    def analyze_vk_sender(self, sender_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует отправителя сообщения VK"""
        user_id = sender_data.get("id", "unknown")
        is_verified = sender_data.get("verified", False)
        is_bot = sender_data.get("is_bot", False)
        registration_date = sender_data.get("registration_date")
        friends_count = sender_data.get("friends_count", 0)
        subscribers_count = sender_data.get("subscribers_count", 0)

        risk_score = 0.0
        suspicious_indicators = []

        # Проверка на бота
        if is_bot:
            risk_score += 0.3
            suspicious_indicators.append("bot_account")

        # Проверка на верификацию
        if not is_verified and subscribers_count > 1000:
            risk_score += 0.2
            suspicious_indicators.append("unverified_large_account")

        # Проверка на новый аккаунт
        if registration_date:
            reg_date = (
                datetime.fromisoformat(registration_date)
                if isinstance(registration_date, str)
                else registration_date
            )
            days_since_registration = (datetime.now() - reg_date).days
            if days_since_registration < 30:
                risk_score += 0.2
                suspicious_indicators.append("new_account")

        # Проверка на подозрительное количество друзей
        if friends_count > 5000:  # Слишком много друзей
            risk_score += 0.1
            suspicious_indicators.append("too_many_friends")
        elif friends_count < 10:  # Слишком мало друзей
            risk_score += 0.1
            suspicious_indicators.append("too_few_friends")

        return {
            "user_id": user_id,
            "risk_score": risk_score,
            "suspicious_indicators": suspicious_indicators,
            "is_verified": is_verified,
            "is_bot": is_bot,
            "friends_count": friends_count,
            "subscribers_count": subscribers_count,
        }

    def analyze_vk_content(self, content: str) -> Dict[str, Any]:
        """Анализирует содержимое сообщения VK"""
        content_lower = content.lower()
        risk_score = 0.0
        threat_type = "none"
        detected_patterns = []

        # Проверка паттернов угроз
        for pattern_name, pattern_data in self.vk_threat_patterns.items():
            pattern_matches = 0
            for keyword in pattern_data["keywords"]:
                if keyword.lower() in content_lower:
                    pattern_matches += 1

            if pattern_matches > 0:
                pattern_risk = (
                    pattern_matches / len(pattern_data["keywords"])
                ) * pattern_data["threshold"]
                risk_score += pattern_risk
                detected_patterns.append(pattern_name)

                if (
                    pattern_risk > risk_score
                    and pattern_risk > pattern_data["threshold"]
                ):
                    threat_type = pattern_name

        # Проверка на спам (повторяющиеся символы)
        if self.is_spam_content(content):
            risk_score += 0.4
            detected_patterns.append("spam_format")
            if threat_type == "none":
                threat_type = "spam"

        # Проверка на ссылки
        links = self.extract_links(content)
        if links:
            link_analysis = self.analyze_vk_links(links)
            risk_score += link_analysis.get("risk_score", 0)
            if link_analysis.get("is_suspicious"):
                detected_patterns.append("suspicious_links")

        return {
            "risk_score": risk_score,
            "threat_type": threat_type,
            "detected_patterns": detected_patterns,
            "content_length": len(content),
            "links_found": len(links),
        }

    def analyze_vk_media(self, media_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует медиа контент в VK"""
        media_type = media_data.get("type", "unknown")
        risk_score = 0.0
        suspicious_indicators = []

        # Проверка размера файла
        file_size = media_data.get("size", 0)
        if file_size > 100 * 1024 * 1024:  # Больше 100MB
            risk_score += 0.2
            suspicious_indicators.append("large_file")

        # Проверка типа файла
        file_extension = media_data.get("extension", "")
        suspicious_extensions = [".exe", ".bat", ".cmd", ".scr", ".pif"]
        if file_extension.lower() in suspicious_extensions:
            risk_score += 0.5
            suspicious_indicators.append("suspicious_file_type")

        # Проверка метаданных
        metadata = media_data.get("metadata", {})
        if not metadata:
            risk_score += 0.1
            suspicious_indicators.append("missing_metadata")

        return {
            "media_type": media_type,
            "risk_score": risk_score,
            "suspicious_indicators": suspicious_indicators,
            "file_size": file_size,
            "file_extension": file_extension,
        }

    def is_spam_content(self, content: str) -> bool:
        """Проверяет, является ли контент спамом"""
        # Проверка на повторяющиеся символы
        if len(set(content)) < len(content) * 0.3:
            return True

        # Проверка на CAPS LOCK
        if len([c for c in content if c.isupper()]) > len(content) * 0.7:
            return True

        # Проверка на повторяющиеся слова
        words = content.split()
        if len(words) > 10:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            max_repetition = max(word_counts.values())
            if max_repetition > len(words) * 0.3:
                return True

        return False

    def extract_links(self, content: str) -> List[str]:
        """Извлекает ссылки из контента"""
        import re

        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        return re.findall(url_pattern, content)

    def analyze_vk_links(self, links: List[str]) -> Dict[str, Any]:
        """Анализирует ссылки в VK сообщениях"""
        risk_score = 0.0
        suspicious_links = []

        suspicious_domains = [
            "bit.ly",
            "tinyurl.com",
            "goo.gl",
            "t.co",
            "vk.cc",
            "vk.me",
            "vk.com/away",
        ]

        for link in links:
            domain = self.extract_domain(link)
            if domain in suspicious_domains:
                risk_score += 0.3
                suspicious_links.append(link)

            # Проверка на фишинговые домены
            if self.is_phishing_domain(domain):
                risk_score += 0.5
                suspicious_links.append(link)

        return {
            "risk_score": risk_score,
            "suspicious_links": suspicious_links,
            "is_suspicious": risk_score > 0.3,
        }

    def extract_domain(self, url: str) -> str:
        """Извлекает домен из URL"""
        import re

        domain_pattern = r"https?://([^/]+)"
        match = re.search(domain_pattern, url)
        return match.group(1) if match else ""

    def is_phishing_domain(self, domain: str) -> bool:
        """Проверяет, является ли домен фишинговым"""
        # В реальной системе здесь был бы запрос к базе данных фишинговых доменов
        phishing_domains = [
            "vk-security.com",
            "vk-login.net",
            "vkontakte-secure.org",
        ]
        return domain in phishing_domains

    async def monitor_vk_group(
        self, group_id: str, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Мониторит группу VK на предмет подозрительной активности.

        Args:
            group_id: ID группы VK
            messages: Список сообщений группы

        Returns:
            Dict[str, Any]: Результат мониторинга
        """
        self.logger.info(f"Мониторинг группы VK: {group_id}")

        suspicious_messages = []
        total_risk_score = 0.0

        for message in messages:
            analysis = self.analyze_vk_message(message)
            if analysis.is_suspicious:
                suspicious_messages.append(analysis)
                total_risk_score += analysis.risk_score

        group_risk_score = (
            total_risk_score / len(messages) if messages else 0.0
        )
        is_suspicious = group_risk_score > self.config.get(
            "threat_detection_threshold", 0.7
        )

        result = {
            "group_id": group_id,
            "is_suspicious": is_suspicious,
            "risk_score": group_risk_score,
            "suspicious_messages_count": len(suspicious_messages),
            "total_messages": len(messages),
            "suspicious_messages": suspicious_messages,
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info(
            f"VK group monitoring: {group_id}, suspicious={is_suspicious}, risk={group_risk_score:.2f}"
        )
        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику защиты VK мессенджера"""
        detection_rate = (
            (
                self.suspicious_messages_detected
                / self.total_messages_analyzed
                * 100
            )
            if self.total_messages_analyzed > 0
            else 0.0
        )

        return {
            "total_messages_analyzed": self.total_messages_analyzed,
            "suspicious_messages_detected": self.suspicious_messages_detected,
            "blocked_users": self.blocked_users,
            "detection_rate": detection_rate,
            "enabled": self.config.get("enabled", True),
            "threat_patterns_count": len(self.vk_threat_patterns),
            "monitored_groups": len(self.config.get("monitored_groups", [])),
        }
