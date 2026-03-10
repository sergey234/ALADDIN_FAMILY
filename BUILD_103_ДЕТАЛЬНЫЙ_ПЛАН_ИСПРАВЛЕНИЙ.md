# 📋 BUILD 103: ДЕТАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЙ

**Дата:** 2026-03-11  
**Build:** 103  
**Цель:** Исправить краш с Dictionary.resize, используя `Task { @MainActor in }` вместо костылей

---

## 🤔 ПОЧЕМУ ЭТО ПРАВИЛЬНО?

### ✅ `Task { @MainActor in }` - это НЕ костыль!

**Причины:**

1. **Явно указываем контекст при создании Task**
   - Мы явно говорим Swift: "выполни этот код на main thread"
   - Это стандартная практика Swift Concurrency
   - Это лучше, чем полагаться на неявное поведение `@MainActor`

2. **Соответствует best practices Swift Concurrency**
   - Apple рекомендует использовать `Task { @MainActor in }` для UI операций
   - Это явное указание намерения разработчика
   - Код становится понятнее и проще поддерживать

3. **Не используем `await MainActor.run {}` внутри методов**
   - Мы НЕ добавляем костыли внутрь методов ViewModel
   - Методы остаются чистыми и простыми
   - Вся логика выполнения на main thread находится в одном месте - при создании Task

4. **Код проще и понятнее**
   - Видно сразу, что код выполняется на main thread
   - Не нужно искать по всему коду, где используется `await MainActor.run`
   - Легче понять поток выполнения

---

## 📍 КОНКРЕТНЫЕ МЕСТА ИСПРАВЛЕНИЙ

### 🎯 ЭТАП 1: Исправить все тумблеры на странице NetworkProtectionScreen

**Файл:** `Screens/03_NetworkProtectionScreen.swift`

#### Раздел 1: Экстренная помощь (4 тумблера)

**1.1. Crash Detection (строка 210)**
```swift
// ❌ Было:
onToggle: { newValue in
    logger.toggleChanged("Crash Detection", newValue: newValue, screen: "NetworkProtection")
    Task { await viewModel.toggleCrashDetection(newValue) }
}

// ✅ Стало:
onToggle: { newValue in
    logger.toggleChanged("Crash Detection", newValue: newValue, screen: "NetworkProtection")
    Task { @MainActor in await viewModel.toggleCrashDetection(newValue) }
}
```

**1.2. Roadside Assistance (строка 257)**
```swift
// ❌ Было:
onToggle: { newValue in
    logger.toggleChanged("Roadside Assistance", newValue: newValue, screen: "NetworkProtection")
    Task { await viewModel.toggleRoadsideAssistance(newValue) }
}

// ✅ Стало:
onToggle: { newValue in
    logger.toggleChanged("Roadside Assistance", newValue: newValue, screen: "NetworkProtection")
    Task { @MainActor in await viewModel.toggleRoadsideAssistance(newValue) }
}
```

**1.3. Emergency Response (строка 267)**
```swift
// ❌ Было:
onToggle: { newValue in Task { await viewModel.toggleEmergencyResponse(newValue) } }

// ✅ Стало:
onToggle: { newValue in Task { @MainActor in await viewModel.toggleEmergencyResponse(newValue) } }
```

**1.4. Emergency Event (строка 276)**
```swift
// ❌ Было:
onToggle: { newValue in Task { await viewModel.toggleEmergencyEvent(newValue) } }

// ✅ Стало:
onToggle: { newValue in Task { @MainActor in await viewModel.toggleEmergencyEvent(newValue) } }
```

#### Раздел 2: Защита от угроз (4 тумблера)

**2.1. Phishing Protection (строка 293)**
```swift
// ❌ Было:
onToggle: { newValue in Task { await viewModel.togglePhishingProtection(newValue) } },

// ✅ Стало:
onToggle: { newValue in Task { @MainActor in await viewModel.togglePhishingProtection(newValue) } },
```

**2.2. Malware Detection (строка 303)**
```swift
// ❌ Было:
onToggle: { newValue in Task { await viewModel.toggleMalwareDetection(newValue) } },

// ✅ Стало:
onToggle: { newValue in Task { @MainActor in await viewModel.toggleMalwareDetection(newValue) } },
```

