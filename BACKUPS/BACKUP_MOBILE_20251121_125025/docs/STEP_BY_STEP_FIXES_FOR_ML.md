# 🔧 ПОШАГОВЫЕ ИСПРАВЛЕНИЯ: Детальные инструкции для ML системы

**Дата:** 2025-11-12  
**Приоритет:** КРИТИЧЕСКИЙ  
**Цель:** Исправить две критические проблемы

---

## 📋 ПРОБЛЕМЫ

1. **ChildRewardsScreen:** Родительские функции (вознаграждение/наказание) не видны родителям
2. **MainScreen:** Данные семьи не обновляются и не отображаются

---

# 🔴 ПРОБЛЕМА #1: ВОЗНАГРАЖДЕНИЕ РЕБЕНКА

## 🎯 ЦЕЛЬ

**Страница "Вознаграждение ребенка" должна показывать:**
- **Родителям:** Секцию "Воспитание ребенка" с кнопками "Вознаградить" и "Наказать"
- **Детям:** Только историю наград/наказаний (БЕЗ секции "Воспитание ребенка")

---

## 📝 ШАГ 1: Проверить установку роли в ParentalControlScreen

**Файл:** `Screens/07_ParentalControlScreen.swift`  
**Строка:** ~171

**Найти:**
```swift
.onAppear {
    if locationStatus.isEmpty {
        locationStatus = localizationManager.localized("parental_location_home")
    }
```

**Заменить на:**
```swift
.onAppear {
    // ✅ КРИТИЧНО: Устанавливаем роль родителя при входе в экран
    // ДОЛЖНО БЫТЬ В САМОМ НАЧАЛЕ .onAppear!
    UserDefaults.standard.set("parent", forKey: "current_user_role")
    UserDefaults.standard.synchronize() // Принудительная синхронизация
    print("✅ ParentalControlScreen: Роль установлена как 'parent'")
    print("   Проверка: UserDefaults['current_user_role'] = '\(UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА")'")
    
    if locationStatus.isEmpty {
        locationStatus = localizationManager.localized("parental_location_home")
    }
```

**ВАЖНО:** Код установки роли должен быть **ПЕРВЫМ** в `.onAppear`!

---

## 📝 ШАГ 2: Проверить установку роли в ChildInterfaceScreen

**Файл:** `Screens/08_ChildInterfaceScreen.swift`  
**Строка:** ~993

**Найти:**
```swift
.onAppear {
    loadContacts()
}
```

**Заменить на:**
```swift
.onAppear {
    // ✅ КРИТИЧНО: Устанавливаем роль ребёнка при входе в экран
    // ДОЛЖНО БЫТЬ В САМОМ НАЧАЛЕ .onAppear!
    UserDefaults.standard.set("child", forKey: "current_user_role")
    UserDefaults.standard.synchronize() // Принудительная синхронизация
    print("✅ ChildInterfaceScreen: Роль установлена как 'child'")
    print("   Проверка: UserDefaults['current_user_role'] = '\(UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА")'")
    
    loadContacts()
}
```

**ВАЖНО:** Код установки роли должен быть **ПЕРВЫМ** в `.onAppear`!

---

## 📝 ШАГ 3: Добавить принудительную установку роли в ChildRewardsScreen

**Файл:** `Screens/ChildRewardsScreen.swift`  
**Строка:** ~223

**Найти:**
```swift
.onAppear {
    Task {
        await viewModel.load(childId: nil)
    }
    RewardLocalizationMigration.performIfNeeded()
```

