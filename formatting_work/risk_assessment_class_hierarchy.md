# ИЕРАРХИЯ КЛАССОВ risk_assessment.py

## ОБЗОР
Документация иерархии классов в файле `risk_assessment.py` для системы оценки рисков безопасности ALADDIN.

## СТРУКТУРА КЛАССОВ

### 1. ENUM КЛАССЫ (4 класса)

#### 1.1 RiskCategory
- **Базовый класс**: `Enum`
- **Назначение**: Категории рисков безопасности
- **Значения**: AUTHENTICATION, AUTHORIZATION, DATA_PROTECTION, NETWORK_SECURITY, DEVICE_SECURITY, USER_BEHAVIOR, THIRD_PARTY, PHYSICAL_SECURITY, COMPLIANCE, BUSINESS_CONTINUITY
- **Строка**: 21

#### 1.2 RiskLevel
- **Базовый класс**: `Enum`
- **Назначение**: Уровни риска
- **Значения**: CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
- **Строка**: 36

#### 1.3 RiskStatus
- **Базовый класс**: `Enum`
- **Назначение**: Статусы риска
- **Значения**: IDENTIFIED, ASSESSED, MITIGATED, ACCEPTED, TRANSFERRED
- **Строка**: 46

#### 1.4 ThreatSource
- **Базовый класс**: `Enum`
- **Назначение**: Источники угроз
- **Значения**: INTERNAL, EXTERNAL, UNKNOWN
- **Строка**: 57

### 2. DATACLASS КЛАССЫ (3 класса)

#### 2.1 RiskFactor
- **Базовый класс**: `@dataclass`
- **Назначение**: Фактор риска
- **Атрибуты**: factor_id, name, description, category, weight, impact_score, likelihood_score, risk_score, created_at, updated_at
- **Строка**: 69

#### 2.2 RiskAssessment
- **Базовый класс**: `@dataclass`
- **Назначение**: Оценка риска
- **Атрибуты**: assessment_id, risk_id, risk_name, category, level, status, risk_score, impact_score, likelihood_score, description, threat_sources, affected_assets, mitigation_measures, residual_risk, assessment_date, assessor, next_review_date, metadata
- **Строка**: 85

#### 2.3 RiskProfile
- **Базовый класс**: `@dataclass`
- **Назначение**: Профиль риска пользователя/семьи
- **Атрибуты**: profile_id, user_id, risk_factors, overall_risk_score, risk_level, last_assessment, assessment_history, mitigation_recommendations
- **Строка**: 109

### 3. СЕРВИСНЫЙ КЛАСС (1 класс)

#### 3.1 RiskAssessmentService
- **Базовый класс**: `SecurityBase`
- **Назначение**: Основной сервис оценки рисков
- **Методы**: 16 методов
- **Интеграция**: Наследует от SecurityBase для интеграции с системой ALADDIN
- **Строка**: 122

## ДИАГРАММА ИЕРАРХИИ

```
Enum
├── RiskCategory
├── RiskLevel
├── RiskStatus
└── ThreatSource

@dataclass
├── RiskFactor
├── RiskAssessment
└── RiskProfile

SecurityBase
└── RiskAssessmentService
```

## АНАЛИЗ ПОЛИМОРФИЗМА

### Enum классы
- **Общий интерфейс**: Все наследуют от `Enum`
- **Полиморфизм**: Единообразный доступ к значениям через `.value`
- **Использование**: Типизация и валидация данных

### Dataclass классы
- **Общий интерфейс**: Все используют `@dataclass`
- **Полиморфизм**: Автоматические методы `__init__`, `__repr__`, `__eq__`
- **Использование**: Структуры данных для хранения информации

### SecurityBase класс
- **Интеграция**: Наследует от `SecurityBase`
- **Полиморфизм**: Стандартный интерфейс безопасности ALADDIN
- **Использование**: Основная бизнес-логика системы

## ПРИНЦИПЫ ПРОЕКТИРОВАНИЯ

### 1. Разделение ответственности
- **Enum классы**: Определение типов и констант
- **Dataclass классы**: Хранение данных
- **Сервисный класс**: Бизнес-логика

### 2. Инкапсуляция
- **Приватные методы**: Начинаются с `_`
- **Публичные методы**: Доступны для внешнего использования
- **Защищенные атрибуты**: Наследуются от SecurityBase

### 3. Расширяемость
- **Enum классы**: Легко добавлять новые значения
- **Dataclass классы**: Легко добавлять новые поля
- **Сервисный класс**: Легко добавлять новые методы

## РЕКОМЕНДАЦИИ

### ✅ Сильные стороны
1. Четкое разделение типов данных (Enum) и структур (dataclass)
2. Правильное наследование от SecurityBase для интеграции
3. Использование современных Python возможностей (@dataclass)
4. Хорошая типизация и документация

### 🔄 Возможные улучшения
1. Добавить абстрактные базовые классы для dataclass
2. Реализовать интерфейсы для полиморфизма
3. Добавить валидацию данных в dataclass
4. Расширить функциональность SecurityBase

---
*Документация создана: 2025-09-17*
*Алгоритм: УЛУЧШЕННЫЙ АЛГОРИТМ ВЕРСИИ 2.5*
*Статус: ЭТАП 6.1.4 ЗАВЕРШЕН*