**2.3. Mobile Security (строка 313)**
```swift
// ❌ Было:
onToggle: { newValue in Task { await viewModel.toggleMobileSecurity(newValue) } },

// ✅ Стало:
onToggle: { newValue in Task { @MainActor in await viewModel.toggleMobileSecurity(newValue) } },
```

**2.4. Network Security (строка 323)**
```swift
// ❌ Было:
onToggle: { newValue in Task { await viewModel.toggleNetworkSecurity(newValue) } },

// ✅ Стало:
onToggle: { newValue in Task { @MainActor in await viewModel.toggleNetworkSecurity(newValue) } },
```

#### Раздел 3: Автоматическая система защиты (1 тумблер)

**3.1. Incident Response (строка 341)**
```swift
// ❌ Было:
onToggle: { newValue in Task { await viewModel.toggleIncidentResponse(newValue) } },

// ✅ Стало:
onToggle: { newValue in Task { @MainActor in await viewModel.toggleIncidentResponse(newValue) } },
```

#### Раздел 4: Безопасность паролей (1 тумблер)

**4.1. Password Security (строка 359)**
```swift
// ❌ Было:
onToggle: { newValue in Task { await viewModel.togglePasswordSecurity(newValue) } },

// ✅ Стало:
onToggle: { newValue in Task { @MainActor in await viewModel.togglePasswordSecurity(newValue) } },
```

**ИТОГО: 10 тумблеров на странице NetworkProtectionScreen**

---

### 🎯 ЭТАП 2: Исправить все модальные окна настроек

#### 2.1. NetworkSecuritySettingsModal.swift

**Файл:** `Shared/Components/Modals/NetworkSecuritySettingsModal.swift`

**2.1.1. Загрузка настроек (строка 128)**
```swift
// ❌ Было:
private func loadSettings() {
    isLoading = true
    Task {
        do {
            let config = try await configurationService.getConfiguration(for: componentId)
            // ...
        }
    }
}

// ✅ Стало:
private func loadSettings() {
    isLoading = true
    Task { @MainActor in
        do {
            let config = try await configurationService.getConfiguration(for: componentId)
            // ...
        }
    }
}
```

**2.1.2. Сохранение настроек (строка 165) - КРИТИЧНО!**
```swift
// ❌ Было:
private func saveSettings() {
    Task {
        do {
            let isComponentEnabled = await MainActor.run {
                ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)
            }

            let config = ComponentConfiguration(
                isEnabled: isComponentEnabled,
                priority: .normal,
                additionalSettings: [
                    "blockUnsafeNetworks": AnyCodable(blockUnsafeNetworks),
                    "warnOnPublicWiFi": AnyCodable(warnOnPublicWiFi),
                    "autoConnectVPN": AnyCodable(autoConnectVPN),
                    "blockTracking": AnyCodable(blockTracking),
                    "encryptTraffic": AnyCodable(encryptTraffic),
                    "firewallEnabled": AnyCodable(firewallEnabled)
                ]
            )
            // ...
        }
    }
}

// ✅ Стало:
private func saveSettings() {
    Task { @MainActor in
        do {
            let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

            let config = ComponentConfiguration(
                isEnabled: isComponentEnabled,
                priority: .normal,
                additionalSettings: [
                    "blockUnsafeNetworks": AnyCodable(blockUnsafeNetworks),
                    "warnOnPublicWiFi": AnyCodable(warnOnPublicWiFi),
                    "autoConnectVPN": AnyCodable(autoConnectVPN),
                    "blockTracking": AnyCodable(blockTracking),
                    "encryptTraffic": AnyCodable(encryptTraffic),
                    "firewallEnabled": AnyCodable(firewallEnabled)
                ]
            )
            // ...
        }
    }
}
```

**Примечание:** Убрать `await MainActor.run {}` вокруг `getComponentEnabledStatus`, так как весь Task уже на main thread.

---

#### 2.2. PhishingProtectionSettingsModal.swift

