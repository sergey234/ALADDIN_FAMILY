# 📱 ТЕХНИЧЕСКОЕ ЗАДАНИЕ: ALADDIN FAMILY SECURITY - МОБИЛЬНЫЕ ПРИЛОЖЕНИЯ

**Дата:** 11 октября 2025  
**Версия:** 1.0.0  
**Статус:** Утверждено к разработке  
**Цель:** Создание iOS и Android приложений

---

## 🎯 **ЦЕЛЬ ПРОЕКТА**

Разработать мобильные приложения **ALADDIN Family Security** для iOS и Android с полным функционалом семейной безопасности, VPN защиты, родительского контроля и AI помощника.

---

## 📋 **СОДЕРЖАНИЕ**

1. Общее описание
2. Целевая аудитория
3. Функциональные требования
4. Технический стек
5. Архитектура приложения
6. Список экранов (14 шт)
7. API интеграция
8. Дизайн и UI/UX
9. Безопасность
10. Тестирование
11. Сроки и бюджет
12. Критерии приёмки

---

## 1. 📖 **ОБЩЕЕ ОПИСАНИЕ**

### **Название:** ALADDIN Family Security

### **Описание:**
Мобильное приложение для комплексной защиты семьи в интернете с функциями:
- 🛡️ VPN защита всех устройств
- 👨‍👩‍👧‍👦 Контроль безопасности членов семьи
- 👶 Родительский контроль (28 функций)
- 📊 Аналитика угроз в реальном времени
- 🤖 AI помощник по кибербезопасности
- 📍 Геолокация членов семьи
- 🚨 Обнаружение мошенников и фишинга

### **Платформы:**
- iOS 14.0+ (iPhone, iPad)
- Android 8.0+ (API 26+)

### **Языки:**
- Русский (основной)
- Английский (дополнительно)

---

## 2. 👥 **ЦЕЛЕВАЯ АУДИТОРИЯ**

### **Основные сегменты:**

1. **Семьи с детьми (70%)**
   - Родители 30-45 лет
   - Дети 8-17 лет
   - 2-6 членов семьи
   - Забота о безопасности детей

2. **Корпоративные пользователи (20%)**
   - Малый и средний бизнес
   - Защита корпоративных данных
   - VPN для сотрудников

3. **Индивидуальные пользователи (10%)**
   - Одиночки или пары
   - Забота о личной безопасности
   - VPN для конфиденциальности

---

## 3. 🎯 **ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ**

### **3.1. Авторизация и регистрация**

**FR-001:** Регистрация через email/телефон
- Валидация email (regex)
- Подтверждение через код (SMS/Email)
- Минимум 8 символов пароль

**FR-002:** OAuth 2.0 авторизация
- Вход через Google
- Вход через Apple ID
- Вход через VK

**FR-003:** Восстановление пароля
- Через email
- Через SMS
- Безопасный токен

---

### **3.2. Главный экран (MainScreen)**

**FR-004:** Отображение статуса семьи
- Общий статус: "Защищено" 🟢 / "Угрозы" 🔴
- Количество активных угроз
- Статус VPN (подключен/отключен)

**FR-005:** 4 главные карточки функций
- 👨‍👩‍👧‍👦 Семья → переход на FamilyScreen
- 🛡️ Защита → переход на ProtectionScreen
- 📊 Аналитика → переход на AnalyticsScreen
- 🤖 AI помощник → переход на AIAssistantScreen

**FR-006:** Быстрые действия
- Кнопка экстренного отключения VPN
- Уведомления (badge с количеством)

---

### **3.3. Семейный экран (FamilyScreen)**

**FR-007:** Список членов семьи
- Карточки всех членов (до 6)
- Фото, имя, возраст, роль
- Индикатор статуса 🟢🔴
- Последняя активность

**FR-008:** 4 карточки контроля
- 👁️ Мошенники (обнаружены/нет)
- 🚨 Угрозы (заблокировано сегодня)
- 📍 Геолокация (показать на карте)
- 💪 Здоровье (шаги, активность)

**FR-009:** Управление семьёй
- Добавить члена семьи
- Редактировать профиль члена
- Удалить члена семьи (с подтверждением)
- Назначить роль (Админ/Родитель/Ребёнок)

