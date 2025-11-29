# 🧠 ПОЛНАЯ АРХИТЕКТУРА: SFM В ЦЕНТРЕ СИСТЕМЫ

**Дата:** 2025-11-26  
**Статус:** ✅ Правильная архитектура с SFM как центральным мозгом

---

## 🎯 ПРАВИЛЬНАЯ СХЕМА С SFM В ЦЕНТРЕ

```
┌─────────────────────────────────────────────────────────────────┐
│  📱 ALADDIN iOS App                                              │
│  ├── APIService.swift (58 методов)                              │
│  │   ├── getTopThreats()                                        │
│  │   ├── getProtectionSettings()                                │
│  │   ├── getFamilyMembers()                                     │
│  │   └── ... (55 еще)                                           │
│  │                                                               │
│  └── NetworkManager.swift                                        │
│      ├── SSL Pinning ✅                                          │
│      └── Base URL: https://aladdin-ai.ru/api                    │
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
│  🧠 SFM (Safe Function Manager) ⭐ ЦЕНТР СИСТЕМЫ                 │
│  │                                                               │
│  ├── safe_function_manager.py (212 KB)                          │
│  │   ├── register_function() - регистрация функций             │
│  │   ├── execute_function() - выполнение функций                │
│  │   ├── execute_function_async() - асинхронное выполнение     │
│  │   └── register_function_handler() - регистрация обработчиков│
│  │                                                               │
│  ├── function_registry.json (33,431 строка)                     │
│  │   ├── 138+ функций защиты                                    │
│  │   ├── Зависимости между функциями                            │
│  │   ├── Политики выполнения                                    │
│  │   └── ML модели для AI Agents                                │
│  │                                                               │
│  │ ВСЕ КОМПОНЕНТЫ РАБОТАЮТ ЧЕРЕЗ SFM:                            │
│  │                                                               │
│  ├─→ 🤖 AI AGENTS (76 файлов)                                   │
│  │   │                                                           │
│  │   ├── Регистрация: SFM.register_function()                  │
│  │   ├── Выполнение: SFM.execute_function()                    │
│  │   └── Управление: через function_registry.json               │
│  │                                                               │
│  │   Примеры функций:                                            │
│  │   ├── self_harm_detection_agent ⭐                          │
│  │   │   └── Вызов: SFM.execute_function("self_harm_detection")│
│  │   ├── online_predators_agent ⭐                              │
│  │   │   └── Вызов: SFM.execute_function("online_predators")  │
│  │   ├── grooming_detection_agent ⭐                            │
│  │   │   └── Вызов: SFM.execute_function("grooming_detection")│
│  │   ├── fake_news_detection_agent ⭐                          │
│  │   │   └── Вызов: SFM.execute_function("fake_news_detection")│
│  │   ├── fake_documents_agent ⭐                               │
│  │   │   └── Вызов: SFM.execute_function("fake_documents")    │
│  │   └── ... (71 еще)                                           │
│  │                                                               │
│  ├─→ 🤖 BOTS (22 файла)                                         │
│  │   │                                                           │
│  │   ├── Регистрация: SFM.register_function()                  │
│  │   ├── Выполнение: SFM.execute_function()                    │
│  │   └── Управление: через function_registry.json               │
│  │                                                               │
│  │   Примеры функций:                                            │
│  │   ├── telegram_security_bot                                 │
│  │   │   └── Вызов: SFM.execute_function("telegram_security") │
│  │   ├── whatsapp_security_bot                                 │
│  │   │   └── Вызов: SFM.execute_function("whatsapp_security") │
│  │   ├── parental_control_bot                                  │
│  │   │   └── Вызов: SFM.execute_function("parental_control")  │
│  │   └── ... (19 еще)                                           │
│  │                                                               │
│  ├─→ 🛡️ MANAGERS (24 файла)                                     │
│  │   │                                                           │
│  │   ├── Регистрация: SFM.register_function()                  │
│  │   ├── Выполнение: SFM.execute_function()                    │
│  │   └── Управление: через function_registry.json               │
│  │                                                               │
│  │   Примеры функций:                                            │
│  │   ├── subscription_manager                                  │
│  │   │   └── Вызов: SFM.execute_function("subscription_manager")│
│  │   ├── analytics_manager                                     │
│  │   │   └── Вызов: SFM.execute_function("analytics_manager") │
│  │   ├── sleep_mode_manager                                    │
│  │   │   └── Вызов: SFM.execute_function("sleep_mode_manager") │
│  │   └── ... (21 еще)                                           │
│  │                                                               │
│  ├─→ 🔧 MICROSERVICES (17 файлов)                               │
│  │   │                                                           │
│  │   ├── Регистрация: SFM.register_service_in_mesh()          │
│  │   └── Управление: через service_mesh_manager                │
│  │                                                               │
│  │   Примеры:                                                    │
│  │   ├── api_gateway.py ✅                                     │
│  │   ├── rate_limiter.py                                        │
│  │   └── ... (15 еще)                                           │
│  │                                                               │
│  ├─→ ⚡ ACTIVE MODULES (7 файлов)                               │
│  │   └── Выполнение через SFM.execute_function()               │
│  │                                                               │
│  ├─→ 👨‍👩‍👧 FAMILY MODULES (18 файлов)                            │
│  │   └── Выполнение через SFM.execute_function()               │
│  │                                                               │
│  ├─→ 🛡️ ANTIVIRUS (7 файлов)                                    │
│  │   └── Выполнение через SFM.execute_function()               │
│  │                                                               │
│  ├─→ 🔐 VPN (20 файлов)                                         │
│  │   └── Выполнение через SFM.execute_function()               │
│  │                                                               │
│  ├─→ 📋 COMPLIANCE (3 файла)                                    │
│  │   └── Выполнение через SFM.execute_function()               │
│  │                                                               │
│  ├─→ 🎯 ORCHESTRATION (1 файл)                                  │
│  │   └── Выполнение через SFM.execute_function()               │
│  │                                                               │
│  ├─→ 🔧 CORE (1 файл)                                           │
│  │   └── Выполнение через SFM.execute_function()               │
│  │                                                               │
│  └─→ 🛡️ КРИТИЧНЫЕ МОДУЛИ (20 файлов)                            │
│      └── Выполнение через SFM.execute_function()               │
│                                                                  │
│  ВСЕ КОМПОНЕНТЫ РАБОТАЮТ ЧЕРЕЗ SFM! ⭐                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 ПОЛНЫЙ ПОТОК С SFM

### Пример 1: Запрос защиты от угроз

```
📱 iOS App
   │ APIService.getTopThreats()
   │
   ▼
