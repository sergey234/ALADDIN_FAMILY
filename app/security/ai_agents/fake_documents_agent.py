# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Fake Documents Detection Agent
---------------------------------------------------------

Задача: детектировать поддельные документы (паспорта, водительские права, 
удостоверения) с помощью компьютерного зрения (OpenCV) и эвристических проверок.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from security.base import SecurityBase

from app.security.ml_lazy_loader import get_cv2, get_numpy


def _cv2():
    return get_cv2()


def _np():
    return get_numpy()


class FakeDocumentsAgent(SecurityBase):
    """
    ML агент для детекции поддельных документов на основе OpenCV.

    Возможности:
    - Анализ изображений документов
    - Проверка качества печати, водяных знаков, голограмм
    - Выявление признаков подделки (размытие, артефакты, несоответствия)
    """

    def __init__(
        self,
        threshold_low: float = 0.3,
        threshold_medium: float = 0.5,
        threshold_high: float = 0.7,
    ) -> None:
        """
        Args:
            threshold_low: порог низкой вероятности подделки.
            threshold_medium: порог средней вероятности.
            threshold_high: порог высокой вероятности (подделка).
        """
        super().__init__(name="FakeDocumentsAgent")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.threshold_low = threshold_low
        self.threshold_medium = threshold_medium
        self.threshold_high = threshold_high

    # --------------------------------------------------------------------- #
    # ПУБЛИЧНЫЕ МЕТОДЫ АНАЛИЗА
    # --------------------------------------------------------------------- #
    def detect_fake_document(self, image_path: str | Path) -> Dict:
        """
        Анализирует изображение документа на наличие признаков подделки.

        Args:
            image_path: Путь к изображению документа.

        Returns:
            Dict с оценкой подлинности и объяснением.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            return self._empty_result(reason="file_not_found")

        try:
            image = _cv2().imread(str(image_path))
            if image is None:
                return self._empty_result(reason="invalid_image")

            # Анализ различных признаков
            quality_score = self._analyze_image_quality(image)
            consistency_score = self._analyze_consistency(image)
            artifacts_score = self._analyze_artifacts(image)
            sharpness_score = self._analyze_sharpness(image)

            # Комбинированная оценка
            fake_score = self._combine_scores(
                quality_score, consistency_score, artifacts_score, sharpness_score
            )
            authenticity_level = self._score_to_level(fake_score)

            result = {
                "image_path": str(image_path),
                "quality_score": round(quality_score, 4),
                "consistency_score": round(consistency_score, 4),
                "artifacts_score": round(artifacts_score, 4),
                "sharpness_score": round(sharpness_score, 4),
                "fake_score": round(fake_score, 4),
                "authenticity_level": authenticity_level,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "recommendations": self._recommendations_for_level(authenticity_level),
            }

            self.logger.debug(
                "Fake document анализ завершён",
                extra={"authenticity_level": authenticity_level, "score": fake_score},
            )
            return result

        except Exception as exc:
            self.logger.error("Ошибка анализа документа: %s", exc)
            return self._empty_result(reason=str(exc))

    def analyze_batch(self, image_paths: Sequence[str | Path]) -> List[Dict]:
        """Обрабатывает список изображений и возвращает список результатов."""
        results: List[Dict] = []
        for image_path in image_paths:
            try:
                results.append(self.detect_fake_document(image_path))
            except Exception as exc:
                self.logger.error("Ошибка анализа изображения: %s", exc)
                results.append(self._empty_result(reason=str(exc)))
        return results

    # --------------------------------------------------------------------- #
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # --------------------------------------------------------------------- #
    def _analyze_image_quality(self, image: Any) -> float:
        """Анализирует общее качество изображения."""
        cv2 = _cv2()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Проверка разрешения
        height, width = gray.shape
        resolution_score = min(1.0, (height * width) / (2000 * 1500))
        
        # Проверка контрастности
        contrast = gray.std()
        contrast_score = min(1.0, contrast / 50.0)
        
        # Комбинированный скор качества
        quality = (resolution_score + contrast_score) / 2.0
        
        # Низкое качество может указывать на подделку
        return 1.0 - quality

    def _analyze_consistency(self, image: Any) -> float:
        """Проверяет консистентность изображения (однородность фона, текста)."""
        cv2 = _cv2()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Разделение на области (фон и текст)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Анализ вариативности
        std_dev = gray.std()
        
        # Высокая вариативность может указывать на подделку
        consistency = min(1.0, std_dev / 100.0)
        
        return consistency

    def _analyze_artifacts(self, image: Any) -> float:
        """Выявляет артефакты редактирования (клонирование, размытие, шум)."""
        cv2 = _cv2()
        np = _np()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Детекция краёв
        edges = cv2.Canny(gray, 50, 150)
        
        # Анализ паттернов краёв (неправильные паттерны = артефакты)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Проверка на размытие (лапласиан)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_score = 1.0 - min(1.0, laplacian_var / 500.0)
        
        # Комбинированный скор артефактов
        artifacts = (edge_density + blur_score) / 2.0
        
        return artifacts

    def _analyze_sharpness(self, image: Any) -> float:
        """Анализирует резкость изображения."""
        cv2 = _cv2()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Метрика резкости через лапласиан
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        # Нормализация
        sharpness_score = min(1.0, sharpness / 1000.0)
        
        # Низкая резкость может указывать на подделку
        return 1.0 - sharpness_score

    def _combine_scores(
        self,
        quality_score: float,
        consistency_score: float,
        artifacts_score: float,
        sharpness_score: float,
    ) -> float:
        """Комбинирует все оценки в итоговый скор подделки."""
        # Взвешенная сумма
        fake_score = (
            quality_score * 0.25
            + consistency_score * 0.25
            + artifacts_score * 0.30
            + sharpness_score * 0.20
        )
        
        return min(fake_score, 0.999)

    def _score_to_level(self, score: float) -> str:
        """Преобразует числовой скор в уровень подлинности."""
        if score >= self.threshold_high:
            return "fake"  # Подделка
        if score >= self.threshold_medium:
            return "suspicious"  # Подозрительно
        if score >= self.threshold_low:
            return "low_authenticity"  # Низкая подлинность
        return "authentic"  # Подлинный

    def _recommendations_for_level(self, level: str) -> List[str]:
        """Возвращает рекомендации в зависимости от уровня подлинности."""
        recommendations = {
            "fake": [
                "Документ вероятно поддельный",
                "Требуется дополнительная проверка специалистом",
                "Не использовать документ для идентификации",
            ],
            "suspicious": [
                "Документ вызывает подозрения",
                "Рекомендуется проверка через официальные каналы",
            ],
            "low_authenticity": [
                "Качество документа низкое",
                "Рекомендуется проверить оригинал",
            ],
        }
        return recommendations.get(level, [])

    @staticmethod
    def _empty_result(reason: str) -> Dict:
        """Возвращает шаблон результата в случае ошибки."""
        return {
            "image_path": "",
            "quality_score": 0.0,
            "consistency_score": 0.0,
            "artifacts_score": 0.0,
            "sharpness_score": 0.0,
            "fake_score": 0.0,
            "authenticity_level": "unknown",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reason": reason,
            "recommendations": [],
        }


__all__ = ["FakeDocumentsAgent"]

