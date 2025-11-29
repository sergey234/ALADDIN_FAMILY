# 📱 ПОЛНОЕ РУКОВОДСТВО: Как правильно добавлять новые экраны/страницы

**Дата:** 2025-11-12  
**Для:** Передача работы другой ML модели

---

## 📋 ОГЛАВЛЕНИЕ

1. [Архитектура навигации](#архитектура-навигации)
2. [Как добавить новый экран](#как-добавить-новый-экран)
3. [Структура файлов](#структура-файлов)
4. [Интеграция с NavigationManager](#интеграция-с-navigationmanager)
5. [Интеграция с ALADDINApp](#интеграция-с-aladdinapp)
6. [Добавление в project.pbxproj](#добавление-в-projectpbxproj)
7. [Локализация](#локализация)
8. [Навигация (кнопка Назад)](#навигация-кнопка-назад)
9. [Примеры](#примеры)
10. [Чеклист](#чеклист)

---

## 🏗️ АРХИТЕКТУРА НАВИГАЦИИ

### Основные компоненты:

1. **NavigationManager** (`Core/Navigation/NavigationManager.swift`)
   - Управляет стеком навигации
   - Определяет все возможные экраны через `enum ALADDINScreen`
   - Методы: `navigateTo()`, `goBack()`, `canGoBack`

2. **ALADDINApp** (`ALADDINApp.swift`)
   - Главный файл приложения
   - Содержит `switch` для отображения экранов
   - Инжектит `@EnvironmentObject` для всех экранов

3. **ALADDINNavigationBar** (`Shared/Components/Navigation/ALADDINNavigationBar.swift`)
   - Стандартная навигационная панель
   - Кнопка "Назад", профиль, список экранов

---

## ➕ КАК ДОБАВИТЬ НОВЫЙ ЭКРАН

### Шаг 1: Создать файл экрана

**Расположение:** `Screens/XX_NewScreen.swift` (где XX — номер экрана)

**Шаблон:**
```swift
import SwiftUI

struct NewScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss // Для NavigationLink
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: localizationManager.localized("new_screen_title"),
                    subtitle: localizationManager.localized("new_screen_subtitle"),
                    showBackButton: true,
                    onBack: {
                        // ✅ ГИБРИДНЫЙ ПОДХОД для кнопки Назад
                        dismiss()
                        DispatchQueue.main.async {
                            if navigationManager.canGoBack {
                                navigationManager.goBack()
                            } else {
                                navigationManager.navigateTo(.main)
                            }
                        }
                    }
                )
                
                // Контент экрана
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Ваш контент здесь
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                }
            }
        }
        .navigationBarHidden(true)
        .id("new_screen_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

#if DEBUG
struct NewScreen_Previews: PreviewProvider {
    static var previews: some View {
        NewScreen()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
#endif
```

---

### Шаг 2: Добавить в NavigationManager

**Файл:** `Core/Navigation/NavigationManager.swift`

#### 2.1. Добавить case в enum ALADDINScreen:

```swift
enum ALADDINScreen: String, CaseIterable {
    // ... существующие экраны ...
    case newScreen = "NewScreen" // ✅ ДОБАВИТЬ
}
```

#### 2.2. Добавить displayName:

```swift
var displayName: String {
    switch self {
    // ... существующие ...
    case .newScreen: return "Новый экран" // ✅ ДОБАВИТЬ
    }
}
```

#### 2.3. Добавить icon:

```swift
var icon: String {
    switch self {
    // ... существующие ...
    case .newScreen: return "star.fill" // ✅ ДОБАВИТЬ
    }
}
```

---

### Шаг 3: Добавить в ALADDINApp

**Файл:** `ALADDINApp.swift`

**Найти `switch navigationManager.currentScreen` и добавить:**

```swift
switch navigationManager.currentScreen {
    // ... существующие case ...
    case .newScreen:
        AnyView(NewScreen()
            .id("newScreen")
            .environmentObject(navigationManager)
            .environmentObject(localizationManager))
}
```

**ВАЖНО:** Всегда используйте `AnyView()` и инжектируйте `@EnvironmentObject`!

---

### Шаг 4: Добавить локализацию

**Файл:** `Core/Localization/LocalizationManager.swift`

**В русской локализации:**
```swift
"new_screen_title": "Новый экран",
"new_screen_subtitle": "Описание нового экрана",
```

**В английской локализации:**
```swift
"new_screen_title": "New Screen",
"new_screen_subtitle": "New screen description",
```

---

### Шаг 5: Добавить файл в project.pbxproj

**Файл:** `ALADDIN.xcodeproj/project.pbxproj`

**Нужно добавить в 4 места:**

1. **PBXBuildFile section:**
```swift
5EXXXXXX2EXXXXXX000XXXXX /* NewScreen.swift in Sources */ = {isa = PBXBuildFile; fileRef = 5EXXXXXX2EXXXXXX000XXXXX /* NewScreen.swift */; };
```

2. **PBXFileReference section:**
```swift
5EXXXXXX2EXXXXXX000XXXXX /* NewScreen.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = NewScreen.swift; sourceTree = "<group>"; };
```

3. **PBXGroup section (в группе Screens):**
```swift
5EXXXXXX2EXXXXXX000XXXXX /* NewScreen.swift */,
```

4. **PBXSourcesBuildPhase section:**
```swift
5EXXXXXX2EXXXXXX000XXXXX /* NewScreen.swift in Sources */,
```

**ВАЖНО:** Используйте уникальные UUID для каждого файла!

---

## 🔄 НАВИГАЦИЯ (КНОПКА НАЗАД)

### Проблема:
Кнопка "Назад" не работает или отсутствует.

### Решение (Гибридный подход):

```swift
ALADDINNavigationBar(
    showBackButton: true,
    onBack: {
        // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() + NavigationManager
        dismiss() // Для NavigationLink
        
        DispatchQueue.main.async {
            if navigationManager.canGoBack {
                navigationManager.goBack()
            } else {
                navigationManager.navigateTo(.main)
            }
        }
    }
)
```

### Когда использовать:

- **NavigationLink** → используйте `dismiss()` + синхронизацию
- **Programmatic navigation** → используйте `navigationManager.goBack()`

---

## 📁 СТРУКТУРА ФАЙЛОВ

### Расположение экранов:

```
Screens/
├── 01_MainScreen.swift
├── 02_FamilyScreen.swift
├── 03_VPNScreen.swift
├── ...
└── XX_NewScreen.swift
```

### Расположение компонентов:

```
Components/
├── Modals/
│   ├── AgeGroupSelectionModal.swift
│   └── ...
└── Navigation/
    └── ALADDINNavigationBar.swift
```

### Расположение моделей:

```
Shared/Models/
├── ProtectionGroup.swift
├── ProtectionSettings.swift
└── ...
```

---

## 🎨 СТАНДАРТЫ ДИЗАЙНА

### Фон:
```swift
LinearGradient.backgroundGradient
    .ignoresSafeArea()
```

### Отступы:
```swift
.padding(.horizontal, Spacing.screenPadding) // 20
.padding(.vertical, Spacing.m) // 16
```

### Цвета:
```swift
.textPrimary      // Основной текст
.textSecondary    // Вторичный текст
.textTertiary     // Третичный текст
.secondaryGold    // Золотой акцент
.primaryBlue      // Синий акцент
.successGreen     // Зелёный (успех)
.warningOrange    // Оранжевый (предупреждение)
.dangerRed        // Красный (опасность)
```

### Шрифты:
```swift
.h1, .h2, .h3     // Заголовки
.body, .bodyBold  // Основной текст
.caption, .captionBold // Подписи
```

---

## 📝 ПРИМЕРЫ

### Пример 1: Простой экран

```swift
import SwiftUI

struct SimpleScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: "Простой экран",
                    subtitle: "Описание",
                    showBackButton: true,
                    onBack: {
                        dismiss()
                        DispatchQueue.main.async {
                            if navigationManager.canGoBack {
                                navigationManager.goBack()
                            } else {
                                navigationManager.navigateTo(.main)
                            }
                        }
                    }
                )
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        Text("Контент экрана")
                            .foregroundColor(.textPrimary)
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                }
            }
        }
        .navigationBarHidden(true)
    }
}
```

### Пример 2: Экран с ViewModel

```swift
import SwiftUI

struct ScreenWithViewModel: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = ScreenViewModel()
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        // ... как в примере 1, но используйте viewModel
    }
}
```

---

## ✅ ЧЕКЛИСТ

При добавлении нового экрана проверьте:

- [ ] Файл создан в `Screens/XX_NewScreen.swift`
- [ ] Добавлен case в `NavigationManager.ALADDINScreen`
- [ ] Добавлен displayName в NavigationManager
- [ ] Добавлен icon в NavigationManager
- [ ] Добавлен case в `ALADDINApp.swift` switch
- [ ] Инжектированы `@EnvironmentObject` (navigationManager, localizationManager)
- [ ] Добавлена локализация (RU + EN)
- [ ] Файл добавлен в `project.pbxproj` (4 места)
- [ ] Кнопка "Назад" работает (гибридный подход)
- [ ] Используется `ALADDINNavigationBar`
- [ ] Фон: `LinearGradient.backgroundGradient`
- [ ] `.navigationBarHidden(true)` добавлен
- [ ] Preview добавлен (для DEBUG)

---

## 📚 СВЯЗАННЫЕ ДОКУМЕНТЫ

1. **SCREEN_ADDITION_WORKFLOW_ALGORITHM.md** — алгоритм добавления экранов
2. **SCREEN_NAVIGATION_WORKFLOW_ALGORITHM.md** — алгоритм навигации
3. **THREATPROTECTION_COMPLETE_ARCHITECTURE.md** — архитектура системы защиты
4. **EXISTING_SCREENS_ANALYSIS.md** — анализ существующих экранов
5. **NAVIGATION_COMPLETE_FIX.md** — исправления навигации

---

## 🔗 КЛЮЧЕВЫЕ ФАЙЛЫ

- `Core/Navigation/NavigationManager.swift` — менеджер навигации
- `ALADDINApp.swift` — главный файл приложения
- `Shared/Components/Navigation/ALADDINNavigationBar.swift` — навигационная панель
- `Core/Localization/LocalizationManager.swift` — локализация
- `ALADDIN.xcodeproj/project.pbxproj` — конфигурация проекта

---

**Обновлено:** 2025-11-12

