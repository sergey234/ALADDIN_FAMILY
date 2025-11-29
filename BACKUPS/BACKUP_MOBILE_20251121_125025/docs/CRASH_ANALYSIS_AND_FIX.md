# 🔍 Анализ краша при запуске и исправление

**Дата:** 19 ноября 2025  
**Проблема:** Приложение крашится при запуске после добавления согласия и кнопки активации

---

## 📋 ЧТО МЫ ДОБАВИЛИ

### 1. Карточка согласия в Настройках
- **Файл:** `Screens/05_SettingsScreen.swift`
- **Строки:** 515-524
- **Добавлено:** `@AppStorage("personal_data_consent_accepted")` (строка 61)

### 2. Кнопка активации кода в Тарифах
- **Файл:** `Screens/10_TariffsScreen.swift`
- **Строки:** 131 (вызов), 424-462 (определение)
- **Использует:** `navigationManager.navigateTo(.activationCode)`

---

## 🔍 ВОЗМОЖНЫЕ ПРИЧИНЫ КРАША

### ❌ ПРОБЛЕМА 1: Доступ к navigationManager в computed property

**Проблема:**
- `activationCodeButton` - это computed property (`private var`)
- Внутри используется `navigationManager.navigateTo(.activationCode)`
- Computed properties могут вызываться до инициализации `@EnvironmentObject`

**Решение:**
- Использовать `@ViewBuilder` или переместить в `body`
- Или использовать замыкание, которое будет вызвано позже

---

### ❌ ПРОБЛЕМА 2: Spacing.screenPadding вызывается слишком рано

**Проблема:**
- `Spacing.screenPadding` - это computed static property
- Использует `UIScreen.main.bounds.width`
- Может быть недоступен при первом рендере

**Решение:**
- Использовать фиксированное значение или безопасный доступ

---

### ❌ ПРОБЛЕМА 3: Порядок инициализации

**Проблема:**
- Кнопка вызывается в `VStack` сразу при рендере
- `navigationManager` может быть еще не готов

**Решение:**
- Проверить доступность `navigationManager` перед использованием

---

## ✅ ИСПРАВЛЕНИЕ

### Вариант 1: Использовать @ViewBuilder

```swift
@ViewBuilder
private var activationCodeButton: some View {
    Button(action: {
        HapticFeedback.impact(.medium)
        navigationManager.navigateTo(.activationCode)
    }) {
        // ... UI код
    }
}
```

### Вариант 2: Переместить в body

```swift
// Вместо computed property, создать функцию
private func activationCodeButton() -> some View {
    Button(action: {
        HapticFeedback.impact(.medium)
        navigationManager.navigateTo(.activationCode)
    }) {
        // ... UI код
    }
}
```

### Вариант 3: Использовать безопасный доступ

```swift
private var activationCodeButton: some View {
    Button(action: {
        guard navigationManager != nil else { return }
        HapticFeedback.impact(.medium)
        navigationManager.navigateTo(.activationCode)
    }) {
        // ... UI код
    }
}
```

---

## 🎯 РЕКОМЕНДУЕМОЕ ИСПРАВЛЕНИЕ

Использовать `@ViewBuilder` для computed property, который использует `@EnvironmentObject`:

```swift
@ViewBuilder
private var activationCodeButton: some View {
    Button(action: {
        HapticFeedback.impact(.medium)
        navigationManager.navigateTo(.activationCode)
    }) {
        HStack(spacing: Spacing.m) {
            Image(systemName: "key.fill")
                .font(.system(size: 18))
                .foregroundColor(.primaryBlue)
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text("Активировать код подписки")
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Text("Введите код, полученный после оплаты")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .font(.system(size: 14))
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 1)
        )
    }
    .buttonStyle(PlainButtonStyle())
    .padding(.horizontal, Spacing.screenPadding)
}
```

---

**Дата:** 19 ноября 2025  
**Статус:** Требуется исправление

