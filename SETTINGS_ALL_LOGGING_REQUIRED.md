# 🔍 ПОЛНЫЙ СПИСОК ЛОГИРОВАНИЯ ДЛЯ SETTINGS SCREEN
## Все места где нужно добавить логирование

**Дата:** 2026-02-16  
**Версия сборки:** 38

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### **SETTINGS SCREEN (05_SettingsScreen.swift):**
- **Секций без логов:** 6
- **Функций без логов:** 4
- **Computed properties без логов:** 2
- **Всего критичных мест:** 10

### **ADVANCED PROTECTION SETTINGS SCREEN:**
- **Функций без логов:** 8
- **Computed properties без логов:** 5
- **Всего критичных мест:** 13

### **ОБЩИЙ ИТОГ:**
- **Всего мест без логов:** 23
- **Критичных мест:** 10
- **Важных мест:** 8
- **Желательных мест:** 5

---

## 🔴 КРИТИЧНО (SETTINGS SCREEN)

### 1. **`systemComponentsSection()` - НЕТ ЛОГОВ**
**Строка:** ~858  
**Что нужно:**
```swift
@ViewBuilder
private func systemComponentsSection() -> some View {
    let _ = {
        if Self.ENABLE_CRASH_LOGS {
            print("🔍 SETTINGS: systemComponentsSection() НАЧАЛО")
            print("🔍 SETTINGS: Thread.isMainThread = \(Thread.isMainThread)")
            print("🔍 SETTINGS: isAdmin = \(isAdmin)")
        }
    }()
    
    VStack(spacing: Spacing.m) {
        // ... код секции ...
    }
    .onAppear {
        if Self.ENABLE_CRASH_LOGS {
            print("✅ SETTINGS: systemComponentsSection() ЗАВЕРШЕН")
        }
    }
}
```

---

### 2. **`loadComponents()` - НЕТ ЛОГОВ**
**Строка:** ~923  
**Что нужно:**
```swift
private func loadComponents() {
    if Self.ENABLE_CRASH_LOGS {
        print("🔍 SETTINGS: loadComponents() НАЧАЛО")
        print("🔍 SETTINGS: Thread.isMainThread = \(Thread.isMainThread)")
        print("🔍 SETTINGS: isAdmin = \(isAdmin)")
    }
    
    guard isAdmin else {
        if Self.ENABLE_CRASH_LOGS {
            print("⚠️ SETTINGS: loadComponents() пропущен - не админ")
        }
        return
    }
    
    Task { @MainActor in
        isLoadingComponents = true
        componentsError = nil
        
        if Self.ENABLE_CRASH_LOGS {
            print("🔍 SETTINGS: loadComponents() API вызов начат")
        }
    }
    
    apiService.getComponentsList { result in
        Task { @MainActor in
            isLoadingComponents = false
            
            if Self.ENABLE_CRASH_LOGS {
                print("🔍 SETTINGS: loadComponents() API вызов завершен")
            }
            
            switch result {
            case .success(let loadedComponents):
                if Self.ENABLE_CRASH_LOGS {
                    print("✅ SETTINGS: loadComponents() успех: \(loadedComponents.count) компонентов")
                }
                components = loadedComponents
            case .failure(let error):
                if Self.ENABLE_CRASH_LOGS {
                    print("❌ SETTINGS: loadComponents() ошибка: \(error.localizedDescription)")
                }
                componentsError = error.localizedDescription
                print("❌ Ошибка загрузки компонентов: \(error.localizedDescription)")
            }
            
            if Self.ENABLE_CRASH_LOGS {
                print("✅ SETTINGS: loadComponents() ЗАВЕРШЕН")
            }
        }
    }
}
```

---

