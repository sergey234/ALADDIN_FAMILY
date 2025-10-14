
# ИЕРАРХИЯ КЛАССОВ THREAT_DETECTION_AGENT.PY

## 📊 СТРУКТУРА НАСЛЕДОВАНИЯ



## 🏷️ ENUM КЛАССЫ (Перечисления)

### ThreatLevel
- **Наследование:** Enum
- **Назначение:** Уровни угроз
- **Значения:** LOW, MEDIUM, HIGH, CRITICAL

### ThreatType  
- **Наследование:** Enum
- **Назначение:** Типы угроз
- **Значения:** malware, phishing, ddos, brute_force, etc.

### DetectionStatus
- **Наследование:** Enum
- **Назначение:** Статусы обнаружения
- **Значения:** detected, analyzing, confirmed, false_positive, resolved

## 📊 DATA CLASSES (Структуры данных)

### ThreatIndicator
- **Наследование:** object (dataclass)
- **Назначение:** Индикатор угрозы
- **Атрибуты:** indicator_id, indicator_type, value, confidence, source

### ThreatDetection
- **Наследование:** object (dataclass)
- **Назначение:** Обнаружение угрозы
- **Атрибуты:** detection_id, threat_type, threat_level, confidence, timestamp

### DetectionMetrics
- **Наследование:** object (dataclass)
- **Назначение:** Метрики обнаружения
- **Атрибуты:** total_detections, false_positives, true_positives, accuracy

## 🤖 ОСНОВНОЙ КЛАСС

### ThreatDetectionAgent
- **Наследование:** SecurityBase
- **Назначение:** Основной агент обнаружения угроз
- **Функциональность:** Анализ, обнаружение, мониторинг угроз
- **Методы:** analyze_threat, detect_malware, update_metrics, etc.

## 🎯 ПРИНЦИПЫ АРХИТЕКТУРЫ

1. **Разделение ответственности:** Enum для констант, dataclass для данных, Agent для логики
2. **Наследование:** Использование базовых классов для общей функциональности
3. **Полиморфизм:** Переопределение методов базового класса
4. **Инкапсуляция:** Скрытие внутренней реализации за публичным API
