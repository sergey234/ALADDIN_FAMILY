# 🚀 **UNIFIED SUPPORT API - ЕДИНЫЙ API ПОДДЕРЖКИ**

**Эксперт:** API Design + System Integration  
**Дата:** 2025-01-27  
**Статус:** 📋 ДОКУМЕНТАЦИЯ УНИФИЦИРОВАННОГО API

---

## 🎯 **ОБЗОР СИСТЕМЫ:**

### **📋 ЧТО ОБЪЕДИНЯЕТ:**
- **Super AI Support Assistant** - основные функции поддержки
- **Psychological Support Agent** - психологическая поддержка и кризисные протоколы
- **User Support System** - техническая поддержка и диагностика

### **🔗 ЕДИНЫЙ API:**
- **Один интерфейс** для всех типов поддержки
- **Автоматическая маршрутизация** запросов
- **Умная эскалация** по уровням сложности
- **Кризисное обнаружение** и немедленная реакция

---

## 📱 **ПОДДЕРЖИВАЕМЫЕ ПЛАТФОРМЫ:**

### **🍎 iOS (Swift):**
- **Файл:** `UnifiedSupportAPI.swift`
- **Фреймворк:** Combine + URLSession
- **Минимальная версия:** iOS 14.0+
- **Архитектура:** MVVM + Reactive Programming

### **🤖 Android (Kotlin):**
- **Файл:** `UnifiedSupportAPI.kt`
- **Фреймворк:** Coroutines + HttpURLConnection
- **Минимальная версия:** Android API 21+
- **Архитектура:** MVVM + Coroutines

---

## 🎯 **ОСНОВНЫЕ КОМПОНЕНТЫ:**

### **1. 📊 КАТЕГОРИИ ПОДДЕРЖКИ (24 категории):**

#### **🔒 Безопасность:**
- `CYBERSECURITY` - Кибербезопасность
- `DEVICE_SECURITY` - Безопасность устройств
- `PARENTAL_CONTROL` - Родительский контроль

#### **👨‍👩‍👧‍👦 Семья:**
- `FAMILY_SUPPORT` - Семейная поддержка
- `PSYCHOLOGY` - Психологическая поддержка
- `EDUCATION` - Образование

#### **💻 Технологии:**
- `TECHNOLOGY` - Общие технологии
- `VPN_SUPPORT` - Поддержка VPN
- `ACCOUNT_MANAGEMENT` - Управление аккаунтом

#### **💰 Финансы:**
- `FINANCE` - Финансовые вопросы
- `PAYMENT_ISSUES` - Проблемы с платежами

#### **🏥 Здоровье:**
- `MEDICAL_SUPPORT` - Медицинская поддержка
- `HEALTH` - Здоровье
- `FITNESS` - Фитнес

#### **🏠 Дом и быт:**
- `HOUSEHOLD` - Домашние дела
- `COOKING` - Кулинария
- `GARDENING` - Садоводство
- `REPAIR` - Ремонт

#### **🎯 Другие:**
- `LEGAL` - Юридические вопросы
- `TRAVEL` - Путешествия
- `ENTERTAINMENT` - Развлечения
- `RELATIONSHIPS` - Отношения
- `CAREER` - Карьера
- `BUSINESS` - Бизнес
- `SHOPPING` - Покупки

---

### **2. 😊 ТИПЫ ЭМОЦИЙ (13 типов):**

#### **😊 Положительные:**
- `HAPPY` - Счастливый
- `EXCITED` - Взволнованный
- `CALM` - Спокойный

#### **😢 Негативные:**
- `SAD` - Грустный
- `ANGRY` - Злой
- `FEARFUL` - Испуганный
- `STRESSED` - Стресс
- `ANXIOUS` - Тревожный
- `LONELY` - Одинокий

#### **🤔 Нейтральные:**
- `NEUTRAL` - Нейтральный
- `SURPRISED` - Удивленный
- `DISGUSTED` - Отвращение
- `CONFUSED` - Запутанный

---

### **3. ⚡ УРОВНИ ПРИОРИТЕТА (6 уровней):**

- `CRITICAL` - Критический
- `HIGH` - Высокий
- `MEDIUM` - Средний
- `LOW` - Низкий
- `EMERGENCY` - Экстренный
- `URGENT` - Срочный

---

### **4. 📊 СТАТУСЫ ПОДДЕРЖКИ (8 статусов):**

- `PENDING` - Ожидает
- `IN_PROGRESS` - В процессе
- `RESOLVED` - Решен
- `ESCALATED` - Эскалирован
- `CANCELLED` - Отменен
- `CRISIS_ACTIVE` - Кризис активен
- `TECHNICAL_REVIEW` - Технический обзор
- `AWAITING_USER` - Ожидает пользователя

---

### **5. 👶 ВОЗРАСТНЫЕ ГРУППЫ (5 групп):**

- `CHILD_3_6` - Дети 3-6 лет
- `CHILD_7_12` - Дети 7-12 лет
- `TEEN_13_17` - Подростки 13-17 лет
- `ADULT_18_65` - Взрослые 18-65 лет
- `ELDERLY_65_PLUS` - Пожилые 65+ лет