### 3. **`toggleComponent()` - НЕТ ЛОГОВ**
**Строка:** ~947  
**Что нужно:**
```swift
private func toggleComponent(_ component: ComponentStatus) {
    if Self.ENABLE_CRASH_LOGS {
        print("🔍 SETTINGS: toggleComponent() НАЧАЛО")
        print("🔍 SETTINGS: componentId = \(component.componentId)")
        print("🔍 SETTINGS: isEnabled = \(component.isEnabled)")
        print("🔍 SETTINGS: Thread.isMainThread = \(Thread.isMainThread)")
    }
    
    guard isAdmin else {
        if Self.ENABLE_CRASH_LOGS {
            print("⚠️ SETTINGS: toggleComponent() пропущен - не админ")
        }
        return
    }
    
    Task { @MainActor in
        do {
            if component.isEnabled {
                if Self.ENABLE_CRASH_LOGS {
                    print("🔍 SETTINGS: toggleComponent() отключение компонента")
                }
                _ = try await apiService.disableComponent(componentId: component.componentId)
            } else {
                if Self.ENABLE_CRASH_LOGS {
                    print("🔍 SETTINGS: toggleComponent() включение компонента")
                }
                _ = try await apiService.enableComponent(componentId: component.componentId)
            }
            
            if Self.ENABLE_CRASH_LOGS {
                print("✅ SETTINGS: toggleComponent() успех")
            }
            
            // Обновляем список компонентов
            loadComponents()
        } catch {
            if Self.ENABLE_CRASH_LOGS {
                print("❌ SETTINGS: toggleComponent() ошибка: \(error)")
            }
            componentsError = error.localizedDescription
        }
        
        if Self.ENABLE_CRASH_LOGS {
            print("✅ SETTINGS: toggleComponent() ЗАВЕРШЕН")
        }
    }
}
```

---

### 4. **`notificationsSection()` - НЕТ ЛОГОВ**
**Строка:** ~738  
**Что нужно:**
```swift
@ViewBuilder
private func notificationsSection() -> some View {
    let _ = {
        if Self.ENABLE_CRASH_LOGS {
            print("🔍 SETTINGS: notificationsSection() НАЧАЛО")
            print("🔍 SETTINGS: Thread.isMainThread = \(Thread.isMainThread)")
            print("🔍 SETTINGS: isSecurityNotificationsEnabled = \(isSecurityNotificationsEnabled)")
            print("🔍 SETTINGS: isSoundNotificationsEnabled = \(isSoundNotificationsEnabled)")
        }
    }()
    
    VStack(spacing: Spacing.m) {
        // ... код секции ...
    }
    .onAppear {
        if Self.ENABLE_CRASH_LOGS {
            print("✅ SETTINGS: notificationsSection() ЗАВЕРШЕН")
        }
    }
}
```

---

## 🟡 ВАЖНО (SETTINGS SCREEN)

### 5. **`securitySection()` - НЕТ ЛОГОВ**
**Строка:** ~558

### 6. **`appSection()` - НЕТ ЛОГОВ**
**Строка:** ~785

### 7. **`calculatedProtectionLevel` - НЕТ ЛОГОВ**
**Строка:** ~1300

### 8. **`handleBiometricToggle()` - УЛУЧШИТЬ ЛОГИ**
**Строка:** ~1150  
**Что нужно:**
- Обернуть существующие логи в `if Self.ENABLE_CRASH_LOGS`
- Добавить логи в начале функции
- Добавить логи при проверке `Thread.isMainThread`

---

## 🟢 ЖЕЛАТЕЛЬНО (SETTINGS SCREEN)

### 9. **`profileSection()` - НЕТ ЛОГОВ**
**Строка:** ~463

### 10. **`additionalSection()` - НЕТ ЛОГОВ**
**Строка:** ~1019

### 11. **`cycleTheme()` - УЛУЧШИТЬ ЛОГИ**
**Строка:** ~1361

### 12. **`checkForUpdates()` - НЕТ ЛОГОВ**
**Строка:** ~1391

### 13. **`protectionLevelText` - НЕТ ЛОГОВ**
**Строка:** ~1327

---

## 🔴 КРИТИЧНО (ADVANCED PROTECTION SETTINGS SCREEN)

### 14. **Добавить `ENABLE_CRASH_LOGS` флаг**
**Файл:** `Screens/AdvancedProtectionSettingsScreen.swift`  
**Строка:** После `import SwiftUI`

```swift
struct AdvancedProtectionSettingsScreen: View {
    #if DEBUG
    private static let ENABLE_CRASH_LOGS = true
    #else
    private static let ENABLE_CRASH_LOGS = true
    #endif
    
    init() {
        if Self.ENABLE_CRASH_LOGS {
            print("🔍 ADVANCED_PROTECTION: init() ВЫЗВАН")
            print("🔍 ADVANCED_PROTECTION: Thread.isMainThread = \(Thread.isMainThread)")
        }
    }
    
    // ...
}
```

---

### 15. **Логи в `body`**
**Строка:** ~61

