# 🧠 SFM (SAFE FUNCTION MANAGER) - ЦЕНТРАЛЬНАЯ АРХИТЕКТУРА

**Дата:** 2025-11-26  
**Статус:** ✅ SFM - главный мозг системы безопасности

---

## 🎯 SFM - ГЛАВНЫЙ МОЗГ СИСТЕМЫ

### Что такое SFM?

**SFM (Safe Function Manager)** - это центральный оркестратор всей системы безопасности, который:
- ✅ **Управляет всеми 138+ функциями** защиты
- ✅ **Регистрирует все компоненты** (AI Agents, Bots, Managers)
- ✅ **Контролирует выполнение** всех функций
- ✅ **Управляет зависимостями** между функциями
- ✅ **Обеспечивает безопасное выполнение**

**Файлы:**
- ✅ `safe_function_manager.py` (212 KB) - основной код
- ✅ `function_registry.json` (33,268 строк) - каталог всех функций

---

## 📊 ПРАВИЛЬНАЯ СХЕМА С SFM В ЦЕНТРЕ

```
┌─────────────────────────────────────────────────────────────────┐
│  📱 ALADDIN iOS App                                              │
│  ├── APIService.swift (58 методов)                              │
│  └── NetworkManager.swift (SSL Pinning)                         │
└─────────────────────────────────────────────────────────────────┘
         │
         │ HTTPS (443)
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  🌐 Nginx → 🚪 API Gateway (8001)                               │
│  ├── Rate Limiting ✅                                            │
│  ├── Authentication ✅                                          │
│  └── Routing ✅                                                  │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Все запросы проходят через API Gateway
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  🧠 SFM (Safe Function Manager) ⭐ ЦЕНТР СИСТЕМЫ               │
│  ├── safe_function_manager.py (212 KB)                          │
│  ├── function_registry.json (33,268 строк)                      │
│  │                                                               │
│  │ МЕТОДЫ УПРАВЛЕНИЯ:                                            │
│  ├── register_function() - регистрация функций                │
│  ├── execute_function() - выполнение функций                    │
│  ├── execute_function_async() - асинхронное выполнение          │
│  ├── register_function_handler() - регистрация обработчиков     │
│  ├── unregister_function() - удаление функций                  │
│  └── register_function_with_sleep() - регистрация с sleep mode  │
│  │                                                               │
│  │ УПРАВЛЯЕТ ВСЕМИ КОМПОНЕНТАМИ:                                 │
│  │                                                               │
│  ├─→ 🤖 AI AGENTS (76 файлов)                                   │
│  │   ├── Регистрация: register_function("self_harm_detection") │
│  │   ├── Выполнение: execute_function("self_harm_detection")    │
│  │   ├── Зависимости: проверка через function_registry.json     │
│  │   └── Sleep Mode: управление через sleep_mode_manager        │
│  │                                                               │
│  ├─→ 🤖 BOTS (22 файла)                                         │
│  │   ├── Регистрация: register_function("telegram_security")  │
│  │   ├── Выполнение: execute_function("telegram_security")     │
│  │   ├── Зависимости: проверка через function_registry.json     │
│  │   └── Sleep Mode: управление через sleep_mode_manager        │
│  │                                                               │
│  ├─→ 🛡️ MANAGERS (24 файла)                                     │
│  │   ├── Регистрация: register_function("subscription_manager")│
│  │   ├── Выполнение: execute_function("subscription_manager")  │
│  │   ├── Зависимости: проверка через function_registry.json     │
│  │   └── Sleep Mode: управление через sleep_mode_manager        │
│  │                                                               │
│  ├─→ 🔧 MICROSERVICES (17 файлов)                               │
│  │   ├── Регистрация: register_service_in_mesh()               │
│  │   ├── Выполнение: через service mesh                         │
│  │   └── Управление: через service_mesh_manager                 │
│  │                                                               │
│  ├─→ ⚡ ACTIVE MODULES (7 файлов)                               │
│  ├─→ 👨‍👩‍👧 FAMILY MODULES (18 файлов)                            │
│  ├─→ 🛡️ ANTIVIRUS (7 файлов)                                    │
│  ├─→ 🔐 VPN (20 файлов)                                         │
│  ├─→ 📋 COMPLIANCE (3 файла)                                    │
│  ├─→ 🎯 ORCHESTRATION (1 файл)                                  │
│  ├─→ 🔧 CORE (1 файл)                                           │
│  └─→ 🛡️ КРИТИЧНЫЕ МОДУЛИ (20 файлов)                            │
│                                                                  │
│  ВСЕ КОМПОНЕНТЫ РАБОТАЮТ ЧЕРЕЗ SFM! ⭐                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 КАК МОБИЛЬНОЕ ПРИЛОЖЕНИЕ ВЗАИМОДЕЙСТВУЕТ С SFM

### Прямое взаимодействие:

#### 1. Через API Gateway → SFM API:
- `/api/sfm/functions` → Получить список всех функций из SFM
- `/api/sfm/function-status` → Получить статус функции из SFM
- `/api/sfm/execute` → Выполнить функцию через SFM

### Косвенное взаимодействие (через компоненты):

#### 2. Через API Gateway → Компонент → SFM:

**Пример 1: Запрос защиты от угроз**
```
📱 iOS App
   │
   │ APIService.getTopThreats()
   │
   ▼
