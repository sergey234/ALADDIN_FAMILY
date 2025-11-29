# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Fake Documents Detection Agent
--------------------------------------------------------

Задача: выявлять поддельные документы (паспорт, ID, справки) по изображениям.
Агент использует классические методы компьютерного зрения (OpenCV + NumPy)
и эвристики качества печати/защитных элементов.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

from security.base import SecurityBase


@dataclass
class DocumentAnalysisConfig:
    """Пороговые значения и настройки анализа документов."""

    min_resolution: Tuple[int, int] = (600, 400)
    brightness_range: Tuple[int, int] = (40, 220)  # допустимый средний уровень яркости
    min_edge_density: float = 0.08
    max_edge_density: float = 0.45
    min_line_count: int = 15  # количество прямых линий (границы, поля)
    hologram_color_std_threshold: float = 25.0
    watermark_frequency_threshold: float = 0.55
    text_alignment_threshold: float = 0.12


class FakeDocumentsAgent(SecurityBase):
    """
    Агент детекции поддельных документов на базе OpenCV.

    Возможности:
    - Анализ структуры документа (поля, края, линии)
    - Детекция защитных элементов (водяные знаки, голограммы)
    - Проверка качества печати и уровня шума
    - Батч-анализ изображений
    """

    def __init__(self, config: Optional[DocumentAnalysisConfig] = None) -> None:
        super().__init__(name="FakeDocumentsAgent")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or DocumentAnalysisConfig()

    # ------------------------------------------------------------------ #
    # Основной публичный API
    # ------------------------------------------------------------------ #
    def analyze_document(self, image_path: Path, metadata: Optional[Dict] = None) -> Dict:
        """
        Анализ конкретного документа.

        Args:
            image_path: путь к изображению.
            metadata: дополнительные данные (тип документа, страна, серия).
        """
        if not image_path.exists():
            return self._empty_result(reason=f"file_not_found:{image_path}")

        image = cv2.imread(str(image_path))
        if image is None:
            return self._empty_result(reason=f"unreadable_file:{image_path}")

        features = self._extract_features(image)
        security_flags = self._detect_security_features(image)
        text_alignment = self._analyze_text_alignment(image)

        fake_score = self._combine_scores(features, security_flags, text_alignment, metadata)
        risk_level = self._score_to_level(fake_score)

        result = {
            "file": str(image_path),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "resolution": features["resolution"],
            "avg_brightness": round(features["avg_brightness"], 2),
            "edge_density": round(features["edge_density"], 3),
            "line_count": features["line_count"],
            "noise_index": round(features["noise_index"], 3),
            "security_flags": security_flags,
            "text_alignment": text_alignment,
            "fake_score": round(fake_score, 3),
            "risk_level": risk_level,
            "recommendations": self._recommendations_for_level(risk_level),
            "metadata": metadata or {},
        }

        self.logger.debug(
            "Документ проанализирован",
            extra={"file": str(image_path), "risk_level": risk_level, "score": fake_score},
        )
        return result

    def analyze_batch(
        self, image_paths: Sequence[Path], metadata_list: Optional[Sequence[Dict]] = None
    ) -> List[Dict]:
        """Обрабатывает список документов."""
        results: List[Dict] = []
        metadata_list = metadata_list or [None] * len(image_paths)
        for path, metadata in zip(image_paths, metadata_list):
            try:
                results.append(self.analyze_document(Path(path), metadata))
            except Exception as exc:
                self.logger.error("Ошибка анализа %s: %s", path, exc)
                results.append(self._empty_result(reason=str(exc), file=str(path)))
        return results

    # ------------------------------------------------------------------ #
    # Вспомогательные методы
    # ------------------------------------------------------------------ #
    def _extract_features(self, image: np.ndarray) -> Dict[str, float]:
        """Извлекает базовые визуальные признаки."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        edges = cv2.Canny(gray, 80, 200)
        edge_density = float(np.count_nonzero(edges)) / float(h * w)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=40, maxLineGap=5)
        line_count = 0 if lines is None else len(lines)

        avg_brightness = float(np.mean(gray))
        noise_index = float(np.std(gray) / (avg_brightness + 1e-3))

        return {
            "resolution": (w, h),
            "edge_density": edge_density,
            "line_count": line_count,
            "avg_brightness": avg_brightness,
            "noise_index": noise_index,
        }

    def _detect_security_features(self, image: np.ndarray) -> Dict[str, bool]:
        """Детектирует водяные знаки, голограммы и цветовые аномалии."""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        _, s, v = cv2.split(hsv)
        hologram_std = float(np.std(s))
        watermark_presence = self._fourier_watermark_score(image)

        return {
            "hologram_detected": hologram_std >= self.config.hologram_color_std_threshold,
            "watermark_detected": watermark_presence >= self.config.watermark_frequency_threshold,
            "uv_mark_detected": self._detect_uv_mark(image),
        }

    def _fourier_watermark_score(self, image: np.ndarray) -> float:
        """Простая метрика наличия водяного знака через спектр Фурье."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (512, 512))
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = 20 * np.log(np.abs(f_shift) + 1)

        center = magnitude[200:312, 200:312]
        peripheral = np.delete(magnitude.flatten(), np.s_[200:312])

        center_energy = np.mean(center)
        peripheral_energy = np.mean(peripheral)
        score = center_energy / (center_energy + peripheral_energy + 1e-3)
        return float(np.clip(score, 0.0, 1.0))

    def _detect_uv_mark(self, image: np.ndarray) -> bool:
        """Эвристика: ищем участки с аномальной флуоресцентной окраской."""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (120, 50, 120), (150, 255, 255))
        uv_ratio = float(np.count_nonzero(mask)) / float(image.shape[0] * image.shape[1])
        return uv_ratio > 0.02

    def _analyze_text_alignment(self, image: np.ndarray) -> Dict[str, float]:
        """Проверяет горизонтальность и вертикальность текстовых блоков."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        angles: List[float] = []
        aspect_ratios: List[float] = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w * h < 150 or w < 10 or h < 10:
                continue
            rect = cv2.minAreaRect(cnt)
            angle = rect[2]
            if angle < -45:
                angle += 90
            angles.append(angle)
            aspect_ratios.append(float(w) / float(h + 1e-3))

        if not angles:
            return {"avg_angle": 0.0, "std_angle": 0.0, "aspect_std": 0.0}

        return {
            "avg_angle": float(np.mean(angles)),
            "std_angle": float(np.std(angles)),
            "aspect_std": float(np.std(aspect_ratios)) if aspect_ratios else 0.0,
        }

    def _combine_scores(
        self,
        features: Dict[str, float],
        security_flags: Dict[str, bool],
        text_alignment: Dict[str, float],
        metadata: Optional[Dict],
    ) -> float:
        """Комбинирует метрики в итоговый риск."""
        score = 0.0

        # Разрешение/яркость
        w, h = features["resolution"]
        min_w, min_h = self.config.min_resolution
        if w < min_w or h < min_h:
            score += 0.15
        if not (self.config.brightness_range[0] <= features["avg_brightness"] <= self.config.brightness_range[1]):
            score += 0.1

        # Эджи и линии
        if features["edge_density"] < self.config.min_edge_density or features["edge_density"] > self.config.max_edge_density:
            score += 0.1
        if features["line_count"] < self.config.min_line_count:
            score += 0.1

        # Шум
        if features["noise_index"] > 0.8:
            score += 0.2

        # Защитные элементы
        if not security_flags["hologram_detected"]:
            score += 0.2
        if not security_flags["watermark_detected"]:
            score += 0.2
        if metadata and metadata.get("requires_uv_mark") and not security_flags["uv_mark_detected"]:
            score += 0.15

        # Геометрия текста
        angle_std = abs(text_alignment.get("std_angle", 0.0))
        if angle_std > self.config.text_alignment_threshold * 100:
            score += 0.15

        return float(np.clip(score, 0.0, 1.0))

    # ------------------------------------------------------------------ #
    # Утилиты
    # ------------------------------------------------------------------ #
    def _score_to_level(self, score: float) -> str:
        if score >= 0.75:
            return "fake"
        if score >= 0.55:
            return "likely_fake"
        if score >= 0.35:
            return "requires_review"
        return "verified"

    def _recommendations_for_level(self, level: str) -> List[str]:
        recommendations = {
            "fake": [
                "Не принимать документ",
                "Запросить оригинал в оффлайне",
                "Перепроверить гражданина через базу МВД",
            ],
            "likely_fake": [
                "Повторно отсканировать документ",
                "Сверить данные с реестром",
                "Попросить дополнительное удостоверение",
            ],
            "requires_review": [
                "Отправить на ручную проверку оператору",
                "Сохранить оригинал скана для аудита",
            ],
            "verified": [
                "Документ соответствует базовым критериям",
                "Можно продолжить автоматическую обработку",
            ],
        }
        return recommendations.get(level, [])

    @staticmethod
    def _empty_result(reason: str, file: Optional[str] = None) -> Dict:
        return {
            "file": file,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "resolution": (0, 0),
            "avg_brightness": 0.0,
            "edge_density": 0.0,
            "line_count": 0,
            "noise_index": 0.0,
            "security_flags": {},
            "text_alignment": {},
            "fake_score": 0.0,
            "risk_level": "unknown",
            "recommendations": [],
            "reason": reason,
            "metadata": {},
        }


__all__ = ["FakeDocumentsAgent", "DocumentAnalysisConfig"]

