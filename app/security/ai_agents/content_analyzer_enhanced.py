# -*- coding: utf-8 -*-
"""
Анализатор контента для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from security.bots.parental_control_bot import (
    ContentAnalysisRequest,
    ContentAnalysisResult,
    ContentCategory,
    ControlAction
)


@dataclass
class AnalysisStats:
    """Статистика анализа контента"""
    total_analyses: int = 0
    blocks_by_category: Dict[str, int] = None
    blocks_by_age_group: Dict[str, int] = None
    average_risk_score: float = 0.0

    def __post_init__(self):
        if self.blocks_by_category is None:
            self.blocks_by_category = {}
        if self.blocks_by_age_group is None:
            self.blocks_by_age_group = {}


class ContentAnalyzer:
    """Анализатор контента"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.stats = AnalysisStats()
        self._lock = asyncio.Lock()

        # Паттерны для анализа URL
        self.url_patterns = {
            ContentCategory.EDUCATIONAL: [
                r'khanacademy\.org',
                r'coursera\.org',
                r'edx\.org',
                r'udemy\.com',
                r'codecademy\.com',
                r'duolingo\.com',
                r'wikipedia\.org',
                r'\.edu',
                r'\.ac\.'
            ],
            ContentCategory.SOCIAL: [
                r'facebook\.com',
                r'instagram\.com',
                r'twitter\.com',
                r'tiktok\.com',
                r'snapchat\.com',
                r'linkedin\.com',
                r'vk\.com',
                r'telegram\.org'
            ],
            ContentCategory.GAMING: [
                r'steam\.com',
                r'epicgames\.com',
                r'roblox\.com',
                r'minecraft\.net',
                r'fortnite\.com',
                r'game\.com',
                r'gaming'
            ],
            ContentCategory.ENTERTAINMENT: [
                r'youtube\.com',
                r'netflix\.com',
                r'hulu\.com',
                r'disney\.com',
                r'primevideo\.com',
                r'twitch\.tv',
                r'vimeo\.com'
            ],
            ContentCategory.ADULT: [
                r'porn',
                r'adult',
                r'xxx',
                r'sex',
                r'18\+',
                r'nsfw'
            ],
            ContentCategory.NEWS: [
                r'cnn\.com',
                r'bbc\.com',
                r'reuters\.com',
                r'news\.com',
                r'\.news',
                r'breaking'
            ],
            ContentCategory.SHOPPING: [
                r'amazon\.com',
                r'ebay\.com',
                r'shop\.com',
                r'store\.com',
                r'buy\.com',
                r'cart\.com'
            ]
        }

        # Ключевые слова для анализа
        self.keywords = {
            ContentCategory.EDUCATIONAL: [
                'learn', 'education', 'course', 'tutorial', 'study',
                'school', 'university', 'academic', 'knowledge'
            ],
            ContentCategory.SOCIAL: [
                'social', 'friend', 'follow', 'like', 'share',
                'post', 'comment', 'message', 'chat'
            ],
            ContentCategory.GAMING: [
                'game', 'play', 'player', 'level', 'score',
                'gaming', 'quest', 'battle', 'adventure'
            ],
            ContentCategory.ADULT: [
                'adult', 'mature', 'explicit', 'nsfw', '18+',
                'porn', 'sex', 'xxx', 'adult content'
            ]
        }

    async def analyze_content(
        self, url: str, child_id: str, child_age: int = None
    ) -> ContentAnalysisResult:
        """Анализ контента с валидацией данных"""
        try:
            # Валидация входных данных
            request_data = ContentAnalysisRequest(url=url, child_id=child_id)

            async with self._lock:
                # Базовый анализ URL
                category = self._categorize_url(request_data.url)
                risk_score = self._calculate_risk_score(request_data.url, category)
                age_appropriate = self._is_age_appropriate(category, child_age or 10)

                # Определение действия
                action = self._determine_action(category, risk_score, age_appropriate, child_age)

                # Обновление статистики
                self._update_stats(category, action, child_age)

                result = ContentAnalysisResult(
                    url=request_data.url,
                    category=category,
                    risk_score=risk_score,
                    age_appropriate=age_appropriate,
                    action=action,
                    reason=self._get_action_reason(action, category, risk_score),
                    keywords=self._extract_keywords(request_data.url, category)
                )

                self.logger.info(f"Контент проанализирован: {url} -> {action.value}")
                return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа контента: {e}")
            raise

    def _categorize_url(self, url: str) -> ContentCategory:
        """Категоризация URL"""
        url_lower = url.lower()

        for category, patterns in self.url_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return category

        # Если не найдено совпадений, проверяем по ключевым словам
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in url_lower:
                    return category

        return ContentCategory.UNKNOWN

    def _calculate_risk_score(self, url: str, category: ContentCategory) -> float:
        """Расчет оценки риска"""
        base_scores = {
            ContentCategory.EDUCATIONAL: 0.1,
            ContentCategory.NEWS: 0.2,
            ContentCategory.SHOPPING: 0.3,
            ContentCategory.ENTERTAINMENT: 0.4,
            ContentCategory.SOCIAL: 0.6,
            ContentCategory.GAMING: 0.7,
            ContentCategory.ADULT: 0.9,
            ContentCategory.UNKNOWN: 0.5
        }

        base_score = base_scores.get(category, 0.5)

        # Дополнительные факторы риска
        risk_factors = 0.0

        # Проверка на подозрительные домены
        suspicious_domains = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co']
        for domain in suspicious_domains:
            if domain in url.lower():
                risk_factors += 0.2
                break

        # Проверка на длинные URL (возможно, скрытый контент)
        if len(url) > 100:
            risk_factors += 0.1

        # Проверка на множественные поддомены
        if url.count('.') > 3:
            risk_factors += 0.1

        return min(1.0, base_score + risk_factors)

    def _is_age_appropriate(self, category: ContentCategory, child_age: int) -> bool:
        """Проверка соответствия возрасту"""
        age_limits = {
            ContentCategory.EDUCATIONAL: 0,
            ContentCategory.NEWS: 8,
            ContentCategory.SHOPPING: 12,
            ContentCategory.ENTERTAINMENT: 6,
            ContentCategory.SOCIAL: 13,
            ContentCategory.GAMING: 8,
            ContentCategory.ADULT: 18,
            ContentCategory.UNKNOWN: 10
        }

        min_age = age_limits.get(category, 10)
        return child_age >= min_age

    def _determine_action(
        self, category: ContentCategory, risk_score: float,
        age_appropriate: bool, child_age: int = None
    ) -> ControlAction:
        """Определение действия на основе анализа"""

        # Автоматическая блокировка для взрослого контента
        if category == ContentCategory.ADULT:
            return ControlAction.BLOCK

        # Блокировка если не подходит по возрасту
        if not age_appropriate:
            return ControlAction.BLOCK

        # Блокировка при высоком риске
        if risk_score > 0.8:
            return ControlAction.BLOCK

        # Предупреждение при среднем риске
        if risk_score > 0.5:
            return ControlAction.WARN

        # Разрешение при низком риске
        return ControlAction.ALLOW

    def _get_action_reason(
        self, action: ControlAction, category: ContentCategory, risk_score: float
    ) -> str:
        """Получение причины действия"""
        if action == ControlAction.BLOCK:
            if category == ContentCategory.ADULT:
                return "Взрослый контент заблокирован"
            elif risk_score > 0.8:
                return f"Высокий риск (оценка: {risk_score:.2f})"
            else:
                return "Контент не подходит по возрасту"
        elif action == ControlAction.WARN:
            return f"Средний риск (оценка: {risk_score:.2f})"
        else:
            return "Контент безопасен"

    def _extract_keywords(self, url: str, category: ContentCategory) -> List[str]:
        """Извлечение ключевых слов из URL"""
        keywords = []
        url_lower = url.lower()

        # Извлечение из URL
        url_parts = re.split(r'[\/\?\&\=]', url_lower)
        for part in url_parts:
            if len(part) > 3 and part.isalpha():
                keywords.append(part)

        # Добавление ключевых слов категории
        if category in self.keywords:
            keywords.extend(self.keywords[category][:3])

        return keywords[:10]  # Ограничиваем количество

    def _update_stats(self, category: ContentCategory, action: ControlAction, child_age: int = None):
        """Обновление статистики"""
        self.stats.total_analyses += 1

        if action == ControlAction.BLOCK:
            category_name = category.value
            self.stats.blocks_by_category[category_name] = \
                self.stats.blocks_by_category.get(category_name, 0) + 1

            if child_age:
                age_group = self._get_age_group(child_age)
                self.stats.blocks_by_age_group[age_group] = \
                    self.stats.blocks_by_age_group.get(age_group, 0) + 1

    def _get_age_group(self, age: int) -> str:
        """Определение возрастной группы"""
        if age <= 2:
            return "toddler"
        elif age <= 4:
            return "preschool"
        elif age <= 6:
            return "elementary"
        elif age <= 12:
            return "elementary"
        elif age <= 18:
            return "teen"
        else:
            return "adult"

    async def get_stats(self) -> AnalysisStats:
        """Получение статистики анализа"""
        return self.stats

    async def add_custom_pattern(self, category: ContentCategory, pattern: str):
        """Добавление пользовательского паттерна"""
        if category not in self.url_patterns:
            self.url_patterns[category] = []

        self.url_patterns[category].append(pattern)
        self.logger.info(f"Добавлен пользовательский паттерн для {category.value}: {pattern}")

    async def add_custom_keywords(self, category: ContentCategory, keywords: List[str]):
        """Добавление пользовательских ключевых слов"""
        if category not in self.keywords:
            self.keywords[category] = []

        self.keywords[category].extend(keywords)
        self.logger.info(f"Добавлены ключевые слова для {category.value}: {keywords}")

    async def validate_content_request(self, url: str, child_id: str) -> Tuple[bool, Optional[str]]:
        """Валидация запроса анализа контента"""
        try:
            ContentAnalysisRequest(url=url, child_id=child_id)
            return True, None
        except Exception as e:
            return False, str(e)
