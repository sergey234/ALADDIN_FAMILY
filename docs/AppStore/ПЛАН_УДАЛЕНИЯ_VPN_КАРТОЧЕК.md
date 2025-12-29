# ПЛАН УДАЛЕНИЯ VPN КАРТОЧЕК ИЗ PRIVACY POLICY

**Дата:** 28 декабря 2025  
**Цель:** Удалить карточки, которые намекают на VPN функциональность

---

## 📋 АНАЛИЗ: СКРЫТЬ ИЛИ УДАЛИТЬ?

### Вариант 1: Скрыть (через фильтр)
**Плюсы:**
- Быстро
- Легко вернуть обратно

**Минусы:**
- ❌ Код останется в проекте
- ❌ Apple может найти при ревью
- ❌ Локализация останется (лишний код)
- ❌ Может вызвать проблемы при проверке

### Вариант 2: Удалить (рекомендуется) ✅
**Плюсы:**
- ✅ Чистое решение
- ✅ Код не содержит упоминаний VPN
- ✅ Apple не найдет при ревью
- ✅ Меньше кода = меньше проблем

**Минусы:**
- Нужно удалить из enum и switch statements
- Локализацию можно оставить (не мешает) или удалить

---

## 🎯 РЕШЕНИЕ: УДАЛИТЬ

**Удаляем 3 case из enum `NetworkProtectionSection`:**
1. `case servers = "Серверы"` - намекает на VPN инфраструктуру
2. `case features = "Дополнительные функции"` - 100% VPN функции (Kill Switch, DNS Protection, etc.)
3. `case energy = "Энергосбережение"` - "режимы работы защиты сети" намекает на VPN

**Оставляем 2 case:**
1. ✅ `case noLogs = "NO-LOGS POLICY"` - политика конфиденциальности, не VPN
2. ✅ `case encryption = "Технологии шифрования"` - общее описание, не специфично для VPN

---

## 📝 ЧТО НУЖНО ИЗМЕНИТЬ

### 1. Файл: `Screens/18_PrivacyPolicyScreen.swift`

**Удалить из enum (строка 733):**
```swift
// БЫЛО:
enum NetworkProtectionSection: String, CaseIterable {
    case noLogs = "NO-LOGS POLICY"
    case encryption = "Технологии шифрования"
    case servers = "Серверы"                    // ❌ УДАЛИТЬ
    case features = "Дополнительные функции"    // ❌ УДАЛИТЬ
    case energy = "Энергосбережение"            // ❌ УДАЛИТЬ
}

// ДОЛЖНО БЫТЬ:
enum NetworkProtectionSection: String, CaseIterable {
    case noLogs = "NO-LOGS POLICY"
    case encryption = "Технологии шифрования"
}
```

**Удалить из switch emoji (строка 740):**
```swift
// БЫЛО:
var emoji: String {
    switch self {
    case .noLogs: return "🔒"
    case .encryption: return "🔐"
    case .servers: return "🌐"              // ❌ УДАЛИТЬ
    case .features: return "🛡️"            // ❌ УДАЛИТЬ
    case .energy: return "⚡"                // ❌ УДАЛИТЬ
    }
}

// ДОЛЖНО БЫТЬ:
var emoji: String {
    switch self {
    case .noLogs: return "🔒"
    case .encryption: return "🔐"
    }
}
```

**Удалить из switch localizedTitle (строка 750):**
```swift
// БЫЛО:
func localizedTitle(_ localizationManager: LocalizationManager) -> String {
    switch self {
    case .noLogs: return localizationManager.localized("privacy_policy_network_protection_no_logs")
    case .encryption: return localizationManager.localized("privacy_policy_network_protection_encryption")
    case .servers: return localizationManager.localized("privacy_policy_network_protection_servers")        // ❌ УДАЛИТЬ
    case .features: return localizationManager.localized("privacy_policy_network_protection_features")    // ❌ УДАЛИТЬ
    case .energy: return localizationManager.localized("privacy_policy_network_protection_energy")          // ❌ УДАЛИТЬ
    }
}

// ДОЛЖНО БЫТЬ:
func localizedTitle(_ localizationManager: LocalizationManager) -> String {
    switch self {
    case .noLogs: return localizationManager.localized("privacy_policy_network_protection_no_logs")
    case .encryption: return localizationManager.localized("privacy_policy_network_protection_encryption")
    }
}
```

