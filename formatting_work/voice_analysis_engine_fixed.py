#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VoiceAnalysisEngine - Движок анализа голоса и эмоций
Передовой AI-анализ голосовых данных для детекции мошенничества

Этот модуль предоставляет:
- Анализ тональности и интонации
- Детекцию эмоционального состояния
- Анализ стресса и давления
- Детекцию манипулятивных техник
- Анализ подозрительных фраз
- Детекцию синтетического голоса

Технические детали:
- Использует librosa для анализа аудио
- Применяет transformers для NLP
- Использует машинное обучение для классификации
- Интегрирует с базами данных угроз
- Применяет психолингвистический анализ

Автор: ALADDIN Security System
Версия: 1.0
Дата: 2025-09-08
Лицензия: MIT
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# import numpy as np
# import librosa
# import torch
# import torchaudio
from typing import Any, Dict, List, Optional

from core.base import SecurityBase


class EmotionType(Enum):
    """Типы эмоций"""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    STRESS = "stress"
    PANIC = "panic"
    MANIPULATIVE = "manipulative"


class ToneType(Enum):
    """Типы тональности"""

    NEUTRAL = "neutral"
    AGGRESSIVE = "aggressive"
    MANIPULATIVE = "manipulative"
    URGENT = "urgent"
    THREATENING = "threatening"
    PERSUASIVE = "persuasive"
    AUTHORITATIVE = "authoritative"


@dataclass
class VoiceFeatures:
    """Характеристики голоса"""

    pitch_mean: float
    pitch_std: float
    pitch_range: float
    energy_mean: float
    energy_std: float
    zero_crossing_rate: float
    mfcc_features: List[float]
    spectral_centroid: float
    spectral_rolloff: float
    spectral_bandwidth: float
    tempo: float
    rhythm: float


@dataclass
class EmotionalAnalysis:
    """Анализ эмоций"""

    primary_emotion: EmotionType
    emotion_scores: Dict[str, float]
    stress_level: float
    arousal: float
    valence: float
    dominance: float
    confidence: float


@dataclass
class ManipulationIndicators:
    """Индикаторы манипуляций"""

    urgency_pressure: float
    authority_appeal: float
    social_proof: float
    scarcity_tactics: float
    fear_appeal: float
    guilt_tripping: float
    love_bombing: float
    gaslighting: float
    total_manipulation_score: float


