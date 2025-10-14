# Smart Notification Manager Extra

## 📋 Описание

`SmartNotificationManagerExtra` - это продвинутый менеджер уведомлений с поддержкой умной маршрутизации, анализа вовлеченности пользователей и персонализации уведомлений.

## 🚀 Основные возможности

### ✨ Умная маршрутизация
- Автоматический выбор оптимального канала доставки
- Анализ контекста уведомления
- Учет предпочтений пользователя
- Временная оптимизация отправки

### 📊 Аналитика и метрики
- Комплексные метрики доставки
- Анализ вовлеченности пользователей
- Статистика по типам уведомлений
- Отчеты о качестве доставки

### 🎯 Персонализация
- Адаптация под предпочтения пользователя
- Оптимизация времени отправки
- Умные рекомендации
- Обучение на основе поведения

### 🔧 Управление уведомлениями
- Создание и управление шаблонами
- Планирование отправки
- Валидация и форматирование
- Обработка очереди уведомлений

## 📚 API Reference

### Основные классы

#### `SmartNotificationManagerExtra`
Главный класс менеджера уведомлений.

**Инициализация:**
```python
manager = SmartNotificationManagerExtra()
```

#### `NotificationType` (Enum)
Типы уведомлений:
- `INFO` - информационные
- `WARNING` - предупреждения
- `ERROR` - ошибки
- `SUCCESS` - успешные операции
- `SECURITY` - безопасность

#### `NotificationPriority` (Enum)
Приоритеты уведомлений:
- `LOW` - низкий
- `NORMAL` - обычный
- `HIGH` - высокий
- `CRITICAL` - критический

#### `NotificationChannel` (Enum)
Каналы доставки:
- `PUSH` - push-уведомления
- `EMAIL` - электронная почта
- `SMS` - SMS
- `IN_APP` - внутри приложения

#### `NotificationStatus` (Enum)
Статусы уведомлений:
- `PENDING` - ожидает отправки
- `SENT` - отправлено
- `DELIVERED` - доставлено
- `READ` - прочитано
- `FAILED` - ошибка отправки

### Основные методы

#### Отправка уведомлений

```python
# Отправка уведомления
result = manager.send_notification({
    'id': 'notif_001',
    'type': 'info',
    'title': 'Заголовок',
    'message': 'Текст уведомления',
    'user_id': 'user_123'
})

# Умная маршрутизация
routing = manager.smart_route_notification(notification, user_id)
```

#### Управление пользователями

```python
# Получение предпочтений
preferences = manager.get_user_preferences(user_id)

# Обновление предпочтений
manager.update_user_preferences(user_id, {
    'theme': 'dark',
    'notifications': True,
    'quiet_hours': {'start': 22, 'end': 8}
})

# Оптимизация вовлеченности
optimization = manager.optimize_user_engagement(user_id)
```

#### Шаблоны уведомлений

```python
# Создание шаблона
template = {
    'id': 'welcome_template',
    'name': 'Приветственное уведомление',
    'subject': 'Добро пожаловать!',
    'body': 'Спасибо за регистрацию'
}
manager.create_notification_template(template)

# Получение шаблонов
templates = manager.get_notification_templates()
```

#### Планирование

```python
# Планирование отправки
manager.schedule_notification(notification, '2024-01-01T12:00:00')

# Получение запланированных уведомлений
scheduled = manager.get_scheduled_notifications()

# Отмена уведомления
manager.cancel_notification('scheduled_001')
```

#### Аналитика

```python
# Получение метрик
metrics = manager.get_comprehensive_metrics()

# Статистика уведомлений
stats = manager.get_notification_statistics()

# История уведомлений
history = manager.get_notification_history(user_id)
```

### Private методы

#### Анализ контекста
- `_analyze_notification_context()` - анализ контекста уведомления
- `_assess_urgency()` - оценка срочности
- `_classify_content_type()` - классификация типа контента
- `_assess_time_sensitivity()` - оценка временной чувствительности

#### Маршрутизация
- `_select_optimal_channel()` - выбор оптимального канала
- `_select_optimal_time()` - выбор оптимального времени
- `_generate_routing_recommendations()` - генерация рекомендаций

#### Анализ вовлеченности
- `_analyze_engagement_patterns()` - анализ паттернов вовлеченности
- `_generate_engagement_recommendations()` - генерация рекомендаций

## 🔧 Конфигурация

### Настройки по умолчанию

```python
settings = {
    "max_notifications_per_hour": 100,
    "retry_attempts": 3,
    "timeout_seconds": 30,
    "enable_smart_routing": True,
    "enable_engagement_optimization": True
}
```

### Цветовая схема

```python
color_scheme = {
    "notification_colors": {
        "info": "#3498db",
        "warning": "#f39c12",
        "error": "#e74c3c",
        "success": "#27ae60",
        "security": "#9b59b6"
    }
}
```

## 📊 Метрики

