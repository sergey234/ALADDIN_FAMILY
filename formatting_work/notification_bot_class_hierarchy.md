# Иерархия классов notification_bot.py

## Основные классы

### 1. Enum классы (Перечисления)
- **NotificationType(Enum)** - типы уведомлений
- **Priority(Enum)** - приоритеты уведомлений  
- **DeliveryChannel(Enum)** - каналы доставки
- **NotificationStatus(Enum)** - статусы уведомлений

### 2. SQLAlchemy модели (База данных)
- **UserPreference(Base)** - предпочтения пользователя
- **Notification(Base)** - уведомление
- **NotificationTemplate(Base)** - шаблон уведомления

### 3. Pydantic модели (Валидация данных)
- **NotificationRequest(BaseModel)** - запрос на отправку уведомления
- **NotificationResponse(BaseModel)** - ответ на отправку уведомления
- **NotificationAnalytics(BaseModel)** - аналитика уведомлений

### 4. Основной класс
- **NotificationBot(SecurityBase)** - главный класс бота уведомлений

## Наследование

```
Enum
├── NotificationType
├── Priority
├── DeliveryChannel
└── NotificationStatus

Base (SQLAlchemy)
├── UserPreference
├── Notification
└── NotificationTemplate

BaseModel (Pydantic)
├── NotificationRequest
├── NotificationResponse
└── NotificationAnalytics

SecurityBase
└── NotificationBot
```

## Полиморфизм

- **Enum классы** - обеспечивают типобезопасность для констант
- **SQLAlchemy модели** - обеспечивают ORM функциональность
- **Pydantic модели** - обеспечивают валидацию и сериализацию данных
- **NotificationBot** - основной функциональный класс с полиморфными методами