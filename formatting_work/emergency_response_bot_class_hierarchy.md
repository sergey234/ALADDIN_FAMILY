# Emergency Response Bot - Иерархия Классов

## Обзор классов

### 1. Enum классы (3 класса)
- **EmergencyType** - типы экстренных ситуаций
  - Базовый класс: `Enum`
  - Значения: MEDICAL, FIRE, POLICE, SECURITY, NATURAL_DISASTER, TECHNICAL, FAMILY, CHILD_SAFETY, ELDERLY_CARE, PET_EMERGENCY

- **EmergencySeverity** - уровни серьезности
  - Базовый класс: `Enum`
  - Значения: LOW, MEDIUM, HIGH, CRITICAL, LIFE_THREATENING

- **ResponseStatus** - статусы реагирования
  - Базовый класс: `Enum`
  - Значения: PENDING, IN_PROGRESS, RESOLVED, ESCALATED, CANCELLED

### 2. SQLAlchemy модели (2 класса)
- **EmergencyContact** - контакты экстренных служб
  - Базовый класс: `Base` (SQLAlchemy)
  - Таблица: emergency_contacts
  - Поля: id, name, phone, email, service_type, priority, is_active, created_at, updated_at

- **EmergencyIncident** - инциденты экстренного реагирования
  - Базовый класс: `Base` (SQLAlchemy)
  - Таблица: emergency_incidents
  - Поля: id, incident_type, severity, description, location, coordinates, reported_by, status, response_time, resolution_time, contacts_notified, actions_taken, created_at, updated_at

### 3. Pydantic модели (3 класса)
- **EmergencyResponse** - модель ответа экстренного реагирования
  - Базовый класс: `BaseModel` (Pydantic)
  - Поля: incident_id, emergency_type, severity, location, description, reported_by, timestamp, contacts_to_notify, actions_required, estimated_response_time, priority_score

- **EmergencyContactInfo** - информация о контакте экстренных служб
  - Базовый класс: `BaseModel` (Pydantic)
  - Поля: name, phone, email, service_type, priority, is_active

- **EmergencyBotConfig** - конфигурация бота экстренного реагирования
  - Базовый класс: `BaseModel` (Pydantic)
  - Поля: auto_dial, voice_commands, gps_tracking, family_notifications, medical_data_access, multi_language, response_timeout, escalation_timeout, max_retries, emergency_contacts

### 4. Основной класс (1 класс)
- **EmergencyResponseBot** - главный класс бота
  - Базовый класс: `SecurityBase` (core.base)
  - Цепочка наследования: EmergencyResponseBot → SecurityBase → CoreBase → object

## Архитектурные особенности

### Наследование
- **Enum классы**: Простое наследование от `Enum`
- **SQLAlchemy модели**: Наследование от `Base` для ORM
- **Pydantic модели**: Наследование от `BaseModel` для валидации
- **Основной класс**: Наследование от `SecurityBase` для интеграции с системой безопасности

### Полиморфизм
- **Enum классы**: Полиморфное поведение через общий интерфейс `Enum`
- **Pydantic модели**: Полиморфизм через общие методы `BaseModel`
- **Основной класс**: Полиморфизм через интерфейс `SecurityBase`

### Интеграция
- Все классы интегрированы в единую систему экстренного реагирования
- Используют общие типы данных (Enum значения)
- Поддерживают сериализацию/десериализацию
- Интегрированы с системой логирования и мониторинга

## Статус анализа
- ✅ Структура классов проанализирована
- ✅ Наследование проверено
- ✅ Полиморфизм подтвержден
- ✅ Интеграция с системой безопасности работает