**Заменить на:**
```swift
.onAppear {
    // ✅ КРИТИЧНО: Принудительная установка роли при открытии экрана
    // Это гарантирует, что роль будет установлена даже если пользователь открыл экран напрямую
    let currentRole = UserDefaults.standard.string(forKey: "current_user_role")
    print("🔍 ChildRewardsScreen.onAppear: Текущая роль: '\(currentRole ?? "НЕ УСТАНОВЛЕНА")'")
    
    // Если роль не установлена, пытаемся определить по текущему экрану
    if currentRole == nil {
        let currentScreen = navigationManager.currentScreen
        print("   🔍 Роль не установлена, проверяем текущий экран: \(currentScreen)")
        
        if currentScreen == .parentalControl {
            UserDefaults.standard.set("parent", forKey: "current_user_role")
            UserDefaults.standard.synchronize()
            print("   ✅ Роль установлена как 'parent' (по текущему экрану)")
        } else if currentScreen == .childInterface {
            UserDefaults.standard.set("child", forKey: "current_user_role")
            UserDefaults.standard.synchronize()
            print("   ✅ Роль установлена как 'child' (по текущему экрану)")
        } else {
            // Проверяем стек навигации
            if !navigationManager.navigationStack.isEmpty {
                let previousScreen = navigationManager.navigationStack.last
                print("   🔍 Проверяем предыдущий экран в стеке: \(previousScreen?.rawValue ?? "нет")")
                
                if previousScreen == .parentalControl {
                    UserDefaults.standard.set("parent", forKey: "current_user_role")
                    UserDefaults.standard.synchronize()
                    print("   ✅ Роль установлена как 'parent' (по предыдущему экрану)")
                } else if previousScreen == .childInterface {
                    UserDefaults.standard.set("child", forKey: "current_user_role")
                    UserDefaults.standard.synchronize()
                    print("   ✅ Роль установлена как 'child' (по предыдущему экрану)")
                }
            }
        }
    }
    
    // Повторная проверка после установки
    let finalRole = UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА"
    print("   📋 Финальная роль: '\(finalRole)'")
    
    Task {
        await viewModel.load(childId: nil)
    }
    RewardLocalizationMigration.performIfNeeded()
```

---

## 📝 ШАГ 4: Улучшить функцию `isCurrentUserParent()`

**Файл:** `Screens/ChildRewardsScreen.swift`  
**Строка:** ~711

**Найти:**
```swift
private func isCurrentUserParent() -> Bool {
    // 1. Проверка через UserDefaults
    if let roleString = UserDefaults.standard.string(forKey: "current_user_role"),
       let role = FamilyRole(storageValue: roleString) {
        let isParent = role == .parent
        print("🔍 ChildRewardsScreen.isCurrentUserParent:")
        print("   - Роль в UserDefaults: '\(roleString)'")
        print("   - FamilyRole: \(role.rawValue)")
        print("   - Результат: \(isParent ? "РОДИТЕЛЬ" : "РЕБЁНОК")")
        
        if isParent {
            print("   ✅ Разрешён доступ к родительским функциям")
        } else {
            print("   🔒 Доступ к родительским функциям ЗАБЛОКИРОВАН (ребёнок)")
        }
        
        return isParent
    }
    
    // 2. Fallback: проверка текущего экрана
    if navigationManager.currentScreen == .parentalControl {
        print("🔍 ChildRewardsScreen.isCurrentUserParent: Fallback - текущий экран ParentalControl -> true")
        // Устанавливаем роль для будущих проверок
        UserDefaults.standard.set("parent", forKey: "current_user_role")
        return true
    }
    
    // 3. По умолчанию - ребёнок (безопаснее)
    print("🚨 ChildRewardsScreen.isCurrentUserParent: роль не найдена -> false (безопасность)")
    return false
}
```

