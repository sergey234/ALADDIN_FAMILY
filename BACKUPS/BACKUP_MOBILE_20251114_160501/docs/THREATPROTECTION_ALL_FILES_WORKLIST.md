# 📁 ПОЛНЫЙ СПИСОК ФАЙЛОВ ДЛЯ РАБОТЫ: Система защиты от угроз

**Дата:** 2025-11-12  
**Статус:** Все файлы для реализации  
**Версия:** 1.0

---

## ✅ ЭТАП 0: ПОДГОТОВКА (ВЫПОЛНЕНО)

### 1. Конфигурация и API

#### ✅ `Core/Config/AppConfig.swift`
**Статус:** ✅ ИЗМЕНЁН  
**Что добавлено:**
- API endpoints для защиты от угроз
- `protectionSettings`, `protectionStatus`, `threatScenarios`, и т.д.

---

#### ✅ `Core/Network/APIService.swift`
**Статус:** ✅ ИЗМЕНЁН  
**Что добавлено:**
- Методы API для защиты от угроз
- `getProtectionSettings()`, `updateProtectionSettings()`, `getThreatScenarios()`, и т.д.

---

#### ✅ `Core/Models/APIModels.swift`
**Статус:** ✅ ИЗМЕНЁН  
**Что добавлено:**
- `ProtectionSettingsResponse`
- `ProtectionStatusResponse`
- `ThreatScenarioResponse`
- `ProtectionStatsResponse`

---

#### ✅ `Core/Navigation/NavigationManager.swift`
**Статус:** ✅ ИЗМЕНЁН  
**Что добавлено:**
- Новые экраны в enum `ALADDINScreen`
- `threatProtection`, `threatProtectionSettings`, `iotSecurity`, `advancedProtection`

---

#### ⚠️ `Core/Localization/LocalizationManager.swift`
**Статус:** ⚠️ ТРЕБУЕТ ИЗМЕНЕНИЯ  
**Что нужно добавить:**
- Новые ключи локализации для защиты от угроз
- `protection_settings_title`, `protection_what_this_gives`, и т.д.

---

## 🆕 ЭТАП 1: БАЗОВАЯ ИНФРАСТРУКТУРА

### 2. Модели данных

#### ⚠️ `Shared/Models/ThreatProtectionCategory.swift`
**Статус:** ⚠️ ИЗМЕНИТЬ (файл уже существует)  
**Путь:** `Shared/Models/ThreatProtectionCategory.swift`  
**Что уже есть:**
- ✅ Enum `ThreatProtectionCategory` с 9 категориями
- ✅ `emoji: String`
- ✅ `count: Int`
- ✅ `localizedTitle()` и `localizedThreats()`

**Что нужно добавить:**
- `requiredTariff: TariffType`
- `benefit: String`
- `settingsScreen: NavigationManager.ALADDINScreen?`
- `group: ProtectionGroup`

---

#### ⚠️ `Shared/Models/ProtectionGroup.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Shared/Models/ProtectionGroup.swift`  
**Что нужно:**
- Enum `ProtectionGroup`
- Cases: `.devices`, `.internet`, `.family`, `.finance`, `.premium`
- `categories: [ThreatProtectionCategory]`
- `icon: String`
- `color: Color`
- `gradient: LinearGradient`

---

#### ⚠️ `Shared/Models/ProtectionSettings.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Shared/Models/ProtectionSettings.swift`  
**Что нужно:**
- Struct `ProtectionSettings: Codable`
- Поля для каждой категории (Bool)
- Методы `isEnabled(_ category:)` и `setEnabled(_ category:, _ enabled:)`
- Вычисляемые свойства для групп

---

### 3. Менеджеры

