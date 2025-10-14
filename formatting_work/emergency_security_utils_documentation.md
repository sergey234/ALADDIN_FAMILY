# Документация файла emergency_security_utils.py

## Общая информация
- **Путь**: `/Users/sergejhlystov/ALADDIN_NEW/security/ai_agents/emergency_security_utils.py`
- **Размер**: 341 строка
- **Назначение**: Утилиты безопасности для системы экстренного реагирования
- **Принципы**: Single Responsibility Principle (SRP)

## Структура файла

### Импорты
```python
import re
import hashlib
from typing import Dict, Any, List
```

### Классы (5 классов)

#### 1. InputSanitizer
- **Назначение**: Очистка пользовательского ввода
- **Методы**:
  - `sanitize_text(text: str) -> str` - очистка текста от HTML и опасных символов
  - `sanitize_phone(phone: str) -> str` - очистка номера телефона
  - `sanitize_email(email: str) -> str` - очистка email адреса

#### 2. SecurityValidator
- **Назначение**: Валидация безопасности
- **Методы**:
  - `validate_emergency_description(description: str) -> bool` - валидация описания экстренной ситуации
  - `validate_input_length(text: str, min_length: int, max_length: int) -> bool` - проверка длины
  - `validate_contains_suspicious_content(text: str) -> bool` - проверка на подозрительное содержимое

#### 3. DataHasher
- **Назначение**: Хеширование данных для безопасности
- **Методы**:
  - `generate_event_hash(event_data: Dict[str, Any]) -> str` - хеш события для дедупликации
  - `generate_contact_hash(contact_data: Dict[str, Any]) -> str` - хеш контакта

#### 4. SecurityLogger
- **Назначение**: Логирование событий безопасности
- **Методы**:
  - `log_security_event(event_type: str, details: str, severity: str) -> None` - запись события
  - `log_validation_failure(field: str, value: str, reason: str) -> None` - запись неудачной валидации
  - `log_suspicious_activity(activity: str, details: str) -> None` - запись подозрительной активности

#### 5. EmergencySecurityUtils
- **Назначение**: Основные утилиты безопасности
- **Методы**:
  - `secure_emergency_data(data: Dict[str, Any]) -> Dict[str, Any]` - обезопасить данные
  - `validate_emergency_request(request_data: Dict[str, Any]) -> bool` - валидация запроса

## Зависимости
- **Внутренние**: Нет
- **Стандартные**: re, hashlib, typing
- **Внешние**: Нет

## Потенциальные проблемы
1. **Отсутствует импорт datetime** - используется в SecurityLogger.log_security_event
2. **Нет обработки исключений** в некоторых местах
3. **Хардкод значений** - магические числа (1000, 10, 50, 100)

## Связанные файлы
Файл импортируется в:
- emergency_event_manager.py
- emergency_utils.py  
- emergency_ml_analyzer.py
- emergency_service.py

## Оценка качества кода
- **Читаемость**: Хорошая
- **Документация**: Отличная (docstrings для всех методов)
- **Типизация**: Хорошая (используется typing)
- **Архитектура**: Соответствует SRP
- **Безопасность**: Высокая (множественные проверки)

## Рекомендации по улучшению
1. Добавить недостающий импорт datetime
2. Улучшить обработку исключений
3. Вынести константы в отдельные переменные
4. Добавить unit тесты
5. Рассмотреть использование enum для severity levels