# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Grooming Detection Agent
---------------------------------------------------

Задача: детектировать паттерны grooming (ухаживания/манипуляций) в переписках
с несовершеннолетними. Агент использует Transformer-архитектуру (BERT-based)
для анализа последовательностей сообщений и выявления подозрительных паттернов.
"""

from __future__ import annotations

import logging
from datetime import datetime
import os
from typing import Dict, List, Optional, Sequence, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

from security.base import SecurityBase


DEFAULT_MODEL_NAME = "distilbert-base-uncased"


class GroomingDetectionAgent(SecurityBase):
    """
    ML агент для детекции grooming контента на основе Transformer.

    Возможности:
    - Анализ одиночных сообщений и последовательностей диалогов
    - Выявление паттернов манипуляций (секретность, подарки, изоляция)
    - Оценка риска с объяснениями
    """

    # Паттерны grooming для эвристической проверки
    GROOMING_PATTERNS: Dict[str, Tuple[str, ...]] = {
        "secrecy": (
            "don't tell anyone",
            "this is our secret",
            "just between us",
            "don't mention this",
            "keep this private",
            "не говори никому",
            "это наш секрет",
            "только между нами",
        ),
        "gifts_bribery": (
            "i can buy you",
            "i'll give you",
            "i have gifts for you",
            "i can send you money",
            "я куплю тебе",
            "я подарю тебе",
            "я могу дать тебе",
        ),
        "isolation": (
            "your parents don't understand",
            "they won't let us",
            "don't trust them",
            "твои родители не поймут",
            "они нам не позволят",
            "не доверяй им",
        ),
        "age_inappropriate": (
            "you're so mature",
            "you're not like other kids",
            "you're special",
            "ты такая взрослая",
            "ты не как другие дети",
            "ты особенная",
        ),
        "meeting_request": (
            "let's meet alone",
            "come to my place",
            "we should meet",
            "давай встретимся",
            "приходи ко мне",
            "надо встретиться",
        ),
    }

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[int] = None,
        threshold_medium: float = 0.5,
        threshold_high: float = 0.7,
        threshold_critical: float = 0.85,
    ) -> None:
        """
        Args:
            model_name: HuggingFace репозиторий с Transformer моделью.
            device: индекс CUDA; -1/None для CPU.
            threshold_medium: порог среднего риска.
            threshold_high: порог высокого риска.
            threshold_critical: порог критического риска.
        """
        super().__init__(name="GroomingDetectionAgent")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name or os.environ.get("GROOMING_MODEL_NAME", DEFAULT_MODEL_NAME)
        self.threshold_medium = threshold_medium
        self.threshold_high = threshold_high
        self.threshold_critical = threshold_critical
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
                "Загружаю GroomingDetection модель %s (device=%s)", self.model_name, self.device
            )
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            try:
                self._model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name, num_labels=2
                )
            except Exception:
                # Если модель не поддерживает num_labels, загружаем без него
                self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            try:
                self._pipeline = pipeline(
                    "text-classification",
                    model=self._model,
                    tokenizer=self._tokenizer,
                    device=self.device,
                    return_all_scores=True,
                    truncation=True,
                    max_length=512,
                )
            except Exception:
                # Fallback: без return_all_scores для совместимости
                self._pipeline = pipeline(
                    "text-classification",
                    model=self._model,
                    tokenizer=self._tokenizer,
                    device=self.device,
                    truncation=True,
                    max_length=512,
                )
        except Exception as exc:
            self.logger.error("Не удалось загрузить модель %s: %s", self.model_name, exc)
            raise

    # --------------------------------------------------------------------- #
    # ПУБЛИЧНЫЕ МЕТОДЫ АНАЛИЗА
    # --------------------------------------------------------------------- #
    def detect_grooming(self, text: str, context: Optional[List[str]] = None) -> Dict:
        """
        Анализирует текст на наличие grooming паттернов.

        Args:
            text: Текст сообщения для анализа.
            context: Опциональный список предыдущих сообщений для контекста.

        Returns:
            Dict с оценкой риска и объяснением.
        """
        prepared_text = (text or "").strip()
        if not prepared_text:
            return self._empty_result(reason="empty_text")

        # ML модель предсказание
        model_score = self._predict_probability(prepared_text)

        # Эвристический анализ паттернов
        pattern_hits = self._match_grooming_patterns(prepared_text.lower())

        # Комбинированная оценка
        risk_score = self._combine_scores(model_score, pattern_hits, context)
        risk_level = self._score_to_level(risk_score)

        result = {
            "text_preview": prepared_text[:200],
            "model_score": round(model_score, 4),
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level,
            "pattern_hits": pattern_hits,
            "context_used": context is not None and len(context) > 0,
            "model_name": self.model_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "recommendations": self._recommendations_for_level(risk_level),
        }

        self.logger.debug(
            "Grooming анализ завершён", extra={"risk_level": risk_level, "score": risk_score}
        )
        return result

    def analyze_conversation(self, messages: Sequence[str]) -> Dict:
        """
        Анализирует последовательность сообщений в диалоге.

        Args:
            messages: Список сообщений в хронологическом порядке.

        Returns:
            Dict с агрегированной оценкой риска для всего диалога.
        """
        if not messages:
            return self._empty_result(reason="empty_conversation")

        individual_results = []
        for msg in messages:
            context = messages[: messages.index(msg)] if msg in messages else []
            result = self.detect_grooming(msg, context)
            individual_results.append(result)

        # Агрегация результатов
        max_risk = max(r.get("risk_score", 0.0) for r in individual_results)
        avg_risk = sum(r.get("risk_score", 0.0) for r in individual_results) / len(individual_results)
        total_patterns = sum(len(r.get("pattern_hits", {})) for r in individual_results)

        return {
            "conversation_risk_score": round(max_risk, 4),
            "average_risk_score": round(avg_risk, 4),
            "risk_level": self._score_to_level(max_risk),
            "total_messages": len(messages),
            "total_pattern_hits": total_patterns,
            "individual_results": individual_results,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "recommendations": self._recommendations_for_level(self._score_to_level(max_risk)),
        }

    def analyze_batch(self, texts: Sequence[str]) -> List[Dict]:
        """Обрабатывает список сообщений и возвращает список результатов."""
        results: List[Dict] = []
        for text in texts:
            try:
                results.append(self.detect_grooming(text))
            except Exception as exc:
                self.logger.error("Ошибка анализа сообщения: %s", exc)
                results.append(self._empty_result(reason=str(exc)))
        return results

    # --------------------------------------------------------------------- #
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # --------------------------------------------------------------------- #
    def _predict_probability(self, text: str) -> float:
        """Получает вероятность grooming от Transformer модели."""
        if self._pipeline is None:
            raise RuntimeError("Grooming pipeline не загружен")

        with torch.no_grad():
            predictions = self._pipeline(text)

        # Извлекаем вероятность положительного класса (grooming)
        if predictions and len(predictions) > 0:
            # Если predictions - список списков (return_all_scores=True)
            if isinstance(predictions[0], list):
                scores = predictions[0]
                for score_dict in scores:
                    label = str(score_dict.get("label", "")).lower()
                    if "positive" in label or "1" in label or "grooming" in label:
                        return float(score_dict.get("score", 0.0))
                # Если не нашли положительный класс, берём максимальный скор
                return max(float(s.get("score", 0.0)) for s in scores)
            else:
                # Если predictions - один словарь (без return_all_scores)
                score_dict = predictions[0] if isinstance(predictions, list) else predictions
                label = str(score_dict.get("label", "")).lower()
                score = float(score_dict.get("score", 0.0))
                # Если метка похожа на положительную, возвращаем скор, иначе 1-score
                if "positive" in label or "1" in label or "grooming" in label:
                    return score
                return 1.0 - score if score < 0.5 else score
        return 0.0

    def _match_grooming_patterns(self, text: str) -> Dict[str, List[str]]:
        """Собирает совпавшие grooming паттерны по категориям."""
        matches: Dict[str, List[str]] = {}
        for category, patterns in self.GROOMING_PATTERNS.items():
            found = []
            for pattern in patterns:
                if pattern.lower() in text:
                    found.append(pattern)
            if found:
                matches[category] = found
        return matches

    def _combine_scores(
        self, model_score: float, pattern_hits: Dict[str, List[str]], context: Optional[List[str]]
    ) -> float:
        """
        Комбинирует модельный скор, эвристики и контекст.
        """
        score = model_score

        # Усиление при наличии паттернов
        if pattern_hits:
            pattern_boost = min(len(pattern_hits) * 0.15, 0.3)
            score = max(score, score + pattern_boost)

        # Усиление при наличии контекста (повторяющиеся паттерны)
        if context and len(context) > 0:
            context_boost = min(len(context) * 0.05, 0.2)
            score = max(score, score + context_boost)

        # Критические паттерны дают максимальный буст
        if "secrecy" in pattern_hits and "meeting_request" in pattern_hits:
            score = max(score, 0.95)
        elif "secrecy" in pattern_hits or "meeting_request" in pattern_hits:
            score = max(score, 0.85)

        return min(score, 0.999)

    def _score_to_level(self, score: float) -> str:
        """Преобразует числовой скор в уровень риска."""
        if score >= self.threshold_critical:
            return "critical"
        if score >= self.threshold_high:
            return "high"
        if score >= self.threshold_medium:
            return "medium"
        if score >= 0.3:
            return "low"
        return "safe"

    def _recommendations_for_level(self, level: str) -> List[str]:
        """Возвращает рекомендации в зависимости от уровня риска."""
        recommendations = {
            "critical": [
                "Немедленно заблокировать контакт и уведомить родителей",
                "Сохранить все сообщения для правоохранительных органов",
                "Запустить протокол экстренного реагирования",
            ],
            "high": [
                "Заблокировать контакт и уведомить родителей",
                "Усилить мониторинг активности ребёнка",
                "Провести беседу о безопасности в интернете",
            ],
            "medium": [
                "Показать родителям подозрительные сообщения",
                "Усилить мониторинг переписки",
                "Объяснить ребёнку признаки опасного общения",
            ],
            "low": [
                "Сохранить запись для последующего анализа",
                "Продолжать обычный мониторинг",
            ],
        }
        return recommendations.get(level, [])

    @staticmethod
    def _empty_result(reason: str) -> Dict:
        """Возвращает шаблон результата в случае ошибки или пустого текста."""
        return {
            "text_preview": "",
            "model_score": 0.0,
            "risk_score": 0.0,
            "risk_level": "safe",
            "pattern_hits": {},
            "context_used": False,
            "model_name": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reason": reason,
            "recommendations": [],
        }


__all__ = ["GroomingDetectionAgent"]