#### ⚠️ `Core/Managers/ProtectionSettingsManager.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Core/Managers/ProtectionSettingsManager.swift`  
**Что нужно:**
- Класс `ProtectionSettingsManager: ObservableObject` (Singleton)
- `@Published var settings: ProtectionSettings`
- Методы `loadSettings()`, `saveSettings()`
- Методы `toggleCategory()`, `enableCategory()`, `disableCategory()`
- Метод `enableForTariff(_ tariff:)`
- Метод `isCategoryAvailable(_ category:, in tariff:)`
- Синхронизация с API (опционально)

---

#### ⚠️ `Core/Managers/TariffManager.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Core/Managers/TariffManager.swift`  
**Что нужно:**
- Класс `TariffManager: ObservableObject` (Singleton)
- `@Published var currentTariff: TariffType`
- Методы `loadTariff()`, `saveTariff(_ tariff:)`
- Расширение `TariffType` с `level: Int` property
- Observer для изменений тарифов (NotificationCenter)

---

## 🎨 ЭТАП 2: UI КОМПОНЕНТЫ

### 4. Компоненты

#### ⚠️ `Components/EnhancedThreatCategoryCard.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Components/EnhancedThreatCategoryCard.swift`  
**Что нужно:**
- Компонент расширенной карточки категории
- Статус-индикатор (🟢🟡🔴)
- Блок "Что это даёт"
- Кнопка "Подробнее"
- Мотивационный баннер (если недоступно)
- Анимация раскрытия (аккордеон)

---

#### ⚠️ `Components/MotivationBanner.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Components/MotivationBanner.swift`  
**Что нужно:**
- Компонент мотивационного баннера
- Иконка замка
- Текст "Требует тариф X"
- Кнопка "Обновить тариф"
- Навигация на экран тарифов

---

#### ⚠️ `Components/ThreatScenariosGallery.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Components/ThreatScenariosGallery.swift`  
**Что нужно:**
- Компонент галереи сценариев
- Горизонтальный ScrollView
- Карточки сценариев (`ThreatScenarioCard`)
- Модель `ThreatScenario`
- Загрузка сценариев из API или локальных данных

---

#### ⚠️ `Components/ThreatScenarioCard.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Components/ThreatScenarioCard.swift`  
**Что нужно:**
- Компонент карточки сценария
- Иконка сценария
- Название и описание
- Индикатор требуемого тарифа
- Кнопка "Как защититься" или "Получить защиту"

---

#### ⚠️ `Components/ProtectionCategoryRow.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Components/ProtectionCategoryRow.swift`  
**Что нужно:**
- Компонент строки категории в настройках
- Иконка категории
- Название и описание
- Переключатель (если доступно)
- Баннер (если недоступно)

---

#### ⚠️ `Components/ProtectionGroupSection.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Components/ProtectionGroupSection.swift`  
**Что нужно:**
- Компонент секции группы
- Заголовок группы с иконкой
- Список категорий в группе
- Градиентный фон для группы

---

## 📱 ЭТАП 3: ЭКРАНЫ

### 5. Экраны

#### ⚠️ `Screens/ThreatProtectionScreen.swift`
**Статус:** ⚠️ ИЗМЕНИТЬ  
**Путь:** `Screens/ThreatProtectionScreen.swift`  
**Что нужно изменить:**
- Добавить галерею сценариев (сверху)
- Обновить структуру с группами
- Интеграция с `EnhancedThreatCategoryCard`
- Интеграция с `ThreatScenariosGallery`

---

#### ⚠️ `Screens/ThreatProtectionSettingsScreen.swift`
**Статус:** ⚠️ СОЗДАТЬ  
**Путь:** `Screens/ThreatProtectionSettingsScreen.swift`  
**Что нужно:**
- Единый экран настроек защиты
- Группы категорий (вертикально)
- Переключатели для всех категорий
- Навигация на детальные экраны
- Интеграция с `ProtectionGroupSection`

---

#### ⚠️ `Components/ThreatProtectionCategoriesView.swift`
**Статус:** ⚠️ ИЗМЕНИТЬ (файл уже существует)  
**Путь:** `Components/ThreatProtectionCategoriesView.swift`  
**Что уже есть:**
- ✅ Базовый список категорий
- ✅ Раскрытие/сворачивание категорий
- ✅ Отображение списка угроз

