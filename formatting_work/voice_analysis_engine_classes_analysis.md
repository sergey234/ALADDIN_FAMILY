# Анализ структуры классов voice_analysis_engine.py

## Иерархия классов

### 1. Enum классы
- **EmotionType(Enum)** - типы эмоций
  - Базовый класс: Enum
  - MRO: EmotionType → Enum → object
  - Значения: NEUTRAL, HAPPY, SAD, ANGRY, FEAR, SURPRISE, DISGUST, STRESS, PANIC, MANIPULATIVE

- **ToneType(Enum)** - типы тональности
  - Базовый класс: Enum
  - MRO: ToneType → Enum → object
  - Значения: NEUTRAL, AGGRESSIVE, MANIPULATIVE, URGENT, THREATENING, PERSUASIVE, AUTHORITATIVE

### 2. Dataclass классы
- **VoiceFeatures(dataclass)** - характеристики голоса
  - Базовый класс: object
  - MRO: VoiceFeatures → object
  - Атрибуты: pitch_mean, pitch_std, pitch_range, energy_mean, energy_std, zero_crossing_rate, mfcc_features, spectral_centroid, spectral_rolloff, spectral_bandwidth, tempo, rhythm

- **EmotionalAnalysis(dataclass)** - анализ эмоций
  - Базовый класс: object
  - MRO: EmotionalAnalysis → object
  - Атрибуты: primary_emotion, emotion_scores, stress_level, arousal, valence, dominance, confidence

- **ManipulationIndicators(dataclass)** - индикаторы манипуляций
  - Базовый класс: object
  - MRO: ManipulationIndicators → object
  - Атрибуты: urgency_pressure, authority_appeal, social_proof, scarcity_tactics, fear_appeal, guilt_tripping, love_bombing, gaslighting, total_manipulation_score

### 3. Основной класс
- **VoiceAnalysisEngine(SecurityBase)** - движок анализа голоса
  - Базовый класс: SecurityBase
  - MRO: VoiceAnalysisEngine → SecurityBase → CoreBase → ABC → object
  - Наследует от SecurityBase (система безопасности ALADDIN)

## Анализ наследования
- Все Enum классы наследуют от стандартного Enum
- Все dataclass классы наследуют от object
- VoiceAnalysisEngine наследует от SecurityBase (интеграция с системой безопасности)
- Полиморфизм реализован через наследование от SecurityBase

## Статус: ✅ Структура классов корректна