```swift
var body: some View {
    let _ = {
        if Self.ENABLE_CRASH_LOGS {
            print("🔍 ADVANCED_PROTECTION: body НАЧАЛО")
            print("🔍 ADVANCED_PROTECTION: Thread.isMainThread = \(Thread.isMainThread)")
        }
    }()
    
    ZStack {
        // ... код ...
    }
    .onAppear {
        if Self.ENABLE_CRASH_LOGS {
            print("✅ ADVANCED_PROTECTION: body ЗАВЕРШЕН")
        }
    }
}
```

---

### 16. **Логи в `componentsSections`**
**Строка:** ~297

```swift
private var componentsSections: some View {
    let _ = {
        if Self.ENABLE_CRASH_LOGS {
            print("🔍 ADVANCED_PROTECTION: componentsSections НАЧАЛО")
        }
    }()
    
    VStack(spacing: Spacing.l) {
        // ... код ...
    }
}
```

---

### 17. **Логи в `loadFamilyStats()` - КРИТИЧНО!**
**Строка:** ~701

```swift
private func loadFamilyStats() {
    if Self.ENABLE_CRASH_LOGS {
        print("🔍 ADVANCED_PROTECTION: loadFamilyStats() НАЧАЛО")
        print("🔍 ADVANCED_PROTECTION: Thread.isMainThread = \(Thread.isMainThread)")
    }
    
    // Monitoring stats
    if let stats = UserDefaults.standard.dictionary(forKey: "parental_monitoring_stats") {
        if Self.ENABLE_CRASH_LOGS {
            print("✅ ADVANCED_PROTECTION: loadFamilyStats() monitoring stats загружены")
        }
        familyBrowserSitesCount = stats["browserSitesCount"] as? Int ?? familyBrowserSitesCount
        familyAppsUsedCount = stats["appsUsedCount"] as? Int ?? familyAppsUsedCount
    } else {
        if Self.ENABLE_CRASH_LOGS {
            print("⚠️ ADVANCED_PROTECTION: loadFamilyStats() monitoring stats не найдены")
        }
    }

    // Time stats
    if let stats = UserDefaults.standard.dictionary(forKey: "parental_time_stats") as? [String: String] {
        if Self.ENABLE_CRASH_LOGS {
            print("✅ ADVANCED_PROTECTION: loadFamilyStats() time stats загружены")
        }
        familyTotalTimeUsed = stats["totalTimeUsed"] ?? familyTotalTimeUsed
        familyTotalTimeLimit = stats["totalTimeLimit"] ?? familyTotalTimeLimit
    } else {
        if Self.ENABLE_CRASH_LOGS {
            print("⚠️ ADVANCED_PROTECTION: loadFamilyStats() time stats не найдены")
        }
    }

    // App limits count
    if let data = UserDefaults.standard.data(forKey: "app_limits_settings"),
       let decoded = try? JSONDecoder().decode([AppLimitItemCodable].self, from: data) {
        if Self.ENABLE_CRASH_LOGS {
            print("✅ ADVANCED_PROTECTION: loadFamilyStats() app limits загружены: \(decoded.count)")
        }
        familyAppLimitsCount = decoded.count
    } else {
        if Self.ENABLE_CRASH_LOGS {
            print("⚠️ ADVANCED_PROTECTION: loadFamilyStats() app limits не найдены")
        }
        familyAppLimitsCount = 0
    }
    
    if Self.ENABLE_CRASH_LOGS {
        print("✅ ADVANCED_PROTECTION: loadFamilyStats() ЗАВЕРШЕН")
    }
}
```

---

### 18. **Логи в `applySafariUnionRules()` - КРИТИЧНО!**
**Строка:** ~985