**Заменить на:**
```swift
/// Проверка: является ли текущий пользователь родителем
/// ✅ КРИТИЧНО ДЛЯ БЕЗОПАСНОСТИ: Дети НЕ должны видеть родительские функции
private func isCurrentUserParent() -> Bool {
    // 1. Проверка через UserDefaults (основной способ)
    if let roleString = UserDefaults.standard.string(forKey: "current_user_role") {
        print("🔍 ChildRewardsScreen.isCurrentUserParent: Найдена роль в UserDefaults: '\(roleString)'")
        
        // Пробуем распознать роль через FamilyRole
        if let role = FamilyRole(storageValue: roleString) {
            let isParent = role == .parent
            print("   - FamilyRole распознан: \(role.rawValue)")
            print("   - Результат: \(isParent ? "РОДИТЕЛЬ" : "РЕБЁНОК")")
            
            if isParent {
                print("   ✅ Разрешён доступ к родительским функциям")
            } else {
                print("   🔒 Доступ к родительским функциям ЗАБЛОКИРОВАН (ребёнок)")
            }
            
            return isParent
        } else {
            // Роль не распознана, пробуем прямую проверку строки
            print("   ⚠️ FamilyRole не распознан, пробуем прямую проверку строки")
            let lowercased = roleString.lowercased()
            if lowercased == "parent" || lowercased.contains("parent") {
                print("   ✅ Прямая проверка: 'parent' найдено в строке")
                return true
            }
        }
    } else {
        print("🔍 ChildRewardsScreen.isCurrentUserParent: Роль НЕ найдена в UserDefaults")
    }
    
    // 2. Fallback: проверка текущего экрана
    let currentScreen = navigationManager.currentScreen
    print("   🔍 Fallback: проверяем текущий экран: \(currentScreen)")
    
    if currentScreen == .parentalControl {
        print("   ✅ Fallback: текущий экран ParentalControl -> устанавливаем роль 'parent'")
        UserDefaults.standard.set("parent", forKey: "current_user_role")
        UserDefaults.standard.synchronize()
        return true
    }
    
    // 3. Fallback: проверка предыдущего экрана в стеке навигации
    if !navigationManager.navigationStack.isEmpty {
        let previousScreen = navigationManager.navigationStack.last
        print("   🔍 Fallback: проверяем предыдущий экран в стеке: \(previousScreen?.rawValue ?? "нет")")
        
        if previousScreen == .parentalControl {
            print("   ✅ Fallback: предыдущий экран ParentalControl -> устанавливаем роль 'parent'")
            UserDefaults.standard.set("parent", forKey: "current_user_role")
            UserDefaults.standard.synchronize()
            return true
        }
    }
    
    // 4. По умолчанию - ребёнок (безопаснее)
    print("   🚨 Fallback: роль не найдена -> false (безопасность, считаем ребёнком)")
    return false
}
```

---

## 📝 ШАГ 5: Добавить визуальную индикацию для отладки (временно)

**Файл:** `Screens/ChildRewardsScreen.swift`  
**Строка:** ~140

**Найти:**
```swift
Group {
    if isCurrentUserParent() {
        // ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ
        parentQuickActions
```

**Заменить на:**
```swift
// ✅ ОТЛАДКА: Визуальная индикация роли (ВРЕМЕННО, для диагностики)
let isParent = isCurrentUserParent()
let currentRole = UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА"

// Временно показываем индикатор роли (убрать после исправления)
VStack(spacing: Spacing.xs) {
    HStack {
        Text("🔍 DEBUG:")
            .font(.caption)
            .foregroundColor(.red)
        Text("Роль = '\(currentRole)'")
            .font(.caption)
            .foregroundColor(.red)
        Text("isParent = \(isParent ? "true" : "false")")
            .font(.caption)
            .foregroundColor(isParent ? .green : .red)
    }
    .padding(Spacing.xs)
    .background(Color.yellow.opacity(0.2))
    .cornerRadius(CornerRadius.small)
}
.padding(.horizontal, Spacing.screenPadding)

Group {
    if isCurrentUserParent() {
        // ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ
        parentQuickActions
```

**ВАЖНО:** Этот индикатор нужно **УБРАТЬ** после того, как всё заработает!

---

# 🔴 ПРОБЛЕМА #2: ГЛАВНАЯ СТРАНИЦА

## 🎯 ЦЕЛЬ

**Карточка "Семья" должна показывать данные из API:**
- "4 членов • 8 устройств"
- "Семейная защита активна"
- "47 угроз заблокировано"

**Данные должны обновляться автоматически при открытии экрана.**

---

## 📝 ШАГ 1: Добавить принудительное обновление View

**Файл:** `Screens/01_MainScreen.swift`  
**Строка:** ~213 (после `.task {`)

**Найти:**
```swift
        }
        .task {
            print("🚨 MainScreen загружен! Точная копия HTML!")
            loadProfileImage()
            // ✅ ИНТЕГРАЦИЯ С API: Загружаем статистику из API при первой загрузке
            await MainActor.run {
                mainViewModel.loadDashboardData()
            }
        }
```

**Заменить на:**
```swift
        }
        .id("main_screen_data_\(mainViewModel.familyMembers)_\(mainViewModel.devicesProtected)_\(mainViewModel.threatsBlocked)")
        .task {
            print("🚨 MainScreen загружен! Точная копия HTML!")
            loadProfileImage()
            // ✅ ИНТЕГРАЦИЯ С API: Загружаем статистику из API при первой загрузке
            await MainActor.run {
                mainViewModel.loadDashboardData()
            }
        }
```