**FR-010:** Модальные окна
- Детали мошенников (список, описание)
- Детали угроз (тип, время, действие)
- Карта геолокации (Apple Maps / Google Maps)
- Статистика здоровья (графики)

---

### **3.4. VPN защита (ProtectionScreen)**

**FR-011:** Управление VPN
- Кнопка ВКЛ/ВЫКЛ (большая, центральная)
- Статус подключения (Подключено/Отключено/Подключение...)
- Автоматическое переподключение

**FR-012:** Выбор сервера
- Список стран (10+ серверов)
- Флаги стран
- Пинг (задержка)
- Нагрузка сервера (%)
- Рекомендуемый сервер (звёздочка)

**FR-013:** Статистика VPN
- Скорость загрузки/отдачи (реальное время)
- Трафик за день/неделю/месяц
- Время подключения
- Угроз заблокировано

**FR-014:** Список устройств с VPN
- Все устройства семьи
- Статус VPN на каждом
- Возможность отключить VPN удалённо

---

### **3.5. Аналитика (AnalyticsScreen)**

**FR-015:** Графики угроз
- Линейный график по дням/неделям/месяцам
- Круговая диаграмма по типам угроз
- Столбчатая диаграмма по членам семьи
- Интерактивность (tap для деталей)

**FR-016:** Фильтры
- По времени: День / Неделя / Месяц / Год
- По типу: Все / Фишинг / Вредоносное / Мошенники
- По члену семьи: Все / Конкретный

**FR-017:** Статистика
- Всего угроз заблокировано
- Фишинг-сайтов
- Мошенников обнаружено
- VPN трафик
- Самый опасный час
- Самый безопасный член семьи

**FR-018:** Экспорт отчётов
- PDF отчёт за период
- Отправка на email
- Сохранение в файлы

---

### **3.6. Настройки (SettingsScreen)**

**FR-019:** Аккордеон секций
- 🔒 Безопасность
- 🔔 Уведомления
- 👤 Профиль
- 💳 Подписка
- ⚙️ Дополнительно

**FR-020:** Секция "Безопасность"
- Двухфакторная аутентификация (2FA)
- Биометрия (Face ID / Touch ID / Fingerprint)
- PIN-код для приложения
- Автоматическая блокировка (время)
- Безопасный поиск
- Блокировка контента 18+

**FR-021:** Секция "Уведомления"
- Push-уведомления (ВКЛ/ВЫКЛ)
- Email уведомления
- SMS уведомления
- Типы уведомлений (угрозы, семья, VPN, система)
- Тихий режим (расписание)

**FR-022:** Секция "Профиль"
- Редактировать данные
- Изменить email
- Изменить пароль
- Изменить фото
- Удалить аккаунт (с подтверждением)

**FR-023:** Секция "Подписка"
- Текущий тариф
- Дата следующего платежа
- Изменить тариф
- История платежей
- Отменить подписку

**FR-024:** Секция "Дополнительно"
- Язык интерфейса (RU/EN)
- Тема оформления (Светлая/Тёмная/Авто)
- Единицы измерения
- О приложении
- Политика конфиденциальности
- Условия использования
- Поддержка

---

### **3.7. Родительский контроль (ParentalControlScreen)**

**FR-025:** 28 функций контроля

#### **Время экрана:**
1. Ограничение времени экрана (часы/день)
2. Расписание использования (с/по)
3. Блокировка на ночь
4. Время для сна

#### **Контент:**
5. Безопасный поиск
6. Блокировка контента 18+
7. Блокировка сайтов (чёрный список)
8. Разрешённые сайты (белый список)
9. Блокировка приложений
10. Возрастные ограничения (4+/9+/12+/17+)

#### **Приложения:**
11. Контроль установки приложений
12. Блокировка покупок в приложениях
13. Ограничение по категориям (игры, соцсети и т.д.)
14. Время использования по приложениям

#### **Геолокация:**
15. Отслеживание геолокации
16. Безопасные зоны (дом, школа)
17. Уведомления при входе/выходе из зон
18. История перемещений

#### **Социальные сети:**
19. Мониторинг активности в соцсетях
20. Обнаружение кибербуллинга
21. Контроль контактов
22. Фильтр нецензурной лексики

#### **Связь:**
23. Контроль звонков (входящих/исходящих)
24. Контроль SMS
25. Блокировка номеров