**Что нужно изменить:**
- Группировка категорий по группам
- Использование `ProtectionGroupSection`
- Интеграция с `EnhancedThreatCategoryCard`
- Добавить статус-индикаторы, советы, кнопки

---

## 📊 СТРУКТУРА ФАЙЛОВ

```
ALADDIN_iOS/
├── Core/
│   ├── Config/
│   │   └── AppConfig.swift                    ✅ ИЗМЕНЁН
│   ├── Network/
│   │   └── APIService.swift                   ✅ ИЗМЕНЁН
│   ├── Models/
│   │   └── APIModels.swift                     ✅ ИЗМЕНЁН
│   ├── Localization/
│   │   └── LocalizationManager.swift           ⚠️ ТРЕБУЕТ ИЗМЕНЕНИЯ
│   └── Navigation/
│       └── NavigationManager.swift             ✅ ИЗМЕНЁН
│
├── Shared/
│   └── Models/
│       ├── ThreatProtectionCategory.swift       ⚠️ СОЗДАТЬ/ИЗМЕНИТЬ
│       ├── ProtectionGroup.swift               ⚠️ СОЗДАТЬ
│       └── ProtectionSettings.swift            ⚠️ СОЗДАТЬ
│
├── Core/
│   └── Managers/
│       ├── ProtectionSettingsManager.swift      ⚠️ СОЗДАТЬ
│       └── TariffManager.swift                  ⚠️ СОЗДАТЬ
│
├── Components/
│   ├── EnhancedThreatCategoryCard.swift         ⚠️ СОЗДАТЬ
│   ├── MotivationBanner.swift                  ⚠️ СОЗДАТЬ
│   ├── ThreatScenariosGallery.swift           ⚠️ СОЗДАТЬ
│   ├── ThreatScenarioCard.swift               ⚠️ СОЗДАТЬ
│   ├── ProtectionCategoryRow.swift            ⚠️ СОЗДАТЬ
│   ├── ProtectionGroupSection.swift           ⚠️ СОЗДАТЬ
│   └── ThreatProtectionCategoriesView.swift    ⚠️ ИЗМЕНИТЬ
│
└── Screens/
    ├── ThreatProtectionScreen.swift            ⚠️ ИЗМЕНИТЬ
    └── ThreatProtectionSettingsScreen.swift   ⚠️ СОЗДАТЬ
```

---

## 📋 СТАТИСТИКА

**Всего файлов:**
- ✅ Изменено (Этап 0): 4 файла
- ⚠️ Требует изменения: 1 файл (LocalizationManager)
- ⚠️ Создать: 11 файлов
- ⚠️ Изменить: 2 файла
- **Итого: 18 файлов**

**Строк кода (примерно):**
- Этап 0: ✅ ~200 строк (выполнено)
- Этап 1: ⚠️ ~400 строк
- Этап 2: ⚠️ ~600 строк
- Этап 3: ⚠️ ~400 строк
- **Итого: ~1600 строк (осталось)**

---

## 📝 ПОРЯДОК РЕАЛИЗАЦИИ

### ✅ Этап 0: Подготовка (ВЫПОЛНЕНО)

1. ✅ `AppConfig.swift` — добавлены API endpoints
2. ✅ `APIService.swift` — добавлены методы API
3. ✅ `APIModels.swift` — добавлены модели API
4. ⚠️ `LocalizationManager.swift` — нужно добавить локализацию
5. ✅ `NavigationManager.swift` — добавлена навигация

---

### ⚠️ Этап 1: Базовая инфраструктура (СЛЕДУЮЩИЙ)

1. ⚠️ `ThreatProtectionCategory.swift` — расширить enum
2. ⚠️ `ProtectionGroup.swift` — создать enum
3. ⚠️ `ProtectionSettings.swift` — создать структуру
4. ⚠️ `ProtectionSettingsManager.swift` — создать менеджер
5. ⚠️ `TariffManager.swift` — создать менеджер