```swift
private func applySafariUnionRules(triggeredBy trigger: SafariSettingsSheet) {
    if Self.ENABLE_CRASH_LOGS {
        print("🔍 ADVANCED_PROTECTION: applySafariUnionRules() НАЧАЛО")
        print("🔍 ADVANCED_PROTECTION: trigger = \(trigger)")
        print("🔍 ADVANCED_PROTECTION: Thread.isMainThread = \(Thread.isMainThread)")
    }
    
    guard !isApplyingSafariRules else {
        if Self.ENABLE_CRASH_LOGS {
            print("⚠️ ADVANCED_PROTECTION: applySafariUnionRules() уже выполняется, пропускаем")
        }
        return
    }
    
    isApplyingSafariRules = true

    Task {
        defer { 
            Task { @MainActor in 
                isApplyingSafariRules = false
                if Self.ENABLE_CRASH_LOGS {
                    print("✅ ADVANCED_PROTECTION: applySafariUnionRules() ЗАВЕРШЕН")
                }
            } 
        }
        
        if Self.ENABLE_CRASH_LOGS {
            print("🔍 ADVANCED_PROTECTION: applySafariUnionRules() проверка статуса")
        }
        await contentBlockerManager.checkBlockingStatus()

        // если пользователь пытается включить карточку, но extension выключен
        if case .needsActivation = contentBlockerManager.status {
            if Self.ENABLE_CRASH_LOGS {
                print("⚠️ ADVANCED_PROTECTION: applySafariUnionRules() extension не активирован")
            }
            await MainActor.run {
                if trigger == .sites, safariSitesEnabled { safariSitesEnabled = false }
                if trigger == .social, safariSocialEnabled { safariSocialEnabled = false }
                safariSettingsSheet = trigger
            }
            return
        }

        let sitesCategories = safariSitesEnabled ? getSafariSitesCategories() : []
        let socialCategories: [ContentBlockerCategory] = safariSocialEnabled ? [.socialMedia] : []
        let union = Array(Set(sitesCategories + socialCategories))

        if Self.ENABLE_CRASH_LOGS {
            print("🔍 ADVANCED_PROTECTION: applySafariUnionRules() категории: \(union.count)")
        }

        if union.isEmpty {
            if Self.ENABLE_CRASH_LOGS {
                print("🔍 ADVANCED_PROTECTION: applySafariUnionRules() отключение content blocker")
            }
            await contentBlockerManager.disableContentBlocker()
        } else {
            if Self.ENABLE_CRASH_LOGS {
                print("🔍 ADVANCED_PROTECTION: applySafariUnionRules() включение content blocker")
            }
            try? await contentBlockerManager.enableContentBlocker(categories: union)
        }

        await contentBlockerManager.checkBlockingStatus()
        await MainActor.run {
            contentBlockerManager.loadActiveCategories()
        }
    }
}
```

---

## 🟡 ВАЖНО (ADVANCED PROTECTION SETTINGS SCREEN)

### 19. **Логи в `refreshContentBlockerStatus()`**
**Строка:** ~586

### 20. **Логи в `refreshThreatStatuses()`**
**Строка:** ~598

### 21. **Логи в `setThreatAggregate(isOn:)`**
**Строка:** ~638

### 22. **Логи в `threatProtectionAggregatorCard`**
**Строка:** ~646

---

## 📋 ПОЛНЫЙ СПИСОК ВСЕХ МЕСТ

### **SETTINGS SCREEN (05_SettingsScreen.swift):**

#### Секции (6 мест):
1. ❌ `profileSection()` - строка ~463
2. ❌ `securitySection()` - строка ~558
3. ❌ `notificationsSection()` - строка ~738
4. ❌ `appSection()` - строка ~785
5. ❌ `systemComponentsSection()` - строка ~858 (КРИТИЧНО!)
6. ❌ `additionalSection()` - строка ~1019

#### Функции (4 места):
7. ❌ `loadComponents()` - строка ~923 (КРИТИЧНО!)
8. ❌ `toggleComponent()` - строка ~947 (КРИТИЧНО!)
9. ⚠️ `handleBiometricToggle()` - строка ~1150 (улучшить)
10. ⚠️ `cycleTheme()` - строка ~1361 (улучшить)
11. ❌ `checkForUpdates()` - строка ~1391

#### Computed Properties (2 места):
12. ❌ `calculatedProtectionLevel` - строка ~1300
13. ❌ `protectionLevelText` - строка ~1327

---

### **ADVANCED PROTECTION SETTINGS SCREEN:**

#### Основные точки (3 места):
14. ❌ `ENABLE_CRASH_LOGS` флаг - добавить
15. ❌ `init()` - добавить
16. ❌ `body` - добавить логи

#### Computed Properties (5 мест):
17. ❌ `componentsSections` - строка ~297
18. ❌ `threatProtectionAggregatorCard` - строка ~646
19. ❌ `familyActivityMonitoringCard` - строка ~723
20. ❌ `familyTimeControlCard` - строка ~792
21. ❌ `familyAppLimitsCard` - строка ~830

#### Функции (8 мест):
22. ❌ `refreshContentBlockerStatus()` - строка ~586
23. ❌ `refreshThreatStatuses()` - строка ~598
24. ❌ `setThreatAggregate(isOn:)` - строка ~638
25. ❌ `loadFamilyStats()` - строка ~701 (КРИТИЧНО!)
26. ❌ `applySafariUnionRules(triggeredBy:)` - строка ~985 (КРИТИЧНО!)
27. ❌ `getSafariSitesCategories()` - строка ~958
28. ❌ `setSafariSitesCategories(_:)` - строка ~967
29. ❌ `syncSafariCardsFromActiveCategories()` - строка ~972

