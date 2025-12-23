# 📋 ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ CONTENT BLOCKER EXTENSION

**Дата:** 23 декабря 2025  
**Статус:** 🚧 В РАЗРАБОТКЕ

---

## 🎯 ЦЕЛЬ

Реализовать Content Blocker Extension для блокировки нежелательного контента в Safari согласно правилам родительского контроля.

---

## 📊 АРХИТЕКТУРА

```
┌─────────────────────────────────────────────────────────┐
│  Основное приложение (ALADDIN)                         │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ParentalControlScreen                          │  │
│  │  - Кнопка "Блокировка контента"                 │  │
│  │  - Переключатель включения/выключения           │  │
│  │  - Статистика заблокированных сайтов            │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ContentBlockerManager                          │  │
│  │  - Создание правил блокировки                   │  │
│  │  - Активация/деактивация через                  │  │
│  │    SFContentBlockerManager                      │  │
│  │  - Сохранение правил в App Group                │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  App Group: "group.com.aladdin.family"          │  │
│  │  - Обмен данными между приложением и extension  │  │
│  │  - Хранение JSON правил блокировки              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Content Blocker Extension                              │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ActionRequestHandler.swift                     │  │
│  │  - Загрузка правил из App Group                 │  │
│  │  - Возврат правил Safari                        │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Safari Browser                                 │  │
│  │  - Блокировка контента согласно правилам         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 СТРУКТУРА ФАЙЛОВ

### 1. Основное приложение

```
Core/
├── ContentBlocker/
│   ├── ContentBlockerManager.swift          ✅ СОЗДАТЬ
│   ├── ContentBlockerRule.swift             ✅ СОЗДАТЬ
│   └── ContentBlockerCategory.swift          ✅ СОЗДАТЬ

Components/
└── Modals/
    └── FamilyContentBlockModal.swift         ✅ СОЗДАТЬ (если нет)
```

### 2. Extension Target

```
ALADDINContentBlocker/
├── ActionRequestHandler.swift                ✅ СОЗДАТЬ
├── Info.plist                                ✅ СОЗДАТЬ
└── blockerList.json                          ✅ СОЗДАТЬ (опционально)
```

---

## 🔧 ШАГ 1: СОЗДАНИЕ CONTENTBLOCKERMANAGER

**Файл:** `Core/ContentBlocker/ContentBlockerManager.swift`

**Функционал:**
- Управление правилами блокировки
- Активация/деактивация через SFContentBlockerManager
- Сохранение правил в App Group
- Синхронизация с backend (опционально)

**Методы:**
- `enableContentBlocker(rules: [ContentBlockerRule])` - Включить блокировку
- `disableContentBlocker()` - Выключить блокировку
- `updateRules(rules: [ContentBlockerRule])` - Обновить правила
- `getBlockingStatus()` - Получить статус блокировки
- `createRulesFromSettings()` - Создать правила из настроек родителя

---

## 🔧 ШАГ 2: СОЗДАНИЕ МОДЕЛЕЙ

**Файл:** `Core/ContentBlocker/ContentBlockerRule.swift`

**Структура:**
```swift
struct ContentBlockerRule: Codable {
    let trigger: Trigger
    let action: Action
}

struct Trigger: Codable {
    let urlFilter: String
    let ifDomain: [String]?
    let unlessDomain: [String]?
}

