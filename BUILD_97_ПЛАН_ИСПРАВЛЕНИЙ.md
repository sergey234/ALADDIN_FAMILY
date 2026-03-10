# 🔧 BUILD 97: ДЕТАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЙ КРАША В ОНБОРДИНГЕ

**Дата:** 2026-03-10  
**Версия сборки:** 97 → 98  
**Цель:** Исправить краш при входе в онбординг

---

## 📋 ПЛАН ИСПРАВЛЕНИЙ (3 критичных исправления)

### 🔴 ИСПРАВЛЕНИЕ #1: Вернуть установку `false` в `initializeNavigation()` (асинхронно)

**Файл:** `ALADDINApp.swift:689-691`  
**Проблема:** Убрали `UserDefaults.set(false)` - это вызвало рассинхронизацию между `UserDefaults` и `@AppStorage`

**Решение:**
- Вернуть установку `false` для первого запуска
- Сделать это асинхронно через `Task { @MainActor in }` для предотвращения рекурсии
- Устанавливать только если это первый запуск

**Код:**
```swift
if !ALADDINApp.hasInitializedNavigation {
    print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
    // ✅ BUILD 98: Устанавливаем false асинхронно для предотвращения рекурсии
    Task { @MainActor in
        UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
    }
}
```

**Риск:** 🟢 Низкий (асинхронная установка безопасна)

---

### 🔴 ИСПРАВЛЕНИЕ #2: Исправить `MasterLogger.enableVisualLogging` (не читать из UserDefaults при инициализации)

**Файл:** `Core/Utilities/MasterLogger.swift:32-44`  
**Проблема:** При первом обращении к `enableVisualLogging` происходит чтение из `UserDefaults`, что может вызвать рекурсию при инициализации View

**Решение:**
- Использовать значение по умолчанию `false` без чтения из `UserDefaults` при первом обращении
- Читать из `UserDefaults` только при явном запросе или после инициализации
- Использовать ленивую инициализацию

**Код:**
```swift
private var enableVisualLogging: Bool {
    get {
        // Проверяем кеш в thread dictionary
        let dict = Thread.current.threadDictionary
        if let cached = dict["MasterLogger.enableVisualLogging"] as? Bool {
            return cached
        }
        
        // ✅ BUILD 98: Используем значение по умолчанию false без чтения из UserDefaults при инициализации
        // Читаем из UserDefaults только если это не первый запуск (когда уже есть кеш)
        // Это предотвращает рекурсию при инициализации View
        let defaultValue = false
        dict["MasterLogger.enableVisualLogging"] = defaultValue
        _enableVisualLogging = defaultValue
        
        // Загружаем реальное значение асинхронно после инициализации
        Task { @MainActor in
            let realValue = UserDefaults.standard.bool(forKey: "enable_visual_logging")
            dict["MasterLogger.enableVisualLogging"] = realValue
            _enableVisualLogging = realValue
        }
        
        return defaultValue
    }
    set {
        _enableVisualLogging = newValue
        Thread.current.threadDictionary["MasterLogger.enableVisualLogging"] = newValue
        
        // ✅ BUILD 98: Асинхронная установка для предотвращения рекурсии
        Task { @MainActor in
            UserDefaults.standard.set(newValue, forKey: "enable_visual_logging")
        }
    }
}
```

**Риск:** 🟢 Низкий (используем значение по умолчанию)

---

### 🔴 ИСПРАВЛЕНИЕ #3: Разрешить конфликт `@AppStorage` между `OnboardingScreen` и `ALADDINApp`

**Файлы:** 
- `Screens/14_OnboardingScreen.swift:62`
- `ALADDINApp.swift:133`

**Проблема:** Оба используют один и тот же ключ `hasCompletedOnboarding`, что может вызвать рекурсию

**Решение:**
- Оставить `@AppStorage` только в `ALADDINApp` (источник истины)
- В `OnboardingScreen` использовать `@State` и синхронизировать с `@AppStorage` через `onAppear` и `onChange`
- Или использовать `@Binding` из `ALADDINApp`

**Вариант 1 (Рекомендуемый):** Использовать `@State` в `OnboardingScreen` и синхронизировать
```swift
// В OnboardingScreen:
@State private var hasCompletedOnboarding: Bool = false
@EnvironmentObject private var navigationManager: NavigationManager

.onAppear {
    // Синхронизируем с UserDefaults
    hasCompletedOnboarding = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
}

// При завершении онбординга:
hasCompletedOnboarding = true
UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
```

**Вариант 2:** Использовать `@Binding` из родительского View
- Более сложный, требует изменения архитектуры

**Риск:** 🟡 Средний (нужно проверить синхронизацию)

---

## 📊 ПРИОРИТЕТЫ ИСПРАВЛЕНИЙ

| Исправление | Приоритет | Риск | Время |
|-------------|-----------|------|-------|
| #1: Вернуть установку false | 🔴 Критично | 🟢 Низкий | 5 мин |
| #2: Исправить MasterLogger | 🔴 Критично | 🟢 Низкий | 10 мин |
| #3: Разрешить конфликт @AppStorage | 🔴 Критично | 🟡 Средний | 15 мин |

**Общее время:** ~30 минут

---

## ✅ КРИТЕРИИ УСПЕХА

- [ ] Приложение запускается без краша
- [ ] Онбординг отображается корректно
- [ ] После онбординга переход на главную страницу работает
- [ ] Нет рекурсии в логах
- [ ] Все функции работают корректно

---

**ГОТОВО К ВЫПОЛНЕНИЮ!** 🚀