---

## 🎯 ПРИОРИТЕТЫ

### **ПРИОРИТЕТ #1 (КРИТИЧНО - СЕГОДНЯ):**
1. ✅ `systemComponentsSection()` - логи
2. ✅ `loadComponents()` - логи
3. ✅ `toggleComponent()` - логи
4. ✅ `notificationsSection()` - логи
5. ✅ `AdvancedProtectionSettingsScreen` - добавить флаг и логи в `init()`, `body`, `onAppear`
6. ✅ `loadFamilyStats()` - логи
7. ✅ `applySafariUnionRules()` - логи

**Время:** ~2 часа

---

### **ПРИОРИТЕТ #2 (ВАЖНО - ЗАВТРА):**
8. ✅ `securitySection()` - логи
9. ✅ `appSection()` - логи
10. ✅ `calculatedProtectionLevel` - логи
11. ✅ `handleBiometricToggle()` - улучшить логи
12. ✅ `refreshContentBlockerStatus()` - логи
13. ✅ `refreshThreatStatuses()` - логи
14. ✅ `setThreatAggregate(isOn:)` - логи
15. ✅ `componentsSections` - логи
16. ✅ `threatProtectionAggregatorCard` - логи

**Время:** ~1.5 часа

---

### **ПРИОРИТЕТ #3 (ЖЕЛАТЕЛЬНО - ПОЗЖЕ):**
17. ✅ `profileSection()` - логи
18. ✅ `additionalSection()` - логи
19. ✅ `cycleTheme()` - улучшить логи
20. ✅ `checkForUpdates()` - логи
21. ✅ `protectionLevelText` - логи
22. ✅ Остальные computed properties в AdvancedProtectionSettingsScreen

**Время:** ~1 час

---

## ✅ ИТОГОВЫЙ ЧЕКЛИСТ

### **SETTINGS SCREEN:**
- [ ] `profileSection()` - логи
- [ ] `securitySection()` - логи
- [ ] `notificationsSection()` - логи
- [ ] `appSection()` - логи
- [ ] `systemComponentsSection()` - логи (КРИТИЧНО!)
- [ ] `additionalSection()` - логи
- [ ] `loadComponents()` - логи (КРИТИЧНО!)
- [ ] `toggleComponent()` - логи (КРИТИЧНО!)
- [ ] `handleBiometricToggle()` - улучшить логи
- [ ] `cycleTheme()` - улучшить логи
- [ ] `checkForUpdates()` - логи
- [ ] `calculatedProtectionLevel` - логи
- [ ] `protectionLevelText` - логи

### **ADVANCED PROTECTION SETTINGS SCREEN:**
- [ ] `ENABLE_CRASH_LOGS` флаг
- [ ] `init()` - логи
- [ ] `body` - логи
- [ ] `onAppear` - логи
- [ ] `componentsSections` - логи
- [ ] `refreshContentBlockerStatus()` - логи
- [ ] `refreshThreatStatuses()` - логи
- [ ] `setThreatAggregate(isOn:)` - логи
- [ ] `loadFamilyStats()` - логи (КРИТИЧНО!)
- [ ] `applySafariUnionRules()` - логи (КРИТИЧНО!)
- [ ] `threatProtectionAggregatorCard` - логи
- [ ] `familyActivityMonitoringCard` - логи
- [ ] `familyTimeControlCard` - логи
- [ ] `familyAppLimitsCard` - логи
- [ ] `getSafariSitesCategories()` - логи
- [ ] `setSafariSitesCategories(_:)` - логи
- [ ] `syncSafariCardsFromActiveCategories()` - логи

---

**ВСЕГО:** 30 мест где нужно добавить/улучшить логирование

**КРИТИЧНО:** 7 мест (SETTINGS SCREEN: 4, ADVANCED PROTECTION: 3)  
**ВАЖНО:** 9 мест  
**ЖЕЛАТЕЛЬНО:** 14 мест

---

**ВЫВОД:** Нужно добавить логи в **13 мест в SettingsScreen** и **17 мест в AdvancedProtectionSettingsScreen**. Критично - `systemComponentsSection()`, `loadComponents()`, `toggleComponent()`, `notificationsSection()`, и весь `AdvancedProtectionSettingsScreen` (особенно `loadFamilyStats()` и `applySafariUnionRules()`).
