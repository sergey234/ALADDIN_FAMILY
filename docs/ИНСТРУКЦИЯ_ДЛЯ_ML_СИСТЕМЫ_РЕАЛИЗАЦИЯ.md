# 🤖 ИНСТРУКЦИЯ ДЛЯ ML СИСТЕМЫ: РЕАЛИЗАЦИЯ ФУНКЦИЙ БЕЗОПАСНОСТИ ALADDIN

**Дата создания:** 9 декабря 2025  
**Версия:** 1.0  
**Статус:** ✅ Готово к использованию  
**Целевая аудитория:** ML системы для автоматической реализации кода

---

## 📋 СОДЕРЖАНИЕ

1. [Контекст проекта](#контекст-проекта)
2. [Архитектура системы](#архитектура-системы)
3. [Процесс разработки](#процесс-разработки)
4. [Детальные планы реализации](#детальные-планы-реализации)
5. [Технические детали](#технические-детали)
6. [Структура кода](#структура-кода)
7. [Интеграция с существующими компонентами](#интеграция-с-существующими-компонентами)
8. [Тестирование](#тестирование)
9. [Деплой](#деплой)
10. [Ссылки на документы](#ссылки-на-документы)

---

## 🎯 КОНТЕКСТ ПРОЕКТА

### Что такое ALADDIN?

**ALADDIN** - это мобильное приложение для семейной безопасности на iOS, которое предоставляет комплексную защиту для семей:

- **Защита устройств** (антивирус, VPN, защита от фишинга)
- **Родительский контроль** (контроль времени экрана, блокировка сайтов)
- **Мониторинг безопасности** (отслеживание угроз, утечек данных)
- **Защита IoT устройств** (камеры, умный дом)
- **Геолокация и безопасность** (отслеживание местоположения семьи)

### Текущее состояние проекта

**Серверная часть (SFM - Security Functions Manager):**
- Расположение: `/opt/aladdin-backend/security/`
- Более 1000 функций безопасности
- Более 20 AI агентов
- Более 20 менеджеров
- Более 10 ботов
- Архитектура: Python, асинхронная обработка, интеграция через `function_registry.json`

**iOS приложение:**
- Расположение: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/`
- Язык: Swift, SwiftUI
- Архитектура: MVVM
- API интеграция через `APIService.swift`

### Цель реализации

Реализовать **11 функций безопасности**, которые отсутствуют или частично реализованы, чтобы ALADDIN соответствовал функциональности конкурентов (Aura, Norton 360, Life360, Qustodio и др.).

---

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

### Структура серверной части

```
/opt/aladdin-backend/security/
├── ai_agents/              # AI агенты (новые агенты здесь)
│   ├── threat_intelligence_agent.py  # Существующий (2,598 строк, 80 функций)
│   ├── password_security_agent.py    # Существующий
│   ├── iot_security_agent.py          # Существующий
│   ├── dark_web_monitoring_agent.py  # НОВЫЙ (нужно создать)
│   ├── russian_identity_theft_protection_agent.py  # НОВЫЙ
│   ├── ai_categories_agent.py         # НОВЫЙ
│   ├── crash_detection_agent.py        # НОВЫЙ
│   ├── driving_reports_agent.py       # НОВЫЙ
│   ├── anti_tracker_agent.py          # НОВЫЙ
│   └── roadside_assistance_agent.py  # НОВЫЙ
├── bots/                   # Боты (расширение существующих)
│   ├── enhanced_social_media_bot.py   # Существующий (нужно расширить)
│   └── ...
├── managers/               # Менеджеры (расширение существующих)
│   ├── data_protection_manager.py      # Существующий (нужно расширить)
│   └── ...
└── data/
    └── sfm/
        └── function_registry.json      # Регистр всех функций
```

### Структура iOS приложения

```
ALADDIN_iOS/
├── Core/
│   ├── Config/
│   │   └── AppConfig.swift            # Endpoints (нужно добавить новые)
│   ├── Network/
│   │   └── APIService.swift           # API методы (нужно добавить новые)
│   └── Models/
│       └── APIModels.swift             # Модели данных (нужно добавить новые)
├── Screens/                            # UI экраны (нужно создать новые)
│   ├── DarkWebMonitoringScreen.swift   # НОВЫЙ
│   ├── IdentityTheftProtectionScreen.swift  # НОВЫЙ
│   ├── PasswordManagerScreen.swift     # НОВЫЙ
│   ├── AICategoriesScreen.swift        # НОВЫЙ
│   ├── CrashDetectionScreen.swift      # НОВЫЙ
│   ├── DrivingReportsScreen.swift      # НОВЫЙ
│   ├── PersonalDataCleanupScreen.swift # НОВЫЙ
│   ├── AntiTrackerScreen.swift        # НОВЫЙ
│   ├── RoadsideAssistanceScreen.swift  # НОВЫЙ
│   └── ...
└── backend_agents/                      # Локальная разработка новых агентов
    ├── dark_web_monitoring_agent.py
    └── ...
```

### Принципы архитектуры

1. **Модульность:** Каждая функция = отдельный модуль/агент
2. **Переиспользование:** Использовать существующие утилиты где возможно
3. **Гибридный подход:** Для Dark Web мониторинга - отдельный агент + общие утилиты
4. **Расширение существующих:** Для Social Media и Data Cleanup - расширять существующие модули
5. **Соответствие SFM:** Все новые агенты регистрируются в `function_registry.json`

---

## 🔧 ПРОЦЕСС РАЗРАБОТКИ

### ✅ РЕКОМЕНДУЕМЫЙ ПОДХОД: Локальная разработка → Тестирование → Деплой

#### ШАГ 1: ЛОКАЛЬНАЯ РАЗРАБОТКА

**Где писать код:**
- Локально в проекте: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/`
- Создать папку `backend_agents/` для новых агентов
- Создать папку `backend_tests/` для тестов

**Структура локальной разработки:**
```
ALADDIN_iOS/
├── backend_agents/          # Новые агенты (локально)
│   ├── dark_web_monitoring_agent.py
│   ├── russian_identity_theft_protection_agent.py
│   └── ...
├── backend_tests/           # Тесты для агентов
│   ├── test_dark_web_monitoring.py
│   └── ...
└── docs/                    # Документация
```

**Почему локально:**
- ✅ Можно тестировать без подключения к серверу
- ✅ Git версионирование
- ✅ Легко откатывать изменения
- ✅ Можно работать без интернета

#### ШАГ 2: ТЕСТИРОВАНИЕ

**Что тестировать:**
1. Unit-тесты для каждого метода агента
2. Интеграционные тесты с существующими компонентами
3. Проверка соответствия SFM
4. Проверка работы API endpoints
5. Тестирование iOS интеграции

**Инструменты:**
- `pytest` для Python тестов
- `unittest` для базовых тестов
- Моки для внешних API

#### ШАГ 3: ДЕПЛОЙ НА СЕРВЕР

**Процесс:**
1. ✅ Код протестирован локально
2. ✅ Код проверен на соответствие стандартам
3. ✅ Отправка на сервер через SSH/SCP:
   ```bash
   scp backend_agents/dark_web_monitoring_agent.py root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/
   ```
4. ✅ Интеграция с SFM:
   - Регистрация в `function_registry.json`
   - Добавление в `safe_function_manager.py`
5. ✅ Тестирование на сервере
6. ✅ Интеграция с iOS приложением

---

## 📋 ДЕТАЛЬНЫЕ ПЛАНЫ РЕАЛИЗАЦИИ

### ФАЗА 1: КРИТИЧНЫЕ ФУНКЦИИ (29-32 дня)

#### 1. 🌐 DARK WEB МОНИТОРИНГ (8-9 дней) - **ГИБРИДНЫЙ ПОДХОД**

**Статус:** ❌ НЕТ  
**Приоритет:** ⭐⭐⭐ Критично  
**Подход:** Гибридный (отдельный агент + общие утилиты из ThreatIntelligenceAgent)

**Почему гибридный подход:**
- `ThreatIntelligenceAgent` уже очень большой (2,598 строк, 80 функций)
- Разные задачи: ThreatIntelligenceAgent = общий мониторинг, Dark Web = персональный мониторинг
- Безопасность: изолированная обработка персональных данных (email, пароли)
- Соответствие SFM: каждая функция = отдельный модуль
- Переиспользование: используем общие утилиты из ThreatIntelligenceAgent

**Что нужно сделать:**

**День 1: Анализ и подготовка**
- Изучить структуру `threat_intelligence_agent.py`
- Определить общие утилиты для переиспользования:
  - Методы валидации данных (`_validate_email`, `_validate_phone`)
  - Методы работы с API (`_make_http_request`, обработка ошибок)
  - Методы логирования (`logger`)
  - AI модели (если подходят)
- Изучить Have I Been Pwned API документацию (https://haveibeenpwned.com/API/v3)
- Изучить BreachDirectory API документацию
- Исследовать российские базы утечек

**День 2: Создание базового агента (локально)**
- Создать файл `backend_agents/dark_web_monitoring_agent.py`
- Реализовать класс `DarkWebMonitoringAgent(SecurityBase)`
- Интегрировать с общими утилитами из `ThreatIntelligenceAgent`:
  ```python
  from security.ai_agents.threat_intelligence_agent import ThreatIntelligenceAgent
  
  class DarkWebMonitoringAgent(SecurityBase):
      def __init__(self, config: Optional[Dict[str, Any]] = None):
          super().__init__(config)
          # Используем утилиты из ThreatIntelligenceAgent
          self.threat_intel = ThreatIntelligenceAgent()
          self.api_validator = self.threat_intel._validate_email
          self.http_client = self.threat_intel._make_http_request
          self.logger = self.threat_intel.logger
  ```
- Добавить метод `check_email_breach(email: str)` с k-анонимностью:
  ```python
  def check_email_breach(self, email: str) -> dict:
      """Проверка email на утечки с k-анонимностью"""
      # Используем общий метод валидации
      if not self.api_validator(email):
          return {"error": "Invalid email"}
      
      # k-анонимность для безопасности
      email_hash = hashlib.sha1(email.encode()).hexdigest()
      hash_prefix = email_hash[:5].upper()
      
      # Используем общий HTTP клиент
      response = self.http_client(
          f"https://api.haveibeenpwned.com/v3/range/{hash_prefix}",
          headers={"hibp-api-key": self.config.get("hibp_api_key")}
      )
      
      return self._parse_breach_response(response, email)
  ```
- Добавить метод `monitor_user_data(user_id, email, phone)`
- Добавить метод `start_monitoring(user_id, email, interval)`

**День 3-4: Расширение функциональности (локально)**
- Интеграция с BreachDirectory API
- Российские базы утечек
- Система кэширования (Redis или in-memory, TTL 24 часа)

**День 5: Интеграция с ThreatIntelligenceAgent (локально)**
- Создать общий интерфейс `ThreatMonitoringInterface`:
  ```python
  class ThreatMonitoringInterface:
      """Общий интерфейс для мониторинга угроз"""
      async def collect_threats(self) -> List[Dict]:
          raise NotImplementedError
      
      async def analyze_threats(self, threats: List[Dict]) -> List[Dict]:
          raise NotImplementedError
      
      async def send_alert(self, alert: Dict):
          raise NotImplementedError
  ```
- Реализовать в обоих агентах
- Обмен данными через события
- Синхронизация информации об утечках

**День 6: Интеграция с SFM (локально)**
- Зарегистрировать агент в `function_registry.json`:
  ```json
  {
    "name": "dark_web_monitoring_agent",
    "type": "ai_agent",
    "path": "/opt/aladdin-backend/security/ai_agents/dark_web_monitoring_agent.py",
    "class": "DarkWebMonitoringAgent",
    "functions": [
      {
        "name": "check_email_breach",
        "description": "Проверка email на утечки через Have I Been Pwned API",
        "parameters": ["email: str"],
        "returns": "List[Dict]"
      }
    ],
    "dependencies": ["threat_intelligence_agent"],
    "status": "active"
  }
  ```
- Настроить автоматический запуск мониторинга
- Настроить алерты

**День 7: API endpoints на сервере (деплой)**
- Отправить код на сервер через SSH/SCP
- Добавить в `/opt/aladdin-backend/api/main.py`:
  - `/api/darkweb/check` (POST)
  - `/api/darkweb/start-monitoring` (POST)
  - `/api/darkweb/breaches` (GET)
  - `/api/darkweb/status` (GET)
- Добавить валидацию данных
- Добавить обработку ошибок
- Добавить rate limiting

**День 8: Интеграция в iOS (локально)**
- Добавить endpoints в `AppConfig.swift`:
  ```swift
  enum Endpoint {
      static let darkWebCheck = "/darkweb/check"
      static let darkWebStartMonitoring = "/darkweb/start-monitoring"
      static let darkWebBreaches = "/darkweb/breaches"
      static let darkWebStatus = "/darkweb/status"
  }
  ```
- Добавить методы в `APIService.swift`:
  ```swift
  func checkDarkWeb(email: String, phone: String?, completion: @escaping (Result<DarkWebCheckResponse, Error>) -> Void)
  func startDarkWebMonitoring(email: String, intervalHours: Int = 24, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void)
  func getDarkWebBreaches(completion: @escaping (Result<DarkWebBreachesResponse, Error>) -> Void)
  func getDarkWebStatus(completion: @escaping (Result<DarkWebStatusResponse, Error>) -> Void)
  ```
- Создать модели в `APIModels.swift`:
  ```swift
  struct DarkWebCheckResponse: Codable {
      let userId: String
      let breachesFound: Int
      let breaches: [DarkWebBreach]
      let checkedAt: String
  }
  
  struct DarkWebBreach: Codable {
      let email: String
      let breachName: String
      let count: Int
      let detectedAt: String
      let severity: String?
      let description: String?
      let affectedData: [String]?
  }
  ```
- Создать `DarkWebMonitoringScreen.swift` с UI:
  - Статус мониторинга
  - Список найденных утечек
  - Кнопка запуска проверки
  - Настройки мониторинга

**День 9: Тестирование**
- Unit-тесты для агента
- Тестирование методов проверки email
- Тестирование кэширования
- Тестирование интеграции с ThreatIntelligenceAgent
- Интеграционные тесты API endpoints
- Тестирование iOS интеграции
- Тестирование уведомлений
- Тестирование производительности

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/ai_agents/dark_web_monitoring_agent.py` (новый)
- iOS: `Screens/DarkWebMonitoringScreen.swift` (новый)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)
- iOS: `Core/Models/APIModels.swift` (обновить)

---

#### 2. 🆔 IDENTITY THEFT PROTECTION ДЛЯ РОССИИ (18 дней)

**Статус:** ❌ НЕТ  
**Приоритет:** ⭐⭐⭐ Критично  
**Подход:** Новый агент для России

**Что это:**
- Мониторинг СНИЛС на подозрительную активность
- Мониторинг кредитного отчета (НБКИ, ОКБ)
- Проверка в базе мошенников (147,000 записей)
- Соответствие 152-ФЗ (шифрование, согласие пользователя)

**Что нужно сделать:**

**День 1-2: Исследование российских API**
- Изучить НБКИ API документацию
- Изучить ОКБ API документацию
- Изучить Эквифакс API документацию
- Изучить юридические требования (152-ФЗ)
- Определить возможности мониторинга СНИЛС

**День 3-7: Создание агента (локально)**
- Создать файл `backend_agents/russian_identity_theft_protection_agent.py`
- Реализовать класс `RussianIdentityTheftProtectionAgent(SecurityBase)`
- Интегрировать с существующими компонентами:
  - `russian_data_protection_manager.py` для 152-ФЗ
  - `russian_threat_intelligence.py`
  - База мошенников (147,000 записей)
- Реализовать методы:
  - `monitor_snils(snils: str)` - мониторинг СНИЛС
  - `monitor_credit_report(user_id: str)` - мониторинг кредитного отчета
  - `check_fraud_database(snils, passport)` - проверка в базе мошенников
  - `detect_identity_theft(user_id, snils)` - обнаружение кражи личности

**День 8-10: API endpoints (локально и деплой)**
- Добавить `/api/identity-theft/monitor-snils` (POST)
- Добавить `/api/identity-theft/monitor-credit` (POST)
- Добавить `/api/identity-theft/check` (POST)
- Добавить `/api/identity-theft/alerts` (GET)
- Добавить `/api/identity-theft/status` (GET)
- Добавить проверку согласия пользователя (152-ФЗ)

**День 11-14: Интеграция в iOS (локально)**
- Добавить endpoints в `AppConfig.swift`
- Добавить методы в `APIService.swift`
- Создать модели в `APIModels.swift`
- Создать `IdentityTheftProtectionScreen.swift`:
  - Статус мониторинга СНИЛС
  - Статус мониторинга кредитного отчета
  - Оценка риска
  - Список алертов
  - Настройки мониторинга
- Согласие на обработку данных (152-ФЗ):
  - Экран согласия
  - Согласие на СНИЛС
  - Согласие на паспортные данные
  - Согласие на кредитный отчет
  - Возможность отзыва согласия

**День 15-16: Соответствие 152-ФЗ (локально)**
- Использовать `russian_data_protection_manager.py`
- Добавить минимизацию данных
- Добавить шифрование СНИЛС (AES-256)
- Добавить автоматическое удаление данных при отзыве согласия
- Добавить логирование доступа к данным
- Создать политику обработки персональных данных
- Обновить пользовательское соглашение

**День 17-18: Тестирование и деплой**
- Функциональное тестирование
- Тестирование соответствия 152-ФЗ
- Тестирование мониторинга СНИЛС
- Тестирование мониторинга кредитного отчета
- Тестирование базы мошенников
- Отправка на сервер
- Исправление найденных ошибок

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/ai_agents/russian_identity_theft_protection_agent.py` (новый)
- iOS: `Screens/IdentityTheftProtectionScreen.swift` (новый)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)
- iOS: `Core/Models/APIModels.swift` (обновить)

---

#### 3. 🔐 ИНТЕГРАЦИЯ МЕНЕДЖЕРА ПАРОЛЕЙ В iOS (3-5 дней)

**Статус:** ⚠️ Частично (есть на сервере, нужна интеграция в iOS)  
**Приоритет:** ⭐⭐⭐ Критично  
**Подход:** Интеграция существующего (`password_security_agent.py` уже есть на сервере)

**Что нужно сделать:**

**День 1-2: Интеграция в iOS (локально)**
- Добавить endpoints в `AppConfig.swift`:
  ```swift
  static let passwordManagerGenerate = "/password/generate"
  static let passwordManagerSave = "/password/save"
  static let passwordManagerGet = "/password/get"
  static let passwordManagerCheck = "/password/check"
  ```
- Добавить методы в `APIService.swift`:
  ```swift
  func generatePassword(length: Int, includeSymbols: Bool, completion: @escaping (Result<PasswordGenerateResponse, Error>) -> Void)
  func savePassword(service: String, username: String, password: String, completion: @escaping (Result<PasswordSaveResponse, Error>) -> Void)
  func getPasswords(completion: @escaping (Result<PasswordGetResponse, Error>) -> Void)
  func checkPasswordStrength(password: String, completion: @escaping (Result<PasswordCheckResponse, Error>) -> Void)
  ```
- Создать модели в `APIModels.swift`:
  ```swift
  struct PasswordGenerateResponse: Codable {
      let password: String
      let strength: String
  }
  
  struct PasswordSaveResponse: Codable {
      let success: Bool
      let id: String
  }
  
  struct PasswordGetResponse: Codable {
      let passwords: [PasswordEntry]
  }
  
  struct PasswordEntry: Codable {
      let id: String
      let service: String
      let username: String
      let password: String
      let createdAt: String
  }
  
  struct PasswordCheckResponse: Codable {
      let strength: String
      let score: Int
      let suggestions: [String]
  }
  ```
- Создать `PasswordManagerScreen.swift`:
  - Генератор паролей
  - Список сохраненных паролей
  - Проверка силы пароля
  - Настройки менеджера паролей

**День 3: Тестирование и деплой**
- Unit-тесты для iOS интеграции
- Интеграционные тесты
- Тестирование работы с сервером
- Проверка безопасности хранения паролей
- Исправление найденных ошибок

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/ai_agents/password_security_agent.py` (уже есть, не трогать)
- iOS: `Screens/PasswordManagerScreen.swift` (новый)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)
- iOS: `Core/Models/APIModels.swift` (обновить)

---

### ФАЗА 2: НОВЫЕ КРИТИЧНЫЕ ФУНКЦИИ (17-22 дня)

#### 4. 🤖 AI CATEGORIES (5-7 дней)

**Статус:** ❌ НЕТ  
**Приоритет:** ⭐⭐⭐ Критично  
**Подход:** Новый агент

**Что это:**
- Контроль доступа детей к AI-сайтам (ChatGPT, Midjourney, DALL-E, Claude, Gemini)
- Блокировка/разрешение доступа
- Предупреждения родителям
- Настройки по времени и возрасту

**Что нужно сделать:**

**День 1-2: Создание агента на сервере (локально)**
- Создать файл `backend_agents/ai_categories_agent.py`
- Реализовать класс `AICategoriesAgent(SecurityBase)`
- Список AI-сайтов:
  ```python
  AI_SITES = {
      "chatgpt": "https://chat.openai.com",
      "midjourney": "https://www.midjourney.com",
      "dalle": "https://labs.openai.com",
      "claude": "https://claude.ai",
      "gemini": "https://gemini.google.com"
  }
  ```
- Методы блокировки/разрешения
- Методы предупреждений
- Настройки по времени (блокировка в определенное время)
- Настройки по возрасту

**День 3-4: API endpoints (локально и деплой)**
- Отправить код на сервер
- Добавить `/api/ai-categories/block` (POST)
- Добавить `/api/ai-categories/allow` (POST)
- Добавить `/api/ai-categories/status` (GET)
- Добавить валидацию данных
- Добавить обработку ошибок
- Интеграция с SFM

**День 5-6: Интеграция в iOS (локально)**
- Добавить endpoints в `AppConfig.swift`
- Добавить методы в `APIService.swift`
- Создать модели в `APIModels.swift`
- Создать `AICategoriesScreen.swift`:
  - Список AI-сайтов
  - Настройки блокировки/разрешения
  - Настройки по времени
  - Уведомления родителям

**День 7: Тестирование**
- Unit-тесты
- Интеграционные тесты
- Тестирование блокировки/разрешения
- Исправление найденных ошибок

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/ai_agents/ai_categories_agent.py` (новый)
- iOS: `Screens/AICategoriesScreen.swift` (новый)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)
- iOS: `Core/Models/APIModels.swift` (обновить)

---

#### 5. 📱 РАСШИРЕННЫЙ SOCIAL MEDIA MONITORING (2-3 дня) - **РАСШИРЕНИЕ**

**Статус:** ⚠️ Частично (Instagram, Twitter/X, TikTok, VK, Telegram, WhatsApp, MAX есть)  
**Приоритет:** ⭐⭐⭐ Критично  
**Подход:** Расширение `enhanced_social_media_bot.py`

**Важно:** Instagram, Twitter/X, TikTok, VK, Telegram, WhatsApp, MAX уже есть! Нужно добавить только MAX (интеграция в enum) и Одноклассники (новый)

**Что нужно сделать:**

**День 1: Расширение enhanced_social_media_bot.py (локально и деплой)**
- Подключиться к серверу через SSH
- Открыть файл `/opt/aladdin-backend/security/bots/enhanced_social_media_bot.py`
- Найти `SocialPlatform(Enum)` и добавить:
  ```python
  class SocialPlatform(Enum):
      # Уже есть:
      INSTAGRAM = "instagram"
      TWITTER = "twitter"
      TIKTOK = "tiktok"
      VK = "vk"
      TELEGRAM = "telegram"
      WHATSAPP = "whatsapp"
      FACEBOOK = "facebook"
      YOUTUBE = "youtube"
      DISCORD = "discord"
      SNAPCHAT = "snapchat"
      
      # Нужно добавить:
      MAX = "max"                          # НОВОЕ (интегрировать с max_messenger_security_bot.py)
      ODNOKLASSNIKI = "odnoklassniki"      # НОВОЕ
  ```
- Интегрировать с `max_messenger_security_bot.py` (использовать существующие методы)
- Добавить методы мониторинга для Одноклассники
- Добавить конфигурацию платформ в `_initialize_platform_apis()`

**День 2: API endpoints и тестирование**
- Обновить существующие API endpoints (если нужно)
- Добавить поддержку MAX и Одноклассники в методы мониторинга
- Тестирование мониторинга MAX
- Тестирование мониторинга Одноклассники
- Интеграционные тесты

**День 3: iOS интеграция (если нужно)**
- Проверить, нужно ли обновлять iOS интеграцию
- Обновить `AppConfig.swift` (если нужно)
- Обновить UI экран (если нужно)
- Финальное тестирование

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/bots/enhanced_social_media_bot.py` (обновить)
- Сервер: `/opt/aladdin-backend/security/bots/max_messenger_security_bot.py` (использовать существующий)

---

#### 6. 🚗 CRASH DETECTION (10-12 дней)

**Статус:** ❌ НЕТ  
**Приоритет:** ⭐⭐⭐ Критично  
**Подход:** Новый агент

**Что это:**
- Автоматическое обнаружение автомобильной аварии
- Анализ данных акселерометра, гироскопа
- Алгоритм обнаружения аварий (G-силы, резкое изменение скорости)
- Автоматический вызов помощи (112, 911)
- Отправка точного местоположения

**Что нужно сделать:**

**День 1-3: Создание агента на сервере (локально)**
- Создать файл `backend_agents/crash_detection_agent.py`
- Реализовать класс `CrashDetectionAgent(SecurityBase)`
- Анализ данных акселерометра, гироскопа
- Алгоритм обнаружения аварий:
  - Настройка порогов G-сил
  - Настройка порогов изменения скорости
  - Обработка ложных срабатываний
- Интеграция с экстренными службами (112, 911)
- Метод автоматического вызова помощи
- Отправка точного местоположения

**День 4-5: API endpoints (локально и деплой)**
- Отправить код на сервер
- Добавить `/api/crash-detection/start` (POST)
- Добавить `/api/crash-detection/stop` (POST)
- Добавить `/api/crash-detection/status` (GET)
- Добавить `/api/crash-detection/emergency-call` (POST)
- Интеграция с SFM

**День 6-9: Интеграция в iOS (локально)**
- Добавить endpoints в `AppConfig.swift`
- Добавить методы в `APIService.swift`
- Создать модели в `APIModels.swift`
- Интеграция с CoreMotion:
  - Интеграция с акселерометром
  - Интеграция с гироскопом
  - Отправка данных на сервер
- Создать `CrashDetectionScreen.swift`:
  - Статус мониторинга
  - Настройки чувствительности
  - Экстренные контакты
- Логика автоматического вызова:
  - Обратный отсчет (10 секунд)
  - Автоматический вызов 112
  - Отправка местоположения
  - Уведомление экстренных контактов

**День 10-12: Тестирование и деплой**
- Unit-тесты
- Тестирование алгоритма обнаружения
- Тестирование обработки данных акселерометра
- Тестирование интеграции с экстренными службами
- Интеграционные тесты
- Тестирование с симуляцией аварий
- Тестирование ложных срабатываний
- Тестирование автоматического вызова
- Исправление найденных ошибок
- Оптимизация производительности
- Финальное тестирование на сервере

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/ai_agents/crash_detection_agent.py` (новый)
- iOS: `Screens/CrashDetectionScreen.swift` (новый)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)
- iOS: `Core/Models/APIModels.swift` (обновить)

---

### ФАЗА 3: ВАЖНЫЕ ФУНКЦИИ (36-46 дней)

#### 7. 📊 DRIVING REPORTS (8-10 дней)

**Статус:** ❌ НЕТ  
**Приоритет:** ⭐⭐ Средняя  
**Подход:** Новый агент

**Что это:**
- Детальные отчеты о том, как человек водит машину
- Отслеживание скорости, использования телефона, резкого торможения
- Оценка безопасности вождения
- Еженедельные отчеты

**Что нужно сделать:**

**День 1-3: Создание агента на сервере (локально)**
- Создать файл `backend_agents/driving_reports_agent.py`
- Реализовать класс `DrivingReportsAgent(SecurityBase)`
- Отслеживание скорости, использования телефона, резкого торможения
- Реализовать метод `generate_report(user_id, start_date, end_date)`
- Оценка безопасности вождения
- Статистика нарушений

**День 4-5: API endpoints (локально и деплой)**
- Отправить код на сервер
- Добавить `/api/driving-reports/generate` (POST)
- Добавить `/api/driving-reports/report` (GET)
- Добавить `/api/driving-reports/weekly` (GET)
- Интеграция с SFM

**День 6-8: Интеграция в iOS (локально)**
- Добавить endpoints в `AppConfig.swift`
- Добавить методы в `APIService.swift`
- Создать модели в `APIModels.swift`
- Создать `DrivingReportsScreen.swift`:
  - Еженедельный отчет
  - Графики скорости
  - Статистика нарушений
- Интеграция с геолокацией:
  - Отслеживание скорости
  - Отслеживание использования телефона
  - Отслеживание резкого торможения

**День 9-10: Тестирование и деплой**
- Unit-тесты
- Тестирование генерации отчетов
- Тестирование оценки безопасности
- Интеграционные тесты
- Тестирование с реальными данными
- Исправление найденных ошибок
- Финальное тестирование на сервере

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/ai_agents/driving_reports_agent.py` (новый)
- iOS: `Screens/DrivingReportsScreen.swift` (новый)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)
- iOS: `Core/Models/APIModels.swift` (обновить)

---

#### 8. 🗑️ PERSONAL DATA CLEANUP (10-12 дней) - **РАСШИРЕНИЕ**

**Статус:** ⚠️ Частично (базовая защита есть)  
**Приоритет:** ⭐⭐ Средняя  
**Подход:** Расширение `data_protection_manager.py`

**Важно:** Базовая защита данных уже есть! Нужно добавить только удаление с брокерских сайтов

**Что нужно сделать:**

**День 1-3: Исследование брокерских сайтов (локально)**
- Составить список известных брокерских сайтов (российских и международных)
- Изучить API/формы для удаления данных
- Изучить юридические требования
- Создать план автоматического удаления
- Определить шаблоны запросов
- Определить процесс отслеживания

**День 4-7: Расширение data_protection_manager.py (локально и деплой)**
- Подключиться к серверу через SSH
- Открыть файл `/opt/aladdin-backend/security/data_protection_manager.py`
- Добавить метод `find_data_on_broker_sites(user_data: dict)`:
  - Реализовать поиск данных на брокерских сайтах
- Добавить метод `remove_data_from_broker_sites(user_data: dict, sites: list)`:
  - Реализовать автоматическую отправку запросов на удаление
  - Реализовать обработку ответов
- Добавить метод `track_removal_progress(request_id: str)`:
  - Реализовать систему отслеживания
  - Реализовать повторные запросы (если данные не удалены)
- Интеграция с SFM

**День 8-9: API endpoints (локально и деплой)**
- Добавить `/api/data-cleanup/scan` (POST)
- Добавить `/api/data-cleanup/remove` (POST)
- Добавить `/api/data-cleanup/status` (GET)
- Добавить `/api/data-cleanup/report` (GET)
- Тестирование API

**День 10-12: Интеграция в iOS и тестирование (локально)**
- Добавить endpoints в `AppConfig.swift`
- Добавить методы в `APIService.swift`
- Создать модели в `APIModels.swift`
- Создать `PersonalDataCleanupScreen.swift`:
  - Список найденных сайтов
  - Кнопка запуска сканирования
  - Кнопка запуска удаления
  - Отчет о процессе удаления
- Unit-тесты
- Интеграционные тесты
- Тестирование с реальными брокерскими сайтами
- Исправление найденных ошибок

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/data_protection_manager.py` (обновить)
- iOS: `Screens/PersonalDataCleanupScreen.swift` (новый)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)
- iOS: `Core/Models/APIModels.swift` (обновить)

---

#### 9. 🛡️ ANTI-TRACKER (5-7 дней)

**Статус:** ❌ НЕТ  
**Приоритет:** ⭐⭐ Средняя  
**Подход:** Новый агент

**Что это:**
- Блокировка трекеров и рекламных сетей
- Защита приватности
- Ускорение загрузки страниц

**Что нужно сделать:**

**День 1-2: Создание агента на сервере (локально)**
- Создать файл `backend_agents/anti_tracker_agent.py`
- Реализовать класс `AntiTrackerAgent(SecurityBase)`
- Список известных трекеров и рекламных сетей
- Методы блокировки трекеров
- Методы блокировки рекламы
- Интеграция с VPN модулем
- Настройки блокировки

**День 3-4: API endpoints (локально и деплой)**
- Отправить код на сервер
- Добавить `/api/anti-tracker/block` (POST)
- Добавить `/api/anti-tracker/status` (GET)
- Добавить `/api/anti-tracker/stats` (GET)
- Интеграция с SFM

**День 5-6: Интеграция в iOS (локально)**
- Добавить endpoints в `AppConfig.swift`
- Добавить методы в `APIService.swift`
- Интегрировать в VPN модуль
- Создать `AntiTrackerScreen.swift`:
  - Статистика заблокированных трекеров
  - Настройки блокировки
  - Интеграция с VPN

**День 7: Тестирование**
- Unit-тесты
- Интеграционные тесты
- Тестирование блокировки трекеров
- Тестирование блокировки рекламы
- Исправление найденных ошибок

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/ai_agents/anti_tracker_agent.py` (новый)
- iOS: `Screens/AntiTrackerScreen.swift` (новый)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)
- iOS: `Core/Models/APIModels.swift` (обновить)

---

#### 10. 🚑 ROADSIDE ASSISTANCE (10-12 дней)

**Статус:** ❌ НЕТ  
**Приоритет:** ⭐⭐ Средняя  
**Подход:** Новый агент  
**Важно:** Требует партнерства с службой помощи на дороге

**Что это:**
- Служба помощи на дороге 24/7
- Виды помощи: буксировка, запуск двигателя, замена колеса, открытие замка, доставка топлива
- Быстрая помощь (обычно 30-60 минут)

**Что нужно сделать:**

**День 1-2: Партнерство (локально)**
- Найти партнеров (Росгосстрах, АльфаСтрахование и т.д.)
- Изучить API партнеров
- Договориться об интеграции
- Изучить документацию API
- Изучить методы вызова помощи
- Изучить форматы данных

**День 3-5: Создание агента на сервере (локально)**
- Создать файл `backend_agents/roadside_assistance_agent.py`
- Реализовать класс `RoadsideAssistanceAgent(SecurityBase)`
- Интеграция с API партнеров
- Реализовать метод `call_assistance(user_id, problem_type, location)`
- Виды помощи (буксировка, запуск двигателя, замена колеса и т.д.)
- Отслеживание статуса помощи
- Интеграция с SFM

**День 6-7: API endpoints (локально и деплой)**
- Отправить код на сервер
- Добавить `/api/roadside-assistance/call` (POST)
- Добавить `/api/roadside-assistance/status` (GET)
- Добавить `/api/roadside-assistance/cancel` (POST)
- Тестирование API

**День 8-10: Интеграция в iOS (локально)**
- Добавить endpoints в `AppConfig.swift`
- Добавить методы в `APIService.swift`
- Создать модели в `APIModels.swift`
- Создать `RoadsideAssistanceScreen.swift`:
  - Кнопка вызова помощи
  - Выбор типа проблемы
  - Отслеживание статуса помощи
- Интеграция с геолокацией:
  - Автоматическое определение местоположения
  - Отправка местоположения партнеру

**День 11-12: Тестирование и деплой**
- Интеграционные тесты
- Тестирование с партнерами
- Тестирование вызова помощи
- Тестирование отслеживания статуса
- Исправление найденных ошибок
- Финальное тестирование на сервере

**Ключевые файлы:**
- Сервер: `/opt/aladdin-backend/security/ai_agents/roadside_assistance_agent.py` (новый)
- iOS: `Screens/RoadsideAssistanceScreen.swift` (новый)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)
- iOS: `Core/Models/APIModels.swift` (обновить)

---

#### 11. 💭 BUBBLES FEATURE (3-5 дней) - **РАСШИРЕНИЕ**

**Статус:** ❌ НЕТ  
**Приоритет:** ⭐⭐ Средняя  
**Подход:** Расширение функционала геолокации

**Что это:**
- Показ приблизительного местоположения вместо точного
- Настройки радиуса (100м, 500м, 1км)
- Настройки для разных людей
- Настройки времени

**Что нужно сделать:**

**День 1-2: Расширение функционала геолокации (локально и деплой)**
- Найти существующий агент геолокации на сервере
- Добавить методы приблизительного местоположения (радиус)
- Реализовать метод `get_bubble_location(user_id, radius)`
- Настройки радиуса (100м, 500м, 1км)
- Настройки для разных людей
- Настройки времени

**День 3: API endpoints (локально и деплой)**
- Добавить `/api/location/bubble` (POST)
- Добавить `/api/location/bubble/settings` (GET)
- Тестирование API

**День 4: Интеграция в iOS (локально)**
- Добавить endpoints в `AppConfig.swift`
- Добавить методы в `APIService.swift`
- Обновить UI экран геолокации
- Добавить настройки пузыря

**День 5: Тестирование**
- Unit-тесты
- Интеграционные тесты
- Тестирование отображения пузыря
- Исправление найденных ошибок

**Ключевые файлы:**
- Сервер: Существующий агент геолокации (обновить)
- iOS: Существующий экран геолокации (обновить)
- iOS: `Core/Config/AppConfig.swift` (обновить)
- iOS: `Core/Network/APIService.swift` (обновить)

---

## 🔧 ТЕХНИЧЕСКИЕ ДЕТАЛИ

### Базовый класс SecurityBase

Все новые агенты должны наследоваться от `SecurityBase`:

```python
from security.base import SecurityBase
from typing import Optional, Dict, Any

class NewAgent(SecurityBase):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Ваша инициализация
```

### Регистрация в SFM

Все новые агенты должны быть зарегистрированы в `function_registry.json`:

```json
{
  "name": "agent_name",
  "type": "ai_agent",
  "path": "/opt/aladdin-backend/security/ai_agents/agent_name.py",
  "class": "AgentClassName",
  "functions": [
    {
      "name": "function_name",
      "description": "Описание функции",
      "parameters": ["param1: type", "param2: type"],
      "returns": "ReturnType"
    }
  ],
  "dependencies": ["dependency1", "dependency2"],
  "status": "active"
}
```

### API Endpoints

Все API endpoints должны быть добавлены в `/opt/aladdin-backend/api/main.py`:

```python
from flask import Flask, request, jsonify
from security.ai_agents.agent_name import AgentClass

app = Flask(__name__)
agent = AgentClass()

@app.route('/api/endpoint-name', methods=['POST'])
def endpoint_function():
    try:
        data = request.json
        # Валидация данных
        if not data.get('required_field'):
            return jsonify({"error": "required_field is required"}), 400
        
        # Вызов агента
        result = agent.function_name(data)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### iOS Integration

**AppConfig.swift:**
```swift
enum Endpoint {
    static let newEndpoint = "/api/endpoint-name"
}
```

**APIService.swift:**
```swift
func newFunction(param: String, completion: @escaping (Result<ResponseModel, Error>) -> Void) {
    networkManager.post(
        endpoint: AppConfig.Endpoint.newEndpoint,
        body: RequestModel(param: param),
        completion: completion
    )
}
```

**APIModels.swift:**
```swift
struct RequestModel: Codable {
    let param: String
}

struct ResponseModel: Codable {
    let result: String
}
```

**Screen.swift:**
```swift
import SwiftUI

struct NewScreen: View {
    @StateObject private var viewModel = NewViewModel()
    
    var body: some View {
        // UI код
    }
}
```

---

## 🔗 ИНТЕГРАЦИЯ С СУЩЕСТВУЮЩИМИ КОМПОНЕНТАМИ

### Использование ThreatIntelligenceAgent (для Dark Web мониторинга)

```python
from security.ai_agents.threat_intelligence_agent import ThreatIntelligenceAgent

class DarkWebMonitoringAgent(SecurityBase):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Используем утилиты из ThreatIntelligenceAgent
        self.threat_intel = ThreatIntelligenceAgent()
        self.api_validator = self.threat_intel._validate_email
        self.http_client = self.threat_intel._make_http_request
        self.logger = self.threat_intel.logger
```

### Использование RussianDataProtectionManager (для Identity Theft Protection)

```python
from security.compliance.russian_data_protection_manager import RussianDataProtectionManager

class RussianIdentityTheftProtectionAgent(SecurityBase):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.data_protection = RussianDataProtectionManager()
        
    def monitor_snils(self, snils: str):
        # Шифрование СНИЛС (AES-256)
        encrypted_snils = self.data_protection.encrypt_data(snils)
        # ...
```

### Расширение enhanced_social_media_bot.py

```python
# В файле /opt/aladdin-backend/security/bots/enhanced_social_media_bot.py

class SocialPlatform(Enum):
    # Существующие платформы
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    VK = "vk"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    
    # Добавить новые:
    MAX = "max"
    ODNOKLASSNIKI = "odnoklassniki"
```

### Расширение data_protection_manager.py

```python
# В файле /opt/aladdin-backend/security/data_protection_manager.py

class DataProtectionManager:
    # Существующие методы
    def _cleanup_expired_data(self):
        # ...
    
    # Добавить новые методы:
    def find_data_on_broker_sites(self, user_data: dict):
        """Поиск данных на брокерских сайтах"""
        # ...
    
    def remove_data_from_broker_sites(self, user_data: dict, sites: list):
        """Удаление данных с брокерских сайтов"""
        # ...
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Unit-тесты

Создайте файл `backend_tests/test_agent_name.py`:

```python
import pytest
from backend_agents.agent_name import AgentClass

def test_function_name():
    agent = AgentClass()
    result = agent.function_name("test_param")
    assert result is not None
    assert "expected_field" in result
```

Запуск тестов:
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
pytest backend_tests/test_agent_name.py
```

### Интеграционные тесты

Тестирование интеграции с существующими компонентами:

```python
def test_integration_with_existing_component():
    agent = AgentClass()
    existing_component = ExistingComponent()
    
    result = agent.function_that_uses_existing(existing_component)
    assert result is not None
```

### Тестирование API endpoints

```python
def test_api_endpoint():
    response = requests.post(
        "http://localhost:5000/api/endpoint-name",
        json={"param": "value"}
    )
    assert response.status_code == 200
    assert "result" in response.json()
```

---

## 🚀 ДЕПЛОЙ

### Отправка кода на сервер

```bash
# Отправить файл агента
scp backend_agents/agent_name.py root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# Подключиться к серверу
ssh root@149.154.65.180

# Проверить файл
cd /opt/aladdin-backend/security/ai_agents/
ls -la agent_name.py
```

### Регистрация в SFM

```bash
# На сервере
cd /opt/aladdin-backend/data/sfm/
nano function_registry.json
# Добавить запись для нового агента
```

### Тестирование на сервере

```bash
# На сервере
cd /opt/aladdin-backend
python -m pytest security/ai_agents/agent_name.py
```

---

## 📚 ССЫЛКИ НА ДОКУМЕНТЫ

### Основные документы

1. **TODO_ПОЛНЫЙ_СПИСОК_РЕАЛИЗАЦИИ.md** - Полный список всех задач с чекбоксами
2. **ЕДИНЫЙ_ПЛАН_РЕАЛИЗАЦИИ_ВСЕХ_ФУНКЦИЙ.md** - Единый план реализации
3. **АРХИТЕКТУРА_И_ПРОЦЕСС_РАЗРАБОТКИ.md** - Архитектура и процесс разработки
4. **ДЕТАЛЬНЫЙ_ПЛАН_РЕАЛИЗАЦИИ_ГИБРИДНЫЙ_ПОДХОД.md** - Детальный план для Dark Web мониторинга
5. **ОБОСНОВАНИЕ_ГИБРИДНОГО_ПОДХОДА.md** - Обоснование гибридного подхода
6. **ИТОГОВЫЙ_АНАЛИЗ_ВСЕХ_ФУНКЦИЙ_И_ПЛАН.md** - Итоговый анализ всех функций

### Дополнительные документы

7. **ПРОСТОЕ_ОБЪЯСНЕНИЕ_НОВЫХ_ФУНКЦИЙ.md** - Простое объяснение новых функций
8. **СРАВНИТЕЛЬНЫЙ_АНАЛИЗ_СЕМЕЙНОЙ_БЕЗОПАСНОСТИ_AURA_NORTON_ALADDIN.md** - Сравнение с конкурентами
9. **ПОЛНЫЙ_СРАВНИТЕЛЬНЫЙ_АНАЛИЗ_ВСЕХ_КОМПАНИЙ.md** - Полный анализ конкурентов

---

## ✅ ЧЕКЛИСТ ДЛЯ ML СИСТЕМЫ

### Перед началом реализации

- [ ] Прочитаны все документы из раздела "Ссылки на документы"
- [ ] Понятна архитектура системы
- [ ] Понятен процесс разработки (локально → тестирование → деплой)
- [ ] Понятны технические детали
- [ ] Понятна интеграция с существующими компонентами

### Во время реализации

- [ ] Код пишется локально в `backend_agents/`
- [ ] Используются существующие утилиты где возможно
- [ ] Соблюдаются принципы архитектуры (модульность, переиспользование)
- [ ] Код соответствует стандартам проекта
- [ ] Написаны unit-тесты
- [ ] Написаны интеграционные тесты

### После реализации

- [ ] Код протестирован локально
- [ ] Код отправлен на сервер
- [ ] Агент зарегистрирован в `function_registry.json`
- [ ] API endpoints добавлены в `main.py`
- [ ] iOS интеграция реализована
- [ ] Все тесты пройдены
- [ ] Документация обновлена

---

## 🎯 ИТОГОВАЯ СВОДКА

### Что нужно реализовать

**Фаза 1 (29-32 дня):**
1. Dark Web мониторинг (8-9 дней) - **ГИБРИДНЫЙ ПОДХОД**
2. Identity Theft Protection (18 дней)
3. Интеграция менеджера паролей (3-5 дней)

**Фаза 2 (17-22 дня):**
4. AI Categories (5-7 дней)
5. Расширенный Social Media Monitoring (2-3 дня) - **РАСШИРЕНИЕ**
6. Crash Detection (10-12 дней)

**Фаза 3 (36-46 дней):**
7. Driving Reports (8-10 дней)
8. Personal Data Cleanup (10-12 дней) - **РАСШИРЕНИЕ**
9. Anti-Tracker (5-7 дней)
10. Roadside Assistance (10-12 дней)
11. Bubbles Feature (3-5 дней) - **РАСШИРЕНИЕ**

### Общее время: 82-100 дней (~2.5-3.5 месяца)

---

**Дата создания:** 9 декабря 2025  
**Версия:** 1.0  
**Статус:** ✅ Готово к использованию  
**Автор:** AI Assistant для ALADDIN Project

---

## 📞 КОНТАКТЫ И ПОДДЕРЖКА

Если у ML системы возникнут вопросы:

1. Проверьте документы в разделе "Ссылки на документы"
2. Изучите существующий код на сервере
3. Следуйте примерам кода в этом документе
4. Используйте гибридный подход для Dark Web мониторинга
5. Расширяйте существующие модули где возможно

---

**Удачи в реализации! 🚀**