struct Action: Codable {
    let type: String // "block" или "block-cookies"
}
```

**Файл:** `Core/ContentBlocker/ContentBlockerCategory.swift`

**Категории блокировки:**
- Взрослый контент
- Насилие
- Азартные игры
- Социальные сети
- Видео (YouTube и т.д.)
- Игры
- И другие...

---

## 🔧 ШАГ 3: СОЗДАНИЕ EXTENSION TARGET

**В Xcode:**
1. File → New → Target
2. Выбрать "Content Blocker Extension"
3. Название: `ALADDINContentBlocker`
4. Bundle ID: `family.aladdin.ios.ContentBlocker`

**Файл:** `ALADDINContentBlocker/ActionRequestHandler.swift`

**Функционал:**
- Загрузка правил из App Group
- Возврат правил Safari в формате JSON

---

## 🔧 ШАГ 4: НАСТРОЙКА APP GROUPS

**В Xcode:**
1. Основное приложение → Signing & Capabilities → + App Groups
2. Extension → Signing & Capabilities → + App Groups
3. Оба используют: `group.com.aladdin.family`

**В Info.plist:**
- Добавить `NSExtension` → `NSExtensionPointIdentifier` = `com.apple.Safari.content-blocker`

---

## 🔧 ШАГ 5: ИНТЕГРАЦИЯ С UI

**Файл:** `Screens/07_ParentalControlScreen.swift`

**Изменения:**
1. Добавить состояние для Content Blocker:
   ```swift
   @State private var isContentBlockerEnabled: Bool = false
   @State private var contentBlockerStatus: ContentBlockerStatus = .disabled
   ```

2. Обновить карточку "Блокировка контента":
   - Показать статус блокировки (включена/выключена)
   - Показать количество заблокированных сайтов
   - Кнопка для открытия настроек

3. Добавить модальное окно `FamilyContentBlockModal`:
   - Список категорий для блокировки
   - Переключатели для каждой категории
   - Кнопка "Применить"
   - Кнопка "Включить блокировку в Safari"

---

## 🔧 ШАГ 6: СОЗДАНИЕ МОДАЛЬНОГО ОКНА

**Файл:** `Components/Modals/FamilyContentBlockModal.swift`

**UI элементы:**
- Заголовок: "Блокировка контента в Safari"
- Описание: "Выберите категории контента для блокировки"
- Список категорий с переключателями:
  - ✅ Взрослый контент
  - ✅ Насилие
  - ✅ Азартные игры
  - ✅ Социальные сети
  - ✅ Видео (YouTube)
  - ✅ Игры
  - ✅ И другие...
- Кнопка "Включить блокировку в Safari" (открывает настройки iOS)
- Кнопка "Применить правила"
- Кнопка "Закрыть"

---

## 🔧 ШАГ 7: ИНТЕГРАЦИЯ С PARENTALCONTROLMANAGER

**Файл:** `Core/Managers/ParentalControlManager.swift`

**Добавить методы:**
- `enableContentBlockerForSafari(categories: [ContentBlockerCategory])`
- `disableContentBlockerForSafari()`
- `getContentBlockerStatus()`

---

## 📱 UI ЭЛЕМЕНТЫ НА ЭКРАНЕ

### Карточка "Блокировка контента" (ParentalControlScreen)

```
┌─────────────────────────────────────────┐
│  🔒 Блокировка контента                  │
│                                          │
│  Статус: ✅ Включена в Safari            │
│  Заблокировано: 12 сайтов                │
│  Категорий: 5 активных                   │
│                                          │
│  [⚙️ Настроить]  [🔄 Обновить правила]  │
└─────────────────────────────────────────┘
```

### Модальное окно настроек

```
┌─────────────────────────────────────────┐
│  🔒 Блокировка контента в Safari         │
│                                          │
│  Выберите категории для блокировки:     │
│                                          │
│  ☑️ Взрослый контент                     │
│  ☑️ Насилие                              │
│  ☐ Азартные игры                         │
│  ☑️ Социальные сети                      │
│  ☑️ Видео (YouTube)                      │
│  ☐ Игры                                  │
│                                          │
│  ⚠️ Для работы блокировки необходимо:   │
│  1. Включить в Настройках iOS            │
│  2. Выбрать ALADDIN в Safari             │
│                                          │
│  [📱 Открыть настройки iOS]              │
│  [✅ Применить правила]                  │
│  [❌ Закрыть]                            │
└─────────────────────────────────────────┘
```

---

## 🔄 ПОТОК РАБОТЫ

### 1. Родитель настраивает правила:
```
Родитель → ParentalControlScreen → Нажимает "Блокировка контента"
→ Открывается FamilyContentBlockModal
→ Выбирает категории для блокировки
→ Нажимает "Применить правила"
→ ContentBlockerManager создает JSON правила
→ Правила сохраняются в App Group
→ SFContentBlockerManager активирует блокировку
```

### 2. Safari блокирует контент:
```
Ребенок открывает Safari → Заходит на заблокированный сайт
→ Safari запрашивает правила у Extension
→ ActionRequestHandler загружает правила из App Group
→ Safari блокирует сайт согласно правилам
→ Ребенок видит страницу "Сайт заблокирован"
```

### 3. Обновление правил:
```
Родитель изменяет настройки → ContentBlockerManager обновляет правила
→ Правила сохраняются в App Group
→ SFContentBlockerManager обновляет блокировку
→ Safari получает новые правила
```

---

## ✅ ЧЕКЛИСТ РЕАЛИЗАЦИИ

- [ ] 1. Создать ContentBlockerManager.swift
- [ ] 2. Создать ContentBlockerRule.swift
- [ ] 3. Создать ContentBlockerCategory.swift
- [ ] 4. Создать Extension Target в Xcode (вручную)
- [ ] 5. Создать ActionRequestHandler.swift
- [ ] 6. Настроить App Groups в Xcode (вручную)
- [ ] 7. Создать FamilyContentBlockModal.swift
- [ ] 8. Интегрировать с ParentalControlScreen
- [ ] 9. Добавить методы в ParentalControlManager
- [ ] 10. Добавить локализацию
- [ ] 11. Тестирование

---

## 📝 ПРИМЕЧАНИЯ

1. **Extension Target создается вручную в Xcode** - я создам файлы, но target нужно добавить через Xcode UI
2. **App Groups настраиваются вручную** - нужно добавить capability в Xcode
3. **Правила блокировки** - JSON формат согласно документации Apple
4. **Активация блокировки** - пользователь должен включить в Настройках iOS → Safari → Content Blockers

---

**Готов к реализации!** 🚀