**Файл:** `Shared/Components/Modals/PhishingProtectionSettingsModal.swift`

**2.2.1. Загрузка настроек (строка 129)**
```swift
// ❌ Было:
private func loadSettings() {
    isLoading = true
    Task {
        // ...
    }
}

// ✅ Стало:
private func loadSettings() {
    isLoading = true
    Task { @MainActor in
        // ...
    }
}
```

**2.2.2. Сохранение настроек (строка 162) - КРИТИЧНО!**
```swift
// ❌ Было:
private func saveSettings() {
    Task {
        do {
            let isComponentEnabled = await MainActor.run {
                ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)
            }

            let config = ComponentConfiguration(
                isEnabled: isComponentEnabled,
                priority: .normal,
                additionalSettings: [
                    "blockSuspiciousLinks": AnyCodable(blockSuspiciousLinks),
                    "warnBeforeOpening": AnyCodable(warnBeforeOpening),
                    "checkEmailLinks": AnyCodable(checkEmailLinks),
                    "checkSMSLinks": AnyCodable(checkSMSLinks),
                    "blockKnownPhishingDomains": AnyCodable(blockKnownPhishingDomains),
                    "sensitivityLevel": AnyCodable(sensitivityLevel)
                ]
            )
            // ...
        }
    }
}

// ✅ Стало:
private func saveSettings() {
    Task { @MainActor in
        do {
            let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

            let config = ComponentConfiguration(
                isEnabled: isComponentEnabled,
                priority: .normal,
                additionalSettings: [
                    "blockSuspiciousLinks": AnyCodable(blockSuspiciousLinks),
                    "warnBeforeOpening": AnyCodable(warnBeforeOpening),
                    "checkEmailLinks": AnyCodable(checkEmailLinks),
                    "checkSMSLinks": AnyCodable(checkSMSLinks),
                    "blockKnownPhishingDomains": AnyCodable(blockKnownPhishingDomains),
                    "sensitivityLevel": AnyCodable(sensitivityLevel)
                ]
            )
            // ...
        }
    }
}
```

---

#### 2.3. MobileSecuritySettingsModal.swift

**Файл:** `Shared/Components/Modals/MobileSecuritySettingsModal.swift`

**2.3.1. Загрузка настроек (строка 128)**
```swift
// ❌ Было:
Task {
    // ...
}

// ✅ Стало:
Task { @MainActor in
    // ...
}
```

**2.3.2. Сохранение настроек (строка 165) - КРИТИЧНО!**
```swift
// ❌ Было:
Task {
    do {
        let isComponentEnabled = await MainActor.run {
            ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)
        }

        let config = ComponentConfiguration(
            additionalSettings: [
                "deviceEncryption": AnyCodable(deviceEncryption),
                "appLock": AnyCodable(appLock),
                // ...
            ]
        )
        // ...
    }
}

// ✅ Стало:
Task { @MainActor in
    do {
        let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

        let config = ComponentConfiguration(
            additionalSettings: [
                "deviceEncryption": AnyCodable(deviceEncryption),
                "appLock": AnyCodable(appLock),
                // ...
            ]
        )
        // ...
    }
}
```

---

#### 2.4. IncidentResponseSettingsModal.swift

**Файл:** `Shared/Components/Modals/IncidentResponseSettingsModal.swift`

**2.4.1. Загрузка настроек (строка 184)**
```swift
// ❌ Было:
Task {
    // ...
}

// ✅ Стало:
Task { @MainActor in
    // ...
}
```

**2.4.2. Сохранение настроек (строка 222) - КРИТИЧНО!**
```swift
// ❌ Было:
Task {
    do {
        let isComponentEnabled = await MainActor.run {
            ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)
        }

        let config = ComponentConfiguration(
            additionalSettings: [
                "escalationThresholds": AnyCodable(escalationThresholds),
                // ...
            ]
        )
        // ...
    }
}

// ✅ Стало:
Task { @MainActor in
    do {
        let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

        let config = ComponentConfiguration(
            additionalSettings: [
                "escalationThresholds": AnyCodable(escalationThresholds),
                // ...
            ]
        )
        // ...
    }
}
```

---

