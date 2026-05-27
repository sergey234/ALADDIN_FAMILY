# -*- coding: utf-8 -*-
"""P2-11 — Mood-aware classifier (scores + label for companion)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Tuple

_MOOD_RULES: Tuple[Tuple[str, re.Pattern], ...] = (
    ("playful", re.compile(r"анекдот|шутк|смешн|хаха|прикол", re.I)),
    ("sad", re.compile(r"грустн|печал|тоск|плачу", re.I)),
    ("lonely", re.compile(r"одинок|никто не разговар|некому", re.I)),
    ("nostalgic", re.compile(r"раньше|в молодости|помню", re.I)),
    ("joyful", re.compile(r"ура|получилось|радост|выиграл", re.I)),
    ("excited", re.compile(r"завтра|поездк|жду", re.I)),
    ("curious", re.compile(r"почему|как это|интересно", re.I)),
    ("anxious", re.compile(r"боюсь|страшно|тревож", re.I)),
    ("tired", re.compile(r"устал|нет сил|выгорел", re.I)),
    ("comfort_needed", re.compile(r"самоуб|хочу умереть|режу", re.I)),
)


@dataclass(frozen=True)
class MoodClassification:
    mood: str
    confidence: float
    scores: Dict[str, float]


def classify_mood(message: str) -> MoodClassification:
    """Return dominant mood and normalized scores (sum ≈ 1)."""
    msg = (message or "").strip()
    scores: Dict[str, float] = {name: 0.0 for name, _ in _MOOD_RULES}
    scores["neutral"] = 0.15

    for name, pattern in _MOOD_RULES:
        if pattern.search(msg):
            scores[name] = max(scores[name], 1.0)

    total = sum(scores.values()) or 1.0
    normalized = {k: round(v / total, 3) for k, v in scores.items()}
    mood = max(normalized, key=normalized.get)
    if normalized[mood] < 0.2:
        mood = "neutral"
    confidence = normalized.get(mood, 0.0)
    return MoodClassification(mood=mood, confidence=confidence, scores=normalized)
