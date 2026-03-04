# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Fake News Detection Agent
---------------------------------------------------

Задача: детектировать фейковые новости и дезинформацию в текстах.
Агент использует BERT-модель (`transformers` + `torch`) и эвристические
паттерны для выявления подозрительного контента.
"""

from __future__ import annotations

import logging
from datetime import datetime
import os
import re
from typing import Dict, List, Optional, Sequence, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

from security.base import SecurityBase


DEFAULT_MODEL_NAME = "unitary/toxic-bert"


class FakeNewsDetectionAgent(SecurityBase):
    """
    ML агент для детекции фейковых новостей на основе BERT.

    Возможности:
    - Анализ одиночных текстов и батчей
    - Выявление паттернов дезинформации (сенсационность, отсутствие источников, манипуляции)
    - Оценка достоверности с объяснениями
    """

    # Паттерны фейковых новостей для эвристической проверки
    FAKE_NEWS_PATTERNS: Dict[str, Tuple[str, ...]] = {
        "sensationalism": (
            "shocking truth",
            "they don't want you to know",
            "doctors hate this",
            "secret revealed",
            "шокирующая правда",
            "они скрывают",
            "врачи в шоке",
            "секрет раскрыт",
        ),
        "no_sources": (
            "according to anonymous sources",
            "insiders say",
            "rumors suggest",
            "по данным анонимных источников",
            "инсайдеры сообщают",
            "слухи говорят",
        ),
        "urgency_manipulation": (
            "act now",
            "limited time",
            "don't wait",
            "urgent",
            "действуй сейчас",
            "ограниченное время",
            "не жди",
            "срочно",
        ),
        "conspiracy": (
            "government cover-up",
            "big pharma",
            "mainstream media lies",
            "they're hiding",
            "правительство скрывает",
            "большая фарма",
            "СМИ врут",
            "они скрывают",
        ),
        "emotional_manipulation": (
            "you won't believe",
            "this will shock you",
            "prepare to be amazed",
            "ты не поверишь",
            "это шокирует",
            "приготовься удивиться",
        ),
    }

    # Регулярные выражения для проверки структуры новости
    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[int] = None,
        threshold_low: float = 0.4,
        threshold_medium: float = 0.6,
        threshold_high: float = 0.8,
    ) -> None:
        """
        Args:
            model_name: HuggingFace репозиторий с BERT моделью.
            device: индекс CUDA; -1/None для CPU.
            threshold_low: порог низкой достоверности.
            threshold_medium: порог средней достоверности.
            threshold_high: порог высокой достоверности (фейк).
        """
        super().__init__(name="FakeNewsDetectionAgent")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name or os.environ.get("FAKE_NEWS_MODEL_NAME", DEFAULT_MODEL_NAME)
        self.threshold_low = threshold_low
        self.threshold_medium = threshold_medium
        self.threshold_high = threshold_high
        self.device = device if device is not None else (-1 if not torch.cuda.is_available() else 0)

        self._tokenizer: Optional[AutoTokenizer] = None
        self._model: Optional[AutoModelForSequenceClassification] = None
        self._pipeline = None

        self._load_pipeline()

    # --------------------------------------------------------------------- #
    # МЕТОДЫ ИНИЦИАЛИЗАЦИИ
    # --------------------------------------------------------------------- #
    def _load_pipeline(self) -> None:
        """Загружает токенайзер, модель и инициализирует inference pipeline."""
        try:
            self.logger.info(
                "Загружаю FakeNewsDetection модель %s (device=%s)", self.model_name, self.device
            )
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self._pipeline = pipeline(
                "text-classification",
                model=self._model,
                tokenizer=self._tokenizer,
                device=self.device,
                return_all_scores=True,
                truncation=True,
            )
        except Exception as exc:
            self.logger.error("Не удалось загрузить модель %s: %s", self.model_name, exc)
            raise

    # --------------------------------------------------------------------- #
    # ПУБЛИЧНЫЕ МЕТОДЫ АНАЛИЗА
    # --------------------------------------------------------------------- #
    def detect_fake_news(self, text: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Анализирует текст на наличие признаков фейковых новостей.

        Args:
            text: Текст новости для анализа.
            metadata: Опциональные метаданные (источник, дата, автор).

        Returns:
            Dict с оценкой достоверности и объяснением.
        """
        prepared_text = (text or "").strip()
        if not prepared_text:
            return self._empty_result(reason="empty_text")

        # ML модель предсказание
        model_score = self._predict_probability(prepared_text)

        # Эвристический анализ паттернов
        pattern_hits = self._match_fake_news_patterns(prepared_text.lower())

        # Структурный анализ
        structural_flags = self._analyze_structure(prepared_text, metadata)

        # Комбинированная оценка
        fake_score = self._combine_scores(model_score, pattern_hits, structural_flags)
        credibility_level = self._score_to_level(fake_score)

        result = {
            "text_preview": prepared_text[:200],
            "model_score": round(model_score, 4),
            "fake_score": round(fake_score, 4),
            "credibility_level": credibility_level,
            "pattern_hits": pattern_hits,
            "structural_flags": structural_flags,
            "has_metadata": metadata is not None,
            "model_name": self.model_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "recommendations": self._recommendations_for_level(credibility_level),
        }

        self.logger.debug(
            "Fake news анализ завершён",
            extra={"credibility_level": credibility_level, "score": fake_score},
        )
        return result

    def analyze_batch(self, texts: Sequence[str], metadata_list: Optional[Sequence[Dict]] = None) -> List[Dict]:
        """Обрабатывает список текстов и возвращает список результатов."""
        results: List[Dict] = []
        metadata_list = metadata_list or [None] * len(texts)
        for text, metadata in zip(texts, metadata_list):
            try:
                results.append(self.detect_fake_news(text, metadata))
            except Exception as exc:
                self.logger.error("Ошибка анализа текста: %s", exc)
                results.append(self._empty_result(reason=str(exc)))
        return results

    # --------------------------------------------------------------------- #
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # --------------------------------------------------------------------- #
    def _predict_probability(self, text: str) -> float:
        """Получает вероятность фейка от BERT модели."""
        if self._pipeline is None:
            raise RuntimeError("Fake news pipeline не загружен")

        with torch.no_grad():
            predictions = self._pipeline(text)

        # Извлекаем вероятность положительного класса (fake)
        if predictions and len(predictions) > 0:
            scores = predictions[0] if isinstance(predictions[0], list) else predictions
            for score_dict in scores:
                label = str(score_dict.get("label", "")).lower()
                if "fake" in label or "1" in label or "positive" in label:
                    return float(score_dict.get("score", 0.0))
            # Если не нашли положительный класс, берём максимальный скор
            return max(float(s.get("score", 0.0)) for s in scores)
        return 0.0

    def _match_fake_news_patterns(self, text: str) -> Dict[str, List[str]]:
        """Собирает совпавшие паттерны фейковых новостей по категориям."""
        matches: Dict[str, List[str]] = {}
        for category, patterns in self.FAKE_NEWS_PATTERNS.items():
            found = []
            for pattern in patterns:
                if pattern.lower() in text:
                    found.append(pattern)
            if found:
                matches[category] = found
        return matches

    def _analyze_structure(self, text: str, metadata: Optional[Dict]) -> Dict[str, bool]:
        """Анализирует структурные признаки текста."""
        flags = {
            "has_urls": bool(self.URL_PATTERN.search(text)),
            "has_emails": bool(self.EMAIL_PATTERN.search(text)),
            "has_sources": "source" in text.lower() or "according to" in text.lower(),
            "has_dates": bool(re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", text)),
            "has_quotes": '"' in text or "'" in text,
            "too_short": len(text.split()) < 20,
            "too_long": len(text.split()) > 2000,
        }

        if metadata:
            flags["has_author"] = bool(metadata.get("author"))
            flags["has_source"] = bool(metadata.get("source"))
            flags["has_date"] = bool(metadata.get("date"))

        return flags

    def _combine_scores(
        self,
        model_score: float,
        pattern_hits: Dict[str, List[str]],
        structural_flags: Dict[str, bool],
    ) -> float:
        """
        Комбинирует модельный скор, эвристики и структурные признаки.
        """
        score = model_score

        # Усиление при наличии паттернов
        if pattern_hits:
            pattern_boost = min(len(pattern_hits) * 0.12, 0.35)
            score = max(score, score + pattern_boost)

        # Критические комбинации паттернов
        if "sensationalism" in pattern_hits and "no_sources" in pattern_hits:
            score = max(score, 0.9)
        elif "conspiracy" in pattern_hits and "emotional_manipulation" in pattern_hits:
            score = max(score, 0.85)

        # Структурные признаки снижают достоверность
        if not structural_flags.get("has_sources") and not structural_flags.get("has_urls"):
            score = max(score, score + 0.1)
        if structural_flags.get("too_short"):
            score = max(score, score + 0.05)

        return min(score, 0.999)

    def _score_to_level(self, score: float) -> str:
        """Преобразует числовой скор в уровень достоверности."""
        if score >= self.threshold_high:
            return "fake"  # Фейк
        if score >= self.threshold_medium:
            return "suspicious"  # Подозрительно
        if score >= self.threshold_low:
            return "low_credibility"  # Низкая достоверность
        return "credible"  # Достоверно

    def _recommendations_for_level(self, level: str) -> List[str]:
        """Возвращает рекомендации в зависимости от уровня достоверности."""
        recommendations = {
            "fake": [
                "Не распространять информацию",
                "Проверить через факт-чекинг сервисы",
                "Предупредить пользователей о возможной дезинформации",
            ],
            "suspicious": [
                "Требуется дополнительная проверка",
                "Проверить источники информации",
                "Ограничить распространение до верификации",
            ],
            "low_credibility": [
                "Рекомендуется проверка фактов",
                "Осторожно относиться к информации",
            ],
        }
        return recommendations.get(level, [])

    @staticmethod
    def _empty_result(reason: str) -> Dict:
        """Возвращает шаблон результата в случае ошибки или пустого текста."""
        return {
            "text_preview": "",
            "model_score": 0.0,
            "fake_score": 0.0,
            "credibility_level": "credible",
            "pattern_hits": {},
            "structural_flags": {},
            "has_metadata": False,
            "model_name": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reason": reason,
            "recommendations": [],
        }


__all__ = ["FakeNewsDetectionAgent"]

