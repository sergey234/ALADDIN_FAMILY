# 🧠 SFM (SAFE FUNCTION MANAGER) - ЦЕНТРАЛЬНАЯ АРХИТЕКТУРА

**Дата:** 2025-11-26  
**Статус:** ✅ SFM - главный мозг системы безопасности

---

## 🎯 SFM - ГЛАВНЫЙ МОЗГ СИСТЕМЫ

### Что такое SFM?

**SFM (Safe Function Manager)** - это центральный оркестратор всей системы безопасности, который:
- ✅ Управляет всеми 138+ функциями защиты
- ✅ Регистрирует все AI Agents, Bots, Managers
- ✅ Контролирует выполнение функций
- ✅ Управляет зависимостями между функциями
- ✅ Обеспечивает безопасное выполнение

---

## 📊 SFM В ЦЕНТРЕ АРХИТЕКТУРЫ

### Правильная схема с SFM:

```
┌─────────────────────────────────────────────────────────────────┐
│  📱 ALADDIN iOS App                                              │
│  ├── APIService.swift (58 методов)                              │
│  └── NetworkManager.swift                                        │
└─────────────────────────────────────────────────────────────────┘
         │
         │ HTTPS (443)
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  🌐 Nginx → 🚪 API Gateway (8001)                               │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Все запросы проходят через API Gateway
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  🧠 SFM (Safe Function Manager) ⭐                               │
│  ├── safe_function_manager.py (212 KB)                          │
│  ├── function_registry.json (33,268 строк)                      │
│  │                                                               │
│  │ УПРАВЛЯЕТ ВСЕМИ КОМПОНЕНТАМИ:                                 │
│  │                                                               │
│  ├─→ 🤖 AI AGENTS (76 файлов)                                   │
│  │   ├── Регистрация всех агентов                              │
│  │   ├── Управление выполнением                                 │
│  │   └── Контроль зависимостей                                  │
│  │                                                               │
│  ├─→ 🤖 BOTS (22 файла)                                         │
│  │   ├── Регистрация всех ботов                                 │
│  │   ├── Управление выполнением                                 │
│  │   └── Контроль зависимостей                                  │
│  │                                                               │
│  ├─→ 🛡️ MANAGERS (24 файла)                                     │
│  │   ├── Регистрация всех менеджеров                            │
│  │   ├── Управление выполнением                                 │
│  │   └── Контроль зависимостей                                   │
│  │                                                               │
│  ├─→ 🔧 MICROSERVICES (17 файлов)                               │
│  │   ├── Регистрация всех сервисов                              │
│  │   ├── Управление выполнением                                 │
│  │   └── Контроль зависимостей                                  │
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
│  ФУНКЦИИ:                                                        │
│  ├── register_function() - регистрация функций                │
│  ├── execute_function() - выполнение функций                    │
│  ├── call_function() - вызов функций                           │
│  ├── validate_function() - валидация функций                    │
│  └── manage_dependencies() - управление зависимостями           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 КАК МОБИЛЬНОЕ ПРИЛОЖЕНИЕ ВЗАИМОДЕЙСТВУЕТ С SFM

### Прямое взаимодействие:

#### 1. Через API Gateway → SFM API:
- `/api/sfm/functions` → Получить список всех функций
- `/api/sfm/function-status` → Получить статус функции
- `/api/sfm/execute` → Выполнить функцию через SFM

### Косвенное взаимодействие:

#### 2. Через API Gateway → Компонент → SFM:

**Пример 1: Запрос защиты от угроз**
```
iOS App
   │
   │ APIService.getTopThreats()
   │
   ▼
API Gateway
   │
   │ /api/analytics/top-threats
   │
   ▼
AI Agents Service
   │
   │ Вызов threat_intelligence_agent.py
   │
   ▼
SFM ⭐
   │
   │ execute_function("threat_intelligence_agent")
   │ Проверка function_registry.json
   │ Управление зависимостями
   │
   ▼
threat_intelligence_agent.py
   │
   │ Выполнение анализа
   │
   ▼
Response → iOS App
```

**Пример 2: Запрос защиты семьи**
```
iOS App
   │
   │ APIService.getProtectionSettings()
   │
   ▼
API Gateway
   │
   │ /api/protection/settings
   │
   ▼
AI Agents Service
   │
   │ Вызов self_harm_detection_agent.py ⭐
   │
   ▼
SFM ⭐
   │
   │ execute_function("self_harm_detection_agent")
   │ Проверка function_registry.json
   │ Управление зависимостями
   │ Проверка sleep mode
   │
   ▼
