# NotificationBot Documentation

## Overview

NotificationBot - это интеллектуальный бот для управления уведомлениями в системе ALADDIN.

## Classes

### NotificationBot

Основной класс для работы с уведомлениями.

#### Methods

##### send_notification

Отправка уведомления пользователю.

**Parameters:**
- request (NotificationRequest): Запрос на отправку уведомления

**Returns:**
- NotificationResponse: Ответ с результатом отправки

**Example:**
```python
bot = NotificationBot("TestBot")
request = NotificationRequest(
    user_id="user123",
    notification_type=NotificationType.SECURITY_ALERT,
    priority=Priority.HIGH,
    title="Security Alert",
    message="Your account has been accessed"
)
response = await bot.send_notification(request)
```

##### send_multiple_notifications

Параллельная отправка множественных уведомлений.

**Parameters:**
- requests (List[NotificationRequest]): Список запросов

**Returns:**
- List[NotificationResponse]: Список ответов

##### get_analytics

Получение аналитики уведомлений.

**Parameters:**
- user_id (str, optional): ID пользователя для фильтрации
- start_date (datetime, optional): Начальная дата
- end_date (datetime, optional): Конечная дата

**Returns:**
- NotificationAnalytics: Аналитика уведомлений

## Enums

### NotificationType

Типы уведомлений:
- SECURITY_ALERT
- SYSTEM_UPDATE
- USER_ACTION
- PROMOTIONAL
- EDUCATIONAL
- EMERGENCY
- REMINDER
- SOCIAL
- NEWS
- TRANSACTION

### Priority

Приоритеты уведомлений:
- LOW
- MEDIUM
- HIGH
- URGENT
- CRITICAL

### DeliveryChannel

Каналы доставки:
- PUSH
- EMAIL
- SMS
- IN_APP
- WEBHOOK
- VOICE
- SLACK
- TELEGRAM
- DISCORD
- WHATSAPP