#### **Дополнительно:**
26. Скриншоты экрана (периодически)
27. История браузера
28. Отчёты родителям (ежедневно/еженедельно)

**FR-026:** Настройки по ребёнку
- Индивидуальные настройки для каждого ребёнка
- Профили: Строгий / Умеренный / Свободный
- Возможность временно отключить контроль

---

### **3.8. AI Помощник (AIAssistantScreen)**

**FR-027:** Чат с AI
- Интерфейс как WhatsApp/Telegram
- Сообщения пользователя (справа, синие)
- Ответы AI (слева, серые)
- Аватар AI

**FR-028:** Функции AI
- Ответы на вопросы о безопасности
- Проверка ссылок на фишинг
- Анализ подозрительных сообщений
- Советы по защите
- Обучение кибербезопасности

**FR-029:** Быстрые вопросы
- "Как защититься от фишинга?"
- "Безопасен ли этот сайт?"
- "Что делать если взломали аккаунт?"
- "Как создать сильный пароль?"

**FR-030:** История
- Сохранение всех диалогов
- Поиск по истории
- Удаление истории

---

### **3.9. Профиль (ProfileScreen)**

**FR-031:** Информация пользователя
- Фото профиля (загрузка/изменение)
- Имя и фамилия
- Email
- Телефон
- Дата рождения
- Роль в семье

**FR-032:** Статистика пользователя
- Дней в ALADDIN
- Угроз заблокировано (лично)
- VPN трафик (лично)
- Достижения (бейджи)

**FR-033:** Действия
- Редактировать профиль
- Изменить пароль
- Настройки конфиденциальности
- Выйти из аккаунта

---

### **3.10. Устройства (DevicesScreen)**

**FR-034:** Список устройств
- Все устройства семьи
- Название устройства
- Модель (iPhone 15 Pro, Samsung Galaxy и т.д.)
- Владелец
- Статус (Онлайн 🟢 / Офлайн 🔴)
- Последняя активность
- VPN статус

**FR-035:** Управление устройствами
- Добавить новое устройство
- Удалить устройство
- Переименовать устройство
- Отключить VPN удалённо
- Заблокировать устройство (для детей)

**FR-036:** Детали устройства (модальное окно)
- Подробная информация
- IP адрес
- Операционная система
- Версия приложения
- Статистика использования
- История подключений

---

### **3.11. Детский интерфейс (ChildInterfaceScreen)**

**FR-037:** Игровой режим
- Яркие цвета и картинки
- Крупные кнопки
- Простое меню

**FR-038:** Достижения
- 🏅 Использовал VPN 7 дней подряд
- ⭐ Не кликнул на фишинг-ссылку
- 💪 Создал сильный пароль
- 🎯 Прошёл 5 уроков безопасности
- 🏆 Месяц без угроз

**FR-039:** Мини-игры
- Викторина по кибербезопасности
- "Найди фишинг" (игра)
- "Создай пароль" (обучение)

**FR-040:** Прогресс
- Уровень безопасности (1-10)
- Опыт (XP)
- Рейтинг среди друзей

---

### **3.12. Интерфейс для пожилых (ElderlyInterfaceScreen)**

**FR-041:** Упрощённый дизайн
- Крупный шрифт (22-28px)
- Большие кнопки (мин 60×60pt)
- Высокий контраст
- Минимум элементов на экране

**FR-042:** Экстренная помощь
- 🆘 ОГРОМНАЯ кнопка SOS (красная, всегда видна)
- Быстрый вызов экстренных служб
- Отправка геолокации близким
- Голосовое сообщение

**FR-043:** Голосовое управление
- Активация голосом
- Основные команды голосом
- Озвучивание статуса

**FR-044:** Упрощённое меню
- Только важные функции:
  - VPN ВКЛ/ВЫКЛ
  - Статус семьи
  - SOS кнопка
  - Связь с близкими

---

### **3.13. Тарифы (TariffsScreen)**

**FR-045:** 3 тарифа

#### **BASIC (290₽/мес):**
- 1 пользователь
- VPN базовый (10 ГБ/мес)
- Базовая защита
- 3 устройства

#### **FAMILY (490₽/мес):** ⭐ Рекомендуем
- До 6 пользователей
- VPN неограниченный
- Полная защита
- Родительский контроль
- AI помощник
- Геолокация
- Неограниченно устройств