---

### **6. 🎯 ТИПЫ ПОДДЕРЖКИ (9 типов):**

- `EMOTIONAL` - Эмоциональная
- `BEHAVIORAL` - Поведенческая
- `EDUCATIONAL` - Образовательная
- `SOCIAL` - Социальная
- `CRISIS` - Кризисная
- `TECHNICAL` - Техническая
- `FUNCTIONAL` - Функциональная
- `BILLING` - Биллинг
- `SECURITY` - Безопасность

---

### **7. 🚨 ТИПЫ КРИЗИСОВ (7 типов):**

- `SUICIDAL_IDEATION` - Суицидальные мысли
- `SEVERE_DEPRESSION` - Тяжелая депрессия
- `ANXIETY_ATTACK` - Паническая атака
- `EMOTIONAL_DISTRESS` - Эмоциональное расстройство
- `FAMILY_CRISIS` - Семейный кризис
- `CHILD_ABUSE` - Насилие над детьми
- `ELDERLY_ABUSE` - Насилие над пожилыми

---

## 🔧 **API ENDPOINTS:**

### **👤 УПРАВЛЕНИЕ ПРОФИЛЯМИ:**

#### **POST /profile/create**
Создание профиля пользователя
```json
{
  "user_id": "user123",
  "name": "Иван Иванов",
  "age": 30,
  "preferences": {
    "language": "ru",
    "notifications": "true"
  }
}
```

#### **GET /profile/{userId}**
Получение профиля пользователя

#### **PUT /profile/{userId}/update**
Обновление профиля пользователя

---

### **😊 АНАЛИЗ ЭМОЦИЙ:**

#### **POST /emotion/analyze**
Анализ эмоций в тексте
```json
{
  "text": "Мне очень грустно и я не знаю что делать",
  "user_id": "user123"
}
```

**Ответ:**
```json
{
  "emotion": "sad",
  "confidence": 0.85,
  "intensity": 0.8,
  "triggers": ["грустно", "не знаю"],
  "risk_level": "high",
  "crisis_indicators": ["severe_depression"],
  "recommendations": [
    "Попробуйте заняться любимым делом",
    "Свяжитесь с близкими людьми",
    "Рекомендуется консультация психолога"
  ],
  "timestamp": "2025-01-27T10:30:00Z"
}
```

---

### **📝 ЗАПРОСЫ ПОДДЕРЖКИ:**

#### **POST /request/create**
Создание запроса поддержки
```json
{
  "user_id": "user123",
  "category": "cybersecurity",
  "description": "Мой VPN не подключается",
  "priority": "high"
}
```

#### **GET /request/{requestId}**
Получение запроса поддержки

#### **PUT /request/{requestId}/update**
Обновление запроса поддержки

#### **GET /request/user/{userId}**
Получение всех запросов пользователя

---

### **🚨 КРИЗИСНАЯ ПОДДЕРЖКА:**

#### **POST /crisis/emergency**
Экстренная поддержка
```json
{
  "user_id": "user123",
  "crisis_type": "severe_depression"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Сейчас с вами свяжется специалист",
  "crisis_type": "severe_depression",
  "immediate_actions": [
    "Связаться с психологом",
    "Уведомить семью",
    "Предложить экстренную поддержку"
  ],
  "support_actions": [
    "Предоставить эмоциональную поддержку",
    "Направить к специалисту",
    "Мониторить состояние"
  ],
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### **GET /crisis/alerts/{userId}**
Получение кризисных алертов пользователя

---

### **🔧 ТЕХНИЧЕСКАЯ ПОДДЕРЖКА:**

#### **POST /technical/ticket/create**
Создание технического тикета
```json
{
  "user_id": "user123",
  "issue_type": "vpn_connection",
  "description": "VPN не подключается к серверу",
  "device_info": {
    "os": "iOS 17.0",
    "device": "iPhone 15 Pro",
    "app_version": "2.0.1"
  }
}
```

#### **GET /technical/ticket/{ticketId}**
Получение технического тикета

#### **GET /technical/tickets/{userId}**
Получение всех технических тикетов пользователя

---

### **📊 МЕТРИКИ И АНАЛИТИКА:**

#### **GET /metrics**
Получение метрик поддержки

**Ответ:**
```json
{
  "total_requests": 1500,
  "resolved_requests": 1425,
  "avg_resolution_time": 2.5,
  "satisfaction_score": 4.8,
  "automation_rate": 0.95,
  "escalation_rate": 0.05,
  "crisis_interventions": 25,
  "psychological_sessions": 300,
  "emotional_analysis_count": 5000,
  "crisis_resolution_rate": 0.96,
  "technical_tickets": 800,
  "technical_resolution_rate": 0.94,
  "avg_technical_resolution_time": 1.8,
  "escalation_to_experts": 15,
  "language_distribution": {
    "ru": 1200,
    "en": 300
  },
  "category_distribution": {
    "cybersecurity": 400,
    "family_support": 300,
    "technology": 200
  },
  "age_group_distribution": {
    "adult_18_65": 1000,
    "teen_13_17": 300,
    "elderly_65_plus": 200
  },
  "support_type_distribution": {
    "technical": 600,
    "emotional": 400,
    "functional": 300
  },
  "learning_improvements": 50,
  "feedback_integrations": 200
}
```

#### **GET /status**
Получение статуса системы

---

## 🔐 **АУТЕНТИФИКАЦИЯ:**

### **📋 ТРЕБОВАНИЯ:**
- **Bearer Token** в заголовке Authorization
- **Content-Type: application/json**
- **HTTPS** обязательно

### **🔑 ПРИМЕР ЗАГОЛОВКОВ:**
```
Authorization: Bearer your_auth_token_here
Content-Type: application/json
User-Agent: ALADDIN-Mobile/2.0
```

---

## ⚡ **ОБРАБОТКА ОШИБОК:**

### **📊 КОДЫ ОТВЕТОВ:**
- **200** - Успешно
- **201** - Создано
- **400** - Неверный запрос
- **401** - Не авторизован
- **403** - Доступ запрещен
- **404** - Не найдено
- **429** - Слишком много запросов
- **500** - Внутренняя ошибка сервера

### **🚨 ОБРАБОТКА ОШИБОК В iOS:**
```swift
apiClient.createSupportRequest(...)
    .sink(
        receiveCompletion: { completion in
            if case .failure(let error) = completion {
                switch error {
                case APIError.invalidURL:
                    // Обработка неверного URL
                case APIError.networkError(let networkError):
                    // Обработка сетевой ошибки
                case APIError.serverError(let code):
                    // Обработка ошибки сервера
                default:
                    // Обработка других ошибок
                }
            }
        },
        receiveValue: { response in
            // Обработка успешного ответа
        }
    )
    .store(in: &cancellables)