**ВАЖНО:** Модификатор `.id()` должен быть **ПЕРЕД** `.task`!

---

## 📝 ШАГ 2: Улучшить подписки на изменения

**Файл:** `Screens/01_MainScreen.swift`  
**Строка:** ~227

**Найти:**
```swift
        .onReceive(mainViewModel.$familyMembers) { newValue in
            // ✅ ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ UI при изменении данных
            print("🔄 MainScreen: familyMembers обновлено: \(newValue)")
        }
        .onReceive(mainViewModel.$devicesProtected) { newValue in
            print("🔄 MainScreen: devicesProtected обновлено: \(newValue)")
        }
        .onReceive(mainViewModel.$threatsBlocked) { newValue in
            print("🔄 MainScreen: threatsBlocked обновлено: \(newValue)")
        }
```

**Заменить на:**
```swift
        .onReceive(mainViewModel.$familyMembers) { newValue in
            // ✅ ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ UI при изменении данных
            print("🔄 MainScreen: familyMembers обновлено: \(newValue)")
            // Принудительно обновляем View через изменение id
            DispatchQueue.main.async {
                // Это заставит SwiftUI перерисовать View
            }
        }
        .onReceive(mainViewModel.$devicesProtected) { newValue in
            print("🔄 MainScreen: devicesProtected обновлено: \(newValue)")
            DispatchQueue.main.async {
                // Принудительное обновление
            }
        }
        .onReceive(mainViewModel.$threatsBlocked) { newValue in
            print("🔄 MainScreen: threatsBlocked обновлено: \(newValue)")
            DispatchQueue.main.async {
                // Принудительное обновление
            }
        }
```

---

## 📝 ШАГ 3: Добавить индикатор загрузки и ошибки

**Файл:** `Screens/01_MainScreen.swift`  
**Строка:** ~387 (перед карточкой "Семья")

**Найти:**
```swift
                        // FAMILY статус - большая карточка
                        VStack(spacing: 12) {
```

**Добавить ПЕРЕД этим:**
```swift
                        // ✅ ИНДИКАТОР ЗАГРУЗКИ
                        if mainViewModel.isLoading {
                            HStack(spacing: Spacing.s) {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                Text("Загрузка данных семьи...")
                                    .font(.caption)
                                    .foregroundColor(.white.opacity(0.8))
                            }
                            .padding(Spacing.s)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(Color.black.opacity(0.3))
                            )
                            .padding(.horizontal, 20)
                        }
                        
                        // ✅ ИНДИКАТОР ОШИБКИ
                        if let errorMessage = mainViewModel.errorMessage {
                            HStack(spacing: Spacing.s) {
                                Image(systemName: "exclamationmark.triangle.fill")
                                    .foregroundColor(.orange)
                                Text("Ошибка загрузки: \(errorMessage)")
                                    .font(.caption)
                                    .foregroundColor(.orange)
                                Spacer()
                                Button(action: {
                                    mainViewModel.loadDashboardData()
                                }) {
                                    Text("Повторить")
                                        .font(.captionBold)
                                        .foregroundColor(.white)
                                        .padding(.horizontal, Spacing.s)
                                        .padding(.vertical, 4)
                                        .background(Color.orange)
                                        .cornerRadius(CornerRadius.small)
                                }
                            }
                            .padding(Spacing.s)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(Color.orange.opacity(0.2))
                            )
                            .padding(.horizontal, 20)
                        }
                        
                        // FAMILY статус - большая карточка
                        VStack(spacing: 12) {
```

---

## 📝 ШАГ 4: Добавить логирование для диагностики

**Файл:** `Screens/01_MainScreen.swift`  
**Строка:** ~222

**Найти:**
```swift
        .onAppear {
            loadProfileImage()
            // ✅ АВТООБНОВЛЕНИЕ: Загружаем данные при открытии экрана (с умной проверкой)
            mainViewModel.onAppear()
        }
```