#### **PREMIUM (900₽/мес):**
- До 10 пользователей
- VPN Premium (быстрые серверы)
- Максимальная защита
- Всё из FAMILY +
- Приоритетная поддержка
- Персональный AI ассистент
- Бизнес функции

**FR-046:** Оплата
- Месячная подписка
- Годовая подписка (-20%)
- Пробный период (7 дней бесплатно)
- Apple Pay / Google Pay
- Карта (через Stripe/Tinkoff)

**FR-047:** Управление подпиской
- Изменить тариф (upgrade/downgrade)
- Отменить подписку
- История платежей
- Скачать чек

---

### **3.14. Информация (InfoScreen)**

**FR-048:** О приложении
- Версия приложения
- Дата релиза
- Changelog (что нового)

**FR-049:** О компании
- Описание ALADDIN Security
- Миссия и ценности
- Команда

**FR-050:** Контакты
- Email: support@aladdin.family
- Telegram: @aladdin_support
- Телефон: +7 (495) 123-45-67
- Сайт: https://aladdin.family

**FR-051:** Документы
- Политика конфиденциальности
- Условия использования
- Лицензионное соглашение

**FR-052:** FAQ
- 20 частых вопросов
- Поиск по FAQ
- Видео-инструкции

---

### **3.15. Уведомления (NotificationsScreen)**

**FR-053:** Список уведомлений
- Сортировка: Новые → Старые
- Группировка по дням
- Типы:
  - 🚨 Угрозы (красные)
  - 👁️ Мошенники (оранжевые)
  - ✅ Система (зелёные)
  - 👨‍👩‍👧‍👦 Семья (синие)
  - 🛡️ VPN (фиолетовые)

**FR-054:** Фильтры
- Все
- Непрочитанные
- Важные
- По типу

**FR-055:** Действия
- Пометить прочитанным
- Удалить
- Удалить все
- Настройки уведомлений

**FR-056:** Детали уведомления
- Полное описание
- Время
- Рекомендуемые действия
- Кнопки быстрых действий

---

## 4. 💻 **ТЕХНИЧЕСКИЙ СТЕК**

### **4.1. iOS**

**Язык:** Swift 5.9+
**UI Framework:** SwiftUI
**Минимальная версия:** iOS 14.0+
**Architecture:** MVVM (Model-View-ViewModel)

**Основные библиотеки:**
```swift
// Networking
- Alamofire 5.x (HTTP requests)
- Moya (Network abstraction)

// Storage
- Realm / Core Data (local database)
- KeychainAccess (secure storage)

// UI
- SwiftUI Charts (graphs)
- Kingfisher (image loading)
- SDWebImage (caching)

// VPN
- NetworkExtension (VPN tunnel)
- WireGuard (VPN protocol)

// Analytics
- Firebase Analytics
- Firebase Crashlytics

// Push Notifications
- Firebase Cloud Messaging

// Maps
- MapKit (Apple Maps)

// Authentication
- AuthenticationServices (Sign in with Apple)
- GoogleSignIn

// Payment
- StoreKit 2 (In-App Purchase)

// AI
- OpenAI SDK

// Other
- SwiftLint (code style)
- Combine (reactive programming)
```

---

### **4.2. Android**

**Язык:** Kotlin 1.9+
**UI Framework:** Jetpack Compose
**Минимальная версия:** Android 8.0 (API 26+)
**Architecture:** MVVM (Model-View-ViewModel)

**Основные библиотеки:**
```kotlin
// Networking
- Retrofit 2.x (HTTP requests)
- OkHttp 4.x (HTTP client)
- Moshi (JSON parsing)

// Storage
- Room (local database)
- DataStore (preferences)
- EncryptedSharedPreferences (secure storage)

// UI
- Jetpack Compose
- Accompanist (Compose utilities)
- Coil (image loading)

// VPN
- Android VPN Service
- WireGuard

// Analytics
- Firebase Analytics
- Firebase Crashlytics

// Push Notifications
- Firebase Cloud Messaging

// Maps
- Google Maps SDK

// Authentication
- Google Sign In
- VK SDK

// Payment
- Google Play Billing

// AI
- OpenAI SDK

// Other
- Kotlin Coroutines (async)
- Flow (reactive)
- Hilt (dependency injection)
- Ktlint (code style)
```

