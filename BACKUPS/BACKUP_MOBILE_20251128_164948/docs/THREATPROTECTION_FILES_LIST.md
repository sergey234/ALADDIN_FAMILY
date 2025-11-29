# 📁 СПИСОК ФАЙЛОВ: Система защиты от угроз

**Дата:** 2025-11-12  
**Статус:** Полный список всех файлов для реализации

---

## 📋 ФАЙЛЫ ДЛЯ ИЗМЕНЕНИЯ

### 1. Конфигурация и API

#### `Core/Config/AppConfig.swift`
**Действие:** Изменить  
**Что добавить:**
- API endpoints для защиты от угроз
- `protectionSettings`, `protectionStatus`, `threatScenarios`, и т.д.

---

#### `Core/Network/APIService.swift`
**Действие:** Изменить  
**Что добавить:**
- Методы API для защиты от угроз
- `getProtectionSettings()`, `updateProtectionSettings()`, `getThreatScenarios()`, и т.д.

---

#### `Core/Models/APIModels.swift`
**Действие:** Изменить  
**Что добавить:**
- `ProtectionSettingsResponse`
- `ProtectionStatusResponse`
- `ThreatScenarioResponse`

---

### 2. Локализация

#### `Core/Localization/LocalizationManager.swift`
**Действие:** Изменить  
**Что добавить:**
- Новые ключи локализации для защиты от угроз
- `protection_settings_title`, `protection_what_this_gives`, и т.д.

---

### 3. Навигация

#### `Core/Navigation/NavigationManager.swift`
**Действие:** Изменить  
**Что добавить:**
- Новые экраны в enum `ALADDINScreen`
- `threatProtection`, `threatProtectionSettings`, `iotSecurity`, `advancedProtection`

---

## 🆕 ФАЙЛЫ ДЛЯ СОЗДАНИЯ

### 4. Модели данных

#### `Shared/Models/ThreatProtectionCategory.swift` (если не существует)
**Действие:** Создать или изменить  
**Что добавить:**
- Расширения для `ThreatProtectionCategory`
- `requiredTariff`, `benefit`, `settingsScreen`, `group`
- `ProtectionGroup` enum

---

#### `Shared/Models/ProtectionSettings.swift`
**Действие:** Создать  
**Что добавить:**
- Структура `ProtectionSettings`
- Методы `isEnabled()`, `setEnabled()`
- Вычисляемые свойства для групп

---

### 5. Менеджеры

#### `Managers/ProtectionSettingsManager.swift`
**Действие:** Создать  
**Что добавить:**
- Класс `ProtectionSettingsManager` (Singleton)
- Методы `loadSettings()`, `saveSettings()`
- Методы `toggleCategory()`, `enableCategory()`, `disableCategory()`
- Метод `enableForTariff()`
- Метод `isCategoryAvailable()`

---

#### `Managers/TariffManager.swift`
**Действие:** Создать  
**Что добавить:**
- Класс `TariffManager` (Singleton)
- Методы `loadTariff()`, `saveTariff()`
- Расширение `TariffType` с `level` property
- Observer для изменений тарифов

---

### 6. UI компоненты

#### `Components/EnhancedThreatCategoryCard.swift`
**Действие:** Создать  
**Что добавить:**
- Компонент расширенной карточки категории
- Статус-индикатор (🟢🟡🔴)
- Блок "Что это даёт"
- Кнопка "Подробнее"
- Мотивационный баннер (если недоступно)

---

#### `Components/MotivationBanner.swift`
**Действие:** Создать  
**Что добавить:**
- Компонент мотивационного баннера
- Иконка замка
- Текст "Требует тариф X"
- Кнопка "Обновить тариф"

---

#### `Components/ThreatScenariosGallery.swift`
**Действие:** Создать  
**Что добавить:**
- Компонент галереи сценариев
- Горизонтальный ScrollView
- Карточки сценариев (`ThreatScenarioCard`)
- Модель `ThreatScenario`

---

#### `Components/ProtectionCategoryRow.swift`
**Действие:** Создать  
**Что добавить:**
- Компонент строки категории в настройках
- Иконка категории
- Название и описание
- Переключатель (если доступно)
- Баннер (если недоступно)

---

#### `Components/ProtectionGroupSection.swift`
**Действие:** Создать  
**Что добавить:**
- Компонент секции группы
- Заголовок группы
- Список категорий в группе

---

### 7. Экраны

