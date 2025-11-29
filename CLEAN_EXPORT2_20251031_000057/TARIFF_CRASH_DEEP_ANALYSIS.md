# 🔍 ГЛУБОКИЙ АНАЛИЗ КРАША ТАРИФОВ

## 🚨 СИТУАЦИЯ:
- ✅ Проект компилируется без ошибок
- ❌ Приложение крашится при выборе тарифа
- ❌ Логи не появляются (краш до выполнения кода)

## 🔍 ВОЗМОЖНЫЕ ПРИЧИНЫ:

### 1. ПРОБЛЕМА: Создание PaymentQRViewModel вызывает краш

**Место:** `Screens/10_TariffsScreen.swift:410`
```swift
paymentQRViewModel = PaymentQRViewModel(tariff: tariffObj)
```

**Возможные причины:**
- `PaymentQRViewModel.init` может вызывать NetworkManager/APIService
- NetworkManager может требовать что-то что не готово
- AppConfig может быть nil или невалидным

### 2. ПРОБЛЕМА: Sheet создает view до инициализации

**Место:** Sheet открывается до полной готовности данных

### 3. ПРОБЛЕМА: Thread issue

**Место:** ViewModel создается не на main thread

### 4. ПРОБЛЕМА: Memory issue

**Место:** ViewModel не сохраняется правильно

---

## ✅ РЕШЕНИЕ: ПОЛНАЯ ЗАЩИТА ОТ КРАША

### Вариант A: Try-Catch вокруг создания ViewModel

```swift
do {
    paymentQRViewModel = PaymentQRViewModel(tariff: tariffObj)
} catch {
    print("❌ Ошибка создания ViewModel: \(error)")
    viewModel.errorMessage = "Ошибка при выборе тарифа"
    return
}
```

### Вариант B: Отложенное создание ViewModel

```swift
// НЕ создаем ViewModel сразу, создадим в sheet
selectedTariffForPayment = tariffObj
showPaymentQRScreen = true  // Sheet откроется с placeholder
// ViewModel создастся в onAppear PaymentQRScreen
```

### Вариант C: NavigationLink вместо Sheet

```swift
// Убрать sheet полностью
navigationManager.selectedTariffForPayment = tariffObj
navigationManager.navigateTo(.paymentQR)
```

---

## 🎯 РЕКОМЕНДАЦИЯ: Вариант B + Полная защита

Создать ViewModel НЕ в button action, а в onAppear PaymentQRScreen с полной защитой.

