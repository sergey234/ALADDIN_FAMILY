# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Self Harm Detection Agent
---------------------------------------------------

Задача: анализировать пользовательские сообщения, посты и чаты на наличие
саморазрушительных паттернов поведения. Агент использует BERT-модель
(`transformers` + `torch`) и дополнительные эвристики для повышения точности.
"""

from __future__ import annotations

import logging
from datetime import datetime
import os
from typing import Dict, List, Optional, Sequence, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

from security.base import SecurityBase


DEFAULT_MODEL_NAME = "unitary/toxic-bert"


class SelfHarmDetectionAgent(SecurityBase):
    """
    ML агент для детекции self-harm контента.

    Возможности:
    - Анализ одиночных сообщений и батчей
    - Нормализация оценки риска по нескольким источникам (ML + ключевые слова)
    - Выдача объяснений: что повлияло на итоговый риск
    """

    # Лейблы моделей, которые считаются «саморазрушительными».
    POSITIVE_LABEL_TOKENS = (
        "self-harm",
        "selfharm",
        "suicide",
        "self_harm",
        "harmful",
        "label_1",
    )

    # Списки ключевых слов для быстрой эвристической оценки
    KEYWORD_GROUPS: Dict[str, Tuple[str, ...]] = {
        "critical": (
            "хочу умереть",
            "покончу с собой",
            "повешусь",
            "я умру",
            "я не хочу жить",
            "kill myself",
            "commit suicide",
            "end my life",
        ),
        "high": (
            "резать себя",
            "навредить себе",
            "self harm",
            "суицид",
            "суицидальные мысли",
            "take all pills",
            "jump off",
        ),
        "medium": (
            "депрессия",
            "ненавижу себя",
            "no reason to live",
            "life is pointless",
        ),
    }

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[int] = None,
        threshold_high: float = 0.65,
        threshold_critical: float = 0.85,
    ) -> None:
        """
        Args:
            model_name: HuggingFace репозиторий с моделью.
            device: индекс CUDA; -1/None для CPU.
            threshold_high: порог высокого риска для вывода модели.
            threshold_critical: порог критического риска.
        """
        super().__init__(name="SelfHarmDetectionAgent")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name or os.environ.get("SELF_HARM_MODEL_NAME", DEFAULT_MODEL_NAME)
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
                "Загружаю SelfHarmDetection модель %s (device=%s)", self.model_name, self.device
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
    def detect_self_harm(self, text: str) -> Dict:
        """
        Анализирует одну строку текста.

        Returns:
            Dict с оценкой риска и объяснением.
        """
        prepared_text = (text or "").strip()
        if not prepared_text:
            return self._empty_result(reason="empty_text")

        model_score = self._predict_probability(prepared_text)
        keyword_hits = self._match_keywords(prepared_text.lower())
        risk_score = self._combine_scores(model_score, keyword_hits)
        risk_level = self._score_to_level(risk_score)

        result = {
            "text_preview": prepared_text[:200],
            "model_score": round(model_score, 4),
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level,
            "keyword_hits": keyword_hits,
            "model_name": self.model_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "recommendations": self._recommendations_for_level(risk_level),
        }

        self.logger.debug(
            "Self-harm анализ завершён", extra={"risk_level": risk_level, "score": risk_score}
        )
        return result

    def analyze_batch(self, texts: Sequence[str]) -> List[Dict]:
        """Обрабатывает список сообщений и возвращает список результатов."""
        results: List[Dict] = []
        for text in texts:
            try:
                results.append(self.detect_self_harm(text))
            except Exception as exc:  # pragma: no cover - защитный блок
                self.logger.error("Ошибка анализа сообщения: %s", exc)
                results.append(self._empty_result(reason=str(exc)))
        return results

    # --------------------------------------------------------------------- #
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # --------------------------------------------------------------------- #
    def _predict_probability(self, text: str) -> float:
        """Получает вероятность self-harm от ML модели."""
        if self._pipeline is None:
            raise RuntimeError("Self-harm pipeline не загружен")

        with torch.no_grad():
            predictions = self._pipeline(text)

        return self._extract_positive_score(predictions)

    def _extract_positive_score(self, predictions: List[List[Dict]]) -> float:
        """
        HuggingFace pipeline возвращает список списков (батч x лейблы).
        Забираем максимум по релевантным лейблам.
        """
        if not predictions:
            return 0.0

        label_scores = predictions[0] if isinstance(predictions[0], list) else predictions
        score = 0.0
        for candidate in label_scores:
            label = str(candidate.get("label", "")).lower()
            if any(token in label for token in self.POSITIVE_LABEL_TOKENS):
                score = max(score, float(candidate.get("score", 0.0)))
        return score

    def _match_keywords(self, text: str) -> Dict[str, List[str]]:
        """Собирает совпавшие ключевые слова по группам рисков."""
        matches: Dict[str, List[str]] = {"critical": [], "high": [], "medium": []}
        for level, keywords in self.KEYWORD_GROUPS.items():
            for keyword in keywords:
                if keyword in text:
                    matches[level].append(keyword)
        # очищаем пустые уровни для компактности результата
        return {level: hits for level, hits in matches.items() if hits}

    def _combine_scores(self, model_score: float, keyword_hits: Dict[str, List[str]]) -> float:
        """
        Комбинирует модельный скор и эвристики.
        При наличии совпадений усиливаем итоговую вероятность.
        """
        score = model_score
        if "critical" in keyword_hits:
            score = max(score, 0.95)
        elif "high" in keyword_hits:
            score = max(score, 0.8)
        elif "medium" in keyword_hits:
            score = max(score, 0.6)
        return min(score, 0.999)

    def _score_to_level(self, score: float) -> str:
        if score >= self.threshold_critical:
            return "critical"
        if score >= self.threshold_high:
            return "high"
        if score >= 0.4:
            return "medium"
        if score >= 0.2:
            return "low"
        return "safe"

    def _recommendations_for_level(self, level: str) -> List[str]:
        recommendations = {
            "critical": [
                "Немедленно уведомить службу поддержки и родителей",
                "Запустить протокол экстренной связи",
            ],
            "high": [
                "Отправить уведомление психологу/опекуну",
                "Запросить подтверждение безопасности пользователя",
            ],
            "medium": [
                "Показать пользователю материалы психологической поддержки",
                "Усилить мониторинг общения в течение 24 часов",
            ],
            "low": [
                "Сохранить запись разговора для последующего анализа",
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
            "keyword_hits": {},
            "model_name": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reason": reason,
            "recommendations": [],
        }


__all__ = ["SelfHarmDetectionAgent"]