```

### **🚨 ОБРАБОТКА ОШИБОК В Android:**
```kotlin
apiClient.createSupportRequest(...)
    .onSuccess { request ->
        // Обработка успешного ответа
    }
    .onFailure { error ->
        when (error) {
            is APIException -> {
                // Обработка API ошибки
            }
            is IOException -> {
                // Обработка сетевой ошибки
            }
            else -> {
                // Обработка других ошибок
            }
        }
    }
```

---

## 🎯 **ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:**

### **🍎 iOS (Swift):**
```swift
// Создание менеджера поддержки
let supportManager = SupportManager()

// Создание профиля пользователя
supportManager.createUserProfile(
    userId: "user123",
    name: "Иван Иванов",
    age: 30
)

// Анализ эмоций
supportManager.analyzeEmotion(
    text: "Мне очень грустно",
    userId: "user123"
)

// Создание запроса поддержки
supportManager.createSupportRequest(
    userId: "user123",
    category: .cybersecurity,
    description: "VPN не подключается",
    priority: .high
)

// Экстренная поддержка
supportManager.provideEmergencySupport(
    userId: "user123",
    crisisType: .severeDepression
)
```

### **🤖 Android (Kotlin):**
```kotlin
// Создание менеджера поддержки
val supportManager = SupportManager()

// Создание профиля пользователя
supportManager.createUserProfile("user123", "Иван Иванов", 30)

// Анализ эмоций
supportManager.analyzeEmotion("Мне очень грустно", "user123")

// Создание запроса поддержки
supportManager.createSupportRequest(
    userId = "user123",
    category = SupportCategory.CYBERSECURITY,
    description = "VPN не подключается",
    priority = PriorityLevel.HIGH
)

// Экстренная поддержка
supportManager.provideEmergencySupport(
    userId = "user123",
    crisisType = CrisisType.SEVERE_DEPRESSION
)
```

---

## 🚀 **ПРЕИМУЩЕСТВА УНИФИЦИРОВАННОГО API:**

### **✅ ЕДИНЫЙ ИНТЕРФЕЙС:**
- **Один API** для всех типов поддержки
- **Консистентность** между платформами
- **Простота интеграции** в мобильные приложения

### **✅ УМНАЯ МАРШРУТИЗАЦИЯ:**
- **Автоматическое определение** типа поддержки
- **Эскалация** по уровням сложности
- **Кризисное обнаружение** и немедленная реакция

### **✅ АДАПТИВНОСТЬ:**
- **Возрастные группы** - адаптация под возраст
- **Эмоциональный анализ** - понимание состояния пользователя
- **Персонализация** - индивидуальный подход

### **✅ БЕЗОПАСНОСТЬ:**
- **HTTPS** шифрование
- **Bearer Token** аутентификация
- **Валидация** всех входных данных

### **✅ ПРОИЗВОДИТЕЛЬНОСТЬ:**
- **Асинхронные запросы** - не блокируют UI
- **Кэширование** - быстрые ответы
- **Оптимизация** - минимальный трафик

---

## 🎯 **ЗАКЛЮЧЕНИЕ:**

Unified Support API - это мощный инструмент для интеграции всех типов поддержки в мобильные приложения ALADDIN. Он объединяет AI-помощника, психологическую поддержку и техническую поддержку в единый, простой в использовании интерфейс.

**Цель: 100% удовлетворенность пользователей через умную, адаптивную поддержку! 🚀**