---

### ⚠️ Этап 2: UI компоненты

1. ⚠️ `EnhancedThreatCategoryCard.swift` — создать компонент
2. ⚠️ `MotivationBanner.swift` — создать компонент
3. ⚠️ `ThreatScenariosGallery.swift` — создать компонент
4. ⚠️ `ThreatScenarioCard.swift` — создать компонент
5. ⚠️ `ProtectionCategoryRow.swift` — создать компонент
6. ⚠️ `ProtectionGroupSection.swift` — создать компонент

---

### ⚠️ Этап 3: Экраны

1. ⚠️ `ThreatProtectionScreen.swift` — обновить экран
2. ⚠️ `ThreatProtectionSettingsScreen.swift` — создать экран
3. ⚠️ `ThreatProtectionCategoriesView.swift` — обновить компонент

---

## 🔗 ЗАВИСИМОСТИ МЕЖДУ ФАЙЛАМИ

### Модели данных
```
ThreatProtectionCategory.swift
    ↓ использует
ProtectionGroup.swift
    ↓ использует
ProtectionSettings.swift
```

### Менеджеры
```
ProtectionSettingsManager.swift
    ↓ использует
ProtectionSettings.swift
    ↓ использует
ThreatProtectionCategory.swift
    ↓ использует
TariffManager.swift
```

### UI компоненты
```
EnhancedThreatCategoryCard.swift
    ↓ использует
ThreatProtectionCategory.swift
    ↓ использует
ProtectionSettingsManager.swift
    ↓ использует
TariffManager.swift
    ↓ использует
MotivationBanner.swift
```

### Экраны
```
ThreatProtectionScreen.swift
    ↓ использует
ThreatScenariosGallery.swift
    ↓ использует
ThreatProtectionCategoriesView.swift
    ↓ использует
EnhancedThreatCategoryCard.swift
```

---

## ✅ ЧЕКЛИСТ

### Этап 0: Подготовка
- [x] Добавить API endpoints в `AppConfig.swift`
- [x] Добавить методы API в `APIService.swift`
- [x] Добавить модели API в `APIModels.swift`
- [ ] Добавить локализацию в `LocalizationManager.swift`
- [x] Добавить навигацию в `NavigationManager.swift`

### Этап 1: Базовая инфраструктура
- [ ] Создать/изменить `ThreatProtectionCategory.swift`
- [ ] Создать `ProtectionGroup.swift`
- [ ] Создать `ProtectionSettings.swift`
- [ ] Создать `ProtectionSettingsManager.swift`
- [ ] Создать `TariffManager.swift`

### Этап 2: UI компоненты
- [ ] Создать `EnhancedThreatCategoryCard.swift`
- [ ] Создать `MotivationBanner.swift`
- [ ] Создать `ThreatScenariosGallery.swift`
- [ ] Создать `ThreatScenarioCard.swift`
- [ ] Создать `ProtectionCategoryRow.swift`
- [ ] Создать `ProtectionGroupSection.swift`

### Этап 3: Экраны
- [ ] Изменить `ThreatProtectionScreen.swift`
- [ ] Создать `ThreatProtectionSettingsScreen.swift`
- [ ] Изменить `ThreatProtectionCategoriesView.swift`

---

## 📌 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Порядок создания:** Сначала модели, потом менеджеры, потом компоненты, потом экраны
2. **Зависимости:** Проверять зависимости перед созданием файлов
3. **Локализация:** Все строки должны быть локализованы через `LocalizationManager`
4. **Навигация:** Использовать `NavigationManager` для всех переходов
5. **Тестирование:** Тестировать каждый этап перед переходом к следующему

---

**Дата создания:** 2025-11-12  
**Последнее обновление:** 2025-11-12  
**Статус:** Готово к реализации Этапа 1