🌐 Nginx → 🚪 API Gateway
   │
   │ /api/analytics/top-threats
   │
   ▼
🤖 AI Agents Service
   │
   │ Запрос на выполнение threat_intelligence_agent
   │
   ▼
🧠 SFM ⭐ (ЦЕНТР)
   │
   │ 1. Проверка function_registry.json
   │    ├── Функция: "threat_intelligence_agent"
   │    ├── Статус: "active"
   │    ├── Зависимости: ["threat_detection_agent"]
   │    └── Политики: {...}
   │
   │ 2. Валидация функции
   │    ├── Функция зарегистрирована? ✅
   │    ├── Зависимости доступны? ✅
   │    └── Sleep mode? Проверка
   │
   │ 3. Выполнение через SFM
   │    ├── execute_function("threat_intelligence_agent")
   │    ├── Регистрация вызова
   │    ├── Логирование
   │    └── Мониторинг
   │
   ▼
threat_intelligence_agent.py
   │
   │ Выполнение анализа угроз
   │
   ▼
Response
   │
   ▼
📱 iOS App
```

**Пример 2: Запрос защиты семьи (ML система)**
```
📱 iOS App
   │
   │ APIService.getProtectionSettings()
   │
   ▼
🌐 Nginx → 🚪 API Gateway
   │
   │ /api/protection/settings
   │
   ▼
🤖 AI Agents Service
   │
   │ Запрос на выполнение self_harm_detection_agent ⭐
   │
   ▼
🧠 SFM ⭐ (ЦЕНТР)
   │
   │ 1. Проверка function_registry.json
   │    ├── Функция: "self_harm_detection_agent"
   │    ├── Тип: "ai_agent"
   │    ├── ML система: ✅
   │    ├── Зависимости: ["natural_language_processor"]
   │    └── Политики: {...}
   │
   │ 2. Валидация
   │    ├── Функция зарегистрирована? ✅
   │    ├── Зависимости доступны? ✅
   │    └── Sleep mode? Проверка через sleep_mode_manager
   │
   │ 3. Выполнение через SFM
   │    ├── execute_function("self_harm_detection_agent")
   │    ├── Загрузка ML модели
   │    ├── Выполнение анализа
   │    └── Возврат результата
   │
   ▼
self_harm_detection_agent.py ⭐
   │
   │ ML анализ на самоповреждение
   │
   ▼
Response
   │
   ▼