---

### **4.3. Backend (уже существует)**

**API:** REST API (78 endpoints готовы)
**Base URL:** https://api.aladdin.family/v1/
**Authentication:** JWT Bearer tokens
**Documentation:** Swagger/OpenAPI 3.0

---

## 5. 🏗️ **АРХИТЕКТУРА ПРИЛОЖЕНИЯ**

### **5.1. Архитектурный паттерн: MVVM**

```
View (UI)
   ↓↑
ViewModel (Logic)
   ↓↑
Model (Data)
   ↓↑
Repository (API/DB)
```

### **5.2. Структура проекта iOS**

```
ALADDIN_iOS/
├── App/
│   ├── ALADDINApp.swift         # App entry point
│   ├── AppDelegate.swift
│   └── SceneDelegate.swift
├── Core/
│   ├── Networking/
│   │   ├── APIClient.swift
│   │   ├── Endpoints.swift
│   │   └── NetworkError.swift
│   ├── Storage/
│   │   ├── DatabaseManager.swift
│   │   └── KeychainManager.swift
│   ├── VPN/
│   │   ├── VPNManager.swift
│   │   └── WireGuardTunnel.swift
│   └── Utilities/
│       ├── Logger.swift
│       └── Constants.swift
├── Features/
│   ├── Auth/
│   │   ├── Views/
│   │   │   ├── LoginView.swift
│   │   │   └── RegisterView.swift
│   │   ├── ViewModels/
│   │   │   └── AuthViewModel.swift
│   │   └── Models/
│   │       └── User.swift
│   ├── Main/
│   │   ├── Views/
│   │   │   └── MainScreen.swift
│   │   ├── ViewModels/
│   │   │   └── MainViewModel.swift
│   │   └── Models/
│   │       └── MainStatus.swift
│   ├── Family/
│   │   ├── Views/
│   │   ├── ViewModels/
│   │   └── Models/
│   ├── Protection/
│   ├── Analytics/
│   ├── Settings/
│   ├── ParentalControl/
│   ├── AIAssistant/
│   ├── Profile/
│   ├── Devices/
│   ├── Child/
│   ├── Elderly/
│   ├── Tariffs/
│   ├── Info/
│   └── Notifications/
├── Shared/
│   ├── Components/
│   │   ├── Buttons/
│   │   ├── Cards/
│   │   └── Modals/
│   ├── Extensions/
│   └── Styles/
├── Resources/
│   ├── Assets.xcassets
│   ├── Localizable.strings
│   └── Info.plist
└── Tests/
    ├── UnitTests/
    └── UITests/
```

### **5.3. Структура проекта Android**

```
ALADDIN_Android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/aladdin/familysecurity/
│   │   │   │   ├── ALADDINApplication.kt
│   │   │   │   ├── core/
│   │   │   │   │   ├── network/
│   │   │   │   │   ├── database/
│   │   │   │   │   ├── vpn/
│   │   │   │   │   └── utils/
│   │   │   │   ├── features/
│   │   │   │   │   ├── auth/
│   │   │   │   │   ├── main/
│   │   │   │   │   ├── family/
│   │   │   │   │   ├── protection/
│   │   │   │   │   ├── analytics/
│   │   │   │   │   ├── settings/
│   │   │   │   │   ├── parental/
│   │   │   │   │   ├── ai/
│   │   │   │   │   ├── profile/
│   │   │   │   │   ├── devices/
│   │   │   │   │   ├── child/
│   │   │   │   │   ├── elderly/
│   │   │   │   │   ├── tariffs/
│   │   │   │   │   ├── info/
│   │   │   │   │   └── notifications/
│   │   │   │   └── shared/
│   │   │   │       ├── components/
│   │   │   │       ├── theme/
│   │   │   │       └── utils/
│   │   │   ├── res/
│   │   │   │   ├── values/
│   │   │   │   ├── drawable/
│   │   │   │   └── layout/
│   │   │   └── AndroidManifest.xml
│   │   └── test/
│   └── build.gradle.kts
└── gradle/
```

---

## 6. 📱 **СПИСОК ЭКРАНОВ (14 ШТ)**