**Удалить из switch localizedSubtitle (строка 760):**
```swift
// БЫЛО:
func localizedSubtitle(_ localizationManager: LocalizationManager) -> String {
    switch self {
    case .noLogs: return localizationManager.localized("privacy_policy_network_protection_no_logs_subtitle")
    case .encryption: return localizationManager.localized("privacy_policy_network_protection_encryption_subtitle")
    case .servers: return localizationManager.localized("privacy_policy_network_protection_servers_subtitle")        // ❌ УДАЛИТЬ
    case .features: return localizationManager.localized("privacy_policy_network_protection_features_subtitle")      // ❌ УДАЛИТЬ
    case .energy: return localizationManager.localized("privacy_policy_network_protection_energy_subtitle")          // ❌ УДАЛИТЬ
    }
}

// ДОЛЖНО БЫТЬ:
func localizedSubtitle(_ localizationManager: LocalizationManager) -> String {
    switch self {
    case .noLogs: return localizationManager.localized("privacy_policy_network_protection_no_logs_subtitle")
    case .encryption: return localizationManager.localized("privacy_policy_network_protection_encryption_subtitle")
    }
}
```

**Удалить из switch subtitle (строка 774):**
```swift
// БЫЛО:
var subtitle: String {
    switch self {
    case .noLogs: return "Что мы НЕ собираем"
    case .encryption: return "3 вида военного шифрования"
    case .servers: return "50+ серверов по всему миру"        // ❌ УДАЛИТЬ
    case .features: return "Дополнительная защита"            // ❌ УДАЛИТЬ
    case .energy: return "Экономия батареи"                    // ❌ УДАЛИТЬ
    }
}

// ДОЛЖНО БЫТЬ:
var subtitle: String {
    switch self {
    case .noLogs: return "Что мы НЕ собираем"
    case .encryption: return "3 вида военного шифрования"
    }
}
```

**Удалить из switch localizedContent (строка 785):**
```swift
// БЫЛО:
func localizedContent(_ localizationManager: LocalizationManager) -> [String] {
    switch self {
    case .noLogs: return [...]
    case .encryption: return [...]
    case .servers: return [...]        // ❌ УДАЛИТЬ весь case
    case .features: return [...]       // ❌ УДАЛИТЬ весь case
    case .energy: return [...]          // ❌ УДАЛИТЬ весь case
    }
}

// ДОЛЖНО БЫТЬ:
func localizedContent(_ localizationManager: LocalizationManager) -> [String] {
    switch self {
    case .noLogs: return [...]
    case .encryption: return [...]
    }
}
```

**Удалить из switch content (строка 830):**
```swift
// БЫЛО:
var content: [String] {
    switch self {
    case .noLogs: return [...]
    case .encryption: return [...]
    case .servers: return [...]        // ❌ УДАЛИТЬ весь case
    case .features: return [...]       // ❌ УДАЛИТЬ весь case
    case .energy: return [...]          // ❌ УДАЛИТЬ весь case
    }
}

// ДОЛЖНО БЫТЬ:
var content: [String] {
    switch self {
    case .noLogs: return [...]
    case .encryption: return [...]
    }
}
```

---

### 2. Локализация (опционально)

**Файл:** `Core/Localization/LocalizationManager.swift`

**Можно оставить локализацию** (не мешает, не используется) или удалить для чистоты.

**Если удаляем локализацию, нужно удалить:**
- Русская секция (строки ~2041-2071):
  - `privacy_policy_network_protection_servers`
  - `privacy_policy_network_protection_servers_subtitle`
  - `privacy_policy_network_protection_servers_content_1-5`
  - `privacy_policy_network_protection_features`
  - `privacy_policy_network_protection_features_subtitle`
  - `privacy_policy_network_protection_features_content_1-5`
  - `privacy_policy_network_protection_energy`
  - `privacy_policy_network_protection_energy_subtitle`
  - `privacy_policy_network_protection_energy_content_1-5`

- Английская секция (строки ~4459-4489):
  - Те же ключи на английском

**Рекомендация:** Оставить локализацию (не мешает, можно вернуть позже если нужно)

---

## ✅ ИТОГОВЫЙ ПЛАН

1. ✅ Удалить 3 case из enum `NetworkProtectionSection`
2. ✅ Удалить обработку этих case во всех switch statements
3. ⚠️ Локализацию оставить (опционально можно удалить)

**Результат:** Останется только 2 карточки:
- 🔒 NO-LOGS POLICY
- 🔐 Технологии шифрования

**Никаких упоминаний VPN!**