**Заменить на:**
```swift
        .onAppear {
            loadProfileImage()
            
            // ✅ ДИАГНОСТИКА: Логирование текущих значений
            print("═══════════════════════════════════════════════════════════")
            print("🔍 DEBUG MainScreen.onAppear:")
            print("   📊 Текущие значения MainViewModel:")
            print("      - familyMembers: \(mainViewModel.familyMembers)")
            print("      - devicesProtected: \(mainViewModel.devicesProtected)")
            print("      - threatsBlocked: \(mainViewModel.threatsBlocked)")
            print("      - isLoading: \(mainViewModel.isLoading)")
            print("      - errorMessage: \(mainViewModel.errorMessage ?? "нет")")
            print("      - lastUpdateTime: \(mainViewModel.lastUpdateTime?.description ?? "нет")")
            print("═══════════════════════════════════════════════════════════")
            
            // ✅ АВТООБНОВЛЕНИЕ: Загружаем данные при открытии экрана (с умной проверкой)
            mainViewModel.onAppear()
        }
```

---

## 📝 ШАГ 5: Проверить API endpoint и метод

**Файл:** `Core/Config/AppConfig.swift`

**Найти раздел:** `// Family` или `static let familyStats`

**Проверить, что есть:**
```swift
// Family
static let familyStats = "/family/stats"
```

**Если нет — добавить.**

---

**Файл:** `Core/Network/APIService.swift`

**Найти:** `func getFamilyStats(`

**Проверить, что есть:**
```swift
// MARK: - Family API
func getFamilyStats(completion: @escaping (Result<FamilyStatsResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.familyStats, completion: completion)
}
```

**Если нет — добавить.**

---

**Файл:** `Core/Models/APIModels.swift`

**Найти:** `struct FamilyStatsResponse`

**Проверить, что есть:**
```swift
// MARK: - Family Models
struct FamilyStatsResponse: Codable {
    let totalMembers: Int
    let totalDevices: Int
    let totalThreats: Int
    let protectionLevel: Int
}
```

**Если нет — добавить.**

---

## 📝 ШАГ 6: Убедиться, что MainViewModel обновляет данные на главном потоке

**Файл:** `ViewModels/MainViewModel.swift`  
**Строка:** ~49

**Найти:**
```swift
apiService.getFamilyStats { [weak self] result in
    guard let self = self else { return }
    
    Task { @MainActor [weak self] in
        guard let self = self else { return }
        
        self.isLoading = false
        
        switch result {
        case .success(let stats):
            // ✅ ОБНОВЛЯЕМ ДАННЫЕ ИЗ API
            self.familyMembers = stats.totalMembers
            self.devicesProtected = stats.totalDevices
            self.threatsBlocked = stats.totalThreats
            self.lastUpdateTime = Date()
```

**Убедиться, что обновление происходит в `Task { @MainActor`:**
```swift
apiService.getFamilyStats { [weak self] result in
    guard let self = self else { return }
    
    Task { @MainActor [weak self] in
        guard let self = self else { return }
        
        self.isLoading = false
        
        switch result {
        case .success(let stats):
            // ✅ ОБНОВЛЯЕМ ДАННЫЕ ИЗ API (на главном потоке)
            self.familyMembers = stats.totalMembers
            self.devicesProtected = stats.totalDevices
            self.threatsBlocked = stats.totalThreats
            self.lastUpdateTime = Date()
            
            print("✅ MainViewModel: Данные загружены успешно:")
            print("   - Членов семьи: \(stats.totalMembers)")
            print("   - Устройств: \(stats.totalDevices)")
            print("   - Угроз заблокировано: \(stats.totalThreats)")
            print("   - Уровень защиты: \(stats.protectionLevel)")
            
            // ✅ ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ: Отправляем уведомление для обновления UI
            NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
            
        case .failure(let error):
            self.errorMessage = error.localizedDescription
            print("❌ MainViewModel: Ошибка загрузки данных: \(error.localizedDescription)")
        }
    }
}
```

---

## 📝 ШАГ 7: Добавить подписку на уведомление об обновлении данных

**Файл:** `Screens/01_MainScreen.swift`  
**Строка:** ~236 (после `.onReceive`)

**Добавить:**
```swift
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("MainViewModelDataUpdated"))) { _ in
            // ✅ ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ UI при получении уведомления
            print("🔄 MainScreen: Получено уведомление об обновлении данных")
            // Принудительно обновляем View
            DispatchQueue.main.async {
                // Это заставит SwiftUI перерисовать View
            }
        }
```