| № | Экран | Route | Приоритет | Время |
|---|-------|-------|-----------|-------|
| 1 | MainScreen | `/main` | 🔴 HIGH | 2 дня |
| 2 | FamilyScreen | `/family` | 🔴 HIGH | 2 дня |
| 3 | ProtectionScreen | `/protection` | 🔴 HIGH | 1.5 дня |
| 4 | AnalyticsScreen | `/analytics` | 🔴 HIGH | 2 дня |
| 5 | SettingsScreen | `/settings` | 🟠 MEDIUM | 1.5 дня |
| 6 | ParentalControlScreen | `/parental` | 🔴 HIGH | 2 дня |
| 7 | AIAssistantScreen | `/ai` | 🟠 MEDIUM | 1.5 дня |
| 8 | ProfileScreen | `/profile` | 🟠 MEDIUM | 1 день |
| 9 | DevicesScreen | `/devices` | 🟠 MEDIUM | 1 день |
| 10 | ChildInterfaceScreen | `/child` | 🟡 LOW | 1.5 дня |
| 11 | ElderlyInterfaceScreen | `/elderly` | 🟡 LOW | 1 день |
| 12 | TariffsScreen | `/tariffs` | 🟠 MEDIUM | 1 день |
| 13 | InfoScreen | `/info` | 🟡 LOW | 0.5 дня |
| 14 | NotificationsScreen | `/notifications` | 🟠 MEDIUM | 1 день |

**ИТОГО:** 19.5 дней разработки

---

## 7. 🌐 **API ИНТЕГРАЦИЯ**

### **7.1. Base URL**
```
Production: https://api.aladdin.family/v1/
Staging: https://staging-api.aladdin.family/v1/
Development: http://localhost:8000/api/v1/
```

### **7.2. Аутентификация**
```
Authorization: Bearer {JWT_TOKEN}
```

### **7.3. Основные endpoints**

#### **Auth:**
```
POST /auth/register          # Регистрация
POST /auth/login             # Вход
POST /auth/refresh           # Обновление токена
POST /auth/forgot-password   # Восстановление пароля
POST /auth/verify-email      # Подтверждение email
POST /auth/oauth/google      # OAuth Google
POST /auth/oauth/apple       # OAuth Apple
```

#### **Family:**
```
GET    /family                # Список семьи
POST   /family/members        # Добавить члена
PUT    /family/members/{id}   # Редактировать члена
DELETE /family/members/{id}   # Удалить члена
GET    /family/status         # Статус семьи
```

#### **VPN:**
```
POST   /vpn/connect           # Подключить VPN
POST   /vpn/disconnect        # Отключить VPN
GET    /vpn/status            # Статус VPN
GET    /vpn/servers           # Список серверов
GET    /vpn/stats             # Статистика VPN
```

#### **Threats:**
```
GET    /threats               # Список угроз
GET    /threats/{id}          # Детали угрозы
POST   /threats/report        # Сообщить об угрозе
GET    /threats/stats         # Статистика угроз
```

#### **Analytics:**
```
GET    /analytics/dashboard   # Дашборд
GET    /analytics/threats     # Графики угроз
GET    /analytics/vpn         # Статистика VPN
GET    /analytics/family      # По членам семьи
POST   /analytics/export      # Экспорт отчёта
```

#### **Parental Control:**
```
GET    /parental/settings/{child_id}  # Настройки ребёнка
PUT    /parental/settings/{child_id}  # Обновить настройки
GET    /parental/activity/{child_id}  # Активность ребёнка
POST   /parental/block                # Заблокировать контент
```

#### **AI Assistant:**
```
POST   /ai/chat               # Отправить сообщение
GET    /ai/history            # История чата
POST   /ai/check-url          # Проверить URL
POST   /ai/analyze-message    # Анализ сообщения
```

#### **Devices:**
```
GET    /devices               # Список устройств
POST   /devices/register      # Зарегистрировать устройство
PUT    /devices/{id}          # Обновить устройство
DELETE /devices/{id}          # Удалить устройство
POST   /devices/{id}/block    # Заблокировать устройство
```

#### **Notifications:**
```
GET    /notifications         # Список уведомлений
PUT    /notifications/{id}/read  # Прочитано
DELETE /notifications/{id}    # Удалить
POST   /notifications/settings # Настройки
```

