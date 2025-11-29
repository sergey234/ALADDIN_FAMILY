# ❌ ОШИБКИ КОМПИЛЯЦИИ

## 📊 Общее: **36 ошибок**

### По файлам:

#### 1. `22_DeviceDetailScreen.swift` - 20 ошибок
- Дубликат `InfoRow` (строка 176)
- Дубликат `StatCard` (строка 214)
- Неправильные вызовы `InfoRow` (6 мест)
- Неправильные вызовы `StatCard` (4 места)
- Цвета `.dangerRed`, `.infoBlue` не существуют

#### 2. `14_OnboardingScreen.swift` - 4 ошибки
- `.accessibilityLabel(label:hint:)` не поддерживается в iOS 15

#### 3. `10_TariffsScreen.swift` - 3 ошибки
- `leftButton` в `ALADDINNavigationBar`
- `HapticFeedback.mediumImpact()` не существует

#### 4. `FamilyScreenNew.swift` - 3 ошибки
- `leftButton` в `ALADDINNavigationBar`
- `accessibilityLabel` отсутствует

#### 5. `05_SettingsScreen.swift` - 1 ошибка
- Дубликат `ProfileEditView`

#### 6. `11_ProfileScreen.swift` - 4 ошибки
- `Spacing.lg` не существует (4 места)

---

## 🎯 Нужно исправить ПООЧЕРЕДНО