self_harm_detection_agent.py ⭐
   │
   │ Выполнение анализа
   │
   ▼
Response → iOS App
```

---

## 📊 FUNCTION_REGISTRY.JSON

### Структура:

**function_registry.json** содержит:
- ✅ **138+ функций** защиты
- ✅ **Зависимости** между функциями
- ✅ **Политики** выполнения
- ✅ **Параметры** функций
- ✅ **Статусы** функций (active/sleep)

### Пример записи:

```json
{
  "functions": [
    {
      "name": "self_harm_detection_agent",
      "type": "ai_agent",
      "status": "active",
      "dependencies": ["natural_language_processor", "threat_detection_agent"],
      "parameters": {...},
      "policies": {...}
    },
    {
      "name": "telegram_security_bot",
      "type": "bot",
      "status": "active",
      "dependencies": ["notification_bot", "analytics_manager"],
      "parameters": {...},
      "policies": {...}
    }
  ]
}
```

---

## 🔄 ПОЛНЫЙ ПОТОК С SFM В ЦЕНТРЕ

### Схема с SFM:

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
🧠 SFM ⭐ (ЦЕНТР СИСТЕМЫ)
   │
   │ 1. Проверка function_registry.json
   │ 2. Валидация функции
   │ 3. Проверка зависимостей
   │ 4. Проверка sleep mode
   │ 5. Выполнение execute_function()
   │
   ├─→ Проверяет зависимости
   │   ├── natural_language_processor ✅
   │   └── threat_detection_agent ✅
   │
   ├─→ Управляет выполнением
   │   ├── Регистрация вызова
   │   ├── Логирование
   │   └── Мониторинг
   │
   └─→ Выполняет функцию
       │
       ▼
   threat_intelligence_agent.py
       │
       │ Анализ угроз
       │
       ▼
   Response
       │
       ▼
   📱 iOS App
```

---

## 🎯 SFM УПРАВЛЯЕТ ВСЕМ

### Что делает SFM:

1. **Регистрация функций** ✅
   - Все AI Agents регистрируются в SFM
   - Все Bots регистрируются в SFM
   - Все Managers регистрируются в SFM

2. **Управление выполнением** ✅
   - SFM контролирует выполнение всех функций
   - Проверяет права доступа
   - Управляет ресурсами

3. **Управление зависимостями** ✅
   - SFM знает, какие функции зависят от других
   - Управляет порядком выполнения
   - Контролирует доступность зависимостей

4. **Sleep Mode** ✅
   - SFM управляет sleep mode для функций
   - Проверяет, можно ли выполнить функцию
   - Пробуждает функции при необходимости

5. **Безопасность** ✅
   - SFM проверяет политики безопасности
   - Валидирует параметры
   - Контролирует доступ

---

## 📊 СТАТИСТИКА SFM

### На сервере:
- ✅ **safe_function_manager.py:** 212 KB
- ✅ **function_registry.json:** 33,268 строк
- ✅ **Всего функций:** 138+
- ✅ **Управляет:** ~220 файлами компонентов

---

## ✅ ИТОГОВАЯ СХЕМА С SFM

```
📱 iOS App
   │
   │ HTTPS (443)
   │
   ▼
🌐 Nginx → 🚪 API Gateway
   │
   │ Все запросы
   │
   ▼
🧠 SFM ⭐ (ЦЕНТР)
   │
   │ Управляет всеми компонентами:
   │
   ├─→ 🤖 AI Agents (76) → через SFM
   ├─→ 🤖 Bots (22) → через SFM
   ├─→ 🛡️ Managers (24) → через SFM
   ├─→ 🔧 Microservices (17) → через SFM
   ├─→ ⚡ Active Modules (7) → через SFM
   ├─→ 👨‍👩‍👧 Family Modules (18) → через SFM
   ├─→ 🛡️ Antivirus (7) → через SFM
   ├─→ 🔐 VPN (20) → через SFM
   ├─→ 📋 Compliance (3) → через SFM
   ├─→ 🎯 Orchestration (1) → через SFM
   ├─→ 🔧 Core (1) → через SFM
   └─→ 🛡️ Критичные модули (20) → через SFM
```

---

## ✅ ВЫВОД

**SFM - это центральный мозг системы!** 🧠

**Все компоненты:**
- ✅ Регистрируются в SFM
- ✅ Выполняются через SFM
- ✅ Управляются SFM
- ✅ Контролируются SFM

**Мобильное приложение:**
- ✅ Взаимодействует с компонентами через SFM
- ✅ Все запросы проходят через SFM
- ✅ SFM управляет всей логикой

---

**SFM - главный оркестратор всей системы безопасности!** 🎯