### Основные показатели
- `total_notifications` - общее количество уведомлений
- `delivered_notifications` - доставленные уведомления
- `read_notifications` - прочитанные уведомления
- `failed_notifications` - неудачные отправки

### Расчетные показатели
- `success_rate` - процент успешных доставок
- `delivery_rate` - процент доставки
- `read_rate` - процент прочтения

## 🧪 Тестирование

### Запуск unit тестов

```bash
cd tests
python3 -m pytest test_smart_notification_manager_extra.py -v
```

### Покрытие тестами
- **Всего тестов:** 33
- **Успешных:** 33 (100%)
- **Покрытие методов:** 100%

## 🔍 Логирование

Используется структурированное логирование с помощью `structlog`:

```python
# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## 🚀 Производительность

### Оптимизации
- Кэширование предпочтений пользователей
- Батчевая обработка уведомлений
- Асинхронная отправка
- Умная маршрутизация

### Рекомендации
- Используйте планирование для массовых рассылок
- Настройте лимиты для предотвращения спама
- Регулярно очищайте старые данные
- Мониторьте метрики производительности

## 🔒 Безопасность

### Защита данных
- Шифрование чувствительной информации
- Валидация входных данных
- Защита от инъекций
- Аудит доступа

### Приватность
- Соблюдение GDPR
- Минимизация сбора данных
- Прозрачность обработки
- Право на удаление

## 📈 Мониторинг

### Ключевые метрики
- Время отклика API
- Процент успешных доставок
- Использование ресурсов
- Ошибки и исключения

### Алерты
- Превышение лимитов
- Высокий процент ошибок
- Медленная обработка
- Проблемы с доставкой

## 🤝 Интеграция

### SFM (Safe Function Manager)
Автоматическая регистрация в `data/sfm/function_registry.json`:

```json
{
  "smart_notification_manager_extra": {
    "class": "SmartNotificationManagerExtra",
    "module": "security.ai_agents.smart_notification_manager_extra",
    "methods": [
      "send_notification",
      "smart_route_notification",
      "optimize_user_engagement"
    ]
  }
}
```

### Внешние системы
- Email провайдеры (SMTP, SendGrid, Mailgun)
- Push сервисы (FCM, APNS)
- SMS провайдеры (Twilio, SMS.ru)
- Аналитические системы

## 📝 Примеры использования

### Базовое использование

```python
from smart_notification_manager_extra import SmartNotificationManagerExtra

# Инициализация
manager = SmartNotificationManagerExtra()

# Отправка уведомления
notification = {
    'id': 'welcome_001',
    'type': 'info',
    'title': 'Добро пожаловать!',
    'message': 'Спасибо за регистрацию в нашей системе',
    'user_id': 'user_123'
}

# Отправка
success = manager.send_notification(notification)
if success:
    print("Уведомление отправлено успешно!")
```

### Умная маршрутизация

```python
# Анализ и маршрутизация
routing = manager.smart_route_notification(notification, 'user_123')

print(f"Оптимальный канал: {routing['optimal_channel']}")
print(f"Оптимальное время: {routing['optimal_time']}")
print(f"Уверенность: {routing['confidence']}")

# Рекомендации
for rec in routing['recommendations']:
    print(f"- {rec}")
```

### Оптимизация вовлеченности

```python
# Анализ вовлеченности пользователя
optimization = manager.optimize_user_engagement('user_123')

print(f"Оценка вовлеченности: {optimization['engagement_score']}")
print("Рекомендации:")
for rec in optimization['recommendations']:
    print(f"- {rec}")
```

### Работа с шаблонами

```python
# Создание шаблона
template = {
    'id': 'security_alert',
    'name': 'Предупреждение безопасности',
    'subject': 'Обнаружена подозрительная активность',
    'body': 'В вашем аккаунте обнаружена подозрительная активность. Проверьте безопасность.',
    'priority': 'high',
    'channel': 'email'
}

manager.create_notification_template(template)

# Использование шаблона
notification = manager.format_notification({
    'template_id': 'security_alert',
    'user_id': 'user_123',
    'variables': {
        'username': 'Иван Иванов',
        'timestamp': '2024-01-01 12:00:00'
    }
})
```

## 🐛 Отладка

### Включение отладочного логирования

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Проверка состояния

```python
# Получение статуса
status = await manager.get_status()
print(f"Статус системы: {status}")

# Проверка метрик
metrics = manager.get_comprehensive_metrics()
print(f"Метрики: {metrics}")
```

### Очистка данных

```python
# Очистка истории
manager.clear_notification_history('user_123')

# Сброс статистики
manager.reset_statistics()

# Общая очистка
manager.cleanup()
```

## 📚 Дополнительные ресурсы

- [Документация structlog](https://www.structlog.org/)
- [Руководство по тестированию](tests/test_smart_notification_manager_extra.py)
- [Примеры интеграции](examples/)
- [API Reference](api/)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Добавьте тесты
4. Убедитесь, что все тесты проходят
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

---

**Версия:** 2.4  
**Последнее обновление:** 2024-01-01  
**Автор:** ALADDIN Security Team