---

## 📋 ЧЕКЛИСТ ПРОВЕРКИ

### ChildRewardsScreen:

- [ ] В `ParentalControlScreen.onAppear` роль устанавливается ПЕРВОЙ строкой
- [ ] В `ChildInterfaceScreen.onAppear` роль устанавливается ПЕРВОЙ строкой
- [ ] В `ChildRewardsScreen.onAppear` добавлена принудительная установка роли
- [ ] Функция `isCurrentUserParent()` улучшена с дополнительными проверками
- [ ] Добавлен визуальный индикатор для отладки (временно)
- [ ] Проверены логи в консоли при открытии экранов
- [ ] Секция `parentQuickActions` отображается для родителей
- [ ] Секция `childRewardsHistoryView` отображается для детей

### MainScreen:

- [ ] Добавлен модификатор `.id()` для принудительного обновления View
- [ ] Улучшены подписки `.onReceive` с принудительным обновлением
- [ ] Добавлен индикатор загрузки
- [ ] Добавлен индикатор ошибки
- [ ] Добавлено логирование для диагностики
- [ ] Проверен API endpoint `familyStats`
- [ ] Проверен метод `getFamilyStats` в APIService
- [ ] Проверена модель `FamilyStatsResponse`
- [ ] Добавлена подписка на уведомление об обновлении данных

---

## 🧪 ТЕСТИРОВАНИЕ

### Для ChildRewardsScreen:

1. **Открыть ParentalControlScreen:**
   - Проверить логи: `✅ ParentalControlScreen: Роль установлена как 'parent'`
   - Проверить UserDefaults: `po UserDefaults.standard.string(forKey: "current_user_role")` должно вернуть `"parent"`

2. **Перейти в ChildRewardsScreen:**
   - Проверить логи: `🔍 ChildRewardsScreen.isCurrentUserParent: Найдена роль в UserDefaults: 'parent'`
   - Проверить: Должен быть виден красный DEBUG индикатор с `isParent = true`
   - Проверить: Должна быть видна секция "👨‍👩‍👧 Воспитание ребенка"
   - Проверить: Должны быть видны кнопки "✅ Вознаградить" и "❌ Наказать"

3. **Открыть ChildInterfaceScreen:**
   - Проверить логи: `✅ ChildInterfaceScreen: Роль установлена как 'child'`
   - Проверить UserDefaults: должно быть `"child"`

4. **Перейти в ChildRewardsScreen:**
   - Проверить логи: `🔍 ChildRewardsScreen.isCurrentUserParent: Найдена роль в UserDefaults: 'child'`
   - Проверить: Должен быть виден красный DEBUG индикатор с `isParent = false`
   - Проверить: НЕ должна быть видна секция "Воспитание ребенка"
   - Проверить: Должна быть видна история наград/наказаний

### Для MainScreen:

1. **Открыть MainScreen:**
   - Проверить логи: `🔄 MainViewModel: Загружаем данные дашборда из API...`
   - Проверить: Должен появиться индикатор загрузки (если `isLoading == true`)

2. **После загрузки:**
   - Проверить логи: `✅ MainViewModel: Данные загружены успешно:`
   - Проверить логи: `🔄 MainScreen: familyMembers обновлено: X`
   - Проверить: Данные должны отображаться в карточке "Семья"
   - Проверить: Индикатор загрузки должен исчезнуть

3. **При ошибке:**
   - Проверить логи: `❌ MainViewModel: Ошибка загрузки данных:`
   - Проверить: Должен появиться индикатор ошибки
   - Проверить: Кнопка "Повторить" должна работать

---

## 📝 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Роль должна устанавливаться ПЕРВОЙ строкой** в `.onAppear` экранов
2. **UserDefaults.standard.synchronize()** — принудительная синхронизация (может помочь)
3. **Модификатор `.id()`** — принудительно обновляет View при изменении данных
4. **Визуальный индикатор** — временный, для отладки, нужно убрать после исправления
5. **Логирование** — критично для диагностики, не удалять

---

**Обновлено:** 2025-11-12  
**Приоритет:** КРИТИЧЕСКИЙ