### 🎯 ЭТАП 3: Исправить ViewModels

#### 3.1. NetworkSecuritySettingsViewModel.swift

**Файл:** `ViewModels/NetworkSecuritySettingsViewModel.swift`

**3.1.1. Сохранение настроек (строка 151) - КРИТИЧНО!**
```swift
// ❌ Было:
Task {
    do {
        let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

        let config = ComponentConfiguration(
            isEnabled: isComponentEnabled,
            priority: .normal,
            additionalSettings: [
                "blockUnsafeNetworks": AnyCodable(state.blockUnsafeNetworks),
                "warnOnPublicWiFi": AnyCodable(state.warnOnPublicWiFi),
                // ...
            ]
        )
        // ...
    }
}

// ✅ Стало:
Task { @MainActor in
    do {
        let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

        let config = ComponentConfiguration(
            isEnabled: isComponentEnabled,
            priority: .normal,
            additionalSettings: [
                "blockUnsafeNetworks": AnyCodable(state.blockUnsafeNetworks),
                "warnOnPublicWiFi": AnyCodable(state.warnOnPublicWiFi),
                // ...
            ]
        )
        // ...
    }
}
```

---

#### 3.2. PhishingSettingsViewModel.swift

**Файл:** `ViewModels/PhishingSettingsViewModel.swift`

**3.2.1. Сохранение настроек (строка 151) - КРИТИЧНО!**
```swift
// ❌ Было:
Task {
    do {
        let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

        let config = ComponentConfiguration(
            additionalSettings: [
                "blockSuspiciousLinks": AnyCodable(state.blockSuspiciousLinks),
                // ...
            ]
        )
        // ...
    }
}

// ✅ Стало:
Task { @MainActor in
    do {
        let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

        let config = ComponentConfiguration(
            additionalSettings: [
                "blockSuspiciousLinks": AnyCodable(state.blockSuspiciousLinks),
                // ...
            ]
        )
        // ...
    }
}
```

---

#### 3.3. MalwareSettingsViewModel.swift

**Файл:** `ViewModels/MalwareSettingsViewModel.swift`

**3.3.1. Загрузка настроек (строка 59)**
```swift
// ❌ Было:
Task {
    // ...
}

// ✅ Стало:
Task { @MainActor in
    // ...
}
```

**3.3.2. Сохранение настроек (строка 151) - КРИТИЧНО!**
```swift
// ❌ Было:
Task {
    do {
        let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

        let config = ComponentConfiguration(
            additionalSettings: [
                // ...
            ]
        )
        // ...
    }
}

// ✅ Стало:
Task { @MainActor in
    do {
        let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

        let config = ComponentConfiguration(
            additionalSettings: [
                // ...
            ]
        )
        // ...
    }
}
```

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### Исправления по файлам:

1. **Screens/03_NetworkProtectionScreen.swift**
   - 10 тумблеров (строки 210, 257, 267, 276, 293, 303, 313, 323, 341, 359)

2. **Модальные окна (4 файла):**
   - NetworkSecuritySettingsModal.swift (2 места: строки 128, 165)
   - PhishingProtectionSettingsModal.swift (2 места: строки 129, 162)
   - MobileSecuritySettingsModal.swift (2 места: строки 128, 165)
   - IncidentResponseSettingsModal.swift (2 места: строки 184, 222)

3. **ViewModels (3 файла):**
   - NetworkSecuritySettingsViewModel.swift (1 место: строка 151)
   - PhishingSettingsViewModel.swift (1 место: строка 151)
   - MalwareSettingsViewModel.swift (2 места: строки 59, 151)

**ИТОГО: 10 + 8 + 4 = 22 места для исправления**

---

## ✅ ПРОВЕРКА ПОСЛЕ ИСПРАВЛЕНИЙ

1. ✅ Все `Task {` заменены на `Task { @MainActor in`
2. ✅ Убраны все `await MainActor.run {}` внутри Task (они больше не нужны)
3. ✅ Dictionary создается на main thread
4. ✅ Код соответствует best practices Swift Concurrency

---

**ГОТОВ К ИСПРАВЛЕНИЮ!** 🚀