📱 iOS App
```

---

## 📊 FUNCTION_REGISTRY.JSON - КАТАЛОГ ВСЕХ ФУНКЦИЙ

### Структура:

**function_registry.json** содержит:
- ✅ **138+ функций** защиты
- ✅ **Зависимости** между функциями
- ✅ **Политики** выполнения
- ✅ **Параметры** функций
- ✅ **Статусы** функций (active/sleep)
- ✅ **ML модели** для AI Agents

### Пример записи для ML системы:

```json
{
  "functions": [
    {
      "name": "self_harm_detection_agent",
      "type": "ai_agent",
      "category": "ml_system",
      "status": "active",
      "dependencies": [
        "natural_language_processor",
        "threat_detection_agent"
      ],
      "parameters": {
        "model": "bert-base",
        "threshold": 0.8
      },
      "policies": {
        "requires_auth": true,
        "rate_limit": 100
      }
    },
    {
      "name": "telegram_security_bot",
      "type": "bot",
      "status": "active",
      "dependencies": [
        "notification_bot",
        "analytics_manager"
      ],
      "parameters": {...},
      "policies": {...}
    }
  ]
}
```

---

## 🔄 ПОЛНЫЙ ПОТОК С SFM В ЦЕНТРЕ

### Схема выполнения функции:

```
📱 iOS App
   │
   │ APIService.getTopThreats()
   │
   ▼
🌐 Nginx → 🚪 API Gateway
   │
   │ /api/analytics/top-threats
   │
   ▼
🤖 AI Agents Service
   │
   │ Запрос: выполнить threat_intelligence_agent
   │
   ▼
🧠 SFM ⭐ (ЦЕНТР СИСТЕМЫ)
   │
   │ ШАГ 1: Проверка function_registry.json
   │    ├── Функция существует? ✅
   │    ├── Статус: active/sleep? ✅
   │    └── Параметры: корректны? ✅
   │
   │ ШАГ 2: Проверка зависимостей
   │    ├── natural_language_processor доступен? ✅
   │    ├── threat_detection_agent доступен? ✅
   │    └── Все зависимости готовы? ✅
   │
   │ ШАГ 3: Проверка Sleep Mode
   │    ├── Функция в sleep mode? Проверка
   │    ├── Нужно пробудить? Решение
   │    └── Можно выполнить? ✅
   │
   │ ШАГ 4: Выполнение через SFM
   │    ├── execute_function("threat_intelligence_agent")
   │    ├── Регистрация вызова в логах
   │    ├── Мониторинг производительности
   │    └── Обработка ошибок
   │
   │ ШАГ 5: Вызов обработчика
   │    ├── Получение handler из registry
   │    ├── Вызов handler(params)
   │    └── Ожидание результата
   │
   ▼
threat_intelligence_agent.py
   │
   │ Выполнение анализа угроз
   │ Использование ML моделей
   │ Анализ данных
   │
   ▼
Response
   │
   │ Результат анализа
   │
   ▼
🧠 SFM ⭐
   │
   │ Обработка результата
   │ Логирование
   │ Обновление метрик
   │
   ▼
📱 iOS App
   │
   │ Отображение угроз
   │
   ✅
