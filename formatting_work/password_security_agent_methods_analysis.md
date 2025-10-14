# Анализ методов password_security_agent.py

## PasswordConfig (dataclass):
- `__post_init__(self)` - валидация после инициализации

## PasswordPolicy:
- `__init__(self, ...)` - инициализация политики
- `to_dict(self)` - преобразование в словарь

## PasswordMetrics:
- `__init__(self)` - инициализация метрик
- `to_dict(self)` - преобразование в словарь

## PasswordSecurityAgent (основной класс):

### Публичные методы:
- `__init__(self, name="PasswordSecurityAgent")` - конструктор
- `initialize(self)` - инициализация агента
- `generate_password(self, ...)` - генерация пароля
- `analyze_password_strength(self, password)` - анализ сложности
- `hash_password(self, password, salt=None)` - хеширование
- `verify_password(self, password, stored_hash, salt)` - проверка пароля
- `check_password_breach(self, password)` - проверка на утечку
- `validate_password_policy(self, password, policy=None)` - валидация политики
- `generate_report(self)` - генерация отчета
- `stop(self)` - остановка агента
- `to_dict(self)` - преобразование в словарь
- `validate_parameters(self, **kwargs)` - валидация параметров
- `async_generate_password(self, length=12, **kwargs)` - асинхронная генерация
- `async_analyze_password_strength(self, password)` - асинхронный анализ
- `get_health_status(self)` - статус здоровья
- `reset_metrics(self)` - сброс метрик
- `export_data(self, format_type="json")` - экспорт данных
- `import_data(self, data, format_type="json")` - импорт данных

### Приватные методы (начинаются с _):
- `_initialize_ai_models(self)` - инициализация AI моделей
- `_load_breach_database(self)` - загрузка базы утечек
- `_setup_security_systems(self)` - настройка систем безопасности
- `_validate_password_params(self, ...)` - валидация параметров пароля
- `_generate_strong_password(self, length, charset)` - генерация сильного пароля
- `_calculate_entropy(self, password)` - расчет энтропии
- `_has_common_patterns(self, password)` - проверка паттернов
- `_generate_recommendations(self)` - генерация рекомендаций
- `_save_data(self)` - сохранение данных

### Специальные методы:
- `__str__(self)` - строковое представление
- `__repr__(self)` - представление для отладки
- `__eq__(self, other)` - сравнение на равенство
- `__hash__(self)` - хеш для множеств

### Декораторы:
- `validate_parameters(**validators)` - декоратор валидации
- `async_method(func)` - декоратор для асинхронных методов

## Функции (не методы классов):
- `validate_parameters(**validators)` - декоратор валидации
- `async_method(func)` - декоратор асинхронности