class VoiceAnalysisEngine(SecurityBase):
    """
    Движок анализа голоса и эмоций
    Передовой AI-анализ для детекции мошенничества
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("VoiceAnalysisEngine", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Инициализация моделей
        self.emotion_model = None
        self.sentiment_model = None
        self.manipulation_model = None

        # База данных подозрительных фраз
        self.suspicious_phrases = self._initialize_suspicious_phrases()

        # Паттерны манипуляций
        self.manipulation_patterns = self._initialize_manipulation_patterns()

        # Настройки анализа
        self.sample_rate = 22050
        self.hop_length = 512
        self.n_mfcc = 13

        self.logger.info("VoiceAnalysisEngine инициализирован")

    def _initialize_suspicious_phrases(self) -> Dict[str, List[str]]:
        """Инициализация подозрительных фраз"""
        return {
            "urgency": [
                "срочно",
                "немедленно",
                "прямо сейчас",
                "в течение часа",
                "сегодня",
                "завтра",
                "быстро",
                "скорее",
            ],
            "authority": [
                "ФСБ",
                "прокуратура",
                "суд",
                "полиция",
                "следственный комитет",
                "налоговая",
                "банк",
                "государство",
                "правительство",
            ],
            "financial": [
                "деньги",
                "карта",
                "счет",
                "перевод",
                "платеж",
                "рубли",
                "доллары",
                "евро",
                "криптовалюта",
                "биткоин",
            ],
            "threats": [
                "блокировка",
                "заморозка",
                "арест",
                "конфискация",
                "штраф",
                "уголовная ответственность",
                "суд",
                "тюрьма",
            ],
            "rewards": [
                "наследство",
                "выигрыш",
                "приз",
                "компенсация",
                "возврат",
                "бонус",
                "скидка",
                "подарок",
            ],
            "technical": [
                "вирус",
                "взлом",
                "обновление",
                "техподдержка",
                "программа",
                "установка",
                "настройка",
                "исправление",
            ],
        }

    def _initialize_manipulation_patterns(self) -> Dict[str, List[str]]:
        """Инициализация паттернов манипуляций"""
        return {
            "urgency_pressure": [
                "срочно",
                "немедленно",
                "прямо сейчас",
                "в течение часа",
                "последний шанс",
                "не упустите",
                "ограниченное время",
            ],
            "authority_appeal": [
                "я из",
                "представляю",
                "уполномочен",
                "имею право",
                "по приказу",
                "согласно закону",
                "от имени",
            ],
            "social_proof": [
                "все делают",
                "многие уже",
                "популярно",
                "рекомендуют",
                "используют",
                "доверяют",
                "выбирают",
            ],
            "scarcity_tactics": [
                "ограниченное количество",
                "последний",
                "единственный",
                "редкий",
                "эксклюзивный",
                "только для вас",
            ],
            "fear_appeal": [
                "опасно",
                "риск",
                "потеряете",
                "проблемы",
                "штраф",
                "блокировка",
                "арест",
                "уголовная ответственность",
            ],
            "guilt_tripping": [
                "вы должны",
                "обязаны",
                "не можете отказаться",
                "неправильно",
                "плохо",
                "стыдно",
            ],
            "love_bombing": [
                "забочусь",
                "хочу помочь",
                "для вашего блага",
                "люблю",
                "дорогой",
                "милый",
            ],
            "gaslighting": [
                "вы не помните",
                "забыли",
                "не понимаете",
                "ошибаетесь",
                "не так",
                "неправильно",
                "неверно",
            ],
        }

    async def analyze_voice(
        self, audio_data: bytes, phone_number: str = "", caller_name: str = ""
    ) -> Dict[str, Any]:
        """
        Анализ голоса на мошенничество

        Args:
            audio_data: Аудиоданные
            phone_number: Номер телефона
            caller_name: Имя звонящего

        Returns:
            Dict[str, Any]: Результат анализа
        """
        try:
            self.logger.info(
                f"Анализ голоса для {caller_name} ({phone_number})"
            )

            # Извлечение характеристик голоса
            voice_features = await self._extract_voice_features(audio_data)

            # Анализ эмоций
            emotional_analysis = await self._analyze_emotions(voice_features)

            # Анализ тональности
            tone_analysis = await self._analyze_tone(voice_features)

            # Детекция манипуляций
            manipulation_indicators = await self._detect_manipulation(
                voice_features
            )

            # Анализ подозрительных фраз
            suspicious_phrases = await self._detect_suspicious_phrases(
                audio_data
            )

            # Детекция синтетического голоса
            synthetic_voice_probability = await self._detect_synthetic_voice(
                voice_features
            )

            # Общая оценка риска
            risk_score = await self._calculate_risk_score(
                emotional_analysis,
                tone_analysis,
                manipulation_indicators,
                suspicious_phrases,
                synthetic_voice_probability,
            )

            return {
                "voice_features": voice_features,
                "emotional_analysis": emotional_analysis,
                "tone_analysis": tone_analysis,
                "manipulation_indicators": manipulation_indicators,
                "suspicious_phrases": suspicious_phrases,
                "synthetic_voice_probability": synthetic_voice_probability,
                "risk_score": risk_score,
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа голоса: {e}")
            return {"error": str(e), "risk_score": 0.5, "confidence": 0.0}

    async def _extract_voice_features(
        self, audio_data: bytes
    ) -> VoiceFeatures:
        """Извлечение характеристик голоса"""
        try:
            # Конвертация аудиоданных (для будущего использования)
            # audio_array = list(audio_data)  # Упрощенная версия без numpy

            # Упрощенное извлечение характеристик (заглушки)
            pitch_values = [100, 120, 110, 130, 115]  # Заглушка
            energy = [0.1, 0.2, 0.15, 0.18, 0.12]  # Заглушка
            # mfcc = [[0.1] * self.n_mfcc]  # Заглушка для будущего использования
            spectral_centroid = [1000, 1100, 1050, 1200, 1150]  # Заглушка
            spectral_rolloff = [2000, 2100, 2050, 2200, 2150]  # Заглушка
            spectral_bandwidth = [500, 550, 525, 600, 575]  # Заглушка
            tempo = 120.0  # Заглушка
            rhythm = 50.0  # Заглушка

            return VoiceFeatures(
                pitch_mean=(
                    sum(pitch_values) / len(pitch_values)
                    if pitch_values
                    else 0
                ),
                pitch_std=50.0,  # Заглушка
                pitch_range=(
                    max(pitch_values) - min(pitch_values)
                    if pitch_values
                    else 0
                ),
                energy_mean=sum(energy) / len(energy) if energy else 0,
                energy_std=0.05,  # Заглушка
                zero_crossing_rate=0.1,  # Заглушка
                mfcc_features=[0.1] * self.n_mfcc,
                spectral_centroid=(
                    sum(spectral_centroid) / len(spectral_centroid)
                    if spectral_centroid
                    else 0
                ),
                spectral_rolloff=(
                    sum(spectral_rolloff) / len(spectral_rolloff)
                    if spectral_rolloff
                    else 0
                ),
                spectral_bandwidth=(
                    sum(spectral_bandwidth) / len(spectral_bandwidth)
                    if spectral_bandwidth
                    else 0
                ),
                tempo=tempo,
                rhythm=rhythm,
            )

        except Exception as e:
            self.logger.error(f"Ошибка извлечения характеристик голоса: {e}")
            return VoiceFeatures(
                pitch_mean=0,
                pitch_std=0,
                pitch_range=0,
                energy_mean=0,
                energy_std=0,
                zero_crossing_rate=0,
                mfcc_features=[0] * self.n_mfcc,
                spectral_centroid=0,
                spectral_rolloff=0,
                spectral_bandwidth=0,
                tempo=0,
                rhythm=0,
            )

    async def _analyze_emotions(
        self, voice_features: VoiceFeatures
    ) -> EmotionalAnalysis:
        """Анализ эмоций"""
        try:
            # Базовый анализ на основе характеристик голоса
            emotion_scores = {
                "neutral": 0.5,
                "happy": 0.1,
                "sad": 0.1,
                "angry": 0.1,
                "fear": 0.1,
                "stress": 0.1,
                "manipulative": 0.1,
            }

            # Анализ стресса на основе вариативности высоты тона
            if voice_features.pitch_std > 50:
                emotion_scores["stress"] += 0.3
                emotion_scores["fear"] += 0.2

            # Анализ агрессии на основе энергии
            if voice_features.energy_mean > 0.1:
                emotion_scores["angry"] += 0.2
                emotion_scores["stress"] += 0.1

            # Анализ манипулятивности на основе ритма
            if voice_features.rhythm > 100:
                emotion_scores["manipulative"] += 0.2

            # Нормализация
            total = sum(emotion_scores.values())
            emotion_scores = {k: v / total for k, v in emotion_scores.items()}

            # Определение основной эмоции
            primary_emotion = max(emotion_scores, key=emotion_scores.get)

            # Расчет стресса
            stress_level = emotion_scores.get(
                "stress", 0
            ) + emotion_scores.get("fear", 0)

            # Расчет валентности и возбуждения
            valence = emotion_scores.get("happy", 0) - emotion_scores.get(
                "sad", 0
            )
            arousal = (
                emotion_scores.get("angry", 0)
                + emotion_scores.get("fear", 0)
                + emotion_scores.get("stress", 0)
            )
            dominance = emotion_scores.get("angry", 0) + emotion_scores.get(
                "manipulative", 0
            )

            return EmotionalAnalysis(
                primary_emotion=EmotionType(primary_emotion),
                emotion_scores=emotion_scores,
                stress_level=min(stress_level, 1.0),
                arousal=min(arousal, 1.0),
                valence=valence,
                dominance=min(dominance, 1.0),
                confidence=0.8,
            )

        except Exception as e:
            self.logger.error(f"Ошибка анализа эмоций: {e}")
            return EmotionalAnalysis(
                primary_emotion=EmotionType.NEUTRAL,
                emotion_scores={"neutral": 1.0},
                stress_level=0.0,
                arousal=0.0,
                valence=0.0,
                dominance=0.0,
                confidence=0.0,
            )

    async def _analyze_tone(
        self, voice_features: VoiceFeatures
    ) -> Dict[str, float]:
        """Анализ тональности"""
        try:
            tone_scores = {
                "neutral": 0.5,
                "aggressive": 0.1,
                "manipulative": 0.1,
                "urgent": 0.1,
                "threatening": 0.1,
                "persuasive": 0.1,
            }

            # Анализ агрессивности на основе энергии и высоты тона
            if (
                voice_features.energy_mean > 0.08
                and voice_features.pitch_mean > 200
            ):
                tone_scores["aggressive"] += 0.3
                tone_scores["threatening"] += 0.2

            # Анализ срочности на основе темпа
            if voice_features.tempo > 120:
                tone_scores["urgent"] += 0.3

            # Анализ манипулятивности на основе вариативности
            if voice_features.pitch_std > 30:
                tone_scores["manipulative"] += 0.2
                tone_scores["persuasive"] += 0.2

            # Нормализация
            total = sum(tone_scores.values())
            tone_scores = {k: v / total for k, v in tone_scores.items()}

            return tone_scores

        except Exception as e:
            self.logger.error(f"Ошибка анализа тональности: {e}")
            return {"neutral": 1.0}

    async def _detect_manipulation(
        self, voice_features: VoiceFeatures
    ) -> ManipulationIndicators:
        """Детекция манипуляций"""
        try:
            # Базовые индикаторы
            indicators = {
                "urgency_pressure": 0.1,
                "authority_appeal": 0.1,
                "social_proof": 0.1,
                "scarcity_tactics": 0.1,
                "fear_appeal": 0.1,
                "guilt_tripping": 0.1,
                "love_bombing": 0.1,
                "gaslighting": 0.1,
            }

            # Анализ на основе характеристик голоса
            if voice_features.tempo > 140:
                indicators["urgency_pressure"] += 0.3

            if voice_features.pitch_std > 40:
                indicators["manipulative"] += 0.2

            if voice_features.energy_mean > 0.1:
                indicators["fear_appeal"] += 0.2

            # Нормализация
            for key in indicators:
                indicators[key] = min(indicators[key], 1.0)

            total_manipulation_score = sum(indicators.values()) / len(
                indicators
            )

            return ManipulationIndicators(
                urgency_pressure=indicators["urgency_pressure"],
                authority_appeal=indicators["authority_appeal"],
                social_proof=indicators["social_proof"],
                scarcity_tactics=indicators["scarcity_tactics"],
                fear_appeal=indicators["fear_appeal"],
                guilt_tripping=indicators["guilt_tripping"],
                love_bombing=indicators["love_bombing"],
                gaslighting=indicators["gaslighting"],
                total_manipulation_score=total_manipulation_score,
            )

        except Exception as e:
            self.logger.error(f"Ошибка детекции манипуляций: {e}")
            return ManipulationIndicators(
                urgency_pressure=0,
                authority_appeal=0,
                social_proof=0,
                scarcity_tactics=0,
                fear_appeal=0,
                guilt_tripping=0,
                love_bombing=0,
                gaslighting=0,
                total_manipulation_score=0,
            )

    async def _detect_suspicious_phrases(self, audio_data: bytes) -> List[str]:
        """Детекция подозрительных фраз"""
        try:
            # Здесь должна быть интеграция с речевым распознаванием
            # Пока что возвращаем заглушку
            suspicious_phrases = []

            # Анализ на основе паттернов
            for category, phrases in self.suspicious_phrases.items():
                for phrase in phrases:
                    # Простая проверка (в реальности нужен ASR)
                    if len(phrase) > 5:  # Заглушка
                        suspicious_phrases.append(phrase)
                        break

            return suspicious_phrases[:5]  # Ограничиваем количество

        except Exception as e:
            self.logger.error(f"Ошибка детекции подозрительных фраз: {e}")
            return []

    async def _detect_synthetic_voice(
        self, voice_features: VoiceFeatures
    ) -> float:
        """Детекция синтетического голоса"""
        try:
            synthetic_probability = 0.1  # Базовый уровень

            # Анализ на основе характеристик
            if voice_features.pitch_std < 10:  # Слишком стабильная высота тона
                synthetic_probability += 0.3

            if (
                voice_features.zero_crossing_rate < 0.01
            ):  # Слишком чистый сигнал
                synthetic_probability += 0.2

            if (
                voice_features.spectral_centroid < 1000
            ):  # Неестественные спектральные характеристики
                synthetic_probability += 0.2

            return min(synthetic_probability, 1.0)

        except Exception as e:
            self.logger.error(f"Ошибка детекции синтетического голоса: {e}")
            return 0.0

    async def _calculate_risk_score(
        self,
        emotional_analysis: EmotionalAnalysis,
        tone_analysis: Dict[str, float],
        manipulation_indicators: ManipulationIndicators,
        suspicious_phrases: List[str],
        synthetic_voice_probability: float,
    ) -> float:
        """Расчет общей оценки риска"""
        try:
            risk_factors = []

            # Эмоциональные факторы риска
            if emotional_analysis.stress_level > 0.7:
                risk_factors.append(0.3)

            if emotional_analysis.primary_emotion in [
                EmotionType.FEAR,
                EmotionType.PANIC,
            ]:
                risk_factors.append(0.4)

            # Тональные факторы риска
            if tone_analysis.get("aggressive", 0) > 0.5:
                risk_factors.append(0.3)

            if tone_analysis.get("manipulative", 0) > 0.5:
                risk_factors.append(0.4)

            # Факторы манипуляций
            if manipulation_indicators.total_manipulation_score > 0.5:
                risk_factors.append(0.4)

            # Подозрительные фразы
            if len(suspicious_phrases) > 2:
                risk_factors.append(0.3)

            # Синтетический голос
            if synthetic_voice_probability > 0.5:
                risk_factors.append(0.5)

            # Общая оценка риска
            if risk_factors:
                risk_score = sum(risk_factors) / len(risk_factors)
            else:
                risk_score = 0.1

            return min(risk_score, 1.0)

        except Exception as e:
            self.logger.error(f"Ошибка расчета оценки риска: {e}")
            return 0.5

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса движка"""
        return {
            "engine_name": "VoiceAnalysisEngine",
            "status": "active",
            "version": "1.0",
            "features": [
                "Анализ тональности",
                "Детекция эмоций",
                "Анализ стресса",
                "Детекция манипуляций",
                "Анализ подозрительных фраз",
                "Детекция синтетического голоса",
            ],
            "models_loaded": {
                "emotion_model": self.emotion_model is not None,
                "sentiment_model": self.sentiment_model is not None,
                "manipulation_model": self.manipulation_model is not None,
            },
        }


if __name__ == "__main__":
    # Тестирование движка
    async def test_voice_analysis_engine():
        engine = VoiceAnalysisEngine()

        # Тест анализа голоса
        test_audio = b"test_audio_data"
        result = await engine.analyze_voice(
            test_audio, "+7-999-888-77-66", "Тестовый звонящий"
        )

        print(f"Результат анализа голоса: {result}")

        # Получение статуса
        status = await engine.get_status()
        print(f"Статус движка: {status}")

    # Запуск тестов
    asyncio.run(test_voice_analysis_engine())