```

---

## 🎯 SFM УПРАВЛЯЕТ ВСЕМИ КОМПОНЕНТАМИ

### Что делает SFM для каждого компонента:

#### 1. 🤖 AI AGENTS (76 файлов):

**Регистрация:**
```python
SFM.register_function(
    function_id="self_harm_detection_agent",
    handler=self_harm_detection_agent.analyze,
    dependencies=["natural_language_processor"],
    policies={...}
)
```

**Выполнение:**
```python
result = SFM.execute_function(
    function_id="self_harm_detection_agent",
    params={"text": "...", "user_id": "..."}
)
```

#### 2. 🤖 BOTS (22 файла):

**Регистрация:**
```python
SFM.register_function(
    function_id="telegram_security_bot",
    handler=telegram_security_bot.process_message,
    dependencies=["notification_bot"],
    policies={...}
)
```

**Выполнение:**
```python
result = SFM.execute_function(
    function_id="telegram_security_bot",
    params={"message": "...", "chat_id": "..."}
)
```

#### 3. 🛡️ MANAGERS (24 файла):

**Регистрация:**
```python
SFM.register_function(
    function_id="subscription_manager",
    handler=subscription_manager.get_tariffs,
    dependencies=[],
    policies={...}
)
```

**Выполнение:**
```python
result = SFM.execute_function(
    function_id="subscription_manager",
    params={"user_id": "..."}
)
```

---

## 📊 СТАТИСТИКА SFM

### На сервере:
- ✅ **safe_function_manager.py:** 212 KB
- ✅ **function_registry.json:** 33,268 строк
- ✅ **Всего функций:** 138+
- ✅ **Управляет:** ~220 файлами компонентов

### Компоненты под управлением SFM:
- ✅ **AI Agents:** 76 файлов
- ✅ **Bots:** 22 файла
- ✅ **Managers:** 24 файла
- ✅ **Microservices:** 17 файлов
- ✅ **Active Modules:** 7 файлов
- ✅ **Family Modules:** 18 файлов
- ✅ **Antivirus:** 7 файлов
- ✅ **VPN:** ~20 файлов
- ✅ **Compliance:** 3 файла
- ✅ **Orchestration:** 1 файл
- ✅ **Core:** 1 файл
- ✅ **Критичные модули:** ~20 файлов

**ИТОГО:** ~220 файлов под управлением SFM

---

## ✅ ИТОГОВАЯ СХЕМА С SFM В ЦЕНТРЕ

```
📱 iOS App (58 API endpoints)
   │
   │ HTTPS (443)
   │
   ▼
🌐 Nginx → 🚪 API Gateway (8001)
   │
   │ Все запросы
   │
   ▼
🧠 SFM ⭐ (ЦЕНТР СИСТЕМЫ)
   │
   │ safe_function_manager.py
   │ function_registry.json (33,268 строк)
   │
   │ УПРАВЛЯЕТ ВСЕМИ КОМПОНЕНТАМИ:
   │
   ├─→ 🤖 AI AGENTS (76) → через SFM.execute_function()
   ├─→ 🤖 BOTS (22) → через SFM.execute_function()
   ├─→ 🛡️ MANAGERS (24) → через SFM.execute_function()
   ├─→ 🔧 MICROSERVICES (17) → через SFM.register_service_in_mesh()
   ├─→ ⚡ ACTIVE MODULES (7) → через SFM.execute_function()
   ├─→ 👨‍👩‍👧 FAMILY MODULES (18) → через SFM.execute_function()
   ├─→ 🛡️ ANTIVIRUS (7) → через SFM.execute_function()
   ├─→ 🔐 VPN (20) → через SFM.execute_function()
   ├─→ 📋 COMPLIANCE (3) → через SFM.execute_function()
   ├─→ 🎯 ORCHESTRATION (1) → через SFM.execute_function()
   ├─→ 🔧 CORE (1) → через SFM.execute_function()
   └─→ 🛡️ КРИТИЧНЫЕ МОДУЛИ (20) → через SFM.execute_function()
```

---

## ✅ ВЫВОД

**SFM - это центральный мозг системы!** 🧠

**Все компоненты:**
- ✅ Регистрируются в SFM через `register_function()`
- ✅ Выполняются через SFM через `execute_function()`
- ✅ Управляются SFM через `function_registry.json`
- ✅ Контролируются SFM через политики и зависимости

**Мобильное приложение:**
- ✅ Взаимодействует с компонентами через SFM
- ✅ Все запросы проходят через SFM
- ✅ SFM управляет всей логикой выполнения

**SFM - главный оркестратор всей системы безопасности!** 🎯