🌐 Nginx → 🚪 API Gateway
   │ /api/analytics/top-threats
   │
   ▼
🤖 AI Agents Service
   │ Запрос: выполнить threat_intelligence_agent
   │
   ▼
🧠 SFM ⭐ (ЦЕНТР)
   │
   │ 1. Проверка function_registry.json
   │    ├── Функция: "ThreatDetectionAgent"
   │    ├── Статус: "active"
   │    └── Зависимости: проверка
   │
   │ 2. Валидация
   │    ├── Функция зарегистрирована? ✅
   │    ├── Зависимости доступны? ✅
   │    └── Sleep mode? Проверка
   │
   │ 3. Выполнение
   │    ├── execute_function("ThreatDetectionAgent")
   │    ├── Регистрация вызова
   │    └── Мониторинг
   │
   ▼
threat_intelligence_agent.py
   │ Выполнение анализа
   │
   ▼
🧠 SFM ⭐
   │ Обработка результата
   │
   ▼
📱 iOS App
   │ Отображение угроз
   │
   ✅
```

### Пример 2: Запрос защиты семьи (ML система)

```
📱 iOS App
   │ APIService.getProtectionSettings()
   │
   ▼
🌐 Nginx → 🚪 API Gateway
   │ /api/protection/settings
   │
   ▼
🤖 AI Agents Service
   │ Запрос: выполнить self_harm_detection_agent ⭐
   │
   ▼
🧠 SFM ⭐ (ЦЕНТР)
   │
   │ 1. Проверка function_registry.json
   │    ├── Функция: "self_harm_detection_agent"
   │    ├── Тип: "ai_agent"
   │    ├── ML система: ✅
   │    └── Зависимости: ["natural_language_processor"]
   │
   │ 2. Валидация
   │    ├── Функция зарегистрирована? ✅
   │    ├── Зависимости доступны? ✅
   │    └── Sleep mode? Проверка через sleep_mode_manager
   │
   │ 3. Выполнение
   │    ├── execute_function("self_harm_detection_agent")
   │    ├── Загрузка ML модели
   │    ├── Выполнение анализа
   │    └── Возврат результата
   │
   ▼
self_harm_detection_agent.py ⭐
   │ ML анализ на самоповреждение
   │
   ▼
🧠 SFM ⭐
   │ Обработка результата
   │
   ▼
📱 iOS App
   │ Отображение настроек защиты
   │
   ✅
```

---

## 📊 FUNCTION_REGISTRY.JSON

### Статистика:
- ✅ **33,431 строка** данных
- ✅ **138+ функций** защиты
- ✅ **Все компоненты** зарегистрированы

### Примеры функций:
- ✅ `AntiFraudMasterAI` - активна
- ✅ `ThreatDetectionAgent` - активна
- ✅ `SimpleSleep` - активна
- ✅ `MobileSecurityAgent` - активна
- ✅ И еще 134+ функций...

---

## ✅ ИТОГ

**SFM - центральный мозг системы!** 🧠

**Все компоненты:**
- ✅ Регистрируются в SFM
- ✅ Выполняются через SFM
- ✅ Управляются SFM
- ✅ Контролируются SFM

**Мобильное приложение:**
- ✅ Все запросы проходят через SFM
- ✅ SFM управляет всей логикой
- ✅ SFM - главный оркестратор

---

**Архитектура правильная: SFM в центре!** ✅