#### **Subscription:**
```
GET    /subscription          # Текущая подписка
POST   /subscription/upgrade  # Изменить тариф
POST   /subscription/cancel   # Отменить
GET    /subscription/history  # История платежей
```

### **7.4. Response format**

**Success:**
```json
{
  "success": true,
  "data": {...},
  "message": "Success"
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "AUTH_FAILED",
    "message": "Invalid credentials"
  }
}
```

---

## 8. 🎨 **ДИЗАЙН И UI/UX**

### **8.1. Дизайн-система**

**Цвета:**
```
Primary: #2E5BFF (синий)
Secondary: #FCD34D (золотой)
Success: #10B981 (зелёный)
Danger: #EF4444 (красный)
Warning: #F59E0B (оранжевый)
Info: #3B82F6 (голубой)

Background: #0F172A (тёмно-синий)
Surface: #1E293B
Text Primary: #FFFFFF
Text Secondary: #94A3B8
```

**Типография:**
```
H1: 32px, Bold
H2: 24px, Bold
H3: 20px, Semi-Bold
Body: 16px, Regular
Caption: 14px, Regular
Small: 12px, Regular
```

**Отступы:**
```
XXS: 4px
XS: 8px
S: 12px
M: 16px
L: 24px
XL: 32px
XXL: 48px
```

**Радиусы:**
```
Small: 8px
Medium: 12px
Large: 16px
XLarge: 24px
Circle: 50%
```

**Тени:**
```
Small: 0 2px 4px rgba(0,0,0,0.1)
Medium: 0 4px 8px rgba(0,0,0,0.15)
Large: 0 8px 16px rgba(0,0,0,0.2)
```

### **8.2. Компоненты**

**Кнопки:**
- Primary (синяя, заполненная)
- Secondary (обводка)
- Danger (красная)
- Размеры: Small (32px), Medium (44px), Large (56px)

**Карточки:**
- Стандартная (белый фон, тень, rounded)
- Статус (с индикатором 🟢🔴)
- Кликабельная (с эффектом нажатия)

**Инпуты:**
- Text field (email, пароль, текст)
- Search field (с иконкой поиска)
- Select (выпадающий список)
- Switch (переключатель)
- Slider (ползунок)

**Индикаторы:**
- Progress bar (линейный)
- Progress circle (круговой)
- Spinner (загрузка)
- Badge (счётчик уведомлений)

---

## 9. 🔒 **БЕЗОПАСНОСТЬ**

### **9.1. Хранение данных**

**Чувствительные данные** (токены, пароли):
- iOS: Keychain
- Android: EncryptedSharedPreferences

**Обычные данные**:
- iOS: UserDefaults / Core Data
- Android: DataStore / Room

**Кэширование:**
- Максимум 7 дней
- Автоматическая очистка

### **9.2. Сетевая безопасность**

- **SSL Pinning** (certificate pinning)
- **TLS 1.3** обязательно
- **HTTP → HTTPS** редирект

### **9.3. Аутентификация**

- **JWT** токены (Access + Refresh)
- **Access token** lifetime: 15 минут
- **Refresh token** lifetime: 30 дней
- **Biometric** auth (Face ID / Touch ID / Fingerprint)
- **PIN-код** опционально

### **9.4. Код**

- **Code Obfuscation** перед релизом
- **ProGuard** (Android)
- **No hardcoded secrets** (API keys в environment)

---

## 10. ✅ **ТЕСТИРОВАНИЕ**

### **10.1. Unit Tests**

**Покрытие:** минимум 70%

**Что тестируем:**
- ViewModels (логика)
- Repositories (API calls)
- Utilities (helper functions)
- Models (data validation)

### **10.2. Integration Tests**

**Что тестируем:**
- API интеграция
- Database операции
- VPN подключение
- Push notifications

### **10.3. UI Tests**

**Что тестируем:**
- Навигация между экранами
- Формы (регистрация, логин)
- Основные user flows
- Accessibility

### **10.4. Manual Testing**

**Устройства:**
- iOS: iPhone SE, iPhone 15 Pro, iPad Pro
- Android: Pixel 6, Samsung Galaxy S23, различные версии

**Сценарии:**
- Happy path (всё работает)
- Error handling (сервер недоступен)
- Offline mode (нет интернета)
- Edge cases (пустые списки, длинные тексты)

