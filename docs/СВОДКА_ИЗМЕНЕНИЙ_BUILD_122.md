# 📊 СВОДКА ИЗМЕНЕНИЙ BUILD 122

## ✅ ОСНОВНЫЕ ИСПРАВЛЕНИЯ

### 1. Исправление 401 ошибки для `/api/family/stats`
- **Файлы:** `app/auth/auth.py`, `docs/server/auth.py`
- **Изменение:** Добавлена поддержка поля `sub` в JWT токенах для device tokens
- **Приоритет:** `user_id` > `id` > `sub`

### 2. Защита от ложного удаления токенов
- **Файлы:** 
  - `Core/Security/KeychainManager.swift`
  - `ViewModels/MainViewModel.swift`
  - `ALADDINApp.swift`
- **Изменение:** Добавлена проверка валидности токена перед удалением

### 3. Исправления моделей подписки
- **Файлы:** `Core/Models/SubscriptionModels.swift`
- **Изменение:** Исправлены `DecodingError` для всех моделей подписки

### 4. Улучшения UI и локализации
- **Файлы:** 
  - `Core/Localization/LocalizationManager.swift`
  - `ViewModels/DarkWebMonitoringViewModel.swift`
  - `Shared/Components/Modals/*.swift`
- **Изменение:** Исправления локализации и UI для Dark Web Monitoring

### 5. Улучшения Visual Logger
- **Файлы:** `Core/Utilities/VisualLogger.swift`
- **Изменение:** Добавлен модификатор `withVisualLogger()` для всех экранов

### 6. Исправления родительского контроля
- **Файлы:** 
  - `ViewModels/ParentalControlViewModel.swift`
  - `ViewModels/AICategoriesViewModel.swift`
- **Изменение:** Исправлена логика загрузки детей и обработки ошибок

### 7. Исправления регистрации семьи
- **Файлы:** 
  - `ViewModels/FamilyRegistrationViewModel.swift`
  - `Screens/MainScreenWithRegistration.swift`
- **Изменение:** Исправлена логика добавления участников семьи

---

## 📁 ИЗМЕНЕННЫЕ ФАЙЛЫ (23 файла)

### iOS приложение:
- `ALADDINApp.swift`
- `Core/Config/AppConfig.swift` (buildNumber: 122)
- `Core/Localization/LocalizationManager.swift`
- `Core/Managers/SubscriptionManager.swift`
- `Core/Models/APIModels.swift`
- `Core/Models/SubscriptionModels.swift`
- `Core/Security/KeychainManager.swift`
- `Core/Utilities/VisualLogger.swift`
- `Info.plist` (CFBundleVersion: 122)
- `Screens/MainScreenWithRegistration.swift`
- `Shared/Components/Modals/AICategoriesModal.swift`
- `Shared/Components/Modals/DarkWebDataInputView.swift`
- `Shared/Components/Modals/DarkWebMonitoringModal.swift`
- `Shared/Components/Modals/DarkWebScanMethodSelector.swift`
- `Shared/Components/Modals/DrivingReportsModal.swift`
- `ViewModels/AICategoriesViewModel.swift`
- `ViewModels/DarkWebMonitoringViewModel.swift`
- `ViewModels/DrivingReportsViewModel.swift`
- `ViewModels/FamilyRegistrationViewModel.swift`
- `ViewModels/MainViewModel.swift`
- `ViewModels/ParentalControlViewModel.swift`

### Сервер:
- `app/auth/auth.py`
- `docs/server/auth.py`

---

## 🎯 РЕЗУЛЬТАТ

- ✅ Исправление 401 ошибки для device tokens
- ✅ Защита от ложного удаления токенов
- ✅ Исправления моделей подписки
- ✅ Улучшения UI и локализации
- ✅ Номер сборки обновлен до 122

---

**Дата:** 16 марта 2026  
**Build:** 122
