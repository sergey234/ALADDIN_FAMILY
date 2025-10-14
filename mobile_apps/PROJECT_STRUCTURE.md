# 🏗️ СТРУКТУРА МОБИЛЬНЫХ ПРОЕКТОВ

**Дата:** 11 октября 2025  
**Статус:** ✅ Структура создана  
**Готовность:** Готово к разработке

---

## 📊 **ОБЗОР**

Создано **2 проекта**:
- 📱 **ALADDIN_iOS** - приложение для iPhone/iPad
- 🤖 **ALADDIN_Android** - приложение для Android

Оба проекта имеют **идентичную архитектуру MVVM** для упрощения разработки.

---

## 📁 **ОБЩАЯ СТРУКТУРА**

```
mobile_apps/
├── ALADDIN_iOS/              📱 iOS проект
│   ├── App/                  ← Точка входа
│   ├── Core/                 ← Базовая функциональность
│   ├── Features/             ← 14 экранов (каждый = папка)
│   ├── Shared/               ← Переиспользуемые компоненты
│   ├── Resources/            ← Ресурсы (картинки, переводы)
│   ├── Tests/                ← Тесты
│   └── README.md             ← Инструкция
│
└── ALADDIN_Android/          🤖 Android проект
    ├── app/src/main/         ← Основной код
    ├── core/                 ← Базовая функциональность
    ├── features/             ← 14 экранов (каждый = package)
    ├── shared/               ← Переиспользуемые компоненты
    ├── res/                  ← Ресурсы Android
    ├── test/                 ← Тесты
    └── README.md             ← Инструкция
```

---

## 🎯 **АРХИТЕКТУРА: MVVM**

### **Одинаковая для iOS и Android!**

```
┌─────────────────────────────────────────────────┐
│                    VIEW                         │
│  SwiftUI (iOS) или Compose (Android)           │
│  - Только отображение                           │
│  - Никакой бизнес-логики                        │
└────────────┬────────────────────────────────────┘
             │ @Published / StateFlow
             ↓
┌─────────────────────────────────────────────────┐
│                 VIEWMODEL                       │
│  - Бизнес-логика                                │
│  - Состояние экрана                             │
│  - Взаимодействие с Repository                  │
└────────────┬────────────────────────────────────┘
             │ data operations
             ↓
┌─────────────────────────────────────────────────┐
│                   MODEL                         │
│  - Простые данные (Struct/Data class)          │
│  - Без логики                                   │
└─────────────────────────────────────────────────┘
```

---

## 📱 **14 ЭКРАНОВ (FEATURES)**

### **Каждый экран = отдельная папка/package:**

| № | Название | iOS Папка | Android Package | HTML Источник |
|---|----------|-----------|-----------------|---------------|
| 1 | Главный | Features/Main | features.main | 01_main_screen.html |
| 2 | Семья | Features/Family | features.family | 03_family_screen.html |
| 3 | VPN | Features/Protection | features.protection | 02_protection_screen.html |
| 4 | Аналитика | Features/Analytics | features.analytics | 04_analytics_screen.html |
| 5 | Настройки | Features/Settings | features.settings | 05_settings_screen.html |
| 6 | Родительский | Features/ParentalControl | features.parental | 14_parental_control_screen.html |
| 7 | AI | Features/AIAssistant | features.ai | 08_ai_assistant.html |
| 8 | Профиль | Features/Profile | features.profile | 11_profile_screen.html |
| 9 | Устройства | Features/Devices | features.devices | 12_devices_screen.html |
| 10 | Детский | Features/Child | features.child | 06_child_interface.html |
| 11 | Пожилые | Features/Elderly | features.elderly | 07_elderly_interface.html |
| 12 | Тарифы | Features/Tariffs | features.tariffs | 09_tariffs_screen.html |
| 13 | Инфо | Features/Info | features.info | 10_info_screen.html |
| 14 | Уведомления | Features/Notifications | features.notifications | 08_notifications_screen.html |

---

## 📂 **СТРУКТУРА ОДНОГО ЭКРАНА**

### **iOS (Swift + SwiftUI):**
```
Features/Main/
├── Views/                    # UI компоненты
│   ├── MainScreen.swift      ← Основной экран (View)
│   ├── StatusCard.swift      ← Карточка статуса
│   └── FunctionCard.swift    ← Карточка функции
├── ViewModels/               # Логика
│   └── MainViewModel.swift   ← ObservableObject с @Published
└── Models/                   # Данные
    ├── MainStatus.swift      ← Struct с данными статуса
    └── FunctionItem.swift    ← Struct функции
```

### **Android (Kotlin + Compose):**
```
features/main/
├── ui/                       # UI компоненты
│   ├── MainScreen.kt         ← Composable экран
│   ├── StatusCard.kt         ← Composable карточка
│   └── FunctionCard.kt       ← Composable функция
├── viewmodel/                # Логика
│   └── MainViewModel.kt      ← ViewModel с StateFlow
└── model/                    # Данные
    ├── MainStatus.kt         ← Data class статуса
    └── FunctionItem.kt       ← Data class функции
```

---

## 🎨 **ДИЗАЙН-СИСТЕМА**