---

## 11. ⏱️ **СРОКИ И БЮДЖЕТ**

### **11.1. Timeline**

**Неделя 1 (дни 1-7):**
- Setup + Навигация
- MainScreen, FamilyScreen
- ProtectionScreen, AnalyticsScreen
- Прогресс: 28%

**Неделя 2 (дни 8-14):**
- SettingsScreen
- ParentalControlScreen
- AIAssistantScreen
- Прогресс: 50%

**Неделя 3 (дни 15-21):**
- ProfileScreen, DevicesScreen
- ChildInterfaceScreen, ElderlyInterfaceScreen
- TariffsScreen, InfoScreen, NotificationsScreen
- Прогресс: 100%

**ИТОГО: 21 день (3 недели)**

### **11.2. Команда**

- 2 iOS разработчика (Senior)
- 2 Android разработчика (Senior)

### **11.3. Бюджет**

| Роль | Ставка | Время | Сумма |
|------|--------|-------|-------|
| iOS Developer #1 | 300K₽/мес | 0.75 мес | 225,000₽ |
| iOS Developer #2 | 300K₽/мес | 0.75 мес | 225,000₽ |
| Android Developer #1 | 300K₽/мес | 0.75 мес | 225,000₽ |
| Android Developer #2 | 300K₽/мес | 0.75 мес | 225,000₽ |
| **ИТОГО** | | **3 недели** | **900,000₽** |

---

## 12. ✅ **КРИТЕРИИ ПРИЁМКИ**

### **12.1. Функциональность**

- ✅ Все 14 экранов реализованы
- ✅ Навигация между экранами работает
- ✅ API интеграция работает (все endpoints)
- ✅ VPN подключается и отключается
- ✅ Родительский контроль функционирует
- ✅ AI помощник отвечает на вопросы
- ✅ Графики аналитики отображаются
- ✅ Push-уведомления работают
- ✅ Оплата через In-App Purchase работает

### **12.2. Качество кода**

- ✅ Unit tests coverage > 70%
- ✅ No critical bugs
- ✅ No memory leaks
- ✅ Code review passed
- ✅ Linter warnings = 0

### **12.3. Performance**

- ✅ App launch time < 3 секунд
- ✅ Screen transitions < 300ms
- ✅ API response time < 2 секунд
- ✅ Memory usage < 150 MB
- ✅ Battery drain < 5%/час

### **12.4. UI/UX**

- ✅ Responsive на всех устройствах
- ✅ Accessibility labels везде
- ✅ Dark mode поддерживается
- ✅ Animations smooth (60 FPS)
- ✅ No UI bugs

### **12.5. Безопасность**

- ✅ SSL Pinning реализован
- ✅ Tokens хранятся в Keychain/EncryptedPrefs
- ✅ No hardcoded secrets
- ✅ Code obfuscation перед релизом

---

## 13. 📚 **ДОКУМЕНТАЦИЯ**

### **13.1. Для разработчиков**

- README.md (как запустить проект)
- ARCHITECTURE.md (архитектура)
- API.md (документация API)
- TESTING.md (как запустить тесты)

### **13.2. Для дизайнеров**

- DESIGN_SYSTEM.md (цвета, шрифты, компоненты)
- FIGMA_GUIDE.md (как использовать Figma файлы)

### **13.3. Для QA**

- TEST_PLAN.md (план тестирования)
- TEST_CASES.md (тест-кейсы)
- BUG_REPORT_TEMPLATE.md (шаблон отчёта о баге)

---

## 14. 📞 **КОНТАКТЫ**

### **Product Owner:**
- Email: sergej.hlystov@aladdin.family

### **Technical Lead:**
- TBD

### **Design Lead:**
- TBD

---

## 15. ✍️ **УТВЕРЖДЕНИЕ**

**Подготовлено:** 11 октября 2025  
**Версия:** 1.0.0  
**Статус:** ✅ Утверждено к разработке

**Подпись Product Owner:** _________________

**Дата утверждения:** _________________

---

# 🎯 КОНЕЦ ТЕХНИЧЕСКОГО ЗАДАНИЯ

**Документ готов к передаче команде разработки!**

**Следующий шаг:** Создание структуры проекта (ШАГ B)