#### `Screens/ThreatProtectionScreen.swift`
**Действие:** Изменить  
**Что добавить:**
- Галерея сценариев (сверху)
- Обновлённая структура с группами
- Интеграция с новыми компонентами

---

#### `Screens/ThreatProtectionSettingsScreen.swift`
**Действие:** Создать  
**Что добавить:**
- Единый экран настроек защиты
- Группы категорий (вертикально)
- Переключатели для всех категорий
- Навигация на детальные экраны

---

#### `Components/ThreatProtectionCategoriesView.swift`
**Действие:** Изменить  
**Что добавить:**
- Группировка категорий по группам
- Использование `ProtectionGroupSection`
- Интеграция с `EnhancedThreatCategoryCard`

---

## 📊 СТРУКТУРА ФАЙЛОВ

```
ALADDIN_iOS/
├── Core/
│   ├── Config/
│   │   └── AppConfig.swift                    [ИЗМЕНИТЬ]
│   ├── Network/
│   │   └── APIService.swift                   [ИЗМЕНИТЬ]
│   ├── Models/
│   │   └── APIModels.swift                     [ИЗМЕНИТЬ]
│   ├── Localization/
│   │   └── LocalizationManager.swift           [ИЗМЕНИТЬ]
│   └── Navigation/
│       └── NavigationManager.swift             [ИЗМЕНИТЬ]
│
├── Shared/
│   └── Models/
│       ├── ThreatProtectionCategory.swift       [СОЗДАТЬ/ИЗМЕНИТЬ]
│       └── ProtectionSettings.swift             [СОЗДАТЬ]
│
├── Managers/
│   ├── ProtectionSettingsManager.swift          [СОЗДАТЬ]
│   └── TariffManager.swift                     [СОЗДАТЬ]
│
├── Components/
│   ├── EnhancedThreatCategoryCard.swift         [СОЗДАТЬ]
│   ├── MotivationBanner.swift                  [СОЗДАТЬ]
│   ├── ThreatScenariosGallery.swift            [СОЗДАТЬ]
│   ├── ProtectionCategoryRow.swift            [СОЗДАТЬ]
│   ├── ProtectionGroupSection.swift            [СОЗДАТЬ]
│   └── ThreatProtectionCategoriesView.swift    [ИЗМЕНИТЬ]
│
└── Screens/
    ├── ThreatProtectionScreen.swift            [ИЗМЕНИТЬ]
    └── ThreatProtectionSettingsScreen.swift    [СОЗДАТЬ]
```

---

## 📝 ПОРЯДОК РЕАЛИЗАЦИИ

### Этап 0: Подготовка (КРИТИЧНО!)

1. ✅ `AppConfig.swift` — добавить API endpoints
2. ✅ `APIService.swift` — добавить методы API
3. ✅ `APIModels.swift` — добавить модели API
4. ✅ `LocalizationManager.swift` — добавить локализацию
5. ✅ `NavigationManager.swift` — добавить навигацию

---

### Этап 1: Базовая инфраструктура

1. ✅ `ThreatProtectionCategory.swift` — расширить enum
2. ✅ `ProtectionSettings.swift` — создать структуру
3. ✅ `ProtectionSettingsManager.swift` — создать менеджер
4. ✅ `TariffManager.swift` — создать менеджер

---

### Этап 2: UI компоненты

1. ✅ `EnhancedThreatCategoryCard.swift` — создать компонент
2. ✅ `MotivationBanner.swift` — создать компонент
3. ✅ `ThreatScenariosGallery.swift` — создать компонент
4. ✅ `ProtectionCategoryRow.swift` — создать компонент
5. ✅ `ProtectionGroupSection.swift` — создать компонент

---

### Этап 3: Экраны

1. ✅ `ThreatProtectionScreen.swift` — обновить экран
2. ✅ `ThreatProtectionSettingsScreen.swift` — создать экран
3. ✅ `ThreatProtectionCategoriesView.swift` — обновить компонент

---

### Этап 4: Интеграция

1. ✅ Интеграция с тарифами
2. ✅ API синхронизация
3. ✅ Тестирование

---

## 📊 СТАТИСТИКА

**Всего файлов:**
- Изменить: 7 файлов
- Создать: 11 файлов
- **Итого: 18 файлов**

**Строк кода (примерно):**
- Этап 0: ~200 строк
- Этап 1: ~400 строк
- Этап 2: ~600 строк
- Этап 3: ~400 строк
- Этап 4: ~200 строк
- **Итого: ~1800 строк**

---

**Дата создания:** 2025-11-12  
**Статус:** Готово к реализации