### **Цвета (одинаковые для iOS и Android):**

| Название | HEX | Использование |
|----------|-----|---------------|
| Primary Blue | #2E5BFF | Основной цвет, кнопки |
| Secondary Gold | #FCD34D | Акценты, иконки |
| Success Green | #10B981 | Успех, статус OK |
| Danger Red | #EF4444 | Ошибки, угрозы |
| Warning Orange | #F59E0B | Предупреждения |
| Background Dark | #0F172A | Фон приложения |
| Surface Dark | #1E293B | Карточки, модалки |
| Text Primary | #FFFFFF | Основной текст |
| Text Secondary | #94A3B8 | Вторичный текст |

### **Типография:**

| Стиль | Размер | Вес | Использование |
|-------|--------|-----|---------------|
| H1 | 32px | Bold | Заголовки экранов |
| H2 | 24px | Bold | Подзаголовки |
| H3 | 20px | Semi-Bold | Секции |
| Body | 16px | Regular | Основной текст |
| Caption | 14px | Regular | Подписи |
| Small | 12px | Regular | Мелкий текст |

---

## 📋 **СТАТИСТИКА СТРУКТУРЫ**

### **iOS проект:**
```
Папок создано:     78
├── App:           1
├── Core:          4 категории
├── Features:      15 features × 3 папки = 45
├── Shared:        3 категории × 3 = 9
├── Resources:     1
└── Tests:         2

Файлов будет:     ~200-250
```

### **Android проект:**
```
Папок создано:     78
├── core:          4 категории
├── features:      15 features × 3 папки = 45
├── shared:        3 категории × 3 = 9
├── res:           5 категорий
└── test:          2

Файлов будет:     ~200-250
```

---

## 🔗 **СВЯЗЬ С HTML WIREFRAMES**

### **Как использовать:**

```
Шаг 1: Разработчик открывает HTML
├── /Users/sergejhlystov/ALADDIN_NEW/mobile/wireframes/
└── Например: 01_main_screen.html

Шаг 2: Изучает дизайн
├── Смотрит какие элементы
├── Смотрит цвета в CSS
├── Смотрит размеры
└── Смотрит логику в JavaScript

Шаг 3: Создаёт файлы
iOS:
├── Features/Main/Views/MainScreen.swift
├── Features/Main/ViewModels/MainViewModel.swift
└── Features/Main/Models/MainStatus.swift

Android:
├── features/main/ui/MainScreen.kt
├── features/main/viewmodel/MainViewModel.kt
└── features/main/model/MainStatus.kt

Шаг 4: Копирует дизайн и логику из HTML в SwiftUI/Compose

Шаг 5: Тестирует
└── Сравнивает с HTML: "Выглядит так же?" → ДА ✅
```

---

## 🚀 **ПОРЯДОК РАЗРАБОТКИ**

### **Неделя 1: Setup + 4 экрана**
```
1. Setup проекта (Xcode/Android Studio)
2. Базовая навигация
3. Дизайн-система (Colors, Fonts)
4. Shared компоненты (Buttons, Cards)
5. MainScreen
6. FamilyScreen
7. ProtectionScreen
8. AnalyticsScreen
```

### **Неделя 2: 3 экрана**
```
9. SettingsScreen
10. ParentalControlScreen
11. AIAssistantScreen
```

### **Неделя 3: 7 экранов**
```
12. ProfileScreen
13. DevicesScreen
14. ChildInterfaceScreen
15. ElderlyInterfaceScreen
16. TariffsScreen
17. InfoScreen
18. NotificationsScreen
```

---

## ✅ **КРИТЕРИИ КАЧЕСТВА**

### **Для каждого экрана:**

**Code Quality:**
- ✅ SwiftLint / Ktlint без ошибок
- ✅ Code review пройден
- ✅ Комментарии к коду

**Functionality:**
- ✅ Работает как в HTML
- ✅ Все кнопки кликабельны
- ✅ Переходы работают
- ✅ Данные с API загружаются

**Performance:**
- ✅ Запуск экрана < 300ms
- ✅ Плавная прокрутка (60 FPS)
- ✅ Нет утечек памяти

**Accessibility:**
- ✅ VoiceOver/TalkBack labels
- ✅ Минимум кнопок 44×44pt
- ✅ Контраст текста достаточный

**Tests:**
- ✅ Unit tests для ViewModel
- ✅ UI tests для критичных flow
- ✅ Coverage > 70%

---

## 📞 **SUPPORT**

**Вопросы по структуре:**
- См. TECHNICAL_SPECIFICATION.md
- См. README.md в каждом проекте

**Вопросы по дизайну:**
- См. HTML wireframes в `/mobile/wireframes/`
- См. DESIGN_FORMATS_COMPARISON.md

---

## 🎯 **NEXT STEPS**

1. ✅ Структура создана
2. ⏳ Создать конфигурационные файлы
3. ⏳ Создать базовые компоненты
4. ⏳ Начать разработку первого экрана

---

**Создано:** 11 октября 2025  
**Папок:** 156 (78 iOS + 78 Android)  
**Статус:** ✅ Структура готова



