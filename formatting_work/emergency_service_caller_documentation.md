# Документация файла emergency_service_caller.py

## Общая информация
- **Файл**: `/Users/sergejhlystov/ALADDIN_NEW/security/microservices/emergency_service_caller.py`
- **Размер**: 292 строки
- **Назначение**: Менеджер вызова служб экстренного реагирования
- **Принцип**: Single Responsibility

## Структура файла

### Импорты
- `logging` - для логирования
- `datetime` - для работы с временными метками
- `typing` - для типизации (Dict, List, Optional, Any, Tuple)
- `security.ai_agents.emergency_models` - модели данных
- `security.microservices.emergency_formatters` - форматтеры сообщений
- `security.ai_agents.emergency_location_utils` - утилиты для работы с местоположением

### Класс EmergencyServiceCaller
Основной класс для управления вызовами экстренных служб.

#### Методы:
1. `__init__()` - инициализация
2. `_initialize_emergency_services()` - инициализация служб
3. `call_emergency_service()` - вызов службы
4. `_send_service_request()` - отправка запроса
5. `get_nearest_services()` - поиск ближайших служб
6. `update_response_status()` - обновление статуса
7. `get_response()` - получение ответа по ID
8. `get_responses_for_event()` - получение ответов для события
9. `get_service_statistics()` - получение статистики
10. `get_available_services()` - получение доступных служб

## Зависимости
- emergency_models (EmergencyEvent, EmergencyResponse, EmergencyService)
- emergency_formatters (EmergencyMessageFormatter)
- emergency_location_utils (LocationServiceFinder)

## Потенциальные проблемы
- Длинные строки (E501)
- Возможные проблемы с импортами (F401, F821)
- Недостаточно пустых строк (E302)
- Пробелы в конце строк (W291, W292)

## Дата создания документации
2025-01-27